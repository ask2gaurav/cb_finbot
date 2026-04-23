import asyncio
from typing import List, Dict, Any
from pydantic import BaseModel
from docling.document_converter import DocumentConverter

class Chunk(BaseModel):
    text: str
    metadata: Dict[str, Any]

class DoclingParser:
    def __init__(self):
        self.converter = DocumentConverter()

    def _parse_sync(self, file_path: str, filename: str) -> List[Chunk]:
        doc_result = self.converter.convert(file_path)
        doc = doc_result.document
        
        chunks = []
        try:
            from docling.chunking import HierarchicalChunker
            chunker = HierarchicalChunker()
            chunk_iter = chunker.chunk(doc)
            
            for i, doc_chunk in enumerate(chunk_iter):
                page_no = None
                if hasattr(doc_chunk, 'meta') and hasattr(doc_chunk.meta, 'doc_items'):
                    for item in doc_chunk.meta.doc_items:
                        if hasattr(item, 'prov') and item.prov:
                            page_no = item.prov[0].page_no
                            break
                
                metadata = {
                    "filename": filename,
                    "page": page_no or 1,
                    "chunk_index": i
                }
                chunks.append(Chunk(text=doc_chunk.text, metadata=metadata))
        except ImportError:
            # Fallback if docling chunking module is different
            chunks.append(Chunk(text=doc.text, metadata={"filename": filename, "page": 1, "chunk_index": 0}))
            
        return chunks

    async def parse_document(self, file_path: str, filename: str) -> List[Chunk]:
        """
        Runs the CPU-bound docling parsing in a separate thread.
        """
        return await asyncio.to_thread(self._parse_sync, file_path, filename)

parser_instance = DoclingParser()
