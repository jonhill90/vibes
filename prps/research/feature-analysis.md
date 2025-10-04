# Feature Analysis: devcontainer_vibesbox_integration

## INITIAL.md Summary

Automatic MCP Vibesbox Server lifecycle management integrated into VS Code devcontainer with intelligent state detection, health verification, and graceful degradation. The system automatically detects vibesbox container state (running/stopped/missing) during devcontainer startup, starts stopped containers without intervention, prompts for builds when missing, verifies health through multi-layer checks (container → VNC → screenshot), and provides CLI helper functions for manual operations. The implementation uses bash scripts integrated via devcontainer lifecycle hooks with comprehensive error handling and user-friendly output.

## Core Requirements

### Explicit Requirements

**Auto-Detection & Lifecycle Management**:
- Automatically detect vibesbox container state (running/stopped/missing) during devcontainer startup
- Start stopped containers without user intervention
- Interactive build confirmation when container is missing (with configurable auto-build override)
- Use docker compose commands for all lifecycle operations (build, start, stop, restart)

**Health Verification**:
- Multi-layer health checks: container running → VNC server ready → screenshot capability working
- Poll with configurable timeout (30s default)
- Validate full stack before declaring "ready"
- Test VNC display accessibility using xdpyinfo
- Test screenshot capability using ImageMagick import command

**CLI Helper Functions**:
- User-accessible commands: status, start, stop, restart, logs, vnc
- Exported to user shell via /etc/profile.d
- Consistent colored output using ANSI codes (info/success/warn/error)
- Real-time status messages during operations

**Error Handling & UX**:
- Graceful degradation - devcontainer continues if vibesbox fails (non-blocking startup)
- Comprehensive error handling with `set -euo pipefail`
- Actionable error messages with troubleshooting steps
- Progress indicators during long operations (build, startup)
- Step indicators: `[1/5] Creating network...`
- Time estimates: `[00:45] Building containers (60-120s)...`

**Network Management**:
- Ensure vibes-network exists before vibesbox operations
- Idempotent network creation (check-before-create)
- Handle network already exists scenario
- Verify subnet matches expected configuration

### Implicit Requirements

**Modularity & Maintainability**:
- Scripts are modular and single-purpose
- Helper functions defined at top of files
- Source helper functions in all scripts for consistent output
- ASCII art headers for section organization

**Configuration Management**:
- Environment variables for customization (network name, container name, VNC port, timeouts)
- No separate config file - use environment variables
- Provide .env.example file with all configurable options

**Testing & Validation**:
- Scripts must be idempotent (run multiple times safely)
- ShellCheck validation for all bash scripts
- Test full lifecycle: missing → build → start → health check → ready
- Test state transitions: stopped → start, running → already running

**Integration with Existing DevContainer**:
- Integration point: devcontainer.json `postCreateCommand` hook
- Call from existing `.devcontainer/scripts/postCreate.sh`
- Use existing helper functions from postCreate.sh for consistent UX
- Don't break existing devcontainer functionality

**Security Considerations**:
- Document privileged container requirement for systemd
- Add security mitigations: `no-new-privileges:true`
- Use Docker secrets for VNC password (not environment variables)
- Bind VNC to localhost only (access via SSH tunnel)

## Technical Components

### Data Models

**Container State Enumeration**:
- States: `missing`, `created`, `running`, `paused`, `exited`, `restarting`, `dead`
- State detection using: `docker inspect --format '{{.State.Status}}' container_name`
- State transitions: missing → build → created → running

**Health Status Model**:
- Container health: Boolean (running/stopped)
- VNC health: Boolean (port accessible)
- Display health: Boolean (DISPLAY variable works with xdpyinfo)
- Screenshot health: Boolean (ImageMagick import works)
- Overall health: All four checks must pass

