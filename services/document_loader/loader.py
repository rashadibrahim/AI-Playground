from pathlib import Path
from typing import List, Dict
from datetime import datetime

from langchain_community.document_loaders import (
    TextLoader,
    PyPDFLoader,
    UnstructuredHTMLLoader
)
from markitdown import MarkItDown
from langchain_core.documents import Document

from .tracker import IngestionTracker


class DocumentLoader:
    """
    Responsible for loading documents from a directory using LangChain loaders.
    Tracks already ingested files to avoid duplicates.
    """
    
    def __init__(self):
        self.documents_dir = Path("./data/documents")
        self.documents_dir.mkdir(parents=True, exist_ok=True)
        
        self.tracker = IngestionTracker()
        
        self.loader_mapping = {
            ".txt": TextLoader,
            ".md": TextLoader,
            ".pdf": PyPDFLoader,
            ".html": UnstructuredHTMLLoader,
            ".htm": UnstructuredHTMLLoader,
        }
    
    def load_new_documents(self) -> List[Dict]:
        """
        Scan directory for new files, load them using MARKITDOWN, and return in RAG-ready format.
        """
        new_files = self.tracker.get_new_files(str(self.documents_dir))
        print(f"Found {len(new_files)} new files to ingest.")
        if not new_files:
            return []
        
        loaded_documents = []
        
        for file_path in new_files:
            
            try:
                md = MarkItDown(enable_plugins=True)
                result = md.convert(str(file_path))
                
                md_doc = Document(
                    page_content=result.text_content,
                    metadata={
                        "title": result.title,
                    })

                processed_doc = self._convert_to_rag_format(md_doc, file_path)
                loaded_documents.append(processed_doc)
                
                self.tracker.mark_as_ingested(str(file_path))
                
            except Exception as e:
                continue
        
        return loaded_documents
    
    def load_new_documents_langchain(self) -> List[Dict]:
        """
        Scan directory for new files, load them using LangChain Loaders, and return in RAG-ready format.
        """
        new_files = self.tracker.get_new_files(str(self.documents_dir))
        
        if not new_files:
            return []
        
        loaded_documents = []
        
        for file_path in new_files:
            
            try:
                loader = self._get_loader_for_file(file_path)
                
                if loader is None:
                    continue
                
                langchain_docs = loader.load()
                
                for doc in langchain_docs:
                    processed_doc = self._convert_to_rag_format(doc, file_path)
                    loaded_documents.append(processed_doc)
                
                self.tracker.mark_as_ingested(str(file_path))
                
            except Exception as e:
                continue
        
        return loaded_documents

    def _get_loader_for_file(self, file_path: Path):
        suffix = file_path.suffix.lower()
        
        if suffix in self.loader_mapping:
            loader_class = self.loader_mapping[suffix]
            return loader_class(str(file_path))
        
        return None

    def _convert_to_rag_format(self, langchain_doc: Document, original_file_path: Path) -> Dict:
        """
        Convert LangChain Document to the format expected by RAGPipeline.
        """
        return {
            "content": langchain_doc.page_content.strip(),
            "source": str(original_file_path),
            "metadata": {
                **langchain_doc.metadata,
                "loaded_at": datetime.now().isoformat(),
            }
        }