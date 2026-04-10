# -*- coding: utf-8 -*-
"""健康分析插件"""
from typing import Dict, Any
from .base import BaziPlugin

class HealthPlugin(BaziPlugin):
    WUXING_ORGANS = {
        "木": {"yin": "肝", "yang": "胆", "易患": "肝胆疾病、神经系统问题"},
        "火": {"yin": "心", "yang": "小肠", "易患": "心血管疾病、失眠多梦"},
        "土": {"yin": "脾", "yang": "胃", "易患": "消化系统、代谢问题"},
        "金": {"yin": "肺", "yang": "大肠", "易患": "呼吸系统、皮肤问题"},
        "水": {"yin": "肾", "yang": "膀胱", "易患": "泌尿系统疾病、腰膝酸软"},
    }
    SEASON_TIPS = {
        "木": "春（寅卯月）宜养肝，多青色食物，早睡早起",
        "火": "夏（巳午月）宜养心，午时小憩，少思虑",
        "土": "长夏宜养脾，规律饮食，少食生冷油腻",
        "金": "秋（申酉月）宜养肺，多深呼吸，多白色食物",
        "水": "冬（亥子月）宜养肾，多保暖，早睡养精",
    }

    @property
    def name(self) -> str:
        return "health"

    @property
    def display_name(self) -> str:
        return "健康分析"

    def get_tags(self) -> list:
        return ["健康", "养生", "调养"]

    def analyze(self, pillar_data: Dict[str, Any]) -> Dict[str, Any]:
        wuxing = pillar_data.get("wuxing", {})
        scores = wuxing.get("score", {})
        strong_weak = wuxing.get("strong_weak", "中和")
        if not scores:
            return {"plugin_name": self.name, "summary": "数据不足", "details": {}}

        sorted_items = sorted(scores.items(), key=lambda x: x[1])
        weak_list = sorted_items[:2]
        strong_list = sorted_items[-1:]

        risks = []
        suggestions = []
        for elem, score in weak_list:
            if elem in self.WUXING_ORGANS:
                info = self.WUXING_ORGANS[elem]
                risks.append({
                    "element": elem,
                    "yin_organ": info["yin"],
                    "yang_organ": info["yang"],
                    "易患": info["易患"],
                    "score": score
                })
            if elem == "木":
                suggestions.append("早睡养肝（23点前入睡），少怒，饮食清淡，多户外散步")
            elif elem == "火":
                suggestions.append("午时小憩养心（11-13点），少思虑，多静心")
            elif elem == "土":
                suggestions.append("规律饮食养脾胃，少食生冷，多黄色食物（如小米、南瓜）")
            elif elem == "金":
                suggestions.append("秋养肺气，多深呼吸，白色食物（梨、银耳、百合）")
            elif elem == "水":
                suggestions.append("冬季养肾，多保暖，早睡养精，黑色食物（黑豆、黑芝麻）")

        season_tip = ""
        for elem in weak_list[:2]:
            if elem[0] in self.SEASON_TIPS:
                season_tip += self.SEASON_TIPS[elem[0]] + "。"

        health_score = max(0, min(100, 100 - int(weak_list[0][1] * 8))) if weak_list else 70
        health_level = "优秀" if health_score >= 85 else ("良好" if health_score >= 70 else ("一般" if health_score >= 50 else "需关注"))

        summary = (f"健康评估：{health_level}（{health_score}分）。"
                   f"五行偏弱：{weak_list[0][0]}（{weak_list[0][1]}分），"
                   f"{weak_list[0][0]}系统需重点调养。"
                   f"{'日主偏旺，宜疏泄宣泄。' if strong_weak in ['强', '偏强'] else '日主偏弱，宜补益保养。'}")

        return {
            "plugin_name": self.name,
            "summary": summary,
            "details": {
                "health_score": health_score,
                "health_level": health_level,
                "wuxing_scores": scores,
                "strong_weak": strong_weak,
                "weak_elements": [e for e, _ in weak_list],
                "strong_elements": [e for e, _ in strong_list],
                "risk_evaluation": risks,
                "suggestions": suggestions,
                "season_tips": season_tip,
            }
        }
