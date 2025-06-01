FROM ubuntu:22.04

ENV DEBIAN_FRONTEND=noninteractive

# Install basic tools including lsb-release
RUN apt-get update && apt-get install -y \
    curl \
    wget \
    git \
    python3 \
    python3-pip \
    jq \
    vim \
    nano \
    lsb-release \
    gnupg \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/*

# Install Docker CLI
RUN curl -fsSL https://download.docker.com/linux/ubuntu/gpg | gpg --dearmor -o /usr/share/keyrings/docker-archive-keyring.gpg \
    && echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/docker-archive-keyring.gpg] https://download.docker.com/linux/ubuntu jammy stable" | tee /etc/apt/sources.list.d/docker.list > /dev/null \
    && apt-get update \
    && apt-get install -y docker-ce-cli \
    && rm -rf /var/lib/apt/lists/*

# Install MCP SDK
RUN pip3 install mcp

# Create workspace
RUN mkdir -p /workspace
WORKDIR /workspace

# Copy the simple server
COPY server.py /workspace/server.py

# Default command starts the MCP server
CMD ["python3", "/workspace/server.py"]
