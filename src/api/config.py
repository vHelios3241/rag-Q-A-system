import os
from dotenv import load_dotenv

load_dotenv()

'''配置（文件大小上限）'''
class Settings:
    """API 配置"""
    # 文件上传配置
    MAX_FILE_SIZE: int = 1024 * 1024 * 50
    ALLOWED_EXTENSIONS: list = [".pdf", ".docx", ".md", ".html", ".txt"]
    # 文件上传目录
    UPLOAD_DIR: str = "data/uploads"

    # LLM 提供商配置
    LLM_PROVIDERS = {
      "zhipu": {
        "api_key": os.getenv("ZHIPU_API_KEY", ""),
        "base_url": os.getenv("ZHIPU_BASE_URL", "https://open.bigmodel.cn/api/paas/v4"),
        "default_model": os.getenv("ZHIPU_MODEL", "glm-4-flash")
       },
     }

    # 默认提供商（前端不传时使用）
    DEFAULT_PROVIDER = os.getenv("DEFAULT_PROVIDER", "zhipu")

    # LLM 生成参数
    LLM_TEMPERATURE = 0.7
    LLM_MAX_TOKENS = 2000

    # 检索配置
    SEARCH_TOP_K = 5

    # 文件上传配置
    MAX_FILE_SIZE = 1024 * 1024 * 50
    ALLOWED_EXTENSIONS = ['.pdf', '.md', '.html', '.docx']

    # 上传文件存储目录
    UPLOAD_DIR = 'data/uploads'

settings = Settings()