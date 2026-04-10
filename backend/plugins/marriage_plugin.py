# -*- coding: utf-8 -*-
"""姻缘分析插件"""
from typing import Dict, Any
from .base import BaziPlugin

class MarriagePlugin(BaziPlugin):
    TIANGAN=["甲","乙","丙","丁","戊","己","庚","辛","壬","癸"]
    DIZHI=["子","丑","寅","卯","辰","巳","午","未","申","酉","戌","亥"]
    ZHENG_GUAN={"甲":"辛","乙":"庚","丙":"癸","丁":"壬","戊":"乙","己":"甲","庚":"丁","辛":"丙","壬":"己","癸":"戊"}
    TAOHUA={"子":"酉","卯":"子","午":"卯","酉":"午"}
    GONG_NAMES=["命宫","兄弟宫","夫妻宫","子女宫","财帛宫","疾厄宫","迁移宫","仆役宫","官禄宫","田宅宫","福德宫","父母宫"]

    @property
    def name(self) -> str:
        return "marriage"

    @property
    def display_name(self) -> str:
        return "姻缘分析"

    def get_tags(self) -> list:
        return ["姻缘","感情","婚恋"]

    def analyze(self, pillar_data: Dict[str, Any]) -> Dict[str, Any]:
        pillar = pillar_data.get("pillar", {})
        day_zhu = pillar.get("day", "甲子")
        month_zhu = pillar.get("month", "寅月")
        year_zhu = pillar.get("year", "甲子")
        day_gan = day_zhu[0] if day_zhu else "甲"
        day_zhi = day_zhu[-1] if len(day_zhu)>=2 else "子"
        month_zhi = month_zhu[-1] if len(month_zhu)>=2 else "寅"
        year_zhi = year_zhu[-1] if len(year_zhu)>=2 else "子"
        zheng_guan = self.ZHENG_GUAN.get(day_gan, "")
        taohua = self.TAOHUA.get(year_zhi, "") or self.TAOHUA.get(day_zhi, "")
        try:
            month_idx = self.DIZHI.index(month_zhi)
            day_idx = self.DIZHI.index(day_zhi)
        except: month_idx, day_idx = 2, 0
        fq_gong_idx = (month_idx + day_idx) % 12
        suggestions = []
        if zheng_guan in ["辛","庚","癸","壬"]:
            suggestions.append("正缘较强，宜主动社交，通过工作或学习结识异性")
        if taohua:
            suggestions.append("桃花星旺，感情经历丰富，需学会筛选，避免烂桃花")
        suggestions.append("婚恋时机结合流年大运综合判断")
        summary = (
            f"姻缘分析：日主{day_gan}，正缘星为{zheng_guan}，夫妻宫在{self.GONG_NAMES[fq_gong_idx]}。"
            f"{'桃花星旺，感情丰富，需谨慎择偶。' if taohua else '姻缘相对平稳，宜顺其自然。'}"
        )
        return {
            "plugin_name": self.name,
            "summary": summary,
            "details": {
                "day_master": day_gan,
                "zheng_guan_star": zheng_guan,
                "taohua_zhi": taohua,
                "fouqi_gong": self.GONG_NAMES[fq_gong_idx],
                "suggestions": suggestions,
                "partner_description": f"日主{day_gan}，正缘星{zheng_guan}，缘分以稳重踏实者为宜".replace("日主甲","性格刚毅").replace("日主乙","性格温柔").replace("日主丙","热情开朗").replace("日主丁","细腻敏感").replace("日主戊","稳重厚道").replace("日主己","温和务实").replace("日主庚","刚强果断").replace("日主辛","精致内敛").replace("日主壬","灵活变通").replace("日主癸","柔情似水"),
            },
        }
