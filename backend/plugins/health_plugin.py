# -*- coding: utf-8 -*-
from .base import BaziPlugin
from typing import Dict, Any

class HealthPlugin(BaziPlugin):
    @property
    def name(self) -> str:
        return "health"

    @property
    def display_name(self) -> str:
        return "健康分析"

    @property
    def description(self) -> str:
        return "基于五行体质分析健康运势"

    def analyze(self, pillar_data: Dict[str, Any]) -> Dict[str, Any]:
        from backend.services.engine import health_analysis
        return health_analysis(pillar_data)
