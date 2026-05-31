from typing import Dict

PROMPTS: Dict[str, Dict[str, str]] = {
    "v1": {
        "simplify": """You are a query optimizer.
Rewrite the following user question to be clear, concise, and grammatically correct.
Remove filler words and fix typos. Keep the original intent.

User Query: {query}

Rewritten Query:""",

        "decompose": """You are a query analyst.
Break down this complex query into 2-4 simpler sub-queries that cover different aspects.

User Query: {query}

Sub-queries (one per line):"""
    }
}

def get_available_strategies(version: str = "v1"):
    if version not in PROMPTS:
        version = "v1"
    strategies = list(PROMPTS[version].keys())
    return strategies

def get_prompt(strategy: str, version: str = "v1"):
    if version not in PROMPTS:
        version = "v1"
    if strategy not in PROMPTS[version]:
        strategy = "simplify"
    return PROMPTS.get(version).get(strategy), strategy
