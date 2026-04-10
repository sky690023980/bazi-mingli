# -*- coding: utf-8 -*-
"""
用户/历史记录 API
"""
import json
from fastapi import APIRouter, HTTPException, Header
from typing import Optional
from backend.models.models import SaveReadingRequest, ReadingItem
from backend.db import (
    init_db, save_reading, get_readings,
    get_reading_by_id, get_or_create_user, get_recent_readings
)

router = APIRouter(prefix="/api/user", tags=["用户/历史"])


def _parse_openid(x_openid: str = Header(None)) -> str:
    """从请求头解析 openid"""
    return x_openid or "anonymous"


@router.post("/reading/save")
def api_save_reading(req: SaveReadingRequest, x_openid: str = Header(None)):
    """保存一次命盘记录"""
    try:
        init_db()
        openid = x_openid or "anonymous"
        rid = save_reading(
            openid=openid,
            name=req.name or "",
            gender=req.gender or "男",
            year=req.year, month=req.month, day=req.day, hour=req.hour,
            location=req.location or "",
            pillar_json=req.pillar_json,
            gua_json=req.gua_json or {},
            llm_report=req.llm_report or "",
        )
        return {"code": 200, "msg": "success", "data": {"id": rid}}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/reading/list")
def api_list_readings(x_openid: str = Header(None), limit: int = 20):
    """获取当前用户的历史记录"""
    try:
        init_db()
        openid = _parse_openid(x_openid)
        rows = get_readings(openid, limit)
        # 解析 JSON 字段
        for r in rows:
            if "pillar_json" in r and isinstance(r["pillar_json"], str):
                r["pillar_json"] = json.loads(r["pillar_json"])
        return {"code": 200, "msg": "success", "data": {"list": rows, "total": len(rows)}}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/reading/{reading_id}")
def api_get_reading(reading_id: int):
    """获取单条记录详情"""
    try:
        init_db()
        row = get_reading_by_id(reading_id)
        if not row:
            raise HTTPException(status_code=404, detail="记录不存在")
        if "pillar_json" in row and isinstance(row["pillar_json"], str):
            row["pillar_json"] = json.loads(row["pillar_json"])
        return {"code": 200, "msg": "success", "data": row}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/reading/recent")
def api_recent_readings(limit: int = 20):
    """获取最近记录（公开，无需 openid）"""
    try:
        init_db()
        rows = get_recent_readings(limit)
        for r in rows:
            if "pillar_json" in r and isinstance(r["pillar_json"], str):
                r["pillar_json"] = json.loads(r["pillar_json"])
        return {"code": 200, "msg": "success", "data": {"list": rows}}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
