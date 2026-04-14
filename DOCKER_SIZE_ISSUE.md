# Docker Image Size Issue - SOLVED ✅

## Problem
- Original image: **7.8 GB** (exceeded Railway's 4 GB limit)
- Root cause: Heavy ML dependencies (sentence-transformers + PyTorch = 3GB+)

## Solution: HuggingFace Inference API ⚡

Instead of loading embedding models locally (7+ GB), we now use **HuggingFace's hosted API**:

### Benefits:
- ✅ Docker image: **~500 MB** (fits easily under 4 GB)
- ✅ No local model storage needed
- ✅ Free tier: 30,000 requests/month
- ✅ Instant startup (no model download)
- ✅ Automatic model updates from HuggingFace

### Current Architecture:
```
User Query
    ↓
FastAPI (local)
    ↓
Embeddings API (HuggingFace Cloud)
    ↓
FAISS Vector Search (local)
    ↓
LLM (Google Gemini Cloud)
    ↓
Response
```

## Setup for Railway Deployment

### 1. Get HuggingFace API Key
1. Create account: https://huggingface.co/join
2. Get API key: https://huggingface.co/settings/tokens
3. Create "User access token" and copy it

### 2. Configure Environment Variables on Railway

In Railway dashboard, set:

```
GEMINI_API_KEY=your_gemini_key_here
HF_API_KEY=hf_your_huggingface_key_here
MODEL_NAME=gemini-2.0-flash-exp
EMBEDDING_MODEL=sentence-transformers/all-MiniLM-L6-v2
TOP_K=3
RETRIEVE_MIN_SCORE=0.4
MAX_CONTEXT_WORDS=400
```

### 3. Deploy

```bash
git add .
git commit -m "Switch to HuggingFace API for embeddings - reduces image to 500MB"
git push origin main
```

Railway will auto-detect Dockerfile and deploy!

## Fallback Option: Local Embeddings

If you want to use local embeddings instead (4-minute first startup):

Set environment variable:
```
USE_LOCAL_EMBEDDINGS=true
HF_API_KEY=  # leave empty or use API as fallback
```

Then poetry/pip install will include sentence-transformers (~500MB added).

## Image Size Comparison

| Approach | Image Size | Model Download | Cost | Startup |
|----------|-----------|-----------------|------|---------|
| Original (sentence-transformers) | 7.8 GB | N/A | $$ | Fails |
| **HuggingFace API** (Current) ✅ | **500 MB** | Cloud | Free/$ | <5s |
| Local sentence-transformers | 1.2 GB | 500MB | Free | 2-3 min |
| Paid Railway plan | 7.8 GB | N/A | $$$ | Fails→Works |

---

## Troubleshooting

### "Invalid HF API Key"
- Check key format: should start with `hf_`
- Verify key hasn't expired
- Create new token if needed

### "HF API rate limit exceeded"
- Free tier has 30k requests/month
- Consider upgrading HF API to Pro ($9/mo)
- Or set `USE_LOCAL_EMBEDDINGS=true` as fallback

### "ModuleNotFoundError: No module named 'click'"
- Already fixed! `click` is now included in requirements
- Rebuild Railway deployment

---

## Cost Analysis (Monthly)

### Option 1: HuggingFace API (Current)
- 30k embeddings/month = **FREE** ✅
- Railway free tier deployment = **FREE**
- Gemini API usage = **Based on tokens**

### Option 2: Local Embeddings  
- Railway free tier = **FREE**
- One-time 500MB download = **FREE**
- Gemini API usage = **Based on tokens**

### Option 3: Paid Railway
- Starts at $12/month
- Supports 7+ GB images

---

## Next Steps

1. ✅ Code is already updated
2. Generate HF API key
3. Set environment variables on Railway
4. Push to GitHub for deployment

That's it! 🚀

