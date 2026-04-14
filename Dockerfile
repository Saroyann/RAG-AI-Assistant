# Ultra-lightweight build for Railway deployment
FROM python:3.9-slim

WORKDIR /app

# Install minimal system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libopenblas-dev \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/*

# Upgrade pip
RUN pip install --no-cache-dir --upgrade pip setuptools wheel

# Copy application code FIRST (layer caching)
COPY main.py config.py ./
COPY rag/ ./rag/
COPY prompts/ ./prompts/
COPY chat_history/ ./chat_history/

# Install Python dependencies with aggressive cleanup
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt && \
    find /usr/local/lib/python3.9 -name "tests" -type d -exec rm -rf {} + 2>/dev/null || true && \
    find /usr/local/lib/python3.9 -name "*.pyc" -delete && \
    find /usr/local/lib/python3.9 -name "__pycache__" -type d -exec rm -rf {} + 2>/dev/null || true && \
    find /usr/local/lib/python3.9 -name "*.dist-info" -type d -exec rm -rf {} + 2>/dev/null || true && \
    find /usr/local/lib/python3.9 -name "*.egg-info" -type d -exec rm -rf {} + 2>/dev/null || true

# Create data directories (will be populated by volumes or manual upload)
RUN mkdir -p /app/data /app/models /app/chat_history

# Set environment
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    TRANSFORMERS_CACHE=/app/models \
    HF_HOME=/app/models \
    TORCH_HOME=/app/models

EXPOSE 8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
