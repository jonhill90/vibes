# Feature Analysis: devcontainer_vibesbox_integration

## User Request Summary

Create INITIAL.md for automatic vibesbox lifecycle management integrated into VS Code devcontainer

### Clarifications Provided

**1. PRIMARY USE CASE:**
- Problem: Developers manually manage MCP Vibesbox Server (VNC + GUI automation) separately from devcontainer, creating friction
- Solution: Automatic vibesbox lifecycle management integrated into VS Code devcontainer
- Building: Devcontainer enhancement that auto-detects, creates, starts, and verifies vibesbox health
- End Result: Developer opens VS Code → devcontainer starts → vibesbox automatically ready → immediate GUI automation access

**2. TECHNICAL PREFERENCES:**
- Docker + Docker Compose (container orchestration)
- Bash scripting (automation logic)
- VS Code Dev Containers
- MCP Vibesbox Server (existing - VNC + XFCE4 + Chromium + xdotool)
- vibes-network (Docker network)
- Implementation: Bash scripts in `.devcontainer/scripts/`
- Key components: ensure-vibesbox.sh, check-vibesbox.sh, bash helper functions
- Configuration: Environment variables for customization

**3. INTEGRATION NEEDS:**
- MCP Vibesbox Server at `/workspace/vibes/mcp/mcp-vibesbox-server/`
- VS Code Devcontainer at `/workspace/vibes/.devcontainer/`
- Docker Network (vibes-network) - configurable
- Existing scripts: postCreate.sh, test-docker.sh, test-network.sh

**SPECIFIC REQUIREMENTS:**
- CLI usage for vibesbox operations
- Progress display during build/startup
- Graceful degradation (devcontainer works if vibesbox fails)
- Configurable network name
- Single vibesbox instance per devcontainer
- Full health checks (container + VNC + screenshot test)

**SUCCESS CRITERIA:**
- Auto-detection (running/stopped/missing)
- Auto-start if stopped
- Ask before building
- Progress indicators
- Full health check
- CLI helper functions
- Graceful degradation

---

## Core Requirements

### Explicit Requirements

1. **Automatic Lifecycle Management**
   - Auto-detect vibesbox container state (running/stopped/missing)
   - Auto-start if stopped
   - Prompt user before building (if missing)
   - Integrate into devcontainer startup sequence

2. **Health Verification**
   - Container health check (Docker API)
   - VNC server availability check (port 5901)
   - Screenshot test (ImageMagick capture)
   - Full validation before declaring "ready"

3. **User Experience**
   - Progress indicators during build/startup
   - Clear status messages (colored output)
   - Graceful degradation (devcontainer works if vibesbox fails)
   - No blocking on vibesbox failures

4. **CLI Helper Functions**
   - `vibesbox-status` - Check current state
   - `vibesbox-start` - Start if stopped
   - `vibesbox-stop` - Stop if running
   - `vibesbox-restart` - Restart container
   - `vibesbox-logs` - View container logs
   - `vibesbox-vnc` - Display VNC connection info

5. **Configuration**
   - Environment variables for customization
   - Network name configurable (default: vibes-network)
   - Container name configurable (default: mcp-vibesbox-server)
   - VNC port configurable (default: 5901)
   - Workspace path configurable (default: /workspace/vibes)

6. **Integration Points**
   - Hook into devcontainer postCreateCommand
   - Leverage existing postCreate.sh structure
   - Reuse helper functions (info, success, warn, error)
   - Integrate with existing test scripts

### Implicit Requirements

1. **Error Handling** (Inferred from "graceful degradation" requirement)
   - Catch and handle all Docker API errors
   - Provide actionable error messages
   - Continue devcontainer startup even if vibesbox fails
   - Log errors to accessible location for debugging

2. **Idempotency** (Inferred from "auto-detect" requirement)
   - Scripts should be safe to run multiple times
   - No duplicate containers created
   - No port conflicts from multiple instances
   - State checks before actions

3. **Performance** (Inferred from "progress indicators" requirement)
   - Build process should show real-time progress
   - Startup should be non-blocking where possible
   - Health checks should timeout appropriately
   - Background status checks for long operations

4. **Security** (Inferred from Docker/VNC context)
   - VNC should only bind to localhost by default
   - Docker socket access should be controlled
   - No hardcoded credentials
   - Environment variable validation

5. **Documentation** (Inferred from CLI helper requirement)
   - Inline help for all CLI functions
   - Error messages should guide resolution
   - Success messages should provide next steps
   - Troubleshooting guidance for common issues

6. **Logging** (Inferred from operational needs)
   - Capture vibesbox build/startup logs
   - Provide log viewing via CLI
   - Retain logs for debugging
   - Structured log format for parsing

---

## Technical Components

### Data Models

