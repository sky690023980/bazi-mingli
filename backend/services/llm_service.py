# -*- coding: utf-8 -*-
import httpx, json
from typing import Dict, Any, Optional, List
from config import LLM_PROVIDER, GROQ_API_KEY, GROQ_MODEL

GROQ_URL = "https://api.groq.com/openai/v1"

async def call_llm(messages, model=None, temperature=0.7) -> str:
    import openai
    if LLM_PROVIDER == "groq":
        client = openai.OpenAI(api_key=GROQ_API_KEY, base_url=GROQ_URL)
        model = model or GROQ_MODEL
    else:
        from config import OPENAI_API_KEY, OPENAI_BASE_URL, OPENAI_MODEL
        client = openai.OpenAI(api_key=OPENAI_API_KEY, base_url=OPENAI_BASE_URL)
        model = model or OPENAI_MODEL
    try:
        resp = client.chat.completions.create(model=model, messages=messages, temperature=temperature)
        return resp.choices[0].message.content
    except Exception as e:
        return "LLM error: " + str(e)

async def interpret_bazi(pillar_data, style="professional"):
    p = pillar_data
    pillars = p.get("pillar", {})
    wx = p.get("wuxing", {})
    ss = p.get("shishen", {})
    name = p.get("name", "客户")
    gender = "男" if p.get("gender","M") in ["M","男"] else "女"
    birth_info = p.get("birth_info","")
    msgs = [
        {"role": "system", "content": "你是一位专业的中国传统命理师。请根据八字信息进行专业解读，风格专业但不晦涩。"},
        {"role": "user", "content": "姓名：" + name + " 性别：" + gender + " 出生：" + birth_info + "
四柱：" + pillars.get("year","") + " " + pillars.get("month","") + " " + pillars.get("day","") + " " + pillars.get("hour","") + "
十神：" + ss.get("年","") + " " + ss.get("月","") + " " + ss.get("日","") + " " + ss.get("时","") + "
五行：" + str(wx)}
    ]
    return await call_llm(msgs)
