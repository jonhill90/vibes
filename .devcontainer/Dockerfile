# Use official Dev Container base image
FROM mcr.microsoft.com/devcontainers/base:ubuntu

ENV DEBIAN_FRONTEND=noninteractive

# Install Node.js & npm (using Node 20.x for built-in Web Crypto)
RUN apt-get update \
  && apt-get install -y curl ca-certificates gnupg lsb-release \
  && curl -fsSL https://deb.nodesource.com/setup_20.x | bash - \
  && apt-get install -y nodejs \
  && rm -rf /var/lib/apt/lists/*

# Install Azure CLI
RUN apt-get update \
  && apt-get install -y apt-transport-https ca-certificates curl gnupg lsb-release \
  && curl -sL https://packages.microsoft.com/keys/microsoft.asc \
       | gpg --dearmor \
       > /usr/share/keyrings/azurecli-archive-keyring.gpg \
  && echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/azurecli-archive-keyring.gpg] https://packages.microsoft.com/repos/azure-cli/ $(lsb_release -cs) main" \
       > /etc/apt/sources.list.d/azure-cli.list \
  && apt-get update \
  && apt-get install -y azure-cli \
  && rm -rf /var/lib/apt/lists/*

# Install PowerShell via GitHub tarball (multi-arch)
ARG PS_VER=7.4.7
ARG TARGETARCH
RUN if [ "$TARGETARCH" = "arm64" ]; then ARCH=linux-arm64; else ARCH=linux-x64; fi \
  && curl -fsSL "https://github.com/PowerShell/PowerShell/releases/download/v${PS_VER}/powershell-${PS_VER}-${ARCH}.tar.gz" \
       -o /tmp/pw.tar.gz \
  && mkdir -p /opt/microsoft/powershell/${PS_VER} \
  && tar -xzf /tmp/pw.tar.gz -C /opt/microsoft/powershell/${PS_VER} \
  && chmod -R a+rX /opt/microsoft/powershell/${PS_VER} \
  && chmod a+x /opt/microsoft/powershell/${PS_VER}/pwsh \
  && ln -s /opt/microsoft/powershell/${PS_VER}/pwsh /usr/bin/pwsh \
  && rm /tmp/pw.tar.gz

# Install Claude CLI and make “claude” point at it
RUN npm install -g @anthropic-ai/claude-code \
  && ln -sf "$(npm config get prefix)/bin/claude-code" /usr/local/bin/claude \
  && ln -sf "$(npm config get prefix)/bin/claude-code" /usr/local/bin/claude-code

# Copy the postCreate.sh script to the container
COPY .devcontainer/scripts/postCreate.sh /usr/local/share/postCreate.sh
RUN chmod +x /usr/local/share/postCreate.sh

# Install Codex CLI
RUN npm install -g @openai/codex

# Copy Codex config.json to proper location
COPY .devcontainer/scripts/codex/config.json /home/vscode/.codex/config.json