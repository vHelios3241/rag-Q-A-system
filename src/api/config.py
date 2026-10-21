'''配置（文件大小上限）'''
class Settings:
    """API 配置"""
    # 文件上传配置
    MAX_FILE_SIZE: int = 1024 * 1024 * 50
    ALLOWED_EXTENSIONS: list = [".pdf", ".docx", ".md", ".html", ".txt"]
    # 文件上传目录
    UPLOAD_DIR: str = "data/uploads"

settings = Settings()