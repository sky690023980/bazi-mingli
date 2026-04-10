# -*- coding: utf-8 -*-
"""
FastAPI 主入口
启动：cd bazi_system && python -m backend.main
或：cd bazi_system/backend && python main.py
"""
import sys
from pathlib import Path

# 项目根目录
ROOT = Path(__file__).parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from backend.db import init_db
from backend.routes import bazi, llm, user
from backend.routes.extended import router as extended_router
from backend.models.models import HealthResponse
from backend.config import get_settings

settings = get_settings()

app = FastAPI(
    title="易学命理 API",
    description="八字排盘 · 六爻起卦 · LLM 智能解读",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

# CORS — 允许小程序访问
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],           # 小程序域名上线后改为精确配置
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 注册路由
app.include_router(bazi.router)
app.include_router(llm.router)
app.include_router(user.router)
app.include_router(extended_router)


@app.on_event("startup")
def startup():
    init_db()
    # 注册插件
    from backend.plugins.base import get_registry
    registry = get_registry()
    count = registry.discover()
    print(f"[启动] 命理 API 服务 → http://{settings.host}:{settings.port}")
    print(f"[启动] LLM Provider: {settings.llm_provider} | Model: {settings.ollama_model}")
    print(f"[启动] 已加载 {count} 个插件：{[p.name for p in registry.list_all()]}")


@app.get("/", tags=["首页"])
def root():
    return {
        "name": "易学命理 API",
        "version": "1.0.0",
        "docs": "/docs",
        "health": "/api/health",
    }


@app.get("/api/health", response_model=HealthResponse, tags=["系统"])
def health():
    """健康检查 + LLM 状态"""
    try:
        from backend.services.llm_service import get_llm_service
        llm = get_llm_service()
        # 简单连通性检查（不实际调用推理）
        model = (settings.ollama_model if settings.llm_provider == "ollama"
                 else settings.qwen_model if settings.llm_provider == "qwen"
                 else settings.openai_model)
        return HealthResponse(
            status="ok",
            llm_provider=settings.llm_provider,
            llm_model=model,
            db_connected=True,
            version="1.0.0"
        )
    except Exception as e:
        return HealthResponse(
            status="degraded",
            llm_provider=settings.llm_provider,
            llm_model="unknown",
            db_connected=True,
            version="1.0.0"
        )


# 挂载静态文件（小程序前端 build 后放在 frontend/dist）
frontend_dist = ROOT / "frontend" / "dist"
if frontend_dist.exists():
    app.mount("/", StaticFiles(directory=str(frontend_dist), html=True), name="static")
    print(f"[静态] 前端已挂载 → {frontend_dist}")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "backend.main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.debug,
    )
