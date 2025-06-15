FROM python:3.10-slim

WORKDIR /app

# Copy requirements and install dependencies
COPY requirements.txt .
RUN pip install -r requirements.txt

# Copy server files
COPY web_server.py .
COPY server.py .
COPY server_enhanced.py .
COPY server_with_sse.py .
COPY mcps/ mcps/

# Create directory for MCP registry
RUN mkdir -p /app/data

# Set environment variables
ENV PYTHONPATH=/app
ENV MCP_DISCOVERY_DIR=/app/mcps
ENV REGISTRY_FILE=/app/data/mcp_registry.json

EXPOSE 5000

# Run the web server for persistent SSE service
CMD ["python", "/app/web_server.py"]
