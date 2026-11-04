import uuid
import logging
from typing import List, Dict, Optional, Any
import chromadb

from .vector_store import BaseVectorStore, Document, SearchResult


class ChromaVectorStore:
    '''Chromadb向量存储'''

    def __init__(self,
                 collection_name: str = "rag_documents",
                 persist_directory: str = "./data/chroma_db",
                 distance: str = "cosine"
                 ):
        '''
        初始化Chromadb向量存储
        :param collection_name: 集合名称
        :param persist_directory: 持久化目录
        :param distance: 距离度量（cosine / l2 / ip）
        '''

        self.collection_name = collection_name
        self.distance = distance

        # 创建客户端（持久化）
        self.client = chromadb.PersistentClient(path=persist_directory)

        # 获取或创建集合
        self.collection = self.client.get_or_create_collection(
            name=self.collection_name,                  # 集合名称
            metadata={"hnsw:space": self.distance}      # 设置距离度量
        )

    def add_documents(self,
                      documents: List[Document],
                      embeddings: List[List[float]]
                      ) -> List[str]:
        '''添加文档到向量库'''
        ids = []
        texts = []
        metadatas = []

        for doc in documents:
            doc_id = doc.id or str(uuid.uuid4())
            ids.append(doc_id)
            metadatas.append(doc.metadata if doc.metadata else None)
            texts.append(doc.content)

        # 批量添加
        self.collection.add(
            ids=ids,
            embeddings=embeddings,
            documents=texts,
            metadatas=metadatas
        )

        return ids

    def search(
        self,
        query_embedding: List[float],
        top_k: int = 5,
        filter: Optional[Dict[str, Any]] = None
    ) -> List[SearchResult]:
        '''向量检索'''
        results = self.collection.query(
            query_embeddings=[query_embedding],
            n_results=top_k,
            where=filter
        )

        # 格式化
        search_results = []
        if results['ids'] and results['ids'][0]:
            for i, doc_id in enumerate(results['ids'][0]):
                search_results.append(SearchResult(
                    document=Document(
                        id=doc_id,
                        content=results['documents'][0][i],
                        metadata=results['metadatas'][0][i] if results.get(
                            'metadatas') else {}
                    ),
                    score = 1 -results['distances'][0][i] if results.get('distances') else 0.0,
                    metadata={}
                ))

        return search_results

    def get_collection_stats(self) -> Dict[str, int]:
        """获取集合统计信息"""
        return {
            "count": self.collection.count(),
            "name": self.collection_name,
            "distance": self.distance
        }

    def clear(self) -> bool:
        """清空集合"""
        try:
            self.client.delete_collection(name=self.collection_name)
            self.collection = self.client.create_collection(
                name=self.collection_name,
                metadata={"hnsw:space": self.distance}
            )
            return True
        except Exception as e:
            logging.error(f"清空集合失败: {e}")
            return False