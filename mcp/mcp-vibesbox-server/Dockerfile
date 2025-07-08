FROM ubuntu:22.04

ENV DEBIAN_FRONTEND=noninteractive

# Install base system packages
RUN apt-get update && apt-get install -y \
    curl wget git python3 python3-pip jq vim nano \
    lsb-release gnupg ca-certificates \
    && rm -rf /var/lib/apt/lists/*

# Install Docker CLI
RUN curl -fsSL https://download.docker.com/linux/ubuntu/gpg | gpg --dearmor -o /usr/share/keyrings/docker-archive-keyring.gpg \
    && echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/docker-archive-keyring.gpg] https://download.docker.com/linux/ubuntu jammy stable" | tee /etc/apt/sources.list.d/docker.list > /dev/null \
    && apt-get update && apt-get install -y docker-ce-cli \
    && rm -rf /var/lib/apt/lists/*

# Install Node.js 22.x (required for Playwright ARM64 Chromium)
RUN curl -fsSL https://deb.nodesource.com/setup_22.x | bash - \
    && apt-get install -y nodejs \
    && rm -rf /var/lib/apt/lists/*

# Install VNC, desktop environment, and GUI automation tools
RUN apt-get update && apt-get install -y \
    tigervnc-standalone-server tigervnc-viewer \
    xfce4 xfce4-goodies \
    dbus-x11 \
    imagemagick \
    xdotool \
    && rm -rf /var/lib/apt/lists/*

# Install Playwright and ARM64 Chromium (replaces problematic chromium-browser)
WORKDIR /workspace
RUN npm install playwright \
    && npx playwright install chromium \
    && find /root/.cache/ms-playwright -name "chrome" -type f -exec ln -sf {} /usr/bin/google-chrome \; \
    && chmod +x /usr/bin/google-chrome

# Install Python MCP and VNC dependencies
RUN pip3 install mcp pillow

WORKDIR /workspace/vibes
# Enhanced drag_mouse with timing delays - $(date)
COPY server.py /workspace/

# TODO: Add VNC startup scripts and configuration
