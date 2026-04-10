# -*- coding: utf-8 -*-
"""
配置文件
"""
from pathlib import Path
from pydantic_settings import BaseSettings
from functools import lru_cache

BASE_DIR = Path(__file__).parent.parent
DATA_DIR = BASE_DIR.parent / "bazi_engine" / "data"

class Settings(BaseSettings):
    # 数据库
    db_path: Path = BASE_DIR / "bazi_data.db"

    # LLM — Ollama 本地
    ollama_base_url: str = "http://localhost:11434"
    ollama_model: str = "qwen2.5:14b"
    llm_temperature: float = 0.3
    llm_max_tokens: int = 800

    # LLM — OpenAI 兼容接口（可选）
    openai_api_key: str = ""
    openai_base_url: str = ""
    openai_model: str = "gpt-4o-mini"

    # LLM Provider 选择
    llm_provider: str = "ollama"  # "ollama" | "openai" | "qwen"

    # Qwen API（阿里云 DashScope）
    qwen_api_key: str = ""
    qwen_model: str = "qwen-plus"

    # 服务器
    host: str = "0.0.0.0"
    port: int = 8000
    debug: bool = False

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"

@lru_cache
def get_settings() -> Settings:
    return Settings()