**Configuration Model**:
```bash
# Network configuration
VIBESBOX_NETWORK=${VIBESBOX_NETWORK:-vibes-network}

# Container configuration
VIBESBOX_CONTAINER_NAME=${VIBESBOX_CONTAINER_NAME:-mcp-vibesbox-server}
VIBESBOX_VNC_PORT=${VIBESBOX_VNC_PORT:-5901}
VIBESBOX_DOCKER_PORT=${VIBESBOX_DOCKER_PORT:-2375}

# Paths
VIBES_PATH=${VIBES_PATH:-/workspace/vibes}
COMPOSE_FILE=${VIBESBOX_COMPOSE_FILE:-/workspace/vibes/mcp/mcp-vibesbox-server/docker-compose.yml}

# Behavior
VIBESBOX_AUTO_BUILD=${VIBESBOX_AUTO_BUILD:-false}
VIBESBOX_HEALTH_TIMEOUT=${VIBESBOX_HEALTH_TIMEOUT:-30}
VIBESBOX_BUILD_TIMEOUT=${VIBESBOX_BUILD_TIMEOUT:-300}

# X11/VNC
DISPLAY=${DISPLAY:-:1}
VNC_PASSWORD=${VNC_PASSWORD:-/run/secrets/vnc_password}
```

### External Integrations

**Docker CLI**:
- Container state detection: `docker ps -a --filter name=X --format '{{.Status}}'`
- Container inspection: `docker inspect --format '{{.State.Status}}' X`
- Network management: `docker network ls`, `docker network create`, `docker network inspect`
- Commands: `docker ps`, `docker inspect`, `docker logs`

**Docker Compose**:
- Version requirement: 2.30.0+ (for lifecycle hooks)
- Compose file location: `/workspace/vibes/mcp/mcp-vibesbox-server/docker-compose.yml`
- Commands: `docker compose up -d`, `docker compose start`, `docker compose stop`, `docker compose restart`, `docker compose logs`, `docker compose down`
- Key distinction: `up` creates containers, `start` only starts existing

**TigerVNC Server**:
- Display: `:1` (port 5901)
- Check active sessions: `vncserver -list`
- Server runs inside vibesbox container
- Configuration: Managed by vibesbox Dockerfile/systemd

**X11 Display Testing**:
- Tool: `xdpyinfo`
- Test command: `DISPLAY=:1 xdpyinfo`
- Success: Exit code 0 and display info output
- Failure: "Can't open display" error

**ImageMagick**:
- Tool: `import` command
- Test screenshot: `DISPLAY=:1 import -window root /tmp/test.png`
- Verify: Check file exists and size > 0
- Cleanup: Remove test file after validation

**Network Tools**:
- Port check: `nc -z localhost 5901` (netcat)
- Alternative: `lsof -i :5901`
- Alternative: `netstat -tlnp | grep 5901`

### Core Logic

**State Machine Flow**:
```bash
# Phase 1: Detect current state
container_exists=$(docker ps -a --filter name=mcp-vibesbox-server --format '{{.Names}}')
if [ -z "$container_exists" ]; then
    state="missing"
else
    state=$(docker inspect --format '{{.State.Status}}' mcp-vibesbox-server)
fi

# Phase 2: Determine action
case $state in
    missing)
        # Prompt for build or auto-build
        if [ "$VIBESBOX_AUTO_BUILD" = "true" ]; then
            docker compose -f $COMPOSE_FILE up -d --build
        else
            read -p "Build vibesbox? (y/n) " response
            [ "$response" = "y" ] && docker compose -f $COMPOSE_FILE up -d --build
        fi
        ;;
    exited|created)
        # Start stopped container
        docker compose -f $COMPOSE_FILE start
        ;;
    running)
        # Already running, verify health
        echo "Vibesbox already running, verifying health..."
        ;;
    *)
        # Unexpected state
        echo "Warning: Container in unexpected state: $state"
        ;;
esac

# Phase 3: Health verification (if container should be running)
if [ "$state" = "running" ] || [ "$state" = "exited" ]; then
    check_health
fi
```

