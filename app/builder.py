from typing import Optional
import uuid
from langchain_groq import ChatGroq
from agents.router import AgentRouter
from services.memory.short_term import ShortTermMemory
from services.rag_pipeline.service import RAGPipeline
from services.document_loader.service import loader
from .app import App
import datetime


class AppBuilder:

    def __init__(self):
      self._model = "qwen/qwen3-32b"
      self._agent_name: Optional[str] = None
      self._session_id: Optional[str] = None
      self._session_name: Optional[str] = None
      self._tools = []
      self._load_new_docs = False
      self._rag_pipeline: Optional[RAGPipeline] = None

    def with_model(self, model: str):
      self._model = model

    def with_agent(self, agent_name: str):
      self._agent_name = agent_name

    def with_session_info(self, session_id: Optional[str]=None, session_name: Optional[str]=None):
      self._session_id = session_id
      self._session_name = session_name

    def with_new_documents(self):
      self._load_new_docs = True

    def with_tools(self, tools_list):
      self._tools = tools_list

    def _build_llm(self):
      return ChatGroq(model=self._model, temperature=0, max_tokens=None, reasoning_format="parsed", timeout=None, max_retries=2)

    def _build_short_term_memory(self, enable_summarization=False):
      sid = self._session_id or str(uuid.uuid4())
      sname = self._session_name or f"Session {datetime.datetime.now().strftime('%Y-%m-%d %H:%M')}"
      return ShortTermMemory(session_id=sid, session_name=sname, enable_summarization=enable_summarization)

    def _build_rag(self):
      return RAGPipeline()

    def build(self) -> App:
      rag = None
      if self._agent_name == "simple":
        stm = self._build_short_term_memory()
      elif self._agent_name == "rag_memory":
        stm = self._build_short_term_memory(enable_summarization=True)
        rag = self._build_rag()
      else:
        rag = self._build_rag()
        stm = self._build_short_term_memory()
      
      if self._load_new_docs and rag is not None:
        docs = loader.load_new_documents()
        rag.ingest_documents(docs)
        
      if len(self._tools) == 0 and self._agent_name == "advanced":
        from tools.tools import tools_available
        """
        Added the import here so that if we load new docs we make sure that the retrieval tool has an
        updated description reflecting the new documents.
        """
        self._tools = tools_available

      llm = self._build_llm()

      router = AgentRouter(
          llm_client=llm,
          short_term_memory=stm,
          rag_pipeline=rag,
          agent=self._agent_name,
          tools=self._tools,
      )

      app = App(router=router, session_id=stm.session_id)
      return app
