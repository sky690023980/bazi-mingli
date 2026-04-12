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

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host=HOST, port=PORT)
