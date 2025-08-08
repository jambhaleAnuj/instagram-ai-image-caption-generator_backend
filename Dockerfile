# Use official slim Python base
FROM python:3.12-slim

# Install runtime OS deps (Pillow, OpenMP, etc.)
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
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

# Pre-download models at build time to avoid cold start on instance
RUN python - <<'PY'
from transformers import BlipProcessor, BlipForConditionalGeneration
BlipProcessor.from_pretrained('Salesforce/blip-image-captioning-base')
BlipForConditionalGeneration.from_pretrained('Salesforce/blip-image-captioning-base')
print('Models cached')
PY

# Expose port
EXPOSE 8001

# Use multiple workers if CPU allows; tune for free tier
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8001", "--workers", "1"]