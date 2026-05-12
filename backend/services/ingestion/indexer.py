import uuid
import structlog
from qdrant_client import AsyncQdrantClient
from qdrant_client.http.models import Distance, VectorParams, PointStruct
from core.config import get_settings

logger = structlog.get_logger(__name__)
settings = get_settings()

# Initialize global async Qdrant client
qdrant_client = AsyncQdrantClient(host=settings.QDRANT_HOST, port=settings.QDRANT_PORT)

async def init_collection(collection_name: str, vector_size: int = 384):
    try:
        exists = await qdrant_client.collection_exists(collection_name)
        if not exists:
            logger.info("Creating Qdrant collection", collection_name=collection_name)
            await qdrant_client.create_collection(
                collection_name=collection_name,
                vectors_config=VectorParams(size=vector_size, distance=Distance.COSINE),
            )
    except Exception as e:
        logger.error(f"Error initializing collection {collection_name}: {e}")

async def index_chunks(collection_name: str, chunks: list, embeddings: list, role: str, doc_id: str, uploaded_by: str, uploaded_at: str):
    """
    Upsert vectors to Qdrant collection
    """
    points = []
    for chunk, emb in zip(chunks, embeddings):
        payload = chunk.metadata.copy()
        payload.update({
            "doc_id": doc_id,
            "collection": role,
            #"access_roles":access_roles := ["c_level"] if role != "c_level" else ["finance", "engineering", "marketing", "employee", "c_level"],
            #"text": chunk.text,
            "uploaded_by": str(uploaded_by),
            "uploaded_at": str(uploaded_at)
        })
        
        points.append(
            PointStruct(
                id=str(uuid.uuid4()),
                vector=emb,
                payload=payload
            )
        )
        
    batch_size = 100
    for i in range(0, len(points), batch_size):
        batch = points[i:i+batch_size]
        await qdrant_client.upsert(
            collection_name=collection_name,
            points=batch
        )
    logger.info("Indexed chunks", collection=collection_name, count=len(points))
