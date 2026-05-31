from services.memory.long_term import LongTermMemory
from langchain.tools import tool

ltm = LongTermMemory()

@tool
def get_user_facts(query: str = "", top_k:int = 5) -> str:
    """Retrieve relevant facts about the user. Use this when you need context about the user."""
    facts = ltm.get_relevant_facts(query=query, top_k=top_k)
    return str(facts) if facts else "No relevant facts found."

@tool
def store_user_facts(fact: str, importance: float = 0.5) -> str:
    """Store a new fact about the user.
    Use this when the user shares something important to remember."""
    success = ltm.add_fact(fact, importance=importance)
    return success
