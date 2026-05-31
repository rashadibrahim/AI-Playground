from .base import RAGStrategy
from typing import Dict, Any
from langchain_text_splitters import RecursiveCharacterTextSplitter
import uuid

class ParentChildStrategy(RAGStrategy):
    """Parents in SQLite, Children in Chroma"""
    
    def __init__(self, parent_size: int = 2200, child_size: int = 550):
        self.parent_splitter = RecursiveCharacterTextSplitter(
            chunk_size=parent_size, chunk_overlap=150
        )
        self.child_splitter = RecursiveCharacterTextSplitter(
            chunk_size=child_size, chunk_overlap=50
        )
    
    def process_document(self, doc: Dict) -> Dict[str, Any]:
        full_text = doc["content"]
        source = doc.get("source", "unknown")
        doc_id = str(uuid.uuid4())
        
        parent_texts = self.parent_splitter.split_text(full_text)
        child_chunks = []
        parent_chunks = []

        for p_idx, parent_text in enumerate(parent_texts):
            parent_id = f"{doc_id}_p{p_idx}"
            parent_chunks.append({
                "content": parent_text,
                "parent_id": parent_id,
                "metadata": {
                    "source": source,
                    "strategy": "parent_child",
                }
            })
            
            child_texts = self.child_splitter.split_text(parent_text)
            
            for child_text in child_texts:
                child_chunks.append({
                    "content": child_text,
                    "metadata": {
                        "source": source,
                        "strategy": "parent_child",
                        "parent_id": parent_id,
                    }
                })
        
        return {
            "parent_chunks": parent_chunks,
            "vector_chunks": child_chunks
        }