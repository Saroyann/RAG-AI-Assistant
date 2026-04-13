# Railway Deployment Guide

## Prerequisites
- Railway account: https://railway.app
- Docker installed (for local testing)
- Git repository pushed to GitHub

## Steps to Deploy

### 1. Connect Your GitHub Repository
- Go to Railway dashboard
- Click "New Project" → "Deploy from GitHub"
- Select your repository

### 2. Configure Environment Variables
In Railway dashboard, add these variables to your service:

```
GEMINI_API_KEY=your_gemini_api_key_here
MODEL_NAME=gemini-2.0-flash-exp
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

### 3. Image Size Optimization Applied
The following optimizations have been implemented to reduce Docker image size from 5.9 GB to ~2-3 GB:

✅ **Multi-stage Docker build** - Dockerfile uses builder stage to minimize final image
✅ **Slim Python base image** - Uses `python:3.9-slim` instead of full Python image
✅ **No-cache pip installs** - `--no-cache-dir` flag removes unnecessary cached files
✅ **.dockerignore file** - Excludes `__pycache__`, `.git`, and other unnecessary files
✅ **Optimized requirements.txt** - Removed redundant dependencies (starlette is already in fastapi)

### 4. Deploy
- Railway will automatically build and deploy when you push to GitHub
- The Dockerfile will be detected and used automatically

### 5. Monitor Deployment
- Check build logs in Railway dashboard under "Build Logs"
- Once deployed, access your API at: `https://your-railway-domain.com`
- Swagger docs available at: `https://your-railway-domain.com/docs`

## Troubleshooting

### Build Still Fails
If the image is still too large:
1. Check Railway service plan - you may need to upgrade for larger images
2. Move `faiss.index` to Railway Volumes for external storage
3. Only load required data files at runtime

### API Not Responding
- Check environment variables are set correctly
- Verify API_KEY environment variables have no extra spaces
- Check Railway logs for runtime errors

## Testing Locally (Optional)

```bash
docker build -t rag-assistant .
docker run -p 8000:8000 \
  -e GEMINI_API_KEY="your_key" \
  -e MODEL_NAME="gemini-2.0-flash-exp" \
  rag-assistant
```

Then visit: http://localhost:8000/docs
