# -*- coding: utf-8 -*-
"""奇门遁甲插件"""
from typing import Dict, Any
from .base import BaziPlugin

class QimenPlugin(BaziPlugin):
    MEN_NAMES = ["休", "生", "伤", "杜", "中", "景", "死", "惊", "开"]
    STARS = ["天蓬", "天芮", "天冲", "天辅", "天禽", "天心", "天柱", "天任", "天英"]
    PALACE_NAMES = ["坎一宫", "坤二宫", "震三宫", "巽四宫", "中五宫", "乾六宫", "兑七宫", "艮八宫", "离九宫"]
    PALACE_GAN = ["壬", "癸", "甲", "乙", "寄坤", "庚", "辛", "丙", "丁"]

    @property
    def name(self) -> str:
        return "qimen"

    @property
    def display_name(self) -> str:
        return "奇门遁甲"

    def get_tags(self) -> list:
        return ["奇门", "方位", "吉凶"]

    def _solar_to_jd(self, year, month, day):
        if month <= 2: year -= 1; month += 12
        A = int(year / 100)
        B = 2 - A + int(A / 4)
        return int(365.25*(year+4716)) + int(30.6001*(month+1)) + day + B - 1524.5

    def analyze(self, pillar_data: Dict[str, Any]) -> Dict[str, Any]:
        birth = pillar_data.get("birth_info", {})
        year = birth.get("year", 2000)
        month = birth.get("month", 1)
        day = birth.get("day", 1)
        hour = birth.get("hour", 12)

        base_jd = 2451550.0
        target_jd = self._solar_to_jd(year, month, day)
        days_diff = int(target_jd - base_jd)
        ju = (days_diff % 9) + 1
        ju_type = "阳遁" if ju <= 5 else "阴遁"
        zhi_shi = (days_diff + hour) % 9
        if zhi_shi == 0: zhi_shi = 9
        zhi_star = (days_diff * 2 + hour) % 9
        if zhi_star == 0: zhi_star = 9
        lucky_hours = list(range(7, 13))
        is_lucky = hour in lucky_hours
        summary = (
            f"奇门遁甲局：{ju_type}{ju}局，值使门{self.MEN_NAMES[zhi_shi-1] if zhi_shi<=9 else '休'}，"
            f"值符星{self.STARS[zhi_star-1] if zhi_star<=9 else '天蓬'}。"
            f"{'当前时辰为吉时，宜出行求财。' if is_lucky else '当前时辰为平事，静待时机。'}"
        )
        return {
            "plugin_name": self.name,
            "summary": summary,
            "details": {
                "ju": f"{ju_type}{ju}局",
                "ju_type": ju_type,
                "ju_num": ju,
                "zhi_shi_men": self.MEN_NAMES[zhi_shi-1] if zhi_shi<=9 else "休",
                "zhi_star": self.STARS[zhi_star-1] if zhi_star<=9 else "天蓬",
                "lucky_directions": ["东北", "正南", "西南"],
                "unlucky_directions": ["正西", "正北"],
                "is_current_hour_lucky": is_lucky,
                "palace_chart": self._build_chart(ju),
                "interpretation": {
                    "career": f"{ju_type}局{'利于事业拓展' if ju_type=='阳遁' else '宜稳中求进'}",
                    "health": "注意五行调养，参考八字用神",
                },
            },
        }

    def _build_chart(self, ju):
        chart = {}
        for i, name in enumerate(self.PALACE_NAMES):
            offset = (i + ju - 1) % 9
            chart[name] = {
                "men": self.MEN_NAMES[offset],
                "star": self.STARS[offset],
                "gan": self.PALACE_GAN[i],
            }
        return chart