**Health Check Polling Pattern**:
```bash
check_health() {
    local timeout=${VIBESBOX_HEALTH_TIMEOUT:-30}
    local start_time=$(date +%s)

    # Layer 1: Container running
    while true; do
        container_status=$(docker inspect --format '{{.State.Status}}' mcp-vibesbox-server 2>/dev/null || echo "missing")
        [ "$container_status" = "running" ] && break

        elapsed=$(($(date +%s) - start_time))
        [ $elapsed -ge $timeout ] && return 1
        sleep 1
    done

    # Layer 2: VNC port accessible
    start_time=$(date +%s)
    while true; do
        nc -z localhost 5901 &>/dev/null && break

        elapsed=$(($(date +%s) - start_time))
        [ $elapsed -ge $timeout ] && return 1
        sleep 1
    done

    # Layer 3: Display accessible
    start_time=$(date +%s)
    while true; do
        DISPLAY=:1 xdpyinfo &>/dev/null && break

        elapsed=$(($(date +%s) - start_time))
        [ $elapsed -ge $timeout ] && return 1
        sleep 1
    done

    # Layer 4: Screenshot capability
    DISPLAY=:1 import -window root /tmp/test_screenshot.png &>/dev/null
    local screenshot_result=$?
    rm -f /tmp/test_screenshot.png

    return $screenshot_result
}
```

**Network Idempotent Creation**:
```bash
setup_network() {
    local network_name=${VIBESBOX_NETWORK:-vibes-network}

    # Check if network exists
    if docker network ls --format '{{.Name}}' | grep -q "^${network_name}$"; then
        echo "Network $network_name already exists"

        # Verify subnet matches expected (optional validation)
        # subnet=$(docker network inspect $network_name --format '{{range .IPAM.Config}}{{.Subnet}}{{end}}')
        # echo "Network subnet: $subnet"
    else
        echo "Creating network $network_name..."
        docker network create $network_name || {
            echo "Warning: Failed to create network (may already exist)"
        }
    fi
}
```

### UI/CLI Requirements

**CLI Helper Functions** (exported via /etc/profile.d/vibesbox-cli.sh):

```bash
vibesbox-status() {
    # Show current state, VNC port, display info
}

vibesbox-start() {
    # Start stopped container
}

vibesbox-stop() {
    # Stop running container
}

vibesbox-restart() {
    # Restart container
}

vibesbox-logs() {
    # Show container logs (follow mode)
}

vibesbox-vnc() {
    # Display VNC connection information
}
```

**Output Formatting** (source from existing helper functions):
```bash
# From .devcontainer/scripts/postCreate.sh
info() { echo -e "\033[0;34m[INFO]\033[0m $*"; }
success() { echo -e "\033[0;32m[SUCCESS]\033[0m $*"; }
warn() { echo -e "\033[0;33m[WARN]\033[0m $*"; }
error() { echo -e "\033[0;31m[ERROR]\033[0m $*"; }
```

**Progress Indicators**:
```bash
# Spinner for long operations
show_spinner() {
    local pid=$1
    local delay=0.1
    local spinstr='|/-\'
    while ps -p $pid > /dev/null; do
        local temp=${spinstr#?}
        printf " [%c]  " "$spinstr"
        spinstr=$temp${spinstr%"$temp"}
        sleep $delay
        printf "\b\b\b\b\b\b"
    done
    printf "    \b\b\b\b"
}

# Example usage
docker compose up -d &
show_spinner $!
```

## Similar Implementations Found in Archon

### 1. Pydantic AI MCP Server Lifecycle
- **Relevance**: 7/10
- **Archon ID**: c0e629a894699314
- **Key Patterns**:
  - Agent context manager pattern for lifecycle: `async with agent:` starts MCP server subprocess
  - Exit stack management for cleanup
  - Enter/exit reference counting for nested contexts
  - Timeout handling during server startup
- **Applicable Pattern**:
  ```python
  async with AsyncExitStack() as exit_stack:
      toolset = self._get_toolset()
      await exit_stack.enter_async_context(toolset)
      self._exit_stack = exit_stack.pop_all()
  ```
- **Translation to Bash**:
  - Use trap for cleanup on script exit
  - Store PIDs for subprocess management
  - Implement timeout using background processes and wait
- **Gotchas**: None specific to this implementation
- **What to Reuse**: Context manager pattern (enter → do work → exit), reference counting for nested calls

### 2. Agent Hooks & Lifecycle Events
- **Relevance**: 6/10
- **Archon ID**: 9a7d4217c64c9a0a
- **Key Patterns**:
  - PreToolUse and PostToolUse hooks for lifecycle events
  - Event-driven architecture for state transitions
  - Hook registration and execution pattern
- **Applicable Pattern**:
  - Could implement pre/post hooks for devcontainer lifecycle
  - Example: pre_vibesbox_start, post_vibesbox_health_check
