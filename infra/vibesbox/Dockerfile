# Vibesbox MCP Server - Multi-stage Dockerfile
# Lightweight containerized MCP server for secure command execution
# Pattern from: prps/streamlined_vibesbox/examples/docker_alpine_python_pattern.dockerfile

# ============================================================================
# BUILD STAGE - Install dependencies with uv
# ============================================================================
FROM python:3.11-slim AS builder

WORKDIR /build

# Install uv package manager for fast dependency installation
RUN pip install --no-cache-dir uv

# Copy dependency files (layer caching optimization)
COPY pyproject.toml ./

# Create virtual environment and install dependencies using uv
RUN uv venv /venv && \
    . /venv/bin/activate && \
    uv pip install -r pyproject.toml

# ============================================================================
# RUNTIME STAGE - Minimal production image
# ============================================================================
FROM python:3.11-slim

WORKDIR /app

# Install SSH client and rsync for remote operations
# Keeps image minimal while enabling remote connectivity
RUN apt-get update && apt-get install -y --no-install-recommends \
    openssh-client \
    rsync \
    && rm -rf /var/lib/apt/lists/*

# Copy virtual environment from builder stage
# Only the compiled packages, not build tools
COPY --from=builder /venv /venv

# Copy application source code
COPY src/ src/

# Set up Python environment variables
# CRITICAL: PYTHONUNBUFFERED=1 required for streaming output
ENV PYTHONPATH="/app:$PYTHONPATH"
ENV PYTHONUNBUFFERED=1
ENV PATH="/venv/bin:$PATH"

# Create non-root user for security
# Pattern from: Docker security best practices
RUN groupadd -r vibesbox && useradd -r -g vibesbox vibesbox

# Set ownership of application directory
RUN chown -R vibesbox:vibesbox /app

# Switch to non-root user
USER vibesbox

# Expose MCP server port
EXPOSE 8000

# Health check for Docker monitoring
# Calls the health MCP tool via JSON-RPC
HEALTHCHECK --interval=30s --timeout=10s --retries=3 --start-period=10s \
    CMD python -c "import urllib.request, json; req = urllib.request.Request('http://localhost:8000/mcp', data=json.dumps({'jsonrpc': '2.0', 'method': 'tools/call', 'params': {'name': 'health', 'arguments': {}}, 'id': 1}).encode(), headers={'Content-Type': 'application/json'}); urllib.request.urlopen(req)"

# Run MCP server
CMD ["python", "src/mcp_server.py"]
