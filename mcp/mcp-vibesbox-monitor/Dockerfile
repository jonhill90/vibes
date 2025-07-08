# Multi-stage build
FROM node:18-alpine AS frontend-build

WORKDIR /app/web
COPY web/package*.json ./
RUN npm install
COPY web/ ./

# Download noVNC library locally during build
RUN mkdir -p public/novnc
RUN wget -O public/novnc/rfb.js https://unpkg.com/@novnc/novnc@1.4.0/core/rfb.js

RUN npm run build

# Production stage
FROM python:3.11-slim

# Install dependencies
RUN apt-get update && apt-get install -y \
    curl wget nginx python3-websockify \
    && rm -rf /var/lib/apt/lists/*

# Copy frontend build
COPY --from=frontend-build /app/web/build /var/www/html

# Remove default nginx site
RUN rm /etc/nginx/sites-enabled/default

# Create nginx configuration
RUN echo 'server {\n\
    listen 8000;\n\
    server_name localhost;\n\
    \n\
    location / {\n\
        root /var/www/html;\n\
        try_files $uri $uri/ /index.html;\n\
    }\n\
    \n\
    location /api/ {\n\
        proxy_pass http://localhost:8001/api/;\n\
        proxy_set_header Host $host;\n\
        proxy_set_header X-Real-IP $remote_addr;\n\
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;\n\
    }\n\
    \n\
    location /ws {\n\
        proxy_pass http://localhost:8001/ws;\n\
        proxy_http_version 1.1;\n\
        proxy_set_header Upgrade $http_upgrade;\n\
        proxy_set_header Connection "upgrade";\n\
        proxy_set_header Host $host;\n\
        proxy_set_header X-Real-IP $remote_addr;\n\
    }\n\
    \n\
    location /vnc/ {\n\
        proxy_pass http://localhost:6080/;\n\
        proxy_http_version 1.1;\n\
        proxy_set_header Upgrade $http_upgrade;\n\
        proxy_set_header Connection "upgrade";\n\
        proxy_set_header Host $host;\n\
        proxy_set_header X-Real-IP $remote_addr;\n\
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;\n\
        proxy_read_timeout 86400;\n\
        proxy_send_timeout 86400;\n\
    }\n\
}' > /etc/nginx/sites-available/vibesbox-monitor

RUN ln -s /etc/nginx/sites-available/vibesbox-monitor /etc/nginx/sites-enabled/

WORKDIR /app

# Copy requirements and install Python packages
COPY api/requirements.txt ./
RUN pip install -r requirements.txt

# Copy API code
COPY api/ ./

# Create data directory
RUN mkdir -p /app/data

# Create startup script
RUN echo '#!/bin/bash' > /app/start.sh && \
    echo '# Start nginx' >> /app/start.sh && \
    echo 'nginx' >> /app/start.sh && \
    echo '' >> /app/start.sh && \
    echo '# Start websockify to bridge VNC to WebSocket' >> /app/start.sh && \
    echo 'websockify 6080 mcp-vibesbox-server:5901 &' >> /app/start.sh && \
    echo '' >> /app/start.sh && \
    echo '# Start FastAPI on port 8001 (internal)' >> /app/start.sh && \
    echo 'exec python -c "' >> /app/start.sh && \
    echo 'import uvicorn' >> /app/start.sh && \
    echo 'from app import app' >> /app/start.sh && \
    echo '' >> /app/start.sh && \
    echo 'if __name__ == \"__main__\":' >> /app/start.sh && \
    echo '    uvicorn.run(app, host=\"0.0.0.0\", port=8001)' >> /app/start.sh && \
    echo '"' >> /app/start.sh

RUN chmod +x /app/start.sh

# Expose port
EXPOSE 8000

# Start the application
CMD ["/app/start.sh"]