- **What to Skip**: Too complex for bash scripting context
- **Gotchas**: None

### 3. No Direct Docker/Devcontainer PRPs Found
- Archon search did not return existing devcontainer or Docker lifecycle management PRPs
- This is a novel integration pattern for this codebase
- Will rely on extracted code examples and official documentation

## Recommended Technology Stack

Based on INITIAL.md research and extracted examples:

### Core Technologies
- **Shell**: Bash 5.0+ (set -euo pipefail strict mode)
- **Container Runtime**: Docker Engine 27.0+ (for compose lifecycle hooks)
- **Orchestration**: Docker Compose 2.30.0+
- **VNC Server**: TigerVNC 1.14.0+ (running in vibesbox)
- **Display Testing**: xdpyinfo (X11-utils package)
- **Screenshot Tool**: ImageMagick 7.x (import command)

### Development Tools
- **Linting**: ShellCheck for bash validation
- **Testing**: Manual integration tests (idempotency checks)
- **Documentation**: Inline comments + ASCII headers

### Integration Points
- **VS Code Dev Containers**: devcontainer.json (postCreateCommand hook)
- **Existing Scripts**: `.devcontainer/scripts/postCreate.sh` (calls ensure-vibesbox.sh)
- **Profile Integration**: `/etc/profile.d/vibesbox-cli.sh` (CLI helpers)

### Libraries/Utilities
- **Docker CLI**: Container state detection, inspection
- **Docker Compose CLI**: Lifecycle management (up, start, stop, restart, logs)
- **netcat**: Port availability checking (nc -z localhost 5901)
- **coreutils**: date, sleep, timeout for polling

## Assumptions Made

### 1. **Devcontainer Environment**
- **Assumption**: User is running VS Code with Dev Containers extension
- **Reasoning**: Feature is specifically for devcontainer integration
- **Source**: INITIAL.md requirement "integrated into VS Code devcontainer"
- **Impact**: Scripts assume devcontainer environment variables and paths

### 2. **Docker Socket Access**
- **Assumption**: Devcontainer has Docker socket mounted (`/var/run/docker.sock`)
- **Reasoning**: Required to manage vibesbox container from inside devcontainer
- **Source**: Common devcontainer pattern for Docker-in-Docker
- **Impact**: Scripts will fail if socket not available (should check and provide actionable error)

### 3. **Vibesbox Compose File Location**
- **Assumption**: Compose file at `/workspace/vibes/mcp/mcp-vibesbox-server/docker-compose.yml`
- **Reasoning**: Extracted from vibesbox-docker-compose.yml example
- **Source**: examples/devcontainer_vibesbox_integration/vibesbox-docker-compose.yml
- **Impact**: Hardcoded path (made configurable via environment variable)

### 4. **Network Name Consistency**
- **Assumption**: Network is always named `vibes-network`
- **Reasoning**: Existing setup-network.sh creates this network
- **Source**: Codebase pattern from .devcontainer/scripts/setup-network.sh
- **Impact**: Made configurable via `VIBESBOX_NETWORK` environment variable

### 5. **VNC Display Number**
- **Assumption**: VNC server uses display `:1` (port 5901)
- **Reasoning**: Standard VNC convention (`:0` is physical display, `:1` is first VNC)
- **Source**: TigerVNC documentation, vibesbox configuration
- **Impact**: Hardcoded in health checks (DISPLAY=:1)

### 6. **Timeout Values**
- **Assumption**: 30 seconds is sufficient for health checks, 300 seconds for builds
- **Reasoning**: Based on typical container startup and build times
- **Source**: Best practice for containerized services
- **Impact**: Made configurable via environment variables (VIBESBOX_HEALTH_TIMEOUT, VIBESBOX_BUILD_TIMEOUT)

### 7. **ImageMagick Availability**
- **Assumption**: ImageMagick is installed in devcontainer
- **Reasoning**: Required for screenshot testing
- **Source**: Vibesbox uses ImageMagick for screenshots
- **Impact**: Should check with `command -v import` and provide install instructions if missing

### 8. **Netcat Availability**
- **Assumption**: netcat (nc) is available for port checking
- **Reasoning**: Common Unix utility
- **Source**: Standard container troubleshooting tool
- **Impact**: Fallback to other methods if not available (curl, telnet, /dev/tcp)

