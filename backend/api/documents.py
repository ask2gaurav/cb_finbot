import os
import aiofiles
import shutil
from pathlib import Path
from fastapi import APIRouter, Depends, UploadFile, File, Form, BackgroundTasks, HTTPException
from core.dependencies import require_role, get_current_user
from models.user import UserResponse
from models.document import DocumentModel
from db.mongo import get_db
from services.ingestion.docling_parser import parser_instance
from services.ingestion.embedder import embed_chunks
from services.ingestion.indexer import index_chunks, init_collection
import structlog

logger = structlog.get_logger(__name__)

router = APIRouter(prefix="/documents", tags=["documents"])

async def process_document(file_path: str, filename: str, role: str, doc_id: str, uploaded_by: str, uploaded_at: str, db):
    try:
        chunks = await parser_instance.parse_document(file_path, filename)
        if not chunks:
            raise ValueError("No text extracted from document")

        texts = [chunk.text for chunk in chunks]
        embeddings = await embed_chunks(texts)

        #collection_name = f"rag_{role}"
        collection_name = os.getenv("RAG_COLLECTION_NAME", "finbot_documents")
        await init_collection(collection_name)
        await index_chunks(collection_name, chunks, embeddings, role, str(doc_id), uploaded_by, uploaded_at)

        # if role != "c_level":
        #     c_level_collection = "rag_c_level"
        #     await init_collection(c_level_collection)
        #     await index_chunks(c_level_collection, chunks, embeddings, role, str(doc_id), uploaded_by, uploaded_at)

        await db.documents.update_one(
            {"_id": doc_id},
            {"$set": {"status": "completed"}}
        )
        logger.info("Document processing completed", doc_id=doc_id)
        
    except Exception as e:
        logger.error("Document processing failed", doc_id=doc_id, error=str(e))
        await db.documents.update_one(
            {"_id": doc_id},
            {"$set": {"status": "failed", "error": str(e)}}
        )
    #finally:
        # if os.path.exists(file_path):
        #     os.remove(file_path)

@router.post("/upload")
async def upload_document(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    role: str = Form(...),
    current_user: UserResponse = Depends(require_role("admin")),
    db = Depends(get_db)
):
    valid_roles = ["finance", "engineering", "marketing", "employee", "c_level"]
    if role not in valid_roles:
        raise HTTPException(status_code=400, detail=f"Invalid role. Must be one of {valid_roles}")

    doc = DocumentModel(
        filename=file.filename,
        role=role,
        uploaded_by=current_user.id
    )
    
    # We use the current directory + tmp instead of absolute /tmp to ensure permissions on windows
    temp_dir = os.path.join(os.getcwd(), "tmp", "rag_uploads")
    os.makedirs(temp_dir, exist_ok=True)
    temp_path = os.path.join(temp_dir, f"{doc.id}_{file.filename}")
    
    async with aiofiles.open(temp_path, 'wb') as out_file:
        content = await file.read()
        await out_file.write(content)
    doc.filepath = temp_path    
    doc_dict = doc.model_dump(by_alias=True)
    await db.documents.insert_one(doc_dict)
    
    background_tasks.add_task(
        process_document,
        temp_path,
        file.filename,
        role,
        doc.id,
        current_user.id,
        str(doc.uploaded_at),
        db
    )
    
    return {"message": "Upload started", "doc_id": doc.id}

@router.get("")
async def list_documents(
    current_user: UserResponse = Depends(get_current_user),
    db = Depends(get_db)
):
    query = {}
    if current_user.role != "admin" and current_user.role != "c_level":
        query = {"role": current_user.role}
        
    docs_cursor = db.documents.find(query).sort("uploaded_at", -1)
    docs = await docs_cursor.to_list(length=100)
    return docs

@router.delete("/{doc_id}")
async def delete_document(
    doc_id: str,
    current_user: UserResponse = Depends(require_role("admin")),
    db = Depends(get_db)
):
    doc = await db.documents.find_one({"_id": doc_id})
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")
        
    from qdrant_client.http.models import Filter, FieldCondition, MatchValue
    from services.ingestion.indexer import qdrant_client
    
    role = doc["role"]
    filename = doc.get("filename") or doc["filename"] or ""
    filepath = doc.get("filepath") or ""
    stem = Path(filename).stem
    delete_dir = Path(Path(__file__).parent).parent / "services" / "markdown_output" / f"{stem}"
    if os.path.exists(delete_dir):
        shutil.rmtree(delete_dir)
    if filepath and os.path.exists(filepath):
        os.remove(filepath)
    try:
        await qdrant_client.delete(
            #collection_name=f"rag_{role}",
            collection_name=os.getenv("RAG_COLLECTION_NAME", "finbot_documents"),
            points_selector=Filter(
                must=[
                    FieldCondition(key="doc_id", match=MatchValue(value=doc_id))
                ]
            )
        )
        # if role != "c_level":
        #     await qdrant_client.delete(
        #         collection_name="rag_c_level",
        #         points_selector=Filter(
        #             must=[
        #                 FieldCondition(key="doc_id", match=MatchValue(value=doc_id))
        #             ]
        #         )
        #     )
    except Exception as e:
        logger.error("Failed to delete from Qdrant", error=str(e))
        
    await db.documents.delete_one({"_id": doc_id})
    return {"message": "Document deleted"}
