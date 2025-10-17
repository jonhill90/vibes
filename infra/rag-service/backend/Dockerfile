# RAG Service Backend - Docker Image
# Multi-stage build for production optimization

FROM python:3.11-slim as base

# Set working directory
WORKDIR /app

# Install system dependencies
# Added libgl1 and libglib2.0-0 for Docling PDF parsing (fixes libGL.so.1 error)
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    curl \
    libgl1 \
    libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY src/ ./src/

# Expose FastAPI port (default 8003, can be overridden by API_PORT env var)
EXPOSE 8003

# Health check (port will match API_PORT from docker-compose)
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD curl -f http://localhost:${API_PORT:-8003}/health || exit 1

# Run FastAPI server (port from API_PORT env var)
CMD uvicorn src.main:app --host 0.0.0.0 --port ${API_PORT:-8003} --reload
