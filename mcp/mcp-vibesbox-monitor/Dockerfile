# Multi-stage build for React frontend + FastAPI backend

# Stage 1: Build React frontend
FROM node:18-alpine AS frontend-build
WORKDIR /app/web
COPY web/package*.json ./
RUN npm install
COPY web/ ./
RUN npm run build

# Stage 2: Python backend + serve frontend
FROM python:3.11-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \
    curl wget nginx \
    && rm -rf /var/lib/apt/lists/*

# Setup nginx to serve React app and proxy API
COPY --from=frontend-build /app/web/build /var/www/html
RUN rm /etc/nginx/sites-enabled/default

# Create nginx config
RUN echo 'server {\n\
    listen 8000;\n\
    server_name localhost;\n\
    \n\
    # Serve React app\n\
    location / {\n\
        root /var/www/html;\n\
        try_files $uri $uri/ /index.html;\n\
    }\n\
    \n\
    # Proxy API requests to FastAPI\n\
    location /api/ {\n\
        proxy_pass http://localhost:8001/api/;\n\
        proxy_set_header Host $host;\n\
        proxy_set_header X-Real-IP $remote_addr;\n\
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;\n\
    }\n\
    \n\
    # WebSocket support\n\
    location /ws {\n\
        proxy_pass http://localhost:8001/ws;\n\
        proxy_http_version 1.1;\n\
        proxy_set_header Upgrade $http_upgrade;\n\
        proxy_set_header Connection "upgrade";\n\
        proxy_set_header Host $host;\n\
        proxy_set_header X-Real-IP $remote_addr;\n\
    }\n\
}' > /etc/nginx/sites-available/vibesbox-monitor

RUN ln -s /etc/nginx/sites-available/vibesbox-monitor /etc/nginx/sites-enabled/

# Install Python dependencies
WORKDIR /app
COPY api/requirements.txt ./
RUN pip install -r requirements.txt

# Copy backend code
COPY api/ ./

# Create data directory
RUN mkdir -p /app/data

# Create startup script
RUN echo '#!/bin/bash\n\
# Start nginx\n\
nginx\n\
\n\
# Start FastAPI on port 8001 (internal)\n\
exec python -c "\n\
import uvicorn\n\
from app import app\n\
\n\
if __name__ == '\''__main__'\'':\n\
    uvicorn.run(app, host='\''0.0.0.0'\'', port=8001)\n\
"' > /app/start.sh

RUN chmod +x /app/start.sh

EXPOSE 8000

# Start both services
CMD ["/app/start.sh"]
