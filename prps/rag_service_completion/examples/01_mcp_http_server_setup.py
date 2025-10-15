# Source: infra/vibesbox/src/mcp_server.py
# Lines: 38-48 (server initialization), 296-314 (main entry point)
# Pattern: FastMCP HTTP server with Streamable transport
# Extracted: 2025-10-14
# Relevance: 10/10 - Exact pattern needed for Task 2 (MCP Server Migration)

"""
WHAT THIS DEMONSTRATES:
- FastMCP server initialization with HTTP transport
- Port and host configuration
- Streamable HTTP transport setup
- Main entry point with proper error handling
"""

import logging
from mcp.server.fastmcp import FastMCP

logger = logging.getLogger(__name__)

# ==============================================================================
# PATTERN 1: FastMCP Server Initialization with HTTP Transport
# ==============================================================================

# Initialize FastMCP server with HTTP configuration
# CRITICAL: Specify host and port for HTTP transport
mcp = FastMCP(
    "Vibesbox Command Executor",  # Server name (shown in MCP client)
    host="0.0.0.0",  # Listen on all interfaces (required for Docker)
    port=8000  # HTTP port for MCP server
)

# For RAG Service, use port 8002 to avoid conflicts:
# - Task Manager: 8000
# - RAG API: 8001
# - RAG MCP: 8002 (RECOMMENDED)

# ==============================================================================
# PATTERN 2: Main Entry Point with Streamable HTTP Transport
# ==============================================================================

# Main entry point
if __name__ == "__main__":
    # Log startup information
    logger.info("Starting Vibesbox MCP server...")
    logger.info(f"   Mode: Streamable HTTP")
    logger.info(f"   URL: http://0.0.0.0:8000/mcp")

    try:
        # CRITICAL: Use transport="streamable-http" for HTTP mode
        # This is different from transport="stdio" used for local Python scripts
        mcp.run(transport="streamable-http")

    except KeyboardInterrupt:
        logger.info("Vibesbox MCP server stopped by user")

    except Exception as e:
        logger.error(f"Fatal error in MCP server: {e}", exc_info=True)
        raise

    finally:
        # Cleanup on shutdown (if needed)
        logger.info("Vibesbox MCP server shutdown complete")


# ==============================================================================
# KEY DIFFERENCES: STDIO vs HTTP Transport
# ==============================================================================

# STDIO Transport (old RAG service approach):
# - Used for local Python script invocation
# - Claude Desktop starts Python process per request
# - Communication via stdin/stdout
# - No persistent service
# Example:
#   mcp.run(transport="stdio")

# HTTP Transport (new approach for RAG service):
# - Runs as persistent HTTP service
# - Claude Desktop connects via HTTP
# - Better for Docker containerization
# - Allows concurrent requests
# Example:
#   mcp.run(transport="streamable-http")


# ==============================================================================
# DOCKER COMPOSE INTEGRATION
# ==============================================================================

# Add MCP service to docker-compose.yml:
"""
  mcp-server:
    build:
      context: ./backend
      dockerfile: Dockerfile.mcp
    container_name: rag-mcp
    ports:
      - "8002:8002"  # MCP HTTP port
    environment:
      # Same environment as API service
      DATABASE_URL: postgresql://...
      QDRANT_URL: http://qdrant:6333
      OPENAI_API_KEY: ${OPENAI_API_KEY}
      MCP_PORT: 8002
      MCP_HOST: 0.0.0.0
    networks:
      - rag-network
    depends_on:
      postgres:
        condition: service_healthy
      qdrant:
        condition: service_healthy
    restart: unless-stopped
"""

# ==============================================================================
# CLAUDE DESKTOP CONFIGURATION
# ==============================================================================

# Update ~/.claude/claude_desktop_config.json:
"""
{
  "mcpServers": {
    "rag-service": {
      "url": "http://localhost:8002/mcp",
      "transport": "streamable-http"
    }
  }
}
"""

# After configuration:
# 1. Restart Claude Desktop
# 2. Check logs for MCP connection
# 3. Test tools: search_knowledge_base, manage_document, rag_manage_source
