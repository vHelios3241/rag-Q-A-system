from fastapi import APIRouter
import time

from ..models import ChatRequest, ChatResponse
from ..deps import get_search_service, get_llm
from ..config import settings
from ...retrieval.search_service import RetrievalConfig
from ...llm.rag import generate_answer

router = APIRouter(
    prefix="/chat",
    tags=["对话"]
)


@router.post("/", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """RAG 对话"""
    start_time = time.time()

    # 确定使用的提供商
    provider = request.model or settings.DEFAULT_PROVIDER

    # 获取 LLM
    llm = get_llm(provider)

    # 检索
    search_service = get_search_service(request.collection_name)        # 获取检索服务
    search_config = RetrievalConfig(top_k=settings.SEARCH_TOP_K)        # 创建检索配置对象
    search_response = search_service.search(request.query, search_config)    # 检索

    # 生成答案
    result = generate_answer(
        llm=llm,
        question=request.query,
        results=search_response.results,
        temperature=settings.LLM_TEMPERATURE,
        max_token=settings.LLM_MAX_TOKENS
    )

    # 构建来源
    sources = [
        {
            "content": r["content"][:200] + "..." if len(r["content"]) > 200 else r["content"],
            "id": r["id"],
            "score": r["score"]
        }
        for r in search_response.results[:3]
    ]

    total_time_ms = int((time.time() - start_time) * 1000)

    return ChatResponse(
        query=request.query,
        answer=result["answer"],
        sources=sources,
        token_used=result["token_used"],
        total_time_ms=total_time_ms
    )