# -*- coding: utf-8 -*-
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any
import datetime

# === 八字排盘路由 ===
bazi = APIRouter(prefix="/api/bazi", tags=["八字排盘"])

class BaziQ(BaseModel):
    name: Optional[str] = ""
    gender: str = "M"
    birth_year: int = Field(..., ge=1900, le=2030)
    birth_month: int = Field(..., ge=1, le=12)
    birth_day: int = Field(..., ge=1, le=31)
    birth_hour: int = Field(..., ge=0, le=23)

@bazi.post("/pan")
def bazi_pan(q: BaziQ):
    try:
        from engine import bazi_pan as do_pan
        r = do_pan(q.name, q.gender, q.birth_year, q.birth_month, q.birth_day, q.birth_hour)
        return {"code": 200, "msg": "success", "data": r}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# === LLM解读路由 ===
llm = APIRouter(prefix="/api/llm", tags=["LLM解读"])

class LlmQ(BaseModel):
    pillar_json: Dict[str, Any]
    style: str = "professional"

@llm.post("/interpret")
async def llm_interpret(q: LlmQ):
    try:
        from llm_service import interpret_bazi
        result = await interpret_bazi(q.pillar_json, q.style)
        return {"code": 200, "msg": "success", "data": {"interpretation": result}}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# === 扩展分析路由 ===
extended = APIRouter(prefix="/api/extended", tags=["扩展分析"])

class ExtQ(BaseModel):
    pillar_json: Dict[str, Any]

class LqQ(BaseModel):
    birth_year: int = Field(..., ge=1900, le=2030)
    day_zhu: str = Field(..., min_length=2, max_length=2)
    target_year: Optional[int] = None

@extended.post("/health")
def ext_health(q: ExtQ):
    try:
        from engine import health_analysis
        return {"code": 200, "msg": "success", "data": health_analysis(q.pillar_json)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@extended.post("/marriage")
def ext_marriage(q: ExtQ):
    try:
        from engine import marriage_analysis
        return {"code": 200, "msg": "success", "data": marriage_analysis(q.pillar_json)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@extended.post("/liunian")
def ext_liunian(q: LqQ):
    try:
        from engine import liunian_detail
        yr = q.target_year or datetime.datetime.now().year
        return {"code": 200, "msg": "success", "data": liunian_detail(q.birth_year, q.day_zhu, yr)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# === 用户路由 ===
user = APIRouter(prefix="/api/user", tags=["用户"])

@user.get("/me")
def user_me():
    return {"code": 200, "msg": "success", "data": {"user_id": "anonymous"}}
