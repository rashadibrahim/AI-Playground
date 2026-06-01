from services.query_rewriter.service import rewriter
from langchain.tools import tool
from services.semantic_cache.service import SemanticCache
import threading

semantic_cache = SemanticCache(db_dir="./databases/rewriter_cache")

@tool("query_rewriter")
def query_rewriter_tool(query: str, strategy: str) -> str:
  """
  Rewrites the input query based on the specified strategy using the QueryRewriter service.
  Available strategies:
  - "simplify": Simplifies complex queries into more straightforward language.
  - "decompose": Decomposes a query into its components for better understanding.
  """
  if strategy not in rewriter.available_strategies:
      raise ValueError(f"Strategy '{strategy}' is not supported. Available strategies: {rewriter.available_strategies}")
    
  result = semantic_cache.get_similar(query, metadata={"strategy": strategy})
  if result["response"]:
      return result["response"]
  else:
      rewritten = rewriter.rewrite(query, strategy=strategy)
      threading.Thread(
        target=semantic_cache.add_to_cache,
        args=(query, rewritten["rewritten"], {"strategy": strategy}),
        daemon=True
      ).start()
      return rewritten["rewritten"]

