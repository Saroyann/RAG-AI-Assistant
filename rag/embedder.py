import re
import os
import threading
import numpy as np
import requests
from typing import List, Union
from pathlib import Path

_embedding_cache = {}
_cache_lock = threading.Lock()

# HuggingFace Inference API endpoint
HF_API_URL = "https://api-inference.huggingface.co/pipeline/feature-extraction"
HF_API_KEY = os.getenv("HF_API_KEY", "hf_PXxyzABCDEFGHIJKLMNOPQRSTUVWXYZ")  # Get from env
MODEL_NAME = os.getenv("EMBEDDING_MODEL", "sentence-transformers/all-MiniLM-L6-v2")

# Fallback: Use local sentence-transformers if API not available
USE_LOCAL_EMBEDDINGS = os.getenv("USE_LOCAL_EMBEDDINGS", "false").lower() == "true"

if USE_LOCAL_EMBEDDINGS:
    try:
        from sentence_transformers import SentenceTransformer
        _local_model = None
        MODEL_CACHE_DIR = os.getenv("TRANSFORMERS_CACHE", "/app/models")
        Path(MODEL_CACHE_DIR).mkdir(parents=True, exist_ok=True)
    except ImportError:
        USE_LOCAL_EMBEDDINGS = False


def clean_text(text: str) -> str:
    """Clean and normalize text"""
    if not text:
        return ""
    
    text = re.sub(r"&nbsp;?", " ", text)
    text = re.sub(r"<br\s*/?>", " ", text, flags=re.I)
    text = re.sub(r"\s{2,}", " ", text)
    return text.strip()


def embed_with_hf_api(texts: List[str]) -> np.ndarray:
    """
    Use HuggingFace Inference API for embeddings (minimal dependencies).
    Free tier: 30k requests/month. No model download needed!
    """
    headers = {"Authorization": f"Bearer {HF_API_KEY}"}
    
    response = requests.post(
        HF_API_URL,
        headers=headers,
        json={"inputs": texts, "options": {"wait_for_model": True}},
        timeout=30
    )
    
    if response.status_code != 200:
        raise RuntimeError(f"HF API error: {response.status_code} - {response.text}")
    
    return np.array(response.json())


def embed_with_local(texts: List[str]) -> np.ndarray:
    """Fallback: Use local sentence-transformers if available"""
    global _local_model
    
    _model_lock = threading.Lock()
    if _local_model is None:
        with _model_lock:
            if _local_model is None:
                _local_model = SentenceTransformer(
                    MODEL_NAME,
                    cache_folder=MODEL_CACHE_DIR,
                    device="cpu"
                )
    
    return _local_model.encode(texts, normalize_embeddings=True)


def embed(
    texts: Union[str, List[str]]
) -> np.ndarray:
    """
    Generate embeddings with fallback strategy:
    1. Try HuggingFace Inference API (no local files needed)
    2. Fallback to local sentence-transformers if available
    
    This keeps Docker image size ~1 GB instead of 7+ GB!
    """
    single = False
    if isinstance(texts, str):
        texts = [texts]
        single = True
    
    # Clean texts
    texts = [clean_text(t) for t in texts]
    
    # Try HF API first
    if HF_API_KEY and HF_API_KEY != "hf_PXxyzABCDEFGHIJKLMNOPQRSTUVWXYZ":
        try:
            result = embed_with_hf_api(texts)
            if single:
                return result[0]
            return result
        except Exception as e:
            print(f"HF API failed: {e}, falling back to local...")
    
    # Fallback to local
    if USE_LOCAL_EMBEDDINGS:
        try:
            result = embed_with_local(texts)
            if single:
                return result[0]
            return result
        except Exception as e:
            print(f"Local embeddings failed: {e}")
            raise RuntimeError("Embedding service unavailable. Set HF_API_KEY environment variable.")
    
    raise RuntimeError("Embeddings unavailable. Set HF_API_KEY or USE_LOCAL_EMBEDDINGS=true")

