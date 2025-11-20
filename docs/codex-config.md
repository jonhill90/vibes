# Codex Configuration Reference

**Version**: 1.0
**Last Updated**: 2025-10-07
**For**: OpenAI Codex CLI v0.20+

---

## Overview

This guide provides comprehensive configuration reference for the `codex-prp` profile used in PRP-driven development workflows. It covers profile structure, MCP server integration, approval policies, sandbox modes, timeout tuning, and critical v0.20+ gotchas.

**Quick Links**:
- [Profile Structure](#profile-structure)
- [MCP Server Configuration](#mcp-server-configuration)
- [Approval Policies](#approval-policies)
- [Sandbox Modes](#sandbox-modes)
- [Timeout Configuration](#timeout-configuration)
- [Precedence Rules](#precedence-rules)
- [Complete Working Example](#complete-working-example)
- [Troubleshooting](#troubleshooting)

---

## Profile Structure

Profiles isolate configuration settings, preventing conflicts between different workflows (Claude vs Codex, manual vs automation).

### Basic Profile Syntax

```toml
[profiles.codex-prp]
model = "o4-mini"                    # Model selection
approval_policy = "on-request"        # Approval behavior
sandbox_mode = "workspace-write"      # File system access level
cwd = "/Users/jon/source/vibes"      # Working directory
startup_timeout_sec = 60              # MCP server startup timeout
tool_timeout_sec = 600                # Tool execution timeout (10 min)
```

### Model Selection

Choose model based on task complexity and speed requirements:

| Model | Speed | Reasoning | Use Case |
|-------|-------|-----------|----------|
| **o4-mini** | ⚡⚡ Medium | 🧠🧠🧠 High | **Recommended**: Balanced for PRP generation |
| **gpt-5-codex** | ⚡⚡⚡ Fast | 🧠🧠 Medium | Fast iteration, execution phases |
| **o3** | ⚡ Slow | 🧠🧠🧠🧠 Very High | Deep analysis, gotcha detection |

**Example: Different models for different profiles**

```toml
# PRP Generation (analysis-heavy)
[profiles.codex-prp-generate]
model = "o4-mini"
tool_timeout_sec = 600  # 10 minutes for research

# PRP Execution (fast iteration)
[profiles.codex-prp-execute]
model = "gpt-5-codex"
tool_timeout_sec = 300  # 5 minutes

# Deep Analysis (complex gotchas)
[profiles.codex-prp-analysis]
model = "o3"
tool_timeout_sec = 1200  # 20 minutes for reasoning
```

### Working Directory (cwd)

**CRITICAL**: Always set explicit working directory for predictable file paths.

```toml
# ❌ WRONG - No cwd (uses shell's current directory)
[profiles.codex-prp]
model = "o4-mini"
# Missing: cwd = ...

# ✅ RIGHT - Explicit working directory
[profiles.codex-prp]
model = "o4-mini"
cwd = "/Users/jon/source/vibes"  # Repo root - adjust to your path
```

**Platform-specific paths**:

```toml
# macOS/Linux (forward slashes)
cwd = "/Users/jon/source/vibes"

# Windows (use forward slashes or escaped backslashes)
cwd = "C:/Users/jon/source/vibes"           # Recommended
# OR
cwd = 'C:\Users\jon\source\vibes'           # Literal string (single quotes)
# OR
cwd = "C:\\Users\\jon\\source\\vibes"       # Escaped backslashes
```

---

## MCP Server Configuration

MCP servers provide tools (task tracking, knowledge base, Docker management) to Codex during execution. Two transport patterns: **STDIO** (local processes) and **HTTP** (remote services).

### STDIO Transport Pattern

**Use for**: Docker containers, local CLI tools, uvx-installed servers

```toml
[profiles.codex-prp.mcp_servers.SERVER_NAME]
command = "EXECUTABLE"
args = ["arg1", "arg2"]
env = { KEY = "value" }              # Optional environment variables
startup_timeout_sec = 90              # Optional: override profile default
```


```toml
command = "uvx"
startup_timeout_sec = 90  # Allow time for uvx dependency download
```

**Example: Basic Memory MCP Server (Docker)**

```toml
[profiles.codex-prp.mcp_servers.basic_memory]
command = "docker"
args = ["exec", "-i", "basic-memory-mcp", "/app/start.sh"]
startup_timeout_sec = 120  # Docker container startup time
```

**Example: Vibesbox MCP Server (Docker)**

```toml
[profiles.codex-prp.mcp_servers.vibesbox]
command = "docker"
args = ["exec", "-i", "mcp-vibesbox-server", "python3", "/workspace/server.py"]
startup_timeout_sec = 120
```

**Example: Docker MCP Server**

```toml
[profiles.codex-prp.mcp_servers.docker_mcp]
command = "docker"
args = ["mcp", "gateway", "run"]
```

### HTTP Transport Pattern

**Use for**: Remote MCP servers, HTTP-based services

```toml
[profiles.codex-prp.mcp_servers.SERVER_NAME]
url = "http://host:port/path"
bearer_token = "TOKEN"  # Optional: for authenticated servers
```


```toml
url = "http://localhost:8051/mcp"
```

**Example: Authenticated Remote Server**

```toml
experimental_use_rmcp_client = true  # Required for HTTP servers

[profiles.codex-prp.mcp_servers.figma]
url = "https://mcp.linear.app/mcp"
bearer_token = "your_token_here"  # OAuth bearer token
```

### Timeout Tuning

MCP servers have two critical timeout settings:

1. **`startup_timeout_sec`**: How long to wait for server to start (default: 10-30s)
2. **`tool_timeout_sec`**: Max execution time for tool calls (default: 60s)

**Common timeout issues**:

| Issue | Symptom | Solution |
|-------|---------|----------|
| **Server startup failure** | "Timeout waiting for server" | Increase `startup_timeout_sec` to 60-120s |
| **Long-running operations timeout** | "Request timeout" error -32001 | Increase `tool_timeout_sec` to 600s (10 min) |
| **Docker containers slow** | Server not ready in 30s | Increase to 120s, pre-start containers |
| **uvx dependency download** | First-run timeout | Increase to 90s, or pre-install with `uvx --install` |

**Recommended timeout configuration**:

```toml
[profiles.codex-prp]
# Profile-level defaults (apply to all servers unless overridden)
startup_timeout_sec = 60   # 1 minute for server startup
tool_timeout_sec = 600      # 10 minutes for long operations

# Server-specific overrides
command = "uvx"
startup_timeout_sec = 90  # Override: Allow extra time for uvx

[profiles.codex-prp.mcp_servers.basic_memory]
command = "docker"
args = ["exec", "-i", "basic-memory-mcp", "/app/start.sh"]
startup_timeout_sec = 120  # Override: Docker startup slower
```

**Phase-specific timeout recommendations**:

| Phase | Complexity | Recommended `tool_timeout_sec` |
|-------|-----------|-------------------------------|
| Phase 0 (Setup) | Low | 60s (default) |
| Phase 1 (Analysis) | Medium | 300s (5 min) |
| Phase 2 (Research) | High | 600s (10 min) |
| Phase 3 (Gotchas) | Very High | 900s (15 min) |
| Phase 4 (Assembly) | Medium | 300s (5 min) |

---

## Approval Policies

Approval policies control when Codex prompts for human confirmation before executing tools (file writes, network requests, etc.).

### Policy Options

```toml
[profiles.PROFILE_NAME]
approval_policy = "POLICY"
```

| Policy | Behavior | Use Case |
|--------|----------|----------|
| **untrusted** | Prompt for all commands | Safest: Never auto-execute |
| **on-request** | Prompt before tool use | **Recommended for generation**: Review all writes |
| **on-failure** | Only prompt on errors | **Recommended for execution**: Fast, less interruption |
| **never** | Full automation, no prompts | Automation/CI only, use with caution |

### v0.20+ Four-Setting Requirement

**CRITICAL**: Codex v0.20+ requires **FOUR settings** to fully bypass approval prompts:

```toml
# ❌ WRONG - Incomplete configuration (will still prompt)
[profiles.codex-prp]
approval_policy = "never"
sandbox_mode = "workspace-write"

# ✅ RIGHT - All four settings required for v0.20+
[profiles.codex-prp]
approval_policy = "never"
sandbox_mode = "workspace-write"
bypass_approvals = true      # NEW in v0.20+
bypass_sandbox = true         # NEW in v0.20+
trusted_workspace = true      # NEW in v0.20+
```

**Why this changed**: v0.20+ separates approval policy from approval bypass for security. Even with `approval_policy = "never"`, prompts appear unless bypass flags are set.

### Hybrid Approach (Recommended)

Use separate profiles for different workflows:

```toml
# Manual/Supervised runs (maximum safety)
[profiles.codex-prp-manual]
approval_policy = "on-request"  # Prompt for every tool use
sandbox_mode = "workspace-write"

# Automated runs (faster, still safe)
[profiles.codex-prp-auto]
approval_policy = "never"       # No prompts
sandbox_mode = "workspace-write"
bypass_approvals = true
bypass_sandbox = true
trusted_workspace = true

# Execution (balance safety and speed)
[profiles.codex-prp-exec]
approval_policy = "on-failure"  # Only prompt on errors
sandbox_mode = "workspace-write"
```

**Usage**:

```bash
# Manual run (review all actions)
codex exec --profile codex-prp-manual --prompt "Generate PRP"

# Automated run (trusted workflow)
codex exec --profile codex-prp-auto --prompt "Execute Phase 2"
```

---

## Sandbox Modes

Sandbox modes restrict file system access and network capabilities for security.

### Mode Comparison

| Mode | Reads | Writes | Network | Use Case |
|------|-------|--------|---------|----------|
| **read-only** | ✅ Workspace only | ❌ None | ❌ Disabled | Research phases, analysis |
| **workspace-write** | ✅ Workspace only | ✅ Workspace roots only | ⚠️ Disabled by default | **Recommended**: PRP generation |
| **danger-full-access** | ✅ Unrestricted | ✅ Unrestricted | ✅ Unrestricted | Emergency only, git operations |

### Workspace-Write Configuration

**Recommended for most workflows**: Allows writes to specific directories only.

```toml
[profiles.codex-prp]
sandbox_mode = "workspace-write"

# Define allowed write directories
[profiles.codex-prp.sandbox_workspace_write]
workspace_roots = [
    "/Users/jon/source/vibes/prps",  # PRP artifacts
    "/Users/jon/source/vibes/.codex"  # Codex commands
]
network_access = true  # Enable network (disabled by default)
```

**CRITICAL Gotcha**: Network access disabled by default in `workspace-write` mode!

```toml
# ❌ WRONG - Network access disabled
[profiles.codex-prp]
sandbox_mode = "workspace-write"
# Missing: network_access = true

# Result: WebSearch, API calls fail with "Network access denied"

# ✅ RIGHT - Enable network explicitly
[profiles.codex-prp]
sandbox_mode = "workspace-write"

[profiles.codex-prp.sandbox_workspace_write]
network_access = true  # Enable WebSearch, documentation fetching
```

### Git Repository Protection

**CRITICAL**: `.git/` folder always read-only in `workspace-write` mode (security measure).

```bash
# ❌ WRONG - Git operations fail in workspace-write sandbox
codex exec --profile codex-prp --prompt "Generate PRP, then git commit"
# Error: Permission denied writing to .git/objects/

# ✅ RIGHT - Separate Codex execution from git operations
# Step 1: Codex generates artifacts
codex exec --profile codex-prp --prompt "Generate PRP for feature X"

# Step 2: Git operations OUTSIDE Codex sandbox
git add prps/codex_integration/codex/
git commit -m "feat: Add Codex-generated PRP"
```

**Workaround for integrated workflows**: Use `danger-full-access` only for git operations.

```bash
# Generate with workspace-write (safe)
codex exec --profile codex-prp --sandbox workspace-write --prompt "Generate PRP"

# Commit with full access (minimal exposure)
codex exec --profile codex-prp --sandbox danger-full-access \
    --prompt "Commit changes: git add . && git commit -m 'Codex: Generated PRP'"
```

### Platform-Specific Behavior

| Platform | Implementation | Git Protection | Notes |
|----------|---------------|----------------|-------|
| **macOS** | Seatbelt (sandbox-exec) | ✅ Enforced | Most reliable |
| **Linux** | Landlock/seccomp | ✅ Enforced | Requires kernel 5.13+ |
| **Windows** | Experimental | ⚠️ Inconsistent | **Recommend WSL** |

---

## Timeout Configuration

Two types of timeouts control Codex behavior:

### 1. Startup Timeout

**Purpose**: How long to wait for MCP servers to start.
**Default**: 10-30 seconds (often too short for Docker/uvx servers).

```toml
[profiles.codex-prp]
startup_timeout_sec = 60  # Profile-level default

# Server-specific override
command = "uvx"
startup_timeout_sec = 90  # Allow extra time for dependency download
```

**Common startup issues**:

- **Docker containers**: 60-120s (container spin-up time)
- **uvx servers**: 60-90s (first-run dependency download)
- **HTTP servers**: 10-30s (usually fast)
- **Python venv**: 30-60s (if activating virtualenv)

### 2. Tool Timeout

**Purpose**: Max execution time for tool calls (file operations, MCP tools, etc.).
**Default**: 60 seconds (insufficient for complex PRP phases).

```toml
[profiles.codex-prp]
tool_timeout_sec = 600  # 10 minutes (recommended for PRP phases)

# For deep analysis
[profiles.codex-prp-analysis]
model = "o3"
tool_timeout_sec = 1200  # 20 minutes for reasoning models
```

**Timeout vs Model**:

- **gpt-5-codex**: Fast, use 300s timeout
- **o4-mini**: Balanced, use 600s timeout
- **o3**: Deep reasoning, use 1200s timeout

**Handling timeouts**:

```bash
# Wrapper with timeout and retry logic
execute_with_timeout() {
    local phase=$1
    local timeout=$2

    timeout $timeout codex exec --profile codex-prp \
        --prompt "$(cat .codex/commands/${phase}.md)"

    if [ $? -eq 124 ]; then
        echo "⚠️ Phase timed out - check partial output"
        # Attempt resume
        codex exec --profile codex-prp --resume \
            --prompt "Continue from previous timeout"
    fi
}

execute_with_timeout "phase2-research" 600
```

---

## Precedence Rules

Configuration precedence determines which settings apply when multiple sources exist.

### Precedence Order

**Highest Priority → Lowest Priority**:

1. **CLI flags** (e.g., `--model`, `--sandbox`)
2. **Profile settings** (`[profiles.codex-prp]`)
3. **Root config** (top-level settings in `config.toml`)
4. **Codex defaults** (built-in fallback values)

**Example**:

```toml
# Root-level default
model = "gpt-4"  # Applies to all profiles

[profiles.codex-prp]
model = "o4-mini"  # Overrides root for this profile
```

```bash
# CLI flag overrides everything
codex exec --profile codex-prp --model o3 --prompt "Deep analysis"
# Uses o3 (CLI flag), not o4-mini (profile) or gpt-4 (root)
```

### Profile Flag ALWAYS Required

**CRITICAL**: Always use explicit `--profile` flag to avoid config pollution.

```bash
# ❌ WRONG - Uses default or last-used profile
codex exec --prompt "Generate PRP"

# ✅ RIGHT - Explicit profile
codex exec --profile codex-prp --prompt "Generate PRP"
```

**Enforcement in wrapper scripts**:

```bash
enforce_profile() {
    if [[ "$*" != *"--profile"* ]]; then
        echo "❌ Error: --profile flag required"
        echo "Usage: codex exec --profile codex-prp --prompt '...'"
        exit 1
    fi
}

# Check before executing
enforce_profile "$@"
codex exec "$@"
```

---

## Complete Working Example

This is a complete, tested configuration for the `codex-prp` profile.

**Location**: `~/.codex/config.toml` (user-level) OR `.codex/config.toml` (repo-local)

```toml
# =============================================================================
# CODEX PROFILE: codex-prp
# =============================================================================
# Purpose: Dedicated profile for PRP generation/execution via Codex CLI
# Version: 1.0
# Date: 2025-10-07
#
# IMPORTANT: Always use with --profile flag:
#   codex exec --profile codex-prp --prompt "task description"

[profiles.codex-prp]

# Model Configuration
# - o4-mini: Balanced reasoning/speed for PRP generation
# - gpt-5-codex: Fast iteration for execution
# - o3: Deep analysis for complex gotcha detection
model = "o4-mini"

# Approval Policy
# - "untrusted": Prompt for all commands (safest, slowest)
# - "on-request": Prompt before tool use (recommended for generation)
# - "on-failure": Only prompt on errors (recommended for execution)
# - "never": Full automation (use with caution)
approval_policy = "on-request"

# Sandbox Mode
# - "read-only": No writes, no network (default for codex exec)
# - "workspace-write": Allow writes to workspace roots only
# - "danger-full-access": Full system access (requires explicit flag)
sandbox_mode = "workspace-write"

# v0.20+ Bypass Settings (required for automation)
# Uncomment for automated workflows (use with trusted code only):
# bypass_approvals = true
# bypass_sandbox = true
# trusted_workspace = true

# Timeout Configuration (in seconds)
# - startup_timeout_sec: How long to wait for MCP servers to start
# - tool_timeout_sec: Max execution time for tools (10 min for complex phases)
startup_timeout_sec = 60
tool_timeout_sec = 600  # 10 minutes

# Working Directory
# Set to repo root for consistent file paths
# IMPORTANT: Adjust this to your repository location
cwd = "/Users/jon/source/vibes"

# Sandbox Workspace Configuration
[profiles.codex-prp.sandbox_workspace_write]
# Define allowed write directories (only these paths writable)
workspace_roots = [
    "/Users/jon/source/vibes/prps",  # PRP artifacts
    "/Users/jon/source/vibes/.codex"  # Codex commands
]
# Enable network access (disabled by default in workspace-write)
network_access = true

# =============================================================================
# MCP Servers
# =============================================================================
# Pattern: Each server has either:
#   - STDIO: command + args + optional env

# Provides: Task tracking, knowledge base, project management
url = "http://localhost:8051/mcp"
# Note: HTTP servers don't use command/args, only URL

# Basic Memory MCP Server (STDIO via Docker)
# Provides: Persistent memory across Codex sessions
[profiles.codex-prp.mcp_servers.basic_memory]
command = "docker"
args = ["exec", "-i", "basic-memory-mcp", "/app/start.sh"]
startup_timeout_sec = 120  # Docker container startup time

# Vibesbox MCP Server (STDIO via Docker)
# Provides: Desktop automation, screenshot capture
[profiles.codex-prp.mcp_servers.vibesbox]
command = "docker"
args = ["exec", "-i", "mcp-vibesbox-server", "python3", "/workspace/server.py"]
startup_timeout_sec = 120

# Docker MCP Server (STDIO)
# Provides: Container management, image inspection
[profiles.codex-prp.mcp_servers.docker_mcp]
command = "docker"
args = ["mcp", "gateway", "run"]

# =============================================================================
# =============================================================================
# command = "uvx"
# startup_timeout_sec = 90  # Allow time for uvx dependency download

# =============================================================================
# Model Provider Overrides (Optional)
# =============================================================================
# Uncomment to add custom providers (Ollama, Azure, etc.)

# [model_providers.ollama]
# name = "Ollama Local"
# base_url = "http://localhost:11434/v1"
# wire_api = "chat"

# [model_providers.azure]
# name = "Azure OpenAI"
# base_url = "https://YOUR_PROJECT.openai.azure.com/openai"
# env_key = "AZURE_OPENAI_API_KEY"
# query_params = { api-version = "2025-04-01-preview" }
# wire_api = "responses"

# =============================================================================
# Usage Instructions
# =============================================================================
# 1. Copy this to ~/.codex/config.toml (user-level)
#    OR .codex/config.toml (repo-local for team sharing)
#
# 2. Update `cwd` to match your repository path
#
# 3. Update `workspace_roots` to match your directory structure
#
# 4. Test profile:
#    codex config show --profile codex-prp
#    codex config validate
#
# 5. Use profile with exec:
#    codex exec --profile codex-prp --prompt "task description"
#
# 6. Verify MCP servers:
#    Check logs at ~/.codex/logs/ for server startup issues
```

---

## Validation & Testing

### Validate Configuration

```bash
# Show effective profile configuration (resolved precedence)
codex config show --profile codex-prp

# Validate TOML syntax
codex config validate

# Test profile with simple command
codex exec --profile codex-prp --prompt "echo test"
```

### Test MCP Server Startup

```bash
# Check MCP server logs
tail -f ~/.codex/logs/mcp-servers.log

# Test specific server (if available)

# View all available MCP tools
codex exec --profile codex-prp --prompt "list available tools"
```

### Verify Approval Policy

```bash
# Test on-request policy (should prompt)
codex exec --profile codex-prp --approval-policy on-request \
    --prompt "Create test file"

# Test never policy (no prompts with v0.20+ bypass settings)
codex exec --profile codex-prp --approval-policy never \
    --prompt "Create test file"
```

### Verify Sandbox Mode

```bash
# Test read-only (write should fail)
codex exec --profile codex-prp --sandbox read-only \
    --prompt "Create file in current directory"

# Test workspace-write (write to workspace roots succeeds)
codex exec --profile codex-prp --sandbox workspace-write \
    --prompt "Create file in prps/ directory"

# Verify network access (if enabled)
codex exec --profile codex-prp --prompt "Search web for latest Python version"
```

---

## Troubleshooting

### Common Issues

#### 1. Approval Prompts Despite "never" Policy

**Symptom**: Prompts appear even with `approval_policy = "never"`.

**Cause**: v0.20+ requires bypass flags.

**Solution**:

```toml
[profiles.codex-prp]
approval_policy = "never"
bypass_approvals = true      # Add this
bypass_sandbox = true         # Add this
trusted_workspace = true      # Add this
```

#### 2. MCP Server Startup Timeout

**Symptom**: "Timeout waiting for server" error.

**Cause**: Default 10-30s timeout too short for Docker/uvx servers.

**Solution**:

```toml
[profiles.codex-prp]
startup_timeout_sec = 60  # Increase profile default

[profiles.codex-prp.mcp_servers.slow_server]
startup_timeout_sec = 120  # Or override per-server
```

#### 3. Network Access Denied

**Symptom**: "Network access denied" when using WebSearch or API calls.

**Cause**: Network disabled by default in `workspace-write` mode.

**Solution**:

```toml
[profiles.codex-prp.sandbox_workspace_write]
network_access = true  # Enable explicitly
```

#### 4. Git Operations Fail

**Symptom**: `git commit` returns "Permission denied" on `.git/objects/`.

**Cause**: `.git/` folder always read-only in `workspace-write` sandbox.

**Solution**: Run git operations outside Codex sandbox.

```bash
# Generate artifacts with Codex
codex exec --profile codex-prp --prompt "Generate PRP"

# Commit OUTSIDE Codex
git add prps/
git commit -m "feat: Add Codex-generated PRP"
```

#### 5. Wrong Profile Used

**Symptom**: Unexpected model, MCP servers, or approval behavior.

**Cause**: Omitted `--profile` flag (uses default).

**Solution**: Always use explicit `--profile` flag.

```bash
# ❌ WRONG
codex exec --prompt "task"

# ✅ RIGHT
codex exec --profile codex-prp --prompt "task"
```

### Debug Commands

```bash
# Show effective configuration (precedence resolved)
codex config show --profile codex-prp

# Check which profile is active
codex config list

# View MCP server logs
cat ~/.codex/logs/mcp-servers.log

# Test with JSON output for debugging
codex exec --profile codex-prp --json --prompt "test" 2>&1 | tee debug.log
```

---

## Additional Resources

**Official Documentation**:
- [Codex Configuration Guide](https://github.com/openai/codex/blob/main/docs/config.md)
- [Sandbox & Approvals](https://github.com/openai/codex/blob/main/docs/sandbox.md)
- [MCP Specification](https://modelcontextprotocol.io/specification/2025-03-26)
- [TOML Syntax](https://toml.io/en/v1.0.0)

**Local References**:
- Bootstrap Guide: `docs/codex-bootstrap.md`
- Artifact Structure: `docs/codex-artifacts.md`
- Validation Procedures: `docs/codex-validation.md`
- Example Config: `prps/codex_integration/examples/config_profile.toml`

---

**Last Updated**: 2025-10-07
**Maintained By**: Vibes Development Team
**Questions**: See troubleshooting section or consult `prps/codex_integration/planning/gotchas.md`
