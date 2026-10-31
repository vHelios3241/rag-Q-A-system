# 解析数据 - 向量 - 存储向量 - 检索向量 - 获取结果  
import uuid
from typing import Optional, List, Dict, Any
from src.embeddings.chroma_store import ChromaVectorStore
from src.embeddings.vector_store import Document
from src.parsers.base import ParseResult
from src.embeddings.base import BaseEmbedding


class DocumentStore:
    """文档存储服务 - 整合解析、向量化、存储"""

    def __init__(self, 
                 embedding_model: BaseEmbedding, 
                 vector_store: Optional[ChromaVectorStore] = None,
                 collection_name: str="rag_documents"
                 ):
        """
        初始化文档存储
        Args:
          embedding_model: 嵌入模型
          vector_store: 向量存储, 检索相似文档。默认使用 ChromaDB
          collection_name: 向量存储集合名称 
        """
        self.embedding_model = embedding_model
        self.vector_store = vector_store or ChromaVectorStore(
            collection_name=collection_name
        )


    def add_parse_result(self,
                         parser_result: ParseResult,
                         namespace: str = "default") -> List[str]:
        """添加解析结果到向量数据库
        Args:
          parser_result: 解析结果
          namespace: 命名空间
        Returns:
          文档ID列表
        """
        documents = []
        texts_to_embed = []

        # 整理数据
        for chunk in parser_result.chunks:
            # 文档id
            doc_id = f"{namespace}_{parser_result.filename}_{chunk['index']}"
            # 元数据（
            metadata={
                "filename": parser_result.filename,
                "chunk_index": chunk['index'],
                "chunk_type": chunk.get('type', 'text'),
                "namespace": namespace,
                "length": chunk['length']
            }

            # 如果是表格，添加页码
            if chunk.get('type') == 'table' and 'page' in chunk:
                metadata['page'] = chunk['page']

            # 保存文档对象
            documents.append(
                Document(
                    id=doc_id,
                    content=chunk['content'],
                    metadata=metadata
                    )
                )
            # 保存文本内容
            texts_to_embed.append(chunk['content'])

          # 批量生成向量
        embeddings = self.embedding_model.embed_batch(texts_to_embed)
      
          # 把“文档对象”和“对应向量”添加到向量库
        doc_ids = self.vector_store.add_documents(documents, embeddings)

        return doc_ids

    def add_documents(self,
                      texts: List[str],
                      metadatas: List[Dict[str, Any]],
                      namespace: str = "default") -> List[str]:
        """添加文档到向量数据库
        Args:
          texts: 文本列表
          metadatas: 元数据列表
          namespace: 命名空间
        Returns:
          文档ID列表
        """
        # 准备文档对象列表
        documents = []
        # 遍历每段文本和对应的元数据，创建Document对象
        for text, metadata in zip(texts, metadatas):
            # 处理元数据为空的情况
            meta = dict(metadata) if metadata else {}
            meta["namespace"] = namespace

            doc_id = f"{namespace}_{uuid.uuid4().hex[:8]}"
            documents.append(
                Document(
                    id=doc_id,
                    content=text,
                    metadata=meta
                )
            )
        # 批量将文本转为向量
        embeddings = self.embedding_model.embed_batch(texts)
        # 文档+向量存到向量库
        doc_ids = self.vector_store.add_documents(documents, embeddings)
        return doc_ids



    def search(self, 
               query: str,
               top_k: int = 5,
               namespace: str = "default"
               ) -> List[Dict[str,Any]]:
        """
        语义搜索
        Args:
            query: 查询文本
            top_k: 返回结果数
            namespace: 命名空间过滤
        Returns:
            检索结果列表
        """
        # 问题向量化
        query_embedding = self.embedding_model.embed(query)

        # 构建过滤条件
        filter_condition = {"namespace": namespace} if namespace else None

        # 检索相似文档(注意接受的是单个向量还是向量列表)
        results = self.vector_store.search(
            query_embedding = query_embedding,
            top_k=top_k,
            filter = filter_condition
        )

        # 返回检索列表
        return [
            {
                "id": r.document.id,
                "content": r.document.content,
                "score": r.score,
                "metadata": r.document.metadata
                }
                for r in results
                ]
    def get_stats(self) -> Dict[str, Any]:
        """获取存储统计信息"""
        # 从向量存储拉取集合统计
        stats = self.vector_store.get_collection_stats()
        # 返回模型标识
        stats['embedding_model'] = self.embedding_model.get_model_name()
        # 返回向量维度
        stats['embedding_dimension'] = self.embedding_model.get_dimension()

        return stats