from abc import abstractmethod

from dataclasses import dataclass, field
from typing import Dict, Any, Optional, List


'''统一文档数据模型'''


@dataclass
class Document:
    '''文档对象'''
    id: str                             # 文档ID
    content: str                        # 文档内容
    metadata: Dict[str, Any]            # 文档元数据
    embedding: Optional[List[float]] = None   # 文档嵌入向量


@dataclass
class SearchResult:
    '''搜索结果对象'''
    document: Document         # 文档
    score: float               # 相似度分数
    metadata: Dict[str, Any]   # 额外元数据得分


'''向量存储基类'''


class BaseVectorStore:

    @abstractmethod
    def add_document(self,
                     documents: List[Document],
                     embeddings: List[List[float]],
                     ) -> List[str]:
     '''
     添加文档到向量库
          Args:
            documents: 文档列表
            embeddings: 对应的向量列表
          Returns:
            文档ID列表
     '''
     pass

    @abstractmethod
    def search(self,
               top_k: int,
               query_embedding: List[float],
               filter: Optional[Dict[str, Any]] = None,
               ) -> List[SearchResult]:
        """
     向量检索

     Args:
       query_embedding: 查询向量
       top_k: 返回结果数量
       filter: 元数据过滤条件
     Returns:
       检索结果列表
     """
    pass


    @abstractmethod
    def get_collection_stats(self) -> Dict[str, int]:
        """
         获取集合统计信息
         Returns:
           统计信息（文档数、维度等）
         """
        pass

    @abstractmethod
    def clear(self) -> bool:
        """清空集合"""
        pass