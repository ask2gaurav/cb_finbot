from typing import AsyncGenerator
from services.retrieval.retriever import retrieve
from services.generation.prompts import get_role_prompt
from core.config import get_settings
from langchain_groq import ChatGroq
from langchain_core.output_parsers import StrOutputParser

settings = get_settings()

async def format_docs(docs) -> tuple[str, list[dict]]:
    formatted = []
    meta_list = []
    for i, doc in enumerate(docs):
        payload = doc.payload or {}
        text = payload.get("text", "")
        formatted.append(f"Document {i+1}:\n{text}")
        meta_list.append(payload)
    return "\n\n".join(formatted), meta_list

def get_generation_chain(role: str, streaming: bool = True):
    prompt = get_role_prompt(role if role != "admin" else "c_level")
    llm = ChatGroq(api_key=settings.GROQ_API_KEY, model_name="llama3-8b-8192", streaming=streaming)
    return prompt | llm | StrOutputParser()
