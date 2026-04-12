# -*- coding: utf-8 -*-
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List

class BaziQuery(BaseModel):
    name: Optional[str] = ''
    gender: str = 'M'
    birth_year: int = Field(..., ge=1900, le=2030)
    birth_month: int = Field(..., ge=1, le=12)
    birth_day: int = Field(..., ge=1, le=31)
    birth_hour: int = Field(..., ge=0, le=23)

class LLMQuery(BaseModel):
    pillar_json: Dict[str, Any]
    style: str = 'professional'
