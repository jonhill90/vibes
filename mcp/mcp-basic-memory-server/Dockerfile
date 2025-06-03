FROM python:3.12-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \
    git \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install uv for fast Python package management
RUN pip install uv

# Clone the basic-memory repository
RUN git clone https://github.com/basicmachines-co/basic-memory.git /app

WORKDIR /app

# Install only the core dependencies needed for MCP server (skip GUI extras)
RUN uv sync --group=server --no-dev || uv sync --no-dev || \
    (echo "Trying minimal install..." && \
     uv venv && \
     . .venv/bin/activate && \
     pip install -e . --no-deps && \
     pip install fastmcp mcp loguru typer python-dotenv pydantic sqlalchemy aiosqlite watchfiles)

# Create data directory for markdown files
RUN mkdir -p /data/basic-memory

# Expose MCP port
EXPOSE 8000

# Create startup script
COPY start.sh /app/start.sh
RUN chmod +x /app/start.sh

CMD ["/app/start.sh"]
