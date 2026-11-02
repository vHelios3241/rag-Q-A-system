
import time
from typing import Optional, Dict, Any, List
from dataclasses import dataclass

from src.database.document_store import DocumentStore


class RetrievalConfig:
    """检索配置"""
    top_k: int=5
    min_score: float = 0.0        # 最低分数阈值
    namespace: Optional[str] = None    # 命名空间过滤
    metadata_filter: Optional[Dict] = None # 元数据过滤

@dataclass
class SearchResponse:
    '''搜索响应'''
    query: str                       # 查询文本
    total_results: int               # 结果总数
    results: List[Dict[str, Any]]    # 结果列表
    retrieval_time_ms: int           # 检索耗时

class SearchService:
    '''检索服务 - 统一的检索入口'''
    def __init__(self,
                 document_store: DocumentStore):
        """
        初始化检索服务
        Args:
          document_store: 文档存储实例
        """
        self.store = document_store

    def search(self,
               query: str,
               config: Optional[RetrievalConfig] = None,
               ) -> SearchResponse:
        """
        执行检索
        Args:
          query: 查询文本
          config: 检索配置
        Returns:
          检索响应
        """
        # 记录开始时间
        start_time = time.time()
        # 获取检索配置(没有传配置就使用默认配置)
        if config is None:
            config = RetrievalConfig()
        # 将查询转换为向量
        query_embedding = self.store.embedding_model.embed(query)
        # 构建过滤条件
        filter = self._build_filter(config)
        # 执行检索
        raw_results = self.store.search(
            query_embedding=query_embedding,
            top_k=config.top_k,
            namespace=config.namespace,
            filter=filter
        )
        # 把候选文档整理成字典，过滤低分结果
        results = [
            {
                "content": r.document.content,
                "doc_id": r.document.id,
                "score": r.score,
                "metadata": r.document.metadata
            }
            for r in raw_results
        ]
        results = [r for r in results if r["score"] >= config.min_score]
        results = results[:config.top_k]
        # 计算耗时，返回响应结果
        retrieval_time_ms = int((time.time() - start_time) * 1000)
        return SearchResponse(
            query=query,
            total_results=len(raw_results),
            results=results,
            results=results,
            retrieval_time_ms=retrieval_time_ms
        )

    def _build_filter(self, config: RetrievalConfig) -> Optional[Dict]:
        """构建过滤条件"""
        filter_condition = {}

        if config.namespace:
          filter_condition["namespace"] = config.namespace

        if config.metadata_filter:
          filter_condition.update(config.metadata_filter)

        return filter_condition if filter_condition else None

    def get_stats(self) -> Dict[str, Any]:
        """获取检索服务统计信息"""
        return self.store.get_stats()
