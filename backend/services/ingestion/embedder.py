import asyncio
from typing import List
from fastembed import TextEmbedding
from tenacity import retry, wait_exponential, stop_after_attempt
import structlog

logger = structlog.get_logger(__name__)

# Initialize TextEmbedding globally (bundled with qdrant-client)
# all-MiniLM-L6-v2 produces 384 dimensional vectors
embedding_model = TextEmbedding(model_name="sentence-transformers/all-MiniLM-L6-v2")

@retry(wait=wait_exponential(multiplier=1, min=4, max=10), stop=stop_after_attempt(3))
async def embed_chunks(texts: List[str]) -> List[List[float]]:
    """
    Batch embed chunks using fastembed.
    """
    logger.info("Embedding batch", size=len(texts))
    embeddings_gen = await asyncio.to_thread(embedding_model.embed, texts)
    return [list(emb) for emb in embeddings_gen]
