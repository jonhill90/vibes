#!/usr/bin/env bash
set -euo pipefail

# ┌───────────────────────────────────────────────────────────────────┐
# │                        Dev Container Setup                        │
# └───────────────────────────────────────────────────────────────────┘

#── helper for colored output ───────────────────────────────────────
info()    { printf "\033[36mℹ [INFO]\033[0m  %s\n" "$*"; }
success() { printf "\033[32m✔ [OK]\033[0m    %s\n" "$*"; }
warn()    { printf "\033[33m⚠ [WARN]\033[0m  %s\n" "$*"; }
error()   { printf "\033[31m✖ [ERROR]\033[0m %s\n" "$*"; }

info "Welcome to your Vibes Development Container!"
echo

#── show the key tools ───────────────────────────────────────────────
info "🔧 Core Tools:"
printf "  • Node.js: %s\n" "$(node --version 2>/dev/null || echo 'not found')"
printf "  • npm:     %s\n" "$(npm --version 2>/dev/null || echo 'not found')"
printf "  • Python:  %s\n" "$(python3 --version 2>/dev/null | awk '{print $2}' || echo 'not found')"
printf "  • Git:     %s\n" "$(git --version 2>/dev/null | awk '{print $3}' || echo 'not found')"

echo
info "🐳 Docker & Container Tools:"
if command -v docker &>/dev/null; then
  DOCKER_PATH=$(which docker)
  DOCKER_VER=$(docker --version 2>/dev/null | awk '{print $3}' | tr -d ',' || echo 'unknown')
  success "Docker CLI: found at $DOCKER_PATH (v$DOCKER_VER)"
  
  # Test Docker connectivity
  if docker info &>/dev/null; then
    success "Docker daemon: accessible"
  else
    warn "Docker daemon: not accessible (may connect after network setup)"
  fi
else
  error "Docker CLI: NOT found"
fi

if command -v docker-compose &>/dev/null || docker compose version &>/dev/null; then
  success "Docker Compose: available"
else
  warn "Docker Compose: NOT found"
fi

echo
info "🌐 Development Languages:"
if command -v go &>/dev/null; then
  GO_VER=$(go version 2>/dev/null | awk '{print $3}' || echo 'unknown')
  success "Go: found (${GO_VER})"
else
  warn "Go: NOT found (optional)"
fi

if command -v dotnet &>/dev/null; then
  DOTNET_VER=$(dotnet --version 2>/dev/null || echo 'unknown')
  success ".NET SDK: found (v$DOTNET_VER)"
else
  warn ".NET SDK: NOT found (optional)"
fi

if command -v pwsh &>/dev/null; then
  PS_VER=$(pwsh -c '$PSVersionTable.PSVersion.ToString()' 2>/dev/null || echo 'unknown')
  success "PowerShell: found (v$PS_VER)"
else
  warn "PowerShell: NOT found (optional)"
fi

echo
info "🐍 Python & MCP:"
if command -v pip3 &>/dev/null; then
  PIP_VER=$(pip3 --version 2>/dev/null | awk '{print $2}' || echo 'unknown')
  success "pip3: found (v$PIP_VER)"
else
  warn "pip3: NOT found"
fi

# Check if MCP is installed
if python3 -c "import mcp" &>/dev/null; then
  MCP_VER=$(python3 -c "import mcp; print(mcp.__version__)" 2>/dev/null || echo "unknown")
  success "MCP: found (v$MCP_VER)"
else
  warn "MCP: NOT found - installing..."
  pip3 install mcp &>/dev/null && success "MCP: installed" || error "MCP: installation failed"
fi

echo
#── AI Tools ──────────────────────────────────────────────
info "🤖 AI Tools:"
if command -v claude &>/dev/null; then
  CLAUDE_PATH=$(which claude)
  CLAUDE_VER=$(claude --version 2>/dev/null || echo "n/a")
  success "Claude CLI: found at $CLAUDE_PATH (v$CLAUDE_VER)"
else
  warn "Claude CLI: NOT found"
