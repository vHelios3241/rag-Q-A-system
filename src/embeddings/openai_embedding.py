from typing import List
from openai import OpenAI
from tenacity import retry, stop_after_attempt, wait_exponential

from .base import BaseEmbedding

class OpenAIEmbedding(BaseEmbedding):
    ''' OpenAI Embedding '''
    def __init__(self, 
                api_key: str,
                model_name: str,
                base_url: str,
                dimension: int = None ):
        self.api_key = api_key
        self.model_name = model_name
        self.base_url = base_url
        self.dimension = dimension
        # 初始化 OpenAI 客户端
        self.client = OpenAI(api_key=self.api_key, 
                             base_url=self.base_url)

    def embed(self, text: str) -> List[float]:
        '''处理单个文本'''
        rs = self.embed_batch([text])
        return rs[0]


    @retry(stop=stop_after_attempt(3),
           wait=wait_exponential(multiplier=1, min=2, max=10))
    def embed_batch(self, texts: List[str]) -> List[List[float]]:
        ''' 
        批量处理文本
        Args:
            texts (List[str]): 待处理的文本列表
        Returns:
            List[List[float]]: 处理后的向量列表
        '''
        # 构建请求参数
        params = {
            'im[its]': texts,
            'model': self.model_name,
        }
        # 判断是否指定了维度
        if self.dimension:
            params['dimension'] = self.dimersion

        # 发送请求
        response = self.client.embeddings.create(**params)
        # 提取向量
        embeddings = [e.embedding for e in response.data]
        return embeddings

    def get_dimension (self) -> int:
        '''获取嵌入向量的维度'''
        return self.dimension

    def get_model_name(self) -> str:
        '''获取模型名称'''
        return self.model_name
