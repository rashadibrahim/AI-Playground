from typing import Dict
import time
from langchain_groq import ChatGroq
from .prompts import get_prompt, get_available_strategies
from dotenv import load_dotenv
load_dotenv()

class QueryRewriter:
    def __init__(self):
        self.llm_client = ChatGroq(model="qwen/qwen3-32b", temperature=0, reasoning_format="parsed", timeout=None, max_retries=2)
        self.default_version = "v1"
        self.available_strategies = get_available_strategies(self.default_version)

    def _validate_input(self, query: str, strategy: str) -> None:
        if not query or not isinstance(query, str):
            raise ValueError("Query must be a non-empty string")
        if len(query.strip()) < 3:
            raise ValueError("Query is too short")
        if len(query) > 2000:
            raise ValueError("Query is too long (max 2000 chars)")
        if strategy not in self.available_strategies:
            raise ValueError(f"Strategy '{strategy}' is not supported. Available strategies: {self.available_strategies}")

    def _call_llm(self, prompt: str) -> str:
        response = self.llm_client.invoke([("system", prompt)])
        return response.content.strip()

    def rewrite(self, query: str, strategy: str = "simplify", version: str = None) -> Dict:
        try:
            self._validate_input(query, strategy)
            version = version or self.default_version
            
            prompt, strat = get_prompt(strategy, version)
            
            rewritten= self._call_llm(prompt.format(query=query))
            

            
            return {
                "original": query,
                "rewritten": rewritten,
                "strategy": strat,
                "version": version,
                "metadata": {
                    "timestamp": time.time(),
                    "success": True
                }
            }
        except Exception as e:
            return {
                "original": query,
                "rewritten": query,
                "strategy": strategy,
                "version": version,
                "metadata": {
                    "timestamp": time.time(),
                    "success": False,
                }
            }

    def advanced_rewrite(self, query: str) -> Dict:
        """Example of prompt chaining"""
        step1 = self.rewrite(query, "simplify")
        
        step2 = self.rewrite(step1["rewritten"], "decompose")
        
        return {
            "original": query,
            "final": step2["rewritten"],
            "chain": [step1, step2],
            "strategy": "chained_simplify_expand"
        }