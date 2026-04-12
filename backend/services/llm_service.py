# -*- coding: utf-8 -*-
import openai
import json
from typing import Dict, Any, Optional, List
from config import LLM_PROVIDER, GROQ_API_KEY, GROQ_MODEL

GROQ_URL = "https://api.groq.com/openai/v1"

def get_client():
    """获取 LLM 客户端"""
    if LLM_PROVIDER == "groq":
        return openai.OpenAI(api_key=GROQ_API_KEY, base_url=GROQ_URL), GROQ_MODEL
    else:
        from config import OPENAI_API_KEY, OPENAI_BASE_URL, OPENAI_MODEL
        return openai.OpenAI(api_key=OPENAI_API_KEY, base_url=OPENAI_BASE_URL), OPENAI_MODEL

async def call_llm(messages, model=None, temperature=0.7) -> str:
    """调用 LLM API"""
    client, default_model = get_client()
    model = model or default_model
    try:
        resp = client.chat.completions.create(
            model=model,
            messages=messages,
            temperature=temperature
        )
        return resp.choices[0].message.content
    except Exception as e:
        return f"LLM 调用失败: {str(e)}"

async def interpret_bazi(pillar_data: Dict, style: str = "professional") -> str:
    """解读八字命盘"""
    p = pillar_data
    pillars = p.get("pillar", {})
    wx = p.get("wuxing", {})
    ss = p.get("shishen", {})
    name = p.get("name", "客户")
    gender = "男" if p.get("gender", "M") in ["M", "男", "male"] else "女"
    birth_info = p.get("birth_info", "")
    
    # 构建系统提示
    system_prompt = """你是一位专业的中国传统命理师，精通八字命理、五行生克、十神关系。
请根据客户提供的八字信息进行专业解读，要求：
1. 分析日主强弱
2. 解读十神含义
3. 分析五行喜忌
4. 提供事业、财运、婚姻、健康方面的建议
风格要专业但不晦涩，通俗易懂。"""

    # 构建用户提示
    user_prompt = f"""请为以下命主进行八字解读：

姓名：{name}
性别：{gender}
出生：{birth_info}

四柱八字：
- 年柱：{pillars.get('year', '')}
- 月柱：{pillars.get('month', '')}
- 日柱：{pillars.get('day', '')}
- 时柱：{pillars.get('hour', '')}

十神：
- 年柱：{ss.get('年', '')}
- 月柱：{ss.get('月', '')}
- 日柱：{ss.get('日', '')}（日主）
- 时柱：{ss.get('时', '')}

五行分布：{json.dumps(wx, ensure_ascii=False)}

请从性格、事业、财运、婚姻、健康五个方面进行详细解读。"""

    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_prompt}
    ]
    
    return await call_llm(messages)
