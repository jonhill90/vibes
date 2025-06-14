# Use the same image that's currently working
FROM browserless/chrome:latest

# Switch to root to make changes
USER root

# Install curl for health checks (might already be installed)
RUN apt-get update && apt-get install -y curl || true \
    && rm -rf /var/lib/apt/lists/* || true

# Configure for MCP usage  
ENV MCP_SERVER_NAME="browserless-mcp-server"

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
  CMD curl -f http://localhost:3000/pressure || exit 1

# Switch back to original user if needed
USER blessuser

# Use the original entrypoint
