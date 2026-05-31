from typing import Dict, Any
from .simple_agent import SimpleAgent
from .rag_memory_agent import RAGMemoryAgent
from .advanced_agent import AdvancedAgent

class AgentRouter:

    def __init__(self, llm_client, short_term_memory, rag_pipeline=None, agent=None, tools=[]):
        self.llm = llm_client
        self.agent = agent
        self.short_term_memory = short_term_memory
        
        self.agents = {
            "simple": SimpleAgent(llm_client),
            "rag_memory": RAGMemoryAgent(llm_client, short_term_memory=short_term_memory, rag_pipeline=rag_pipeline),
            "advanced": AdvancedAgent(llm_client, short_term_memory=short_term_memory, tools=tools)
        }

    def run(self, user_query: str) -> Dict[str, Any]:

        if self.agent:
            selected_agent = self.agents.get(self.agent)
            if not selected_agent:
                selected_agent = self.agents["rag_memory"]
        else:
          # Routing prompt
          routing_prompt = f"""
          You are an expert router. Analyze the user query and choose the best agent.

          Query: "{user_query}"

          Available Agents:
          - simple: For very simple, casual, or quick questions
          - rag_memory: When the user asks about their documents or conversation history
          - advanced: For complex, multi-step, or thoughtful responses

          Reply with ONLY one word: simple, rag_memory, or advanced
          """
          
          try:
              decision = self.llm.invoke(routing_prompt)
              choice = decision.content.strip().lower()
              
              if "advanced" in choice:
                  selected_agent = self.agents["advanced"]
              elif "rag_memory" in choice or "rag" in choice:
                  selected_agent = self.agents["rag_memory"]
              else:
                  selected_agent = self.agents["simple"]
                  
          except:
              # Fallback
              selected_agent = self.agents["rag_memory"]
        
        # Execute chosen agent
        result = selected_agent.run(user_query)
        
        return result
    