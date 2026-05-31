from .base import BaseAgent
from typing import Dict, Any

class SimpleAgent(BaseAgent):
    """
    Fastest agent. 
    Purpose: Quick responses without heavy tools or memory.
    Best for: Simple questions, greetings, basic info.
    """
    
    def __init__(self, llm_client, short_term_memory):
        super().__init__(
            llm_client=llm_client,
            short_term_memory=short_term_memory,
        )
        self.llm_client = llm_client
        self.short_term_memory = short_term_memory

    def run(self, user_query: str) -> Dict[str, Any]:
        prompt = f"""You are a helpful assistant. Answer the following question clearly and concisely.

Question: {user_query}

Answer:"""
        
        # Step 3: Call LLM
        response = self.llm.invoke(prompt)
        self.short_term_memory.add_message("user", user_query)
        self.short_term_memory.add_message("assistant", response.content)
        return {
            "answer": response.content,
            "agent_type": "simple",
        }