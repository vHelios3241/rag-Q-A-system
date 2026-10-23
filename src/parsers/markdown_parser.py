from pathlib import Path
from typing import Optional

from .base import BaseParser, ParseResult
from .cleaner import TextCleaner
from .chunker import TextChunker, ChunkStrategy


class MarkdownParser(BaseParser):
    """Markdown文档解析器"""

    def __init__(
        self,
        chunker: Optional[TextChunker] = None,
        cleaner: Optional[TextCleaner] = None
    ):
        self.cleaner = cleaner or TextCleaner()
        self.chunker = chunker or TextChunker(
            strategy=ChunkStrategy.PARAGRAPH,
            max_chunk_size=1000,
            chunk_overlap=200
        )

    def parse(self, file_path: str) -> ParseResult:
        """解析Markdown文件"""
        with open(file_path, 'r', encoding='utf-8') as f:
            raw_text = f.read()

        cleaned_text = self.cleaner.full_clean(raw_text)
        chunks = self.chunker.split(cleaned_text)

        return ParseResult(
            filename=Path(file_path).name,
            total_pages=1,
            total_chunks=len(chunks),
            table_count=0,
            chunks=chunks,
            raw_text=cleaned_text,
            tables=[],
            metadata={"parser": "markdown"}
        )

    def parse_from_bytes(self, file_bytes: bytes, filename: str) -> ParseResult:
        """从字节流解析Markdown"""
        raw_text = file_bytes.decode('utf-8')
        cleaned_text = self.cleaner.full_clean(raw_text)
        chunks = self.chunker.split(cleaned_text)

        return ParseResult(
            filename=filename,
            total_pages=1,
            total_chunks=len(chunks),
            table_count=0,
            chunks=chunks,
            raw_text=cleaned_text,
            tables=[],
            metadata={"parser": "markdown"}
        )

    def support_extensions(self) -> list[str]:
        return [".md", ".markdown", ".MD", ".MARKDOWN"]