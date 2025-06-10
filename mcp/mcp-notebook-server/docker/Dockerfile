# INMPARA Notebook MCP Server - Production Docker Image
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    sqlite3 \
    git \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy source code
COPY src/ ./src/
COPY bin/ ./bin/
COPY scripts/ ./scripts/

# Create necessary directories
RUN mkdir -p /data/vault /data/db /app/logs

# Set permissions
RUN chmod +x scripts/*.sh bin/*.py

# Default environment variables
ENV PYTHONPATH=/app/src
ENV VAULT_PATH=/data/vault
ENV DATABASE_PATH=/data/db/inmpara.db
ENV LOG_LEVEL=INFO

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python3 bin/run_production_server.py --test || exit 1

# Default command
CMD ["python3", "bin/run_production_server.py", "--vault-path", "/data/vault"]

# Expose MCP port (for future HTTP transport)
EXPOSE 8000

# Volume mounts
VOLUME ["/data/vault", "/data/db", "/app/logs"]
