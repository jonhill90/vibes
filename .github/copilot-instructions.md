# Vibes Workspace Instructions for GitHub Copilot

## About This Workspace

This is the **Vibes** workspace - a learning environment that gives Claude Desktop superpowers through MCP (Model Context Protocol) servers. The goal is to enable conversational learning where users describe what they want to build and Claude implements it while teaching.

## Key Technologies & Tools

**Container Environment:** We use Docker containers extensively. All MCP servers run in Docker on the `vibes-network`. Default shell is `bash` on Linux.

**MCP Servers:** This workspace includes several MCP servers that provide Claude with capabilities:
- `mcp-vibes-server`: Shell access and container management  
- `mcp-openmemory-server`: Persistent memory using Qdrant vector database
- `mcp-azure-server`: Azure cloud resource management
- `mcp-terraform-server`: Infrastructure as Code automation

**Development Stack:** Primary focus on Python, Terraform, Docker, and cloud technologies. We use VS Code extensions for Docker, Python, Azure CLI, and Terraform.

## Coding Standards & Preferences

**File Organization:** Follow the established structure:
- `/mcp/` - MCP server configurations and Docker setups
- `/docs/` - Documentation with beginner-friendly explanations
- `/projects/` - Active learning projects and labs
- `/repos/` - Repository examples and templates

**Documentation Style:** Write documentation for complete beginners. Use simple language, practical examples, and explain concepts step-by-step. Include emojis for visual appeal and readability.

**Docker Practices:** Use `docker compose` (not `docker-compose`). All services should connect to the `vibes-network`. Mount `/workspace` as working directory and include proper volume persistence.

**Environment Variables:** Use `${USER:-vibes-user}` pattern for user context in Docker configurations. Default user should be `vibes-user` for consistency.

## Learning Philosophy

The Vibes approach prioritizes **conversational learning** over traditional study methods. When generating code or explanations:
- Focus on "learning by doing" rather than theory-first approaches
- Provide working examples that can be immediately tested
- Break complex topics into digestible conversation-sized chunks
- Explain the "why" behind technical decisions in accessible language

## MCP Integration Context

When working with MCP-related functionality, remember that this workspace uses the OpenMemory MCP server for persistent memory across conversations. Users can store and retrieve context using memory tools. The deepwiki MCP server provides access to GitHub repository documentation and knowledge.

**Network Architecture:** All MCP servers communicate over Docker's `vibes-network` for seamless integration. Services can reference each other by container names.
