from fastapi import HTTPException
from .config import settings
from ..database.document_store import DocumentStore
from ..embeddings.local_embedding import LocalEmbedding
from ..retrieval.search_service import SearchService
from ..llm import LLM

def get_search_service(collection_name: str = "default"):
  """获取检索服务"""
  embedding_model = LocalEmbedding(model_name="BAAI/bge-small-zh-v1.5")
  store = DocumentStore(
    embedding_model=embedding_model,
    collection_name=collection_name
   )
  return SearchService(document_store=store)