**Vibesbox State Object:**
```bash
VIBESBOX_STATE=(
  container_exists    # boolean: true/false
  container_running   # boolean: true/false
  vnc_port_open       # boolean: true/false
  screenshot_works    # boolean: true/false
  health_status       # string: healthy/unhealthy/unknown
  container_id        # string: Docker container ID or empty
  uptime              # string: Container uptime or "N/A"
)
```

**Configuration Object:**
```bash
VIBESBOX_CONFIG=(
  network_name        # string: Docker network name (default: vibes-network)
  container_name      # string: Container name (default: mcp-vibesbox-server)
  vnc_port           # int: VNC port (default: 5901)
  workspace_path     # string: Vibes workspace path (default: /workspace/vibes)
  compose_file       # string: Path to docker-compose.yml
  auto_build         # boolean: Build without prompting (default: false)
  health_timeout     # int: Health check timeout in seconds (default: 30)
)
```

### External APIs

**Docker API (via CLI):**
- `docker ps` - List containers
- `docker inspect` - Get container details
- `docker compose up -d` - Start via compose
- `docker compose build` - Build image
- `docker logs` - Fetch container logs
- `docker network ls` - List networks

**VNC/Display Testing:**
- `nc -z localhost 5901` - Port connectivity test
- `DISPLAY=:1 import -window root screenshot.png` - Screenshot test (ImageMagick)

**Network API:**
- `ping -c 1 mcp-vibesbox-server` - DNS resolution test
- `curl -s http://localhost:5901` - HTTP connectivity test (if applicable)

### Processing Logic

**Algorithm 1: Auto-Detection & Startup Workflow**
```
1. Load configuration from environment
2. Check if vibes-network exists
   - If not: Create network, log action
3. Check if container exists
   - If exists and running: Proceed to health check
   - If exists and stopped: Auto-start, proceed to health check
   - If not exists: Prompt for build (or auto-build if configured)
4. Health check sequence:
   a. Container running check (docker ps)
   b. VNC port open check (nc -z)
   c. Screenshot test (DISPLAY=:1 import)
5. Report status:
   - All checks pass: SUCCESS (green)
   - Any check fails: WARN (yellow, non-blocking)
   - Critical error: ERROR (red, guidance provided)
6. Export helper functions to shell environment
7. Continue devcontainer startup
```

**Algorithm 2: Health Check Validation**
```
1. Set timeout (default 30s)
2. Start timer
3. Check container running:
   - Poll docker ps every 2s
   - Break if running or timeout
4. Check VNC port:
   - Poll nc -z every 2s
   - Break if open or timeout
5. Check screenshot capability:
   - Try DISPLAY=:1 import
   - Retry 3 times with 2s delay
   - Mark success/failure
6. Return health object with:
   - Overall status (healthy/degraded/unhealthy)
   - Individual check results
   - Timestamp
   - Diagnostic messages
```

**Algorithm 3: Build Orchestration**
```
1. Verify docker-compose.yml exists
2. Check if image already built:
   - If built: Skip build, log message
3. Prompt user (unless auto_build=true):
   - "Vibesbox not found. Build now? (y/n)"
4. If yes to build:
   a. Display "Building vibesbox image..."
   b. Run: docker compose build --progress=plain
   c. Stream output to terminal (real-time)
   d. Capture exit code
5. If build succeeds:
   - Display "Build complete!"
   - Proceed to startup
6. If build fails:
   - Display error with log snippet
   - Provide troubleshooting steps
   - Exit gracefully (non-blocking)
```

### UI/CLI Requirements

**Interface Type:** CLI (Bash shell)

**Key Interactions:**

1. **Automatic (during devcontainer startup):**
   ```
   ℹ [INFO]  Checking vibesbox status...
   ℹ [INFO]  Vibesbox not running - starting...
   ✔ [OK]    Container started
   ℹ [INFO]  Waiting for VNC server...
   ✔ [OK]    VNC server ready on port 5901
   ℹ [INFO]  Testing screenshot capability...
   ✔ [OK]    Vibesbox fully operational
   ```

2. **Manual status check:**
   ```
   $ vibesbox-status

   Vibesbox Status:
   ================
   Container:    mcp-vibesbox-server
   Status:       running (healthy)
   Uptime:       2 hours 34 minutes
   VNC Port:     5901 (open)
   Network:      vibes-network
   Screenshot:   ✔ working

   VNC Connection: localhost:5901
   ```

3. **Manual operations:**
   ```
   $ vibesbox-start      # Start stopped container
   $ vibesbox-stop       # Stop running container
   $ vibesbox-restart    # Restart container
   $ vibesbox-logs       # View logs (last 50 lines)
   $ vibesbox-logs -f    # Follow logs (tail -f)
   $ vibesbox-vnc        # Display VNC connection details
   $ vibesbox-rebuild    # Rebuild image and restart
   ```

