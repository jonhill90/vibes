# Source: /Users/jon/source/vibes/infra/task-manager/backend/Dockerfile
# Pattern: Multi-stage Docker build for minimal Python Alpine image
# Extracted: 2025-10-13
# Relevance: 9/10 - Excellent pattern for lightweight containerization

# ============================================================================
# MULTI-STAGE DOCKERFILE PATTERN
# ============================================================================
# This pattern creates a minimal production image by:
# 1. Builder stage: Install dependencies with uv (fast package manager)
# 2. Runtime stage: Copy only venv, not build tools
# Result: Smaller image, faster builds, cached layers

# ============================================================================
# BUILD STAGE - Install dependencies with uv
# ============================================================================
FROM python:3.12-slim AS builder

WORKDIR /build

# PATTERN 1: Use uv for fast dependency installation
# uv is much faster than pip for dependency resolution
RUN pip install --no-cache-dir uv

# PATTERN 2: Copy only dependency files first (layer caching)
# This means dependency layer is cached unless pyproject.toml changes
COPY pyproject.toml ./

# PATTERN 3: Create virtual environment and install dependencies
# Using venv isolation even in Docker for clean separation
RUN uv venv /venv && \
    . /venv/bin/activate && \
    uv pip install -r pyproject.toml

# ============================================================================
# RUNTIME STAGE - Minimal production image
# ============================================================================
FROM python:3.12-slim

WORKDIR /app

# PATTERN 4: Copy virtual environment from builder stage
# This is more efficient than reinstalling dependencies
# Only the compiled packages, not build tools
COPY --from=builder /venv /venv

# PATTERN 5: Copy application source code
# Structure matches our vibesbox layout
COPY src/ src/

# PATTERN 6: Set up Python environment variables
ENV PYTHONPATH="/app:$PYTHONPATH"
ENV PYTHONUNBUFFERED=1  # CRITICAL: Don't buffer output (needed for streaming)
ENV PATH="/venv/bin:$PATH"

# PATTERN 7: Expose MCP server port
# Vibesbox only needs MCP endpoint, not API endpoint
EXPOSE 8051

# PATTERN 8: Health check for MCP server
# FastMCP provides a health endpoint by default
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8051/health')"

# PATTERN 9: Run MCP server directly
# Simple single-process container (no need for complex startup script)
CMD ["python", "-m", "src.mcp_server"]


# ============================================================================
# ALPINE VARIANT (for even smaller images)
# ============================================================================
# For vibesbox, we can use Alpine for minimal size (~50MB vs ~150MB)
#
# FROM python:3.12-alpine AS builder
#
# WORKDIR /build
#
# # Alpine requires build dependencies for some Python packages
# RUN apk add --no-cache gcc musl-dev libffi-dev
#
# RUN pip install --no-cache-dir uv
# COPY pyproject.toml ./
# RUN uv venv /venv && \
#     . /venv/bin/activate && \
#     uv pip install -r pyproject.toml
#
# FROM python:3.12-alpine
#
# WORKDIR /app
#
# # Alpine runtime dependencies (minimal)
# RUN apk add --no-cache libffi
#
# COPY --from=builder /venv /venv
# COPY src/ src/
#
# ENV PYTHONPATH="/app:$PYTHONPATH"
# ENV PYTHONUNBUFFERED=1
# ENV PATH="/venv/bin:$PATH"
#
# EXPOSE 8051
#
# HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
#     CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8051/health')"
#
# CMD ["python", "-m", "src.mcp_server"]


# ============================================================================
# KEY DIFFERENCES FROM TASK-MANAGER DOCKERFILE
# ============================================================================
# 1. Single port (8051 MCP) vs dual ports (8000 API + 8051 MCP)
# 2. No start.sh script needed (single process)
# 3. Optional Alpine variant for smaller size
# 4. No alembic/ migrations (stateless container)
# 5. Health check targets MCP endpoint only

# ============================================================================
# USAGE NOTES
# ============================================================================
# Build: docker build -t vibesbox:latest .
# Run: docker run -p 8051:8051 vibesbox:latest
# Size: ~150MB (slim) or ~50MB (alpine)
# Startup: < 3 seconds
