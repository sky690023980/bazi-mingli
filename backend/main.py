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
    import os as _os, httpx as _httpx, json as _json
    # Check ALL env vars containing GROQ/API/KEY
    relevant = {k: v for k, v in _os.environ.items() 
                if any(x in k.upper() for x in ["GROQ", "API", "KEY", "LLM"])}
    groq_val = _os.environ.get("GROQ_API_KEY", "")
    return {"env_groq_key": repr(groq_val), "relevant_envs": relevant,
            "env_groq_key_len": len(groq_val), "env_groq_key_bytes": list(bytes(groq_val, "utf-8"))}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host=HOST, port=PORT)
