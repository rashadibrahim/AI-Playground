from abc import ABC, abstractmethod
from typing import List, Dict, Any

class RAGStrategy(ABC):
    """Base class for RAG strategies"""
    
    @abstractmethod
    def process_document(self, doc: Dict) -> Dict[str, Any]:
        """Return list of items to be stored in vector database"""
        pass

    def get_name(self) -> str:
        return self.__class__.__name__