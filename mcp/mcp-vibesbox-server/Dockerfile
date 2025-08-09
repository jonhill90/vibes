FROM ubuntu:22.04

ENV DEBIAN_FRONTEND=noninteractive

# Install base system packages
RUN apt-get update && apt-get install -y \
    curl wget git python3 python3-pip jq vim nano \
    lsb-release gnupg ca-certificates \
    systemd systemd-sysv \
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
    fonts-noto-color-emoji \
    && rm -rf /var/lib/apt/lists/*

# ===== SCREENSAVER DISABLING CONFIGURATION =====

# Disable screensaver autostart services
RUN rm -f /etc/xdg/autostart/xfce4-screensaver.desktop \
    && rm -f /etc/xdg/autostart/xscreensaver.desktop

# Create XFCE configuration directory
RUN mkdir -p /etc/xdg/xfce4/xfconf/xfce-perchannel-xml

# Create XFCE power manager configuration (no timeouts)
RUN echo '<?xml version="1.0" encoding="UTF-8"?>' > /etc/xdg/xfce4/xfconf/xfce-perchannel-xml/xfce4-power-manager.xml && \
    echo '<channel name="xfce4-power-manager" version="1.0">' >> /etc/xdg/xfce4/xfconf/xfce-perchannel-xml/xfce4-power-manager.xml && \
    echo '  <property name="xfce4-power-manager" type="empty">' >> /etc/xdg/xfce4/xfconf/xfce-perchannel-xml/xfce4-power-manager.xml && \
    echo '    <property name="power-button-action" type="uint" value="3"/>' >> /etc/xdg/xfce4/xfconf/xfce-perchannel-xml/xfce4-power-manager.xml && \
    echo '    <property name="show-tray-icon" type="bool" value="false"/>' >> /etc/xdg/xfce4/xfconf/xfce-perchannel-xml/xfce4-power-manager.xml && \
    echo '    <property name="dpms-enabled" type="bool" value="false"/>' >> /etc/xdg/xfce4/xfconf/xfce-perchannel-xml/xfce4-power-manager.xml && \
    echo '    <property name="dpms-on-ac-sleep" type="uint" value="0"/>' >> /etc/xdg/xfce4/xfconf/xfce-perchannel-xml/xfce4-power-manager.xml && \
    echo '    <property name="dpms-on-ac-off" type="uint" value="0"/>' >> /etc/xdg/xfce4/xfconf/xfce-perchannel-xml/xfce4-power-manager.xml && \
    echo '    <property name="dpms-on-battery-sleep" type="uint" value="0"/>' >> /etc/xdg/xfce4/xfconf/xfce-perchannel-xml/xfce4-power-manager.xml && \
    echo '    <property name="dpms-on-battery-off" type="uint" value="0"/>' >> /etc/xdg/xfce4/xfconf/xfce-perchannel-xml/xfce4-power-manager.xml && \
    echo '    <property name="blank-on-ac" type="int" value="0"/>' >> /etc/xdg/xfce4/xfconf/xfce-perchannel-xml/xfce4-power-manager.xml && \
    echo '    <property name="blank-on-battery" type="int" value="0"/>' >> /etc/xdg/xfce4/xfconf/xfce-perchannel-xml/xfce4-power-manager.xml && \
    echo '  </property>' >> /etc/xdg/xfce4/xfconf/xfce-perchannel-xml/xfce4-power-manager.xml && \
    echo '</channel>' >> /etc/xdg/xfce4/xfconf/xfce-perchannel-xml/xfce4-power-manager.xml

# Create XFCE screensaver configuration (disabled)
RUN echo '<?xml version="1.0" encoding="UTF-8"?>' > /etc/xdg/xfce4/xfconf/xfce-perchannel-xml/xfce4-screensaver.xml && \
    echo '<channel name="xfce4-screensaver" version="1.0">' >> /etc/xdg/xfce4/xfconf/xfce-perchannel-xml/xfce4-screensaver.xml && \
    echo '  <property name="saver" type="empty">' >> /etc/xdg/xfce4/xfconf/xfce-perchannel-xml/xfce4-screensaver.xml && \
    echo '    <property name="enabled" type="bool" value="false"/>' >> /etc/xdg/xfce4/xfconf/xfce-perchannel-xml/xfce4-screensaver.xml && \
    echo '    <property name="idle-activation" type="empty">' >> /etc/xdg/xfce4/xfconf/xfce-perchannel-xml/xfce4-screensaver.xml && \
    echo '      <property name="enabled" type="bool" value="false"/>' >> /etc/xdg/xfce4/xfconf/xfce-perchannel-xml/xfce4-screensaver.xml && \
    echo '      <property name="delay" type="int" value="0"/>' >> /etc/xdg/xfce4/xfconf/xfce-perchannel-xml/xfce4-screensaver.xml && \
    echo '    </property>' >> /etc/xdg/xfce4/xfconf/xfce-perchannel-xml/xfce4-screensaver.xml && \
    echo '  </property>' >> /etc/xdg/xfce4/xfconf/xfce-perchannel-xml/xfce4-screensaver.xml && \
    echo '  <property name="lock" type="empty">' >> /etc/xdg/xfce4/xfconf/xfce-perchannel-xml/xfce4-screensaver.xml && \
    echo '    <property name="enabled" type="bool" value="false"/>' >> /etc/xdg/xfce4/xfconf/xfce-perchannel-xml/xfce4-screensaver.xml && \
    echo '    <property name="saver-activation" type="empty">' >> /etc/xdg/xfce4/xfconf/xfce-perchannel-xml/xfce4-screensaver.xml && \
    echo '      <property name="enabled" type="bool" value="false"/>' >> /etc/xdg/xfce4/xfconf/xfce-perchannel-xml/xfce4-screensaver.xml && \
    echo '      <property name="delay" type="int" value="0"/>' >> /etc/xdg/xfce4/xfconf/xfce-perchannel-xml/xfce4-screensaver.xml && \
    echo '    </property>' >> /etc/xdg/xfce4/xfconf/xfce-perchannel-xml/xfce4-screensaver.xml && \
    echo '  </property>' >> /etc/xdg/xfce4/xfconf/xfce-perchannel-xml/xfce4-screensaver.xml && \
    echo '</channel>' >> /etc/xdg/xfce4/xfconf/xfce-perchannel-xml/xfce4-screensaver.xml

# Create VNC startup script with screensaver disabling
RUN echo '#!/bin/bash' > /usr/local/bin/start-vnc-no-screensaver.sh && \
    echo 'set -e' >> /usr/local/bin/start-vnc-no-screensaver.sh && \
    echo 'echo "Starting VNC with screensaver disabled..."' >> /usr/local/bin/start-vnc-no-screensaver.sh && \
    echo 'if ! pgrep -x "dbus-daemon" > /dev/null; then' >> /usr/local/bin/start-vnc-no-screensaver.sh && \
    echo '    dbus-daemon --system --fork' >> /usr/local/bin/start-vnc-no-screensaver.sh && \
    echo 'fi' >> /usr/local/bin/start-vnc-no-screensaver.sh && \
    echo 'vncserver -kill :1 2>/dev/null || true' >> /usr/local/bin/start-vnc-no-screensaver.sh && \
    echo 'sleep 1' >> /usr/local/bin/start-vnc-no-screensaver.sh && \
    echo 'vncserver :1 -geometry 1920x1080 -depth 24 -SecurityTypes None' >> /usr/local/bin/start-vnc-no-screensaver.sh && \
    echo 'sleep 3' >> /usr/local/bin/start-vnc-no-screensaver.sh && \
    echo 'export DISPLAY=:1' >> /usr/local/bin/start-vnc-no-screensaver.sh && \
    echo 'xset s off' >> /usr/local/bin/start-vnc-no-screensaver.sh && \
    echo 'xset -dpms' >> /usr/local/bin/start-vnc-no-screensaver.sh && \
    echo 'xset s noblank' >> /usr/local/bin/start-vnc-no-screensaver.sh && \
    echo 'pkill -f "xfce4-screensaver" 2>/dev/null || true' >> /usr/local/bin/start-vnc-no-screensaver.sh && \
    echo 'pkill -f "xscreensaver" 2>/dev/null || true' >> /usr/local/bin/start-vnc-no-screensaver.sh && \
    echo 'echo "VNC server started with screensaver disabled"' >> /usr/local/bin/start-vnc-no-screensaver.sh && \
    echo 'echo "Current screensaver status:"' >> /usr/local/bin/start-vnc-no-screensaver.sh && \
    echo 'xset q | grep -A 3 "Screen Saver"' >> /usr/local/bin/start-vnc-no-screensaver.sh

# Create systemd service for VNC with screensaver disabled
RUN echo '[Unit]' > /etc/systemd/system/vnc-no-screensaver.service && \
    echo 'Description=VNC Server with Screensaver Disabled' >> /etc/systemd/system/vnc-no-screensaver.service && \
    echo 'After=multi-user.target' >> /etc/systemd/system/vnc-no-screensaver.service && \
    echo '' >> /etc/systemd/system/vnc-no-screensaver.service && \
    echo '[Service]' >> /etc/systemd/system/vnc-no-screensaver.service && \
    echo 'Type=forking' >> /etc/systemd/system/vnc-no-screensaver.service && \
    echo 'User=root' >> /etc/systemd/system/vnc-no-screensaver.service && \
    echo 'ExecStart=/usr/local/bin/start-vnc-no-screensaver.sh' >> /etc/systemd/system/vnc-no-screensaver.service && \
    echo 'ExecStop=/usr/bin/vncserver -kill :1' >> /etc/systemd/system/vnc-no-screensaver.service && \
    echo 'Restart=always' >> /etc/systemd/system/vnc-no-screensaver.service && \
    echo 'RestartSec=10' >> /etc/systemd/system/vnc-no-screensaver.service && \
    echo '' >> /etc/systemd/system/vnc-no-screensaver.service && \
    echo '[Install]' >> /etc/systemd/system/vnc-no-screensaver.service && \
    echo 'WantedBy=multi-user.target' >> /etc/systemd/system/vnc-no-screensaver.service

# Make VNC startup script executable and enable service
RUN chmod +x /usr/local/bin/start-vnc-no-screensaver.sh \
    && systemctl enable vnc-no-screensaver.service

# ===== END SCREENSAVER CONFIGURATION =====

# Install Playwright and ARM64 Chromium (replaces problematic chromium-browser)
WORKDIR /workspace
RUN npm install playwright \
    && npx playwright install chromium \
    && find /root/.cache/ms-playwright -name "chrome" -type f -exec ln -sf {} /usr/bin/google-chrome \; \
    && chmod +x /usr/bin/google-chrome

# Install Python MCP and VNC dependencies
RUN pip3 install mcp pillow

WORKDIR /workspace/vibes
# Enhanced with comprehensive screensaver disabling - $(date)
COPY server.py /workspace/

# Use systemd init (works with docker-compose.yml)
CMD ["/sbin/init"]