### 9. **User Interaction During Build**
- **Assumption**: User is present during devcontainer creation to respond to build prompt
- **Reasoning**: postCreateCommand runs during container creation (user is watching)
- **Source**: VS Code devcontainer behavior
- **Impact**: Provide auto-build flag for CI/CD scenarios (VIBESBOX_AUTO_BUILD=true)

### 10. **Non-Blocking Failure Requirement**
- **Assumption**: Devcontainer should continue working even if vibesbox fails
- **Reasoning**: Vibesbox is optional enhancement, not core dependency
- **Source**: INITIAL.md "graceful degradation" requirement
- **Impact**: All vibesbox scripts must handle errors gracefully and not exit 1 on failure

### 11. **Privileged Container Acceptance**
- **Assumption**: User accepts security implications of privileged vibesbox container
- **Reasoning**: Required for systemd inside container
- **Source**: Existing vibesbox docker-compose.yml
- **Impact**: Document security considerations, add mitigation layers

### 12. **Single Vibesbox Instance**
- **Assumption**: Only one vibesbox container per host
- **Reasoning**: Simplifies state management
- **Source**: Not explicitly stated, but container name is hardcoded
- **Impact**: Future enhancement could support multiple instances with name prefix

## Success Criteria

### Functional Requirements
- ✅ Devcontainer opens → vibesbox automatically detected → auto-started if stopped → health verified → VNC accessible
- ✅ Developer can immediately use GUI automation (DISPLAY=:1 works)
- ✅ No manual intervention required for common scenarios (stopped container)
- ✅ Interactive prompt for missing container (with auto-build option)

### Non-Functional Requirements
- ✅ Status is clear at all times (informative output with colors)
- ✅ Failures are non-blocking with actionable error messages
- ✅ Scripts are idempotent (can run multiple times safely)
- ✅ All bash scripts pass ShellCheck validation
- ✅ Health checks complete within 30 seconds (configurable)
- ✅ Build operations show progress indicators

### User Experience
- ✅ CLI helpers available immediately: vibesbox-status, vibesbox-start, etc.
- ✅ Colored output for visual clarity (blue info, green success, yellow warn, red error)
- ✅ VNC connection information displayed after successful startup
- ✅ Error messages include troubleshooting steps
- ✅ Progress indicators during long operations (build, health checks)

