from typing import Any, Dict, Optional
from .embedding import EmbeddingModel
from .store import SemanticCacheStore


class SemanticCache:
    def __init__(self, 
                 similarity_threshold: float = 0.85,
                 default_ttl: int = 86400, # 1 day in seconds
                 db_dir: str = "./databases/semantic_cache_db",
                 enable_ttl: bool = False):   
        
        self.embedding_model = EmbeddingModel("all-MiniLM-L6-v2")
        self.store = SemanticCacheStore(persist_directory=db_dir, enable_ttl=enable_ttl)
        self.similarity_threshold = similarity_threshold
        self.default_ttl = default_ttl

    def get_similar(self, query: str, metadata: Optional[Dict] = None) -> Dict[str, Any]:

        embedding = self.embedding_model.embed([query])[0]

        cached = self.store.query(embedding, self.similarity_threshold, metadata=metadata)

        if cached:
            return {
                "response": cached["response"],
                "similarity": cached["similarity"]
            }
        else:
            return {
                "response": None,
                "similarity": 0.0
            }
    
    def add_to_cache(self, query: str, response: str, metadata: Optional[Dict] = None) -> None:
        embedding = self.embedding_model.embed([query])[0]
        self.store.add(
            query=query,
            response=response,
            embedding=embedding,
            ttl_seconds=self.default_ttl,
            metadata=metadata
        )

