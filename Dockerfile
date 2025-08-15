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

WORKDIR /app

# Copy only requirements first to leverage Docker layer caching
COPY requirements.txt ./

# CPU-only PyTorch wheels from extra index
RUN pip install --no-cache-dir -r requirements.txt

# Copy app code
COPY . .

# Pre-download model files without loading them into memory to avoid OOM
RUN python - <<'PY'
from huggingface_hub import snapshot_download
snapshot_download(repo_id='Salesforce/blip-image-captioning-base')
print('Models cached')
PY

# Expose port
EXPOSE 8001

# Use single worker for free-tier CPU; scale via replicas if needed
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8001", "--workers", "1"]