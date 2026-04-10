# -*- coding: utf-8 -*-
"""
LLM 解读 API 路由
"""
from fastapi import APIRouter, HTTPException
from backend.models.models import LLMQuery, LLMResponse
from backend.services.engine import build_llm_prompt
from backend.services.llm_service import get_llm_service

router = APIRouter(prefix="/api/llm", tags=["LLM解读"])


@router.post("/interpret", response_model=LLMResponse)
def api_llm_interpret(query: LLMQuery):
    """
    LLM 命理解读
    输入：排盘结果 JSON + 用户提问（可选）
    返回：LLM 生成的自然语言解读
    """
    try:
        # 构建 Prompt
        sys_p, usr_p = build_llm_prompt(
            pillar_result=query.pillar_json,
            ask=query.question,
            style=query.style,
        )
        # 调用 LLM
        llm = get_llm_service()
        answer = llm.chat(system=sys_p, user=usr_p)
        return LLMResponse(code=200, msg="success", data={"answer": answer})
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/interpret-enriched")
def api_llm_interpret_enriched(query: LLMQuery):
    """
    RAG增强版 LLM 解读
    自动从古籍书库检索相关内容，再调用 LLM
    """
    try:
        llm = get_llm_service()
        topic = "all"
        if query.question:
            q = query.question
            if "事业" in q or "工作" in q:
                topic = "career"
            elif "姻缘" in q or "感情" in q or "婚姻" in q:
                topic = "marriage"
            elif "健康" in q or "身体" in q:
                topic = "health"
        result = llm.interpret_with_book(
            pillar_result=query.pillar_json,
            topic=topic,
            style=query.style,
        )
        return {"code": 200, "msg": "success", "data": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/status")
def api_llm_status():
    """查询 LLM 服务状态"""
    try:
        from backend.config import get_settings
        settings = get_settings()
        return {
            "code": 200,
            "data": {
                "provider": settings.llm_provider,
                "model": settings.ollama_model if settings.llm_provider == "ollama"
                         else settings.qwen_model if settings.llm_provider == "qwen"
                         else settings.openai_model,
                "base_url": settings.ollama_base_url if settings.llm_provider == "ollama"
                           else settings.openai_base_url if settings.llm_provider == "openai"
                           else "dashscope",
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
