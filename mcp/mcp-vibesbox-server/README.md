# MCP Vibesbox Server

Unified MCP server that combines shell access + VNC GUI automation for managing containerized desktop environments.

## Features

### ✅ **Working** (Implemented & Tested)
- **`run_command`** - Execute shell commands in container environment
- **`take_screenshot`** - Capture desktop screenshots as base64 images for Claude's vision
- **`click_desktop`** - Click at coordinates on the desktop (single/double-click)
- **`type_text`** - Type text into GUI applications
- **`send_keys`** - Send keyboard combinations (Ctrl+C, Alt+Tab, etc.)
- **`start_vnc_server`** - Start/manage VNC server sessions

### 🚧 **Planned** (Future Development)
- Multi-vibesbox environment management
- Template system (development, testing, demo, minimal)
- Container lifecycle management
- Advanced window management tools

## Current Status

**READY FOR USE** - Core VNC functionality implemented and tested:
- VNC server running on display `:1` (port 5901)
- XFCE4 desktop environment active
- Screenshot capture with ImageMagick working
- Desktop automation with xdotool working
- Base64 image output for Claude's vision working

## Usage

### Start the Container
```bash
cd /workspace/vibes/mcp/mcp-vibesbox-server
docker compose up -d
```

### Test VNC Functionality
```bash
# Test screenshot
docker exec mcp-vibesbox-server python3 /workspace/server.py

# Access via VNC viewer
# Server: localhost:5901
# Password: vibes123
```

### Available MCP Tools

#### Shell Access
- `run_command(command, working_dir)` - Execute shell commands

#### Visual Feedback  
- `take_screenshot(display=":1")` - Returns viewable screenshot for Claude

#### Desktop Automation
- `click_desktop(x, y, button=1, double_click=False)` - Mouse control
- `type_text(text)` - Keyboard input
- `send_keys(keys)` - Key combinations (e.g., "ctrl+c", "alt+Tab")

#### VNC Management
- `start_vnc_server(display=":1", geometry="1024x768", password="vibes123")`

## Architecture

```
MCP Vibesbox Server
├── Shell Layer (subprocess execution)
├── VNC Layer (TigerVNC + XFCE4)  
├── Screenshot Layer (ImageMagick → base64)
├── Automation Layer (xdotool for mouse/keyboard)
└── Management Layer (VNC server control)
```

**Container Stack:**
- Ubuntu 22.04 base
- TigerVNC server + XFCE4 desktop
- ImageMagick for screenshots
- xdotool for automation
- Python MCP server

**Network:**
- VNC: Port 5901 (display :1)
- Docker network: vibes-network
- MCP: stdio transport

## Testing Results

✅ **Screenshot Capture**: 1024x768 PNG → base64 conversion working  
✅ **Desktop Automation**: Mouse clicks and keyboard input working  
✅ **VNC Server**: XFCE4 desktop accessible via VNC viewer  
✅ **Container Integration**: Docker socket access and volume mounts working  

## Next Development Phase

Ready for advanced features:
1. **Multi-environment support** - Create/manage multiple vibesbox containers
2. **Template system** - Pre-configured environments (dev, test, demo)
3. **Enhanced automation** - Window management, app launching
4. **Visual feedback loops** - Screenshot → Claude analysis → automation

## Requirements

- Docker with vibes-network
- VNC viewer (optional, for human observation)
- Host paths mounted appropriately

---

**Status**: ✅ **PRODUCTION READY** for core VNC automation workflows
