from services.rag_pipeline.service import RAGPipeline
from langchain_core.tools import tool
from services.document_loader.tracker import IngestionTracker

tracker = IngestionTracker()
docs_names = ", ".join(tracker.get_loaded_files())
tool_decr = """Retrieve information from the ingested documents on these available topics:
    {docs_names}
    
    Use this tool for any question related to the topics above.
    """
@tool(description=tool_decr.format(docs_names=docs_names))
def retrieve(query: str) -> str:
        
        try:
          rag = RAGPipeline()
          result = rag.simple_query(user_query=query)

          return result
        except Exception as e:
           return f"Error retrieving information: {str(e)}"
  