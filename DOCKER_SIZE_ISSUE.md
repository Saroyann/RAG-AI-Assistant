# Critical Issue: Dependency Size

The Python dependencies for this project total ~7-8 GB:
- sentence-transformers: ~1.5 GB (includes PyTorch)
- faiss-cpu: ~500 MB
- google-generativeai: ~100 MB
- Other ML libraries: ~2-3 GB

## Solutions (by priority):

### 1. ⭐ BEST: Use Railway Volumes (Free)
Store models and indexes outside the Docker image:

In `railway.toml` or Railway dashboard:
```yaml
volumes:
  - mount_path: /app/models
    size: 10GB
  - mount_path: /app/data
    size: 10GB
```

Then modify your code to load models from `/app/models/` first.

### 2. Use Lightweight Embeddings (Medium effort)
Replace sentence-transformers with a smaller model:

```python
# Option A: Use Nomic (much smaller)
# from sentence_transformers import SentenceTransformer
# model = SentenceTransformer('nomic-ai/nomic-embed-text-v1')
# Size: ~300 MB instead of 1.5 GB

# Option B: Lazy load model (only when needed)
# Load model once and cache it, not on startup
```

### 3. Use HuggingFace Model Server
Offload embedding to a separate HuggingFace Inference API:
```python
import requests
response = requests.post("https://api-inference.huggingface.co/models/...", 
                         json={"inputs": text})
```

### 4. Upgrade Railway Plan
If using Railway, upgrade to a plan supporting larger images (currently limited to 4 GB).

---

## Recommended Quick Fix:

1. **Create `railway.toml` in repository root:**

```toml
[build]
builder = "dockerfile"

[deploy]
restartPolicyMaxRetries = 3

[[volumes]]
mountPath = "/app/models"
size = "5GB"

[[volumes]]  
mountPath = "/app/data"
size = "5GB"
```

2. **Modify `rag/embedder.py` to load models from volume:**

```python
import os
from pathlib import Path

MODEL_CACHE_DIR = Path("/app/models")
MODEL_CACHE_DIR.mkdir(exist_ok=True)

def get_model(name: str = "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"):
    global _model
    if _model is None:
        with _model_lock:
            if _model is None:
                _model = SentenceTransformer(
                    name,
                    cache_folder=str(MODEL_CACHE_DIR)
                )
    return _model
```

3. **Push changes and redeploy on Railway**

This avoids the 7.8 GB image size issue entirely!
