'''FastAPI 应用入口（注册路由）'''
import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from fastapi import FastAPI

from src.api.routers import document
from src.api.routers import chat
from src.api.routers import health

app = FastAPI(
    title="RAG System API",
    description="基于FastAPI的RAG系统API",
    version="0.1.0"
)

# 路由
app.include_router(document.router,prefix="/api")
app.include_router(chat.router,prefix="/api")
app.include_router(health.router)

@app.get("/")
async def index():
    return "Hello, RAG System API!"

if __name__ == '__main__':
    import uvicorn
    uvicorn.run('src.api.main:app', port=8000, reload=True)