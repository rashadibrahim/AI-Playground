from typing import List, Dict
from ..semantic_cache.embedding import EmbeddingModel
import chromadb
import uuid

class DocumentStore:
    """Handles all vector operations using Chroma"""
    
    def __init__(self, collection_name: str = "rag_documents"):
        self.embedding_model = EmbeddingModel("all-MiniLM-L6-v2")
        self._init_chroma(collection_name)
    
    def _init_chroma(self, collection_name: str):
        self.client = chromadb.PersistentClient(path="./databases/doc_store")
        self.collection = self.client.get_or_create_collection(
            name=collection_name,
            metadata={"hnsw:space": "cosine"}
        )
    
    def add_chunks(self, chunks: List[Dict]):
        """Add chunks to vector database"""
        if not chunks:
            return
            
        texts = [chunk["content"] for chunk in chunks]
        embeddings = self.embedding_model.embed(texts)
        
        for i, chunk in enumerate(chunks):
            self.collection.add(
                embeddings=[embeddings[i].tolist()],
                documents=[chunk["content"]],
                metadatas=[chunk["metadata"]],
                ids=[str(uuid.uuid4())]
            )
    
    def retrieve(self, query: str, top_k: int = 6) -> List[Dict]:
        """Retrieve relevant chunks from vector store"""
        embedding = self.embedding_model.embed([query])[0]
        
        results = self.collection.query(
            query_embeddings=[embedding.tolist()],
            n_results=top_k,
        )

        return [{"content": doc, "metadata": meta} for doc, meta in zip(results["documents"][0], results["metadatas"][0])]