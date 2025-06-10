# INMPARA Notebook MCP Server - Production Docker Image
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    sqlite3 \
    git \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy source code and entry point
COPY src/ ./src/
COPY server.py .

# Create necessary directories (new vault structure)
RUN mkdir -p /app/vault/.notebook /app/logs

# Set permissions
RUN chmod +x server.py

# Default environment variables (updated for new structure)
ENV PYTHONPATH=/app/src
ENV VAULT_PATH=/app/vault
ENV DATABASE_PATH=/app/vault/.notebook/inmpara.db
ENV LOG_LEVEL=INFO

# Health check (updated for new entry point)
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python3 -c "from src.server.mcp_server import INMPARAServer; print('Server imports OK')" || exit 1

# Default command (updated for new entry point)
CMD ["python3", "server.py"]

# Expose MCP port (for future HTTP transport)
EXPOSE 8000

# Volume mounts (updated for vault structure)
VOLUME ["/app/vault", "/app/logs"]
