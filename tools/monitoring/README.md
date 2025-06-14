# Monitoring Tools

Tools for checking service status, health monitoring, and system inspection.

## Available Tools

### `check-services.sh`
Comprehensive service availability checker for the vibes environment.

**Usage:**
```bash
./check-services.sh
```

**Features:**
- Lists all running Docker containers with ports and status
- Tests accessibility of common service ports (3000, 3333, 8082, 8765)
- Shows container health status
- Easy-to-read tabular output

**Sample Output:**
```
🔍 Checking available services...

Docker containers running:
NAMES                    PORTS                              STATUS
browserless-mcp-server   3000/tcp, 0.0.0.0:9333->9333/tcp   Up 43 minutes
concept-app-container    0.0.0.0:8082->80/tcp               Up 2 hours

Testing service availability:
✓ Port 3000 is accessible
✗ Port 3333 is not accessible
✓ Port 8082 is accessible
```

## Dependencies

- **Docker** for container inspection
- **curl** for port testing
- **Network access** to test service endpoints

## Future Tools

Potential additions to this category:
- Resource usage monitoring (CPU, memory, disk)
- Log aggregation and analysis
- Performance benchmarking
- Health check endpoints
- Alert and notification tools
- Database connection testing
- API endpoint validation
- Network latency testing