fi

if command -v codex &>/dev/null; then
  CODEX_PATH=$(which codex)
  CODEX_VER=$(codex --version 2>/dev/null || echo "n/a")
  success "Codex CLI: found at $CODEX_PATH (v$CODEX_VER)"
else
  warn "Codex CLI: NOT found"
fi

echo
#── Cloud Tools ─────────────────────────────────────────────────
info "☁️ Cloud Tools:"
if command -v az &>/dev/null; then
  AZ_PATH=$(which az)
  AZ_VER=$(az --version 2>/dev/null | head -n1 | awk '{print $2}' || echo 'unknown')
  success "Azure CLI: found at $AZ_PATH (v$AZ_VER)"
else
  warn "Azure CLI: NOT found"
fi

echo
#── API Key Configuration ────────────────────────────────────────────
info "🔑 Configuring API credentials…"

# Claude (Anthropic) configuration
if [[ -n "${ANTHROPIC_API_KEY-}" ]]; then
  success "ANTHROPIC_API_KEY is set"
  CONF_DIR="$HOME/.config/anthropic"
  mkdir -p "$CONF_DIR"
  cat > "$CONF_DIR/credentials.json" <<-EOFCRED
  {
    "api_key": "${ANTHROPIC_API_KEY}"
  }
EOFCRED
  chmod 600 "$CONF_DIR/credentials.json"
  success "Wrote Claude credentials to $CONF_DIR/credentials.json"
else
  warn "ANTHROPIC_API_KEY not set — Claude may not work"
fi

# Codex (OpenAI) configuration
if [[ -n "${OPENAI_API_KEY-}" ]]; then
  success "OPENAI_API_KEY is set"
  CODEX_CONF_DIR="$HOME/.codex"
  mkdir -p "$CODEX_CONF_DIR"
  if [ ! -f "$CODEX_CONF_DIR/config.json" ]; then
    cat > "$CODEX_CONF_DIR/config.json" <<-EOFCODEX
{
  "model": "gpt-4",
  "approvalMode": "suggest",
  "notify": true
}
EOFCODEX
    chmod 600 "$CODEX_CONF_DIR/config.json"
    success "Wrote Codex config to $CODEX_CONF_DIR/config.json"
  else
    success "Codex config already exists"
  fi
else
  warn "OPENAI_API_KEY not set — Codex may not work"
fi

echo
#── Docker group setup ──────────────────────────────────────────────
info "🐳 Setting up Docker access..."
if groups | grep -q docker; then
  success "User is in docker group"
else
  warn "User not in docker group - some Docker commands may fail"
fi

echo
#── Workspace setup ─────────────────────────────────────────────────
info "📁 Setting up workspace..."

# Add aliases to bashrc if not already present
if ! grep -q "alias cdv=" "$HOME/.bashrc" 2>/dev/null; then
  echo 'alias cdv="cd /workspace/vibes"' >> "$HOME/.bashrc"
  echo 'alias vibes="cd /workspace/vibes"' >> "$HOME/.bashrc"
  echo 'export VIBES_HOME="/workspace/vibes"' >> "$HOME/.bashrc"
  echo 'export PATH="/workspace/vibes/bin:$PATH"' >> "$HOME/.bashrc"
  success "Added workspace aliases to ~/.bashrc"
else
  success "Workspace aliases already configured"
fi

echo
success "🎉 Vibes development environment setup complete!"
echo
info "Available commands:"
info "  • cdv or vibes - Navigate to vibes directory"
info "  • docker ps - Check running containers"
if command -v claude &>/dev/null; then
  info "  • claude --help - Claude CLI help"
fi
if command -v az &>/dev/null; then
  info "  • az --help - Azure CLI help"
fi
echo
info "To test functionality:"
info "  • bash /usr/local/share/test-docker.sh - Test Docker access"
if [ -f "/usr/local/share/test-network.sh" ]; then
  info "  • bash /usr/local/share/test-network.sh - Test network connectivity"
fi
echo
