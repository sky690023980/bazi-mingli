# -*- coding: utf-8 -*-
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from typing import Dict, Any, Optional
import datetime
router = APIRouter(prefix="/api/extended", tags=["扩展分析"])

class HQ(BaseModel):
    pillar_json: Dict[str, Any]

class MQ(BaseModel):
    pillar_json: Dict[str, Any]

class LQ(BaseModel):
    birth_year: int = Field(..., ge=1900, le=2030)
    day_zhu: str = Field(..., min_length=2, max_length=2)
    target_year: Optional[int] = None

@router.post("/health")
def health(q: HQ):
    try:
        from engine import health_analysis
        return {"code": 200, "msg": "success", "data": health_analysis(q.pillar_json)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/marriage")
def marriage(q: MQ):
    try:
        from engine import marriage_analysis
        return {"code": 200, "msg": "success", "data": marriage_analysis(q.pillar_json)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/liunian")
def liunian(q: LQ):
    try:
        from engine import liunian_detail
        yr = q.target_year or datetime.datetime.now().year
        return {"code": 200, "msg": "success", "data": liunian_detail(q.birth_year, q.day_zhu, yr)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
