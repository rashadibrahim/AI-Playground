from .base import BaseAgent
from typing import Dict, Any

class RAGMemoryAgent(BaseAgent):
    """
    Balanced agent.
    Purpose: Use personal documents (RAG) + user memory history.
    Best for: Most user questions about their documents or personal history.
    """
    def __init__(self, llm_client, short_term_memory, rag_pipeline):
        super().__init__(
            llm_client=llm_client,
            short_term_memory=short_term_memory,
            rag_pipeline=rag_pipeline,
        )
        self.llm_client = llm_client
        self.short_term_memory = short_term_memory
        self.rag = rag_pipeline
        
    def run(self, user_query: str) -> Dict[str, Any]:
        rag_result = self.rag.simple_query(user_query)
        history_context = self.short_term_memory.history.copy()
        
        prompt = f"""
        You are a helpful assistant. Use the following retrieved information and history context to answer the question clearly and concisely.

        RAG Context:
        {rag_result}

        History Context:
        {history_context}

        Question: {user_query}

        Answer:"""

        response = self.llm.invoke(prompt)
        
        self.short_term_memory.add_message("user", user_query)
        self.short_term_memory.add_message("assistant", response.content)

        return {
            "answer": response.content,
            "agent_type": "rag_memory",
        }