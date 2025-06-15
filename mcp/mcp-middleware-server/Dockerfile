FROM python:3.10-slim

# Install docker CLI for container communication
RUN apt-get update && apt-get install -y \
    curl \
    && curl -fsSL https://get.docker.com -o get-docker.sh \
    && sh get-docker.sh \
    && rm get-docker.sh \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Install Python dependencies
COPY requirements.txt .
RUN pip install -r requirements.txt

# Copy the MCP server
COPY mcp_remote_server.py .

# Copy MCP discovery directory
COPY mcps/ mcps/

# Create data directory
RUN mkdir -p /app/data

EXPOSE 5000

CMD ["python", "/app/mcp_remote_server.py"]
