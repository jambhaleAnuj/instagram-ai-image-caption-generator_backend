# Use official slim Python base
FROM python:3.12-slim

# Install runtime OS deps (Pillow, HTTPS certs, curl for healthchecks)
RUN apt-get update && apt-get install -y --no-install-recommends \
    ca-certificates \
    curl \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    libxrender1 \
    && rm -rf /var/lib/apt/lists/*

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    HOME=/app \
    HF_HOME=/app/.cache/huggingface \
    HUGGINGFACE_HUB_CACHE=/app/.cache/huggingface \
    TORCH_HOME=/app/.cache/torch \
    NUMBA_CACHE_DIR=/app/.cache/numba
ENV OMP_NUM_THREADS=1 MKL_NUM_THREADS=1 NUMEXPR_NUM_THREADS=1

WORKDIR /app

# Copy only requirements first to leverage Docker layer caching
COPY requirements.txt ./

# CPU-only PyTorch wheels from extra index
RUN pip install --no-cache-dir -r requirements.txt

# Ensure writable caches in image for any runtime user
RUN mkdir -p /app/.cache/huggingface /app/.cache/transformers /app/.cache/torch /app/.cache/numba \
    && chmod -R 777 /app/.cache

# Copy app code
COPY . .

# Pre-download model files into the configured cache dir to avoid runtime downloads
RUN python - <<'PY'
from huggingface_hub import snapshot_download
import os
cache_dir = os.environ.get('HUGGINGFACE_HUB_CACHE', '/app/.cache/huggingface')
snapshot_download(repo_id='Salesforce/blip-image-captioning-base', cache_dir=cache_dir)
print('Models cached in', cache_dir)
PY

# Expose port (Hugging Face Spaces provides PORT env)
EXPOSE 7860 8000 8001

# Use single worker for free-tier CPU; respect PORT env on Spaces
ENV PORT=8001
HEALTHCHECK --interval=30s --timeout=5s --start-period=60s --retries=5 \
    CMD curl -fsS http://localhost:${PORT}/healthz || exit 1
CMD ["bash", "-lc", "uvicorn main:app --host 0.0.0.0 --port ${PORT:-8001} --workers 1 --log-level warning"]