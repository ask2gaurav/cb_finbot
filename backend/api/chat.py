import json
from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from typing import Optional
from core.dependencies import get_current_user
from models.user import UserResponse
from models.conversation import ConversationModel, MessageModel
from db.mongo import get_db
from services.retrieval.retriever import retrieve
from services.generation.rag_chain import format_docs, get_generation_chain
from services.guardrails.pipeline import run_guardrails
import structlog

logger = structlog.get_logger(__name__)

router = APIRouter(prefix="/chat", tags=["chat"])

class ChatRequest(BaseModel):
    message: str
    conversation_id: Optional[str] = None

@router.post("/stream")
async def chat_stream(
    request: ChatRequest,
    current_user: UserResponse = Depends(get_current_user),
    db = Depends(get_db)
):
    async def event_generator():
        logger.info("Chat query received", message=request.message, user_id=str(current_user.id), role=current_user.role)
        yield f"data: {json.dumps({'type': 'token', 'content': 'generating...'})}\n\n"
        try:
            retrieved_docs = await retrieve(request.message, current_user.role, top_k=5)
            
            if not retrieved_docs:
                yield f"data: {json.dumps({'type': 'error', 'content': 'There is no relevant data found for given query.'})}\n\n"
                return
                
            context_str, context_meta = await format_docs(retrieved_docs)
            
            chain = get_generation_chain(current_user.role)
            
            full_response = ""
            async for chunk in chain.astream({"context": context_str, "question": request.message}):
                full_response += chunk
                yield f"data: {json.dumps({'type': 'token', 'content': chunk})}\n\n"
                
            guard_result = await run_guardrails(full_response, context_meta, current_user.role)
            logger.info("Chat response generated", final_answer=guard_result.final_answer, flags=guard_result.flags, blocked=guard_result.blocked)
            
            conv_id = request.conversation_id
            if not conv_id:
                conv = ConversationModel(user_id=current_user.id)
                conv_id = conv.id
                await db.conversations.insert_one(conv.model_dump(by_alias=True))
                
            user_msg = MessageModel(role="user", content=request.message)
            asst_msg = MessageModel(
                role="assistant",
                content=guard_result.final_answer,
                sources=context_meta if not guard_result.blocked else [],
                guardrail_flags=guard_result.flags
            )
            
            await db.conversations.update_one(
                {"_id": conv_id},
                {"$push": {"messages": {"$each": [user_msg.model_dump(), asst_msg.model_dump()]}}}
            )
            
            yield f"data: {json.dumps({'type': 'done', 'final_answer': guard_result.final_answer, 'sources': context_meta, 'guardrail_flags': guard_result.flags, 'blocked': guard_result.blocked, 'conversation_id': conv_id})}\n\n"
            
        except Exception as e:
            logger.error("Chat streaming failed", error=str(e))
            yield f"data: {json.dumps({'type': 'error', 'content': str(e)})}\n\n"
            
    return StreamingResponse(event_generator(), media_type="text/event-stream")
