import chromadb
import time
from typing import Optional, Dict
import uuid
import numpy as np

class SemanticCacheStore:
    def __init__(self, 
                 collection_name: str = "semantic_cache", 
                 persist_directory: str = "./databases/semantic_cache_db", 
                 enable_ttl: bool = True):
        
        self.client = chromadb.PersistentClient(path=persist_directory)
        self.enable_ttl = enable_ttl
        
        self.collection = self.client.get_or_create_collection(
            name=collection_name,
            metadata={"hnsw:space": "cosine"} 
        )
    
    def add(self, query: str, response: str, embedding: np.ndarray, ttl_seconds: int = 3600, metadata: Optional[Dict] = None) -> None:
        doc_id = str(uuid.uuid4())
        metadata = {
                "query": query,
                "response": response,
                "timestamp": time.time()
            }
        if metadata is not None:
            metadata.update(metadata)
            
        
        if self.enable_ttl:
            metadata["expires_at"] = time.time() + ttl_seconds
        
        self.collection.add(
            embeddings=[embedding.tolist()],
            documents=[query],
            metadatas=[metadata],
            ids=[doc_id]
        )

    def query(self, embedding: np.ndarray, threshold: float = 0.85, metadata: Optional[Dict] = None) -> Optional[Dict]:
        if metadata is None:
            results = self.collection.query(
                query_embeddings=[embedding.tolist()],
                n_results=1,                       
                include=["metadatas", "distances"]
            )
        else:
            results = self.collection.query(
                query_embeddings=[embedding.tolist()],
                n_results=1,                       
                include=["metadatas", "distances"],
                where=metadata
            )
        
        if not results['metadatas'][0]:
            return None
            
        metadata = results['metadatas'][0][0]
        distance = results['distances'][0][0]
        similarity = 1 - distance               # Convert distance to similarity
        
        if similarity >= threshold and (not self.enable_ttl or  (metadata['expires_at'] > time.time())):
            return {
                "response": metadata['response'],
                "similarity": similarity,
                "original_query": metadata['query']
            }
        return None
    
    def clear_expired(self):
        if not self.enable_ttl:
            return
        
        all_docs = self.collection.get(include=["metadatas", "ids"])
        if not all_docs['metadatas']:
            return
        
        current_time = time.time()
        expired_ids = [doc_id for doc_id, meta in zip(all_docs['ids'], all_docs['metadatas']) 
                       if meta.get('expires_at', float('inf')) < current_time]

        if expired_ids:
            self.collection.delete(ids=expired_ids)