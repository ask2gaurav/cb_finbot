import structlog
from langchain_groq import ChatGroq
from langchain_core.prompts import PromptTemplate
from core.config import get_settings

logger = structlog.get_logger(__name__)
settings = get_settings()

CITATION_PROMPT = """
You are a citation enforcement assistant. You must rewrite the answer to include citations for every factual claim.
The citations must be in the exact format: [Source: filename, p.N]

Context Documents:
{context}

Original Answer:
{answer}

Rewrite the Original Answer. Ensure every claim has a source bracket. Append a 'Sources' section at the end. Any claim without a source must be removed.
"""

async def citation_check(answer: str, context_meta: list[dict]) -> tuple[bool, str]:
    try:
        context_str = ""
        for i, meta in enumerate(context_meta):
             filename = meta.get("filename", "unknown")
             page = meta.get("page", 1)
             text = meta.get("text", "")
             context_str += f"Doc {i+1} [Source: {filename}, p.{page}]:\n{text}\n\n"
             
        llm = ChatGroq(api_key=settings.GROQ_API_KEY, model_name="llama3-8b-8192")
        prompt = PromptTemplate.from_template(CITATION_PROMPT)
        chain = prompt | llm
        
        response = await chain.ainvoke({"context": context_str, "answer": answer})
        cited_answer = response.content
        return True, cited_answer
        
    except Exception as e:
        logger.error("Citation check failed", error=str(e))
        return True, answer
