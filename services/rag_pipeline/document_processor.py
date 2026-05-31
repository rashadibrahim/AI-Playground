from typing import List, Dict, Optional
from .strategies.base import RAGStrategy
from .document_store import DocumentStore
from .parent_store import ParentStore

class DocumentProcessor:
    """Handles ingestion and retrieval logic for both strategies"""
    
    def __init__(self, strategy: RAGStrategy, document_store: DocumentStore):
        self.strategy = strategy
        self.document_store = document_store
        self.parent_store = ParentStore()  # Only used for Parent-Child strategy
    
    def ingest_documents(self, documents: List[Dict]):
        """Main ingestion method"""
        all_child_chunks = []
        
        for doc in documents:
            # Process document according to selected strategy
            chunks_returned = self.strategy.process_document(doc)
            processed_chunks = chunks_returned["vector_chunks"]
            
            # Special handling for Parent-Child strategy
            if self.strategy.get_name() == "ParentChildStrategy":
                self._save_parents(chunks_returned["parent_chunks"])
            
            all_child_chunks.extend(processed_chunks)
        
        # Store all chunks in vector database
        self.document_store.add_chunks(all_child_chunks)
        
    
    def _save_parents(self, parent_chunks: List[Dict]):
        """Save parent chunks to SQLite for Parent-Child strategy"""
        for parent in parent_chunks:
            self.parent_store.save_parent(
                parent_id=parent["parent_id"],
                content=parent["content"],
                metadata=parent.get("metadata", {})
            )
    
    def retrieve(self, query: str, strategy_name: str) -> Optional[str]:
        """Retrieve relevant chunks based on strategy"""
        child_results = self.document_store.retrieve(query, 1)
        
        if strategy_name == "ParentChildStrategy":
            parent_id = child_results[0]["metadata"].get("parent_id")
            if parent_id:
                parent_content = self.parent_store.get_parent(parent_id)
                if parent_content:
                    return parent_content["content"]
            return child_results[0]["content"] if child_results else None
        
        else:
            parent_content = child_results[0]["metadata"].get("full_content") if child_results else None
            if parent_content:
                return parent_content
            return child_results[0]["content"] if child_results else None