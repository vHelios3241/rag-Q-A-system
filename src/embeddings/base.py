from abc import ABC, abstractmethod  # 抽象基类, 抽象方法
from typing import List

class BaseEmbedding(ABC):
    ''' 嵌入模型抽象类 '''

    @abstractmethod
    def embed(self, text: str) -> List[float]:
        ''' 
        嵌入单个文本
        Args:
            text (str): 待嵌入的文本
        Returns:
            List[float]: 嵌入后的向量
        '''
        pass

    @abstractmethod
    def embed_batch(self, texts: List[str]) -> List[List[float]]:
        ''' 
        批量嵌入文本
        Args:
            texts (List[str]): 待嵌入的文本列表
        Returns:
            List[List[float]]: 嵌入后的向量列表
        '''
        pass

    @abstractmethod
    def get_dimension (self) -> int:
        ''' 
        获取嵌入向量的维度
        Returns:
            int: 嵌入向量的维度
        '''
        pass

    @abstractmethod
    def get_model_name(self) -> str:
        ''' 
        获取模型名称
        Returns:
            str: 模型名称
        '''
        pass