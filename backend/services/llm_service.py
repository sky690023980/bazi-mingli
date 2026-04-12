# -*- coding: utf-8 -*-
import httpx
import json
from typing import Dict, Any, Optional, List
import os

GROQ_URL = "https://api.groq.com/openai/v1"

def get_config():
    """鑾峰彇閰嶇疆"""
    llm_provider = os.getenv('llm_provider', 'groq').lower()
    groq_api_key = os.getenv('groq_api_key', '')
    groq_model = os.getenv('groq_model', 'llama-3.3-70b-versatile')
    openai_api_key = os.getenv('openai_api_key', '')
    openai_base_url = os.getenv('openai_base_url', 'https://api.openai.com/v1')
    openai_model = os.getenv('openai_model', 'gpt-4o-mini')
    return {
        'llm_provider': llm_provider,
        'groq_api_key': groq_api_key,
        'groq_model': groq_model,
        'openai_api_key': openai_api_key,
        'openai_base_url': openai_base_url,
        'openai_model': openai_model,
    }

async def call_llm(messages, model=None, temperature=0.7) -> str:
    """璋冪敤 LLM API"""
    import openai
    config = get_config()
    
    if config['llm_provider'] == 'groq':
        client = openai.OpenAI(
            api_key=config['groq_api_key'],
            base_url=GROQ_URL
        )
        model = model or config['groq_model']
    else:
        client = openai.OpenAI(
            api_key=config['openai_api_key'],
            base_url=config['openai_base_url']
        )
        model = model or config['openai_model']
    
    try:
        resp = client.chat.completions.create(
            model=model,
            messages=messages,
            temperature=temperature
        )
        return resp.choices[0].message.content
    except Exception as e:
        return f"LLM 璋冪敤澶辫触: {str(e)}"

async def interpret_bazi(pillar_data: Dict, style: str = "professional") -> str:
    """瑙ｈ鍏瓧鍛界洏"""
    p = pillar_data
    pillars = p.get("pillar", {})
    wx = p.get("wuxing", {})
    ss = p.get("shishen", {})
    name = p.get("name", "瀹㈡埛")
    gender = "鐢? if p.get("gender", "M") in ["M", "鐢?, "male"] else "濂?
    birth_info = p.get("birth_info", "")
    
    # 鏋勫缓绯荤粺鎻愮ず
    system_prompt = """浣犳槸涓€浣嶄笓涓氱殑涓浗浼犵粺鍛界悊甯堬紝绮鹃€氬叓瀛楀懡鐞嗐€佷簲琛岀敓鍏嬨€佸崄绁炲叧绯汇€?璇锋牴鎹鎴锋彁渚涚殑鍏瓧淇℃伅杩涜涓撲笟瑙ｈ锛岃姹傦細
1. 鍒嗘瀽鏃ヤ富寮哄急
2. 瑙ｈ鍗佺鍚箟
3. 鍒嗘瀽浜旇鍠滃繉
4. 鎻愪緵浜嬩笟銆佽储杩愩€佸濮汇€佸仴搴锋柟闈㈢殑寤鸿
椋庢牸瑕佷笓涓氫絾涓嶆櫐娑╋紝閫氫織鏄撴噦銆?""

    # 鏋勫缓鐢ㄦ埛鎻愮ず
    user_prompt = f"""璇蜂负浠ヤ笅鍛戒富杩涜鍏瓧瑙ｈ锛?
濮撳悕锛歿name}
鎬у埆锛歿gender}
鍑虹敓锛歿birth_info}

鍥涙煴鍏瓧锛?- 骞存煴锛歿pillars.get('year', '')}
- 鏈堟煴锛歿pillars.get('month', '')}
- 鏃ユ煴锛歿pillars.get('day', '')}
- 鏃舵煴锛歿pillars.get('hour', '')}

鍗佺锛?- 骞存煴锛歿ss.get('骞?, '')}
- 鏈堟煴锛歿ss.get('鏈?, '')}
- 鏃ユ煴锛歿ss.get('鏃?, '')}锛堟棩涓伙級
- 鏃舵煴锛歿ss.get('鏃?, '')}

浜旇鍒嗗竷锛歿json.dumps(wx, ensure_ascii=False)}

璇蜂粠鎬ф牸銆佷簨涓氥€佽储杩愩€佸濮汇€佸仴搴蜂簲涓柟闈㈣繘琛岃缁嗚В璇汇€?""

    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_prompt}
    ]
    
    return await call_llm(messages)
