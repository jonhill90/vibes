# LiteLLM Infrastructure 🚀

This directory contains the LiteLLM infrastructure that serves as the central MCP server management layer for Vibes.

## Overview

Instead of managing individual MCP servers in Claude Desktop's JSON configuration, LiteLLM acts as a proxy and management layer that:

- **Dynamically manages** MCP servers without Claude Desktop restarts
- **Provides a web UI** for adding/removing servers
- **Monitors health** and performance of MCP servers
- **Tracks costs** and usage per server
- **Handles authentication** and permissions

## Architecture

```
Claude Desktop → LiteLLM Proxy → Individual MCP Servers
                      ↓
              LiteLLM Management UI
                      ↓
                PostgreSQL Database
```

## Quick Start

### 1. Environment Setup
```bash
# Copy and customize environment file
cp .env.example .env
# Edit .env with your specific configuration
```

### 2. Start Services
```bash
# Ensure vibes-network exists
docker network create vibes-network

# Start LiteLLM infrastructure
docker-compose up -d

# Check status
docker-compose ps
```

### 3. Access Points
- **LiteLLM API**: http://localhost:4001
- **Management UI**: http://localhost:4001 (built-in dashboard)
- **Health Check**: http://localhost:4001/health

### 4. Configure Claude Desktop
Replace your current MCP servers with a single LiteLLM connection:

```json
{
  "mcpServers": {
    "litellm-mcp-proxy": {
      "command": "npx",
      "args": ["mcp-remote", "http://localhost:4001/mcp/"]
    }
  }
}
```

## Environment Configuration

### Required Variables (.env)
```bash
# Database credentials
POSTGRES_PASSWORD=your_secure_password
LITELLM_MASTER_KEY=your_master_key
LITELLM_SALT_KEY=your_salt_key  # Generate with: openssl rand -hex 32
JWT_SECRET=your_jwt_secret      # Generate with: openssl rand -hex 64
```

### Port Configuration
- **4001**: LiteLLM Proxy API and UI
- **5434**: PostgreSQL database (external access)

These ports are chosen to avoid conflicts with existing Vibes services:
- 3000: OpenMemory UI
- 4000: Existing LiteLLM configs
- 8080: Azure MCP Server
- etc.

## Managing MCP Servers

### Through Web UI
1. Navigate to http://localhost:4001
2. Use the MCP server management interface
3. Add existing Vibes MCP servers:
   - vibes-server: `docker exec -i mcp-vibes-server python3 /workspace/server.py`
   - azure-server: `docker exec -i azure-mcp-server dotnet azmcp.dll server start`
   - github-server: `docker exec -i github-mcp-server /server/github-mcp-server stdio`

### Through API
```bash
# List servers
curl http://localhost:4001/mcp/servers

# Add server
curl -X POST http://localhost:4001/mcp/servers \
  -H "Content-Type: application/json" \
  -d '{"name": "vibes", "command": "docker", "args": ["exec", "-i", "mcp-vibes-server", "python3", "/workspace/server.py"]}'
```

## Monitoring & Troubleshooting

### Check Service Health
```bash
# All services
docker-compose ps

# LiteLLM logs
docker-compose logs -f litellm-proxy

# Database logs
docker-compose logs -f litellm-db

# Health checks
curl http://localhost:4001/health
```

### Common Issues

**Connection refused to database:**
```bash
# Check database is running
docker-compose ps litellm-db
# Check database health
docker-compose exec litellm-db pg_isready -d litellm -U litellm
```

**MCP servers not responding:**
- Check that servers are running on vibes-network
- Verify server configurations in LiteLLM UI
- Test individual server connections

## Security Notes

### Development vs Production
- Default `.env` has auth disabled for local development
- Production should enable `LITELLM_AUTH_ENABLED=True`
- Use strong passwords and rotate secrets regularly

### Network Security
- All services run on internal `vibes-network`
- Only necessary ports are exposed to host
- Database is isolated from external access

## Integration with Vibes

### Existing MCP Server Migration
1. **Keep existing servers running** (no downtime)
2. **Add servers to LiteLLM** through UI
3. **Test functionality** with new proxy
4. **Update Claude Desktop config** to use LiteLLM
5. **Remove old JSON entries** once confirmed working

### Benefits Over Direct MCP
- **Zero-downtime** server updates
- **Visual management** vs JSON editing
- **Real-time monitoring** and debugging
- **Cost tracking** and usage analytics
- **Team collaboration** on server management

## Development

### Local Development
```bash
# Enable debug mode
echo "DEBUG=True" >> .env
echo "HOT_RELOAD=True" >> .env

# Restart with debug
docker-compose down && docker-compose up -d
```

### Adding Custom Configuration
Place configuration files in `./config/` directory:
- `litellm-config.yml`: LiteLLM proxy configuration
- `mcp-servers.json`: Pre-configured MCP servers
- `permissions.yml`: Access control rules

## Backup & Recovery

### Database Backup
```bash
# Create backup
docker-compose exec litellm-db pg_dump -U litellm litellm > backup.sql

# Restore backup
docker-compose exec -T litellm-db psql -U litellm litellm < backup.sql
```

### Configuration Backup
```bash
# Export MCP server configurations
curl http://localhost:4001/api/config/export > mcp-config-backup.json
```

---

**Next Steps:**
1. Start the infrastructure with `docker-compose up -d`
2. Access the UI at http://localhost:4001
3. Begin migrating existing MCP servers through the interface
4. Update Claude Desktop configuration
5. Enjoy dynamic MCP server management! 🎉
