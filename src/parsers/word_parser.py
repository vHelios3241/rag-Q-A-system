from pathlib import Path
from typing import List, Optional

from docx import Document
from docx.table import Table

from src.parsers.base import BaseParser, ParseResult
from src.parsers.chunker import TextChunker
from src.parsers.cleaner import TextCleaner
from src.parsers.table_parser import TableProcessor

'''word解析器,基于python-docx的Word解析器'''
class WordParser(BaseParser):
    """基于python-docx的Word解析器"""

    def __init__(self,
                 chuncker: Optional[TextChunker] = None,
                 cleaner: Optional[TextCleaner] = None,
                 table_parser: Optional[TableProcessor] = None):
        '''
        Args:
          chunker: 文本分块器
          cleaner: 文本清理器
          table_parser: 表格处理器
        '''
        self.chunker = chuncker if chuncker else TextChunker()
        self.cleaner = cleaner if cleaner else TextCleaner()
        self.table_parser = table_parser if table_parser else TableProcessor()

    def parse(self, file_path: str) -> ParseResult:
        doc = Document(file_path)

        raw_text = self._extract_text(doc)
        tables = self._extract_tables(doc)

        cleaned_text = self.cleaner.clean(raw_text)
        merged_tables = self.table_parser.merge_tables(tables)
        chunks = self.chunker.split(cleaned_text, merged_tables)

        return ParseResult(
            filename=Path(file_path).name,
            total_pages=len(doc.paragraphs),
            total_chunks=len(chunks),
            table_count=len(merged_tables),
            chunks=chunks,
            raw_text=cleaned_text,
            tables=merged_tables,
            metadata={"parser": "python-docx", "file_path": file_path}
        )

    def parse_from_bytes(self, file_bytes: bytes, filename: str) -> ParseResult:
        doc = Document(file_bytes)

        raw_text = self._extract_text(doc)
        tables = self._extract_tables(doc)

        cleaned_text = self.cleaner.clean(raw_text)
        merged_tables = self.table_parser.merge_tables(tables)
        chunks = self.chunker.split(cleaned_text, merged_tables)

        return ParseResult(
            filename=filename,
            total_pages=len(doc.paragraphs),
            total_chunks=len(chunks),
            table_count=len(merged_tables),
            chunks=chunks,
            raw_text=cleaned_text,
            tables=merged_tables,
            metadata={"parser": "python-docx", "file_path": filename}
        )

    def _extract_text(self, doc: Document) -> str:
        paragraphs = []
        for para in doc.paragraphs:
            text = para.text.strip()
            if text:
                paragraphs.append(text)
        return '\n\n'.join(paragraphs)

    def _extract_tables(self, doc: Document) -> list:
        tables = []
        for i, table in enumerate(doc.tables, 1):
            try:
                md = self._table_to_markdown(table)
                cols, rows = self._parse_table_shape(md)

                table_data = {
                    "table_number": i,
                    "page": None,
                    "markdown": md,
                    "cols": cols,
                    "rows": rows,
                }
                tables.append(table_data)
            except Exception as e:
                print(f"警告：无法处理表格 {i}: {e}")
                continue

        return tables

    def _table_to_markdown(self, table: Table) -> str:
        rows = table.rows
        if not rows:
            return ""

        header = [cell.text.strip().replace('\n', ' ') for cell in rows[0].cells]
        md_lines = []
        md_lines.append("| " + " | ".join(header) + " |")
        md_lines.append("| " + " | ".join(["---"] * len(header)) + " |")

        for row in rows[1:]:
            cells = [cell.text.strip().replace('\n', ' ') for cell in row.cells]
            md_lines.append("| " + " | ".join(cells) + " |")

        return '\n'.join(md_lines)

    def _parse_table_shape(self, md: str) -> tuple:
        lines = [l.strip() for l in md.strip().split('\n') if l.strip()]
        if len(lines) < 2:
            return 0, 0
        cols = len([c for c in lines[0].split('|') if c.strip()])
        data_lines = lines[2:] if len(lines) > 2 else []
        rows = len([l for l in data_lines if '|' in l])
        return cols, rows

    def support_extensions(self) -> list[str]:
        return [".docx", ".DOCX"]