### Integration
- ✅ Works with existing devcontainer setup (doesn't break current functionality)
- ✅ Uses existing helper functions from postCreate.sh
- ✅ Network setup integrates with existing setup-network.sh
- ✅ Can be toggled on/off via environment variable

### Validation Gates
- ✅ Container state detection works for all states (missing, stopped, running)
- ✅ Health checks pass all four layers (container, VNC port, display, screenshot)
- ✅ Network creation is idempotent
- ✅ CLI helpers work from user shell
- ✅ Graceful degradation works (devcontainer continues if vibesbox fails)

## Next Steps for Downstream Agents

### Codebase Researcher
Focus on:
- Existing helper function patterns in `.devcontainer/scripts/postCreate.sh`
- Network setup patterns in `.devcontainer/scripts/setup-network.sh`
- Docker testing patterns in `.devcontainer/scripts/test-docker.sh`
- Naming conventions for devcontainer scripts
- Integration patterns with devcontainer.json

Search for:
- `grep -r "set -euo pipefail" .devcontainer/scripts/` - Error handling pattern
- `grep -r "function.*info\|success\|warn\|error" .devcontainer/scripts/` - Output helpers
- `grep -r "docker.*network" .devcontainer/scripts/` - Network management
- `grep -r "postCreateCommand" .devcontainer/` - Lifecycle hook usage

### Documentation Hunter
Find docs for:
- VS Code devcontainer lifecycle hooks (postCreateCommand, postStartCommand, postAttachCommand)
- Docker Compose v2.30.0+ lifecycle hooks (post_start, pre_stop)
- Docker CLI container state values and inspection
- TigerVNC server configuration and display management
- ImageMagick import command for screenshot capture
- Bash strict mode (set -euo pipefail) best practices

Priority sources (already in INITIAL.md):
- https://code.visualstudio.com/docs/devcontainers/create-dev-container
- https://docs.docker.com/compose/how-tos/lifecycle/
- https://docs.docker.com/reference/cli/docker/container/ls/
- https://imagemagick.org/script/import.php

### Example Curator
Extract examples showing:
- State machine implementation in bash (container state detection and transitions)
- Polling with timeout pattern (health check loops)
- Progress indicators and spinners in bash
- Docker Compose lifecycle management (up vs start distinction)
- Idempotent operations (network creation, container startup)
- CLI function export via /etc/profile.d

Already extracted (use these):
- `examples/devcontainer_vibesbox_integration/helper-functions.sh` - Colored output
- `examples/devcontainer_vibesbox_integration/container-state-detection.sh` - State machine
- `examples/devcontainer_vibesbox_integration/polling-with-timeout.sh` - Health polling
- `examples/devcontainer_vibesbox_integration/network-setup.sh` - Idempotent network
- `examples/devcontainer_vibesbox_integration/docker-health-check.sh` - Multi-layer validation

### Gotcha Detective
Investigate:
- Container name conflicts (multiple devcontainers)
- VNC port conflicts (port 5901 already in use)
- VNC display race condition (x11vnc starts before Xvfb ready)
- postCreateCommand silent failures (errors don't stop container startup)
- Docker network already exists with different subnet
- Missing dependencies in postCreateCommand (docker-compose not installed)
- Cryptic error messages (need user-friendly translations)
- Container already running (docker compose up fails)
- DISPLAY variable not set (screenshot capture fails)
- docker compose start vs up (start doesn't create containers)

Already documented (18 gotchas in INITIAL.md):
- All above gotchas have solutions documented
- Security considerations (privileged container, VNC auth, Docker socket)
- Performance considerations (startup race conditions, resource limits, build cache)

### Key Integration Points

**File Locations**:
- New files:
  - `.devcontainer/scripts/ensure-vibesbox.sh` - Main lifecycle management
  - `.devcontainer/scripts/check-vibesbox.sh` - Health checking utility
  - `/etc/profile.d/vibesbox-cli.sh` - CLI helper functions
- Modified files:
  - `.devcontainer/scripts/postCreate.sh` - Add call to ensure-vibesbox.sh
  - `.devcontainer/devcontainer.json` - Already has postCreateCommand hook

**Environment Variables**:
- Create `.env.example` in vibes root with all configurable options
- Document in README how to customize behavior

**Testing Strategy**:
- Integration tests: Run full lifecycle in clean environment
- Idempotency tests: Run scripts multiple times, verify state
- State transition tests: Test all state paths (missing → running, stopped → running, etc.)
- Failure tests: Simulate failures (network down, port conflict, timeout)
- ShellCheck validation: All bash scripts must pass

**Documentation Updates**:
- Update main README with vibesbox integration section
- Document CLI helper functions
- Document environment variables
- Document troubleshooting steps

---

## Quality Metrics

**INITIAL.md Analysis**:
- Quality score: 9.5/10
- Examples extracted: 6 code files
- Documentation sources: 28 URLs
- Gotchas documented: 18 with solutions
- Research documents synthesized: 5

**Feature Analysis Completeness**:
- ✅ Requirements extracted (explicit and implicit)
- ✅ Technical components identified
- ✅ Archon search performed (limited relevant results)
- ✅ Similar implementations analyzed
- ✅ Technology stack defined
- ✅ Assumptions documented (12 assumptions with reasoning)
- ✅ Success criteria clearly defined
- ✅ Next steps specific and actionable
- ✅ Integration points documented

**Readiness for PRP Generation**:
- ✅ Complete context for implementation
- ✅ All external dependencies identified
- ✅ All integration points documented
- ✅ Clear validation criteria
- ✅ Comprehensive gotcha catalog
- ✅ Code examples available for reference

**Estimated PRP Generation Time**: <10 minutes (parallel research phases)
**Estimated Implementation Time**: 3-5 hours (includes testing and validation)

---

**Generated**: 2025-10-04
**Archon Project ID**: 96623e6d-eaa2-4325-beee-21e605255c32
**Source INITIAL.md**: prps/INITIAL_devcontainer_vibesbox_integration.md
**Lines**: 879
**Feature Complexity**: Medium-High (state machine, multi-layer health checks, user interaction)
