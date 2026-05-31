from typing import Dict, List

# from ..query_rewriter.service import rewriter
# from ..semantic_cache.service import SemanticCache

from .document_store import DocumentStore
from .document_processor import DocumentProcessor
from .strategies.parent_child import ParentChildStrategy
from .strategies.summary import SummaryStrategy
from langchain_groq import ChatGroq 


class RAGPipeline:
    def __init__(self, strategy_type: str = "parent_child"):
        
        self.llm_client = ChatGroq(model="qwen/qwen3-32b", temperature=0, reasoning_format="parsed", timeout=None, max_retries=2)
        
        # self.rewriter = rewriter
        # self.semantic_cache = SemanticCache(similarity_threshold=0.83, enable_ttl=True)
        # self.memory = MemoryService()
        
        self.document_store = DocumentStore()
        
        if strategy_type == "parent_child":
            self.strategy = ParentChildStrategy()
        elif strategy_type == "summary":
            self.strategy = SummaryStrategy()
        else:
            raise ValueError("strategy_type must be 'parent_child' or 'summary'")
        
        self.processor = DocumentProcessor(self.strategy, self.document_store)
        

    def ingest_documents(self, documents: List[Dict]):
        """Receive documents from external loader service"""
        if not documents:
            return
        self.processor.ingest_documents(documents)

    def simple_query(self, user_query: str) -> str:
        """Basic retrieval without rewriting or memory context (for testing)"""
        retrieved = self.processor.retrieve(user_query, self.strategy.get_name())
        return retrieved if retrieved else "No relevant information found."
    
#     def query(self, user_query: str, session_id: str) -> Dict[str, Any]:
        
#         # 1. Rewrite query
#         rewritten = self.rewriter.rewrite(user_query, strategy="simplify")
#         optimized_query = rewritten["rewritten"]
        
#         # 2. Semantic Cache
#         def generate_answer(q: str) -> str:
#             return self._generate_final_answer(q, session_id)
        
#         cache_result = self.semantic_cache.get_or_compute(optimized_query, generate_answer)
        
#         # 3. Save to memory
#         self.memory.add_to_conversation(session_id, "user", user_query)
#         self.memory.add_to_conversation(session_id, "assistant", cache_result["response"])
        
#         return {
#             "answer": cache_result["response"],
#             "rewritten_query": optimized_query,
#             "strategy": self.strategy.get_name()
#         }
    
#     def _generate_final_answer(self, query: str, session_id: str) -> str:
#         # Retrieve from vector store
#         retrieved = self.document_store.retrieve(query, top_k=5)
        
#         # Get memory context
#         mem_context = self.memory.get_relevant_context(query, session_id)
        
#         # Build prompt
#         prompt = self._build_prompt(query, retrieved, mem_context)
        
#         if not self.llm_client:
#             return "[Mock Answer] Based on retrieved documents."
        
#         response = self.llm_client.invoke([{"role": "user", "content": prompt}])
#         return response.content.strip()
    
#     def _build_prompt(self, query: str, retrieved: List[Dict], mem_context: Dict) -> str:
#         context_text = "\n\n".join([
#             f"Source: {d['metadata'].get('source')}\n{d['content']}" 
#             for d in retrieved
#         ])
        
#         return f"""Answer the question using the provided context:

# Question: {query}

# Context:
# {context_text}

# Answer:"""