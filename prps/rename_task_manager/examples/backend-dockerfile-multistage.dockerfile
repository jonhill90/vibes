# Source: infra/task-manager/backend/Dockerfile
# Pattern: Multi-stage Dockerfile with uv package manager
# Extracted: 2025-10-07
# Relevance: 10/10 - Complete backend Dockerfile pattern for task manager

# ============================================================================
# BUILD STAGE - Install dependencies with uv
# ============================================================================
FROM python:3.12-slim AS builder

WORKDIR /build

# Install uv package manager
RUN pip install --no-cache-dir uv

# Copy dependency files
COPY pyproject.toml ./

# Create virtual environment and install dependencies using uv
# Using --frozen to ensure reproducible builds (requires uv.lock if exists)
RUN uv venv /venv && \
    . /venv/bin/activate && \
    uv pip install -r pyproject.toml

# ============================================================================
# RUNTIME STAGE - Minimal production image
# ============================================================================
FROM python:3.12-slim

WORKDIR /app

# Copy virtual environment from builder stage
# This is more efficient than reinstalling dependencies
COPY --from=builder /venv /venv

# Copy application source code
COPY src/ src/
COPY alembic/ alembic/
COPY start.sh start.sh

# Set up Python environment
ENV PYTHONPATH="/app:$PYTHONPATH"
ENV PYTHONUNBUFFERED=1
ENV PATH="/venv/bin:$PATH"

# Expose ports
# 8000 - FastAPI REST API
# 8051 - MCP server endpoint
EXPOSE 8000 8051

# Health check for API endpoint
# CRITICAL: Uses Python's urllib.request to check health endpoint
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/health')"

# Start both FastAPI and MCP servers
# Using startup script to run both services
CMD ["./start.sh"]
