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



@app.get("/api/debug")
def debug():
    import os, httpx
    groq_key = os.getenv("groq_api_key", "")
    try:
        r = httpx.get("https://api.groq.com/openai/v1/models", 
                     headers={"Authorization": f"Bearer {groq_key}"}, timeout=5.0)
        return {"status": "ok", "groq_access": True, "status_code": r.status_code}
    except Exception as e:
        return {"status": "error", "groq_access": False, "error": str(e)}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host=HOST, port=PORT)