**Output Format:**
- Colored output using ANSI codes (existing pattern in postCreate.sh)
- Status symbols: ℹ (info), ✔ (success), ⚠ (warning), ✖ (error)
- Structured output for parsing (JSON option for scripts)
- Progress bars for long operations (build, startup)

---

## Similar Features Found (Archon Search)

### Feature 1: Docker Compose Integration Patterns
- **Source:** Archon knowledge base search results (MCP server examples)
- **Similarity Score:** 6/10
- **What's Similar:**
  - MCP server lifecycle management via Docker Compose
  - Health check implementations
  - Configuration via environment variables
  - Client initialization and lifecycle management
- **Lessons Learned:**
  - **Reuse:** Automatic client initialization patterns
  - **Avoid:** Complex configuration that requires manual setup
- **Code Patterns:**
  - Health check loops with timeout
  - Environment variable validation
  - Graceful degradation on connection failures

### Feature 2: Bash Automation Scripts (Existing Codebase)
- **Source:** `/Users/jon/source/vibes/.devcontainer/scripts/postCreate.sh`
- **Similarity Score:** 9/10
- **What's Similar:**
  - Helper functions (info, success, warn, error)
  - Tool availability checks
  - Docker connectivity testing
  - User-friendly colored output
- **Lessons Learned:**
  - **Reuse:** All helper functions, output formatting patterns
  - **Avoid:** Blocking operations without timeout
- **Code Patterns:**
  ```bash
  info()    { printf "\033[36mℹ [INFO]\033[0m  %s\n" "$*"; }
  success() { printf "\033[32m✔ [OK]\033[0m    %s\n" "$*"; }
  warn()    { printf "\033[33m⚠ [WARN]\033[0m  %s\n" "$*"; }
  error()   { printf "\033[31m✖ [ERROR]\033[0m %s\n" "$*"; }
  ```

### Feature 3: Container State Detection
- **Source:** Existing test-docker.sh script
- **Similarity Score:** 7/10
- **What's Similar:**
  - Docker CLI availability checks
  - Docker daemon connectivity tests
  - Group membership verification
- **Lessons Learned:**
  - **Reuse:** Docker socket permission checks
  - **Apply:** Same pattern for vibesbox-specific checks
- **Code Patterns:**
  ```bash
  if docker info &>/dev/null; then
    success "Docker daemon accessible"
  else
    warn "Docker daemon not accessible"
  fi
  ```

---

## Assumptions Made

### Assumption 1: Technology Stack (Bash + Docker Compose)
- **What:** Use Bash scripting for all automation, Docker Compose for container orchestration
- **Reasoning:**
  - Existing scripts are all Bash (postCreate.sh, test-*.sh)
  - MCP Vibesbox Server already uses docker-compose.yml
  - No additional dependencies required
  - Aligns with user's stated preference
- **Alternative:** Python scripts with docker-py library (more complex, requires Python in devcontainer)
- **Confidence:** High

### Assumption 2: Non-Blocking Startup
- **What:** Vibesbox startup should not block devcontainer initialization
- **Reasoning:**
  - "Graceful degradation" requirement suggests optional functionality
  - Developer should be able to work even if vibesbox fails
  - Startup failures shouldn't prevent VS Code from opening
- **Alternative:** Blocking startup until vibesbox ready (slower, more frustrating)
- **Confidence:** High

### Assumption 3: Single Instance Per Workspace
- **What:** Only one vibesbox container should exist per workspace
- **Reasoning:**
  - User requirement: "Single vibesbox instance per devcontainer"
  - Port conflicts would occur with multiple instances
  - Shared workspace volume prevents isolation
- **Alternative:** Multi-instance support with dynamic port allocation
- **Confidence:** High

### Assumption 4: VNC Localhost Binding
- **What:** VNC server should bind to localhost only by default
- **Reasoning:**
  - Security best practice (no remote VNC access without tunneling)
  - Existing docker-compose.yml binds to 5901 (host port)
  - Developer environment typically local
- **Alternative:** Expose to 0.0.0.0 for remote access (security risk)
- **Confidence:** Medium (user may want remote access)

### Assumption 5: Build Prompting
- **What:** Prompt user before building vibesbox image (unless auto_build=true)
- **Reasoning:**
  - Build process takes time (1-3 minutes)
  - User should be aware of resource usage
  - Aligns with "ask before building" requirement
- **Alternative:** Always auto-build (slower initial startup)
- **Confidence:** High

### Assumption 6: Health Check Timeout
- **What:** 30-second default timeout for health checks
- **Reasoning:**
  - Vibesbox startup typically takes 10-20 seconds
  - 30s allows buffer for slower systems
  - Prevents indefinite hanging
- **Alternative:** Longer timeout (60s+) or no timeout (risky)
- **Confidence:** Medium (may need tuning based on performance)

