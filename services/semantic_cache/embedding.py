from sentence_transformers import SentenceTransformer 
import numpy as np
from typing import List

class EmbeddingModel:
    def __init__(self, model_name: str = "all-MiniLM-L6-v2"):
        self.model = SentenceTransformer(model_name)
        self.dimension = self.model.get_sentence_embedding_dimension()
    
    def embed(self, texts: List[str]) -> np.ndarray:
        embeddings = self.model.encode(
            texts, 
            normalize_embeddings=True,   
            show_progress_bar=False
        )
        return embeddings 