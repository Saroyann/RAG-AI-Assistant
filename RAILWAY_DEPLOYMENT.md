# Railway Deployment Guide

## ⚠️ Critical: Image Size Issue Resolved

The Docker image was 7.8 GB because of heavy ML dependencies (sentence-transformers, faiss, PyTorch). 

**Solution**: Use Railway Volumes to store models outside the image.

### Why Volumes?
- Docker image now only ~1-2 GB (just runtime + code)
- Models are stored in persistent 5GB volume
- Models persist across container restarts (fast startup)
- No more size limit issues

---

## Prerequisites
- Railway account: https://railway.app
- Docker installed (for local testing)
- Git repository pushed to GitHub

## Automatic Deployment (Recommended)

Railway will automatically detect and use:
- **Dockerfile** - Custom build configuration
- **railway.toml** - Volumes and environment variables

### 1. Push Updated Code to GitHub

```bash
git add .
git commit -m "Add Docker optimization with Railway volumes"
git push origin main
```

### 2. Deploy on Railway

- Go to Railway dashboard → New Project
- Select "Deploy from GitHub"
- Choose your repository
- Railway will auto-detect `railway.toml` with volume configuration

### 3. Configure Additional Environment Variables

In Railway dashboard → Variables tab, add:

```
GEMINI_API_KEY=your_gemini_api_key_here
MODEL_NAME=gemini-2.0-flash-exp
TOP_K=3
RETRIEVE_MIN_SCORE=0.4
MAX_CONTEXT_WORDS=400
DOCUMENT_PATH=/app/data/data.jsonl
USER_DATA_PATH=/app/data/data.json
COURSES_PATH=/app/data/courses.json
LEARNING_PATHS_PATH=/app/data/learning_paths.json
COURSE_LEVELS_PATH=/app/data/course_levels.json
TUTORIALS_PATH=/app/data/tutorials.json
TRANSFORMERS_CACHE=/app/models
```

### 4. Monitor Deployment

- Railway will detect Dockerfile and build using Docker
- First build: ~5-10 minutes (downloads and caches models to volume)
- Subsequent restarts: ~30 seconds (models already cached)
- Check build logs: Deployments → View Logs

### 5. Test Your API

After successful deployment:
- Visit: `https://your-railway-domain.com/docs` (Swagger UI)
- Test endpoint: `POST /chat` with sample query

---

## What Changed

✅ **Dockerfile** - Multi-stage build, aggressive optimization
✅ **railway.toml** - Volumes configuration (5GB models, 2GB data)
✅ **rag/embedder.py** - Models load from persistent volume
✅ **.dockerignore** - Excludes unnecessary files
✅ **Environment variables** - TRANSFORMERS_CACHE=/app/models

---

## Expected Results

| Metric | Before | After |
|--------|--------|-------|
| Docker Image Size | 7.8 GB ❌ | 1-2 GB ✅ |
| Limit | 4 GB | 4 GB supports image now |
| Model Loading | Every restart | Cached on volume |
| First Startup | N/A | ~2-3 min (model download) |
| Later Startups | N/A | ~30 sec (volume cached) |

---

## Troubleshooting

### "Deployment failed during build process"
1. Check Railway build logs for specific error
2. Verify GitHub repository is public or Railway has access
3. Check for syntax errors in Dockerfile or requirements.txt

### "Image of size X GB exceeded limit"  
- This should be fixed now! Image is only 1-2 GB
- If still occurring: upgrade Railway plan

### "Model download timeout"
- First deployment downloads models to volume (can take 5-10 min)
- Wait for build to complete in Railway logs
- Subsequent deployments are much faster

### "404 on API endpoints"
- Wait for full deployment to complete
- Check Variables are set correctly (especially GEMINI_API_KEY)
- Check Railway logs for runtime errors

---

## Local Testing (Optional)

To test locally before deployment:

```bash
# Create volumes for testing
docker volume create rag-models
docker volume create rag-data

# Build and run
docker build -t rag-assistant .
docker run -p 8000:8000 \
  -e GEMINI_API_KEY="your_key" \
  -e TRANSFORMERS_CACHE="/app/models" \
  -v rag-models:/app/models \
  -v rag-data:/app/data \
  rag-assistant
```

Then visit: http://localhost:8000/docs

---

## Next Deployment Attempts

Just push to GitHub:
```bash
git add .
git commit -m "Your changes"
git push origin main
```

Railway will automatically rebuild and redeploy!

