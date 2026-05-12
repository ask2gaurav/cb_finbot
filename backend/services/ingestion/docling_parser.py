import asyncio
import os
import pickle
from pathlib import Path
from typing import List, Dict, Any
from pydantic import BaseModel
#from docling.document_converter import DocumentConverter
from langchain_docling import DoclingLoader
from langchain_docling.loader import ExportType
from docling_core.transforms.chunker import HierarchicalChunker

class Chunk(BaseModel):
    text: str
    metadata: Dict[str, Any]

class DoclingParser:
    def __init__(self):
        #self.converter = DocumentConverter()

    def _save_markdown(self, doc, filename: str):
        stem = Path(filename).stem
        md_content = doc.export_to_markdown()
        md_path_dir = MARKDOWN_OUTPUT_DIR / f"{stem}"
        md_path_dir.mkdir(parents=True, exist_ok=True)
        CHUNKS_OUTPUT_DIR = md_path_dir / "chunks"
        CHUNKS_OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
        md_path = md_path_dir / f"{stem}.md"
        md_path.write_text(md_content, encoding="utf-8")
        return stem

    def _save_chunk(self, stem: str, chunk_index: int, text: str):
        md_path_dir = MARKDOWN_OUTPUT_DIR / f"{stem}"
        chunk_output_dir = md_path_dir / "chunks"
        chunk_output_dir.mkdir(parents=True, exist_ok=True)
        chunk_path = chunk_output_dir / f"{stem}_chunk_{chunk_index:04d}.md"
        with chunk_path.open("w", encoding="utf-8") as f:
            pickle.dump(text, f)
        #chunk_path.write_text(text, encoding="utf-8")

    def _parse_sync(self, file_path: str, filename: str) -> List[Chunk]:
        #doc_result = self.converter.convert(file_path)
        #doc = doc_result.document
        

        #stem = self._save_markdown(doc, filename)
        stem = Path(filename).stem
        chunks = []
        try:
            #from docling.chunking import HierarchicalChunker
            #chunker = HierarchicalChunker()
            #chunk_iter = chunker.chunk(doc)
            chunk_iter = DoclingLoader(file_path=file_path, export_type=ExportType.DOC_CHUNKS, chunker=HierarchicalChunker(),).load()

        for i, doc_chunk in enumerate(chunk_iter):
                self._save_chunk(stem, i, doc_chunk)
                
                parents = []
                source_document = None
                page_no = None
                section_titles = []
                content_layer=[]
                chunk_types  = []
                parent_chunk_id = []
                if hasattr(doc_chunk, 'metadata' and hasattr(doc_chunk.metadata, 'source')):
                    source_document = doc_chunk.source
                if hasattr(doc_chunk, 'metadata') and hasattr(doc_chunk.metadata, 'dl_meta') and hasattr(doc_chunk.metadata.dl_meta, 'parent'):
                    parent_chunk_id.append(doc_chunk.metadata.dl_meta.parent)
                if hasattr(doc_chunk, 'metadata') and hasattr(doc_chunk.metadata, 'dl_meta') and hasattr(doc_chunk.metadata.dl_meta, 'headings'):
                    section_titles = doc_chunk.metadata.dl_meta.headings.copy()
                if hasattr(doc_chunk, 'metadata') and hasattr(doc_chunk.metadata, 'dl_meta') and hasattr(doc_chunk.metadata.dl_meta, 'doc_items'):
                    for item in doc_chunk.metadata.dl_meta.doc_items:
                        if hasattr(item, 'label') and item.label:
                            chunk_types.append(item.label)
                        if hasattr(item, 'content_layer') and item.content_layer:
                            content_layer.append(item.content_layer)
                if hasattr(doc_chunk, 'metadata') and hasattr(doc_chunk.metadata, 'dl_meta') and hasattr(doc_chunk.metadata.dl_meta, 'doc_items'):
                    for item in doc_chunk.metadata.dl_meta.doc_items:
                        if not page_no and hasattr(item, 'prov') and item.prov:
                            page_no = item.prov[0].page_no
                            break


                metadata = {
                    "filename": filename,
                    "page": page_no or 1,
                    "chunk_index": i,
                    "source_document": source_document,
                    "section_titles": section_titles,
                    "chunk_types": chunk_types,
                    "content_layer": content_layer,
                    "parent_chunk_id": parent_chunk_id
                }
                chunks.append(Chunk(text=doc_chunk.page_content, metadata=metadata))
        # except ImportError:
        #     self._save_chunk(stem, 0, doc.text)
        #     chunks.append(Chunk(text=doc.text, metadata={"filename": filename, "page": 1, "chunk_index": 0}))

        return chunks

    async def parse_document(self, file_path: str, filename: str) -> List[Chunk]:
        """
        Runs the CPU-bound docling parsing in a separate thread.
        """
        return await asyncio.to_thread(self._parse_sync, file_path, filename)

parser_instance = DoclingParser()
