# -*- coding: utf-8 -*-
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Dict, Any
router = APIRouter(prefix="/api/llm", tags=["LLM解读"])

class Q(BaseModel):
    pillar_json: Dict[str, Any]
    style: str = "professional"

@router.post("/interpret")
async def interpret(q: Q):
    try:
        from services.llm_service import interpret_bazi
        result = await interpret_bazi(q.pillar_json, q.style)
        return {"code": 200, "msg": "success", "data": {"interpretation": result}}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
