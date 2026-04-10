# -*- coding: utf-8 -*-
"""
Pydantic 数据模型 — 请求/响应结构
"""

from pydantic import BaseModel, Field, validator
from typing import Optional, List, Dict, Any
from datetime import datetime


# ── 请求模型 ──────────────────────────
class BaziQuery(BaseModel):
    """八字排盘请求"""
    name: Optional[str] = ""
    gender: Optional[str] = "男"
    year: int = Field(..., ge=1920, le=2030, description="出生年")
    month: int = Field(..., ge=1, le=12, description="出生月")
    day: int = Field(..., ge=1, le=31, description="出生日")
    hour: int = Field(..., ge=0, le=23, description="出生时（0-23）")
    location: Optional[str] = "北京"
    ask: Optional[str] = Field("", description="用户提问（可选）")


class GuaQuery(BaseModel):
    """六爻起卦请求"""
    gender: Optional[str] = "男"
    year: int
    month: int
    day: int
    hour: int
    question: Optional[str] = ""


class LLMQuery(BaseModel):
    """LLM 解读请求"""
    pillar_json: Dict[str, Any]
    question: Optional[str] = ""
    style: str = "professional"  # professional | simple | plain


# ── 响应模型 ──────────────────────────
class TenGod(BaseModel):
    position: str
    gan: str
    shishen: str
    wuxing: str


class DayunStep(BaseModel):
    step: int
    ganzhi: str
    wuxing: str
    age_start: int


class LiunianYear(BaseModel):
    year: int
    ganzhi: str
    wuxing: str
    score: int


class WuxingScore(BaseModel):
    木: float = 0
    火: float = 0
    土: float = 0
    金: float = 0
    水: float = 0


class Geju(BaseModel):
    name: str
    level: str


class PillarData(BaseModel):
    year: str
    month: str
    day: str
    time: str


class GuaData(BaseModel):
    original_gua: str
    change_gua: str
    element: str
    yaoci: str
    dong_yao: int
    analysis: str


class BaziResponse(BaseModel):
    """八字排盘完整响应"""
    code: int = 200
    msg: str = "success"
    data: Dict[str, Any]


class LLMResponse(BaseModel):
    """LLM 解读响应"""
    code: int = 200
    msg: str = "success"
    data: Dict[str, Any]


# ── 用户/历史 ──────────────────────────
class SaveReadingRequest(BaseModel):
    name: Optional[str] = ""
    gender: str = "男"
    year: int
    month: int
    day: int
    hour: int
    location: Optional[str] = ""
    pillar_json: Dict[str, Any]
    gua_json: Optional[Dict[str, Any]] = {}
    llm_report: Optional[str] = ""


class ReadingItem(BaseModel):
    id: int
    name: str
    gender: str
    year: int
    month: int
    day: int
    hour: int
    location: str
    created_at: str


# ── 系统状态 ──────────────────────────
class HealthResponse(BaseModel):
    status: str
    llm_provider: str
    llm_model: str
    db_connected: bool
    version: str = "1.0.0"
