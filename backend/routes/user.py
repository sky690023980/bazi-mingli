# -*- coding: utf-8 -*-
from fastapi import APIRouter
router = APIRouter(prefix="/api/user", tags=["用户"])
@router.get("/me")
def me():
    return {"code": 200, "msg": "success", "data": {"user_id": "anonymous"}}
