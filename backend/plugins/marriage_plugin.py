# -*- coding: utf-8 -*-
from .base import BaziPlugin
from typing import Dict, Any

class MarriagePlugin(BaziPlugin):
    @property
    def name(self) -> str:
        return "marriage"

    @property
    def display_name(self) -> str:
        return "姻缘分析"

    @property
    def description(self) -> str:
        return "姻缘配偶星分析"

    def analyze(self, pillar_data: Dict[str, Any]) -> Dict[str, Any]:
        from backend.services.engine import marriage_analysis
        return marriage_analysis(pillar_data)
