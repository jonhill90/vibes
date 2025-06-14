# Browserless MCP Server

A containerized browserless service for the Agent-0 project, providing browser automation and screenshot capabilities via HTTP API.

## Overview

This MCP server provides headless Chrome browser functionality using the Browserless service. It's designed to give Agent-0 "eyes" by enabling screenshot capture and browser automation through a simple HTTP API.

## Quick Start

```bash
# Start the service
docker compose up -d

# Check status
docker compose ps

# View logs
docker compose logs -f

# Stop the service
docker compose down
```

## Service Details

- **Container Name**: `browserless-mcp-server`
- **Internal Port**: 3000
- **External Port**: 9333
- **Network**: `vibes-network`

## API Endpoints

### Health Check
```bash
curl http://localhost:9333/pressure
```

### Screenshot API
```bash
curl -X POST \
  http://localhost:9333/screenshot \
  -H 'Content-Type: application/json' \
  -d '{
    "url": "https://example.com",
    "options": {
      "fullPage": true,
      "type": "png"
    }
  }' \
  --output screenshot.png
```

### From Within Docker Network
```bash
# Access from other containers
curl http://browserless-mcp-server:3000/pressure

# Screenshot from container
curl -X POST \
  http://browserless-mcp-server:3000/screenshot \
  -H 'Content-Type: application/json' \
  -d '{
    "url": "http://host.docker.internal:8082",
    "options": {
      "fullPage": false,
      "type": "png"
    }
  }' \
  --output screenshot.png
```

## Configuration

Environment variables can be set in `.env` file:

```bash
# Browserless Configuration
BROWSERLESS_TOKEN=           # Optional API token
MAX_CONCURRENT_SESSIONS=10   # Max parallel browser sessions
MAX_QUEUE_LENGTH=10          # Max queued requests
CONNECTION_TIMEOUT=30000     # Connection timeout in ms
ENABLE_API_GET=true          # Enable GET request endpoints
ENABLE_HEAP_DUMP=false       # Enable heap dump endpoint
ENABLE_DEBUG_VIEWER=false    # Enable debug viewer
KEEP_ALIVE=true              # Keep connections alive
CHROME_REFRESH_TIME=30000    # Chrome refresh interval
```

## Integration with Agent-0

The browserless MCP server is designed to work seamlessly with Agent-0's screenshot tools:

```bash
# From Agent-0 tools directory
./take-screenshot.sh http://host.docker.internal:8082
```

The screenshot tools automatically use `host.docker.internal:9333` to access the containerized browserless service.

## Resource Requirements

- **RAM**: 2GB shared memory (configured in docker-compose.yml)
- **CPU**: Moderate (depends on concurrent sessions)
- **Storage**: Minimal (browser cache and temporary files)

## Troubleshooting

### Container won't start
```bash
# Check logs
docker compose logs browserless-mcp-server

# Verify network exists
docker network ls | grep vibes
```

### Can't access from host
```bash
# Test from inside container
docker exec browserless-mcp-server curl http://localhost:3000/pressure

# Test from host (use host.docker.internal)
curl http://host.docker.internal:9333/pressure
```

### Health check failing
```bash
# Check if curl is available in container
docker exec browserless-mcp-server which curl

# Manual health check
docker exec browserless-mcp-server curl -f http://localhost:3000/pressure
```

## Comparison with Other MCP Servers

This follows the same pattern as other MCP servers in the vibes project:

- **mcp-azure-server**: Azure cloud management
- **mcp-terraform-server**: Infrastructure as code
- **mcp-vibes-server**: Shell command execution
- **mcp-browserless-server**: Browser automation (this service)

All use the same `vibes-network` and docker-compose structure for consistency.

## Future Enhancements

- [ ] Integration with MCP Middleware for dynamic loading
- [ ] Browser automation tools beyond screenshots
- [ ] Support for multiple browser engines (Firefox, Safari)
- [ ] Performance monitoring and metrics
- [ ] Custom browser profiles and extensions

## Related Files

- `/workspace/vibes/projects/agent-0/tools/take-screenshot.sh` - Screenshot utility
- `/workspace/vibes/projects/agent-0/tools/view.sh` - Wrapper script
- `/workspace/vibes/projects/agent-0/PROJECT_DETAILS.md` - Agent-0 context
