# -*- coding: utf-8 -*-
import sys, os, pathlib
_DEPLOY_ROOT = pathlib.Path("/app")
if _DEPLOY_ROOT.exists():
    sys.path.insert(0, "/app")
sys.path.insert(0, str(pathlib.Path(__file__).parent))

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from config import HOST, PORT

app = FastAPI(title="八字命理LLM系统", version="1.0.0")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_credentials=True, allow_methods=["*"], allow_headers=["*"])

from routes import bazi, llm, user, extended
app.include_router(bazi)
app.include_router(llm)
app.include_router(user)
app.include_router(extended)

@app.get("/api/health/")
def health():
    return {"status": "ok", "service": "bazi-mingli"}

@app.get("/")
def root():
    return {"message": "八字命理LLM系统 API v1.0.0"}





@app.get("/api/groq-test")
def groq_test():
    import os as _os, httpx as _httpx
    key = _os.environ.get("GROQ_API_KEY", "")
    if not key:
        return {"error": "no-key-found"}
    try:
        headers = {"Authorization": "Bearer " + key}
        r = _httpx.get("https://api.groq.com/openai/v1/models", headers=headers, timeout=10.0)
        return {"ok": True, "status": r.status_code, "key_prefix": key[:6]}
    except Exception as e:
        return {"ok": False, "error": str(e)}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host=HOST, port=PORT)
