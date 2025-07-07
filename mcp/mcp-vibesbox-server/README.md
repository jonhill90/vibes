# MCP Vibesbox Server

Unified MCP server that combines shell access + VNC GUI automation for managing containerized desktop environments.

## Features

### Current (Copied from vibes MCP)
- ✅ `run_command` - Execute shell commands in container environment

### Planned (VNC Integration)
- 🚧 `take_screenshot` - Capture desktop screenshots as base64 images for Claude's vision
- 🚧 `click_desktop` - Click at coordinates on the desktop
- 🚧 `type_text` - Type text into GUI applications
- 🚧 `send_keys` - Send keyboard combinations (Ctrl+C, Alt+Tab, etc.)
- 🚧 Multi-vibesbox environment management
- 🚧 Template system (development, testing, demo, minimal)

## Usage

Currently functions as a copy of the vibes MCP server with placeholder VNC tools.

```bash
# Build the container
docker-compose build

# Run the server
docker-compose up -d
```

## Next Steps

1. Implement VNC screenshot functionality with base64 output
2. Add desktop automation tools (click, type, keys)
3. Create vibesbox container management
4. Add template system for different environment types
5. Test end-to-end with Claude vision + VNC viewer

## Architecture

- Base: Ubuntu 22.04 with TigerVNC + XFCE4
- MCP Server: Python with stdio transport
- VNC: TigerVNC server for GUI access
- Docker: Container management and networking
