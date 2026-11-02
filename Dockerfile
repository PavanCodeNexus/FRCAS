# Production Dockerfile for FaceMark FRCAS
FROM python:3.10-slim

# Prevent Python buffering and bytecode generation
ENV DEBIAN_FRONTEND=noninteractive
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

# Install system libraries required by OpenCV and ONNX Runtime on Linux
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libgl1 \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    libxrender-dev \
    libgomp1 \
    curl \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy dependency specifications
COPY requirements.txt .

# Install Python packages
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copy application files
COPY . .

# Pre-download InsightFace model during build (buffalo_sc lightweight detection + arcface)
ENV INSIGHTFACE_MODEL=buffalo_sc
ENV PORT=8000

RUN python scripts/download_models.py

# Expose default port
EXPOSE 8000

# Run Uvicorn production server (supporting cloud PORT environment variables)
CMD ["sh", "-c", "uvicorn backend.app.main:app --host 0.0.0.0 --port ${PORT:-8000} --workers 1"]
