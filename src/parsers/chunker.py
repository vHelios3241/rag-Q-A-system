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
      chunks = self._split_by_paragraph(text)
    elif self.strategy == ChunkStrategy.SENTENCE:
      chunks = self._split_by_sentence(text)
    elif self.strategy == ChunkStrategy.CHARACTER:
      chunks = self._split_by_character(text)
    else:
      chunks = self._split_by_paragraph(text) # 默认按段落

    # 如果有表格，将表格作为单独的块
    if tables:
      chunks = self._attach_tables(chunks, tables)

    return chunks


  def _split_by_paragraph(self, text:str) -> List[Dict]: 
    """按段落分割"""
    chunks=[]
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
          chunks.append({
            "content": current_chunk.strip(),
            "index": chunk_index,
            "length": len(current_chunk),
            "type": "text"
          })
          chunk_index += 1

        # 如果段落太长，进一步分割
        if len(para) > self.max_chunk_size:
        # 段落本身就超长，单独二次拆分
          sub_chunks = self._split_long_paragraph(para, chunk_index)
          chunks.extend(sub_chunks)
          chunk_index = len(chunks)
          current_chunk = ""
        else:
            # 段落不长，拼进当前块，保留重叠部分
            overlap_start = max(0, len(current_chunk) - self.chunk_overlap)
            current_chunk = current_chunk[overlap_start:] + "\n\n" + para

      else:
        # 如果当前块长度加上新段落长度小于最大块大小，则继续添加
        current_chunk = current_chunk + "\n\n" + para if current_chunk else para

    # 最后一块
    if current_chunk and len(current_chunk) >= self.min_chunk_size:
      chunks.append({
        "content": current_chunk.strip(),
        "index": chunk_index,
        "length": len(current_chunk),
        "type": "text"
    })
      chunk_index += 1

    return chunks

  def _split_long_paragraph(self, text: str, start_index: int) -> List[Dict]:
    """
    分割过长的段落
    先尝试按句子切，如果单句也太长，再按字符硬切。
    """
    sentences = re.split(r'([。！？.!?]\s*)', text)     # 正则分割，匹配标点号，以及它们后面跟着的零个或多个空白字符，切成“内容 + 标点 + ...”交替的列表
    sentences = [''.join(pair) for pair in zip(sentences[::2], sentences[1::2])]

    chunks = []          # 最终产出的分块列表
    current_chunk = ""   # 正在累加的"当前块"
    chunk_index = start_index  # 块编号，上层传进来的起始序号（保证全局唯一）

    # 遍历句子
    for sent in sentences:
      # 如果当前块长度加上新句子长度大于最大块大小，则需要分割
      if len(current_chunk) + len(sent) > self.max_chunk_size:
        # 先把之前攒的那块提交，编号 +1，准备装新的块
        if current_chunk:
          chunks.append({
            "content": current_chunk.strip(),
            "index": chunk_index,
            "length": len(current_chunk),
            "type": "text"
           })
          chunk_index += 1

        # 新句子本身也超长 → 按字符硬切
        if len(sent) > self.max_chunk_size:
          for i in range(0, len(sent), self.max_chunk_size - self.chunk_overlap):
            sub_chunk = sent[i:i + self.max_chunk_size]
            if len(sub_chunk) >= self.min_chunk_size:
              chunks.append({
                "content": sub_chunk,
                "index": chunk_index,
                "length": len(sub_chunk),
                "type": "text"
               })
              chunk_index += 1
          current_chunk = ""
        else:
          current_chunk = sent
      else:
        current_chunk += sent

    # 提交最后一块
    if current_chunk and len(current_chunk) >= self.min_chunk_size:
      chunks.append({
        "content": current_chunk.strip(),
        "index": chunk_index,
        "length": len(current_chunk),
        "type": "text"
       })

    return chunks



  def _split_by_sentence(self, text: str) -> List[Dict]:
    """按句子分割"""
    sentences = re.split(r'([。！？.!?]\s*)', text)
    # 重新组合句子和标点
    sentences = [''.join(pair) for pair in zip(sentences[::2], sentences[1::2])]

    chunks = []
    current_chunk = ""
    chunk_index = 0

    for sent in sentences:
      sent = sent.strip()
      if not sent:
        continue

      if len(current_chunk) + len(sent) > self.max_chunk_size:
        if len(current_chunk) >= self.min_chunk_size:
          chunks.append({
            "content": current_chunk.strip(),
            "index": chunk_index,
            "length": len(current_chunk),
            "type": "text"
           })
          chunk_index += 1
        current_chunk = sent
      else:
        current_chunk += " " + sent if current_chunk else sent

    if current_chunk and len(current_chunk) >= self.min_chunk_size:
      chunks.append({
        "content": current_chunk.strip(),
        "index": chunk_index,
        "length": len(current_chunk),
        "type": "text"
       })

    return chunks


  def _split_by_character(self, text: str) -> List[Dict]:
    """按字符数分割"""
    chunks = []
    chunk_index = 0

    for i in range(0, len(text), self.max_chunk_size - self.chunk_overlap):
      chunk = text[i:i + self.max_chunk_size]
      if len(chunk.strip()) >= self.min_chunk_size:
        chunks.append({
          "content": chunk.strip(),
          "index": chunk_index,
          "length": len(chunk),
          "type": "text"
         })
        chunk_index += 1

    return chunks


  def _attach_tables(self, chunks: List[Dict], tables: List[Dict]) -> List[Dict]:
    """将表格作为单独的块附加到分块结果"""
    chunk_index = len(chunks)

    for table in tables:
      table_text = f"表格（第{table.get('page', '?')}页）：\n{table.get('markdown', '')}"
      chunks.append({
        "content": table_text,
        "index": chunk_index,
        "length": len(table_text),
        "type": "table",
        "page": table.get('page'),
        "table_data": table
       })
      chunk_index += 1

    return chunks