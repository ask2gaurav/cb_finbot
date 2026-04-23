import json
import structlog
from langchain_groq import ChatGroq
from langchain_core.prompts import PromptTemplate
from core.config import get_settings

logger = structlog.get_logger(__name__)
settings = get_settings()

GROUNDING_PROMPT = """
You are a grounding verification assistant.
Context:
{context}

Answer:
{answer}

Extract all factual claims from the Answer. Then, verify if each claim is supported by the Context.
Return a JSON object with this exact structure:
{{
    "total_claims": 3,
    "grounded_claims": 2,
    "claims": [
        {{"claim": "Company revenue grew 10%", "supported": true}}
    ]
}}
Do not return any text outside the JSON object.
"""

GROUNDING_FALLBACK = "I can only answer based on the provided documents. The answer to your question isn't clearly supported by the available sources."

async def grounding_check(answer: str, context_texts: list[str]) -> tuple[bool, str]:
    context_str = "\\n\\n".join(context_texts)
    
    try:
        llm = ChatGroq(api_key=settings.GROQ_API_KEY, model_name="llama3-8b-8192", model_kwargs={"response_format": {"type": "json_object"}})
        prompt = PromptTemplate.from_template(GROUNDING_PROMPT)
        chain = prompt | llm
        
        response = await chain.ainvoke({"context": context_str, "answer": answer})
        result = json.loads(response.content)
        
        total = result.get("total_claims", 0)
        grounded = result.get("grounded_claims", 0)
        
        if total == 0:
            return True, answer
            
        score = grounded / total
        logger.info("Grounding score", score=score, total=total)
        
        if score < 0.7:
             return False, GROUNDING_FALLBACK
        return True, answer
        
    except Exception as e:
        logger.error("Grounding check failed", error=str(e))
        return True, answer # fail open
