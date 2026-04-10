# -*- coding: utf-8 -*-
"""
奇门遁甲 API 路由
"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any

router = APIRouter(prefix="/api/qimen", tags=["奇门遁甲"])


class QimenQuery(BaseModel):
    """奇门遁甲排盘请求"""
    year: int = Field(..., ge=1920, le=2030, description="年")
    month: int = Field(..., ge=1, le=12, description="月")
    day: int = Field(..., ge=1, le=31, description="日")
    hour: int = Field(..., ge=0, le=23, description="时（0-23）")


class QimenResponse(BaseModel):
    code: int = 200
    msg: str = "success"
    data: Dict[str, Any]


@router.post("/pan", response_model=QimenResponse)
def api_qimen_pan(query: QimenQuery):
    """
    奇门遁甲排盘接口
    输入：年月日时分
    返回：九宫格布局、八门、八神、九星、旬空、马星、整体解读
    """
    try:
        from engine import qimen_pan
        result = qimen_pan(
            year=query.year,
            month=query.month,
            day=query.day,
            hour=query.hour,
        )
        return QimenResponse(code=200, msg="success", data=result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
