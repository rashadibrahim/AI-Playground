from .base import BaseAgent
from typing import Dict, Any

class SimpleAgent(BaseAgent):
    """
    Fastest agent. 
    Purpose: Quick responses without heavy tools or memory.
    Best for: Simple questions, greetings, basic info.
    """
    
    def __init__(self, llm_client):
        super().__init__(
            llm_client=llm_client,
        )
        self.llm_client = llm_client

    def run(self, user_query: str) -> Dict[str, Any]:
        prompt = f"""You are a helpful assistant. Answer the following question clearly and concisely.

Question: {user_query}

Answer:"""
        
        # Step 3: Call LLM
        response = self.llm.invoke(prompt)
        return {
            "answer": response.content,
            "agent_type": "simple",
        }