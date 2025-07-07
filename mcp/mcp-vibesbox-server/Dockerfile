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

# Install VNC and desktop environment (for future vibesbox containers)
RUN apt-get update && apt-get install -y \
    tigervnc-standalone-server tigervnc-viewer \
    xfce4 xfce4-goodies \
    dbus-x11 \
    && rm -rf /var/lib/apt/lists/*

# Install Python MCP and VNC dependencies
RUN pip3 install mcp pillow

WORKDIR /workspace/vibes
COPY server.py /workspace/

# TODO: Add VNC startup scripts and configuration
