# Railway Deployment Guide

## 🎉 Image Size Issue SOLVED!

Docker image reduced from **7.8 GB → 500 MB** using HuggingFace Inference API for embeddings.

---

## Prerequisites
- Railway account: https://railway.app
- HuggingFace account: https://huggingface.co/join
- Git repository pushed to GitHub

## Deployment Steps

### 1. Get HuggingFace API Key

1. Go to https://huggingface.co/settings/tokens
2. Click "New token" → User access token
3. Copy the key (looks like: `hf_abcdef1234567890...`)
4. Keep it safe!

### 2. Push Code to GitHub

```bash
git add .
git commit -m "Switch to HuggingFace API - fixes Docker image size"
git push origin main
```

### 3. Deploy on Railway

- Go to Railway dashboard → New Project
- Select "Deploy from GitHub"
- Choose your repository
- Railway auto-detects Dockerfile and deploys

### 4. Set Environment Variables

In Railway dashboard → Variables tab, add:

```
# Required: LLM Configuration
GEMINI_API_KEY=your_gemini_api_key_here
MODEL_NAME=gemini-2.0-flash-exp

# Required: Embeddings (HuggingFace API)
HF_API_KEY=hf_your_huggingface_token_here
EMBEDDING_MODEL=sentence-transformers/all-MiniLM-L6-v2

# Optional: RAG Configuration
TOP_K=3
RETRIEVE_MIN_SCORE=0.4
MAX_CONTEXT_WORDS=400
DOCUMENT_PATH=data/data.jsonl
USER_DATA_PATH=data/data.json
COURSES_PATH=data/courses.json
LEARNING_PATHS_PATH=data/learning_paths.json
COURSE_LEVELS_PATH=data/course_levels.json
TUTORIALS_PATH=data/tutorials.json
```

### 5. Monitor Deployment

- Click on service → "Deployment" tab
- Watch build logs (should complete in 2-3 minutes)
- Once green, your API is live!

### 6. Test Your API

Visit: `https://your-railway-domain.com/docs`

Send test request:
```
POST /chat
{
  "query": "What is machine learning?",
  "session_id": "test-session-123"
}
```

---

## Architecture

```
┌─────────────────┐
│   Your App      │
│   (Railway)     │
│   500 MB ✅     │
└────────┬────────┘
         │
    ┌────┴─────────────────────┐
    │                           │
    ▼                           ▼
┌─────────────────┐    ┌──────────────────┐
│ FAISS Search    │    │ HuggingFace API  │
│ (local, fast)   │    │ Embeddings       │
└─────────────────┘    └──────────────────┘
                            (cloud)
    ▼
┌─────────────────┐
│ Google Gemini   │
│ LLM (cloud)     │
└─────────────────┘
```

---

## Key Changes

✅ **requirements.txt** - Removed PyTorch/sentence-transformers (saves 2+ GB)
✅ **rag/embedder.py** - Uses HuggingFace API instead of local models
✅ **Dockerfile** - Ultra-lightweight (~500 MB final image)
✅ **railway.toml** - No volumes needed (models in cloud)
✅ **.dockerignore** - Keeps unnecessary files out

---

## Cost Breakdown (Monthly)

| Component | Cost |
|-----------|------|
| Railway free tier (hosting) | FREE ✅ |
| HuggingFace API (30k requests) | FREE ✅ |
| Google Gemini API | ~$0.01-1 (usage-based) |
| **Total** | **FREE - $1** |

---

## Troubleshooting

### "Deployment failed during build"
- Check Railway build logs for specific error
- Ensure GitHub repo is public
- Check requirements.txt syntax

### "Invalid HF API Key"
- Key must start with `hf_`
- Verify it's a "User access token"
- Create new token if expired

### "HF API rate limit exceeded"
- Free tier: 30k requests/month
- Upgrade to HF Pro ($9/mo) for unlimited
- Or set `USE_LOCAL_EMBEDDINGS=true` for fallback

### "ModuleNotFoundError"
- Should be fixed now (requirements updated)
- Force rebuild: push empty commit
```bash
git commit --allow-empty -m "Rebuild"
git push
```

### "API returns 502 Bad Gateway"
- Wait for container to fully start
- Check Railway logs for errors
- Verify all environment variables are set

---

## Need Help?

Check logs in Railway:
1. Service → Logs
2. Look for errors
3. Compare with troubleshooting section above

---

## Rollback to Local Embeddings (Optional)

If you prefer local embeddings instead of API:

1. Set environment variable:
   ```
   USE_LOCAL_EMBEDDINGS=true
   TRANSFORMERS_CACHE=/app/models
   ```

2. This enables fallback to sentence-transformers
3. First startup will be slow (downloads model)
4. Subsequent restarts will be fast (cached)

---

## Next Deployment Changes

Just push to GitHub and Railway will automatically rebuild:

```bash
git add .
git commit -m "Your changes"
git push origin main
```

Done! 🚀


