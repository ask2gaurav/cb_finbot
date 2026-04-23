from services.guardrails.base import GuardrailResult
from services.guardrails.grounding import grounding_check, GROUNDING_FALLBACK
from services.guardrails.role_leakage import leakage_check
from services.guardrails.citation import citation_check

async def run_guardrails(answer: str, context_chunks: list[dict], user_role: str) -> GuardrailResult:
    flags = []
    
    # Extract texts and roles
    context_texts = [chunk.get("text", "") for chunk in context_chunks]
    context_roles = [chunk.get("role", "unknown") for chunk in context_chunks]
    
    # 1. Grounding 
    passed, new_answer = await grounding_check(answer, context_texts)
    if not passed:
        return GuardrailResult(final_answer=GROUNDING_FALLBACK, blocked=True, flags=["grounding_failed"])
        
    # 2. Leakage
    passed, new_answer = await leakage_check(new_answer, context_roles, user_role)
    if not passed:
        return GuardrailResult(final_answer=new_answer, blocked=True, flags=["leakage_detected"])
        
    # 3. Citation
    passed, cited_answer = await citation_check(new_answer, context_chunks)
    
    return GuardrailResult(final_answer=cited_answer, blocked=False, flags=[])
