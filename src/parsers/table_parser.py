from typing import List, Dict
import pandas as pd

class TableProcessor:
  """表格处理工具"""

  def markdown_to_dataframe(self, table_markdown: str) -> pd.DataFrame:
    """
     将Markdown表格转换为DataFrame

     Args:
       table_markdown: Markdown格式的表格

     Returns:
       pandas DataFrame
     """
    lines = [line.strip() for line in table_markdown.strip().split('\n') if line.strip()]

    if len(lines) < 2:
      return pd.DataFrame()

    # 解析表头
    headers = [cell.strip() for cell in lines[0].split('|')[1:-1]]

    # 跳过分隔线
    data_lines = lines[2:] if len(lines) > 2 else []

    # 解析数据行
    data = []
    for line in data_lines:
      if '|' in line:
        cells = [cell.strip() for cell in line.split('|')[1:-1]]
        if len(cells) == len(headers):
          data.append(cells)

    return pd.DataFrame(data, columns=headers)



  def table_to_text(self, table_markdown: str) -> str:
    """
     将表格转换为文本描述

     Args:
       table_markdown: Markdown格式的表格

     Returns:
       表格的文本描述
     """
    df = self.markdown_to_dataframe(table_markdown)

    if df.empty:
      return ""

    # 生成文本描述
    text_parts = []
    text_parts.append("表格内容：")

    # 添加表头
    text_parts.append(" | ".join(df.columns))

    # 添加数据行
    for _, row in df.iterrows():
      text_parts.append(" | ".join(str(v) for v in row))

    return "\n".join(text_parts)



  def merge_tables(self, tables: List[dict]) -> List[dict]:
    """
     合并跨页的拆分表格

     Args:
       tables: 表格列表

     Returns:
       合并后的表格列表
     """
    if len(tables) <= 1:
      return tables

    merged = [tables[0]]

    for i in range(1, len(tables)):
      current = tables[i]
      last = merged[-1]

      # 简单判断：如果列数相同且页码连续，可能是同一张表格
      if (current.get('cols') == last.get('cols') and
        current.get('page') == last.get('page') + 1):
        # 合并表格内容
        last['markdown'] += '\n' + current['markdown']
        last['rows'] += current['rows']
      else:
        merged.append(current)

    return merged
