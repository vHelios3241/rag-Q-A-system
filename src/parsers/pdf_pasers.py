from pathlib import Path
from typing import List

from src.parsers.base import BaseParser, ParseResult
from docling.document_converter import DocumentConverter

# PDF 解析器


class PDFParser(BaseParser):                    # 继承父类
    """基于Docling的PDF解析器"""
    def __init__(self):                         # 构造函数，创建对象时自动调用
        self.converter = DocumentConverter()

    # 从文件路径解析
    def parse(self, file_path: str) -> ParseResult:
         doc = self.converter.convert(file_path)                # 用 Docling 把 PDF 变成结构化对象
         raw_text = doc.document.export_to_markdown()           # 提取纯文本，并转换为Markdown
         tables = self._extract_table(doc)                      # 提取表格

         return ParseResult(                                    # 组装返回结果
            filename=Path(file_path).name,               # "产品手册.pdf"
            total_pages=len(doc.pages),                  # 总页数
            total_chunks=len(raw_text),                  # 这是字符数不是块数
            table_count=len(tables),                     # 表格数量
            chunks=[],                                   # 空列表 —— Chunking 不在解析阶段做
            raw_text=raw_text,                           # 完整 Markdown 文本
            tables=tables,                               # 表格数据
            metadata={"parse": "docling", "file_path": file_path}  # 解析器信息
         )

    # 从字节流解析
    def parse_from_bytes(self, file_bytes: bytes, filename: str) -> ParseResult:
        doc = self.converter.convert(file_bytes)
        raw_text = doc.document.export_to_markdown()
        tables = self._extract_table(doc)

        return ParseResult(
            filename=filename,          # ← 直接用传入的 filename，不用 Path 解析
            total_pages=len(doc.pages),
            total_chunks=len(raw_text),
            table_count=len(tables),
            chunks=[],
            raw_text=raw_text,
            tables=tables,
            metadata={"parser": "docling", "file_path": filename}
    )

    # 以 _ 开头 = 私有方法,只能在类内部调用
    # 提取表格。 hasattr(obj, "xxx")：检查对象有没有某个属性
    def _extract_table(self, doc) -> list:
        tables = []
        if not hasattr(doc.document, "tables") or not doc.document.tables:   # hasattr(obj, "xxx")：检查对象有没有某个属性
            return tables
        for i, table in enumerate(doc.document.tables, 1):    # 两个变量是因为 enumerate 返回的结果里本身就包含两个东西（编号和对象）（参数1：要遍历的东西，参数2：起始编号）
            try:
                # 获取表格所在的页码（通过 prov 属性）
                prov = getattr(table, "prov", [])             # 在第几页
                page_no = prov[0].page_no if prov else None
                # 将表格数据添加到列表中
                table_data = {
                  "table_number": i,
                  "page": page_no,
                  "markdown": table.export_to_markdown(doc=doc.document),  # 提取表格的Markdown文本
                 }
                tables.append(table_data)
            except Exception as e:
                print(f"警告：无法处理表格 {i}: {e}")
                continue

        return tables


    # 返回支持的文件扩展名
    def support_extensions(self) -> list[str]:
        return [".pdf", ".PDF"]