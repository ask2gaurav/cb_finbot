import re
import structlog
from services.retrieval.retriever import ROLE_COLLECTION_MAP

logger = structlog.get_logger(__name__)

ROLE_PATTERNS = {
    "finance": r"\$\d+(?:,\d+)*(?:\.\d+)?|\b([Rr]evenue|[Pp]rofit|[Mm]argin)\b",
    "engineering": r"\b(def|class|function|import|select \w+ from)\b",
    "employee": r"\b(SSN|salary|[Pp]assport|[Dd]ate of [Bb]irth)\b"
}

async def leakage_check(answer: str, context_roles: list[str], user_role: str) -> tuple[bool, str]:
    allowed_collections = ROLE_COLLECTION_MAP.get(user_role, [])
    for chunk_role in context_roles:
         coll_name = f"rag_{chunk_role}"
         if coll_name not in allowed_collections and coll_name != "rag_c_level":
             logger.warning("SECURITY_WARNING: Cross-role context leakage detected in context chunks", user_role=user_role, chunk_role=chunk_role)
             return False, "I cannot answer this question as it requires information from restricted domains."
             
    for role, pattern in ROLE_PATTERNS.items():
        if user_role not in ["admin", "c_level", role]:
            if re.search(pattern, answer):
                logger.warning("SECURITY_WARNING: Cross-role data leakage detected in generation", user_role=user_role, matched_role=role)
                return False, "This response has been blocked due to cross-domain data leakage policies."
                
    return True, answer
