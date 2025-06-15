# MCP Middleware Server

Dynamic MCP (Model Context Protocol) middleware for Agent-0.

## Overview

This middleware enables dynamic loading and management of MCP servers without requiring configuration changes or Claude Desktop restarts.

## Features

- Dynamic MCP loading/unloading
- Tool aggregation and routing  
- Real-time feedback via SSE
- Persistent configuration registry

## Quick Start

1. Install dependencies: `pip install -r requirements.txt`
2. Run tests: `./run_tests.sh`
3. Configure Claude Desktop with the generated example configuration

## Usage

Basic tools:
- `load_mcp` - Load new MCP server
- `list_loaded_mcps` - Show all loaded MCPs
- `get_mcp_status` - Get detailed MCP status
- `discover_mcps` - Find MCPs in directory

## Testing

Run `./run_tests.sh` for comprehensive validation.
