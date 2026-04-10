# Railway 后端部署指南

## 问题
backend 使用 Ollama（`http://localhost:11434`），Ollama 运行在你本地电脑上，Railway 的服务器访问不到。
**需要改用云端 LLM API**（如 OpenAI / 通义千问 / DeepSeek 等）。

## 步骤 1：修改 backend/.env 支持云端 LLM

推荐用 **Qwen（通义千问）** 或 **DeepSeek**：
```bash
# .env 修改为：
llm_provider = qwen  # 或 openai / deepseek

# 通义千问（推荐）
qwen_api_key = sk-your-key-here
qwen_model = qwen-plus

# 或 DeepSeek
# deepseek_api_key = sk-your-key-here
# deepseek_model = deepseek-chat
```

## 步骤 2：Railway 部署

1. 打开 https://railway.app → 用 GitHub 登录
2. 点击 **"New Project"** → **"Deploy from GitHub repo"**
3. 选择仓库 `sky690023980/bazi-mingli`
4. 点击项目 Settings → **Root Directory** 设为 `/backend`
5. 在 **Variables** 中添加：
   ```
   llm_provider = qwen
   qwen_api_key = sk-你的API密钥
   qwen_model = qwen-plus
   host = 0.0.0.0
   port = 8001
   debug = false
   ```
6. Railway 会自动检测 `requirements.txt` 并安装依赖
7. 部署完成后，Railway 会给你一个 URL，如：`https://xxx.railway.app`

## 步骤 3：更新 Vercel 前端环境变量

在 Vercel 的 Environment Variables 中：
```
VITE_API_BASE = https://xxx.railway.app
```
然后重新部署。

## 快速验证（本地测试）

```bash
cd backend
# 修改 .env 为云端 LLM
uvicorn main:app --reload --port 8001
# 测试 API: http://localhost:8001/api/health
```
