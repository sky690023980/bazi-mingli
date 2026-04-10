# -*- coding: utf-8 -*-
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from typing import Optional
router = APIRouter(prefix="/api/bazi", tags=["八字排盘"])

class Q(BaseModel):
    name: Optional[str] = ""
    gender: str = "M"
    birth_year: int = Field(..., ge=1900, le=2030)
    birth_month: int = Field(..., ge=1, le=12)
    birth_day: int = Field(..., ge=1, le=31)
    birth_hour: int = Field(..., ge=0, le=23)

@router.post("/pan")
def pan(q: Q):
    try:
        from backend.services.engine import bazi_pan
        r = bazi_pan(q.name, q.gender, q.birth_year, q.birth_month, q.birth_day, q.birth_hour)
        return {"code": 200, "msg": "success", "data": r}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
