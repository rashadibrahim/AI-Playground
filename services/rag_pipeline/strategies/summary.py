from .base import RAGStrategy
from typing import Any, Dict
from langchain_text_splitters import RecursiveCharacterTextSplitter
from ...summarizer.summarizer import Summarizer

class SummaryStrategy(RAGStrategy):
    """Large Chunk + Summary (both in Chroma)"""
    
    def __init__(self, chunk_size: int = 1400):
        self.splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size, chunk_overlap=120
        )
        self.summarizer = Summarizer()
    
    def process_document(self, doc: Dict) -> Dict[str, Any]:
        full_text = doc["content"]
        source = doc.get("source", "unknown")
        
        large_chunks = self.splitter.split_text(full_text)
        chunks_to_store = []
        
        for chunk_text in large_chunks:
            summary = self.summarizer.summarize_conversation([
                {"role": "user", "content": chunk_text}
            ])
            
            chunks_to_store.append({
                "content": summary,                       # Summary will be embedded
                "metadata": {
                    "source": source,
                    "strategy": "summary",
                    "full_content": chunk_text, 
                }
            })
        
        return {"vector_chunks": chunks_to_store}