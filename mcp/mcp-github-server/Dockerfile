# Multi-stage build for GitHub MCP Server
FROM golang:1.24.3-alpine AS builder

# Set the working directory
WORKDIR /build

# Clone the GitHub MCP server source code
RUN apk add --no-cache git && \
    git clone https://github.com/github/github-mcp-server.git .

# Set Go module cache
RUN go env -w GOMODCACHE=/root/.cache/go-build

# Install dependencies
RUN --mount=type=cache,target=/root/.cache/go-build go mod download

# Build the server
RUN --mount=type=cache,target=/root/.cache/go-build \
    CGO_ENABLED=0 GOOS=linux GOARCH=arm64 \
    go build -ldflags="-s -w" \
    -o github-mcp-server cmd/github-mcp-server/main.go

# Runtime image
FROM alpine:3.21 AS runtime

# Install required packages
RUN apk add --no-cache \
    ca-certificates \
    curl \
    git \
    bash \
    && rm -rf /var/cache/apk/*

# Set the working directory
WORKDIR /server

# Copy the binary from the builder stage
COPY --from=builder /build/github-mcp-server .

# Make the binary executable
RUN chmod +x github-mcp-server

# Set environment variables
ENV MCP_SERVER_NAME="github-mcp-server"
ENV LOG_LEVEL="info"

# Create a simple startup script
RUN echo '#!/bin/bash' > /server/start.sh && \
    echo 'echo "GitHub MCP Server ready"' >> /server/start.sh && \
    echo 'echo "Server binary available at: /server/github-mcp-server"' >> /server/start.sh && \
    echo 'tail -f /dev/null' >> /server/start.sh && \
    chmod +x /server/start.sh

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD test -f /server/github-mcp-server || exit 1

ENTRYPOINT ["/server/start.sh"]
