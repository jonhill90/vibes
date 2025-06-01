# Multi-stage build for Terraform MCP Server
FROM golang:1.24.3-alpine AS builder

# Set the working directory
WORKDIR /build

# Clone the Terraform MCP server source code
RUN apk add --no-cache git && \
    git clone https://github.com/hashicorp/terraform-mcp-server.git .

# Set Go module cache
RUN go env -w GOMODCACHE=/root/.cache/go-build

# Install dependencies
RUN --mount=type=cache,target=/root/.cache/go-build go mod download

# Build the server
RUN --mount=type=cache,target=/root/.cache/go-build \
    CGO_ENABLED=0 GOOS=linux GOARCH=arm64 \
    go build -ldflags="-s -w" \
    -o terraform-mcp-server ./cmd/terraform-mcp-server

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
COPY --from=builder /build/terraform-mcp-server .

# Make the binary executable
RUN chmod +x terraform-mcp-server

# Set environment variables
ENV MCP_SERVER_NAME="terraform-mcp-server"
ENV LOG_LEVEL="info"

# Create a simple startup script
RUN echo '#!/bin/bash' > /server/start.sh && \
    echo 'echo "Terraform MCP Server ready"' >> /server/start.sh && \
    echo 'echo "Server binary available at: /server/terraform-mcp-server"' >> /server/start.sh && \
    echo 'tail -f /dev/null' >> /server/start.sh && \
    chmod +x /server/start.sh

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD test -f /server/terraform-mcp-server || exit 1

ENTRYPOINT ["/server/start.sh"]
