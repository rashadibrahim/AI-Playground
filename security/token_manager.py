from datetime import datetime, timedelta
import tiktoken
from typing import Dict

class TokenManager:
    def __init__(self, max_tokens: int = 8000, daily_limit: int = 500_000):
        self.max_tokens_per_request = max_tokens
        self.daily_limit = daily_limit
        self.daily_usage = 0
        self.last_reset = datetime.now()
        self.encoder = tiktoken.get_encoding("cl100k_base") 

    def check_request(self, prompt: str) -> Dict:
        tokens = len(self.encoder.encode(prompt))
        
        if tokens > self.max_tokens_per_request:
            return {
                "allowed": False,
                "reason": f"Request exceeds max tokens ({tokens}/{self.max_tokens_per_request})",
                "tokens": tokens
            }
        
        if datetime.now() - self.last_reset > timedelta(days=1):
            self.daily_usage = 0
            self.last_reset = datetime.now()
        
        if self.daily_usage + tokens > self.daily_limit:
            return {
                "allowed": False,
                "reason": "Daily token limit exceeded",
                "tokens": tokens
            }
        
        return {
            "allowed": True,
            "tokens": tokens,
            "daily_usage": self.daily_usage
        }
    
    def record_usage(self, tokens: int):
        self.daily_usage += tokens
  
        
  