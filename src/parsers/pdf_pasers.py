from pathlib import Path
from typing import List,Optional

from docling.document_converter import DocumentConverter,PdfFormatOption
from docling.datamodel.base_models import InputFormat
from docling.datamodel.pipeline_options import PdfPipelineOptions

from src.parsers.base import BaseParser, ParseResult
from src.parsers.chunker import TextChunker
from src.parsers.cleaner import TextCleaner
from src.parsers.table_parser import TableProcessor


# PDF 解析器

class PDFParser(BaseParser):                    # 继承父类
    """基于Docling的PDF解析器"""

    def __init__(self,                           # 构造函数
                 chuncker: Option[TextChunker] = None,
                 cleaner: Option[TextCleaner] = None,
                 table_parser: Option[TableProcessor] = None):
        '''
        Args:
          chunker: 文本分块器
          cleaner: 文本清理器
          table_parser: 表格处理器
        '''
        # 初始化Docling转换选项
        pipeline_options = PdfPipelineOptions()
        pipeline_options.do_ocr = True           # 启用OCR
        pipeline_options.do_table_structure = True     # 启用表格结构识别

        # 初始化组件(传入一个自定义的文本分块器。如果不传入，就会使用默认的)
        self.chunker = chuncker if chuncker else TextChunker()
        self.cleaner = cleaner if cleaner else TextCleaner()
        self.table_parser = table_parser if table_parser else TableParser()

        # 初始化转换器
        self.converter = DocumentConverter(
            format_options={
                InputFormat.PDF: PdfFormatOption(
                    pipeline_options=PdfPipelineOptions()
                ),
            }
        )

    # 从文件路径解析

    def parse(self, file_path: str) -> ParseResult:
        # 使用Docling转换为Document对象
        doc = self.converter.convert(file_path)
        # 提取内容
        raw_text = doc.document.export_to_markdown()
        # 提取表格
        tables = self._extract_tables(doc)

        # 处理流程
        cleaned_text = self.cleaner.clean(raw_text)
        merged_tables = self.table_parser.merge_tables(tables)
        chunks = self.chunker.split(cleaned_text, merged_tables)

        return ParseResult(                             # 组装返回结果
           filename=Path(file_path).name,               # "产品手册.pdf"
           total_pages=len(doc.document.pages),         # 总页数
           total_chunks=len(raw_text),                  # 这是字符数不是块数
           table_count=len(merged_tables),              # 表格数量
           chunks=chunks,                               # 分块数据
           raw_text=cleaned_text,                       # 完整 Markdown 文本
           tables=merged_tables,                        # 表格数据
           metadata={"parse": "docling", "file_path": file_path}  # 解析器信息
           )

    # 从字节流解析
    def parse_from_bytes(self, file_bytes: bytes, filename: str) -> ParseResult:
        doc = self.converter.convert(file_bytes)
        raw_text = doc.document.export_to_markdown()
        tables = self._extract_table(doc)

        # 处理流程
        cleaned_text = self.cleaner.clean(raw_text)
        marged_tables = self.table_parser.merge_tables(tables)
        chunks = self.chunker.split(cleaned_text, marged_tables)

        return ParseResult(
          filename=Path(file_path).name,
          total_pages=len(doc.document.pages),
          total_chunks=len(chunks),
          table_count=len(marged_tables),
          chunks=chunks,
          raw_text=cleaned_text,
          tables=marged_tables,
          metadata={"parser":"docling","file_path":file_path}
            )

    # 以 _ 开头 = 私有方法,只能在类内部调用
    # 提取表格。 hasattr(obj, "xxx")：检查对象有没有某个属性
    def _extract_table(self, doc) -> list:
        tables = []
        # hasattr(obj, "xxx")：检查对象有没有某个属性
        if not hasattr(doc.document, "tables") or not doc.document.tables:
            return tables
        # 两个变量是因为 enumerate 返回的结果里本身就包含两个东西（编号和对象）（参数1：要遍历的东西，参数2：起始编号）
        for i, table in enumerate(doc.document.tables, 1):
            try:
                prov = getattr(table, "prov", [])
                page_no = prov[0].page_no if prov else None
                md = table.export_to_markdown(doc=doc.document)

                cols, rows = self._parse_table_shape(md)

                table_data = {
                    "table_number": i,
                    "page": page_no,
                    "markdown": md,
                    "cols": cols,
                    "rows": rows,
                }
                tables.append(table_data)
            except Exception as e:
                print(f"警告：无法处理表格 {i}: {e}")
                continue

        return tables

    def _parse_table_shape(self, md: str) -> tuple:
        lines = [l.strip() for l in md.strip().split('\n') if l.strip()]
        if len(lines) < 2:
            return 0, 0
        cols = len([c for c in lines[0].split('|') if c.strip()])
        data_lines = lines[2:] if len(lines) > 2 else []
        rows = len([l for l in data_lines if '|' in l])
        return cols, rows

    # 返回支持的文件扩展名

    def support_extensions(self) -> list[str]:
        return [".pdf", ".PDF"]
