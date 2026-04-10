# -*- coding: utf-8 -*-
"""
八字/六爻 API 路由
"""
from fastapi import APIRouter, HTTPException
from backend.models.models import BaziQuery, BaziResponse, GuaQuery, GuaData
from backend.services.engine import bazi_pan, time_gua, build_llm_prompt

router = APIRouter(prefix="/api/bazi", tags=["八字排盘"])


@router.post("/pan", response_model=BaziResponse)
def api_bazi_pan(query: BaziQuery):
    """
    八字排盘接口
    输入：出生年月日时分
    返回：四柱、五行、十神、格局、大运、流年、六爻
    """
    try:
        result = bazi_pan(
            year=query.year,
            month=query.month,
            day=query.day,
            hour=query.hour,
            gender=query.gender or "男",
            location=query.location or "北京",
        )
        return BaziResponse(code=200, msg="success", data=result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/gua", response_model=dict)
def api_time_gua(query: GuaQuery):
    """
    六爻梅花易数起卦
    时间法起卦，返回卦名、动爻、变卦、卦象分析
    """
    try:
        result = time_gua(
            year=query.year,
            month=query.month,
            day=query.day,
            hour=query.hour,
            gender=query.gender or "男",
        )
        return {"code": 200, "msg": "success", "data": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/prompt/demo")
def api_demo_prompt():
    """返回示例 Prompt，供前端预览"""
    try:
        demo_result = bazi_pan(1990, 5, 15, 10, "男", "北京")
        sys_p, usr_p = build_llm_prompt(demo_result, "事业发展方向")
        return {
            "code": 200,
            "data": {
                "system": sys_p,
                "user": usr_p
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
