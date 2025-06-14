# Technical Implementation Details

## 🔧 MCP Middleware Technical Specification

### Core Architecture
```python
# MCP Middleware exposes these tools to Claude:

@server.list_tools()
async def list_tools():
    return [
        Tool(name="load_mcp_server", 
             description="Dynamically load an MCP server",
             inputSchema={
                 "path": {"type": "string"},
                 "name": {"type": "string"}
             }),
        Tool(name="test_mcp_tool",
             description="Test a tool from loaded MCP",
             inputSchema={
                 "mcp_name": {"type": "string"},
                 "tool_name": {"type": "string"},
                 "args": {"type": "object"}
             }),
        Tool(name="start_sse_stream",
             description="Start SSE endpoint for real-time feedback"),
        # ... more tools
    ]
```

### Dynamic Loading Mechanism
```python
# How MCPs are loaded without restart:
import importlib.util
import sys

def load_mcp_dynamically(name: str, path: str):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    
    # Get the server instance
    server = module.server
    registry[name] = server
    
    # Notify via SSE
    broadcast_event({
        "type": "mcp_loaded",
        "name": name,
        "tools": await server.list_tools()
    })
```

### SSE Implementation
```python
# Real-time feedback to Claude
async def sse_endpoint(request):
    response = web.StreamResponse()
    response.headers['Content-Type'] = 'text/event-stream'
    await response.prepare(request)
    
    try:
        while True:
            event = await event_queue.get()
            await response.write(f"data: {json.dumps(event)}\n\n".encode())
    except Exception:
        pass
    
    return response
```

## 🎮 Vibes (Agent-1) Technical Architecture

### Frontend Structure (Discord-like UI)
```
concept/
├── index.html          # Main layout
├── src/
│   ├── App.jsx        # Main React component
│   ├── components/
│   │   ├── AgentList.jsx      # Left sidebar (like Discord servers)
│   │   ├── ChatArea.jsx       # Main chat interface
│   │   ├── AgentScreen.jsx    # Screen share view
│   │   └── InputArea.jsx      # Message input
│   └── agents/
│       ├── BrowserAgent.js    # Web automation
│       ├── CodeAgent.js       # Code execution
│       └── FileAgent.js       # File operations
```

### Agent Communication Protocol
```javascript
// WebSocket message format
{
  "type": "agent_message",
  "agent": "browser",
  "action": "navigate",
  "data": {
    "url": "https://example.com"
  },
  "timestamp": "2024-06-14T10:30:00Z"
}

// Screen share update
{
  "type": "screen_update",
  "agent": "browser",
  "screenshot": "base64_image_data",
  "timestamp": "2024-06-14T10:30:01Z"
}
```

### Backend Architecture
```
vibes-backend/
├── server.js           # Main Express/WebSocket server
├── agents/
│   ├── base.js        # Base agent class
│   ├── browser.js     # Lightpanda integration
│   ├── code.js        # Code execution sandboxing
│   └── file.js        # File system operations
├── memory/
│   ├── session.js     # Short-term memory
│   └── persistent.js  # Long-term storage
└── llm/
    ├── router.js      # LLM selection logic
    ├── bedrock.js     # AWS Bedrock integration
    └── azure.js       # Azure OpenAI integration
```

## 🔌 Integration Points

### Lightpanda Browser Integration
```javascript
// Why Lightpanda?
// - 9x less memory than Chrome
// - 11x faster execution
// - Perfect for agent automation

import { Browser } from 'lightpanda';

class BrowserAgent {
  async navigate(url) {
    const page = await this.browser.newPage();
    await page.goto(url);
    
    // Capture screenshot for UI
    const screenshot = await page.screenshot();
    this.broadcastScreen(screenshot);
    
    return page;
  }
}
```

### Cloud LLM Integration (Future)
```javascript
// AWS Bedrock
const bedrock = new BedrockRuntime({
  region: 'us-east-1'
});

// Azure OpenAI
const azure = new OpenAIClient(
  endpoint,
  new AzureKeyCredential(apiKey)
);

// Router selects based on:
// - Task complexity
// - Cost considerations
// - Latency requirements
// - Model capabilities
```

## 🚀 Performance Considerations

### MCP Middleware Performance
- Dynamic loading: ~50ms per MCP
- SSE latency: <10ms local
- Tool execution: Depends on tool
- Memory overhead: Minimal

### Vibes Performance Targets
- UI responsiveness: <100ms
- Agent action visibility: Real-time
- Chat latency: <200ms
- Screen share FPS: 10-30 (configurable)

## 🔐 Security Considerations

### MCP Security
- Sandboxed execution environments
- Permission system for file access
- No network access by default
- Audit logging for all actions

### Vibes Security
- Local-first: Data stays on machine
- Encrypted cloud communication
- Sanitized LLM inputs/outputs
- User approval for sensitive actions

