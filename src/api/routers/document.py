'''文档解析接口'''
import os

from fastapi import APIRouter, UploadFile, File, HTTPException

from ..config import settings
from src.parsers import ParserFactory, parse_file
from src.parsers.base import ParseResult
from pydantic import BaseModel

# 创建路由对象
router = APIRouter(prefix="/document", tags=["文件解析"])

# 子路由：上传文档并解析


@router.post("/upload")
async def upload_document(file: UploadFile = File(...)):
    '''
    上传文档并解析
    支持格式: pdf, docx, md, html, txt
    '''
    ext = os.path.splitext(file.filename)[-1].lower()     # 获取文件扩展名并转换为小写
    file_bites = await file.read()       # 读取文件内容为字节流

    # 判断文件大小
    if len(file_bites) > settings.MAX_FILE_SIZE:
        max_size_mb = settings.MAX_FILE_SIZE / 1024 / 1024
        raise HTTPException(
            status_code=400, detail=f"文件过大，最大支持{max_size_mb:.2f}MB")
    # 判断文件格式
    if ext not in settings.ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=400, detail=f"不支持的文件格式，仅支持{settings.ALLOWED_EXTENSIONS}")
    try:
        # 获取解析器
        parser = ParserFactory.get_parser(file.filename)
        # 解析文件
        result = parser.parse_from_bytes(file_bites, file.filename)
        # 返回解析结果
        return {
            "message": "文档处理成功",
            "filename": result.filename,
            "saved_path": str(result.saved_path),
            "total_pages": result.total_pages,
            "chunks_count": result.total_chunks,
            "tables_count": result.table_count,
            "chunks": result.chunks
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"文档处理失败: {str(e)}")


class ParsePathRequest(BaseModel):
    file_path: str      # 文件路径


@router.post("/parse-path")
async def parse_document_by_path(body: ParsePathRequest):
    """
     按路径解析文档

     - 传完整路径：直接解析(如 `/path/to/file.pdf`)
     - 只传文件名：在 `data/uploads/` 下查找(如 `report.pdf`)
     """
    input_path = body.file_path

    # 判断文件是否存在
    if not os.path.exists(input_path):
        raise HTTPException(
            status_code=404, detail=f"文件不存在: {input_path}")
    # 解析文件
    try:
        rs = parse_file(input_path)
        return {
            "message": "文档处理成功",
            "filename": rs.filename,
            "saved_path": str(rs.saved_path),
            "total_pages": rs.total_pages,
            "chunks_count": rs.total_chunks,
            "tables_count": rs.table_count,
            "chunks": rs.chunks,
            "tables": rs.tables
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"文档处理失败: {str(e)}")


@router.get("/supported-formats")
async def get_supported_formats():
    """获取支持的文件格式"""
    return {"formats": ParserFactory.supported_extensions()}
