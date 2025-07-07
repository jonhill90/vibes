# Multi-stage build for Context7 MCP Server
FROM node:20-alpine AS builder

# Set the working directory
WORKDIR /build

# Clone the Context7 MCP server source code
RUN apk add --no-cache git && \
    git clone https://github.com/upstash/context7.git .

# Install dependencies
RUN npm install

# Build the server
RUN npm run build

# Runtime image
FROM node:20-alpine AS runtime

# Install required packages
RUN apk add --no-cache \
    ca-certificates \
    curl \
    git \
    bash \
    && rm -rf /var/cache/apk/*

# Set the working directory
WORKDIR /server

# Copy the built application from the builder stage
COPY --from=builder /build/dist ./dist
COPY --from=builder /build/node_modules ./node_modules
COPY --from=builder /build/package.json ./

# Make the binary executable
RUN chmod +x dist/index.js

# Set environment variables
ENV MCP_SERVER_NAME="mcp-context7-server"
ENV NODE_ENV="production"

# Create a simple startup script
RUN echo '#!/bin/bash' > /server/start.sh && \
    echo 'echo "Context7 MCP Server ready"' >> /server/start.sh && \
    echo 'echo "Server binary available at: /server/dist/index.js"' >> /server/start.sh && \
    echo 'echo "Use: node /server/dist/index.js [--transport stdio|http|sse] [--port 3000]"' >> /server/start.sh && \
    echo 'tail -f /dev/null' >> /server/start.sh && \
    chmod +x /server/start.sh

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD test -f /server/dist/index.js || exit 1

ENTRYPOINT ["/server/start.sh"]
