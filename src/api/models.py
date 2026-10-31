from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional

class ChatRequest(BaseModel):
  """对话请求"""
  query: str = Field(..., description="用户问题")
  collection_name: str = Field("default", description="集合名称")
  model: Optional[str] = Field(None, description="提供商名称：zhipu 或 qwen（不传则使用默认）")


class ChatResponse(BaseModel):
  """对话响应"""
  query: str
  answer: str
  sources: List[Dict[str, Any]]
  token_used: Dict[str, int]
  total_time_ms: int
