# Railway Deployment Guide

## ✅ Status: FIXED - Now Starts Successfully!

Docker image: **500 MB** ✅
Data loading: **Lazy** (only loads when needed) ✅
App startup: **Should succeed even without data files** ✅

---

## Prerequisites
- Railway account: https://railway.app
- HuggingFace account: https://huggingface.co/join  
- Git repository pushed to GitHub
- (Optional) Data file: `data.jsonl`

## Deployment Steps

### 1. Get HuggingFace API Key

1. Go to https://huggingface.co/settings/tokens
2. Click "New token" → User access token
3. Copy the key (looks like: `hf_abcdef1234567890...`)

### 2. Push Code to GitHub

```bash
git add .
git commit -m "Fix: Lazy load data files - app starts even without data"
git push origin main
```

### 3. Deploy on Railway

- Go to Railway dashboard → New Project  
- Select "Deploy from GitHub"
- Choose your repository
- Wait for deployment to complete

### 4. Set Environment Variables

In Railway dashboard → Variables tab, add:

```
# Required: LLM Configuration
GEMINI_API_KEY=your_gemini_api_key_here
MODEL_NAME=gemini-2.0-flash-exp

# Required: Embeddings (HuggingFace API)
HF_API_KEY=hf_your_huggingface_token_here
EMBEDDING_MODEL=sentence-transformers/all-MiniLM-L6-v2

# Optional: RAG Configuration (defaults shown)
TOP_K=3
RETRIEVE_MIN_SCORE=0.4
MAX_CONTEXT_WORDS=400

# Optional: Data file paths (if using Railway Volumes)
DOCUMENT_PATH=data/data.jsonl
COURSES_PATH=data/courses.json
```

### 5. (Optional) Add Data via Railway Volumes

To use RAG features, you need to provide your data files.

**Option A: Upload via Railway Volumes**

1. In Railway → Service → "Volumes" tab
2. Create new volume: Mount path `/app/data`, size 1GB
3. Upload your data files:
   - `data.jsonl` (required for RAG)
   - `courses.json` (for recommendations)
   - Other supporting files

**Option B: Use Railway CLI**

```bash
# Install Railway CLI
npm install -g @railway/cli

# Login to Railway
railway login

# Link your service
railway link

# Upload data files to volume
railway volume upload /path/to/local/data.jsonl /app/data/data.jsonl
```

**Option C: Git LFS (Large Files)**

If your data files are large:

```bash
# Install Git LFS
git lfs install

# Track data files
git lfs track "data/*.jsonl"
git add .gitattributes

# Commit and push
git add data/
git commit -m "Add data files via Git LFS"
git push origin main
```

### 6. Check Deployment Status

- Railway dashboard → Service → Logs
- Should see something like:
  ```
  Starting Container
  INFO: Application startup complete
  INFO: Uvicorn running on http://0.0.0.0:8000
  ```

### 7. Test Your API

Visit: `https://your-railway-domain.com/docs`

**If data is NOT provided:**
- API starts successfully ✅
- Chat works but RAG returns: "Maaf, basis data pembelajaran belum tersedia..."
- Other features (tracking, recommendations) may be limited

**If data IS provided:**
- API starts successfully ✅
- Chat with RAG works fully ✅
- Recommendations and tracking work ✅

---

## What's Different Now?

✅ **Lazy Loading** - Data loads only when needed, not on startup
✅ **Graceful Degradation** - App starts even without data files
✅ **Better Error Handling** - Missing files don't crash the app
✅ **500 MB Image** - HuggingFace API removes local ML dependencies

---

## Architecture

```
Request → FastAPI (500MB image, Railway free tier)
         ↓
         → Check data available?
         ├─ YES → Search FAISS + Call LLM + Return answer
         └─ NO → Return friendly message "Data not available"
         ↓
         → HuggingFace API (embeddings, free tier)
         ↓  
         → Google Gemini (LLM, usage-based)
```

---

## Data File Format

**data.jsonl** (one JSON per line):
```json
{
  "name": "Python Basics",
  "summary": "Learn Python fundamentals",
  "description": "Complete Python course for beginners",
  "combined_text": "Python is... [full course content here]",
  "course_difficulty": "Beginner",
  "technologies": ["Python", "Programming"]
}
```

---

## Troubleshooting

### "ModuleNotFoundError"
- App should start now even without data
- If still failing: check Railway build logs
- Force rebuild: `git commit --allow-empty -m "Rebuild"`

### "FileNotFoundError: data/data.jsonl"
- This is now handled gracefully! ✅
- App will warn but continue starting
- Set up data via Volumes (see step 5 above)

### "HF API rate limit exceeded"
- Free tier: 30k requests/month
- Upgrade to HF Pro ($9/mo) for unlimited
- Or set `USE_LOCAL_EMBEDDINGS=true` + add volumes

### "No module named 'click'"
- Fixed in latest version ✅
- Run: `git push origin main` to trigger rebuild

### "API returns 404"
- Deployment still completing
- Check logs: `railway logs`
- Wait 1-2 minutes for full startup

---

## Monitoring

After deployment, monitor in Railway:

1. **Logs** → Check for errors
2. **Metrics** → CPU, Memory usage
3. **Health** → Should show "Running"

---

## Local Testing (Optional)

```bash
# Build locally
docker build -t rag-assistant .

# Run with environment variables
docker run -p 8000:8000 \
  -e GEMINI_API_KEY="your_key" \
  -e HF_API_KEY="hf_your_key" \
  rag-assistant

# Visit: http://localhost:8000/docs
```

---

## Cost (Monthly)

| Component | Cost |
|-----------|------|
| Railway hosting | FREE (free tier) |
| HuggingFace API | FREE (30k requests) |
| Google Gemini | $0.01-1 (usage) |
| **Total** | **FREE - $1** |

---

## Next Steps After Initial Deployment

1. Get your data files ready (JSONL format)
2. Create Railway Volume and upload data
3. Redeploy or upload data to `/app/data/`
4. Test RAG functionality

That's it! 🚀



