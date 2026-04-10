# Vercel Deployment Guide

## Option 1: Deploy via GitHub (Recommended)
1. Push `bazi_system/web-frontend` to a GitHub repository
2. Go to https://vercel.com/new
3. Import the repository
4. Vercel auto-detects Vite and deploys
5. Get your permanent URL like `xxx.vercel.app`

## Option 2: Deploy via Vercel CLI
```bash
npm i -g vercel
cd bazi_system/web-frontend
vercel --prod
```

## IMPORTANT: Backend Configuration
For the web app to work, the backend API must be accessible:

**Option A - Expose local backend (for development):**
Use ngrok to expose local backend:
```bash
ngrok http 8000
# Copy the https://xxx.ngrok.io URL
```
Then create `.env.local`:
```
VITE_API_BASE=https://xxx.ngrok.io
```
Redeploy with the new API URL.

**Option B - Deploy backend to Railway/Render:**
See deploy-guide.md for backend deployment instructions.