### Assumption 7: Screenshot Test as Final Check
- **What:** Screenshot capability test is definitive "healthy" indicator
- **Reasoning:**
  - Screenshot test validates full stack: VNC + X11 + ImageMagick
  - If screenshot works, GUI automation will work
  - Aligns with vibesbox's core purpose (GUI automation)
- **Alternative:** Just check container + VNC port (incomplete validation)
- **Confidence:** High

### Assumption 8: Environment Variable Configuration
- **What:** Use environment variables for all configurable settings
- **Reasoning:**
  - Standard pattern in existing codebase (ANTHROPIC_API_KEY, etc.)
  - Easy to override in devcontainer.json or .env
  - No additional config files needed
- **Alternative:** Dedicated config file (.vibesbox.conf)
- **Confidence:** High

---

## Success Criteria

### Functional Success
- [ ] Vibesbox auto-detects when devcontainer starts
- [ ] Vibesbox auto-starts if stopped
- [ ] User prompted before building (with configurable override)
- [ ] Full health check validates container + VNC + screenshot
- [ ] CLI helper functions available in shell
- [ ] Graceful degradation if vibesbox unavailable

### Quality Success
- [ ] Startup completes in <30 seconds (excluding build)
- [ ] Build process shows real-time progress
- [ ] Error messages provide actionable guidance
- [ ] No port conflicts or duplicate containers
- [ ] Health checks timeout appropriately (30s default)
- [ ] Scripts are idempotent (safe to re-run)

### User Success
- [ ] Developer can immediately use GUI automation after devcontainer opens
- [ ] Status is clear at all times (via CLI or auto-messages)
- [ ] Troubleshooting is self-service via CLI helpers
- [ ] No manual intervention required for common scenarios
- [ ] Documentation explains all CLI functions
- [ ] VNC connection details easily accessible

---

## Recommended Technology Stack

Based on Archon research and existing codebase patterns:

- **Language:** Bash (shell scripting)
  - **Reasoning:** All existing devcontainer scripts are Bash, no additional dependencies, native Docker CLI integration

- **Container Orchestration:** Docker Compose
  - **Reasoning:** Existing vibesbox uses docker-compose.yml, declarative configuration, easy lifecycle management

- **Health Checking:** Bash + Docker CLI + netcat + ImageMagick
  - **Reasoning:** Lightweight, no dependencies, already available in devcontainer and vibesbox

- **Configuration:** Environment Variables
  - **Reasoning:** Standard pattern, easy override in devcontainer.json, no config file parsing needed

- **Output Formatting:** ANSI Color Codes
  - **Reasoning:** Existing pattern in postCreate.sh, clear visual feedback, terminal-native

---

## Implementation Complexity

- **Estimated Complexity:** Medium
- **Key Challenges:**
  1. **Race Conditions:** Docker Compose up may return before VNC fully ready
     - **Mitigation:** Polling health checks with timeout

  2. **Error Handling:** Many failure modes (network missing, port conflict, build failure)
     - **Mitigation:** Explicit error handling for each failure mode, actionable messages

  3. **State Synchronization:** Container state may change between checks
     - **Mitigation:** Atomic state checks, idempotent operations

  4. **Cross-Platform:** Script must work in devcontainer environment
     - **Mitigation:** Test on actual devcontainer, avoid platform-specific commands

  5. **Performance:** Health checks shouldn't delay startup significantly
     - **Mitigation:** Parallel checks where possible, reasonable timeouts

---

## Next Steps for Downstream Agents

### For Codebase Researcher
- **Search for:** Docker Compose lifecycle management patterns in existing codebase
- **Focus on:**
  - Shell scripts in `.devcontainer/scripts/`
  - Helper function patterns (info, success, warn, error)
  - Docker API usage patterns
  - Health check implementations

### For Documentation Hunter
- **Technologies to research:**
  - Docker Compose (lifecycle commands, health checks)
  - VS Code Dev Containers (postCreateCommand hooks)
  - VNC protocol (port checking, connectivity)
  - ImageMagick (screenshot capture in headless mode)
  - Bash scripting (best practices, error handling)

- **Critical documentation:**
  - Docker Compose CLI reference
  - VS Code devcontainer.json schema
  - Bash script error handling patterns
  - Health check timeout patterns

### For Example Curator
- **Examples needed:**
  - Docker container state detection scripts
  - Health check loops with timeout
  - Progress indicators in Bash
  - CLI helper function implementations

- **Test patterns:**
  - Integration tests for container lifecycle
  - Mock Docker API for unit testing
  - Health check validation tests

---

**Generated:** 2025-10-04
**Archon Project:** 9b46c8e3-d6d6-41aa-91fb-ff681a67f413
**Feature Name:** devcontainer_vibesbox_integration
**Archon Sources Referenced:** 3 (MCP patterns, Docker automation examples, container lifecycle management)
