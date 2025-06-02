# DevContainer Troubleshooting Guide

## Common Issues and Solutions

### 🐳 Docker Issues

**Problem**: "docker: command not found" or Docker daemon not accessible
- **Solution**: Make sure Docker Desktop is running on your host machine
- **Check**: Run `docker info` to test connectivity

**Problem**: Permission denied accessing Docker socket
- **Solution**: The devcontainer should handle this automatically via group membership
- **Manual fix**: `sudo usermod -aG docker $USER` (inside container)

### 🌐 Network Issues

**Problem**: Cannot connect to vibes-network
- **Solution**: Run `/usr/local/share/setup-network.sh` to create/connect to network
- **Manual**: `docker network create vibes-network` on host

**Problem**: MCP servers not reachable
- **Check**: Run `/usr/local/share/test-network.sh` to diagnose
- **Verify**: `docker network ls` should show vibes-network

### 🔧 Build Issues

**Problem**: Dockerfile build fails
- **Solution**: Check internet connectivity and package repositories
- **Retry**: Clear build cache with "Rebuild Container" command

**Problem**: Architecture mismatch (ARM64 vs AMD64)
- **Solution**: The Dockerfile should auto-detect, but check TARGETARCH

### 🔑 API Key Issues

**Problem**: Claude/Codex not working
- **Solution**: Set environment variables in VS Code or .env file:
  - `ANTHROPIC_API_KEY` for Claude
  - `OPENAI_API_KEY` for Codex
  - `AZURE_API_KEY` for Azure services

### 📁 File Permission Issues

**Problem**: Cannot write to mounted volumes
- **Solution**: Check that `vscode` user has proper permissions
- **Manual**: `sudo chown -R vscode:vscode /workspace`

## Diagnostic Commands

Run these commands inside the devcontainer to diagnose issues:

```bash
# Validate configuration
bash /usr/local/share/validate-config.sh

# Test Docker functionality  
bash /usr/local/share/test-docker.sh

# Test network connectivity
bash /usr/local/share/test-network.sh

# Check tool installations
which docker node python3 go dotnet az pwsh claude

# Check environment variables
env | grep -E "(ANTHROPIC|OPENAI|AZURE)"
```

## Getting Help

1. Run the diagnostic commands above
2. Check Docker Desktop is running
3. Verify your API keys are set
4. Try rebuilding the container from scratch
5. Check VS Code devcontainer logs for detailed error messages
