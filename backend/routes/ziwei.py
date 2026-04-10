# -*- coding: utf-8 -*-
"""
紫微斗数 API 路由
"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any

router = APIRouter(prefix="/api/ziwei", tags=["紫微斗数"])


class ZiweiQuery(BaseModel):
    """紫微斗数排盘请求"""
    year: int = Field(..., ge=1920, le=2030, description="出生年")
    month: int = Field(..., ge=1, le=12, description="出生月")
    day: int = Field(..., ge=1, le=31, description="出生日")
    hour: int = Field(..., ge=0, le=23, description="出生时（0-23）")
    gender: str = Field("男", description="性别")


class ZiweiResponse(BaseModel):
    code: int = 200
    msg: str = "success"
    data: Dict[str, Any]


@router.post("/pan", response_model=ZiweiResponse)
def api_ziwei_pan(query: ZiweiQuery):
    """
    紫微斗数排盘接口
    输入：出生年月日时分、性别
    返回：14颗主星位置、12宫位、五行局、星曜组合分析
    """
    try:
        from backend.services.engine import ziwei_pan
        result = ziwei_pan(
            year=query.year,
            month=query.month,
            day=query.day,
            hour=query.hour,
            gender=query.gender or "男",
        )
        return ZiweiResponse(code=200, msg="success", data=result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
