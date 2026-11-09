'''FastAPI 应用入口（注册路由）'''
import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
import os

from src.api.routers import chat, document, health

app = FastAPI(
    title="RAG System API",
    description="基于FastAPI的RAG系统API",
    version="0.1.0"
)

# 配置 CORS 中间件(解决跨域请求)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 允许所有来源
    allow_credentials=True,
    allow_methods=["*"],  # 允许所有方法
    allow_headers=["*"],  # 允许所有头部
)


# 路由
app.include_router(document.router,prefix="/api")
app.include_router(chat.router,prefix="/api")
app.include_router(health.router, prefix="/api")

FRONTEND_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "frontend")

if os.path.isdir(FRONTEND_DIR):
    app.mount("/static", StaticFiles(directory=FRONTEND_DIR), name="static")

    @app.get("/")
    async def index():
        return FileResponse(os.path.join(FRONTEND_DIR, "index.html"))
else:
    @app.get("/")
    async def index():
        return "Hello, RAG System API!"

if __name__ == '__main__':
    import uvicorn
    uvicorn.run('src.api.main:app', port=8000, reload=True)