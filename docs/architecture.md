# Vibes Architecture 🏗️

Understanding how Vibes transforms Claude Desktop into a powerful development environment.

## High-Level Overview

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   Claude        │    │   MCP Servers    │    │   Services      │
│   Desktop       │◄──►│                  │◄──►│                 │
│                 │    │ • Shell Access   │    │ • Vector DB     │
│                 │    │ • Memory         │    │ • Ollama        │
│                 │    │ • Code Analysis  │    │ • Containers    │
└─────────────────┘    └──────────────────┘    └─────────────────┘
```

## Core Components

### 1. Claude Desktop
- **Role**: Primary interface and orchestrator
- **Capabilities**: Natural language processing, conversation management
- **Integration**: Communicates with MCP servers via standardized protocol

### 2. MCP (Model Context Protocol) Servers
- **Role**: Capability providers for Claude
- **Protocol**: Standardized interface for tool integration
- **Types**: Shell access, memory, repository analysis

### 3. Docker Infrastructure
- **Role**: Isolated execution environment
- **Benefits**: Security, reproducibility, easy deployment
- **Network**: Shared `vibes-network` for service communication

## MCP Server Architecture

### mcp-vibes-server (Shell Access)
```
┌─────────────────────────────────────────┐
│             mcp-vibes-server            │
├─────────────────────────────────────────┤
│ • Python MCP implementation             │
│ • Shell command execution               │
│ • File system operations                │
│ • Docker socket access                  │
├─────────────────────────────────────────┤
│ Mounted Volumes:                        │
│ • /var/run/docker.sock (Docker access) │
│ • /workspace/vibes (File operations)   │
│ • vibes_workspace (Persistence)        │
└─────────────────────────────────────────┘
```

### mcp-openmemory-server (Memory)
```
┌─────────────────────────────────────────┐
│          OpenMemory Stack               │
├─────────────────────────────────────────┤
│ openmemory-ui (Port 3000)              │
│ ├─ Web interface for memory management  │
├─────────────────────────────────────────┤
│ openmemory-mcp (Port 8765)             │
│ ├─ MCP protocol implementation          │
│ ├─ Memory storage and retrieval         │
├─────────────────────────────────────────┤
│ qdrant (Ports 6333, 6334)              │
│ ├─ Vector database                      │
│ ├─ Semantic search                      │
│ └─ Persistent storage                   │
└─────────────────────────────────────────┘
```

### deepwiki-server (Code Analysis)
```
┌─────────────────────────────────────────┐
│           DeepWiki Remote               │
├─────────────────────────────────────────┤
│ • GitHub repository analysis            │
│ • Documentation parsing                 │
│ • Code structure understanding          │
│ • Remote MCP server (mcp.deepwiki.com) │
└─────────────────────────────────────────┘
```

## Data Flow

### 1. User Interaction
```
User Input → Claude Desktop → MCP Protocol → Appropriate Server → Execution → Response
```

### 2. Shell Command Example
```
"Run ls -la" → Claude Desktop → mcp-vibes-server → Container Execution → File List → User
```

### 3. Memory Storage Example
```
"Remember this" → Claude Desktop → openmemory-mcp → Vector Storage → Confirmation → User
```

### 4. Code Analysis Example
```
"Analyze React repo" → Claude Desktop → deepwiki-server → GitHub API → Analysis → User
```

## Network Architecture

### Docker Network: `vibes-network`
```
┌─────────────────────────────────────────────────────────────┐
│                    vibes-network                            │
├─────────────────┬─────────────────┬─────────────────────────┤
│  mcp-vibes      │  openmemory-*   │  Additional Services    │
│  (shell access) │  (memory stack) │  (as needed)           │
└─────────────────┴─────────────────┴─────────────────────────┘
```

### Port Mapping
- **3000**: OpenMemory UI (memory management interface)
- **6333/6334**: Qdrant vector database
- **8765**: OpenMemory MCP server
- **11434**: Ollama (on host, accessed via host.docker.internal)

## File System Architecture

### Workspace Structure
```
/workspace/
├── vibes/                    # Main project (mounted from host)
│   ├── mcp/                  # MCP server configurations
│   ├── repos/                # Cloned repositories (gitignored)
│   ├── projects/             # User projects (gitignored)
│   └── docs/                 # Documentation
└── [other-workspaces]        # Additional persistent storage
```

### Volume Mounting Strategy
- **Host Volume**: `/path/to/vibes` → `/workspace/vibes` (bidirectional sync)
- **Docker Socket**: `/var/run/docker.sock` → (container management)
- **Persistent Volume**: `vibes_workspace` → (cross-session persistence)

## Security Model

### Containerization Benefits
- **Process Isolation**: Commands run in isolated containers
- **File System Isolation**: Limited access to host system
- **Network Isolation**: Services communicate over defined networks
- **Resource Limits**: Prevent resource exhaustion

### Access Controls
- **Docker Socket**: Carefully controlled container access
- **Volume Mounts**: Limited to specific directories
- **Network Access**: Restricted to vibes-network
- **User Permissions**: Non-root execution where possible

## Scalability Considerations

### Adding New Capabilities
1. **Create MCP Server**: Implement the MCP protocol
2. **Containerize**: Package in Docker container
3. **Network Integration**: Connect to vibes-network
4. **Configuration**: Add to Claude Desktop config
5. **Documentation**: Update capability descriptions

### Service Discovery
- **Static Configuration**: Services have known addresses
- **Docker DNS**: Automatic service name resolution
- **Health Checks**: Monitor service availability

## Performance Characteristics

### Latency Factors
- **MCP Protocol**: Minimal overhead for tool calls
- **Container Startup**: Sub-second for running containers
- **Network Communication**: Local Docker network speeds
- **Memory Operations**: Vector database query performance

### Resource Usage
- **Memory**: Varies by active services and data
- **CPU**: Burst usage during command execution
- **Storage**: Persistent volumes for data retention
- **Network**: Local traffic only (except external APIs)

## Development Workflow

### Typical Development Cycle
1. **Describe Intent**: Natural language description to Claude
2. **Tool Selection**: Claude chooses appropriate MCP servers
3. **Execution**: Commands/operations run in containers
4. **Iteration**: Refine through continued conversation
5. **Persistence**: Results stored in workspace/memory

### Error Handling
- **Container Failures**: Automatic restart policies
- **Network Issues**: Retry mechanisms
- **Resource Limits**: Graceful degradation
- **State Recovery**: Persistent storage for critical data

---

*This architecture enables Claude Desktop to become a complete development environment through conversation*
