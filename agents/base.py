from abc import ABC, abstractmethod
from typing import Dict, Any

class BaseAgent(ABC):
    """
    Base class for all agents in the system.
    Provides common structure and dependencies.
    """
    def __init__(self, 
                 llm_client,
                 short_term_memory=None,
                 rag_pipeline=None, 
                 tools=None):
        self.llm = llm_client
        self.short_term_memory = short_term_memory
        self.rag = rag_pipeline
        self.tools = tools or []
    
    @abstractmethod
    def run(self, user_query: str) -> Dict[str, Any]:
        """
        Every agent must implement this method.
        Returns a standardized response dictionary.
        """
        pass