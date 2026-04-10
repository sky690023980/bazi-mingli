# -*- coding: utf-8 -*-
"""Enhanced LLM service with RAG book search integration"""
import httpx
from typing import Optional
from backend.config import get_settings
from backend.services.book_search import get_book_search

settings = get_settings()


class LLMService:
    def __init__(self):
        self.provider = settings.llm_provider
        self.timeout = httpx.Timeout(120.0, connect=10.0)

    def _call_ollama(self, system: str, user: str) -> str:
        try:
            import ollama
            client = ollama.Client(host=settings.ollama_base_url)
            resp = client.chat(
                model=settings.ollama_model,
                messages=[
                    {"role": "system", "content": system},
                    {"role": "user", "content": user}
                ],
                options={
                    "temperature": settings.llm_temperature,
                    "num_predict": settings.llm_max_tokens,
                }
            )
            return resp["message"]["content"]
        except ImportError:
            return "[ERROR] ollama not installed: pip install ollama"
        except Exception as e:
            return "[ERROR] Ollama failed: " + str(e)

    def _call_openai(self, system: str, user: str) -> str:
        if not settings.openai_api_key:
            return "[ERROR] openai_api_key not configured"
        try:
            with httpx.Client(timeout=self.timeout) as client:
                resp = client.post(
                    settings.openai_base_url.rstrip("/") + "/chat/completions",
                    headers={
                        "Authorization": "Bearer " + settings.openai_api_key,
                        "Content-Type": "application/json",
                    },
                    json={
                        "model": settings.openai_model,
                        "messages": [
                            {"role": "system", "content": system},
                            {"role": "user", "content": user}
                        ],
                        "temperature": settings.llm_temperature,
                        "max_tokens": settings.llm_max_tokens,
                    }
                )
                resp.raise_for_status()
                return resp.json()["choices"][0]["message"]["content"]
        except Exception as e:
            return "[ERROR] OpenAI failed: " + str(e)

    def _call_qwen(self, system: str, user: str) -> str:
        if not settings.qwen_api_key:
            return "[ERROR] qwen_api_key not configured"
        try:
            with httpx.Client(timeout=self.timeout) as client:
                resp = client.post(
                    "https://dashscope.aliyuncs.com/compatible-mode/v1/chat/completions",
                    headers={
                        "Authorization": "Bearer " + settings.qwen_api_key,
                        "Content-Type": "application/json",
                    },
                    json={
                        "model": settings.qwen_model,
                        "messages": [
                            {"role": "system", "content": system},
                            {"role": "user", "content": user}
                        ],
                        "temperature": settings.llm_temperature,
                        "max_tokens": settings.llm_max_tokens,
                    }
                )
                resp.raise_for_status()
                return resp.json()["choices"][0]["message"]["content"]
        except Exception as e:
            return "[ERROR] Qwen failed: " + str(e)

    def chat(self, system: str, user: str) -> str:
        if self.provider == "ollama":
            return self._call_ollama(system, user)
        elif self.provider == "openai":
            return self._call_openai(system, user)
        elif self.provider == "qwen":
            return self._call_qwen(system, user)
        return "[ERROR] Unknown provider: " + self.provider

    def interpret_with_book(self, pillar_result: dict, topic: str = "all",
                           style: str = "professional") -> dict:
        """RAG-enhanced interpretation with classical text retrieval."""
        # Extract search terms
        pillar = pillar_result.get("pillar", {})
        day_gan = pillar.get("day", "甲子")[0] if pillar.get("day") else "甲"
        geju_name = pillar_result.get("geju", {}).get("name", "")
        xiyong = pillar_result.get("wuxing", {}).get("xiyongshen", [])
        jishen = pillar_result.get("wuxing", {}).get("jishen", [])

        search_terms = [day_gan, geju_name] + xiyong + jishen
        if topic == "career":
            search_terms += ["事业", "财运", "官禄"]
        elif topic == "marriage":
            search_terms += ["姻缘", "婚姻", "夫妻"]
        elif topic == "health":
            search_terms += ["健康", "养生"]

        # RAG search
        book_search = get_book_search()
        book_results = book_search.search_bazi_terms(search_terms)

        # Build system prompt
        style_map = {
            "professional": ("严谨专业", "200-400字", "命理专业术语"),
            "simple": ("简洁明了", "100字以内", "通俗易懂"),
            "plain": ("通俗温和", "200字", "有温度的解读"),
        }
        sname, slen, stone = style_map.get(style, style_map["professional"])
        system_prompt = (
            "你是一位精通中国传统命理的学者。\n"
            "基于古籍原文和八字数据进行解读。\n"
            "要求：" + sname + "风格，" + slen + "\n"
            "语言：" + stone + "\n"
            "引经据典，适当引用古籍原文。\n"
            "不恐吓、不封建迷信、不绝对化。"
        )

        # Build user prompt (no nested f-strings)
        score = pillar_result.get("wuxing", {}).get("score", {})
        p = pillar_result.get("pillar", {})
        geju = pillar_result.get("geju", {})
        dayun = pillar_result.get("dayun", [])
        shishen_list = pillar_result.get("shishen", {}).get("positions", [])
        gua = pillar_result.get("gua", {})

        score_str = ("木" + str(score.get("木", 0)) + "分、火" +
                     str(score.get("火", 0)) + "分、土" +
                     str(score.get("土", 0)) + "分、金" +
                     str(score.get("金", 0)) + "分、水" +
                     str(score.get("水", 0)) + "分")
        dayun_str = "、".join(["第" + str(d.get("step", "")) + "步" + d.get("ganzhi", "") for d in dayun[:5]])
        shishen_str = "、".join([
            p2.get("position", "") + p2.get("gan", "") + p2.get("shishen", "") for p2 in shishen_list
        ])

        # Book context
        book_context = ""
        if book_results:
            lines = []
            for r in book_results[:3]:
                lines.append("- 【" + r.get("source", "") + "】" + r.get("segment", "")[:120])
            book_context = "\n古籍引文：\n" + "\n".join(lines)

        topic_map = {
            "all": "请给出整体性格、事业方向与建议性解读",
            "career": "重点分析事业发展和财运走向",
            "marriage": "重点分析姻缘感情和婚恋时机",
            "health": "重点分析健康状况和养生建议",
        }
        topic_text = topic_map.get(topic, topic_map["all"])

        user_prompt = (
            "八字结构：\n" +
            "年柱" + p.get("year", "") + "、月柱" + p.get("month", "") +
            "、日柱" + p.get("day", "") + "、时柱" + p.get("time", "") + "\n\n" +
            "五行分布：" + score_str + "\n" +
            "日主" + pillar_result.get("wuxing", {}).get("strong_weak", "") +
            " | 格局：" + geju.get("name", "") + "（" + geju.get("level", "") + "级）\n" +
            "用神：" + "、".join(xiyong) + " | 忌神：" + "、".join(jishen) + "\n\n" +
            "十神：" + shishen_str + "\n" +
            "大运：" + dayun_str + "\n" +
            "六爻卦：" + gua.get("original_gua", "") + "（" +
            gua.get("yaoci", "") + "）" + gua.get("analysis", "") + "\n" +
            book_context + "\n\n" + topic_text
        )

        answer = self.chat(system_prompt, user_prompt)
        return {
            "answer": answer,
            "book_sources": [r.get("source", "") for r in book_results],
            "book_segments": [r.get("segment", "")[:150] for r in book_results[:3]],
            "search_terms": search_terms[:10],
        }


_llm_service = None

def get_llm_service() -> "LLMService":
    global _llm_service
    if _llm_service is None:
        _llm_service = LLMService()
    return _llm_service
