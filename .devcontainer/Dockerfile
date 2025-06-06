# Minimal version for testing - just core tools
FROM mcr.microsoft.com/devcontainers/base:ubuntu

ENV DEBIAN_FRONTEND=noninteractive

# Install basic tools
RUN apt-get update \
  && apt-get install -y \
    curl wget git python3 python3-pip python3-venv pipx jq vim nano \
    lsb-release gnupg ca-certificates apt-transport-https \
    build-essential \
  && rm -rf /var/lib/apt/lists/*

# Install Docker CLI
RUN curl -fsSL https://download.docker.com/linux/ubuntu/gpg | gpg --dearmor -o /usr/share/keyrings/docker-archive-keyring.gpg \
  && echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/docker-archive-keyring.gpg] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable" | tee /etc/apt/sources.list.d/docker.list > /dev/null \
  && apt-get update && apt-get install -y docker-ce-cli docker-compose-plugin \
  && rm -rf /var/lib/apt/lists/*

# Install Node.js & npm
RUN curl -fsSL https://deb.nodesource.com/setup_20.x | bash - \
  && apt-get install -y nodejs \
  && rm -rf /var/lib/apt/lists/*

# Install Azure CLI
RUN curl -sL https://packages.microsoft.com/keys/microsoft.asc | gpg --dearmor > /usr/share/keyrings/azurecli-archive-keyring.gpg \
  && echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/azurecli-archive-keyring.gpg] https://packages.microsoft.com/repos/azure-cli/ $(lsb_release -cs) main" > /etc/apt/sources.list.d/azure-cli.list \
  && apt-get update && apt-get install -y azure-cli \
  && rm -rf /var/lib/apt/lists/*

# Install Python packages (using --break-system-packages for container environment)
RUN pip3 install --no-cache-dir --break-system-packages mcp

# Install Node.js packages
RUN npm install -g @anthropic-ai/claude-code @openai/codex \
  && ln -sf "$(npm config get prefix)/bin/claude-code" /usr/local/bin/claude

# Copy essential scripts
COPY .devcontainer/scripts/postCreate.sh /usr/local/share/postCreate.sh
COPY .devcontainer/scripts/test-docker.sh /usr/local/share/test-docker.sh
RUN chmod +x /usr/local/share/*.sh

# Set up working directory
WORKDIR /workspace/vibes

# Create docker group and add vscode user
RUN groupadd -g 999 docker || true \
  && usermod -aG docker vscode || true
