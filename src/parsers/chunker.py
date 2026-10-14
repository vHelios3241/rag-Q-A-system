from typing import List, Dict, Optional
import re

''' 智能分块'''

class ChunkStrategy:
  """分块策略枚举"""
  PARAGRAPH = "paragraph"  # 按段落分块
  SENTENCE = "sentence"    # 按句子分块
  CHARACTER = "character"  # 按字符数分块
  SEMANTIC = "semantic"    # 语义分块（阶段三，使用模型）

class TextChunker:
  """文本分块器"""

  def __init__(
    self,
    strategy: str = ChunkStrategy.PARAGRAPH,
    max_chunk_size: int = 1000,
    min_chunk_size: int = 100,
    chunk_overlap: int = 200,
   ):
    """
     初始化分块器

     Args:
       strategy: 分块策略
       max_chunk_size: 最大块大小（字符数）
       min_chunk_size: 最小块大小
       chunk_overlap: 块之间重叠字符数
     """
    self.strategy = strategy
    self.max_chunk_size = max_chunk_size
    self.chunk_overlap = chunk_overlap      # 块之间重叠字符数
    self.min_chunk_size = min_chunk_size

  def split(self, text: str, tables: Optional[List[Dict]] = None) -> List[Dict]:
    """
     分割文本

     Args:
       text: 待分块的文本
       tables: 表格列表（可选，用于保留表格结构）

     Returns:
       分块结果列表
     """
    if self.strategy == ChunkStrategy.PARAGRAPH:
      pass
    elif self.strategy == ChunkStrategy.SENTENCE:
      pass
    elif self.strategy == ChunkStrategy.CHARACTER:
      pass
    elif self.strategy == ChunkStrategy.SEMANTIC:
      pass


  def split_by_paragraph(self, text:str) -> List[Dict]: 
    """按段落分割"""
    chunk=[]
    paragraphs = text.split('\n\n')

    current_chunk = ""           # 当前块
    chunk_index = 0              # 当前块索引

    for paragraph in paragraphs:
      para = paragraph.strip()
      if not para:
        continue

      # 如果当前块长度加上新段落长度大于最大块大小，则需要分割
      if len(current_chunk) + len(para) + self.chunk_overlap > self.max_chunk_size:

        # 如果当前块长度大于最小块大小，则添加到分块结果
        if len(current_chunk) > self.min_chunk_size:
          chunk.append({
            "content": current_chunk.strip(),
            "index": chunk_index,
            "length": len(current_chunk),
            "type": "text"
          })
          chunk_index += 1

        # 如果段落太长，进一步分割
        if len(para) > self.max_chunk_size:
          sub_chunks = self._split_long_paragraph(para, chunk_index)
          chunk.extend(sub_chunks)
          chunk_index = len(chunk)
          current_chunk = ""
        else:
          # 保留重叠
          overlap_start = max(0, len(current_chunk) - self.chunk_overlap)
          current_chunk = current_chunk[overlap_start:] + "\n\n" + para
        
      else:
        # 如果当前块长度加上新段落长度小于最大块大小，则继续添加
        current_chunk = current_chunk + "\n\n" + para if current_chunk else para
    # 最后一块
    if current_chunk and len(current_chunk) >= self.min_chunk_size:
      pass



  def _split_by_sentence(self, text: str) -> List[Dict]:
    """按句子分割"""
    sentences = re.split(r'([。！？.!?]\s*)', text)
    # 重新组合句子和标点
    sentences = [''.join(pair) for pair in zip(sentences[::2], sentences[1::2])]

