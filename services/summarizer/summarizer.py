from typing import List, Dict
from langchain_groq import ChatGroq
from dotenv import load_dotenv
load_dotenv()

class Summarizer:
    def __init__(self):
        self.llm_client = ChatGroq(model="qwen/qwen3-32b", temperature=0, reasoning_format="parsed", timeout=None, max_retries=2)
    
    def summarize_conversation(self, messages: List[Dict]) -> str:
        
        conversation_text = "\n".join([
            f"{msg['role']}: {msg['content']}" for msg in messages
        ])
        
        prompt = f"""Summarize the following conversation in 3-6 sentences. 
          Focus on key facts, user preferences, decisions, and important context.

          Conversation:
          {conversation_text}

          Summary:"""

        response = self.llm_client.invoke([{"role": "user", "content": prompt}])
        return response.content.strip()
    
    def summarize_text(self, text: str) -> str:
                
        prompt = f"""Summarize the following text in 3-6 sentences, focusing on key points and important details.

          Text:
          {text}

          Summary:"""

        response = self.llm_client.invoke([{"role": "user", "content": prompt}])
        return response.content.strip()