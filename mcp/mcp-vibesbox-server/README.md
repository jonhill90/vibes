# MCP Vibesbox Server

✅ **PRODUCTION READY** - Unified MCP server that combines shell access + VNC GUI automation for managing containerized desktop environments.

## Features

### ✅ **Complete & Tested** (July 2025)
- **`run_command`** - Execute shell commands in container environment
- **`take_screenshot`** - Capture desktop screenshots as base64 images for Claude's vision
- **`click_desktop`** - Click at coordinates on the desktop (single/double-click)
- **`type_text`** - Type text into GUI applications
- **`send_keys`** - Send keyboard combinations (Ctrl+C, Alt+Tab, etc.)
- **`start_vnc_server`** - Start/manage VNC server sessions

## Status: ✅ **PRODUCTION READY**

**Core VNC functionality implemented and thoroughly tested:**
- VNC server running on display `:1` (port 5901)
- XFCE4 desktop environment fully operational
- Screenshot capture with ImageMagick working perfectly
- Desktop automation with xdotool working flawlessly
- Base64 image output for Claude's vision validated
- All 6 MCP tools tested and operational

## Validated Workflows

✅ **Visual Feedback Loop**: Screenshot → Claude analysis → automation → verification  
✅ **GUI Application Control**: Launch apps, click elements, type text  
✅ **Desktop Navigation**: Menu interaction, window management  
✅ **Error Handling**: Proper responses to edge cases  

## Usage

### Start the Container
```bash
cd /workspace/vibes/mcp/mcp-vibesbox-server
docker compose up -d
```

### MCP Configuration
Add to your Claude Desktop MCP config:
```json
"vibesbox": {
  "command": "docker",
  "args": ["exec", "-i", "mcp-vibesbox-server", "python3", "/workspace/server.py"]
}
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

## Testing Results ✅

**All Systems Operational (July 7, 2025):**
- ✅ Screenshot Capture: 1024x768 PNG → base64 conversion working perfectly
- ✅ Desktop Automation: Precise mouse clicks and keyboard input working flawlessly  
- ✅ VNC Server: XFCE4 desktop accessible and fully functional
- ✅ Application Integration: Menu system, application launching working
- ✅ MCP Interface: All 6 tools tested through Claude Desktop
- ✅ Visual Feedback: Screenshot → Claude analysis → automation workflows validated

## Use Cases

**Perfect for:**
- **GUI Application Testing**: Automated interaction with desktop applications
- **Visual Workflows**: Claude can see desktop state and respond appropriately
- **Application Demonstrations**: Record and replay GUI interactions
- **Desktop Environment Management**: Programmatic control of containerized desktop
- **Testing & QA**: Automated GUI testing workflows

## Requirements

- Docker with vibes-network
- VNC viewer (optional, for human observation)
- Claude Desktop with MCP configuration

## Performance

- **Screenshot Speed**: ~0.5s capture + base64 conversion
- **Automation Latency**: Instant mouse/keyboard response  
- **Memory Usage**: XFCE4 desktop keeps container footprint reasonable
- **Resolution**: 1024x768 (configurable)

---

**Status**: ✅ **COMPLETE & PRODUCTION READY** for GUI automation workflows

**Version**: 1.0 (July 2025)
