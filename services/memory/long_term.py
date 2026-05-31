import uuid
import time
from typing import List, Dict
from ..semantic_cache.embedding import EmbeddingModel 
import chromadb

class LongTermMemory:
    
    def __init__(self):
        self.embedding_model = EmbeddingModel("all-MiniLM-L6-v2")
        self.collection_name = "long_term_memory"
        self._init_store()
    
    def _init_store(self):
        self.client = chromadb.PersistentClient(path="./databases/long_term_memory_db")
        self.collection = self.client.get_or_create_collection(
            name=self.collection_name,
            metadata={"hnsw:space": "cosine"}
        )
    
    def add_fact(self, fact: str, importance: float) -> str:
        try:
            embedding = self.embedding_model.embed([fact])[0]
        
            metadata = {
                "fact": fact,
                "importance": importance,
                "timestamp": time.time(),
            }
            
            self.collection.add(
                embeddings=[embedding.tolist()],
                documents=[fact],
                metadatas=[metadata],
                ids=[str(uuid.uuid4())]
            )
            return "Fact stored successfully."
        except Exception as e:
            return "Failed to store fact"
    
    def get_relevant_facts(self, query: str, top_k: int = 5) -> List[Dict]:
        embedding = self.embedding_model.embed([query])[0]
        
        results = self.collection.query(
            query_embeddings=[embedding.tolist()],
            n_results=top_k,
            include=["metadatas", "distances"]
        )
        
        facts = []
        for meta, dist in zip(results['metadatas'][0], results['distances'][0]):
            similarity = 1 - dist
            facts.append({
                "fact": meta['fact'],
                "similarity": similarity,
                "importance": meta.get('importance', 0.5)
            })
        return facts