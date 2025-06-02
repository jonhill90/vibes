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

info "Welcome to your Development Container!"
echo

#── show the key tools ───────────────────────────────────────────────
info "🔧 Tools available in this environment:"
printf "  • Node.js: %s\n" "$(node --version)"
printf "  • npm:     %s\n" "$(npm --version)"

#── Codex CLI check ──────────────────────────────────────────────
if command -v codex &>/dev/null; then
  CODEX_PATH=$(which codex)
  CODEX_VER=$(codex --version 2>/dev/null || echo "n/a")
  success "Codex CLI: found at $CODEX_PATH (v$CODEX_VER)"
else
  warn    "Codex CLI: NOT found in PATH"
fi

#── PowerShell check ─────────────────────────────────────────────────
if command -v pwsh &>/dev/null; then
  PS_PATH=$(which pwsh)
  PS_VER=$("$PS_PATH" -c '$PSVersionTable.PSVersion.ToString()')
  success "PowerShell: found at $PS_PATH (v$PS_VER)"
else
  warn    "PowerShell: NOT found in PATH"
fi

echo
#── Claude CLI check ────────────────────────────────────────────────
info "🔧 Claude CLI status:"
if command -v claude &>/dev/null; then
  CLAUDE_PATH=$(which claude)
  CLAUDE_VER=$(claude --version 2>/dev/null || echo "n/a")
  success "Claude CLI: found at $CLAUDE_PATH (v$CLAUDE_VER)"
else
  warn    "Claude CLI: NOT found in PATH"
fi

echo
#── Azure CLI check ─────────────────────────────────────────────────
info "☁️ Azure CLI status:"
if command -v az &>/dev/null; then
  AZ_PATH=$(which az)
  AZ_VER=$(az --version 2>/dev/null | head -n1 | awk '{print $2}')
  success "Azure CLI: found at $AZ_PATH (v$AZ_VER)"
else
  warn    "Azure CLI: NOT found in PATH"
fi

echo
#── Claude (Anthropic) configuration ────────────────────────────────
info "🔑 Configuring Claude (Anthropic)…"
if [[ -n "${ANTHROPIC_API_KEY-}" ]]; then
  success "ANTHROPIC_API_KEY is set"
  CONF_DIR="$HOME/.config/anthropic"
  mkdir -p "$CONF_DIR"
  cat > "$CONF_DIR/credentials.json" <<-EOF
  {
    "api_key": "${ANTHROPIC_API_KEY}"
  }
EOF
  chmod 600 "$CONF_DIR/credentials.json"
  success "Wrote credentials to $CONF_DIR/credentials.json"
else
  error "ANTHROPIC_API_KEY is missing — Claude may not work!"
fi

echo
#── Codex (OpenAI) configuration ────────────────────────────────
info "🔑 Configuring Codex (OpenAI)…"
if [[ -n "${OPENAI_API_KEY-}" ]]; then
  success "OPENAI_API_KEY is set"
  CODEX_CONF_DIR="$HOME/.codex"
  mkdir -p "$CODEX_CONF_DIR"
  cat > "$CODEX_CONF_DIR/config.json" <<-EOF
{
  "model": "o4-mini",
  "approvalMode": "suggest",
  "notify": true
}
EOF
  chmod 600 "$CODEX_CONF_DIR/config.json"
  success "Wrote config to $CODEX_CONF_DIR/config.json"
else
  error "OPENAI_API_KEY is missing — Codex may not work!"
fi

echo
success "Post-create steps completed!"

echo
#── Network connectivity test ──────────────────────────────────────
info "🌐 Testing vibes-network connectivity..."
if command -v ping &>/dev/null && command -v curl &>/dev/null; then
    bash /usr/local/share/test-network.sh
else
    warn "ping or curl not available, skipping network test"
fi


# Add these to your shell profile to always navigate to vibes
alias cdv="cd /workspace/vibes"
alias vibes="cd /workspace/vibes"
export VIBES_HOME="/workspace/vibes"

