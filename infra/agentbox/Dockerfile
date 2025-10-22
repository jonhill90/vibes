# AgentBox - Alpine-based MCP server
# Pattern: infra/vibesbox with Alpine base

FROM python:3.11-alpine

WORKDIR /app

# ==============================================================================
# PACKAGE LIST - Add packages here for easy extension
# ==============================================================================
ARG CORE_PACKAGES="\
    bash \
    git \
    curl \
    wget \
    jq \
    vim \
    openssh-client \
    rsync \
    "

# Add additional tools as needed (uncomment or add more)
ARG EXTRA_PACKAGES="\
    tree \
    htop \
    ncdu \
    "

# Docker CLI support
ARG DOCKER_PACKAGES="\
    docker-cli \
    "

# ==============================================================================
# INSTALL PACKAGES
# ==============================================================================
RUN apk add --no-cache \
    ${CORE_PACKAGES} \
    ${EXTRA_PACKAGES} \
    ${DOCKER_PACKAGES}

# Install Python dependencies
COPY pyproject.toml ./
RUN pip install --no-cache-dir -e .

# Copy application source
COPY src/ src/

# Create non-root user (disabled for Docker socket access)
# RUN addgroup -S agentbox && adduser -S agentbox -G agentbox && \
#     chown -R agentbox:agentbox /app

# USER agentbox

# CRITICAL: Unbuffered output for streaming
ENV PYTHONUNBUFFERED=1
ENV PYTHONPATH=/app

EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=10s --retries=3 --start-period=10s \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/health')" || exit 1

CMD ["python", "src/mcp_server.py"]
