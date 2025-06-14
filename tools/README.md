# Vibes Tools

This directory contains tools that Agent-0 can use to interact with the vibes environment, organized by category.

## Directory Structure

```
tools/
├── visual/          # Screenshot, image, and visual tools
├── monitoring/      # Service checking, health monitoring, status tools  
├── network/         # Network testing, connectivity, and communication tools
├── dev/             # Development, debugging, and code tools
├── files/           # File management, backup, and data tools
├── system/          # System administration and configuration tools
└── README.md        # This file
```

## Quick Access

### Visual Tools (`visual/`)
- **`take-screenshot.sh`** - Core screenshot functionality using browserless MCP server
- **`view.sh`** - Screenshot wrapper with timestamps and file info
- **`screenshot.sh`** - Legacy HTML screenshot tool

### Monitoring Tools (`monitoring/`)
- **`check-services.sh`** - Check running services and port accessibility

### Other Categories
- **`network/`** - Network and connectivity tools (coming soon)
- **`dev/`** - Development and debugging tools (coming soon)  
- **`files/`** - File management tools (coming soon)
- **`system/`** - System administration tools (coming soon)

## Usage Examples

```bash
# Take a screenshot
./visual/take-screenshot.sh https://google.com

# Check service status
./monitoring/check-services.sh

# View website with timestamp
./visual/view.sh https://example.com
```

## Dependencies

- **Browserless MCP Server**: Port 9333 for screenshot functionality
- **Docker**: Required for service checks and container access
- **curl**: Used for HTTP requests and testing

## Output Locations

- **Screenshots**: `/workspace/vibes/screenshots/`
- **Logs**: Displayed in terminal or saved per tool

## Integration

These tools are designed for Agent-0 use through the vibes MCP environment. They provide capabilities for visual inspection, service monitoring, and environment interaction.

## Adding New Tools

When adding new tools:
1. Choose the appropriate category directory
2. Make scripts executable: `chmod +x toolname.sh`
3. Update the category README.md
4. Follow naming convention: `action-target.sh`
5. Include help text and error handling

