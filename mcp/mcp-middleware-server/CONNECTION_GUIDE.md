# 🔗 MCP Middleware Connection Guide

## 🌐 Network Access Patterns

### **From Host Machine (You):**
- **Health**: `http://localhost:5001/health`
- **SSE**: `http://localhost:5001/sse`  
- **Messages**: `http://localhost:5001/messages/`

### **From Vibes Container (Claude/Agent-0):**
- **Health**: `http://host.docker.internal:5001/health`
- **SSE**: `http://host.docker.internal:5001/sse`
- **Messages**: `http://host.docker.internal:5001/messages/`

## 📱 Testing Commands

### **Your Terminal (Host Machine):**
```bash
# Test health
curl -s http://localhost:5001/health

# Test SSE connection
curl -H "Accept: text/event-stream" -N --max-time 10 http://localhost:5001/sse

# Check what's running
docker ps | grep middleware
```

### **Vibes Container (Agent-0):**
```bash
# Test health  
curl -s http://host.docker.internal:5001/health

# Test SSE connection
curl -H "Accept: text/event-stream" -N --max-time 10 http://host.docker.internal:5001/sse

# Run comprehensive test
python3 test_mcp_connection.py
```

## ⚙️ Claude Desktop Configuration

### **Option 1: Claude.ai Web Interface (Recommended)**
According to Anthropic docs, add via Settings > Integrations
- URL: `http://localhost:5001/sse`

### **Option 2: claude_desktop_config.json (Legacy)**
```json
{
  "mcpServers": {
    "middleware": {
      "command": "npx",
      "args": ["mcp-remote", "http://localhost:5001/sse"]
    }
  }
}
```

**Important**: Use `localhost` for Claude Desktop, NOT `host.docker.internal`

## 🐳 Docker Port Mapping
```yaml
# docker-compose.yml
ports:
  - "5001:5000"  # Host port 5001 → Container port 5000
```

This means:
- **Inside container**: Service runs on port 5000
- **Outside container**: Access via port 5001
- **From host**: Use `localhost:5001`
- **From other containers**: Use `host.docker.internal:5001`

## 🧪 Verification Steps

### **1. Test from your host machine:**
```bash
curl http://localhost:5001/health
# Should return: {"status":"healthy","service":"mcp-middleware-remote","loaded_mcps":0}
```

### **2. Test SSE endpoint:**
```bash
curl -H "Accept: text/event-stream" -N --max-time 5 http://localhost:5001/sse
# Should return: event: endpoint + session data + pings
```

### **3. Check container logs:**
```bash
docker logs mcp-middleware-server
# Should show: "Starting MCP Middleware Remote Server on 0.0.0.0:5000"
```

## 🎯 Ready for Claude Desktop Integration!

The middleware server is now accessible at `http://localhost:5001/sse` for your Claude Desktop configuration.
