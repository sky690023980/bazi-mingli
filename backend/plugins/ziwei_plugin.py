# -*- coding: utf-8 -*-
"""紫微斗数插件"""
from typing import Dict, Any
from .base import BaziPlugin

class ZiweiPlugin(BaziPlugin):
    DIZHI = ["子","丑","寅","卯","辰","巳","午","未","申","酉","戌","亥"]
    GONG_NAMES = ["命宫","兄弟宫","夫妻宫","子女宫","财帛宫","疾厄宫","迁移宫","仆役宫","官禄宫","田宅宫","福德宫","父母宫"]
    STAR_PALACE = {
        0:["紫微","天机","太阳"], 1:["天同","天梁"], 2:["紫微","贪狼"], 3:["武曲","天相"],
        4:["太阳","天梁"], 5:["天府","太阴"], 6:["七杀","廉贞"], 7:["天机","天同"],
        8:["武曲","贪狼"], 9:["天府","太阴"], 10:["紫微","天相"], 11:["破军","廉贞"],
    }

    @property
    def name(self) -> str:
        return "ziwei"

    @property
    def display_name(self) -> str:
        return "紫微斗数"

    def get_tags(self) -> list:
        return ["紫微","星曜","命宫"]

    def analyze(self, pillar_data: Dict[str, Any]) -> Dict[str, Any]:
        pillar = pillar_data.get("pillar", {})
        day_zhu = pillar.get("day", "甲子")
        month_zhu = pillar.get("month", "寅月")
        day_zhi = day_zhu[-1] if len(day_zhu)>=2 else "子"
        month_zhi = month_zhu[-1] if len(month_zhu)>=2 else "寅"
        try:
            month_idx = self.DIZHI.index(month_zhi)
            day_idx = self.DIZHI.index(day_zhi)
        except: month_idx, day_idx = 2, 0
        ming_gong_idx = (month_idx + day_idx) % 12
        try:
            hour = pillar_data.get("birth_info", {}).get("hour", 12)
            shi_idx = hour // 2 % 12
        except: shi_idx = 6
        shen_gong_idx = (ming_gong_idx + shi_idx) % 12
        stars = self.STAR_PALACE.get(ming_gong_idx, ["天机","天同"])
        good = {"紫微","天府","天相","天梁","太阳","太阴"}
        good_count = len(set(stars) & good)
        overall = "★★★★☆ 命格上佳" if good_count>=2 else ("★★☆☆☆ 命格平常" if good_count==1 else "★★★☆☆ 命格中等")
        summary = (
            f"紫微斗数命盘：命宫在{self.GONG_NAMES[ming_gong_idx]}（{self.DIZHI[ming_gong_idx]}宫），"
            f"身宫在{self.GONG_NAMES[shen_gong_idx]}。主星：{'、'.join(stars)}。{overall}"
        )
        return {
            "plugin_name": self.name,
            "summary": summary,
            "details": {
                "ming_gong": self.GONG_NAMES[ming_gong_idx],
                "shen_gong": self.GONG_NAMES[shen_gong_idx],
                "main_stars": stars,
                "overall_judge": overall,
                "star_meanings": {
                    "紫微":"帝王星，尊贵、领导力","天机":"谋略星，智慧、策划",
                    "太阳":"光明星，积极、博爱","天府":"财库星，稳重、保守",
                    "太阴":"母星，温柔、财星","贪狼":"欲望星，多才、桃花",
                    "七杀":"将星，刚烈、冒险","破军":"耗星，破旧立新",
                },
                "interpretation": {
                    "personality": self._personality(stars),
                    "career": "职业选择广泛，宜结合大运综合判断" if not any(s in ["紫微","天机","武曲"] for s in stars) else "",
                    "relationship": "姻缘平稳" if "太阴" not in stars else "桃花旺",
                },
            },
        }

    def _personality(self, stars):
        m = {"紫微":"自尊心强，有领导欲","天机":"聪明机敏，善于策划","太阳":"热情开朗，积极向上","天府":"稳重保守，责任心强","太阴":"细腻敏感，感情丰富","贪狼":"多才多艺，欲望强烈","七杀":"刚烈果断","破军":"破旧立新"}
        return "；".join([m.get(s,"") for s in stars if s in m]) or "命主个性平和，运势平稳"
