
from abc import ABC, abstractmethod  # 负责创建抽象类
from typing import List, Dict
from dataclasses import dataclass 

# 定义接口规范

@dataclass
class ParseResult:
    '''解析结果统一格式'''
    filename: str        # 文件名
    total_pages: int     # 总页数
    total_chunks: int    # 文本块数
    table_count: int     # 表格数
    chunks: List[Dict]   # 文本块列表
    raw_text: str        # 原始文本
    tables: List[Dict]   # 表格列表
    metadata: Dict       # 其他元数据

class BaseParser(ABC):
    '''
    文档解析基类
    '''
    @abstractmethod
    def parse(self,file_path:str) -> ParseResult:
        '''
        解析文档文件
        Args:
            file_path: 文件路径
        Returns:
            dict: 解析结果
        '''
        pass

    @abstractmethod
    def parse_from_bytes(self,file_bytes: bytes,filename:str) -> ParseResult:
        '''
        解析文档字节流
        Args:
            file_bytes:文件字节流
            filename: 文件名
        Returns:
            dict: 解析结果
        '''
        # 这是一个方法定义，用于从字节流中解析文档
        # 接收两个参数：文件字节流和文件名
        # 返回一个解析结果对象
        # 目前方法体为空，使用 pass 占位
        pass

    @abstractmethod
    def support_extensions(self) -> list[str]:
        '''
        返回支持的文件扩展名
        Returns:
            支持的扩展名列表,如['docx','pdf']
        '''
        pass