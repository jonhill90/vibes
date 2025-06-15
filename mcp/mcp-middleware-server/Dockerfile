FROM python:3.10-slim

WORKDIR /app

# Copy requirements and install dependencies
COPY requirements.txt .
RUN pip install -r requirements.txt

# Copy server files
COPY mcp_remote_server.py .
COPY mcps/ mcps/

# Create directory for MCP registry
RUN mkdir -p /app/data

# Set environment variables
ENV PYTHONPATH=/app
ENV MCP_DISCOVERY_DIR=/app/mcps
ENV REGISTRY_FILE=/app/data/mcp_registry.json

EXPOSE 5000

# Run the fixed remote server
CMD ["python", "/app/mcp_remote_server.py"]
