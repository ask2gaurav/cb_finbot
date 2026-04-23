from typing import List, Dict, Any
from qdrant_client.http.models import ScoredPoint
from services.retrieval.semantic_router import get_routing_collection
from services.ingestion.indexer import qdrant_client
from services.ingestion.embedder import embed_chunks
import structlog

logger = structlog.get_logger(__name__)

ROLE_COLLECTION_MAP = {
    "finance": ["rag_finance"],
    "engineering": ["rag_engineering"],
    "marketing": ["rag_marketing"],
    "employee": ["rag_employee"],
    "admin": ["rag_finance", "rag_engineering", "rag_marketing", "rag_employee", "rag_c_level"],
    "c_level": ["rag_finance", "rag_engineering", "rag_marketing", "rag_employee", "rag_c_level"]
}

async def retrieve(query: str, user_role: str, top_k: int = 5) -> List[ScoredPoint]:
    """
    Retrieve top_k chunks based on query and user_role.
    """
    logger.info("Retrieving documents for query", query=query, role=user_role)
    
    target_collection = get_routing_collection(query)
    logger.info("Semantic Router suggests collection", collection=target_collection)
    
    allowed_collections = ROLE_COLLECTION_MAP.get(user_role, [])
    
    if target_collection is None:
        target_collection = f"rag_{user_role}" if user_role not in ["admin", "c_level"] else "rag_c_level"
        
    if target_collection not in allowed_collections:
        logger.warning(
            "Access denied to target collection",
            role=user_role,
            requested_collection=target_collection,
            allowed=allowed_collections
        )
        if user_role not in ["admin", "c_level"]:
             target_collection = f"rag_{user_role}"
             
    query_vector = (await embed_chunks([query]))[0]
    
    try:
        search_result = await qdrant_client.search(
            collection_name=target_collection,
            query_vector=query_vector,
            limit=top_k,
            with_payload=True
        )
        return search_result
    except Exception as e:
        logger.error("Query failed, collection might not exist", collection=target_collection, error=str(e))
        return []
