# Codebase Patterns: devcontainer_vibesbox_integration

## Overview

Extracted bash scripting patterns, Docker lifecycle management, and devcontainer integration approaches from existing `.devcontainer/scripts/` and example files. These patterns emphasize idempotent operations, graceful degradation, colored CLI output, and multi-layer health validation. All patterns follow strict error handling (`set -euo pipefail`) and provide user-friendly feedback with ANSI colors and Unicode symbols.

## Architectural Patterns

### Pattern 1: Colored CLI Helper Functions
**Source**: `.devcontainer/scripts/postCreate.sh` (lines 8-12)
**Relevance**: 10/10
**What it does**: Provides consistent colored terminal output with severity-coded messages using ANSI escape codes and Unicode symbols.

**Key Techniques**:
```bash
#── helper for colored output ───────────────────────────────────────
info()    { printf "\033[36mℹ [INFO]\033[0m  %s\n" "$*"; }
success() { printf "\033[32m✔ [OK]\033[0m    %s\n" "$*"; }
warn()    { printf "\033[33m⚠ [WARN]\033[0m  %s\n" "$*"; }
error()   { printf "\033[31m✖ [ERROR]\033[0m %s\n" "$*"; }
```

**When to use**:
- Every script that provides user feedback
- Status messages during vibesbox lifecycle operations
- Health check result reporting
- Error messaging with clear severity levels

**How to adapt**:
- Source these functions at the top of all vibesbox scripts
- Use `info()` for status updates (checking, starting, waiting)
- Use `success()` when operations complete successfully
- Use `warn()` for non-critical issues (graceful degradation scenarios)
- Use `error()` for failures requiring user intervention

**Why this pattern**:
- Creates professional, scannable CLI output
- Color-coding allows quick identification of issues
- Consistent formatting across all scripts improves UX
- Unicode symbols (ℹ ✔ ⚠ ✖) work across terminal emulators
- Already established in codebase, ensures consistency

### Pattern 2: Idempotent Network Creation
**Source**: `.devcontainer/scripts/setup-network.sh`
**Relevance**: 10/10
**What it does**: Creates Docker networks with check-before-create logic, handles "already exists" errors gracefully, making operations safe to run multiple times.

**Key Techniques**:
```bash
# Check if vibes-network exists
if docker network ls | grep -q "vibes-network"; then
    echo "✅ vibes-network already exists"
else
    echo "⚠️  vibes-network not found, creating it..."
    if docker network create vibes-network 2>/dev/null; then
        echo "✅ Created vibes-network"
    else
        echo "❌ Failed to create vibes-network (might already exist)"
    fi
fi
```

**When to use**:
- Before starting vibesbox container (network prerequisite)
- In ensure-vibesbox.sh initialization phase
- Any time Docker resources need conditional creation
- Scripts that may run multiple times (devcontainer rebuild)

**How to adapt**:
- Make network name configurable: `${VIBESBOX_NETWORK:-vibes-network}`
- Add network validation: check subnet matches expected config
- Integrate into ensure-vibesbox.sh as Phase 1 (before container operations)
- Add to CLI helper: `vibesbox-network-setup` for manual troubleshooting

**Why this pattern**:
- Idempotency crucial for devcontainer lifecycle (multiple postCreateCommand runs)
- Prevents script failures on re-execution
- Graceful error handling improves robustness
- Network is external prerequisite for vibesbox, must exist before `docker compose up`

### Pattern 3: Container State Detection State Machine
**Source**: `examples/devcontainer_vibesbox_integration/container-state-detection.sh`
**Relevance**: 10/10
**What it does**: Implements a state machine for detecting and classifying container lifecycle states, enabling automated decision-making for start/stop/restart operations.

**Key Techniques**:
```bash
# Helper functions for state detection
container_exists() {
    docker ps -a --format '{{.Names}}' | grep -q "^${CONTAINER_NAME}$"
}

container_running() {
    docker ps --format '{{.Names}}' | grep -q "^${CONTAINER_NAME}$"
}

get_container_status() {
    docker inspect --format '{{.State.Status}}' "$CONTAINER_NAME" 2>/dev/null
}

# Main state detection logic
detect_vibesbox_state() {
    if ! container_exists; then
        echo "missing"
    elif container_running; then
        echo "running"
    else
        local status=$(get_container_status)
        echo "stopped-${status}"
    fi
}

# State-based action dispatch
STATE=$(detect_vibesbox_state)
case "$STATE" in
    missing)
        # Trigger build workflow
        ;;
    stopped-*)
        # docker compose start
        ;;
    running)
        # Proceed to health checks
        ;;
esac
```

**When to use**:
- Beginning of ensure-vibesbox.sh to determine action
- CLI helpers (vibesbox-status, vibesbox-start)
- Automated lifecycle management during postCreateCommand
- Health monitoring scripts

**How to adapt**:
- Add VNC-specific states: `running-vnc-ready`, `running-vnc-failed`
- Extend with screenshot capability detection
- Create detailed sub-states for troubleshooting
- Return structured data for CLI tools to parse

**Why this pattern**:
- State machine provides clear action dispatch logic
- Small helper functions are testable and reusable
- `docker inspect` provides authoritative state information
- Case statement enables easy extension for new states
- Separates detection from action (single responsibility)

### Pattern 4: Polling with Timeout for Async Operations
**Source**: `examples/devcontainer_vibesbox_integration/polling-with-timeout.sh`
**Relevance**: 10/10
**What it does**: Generic polling function that waits for async conditions (container startup, service readiness) with configurable timeouts and progress indicators.

**Key Techniques**:
```bash
wait_for_condition() {
    local condition_func="$1"
    local timeout_seconds="${2:-30}"
    local check_interval="${3:-2}"
    local description="${4:-condition}"

    local elapsed=0

    echo "⏳ Waiting for $description (timeout: ${timeout_seconds}s)..."

    while [ $elapsed -lt $timeout_seconds ]; do
        if $condition_func; then
            echo "✅ $description ready (${elapsed}s elapsed)"
            return 0
        fi

        sleep "$check_interval"
        elapsed=$((elapsed + check_interval))
        echo -n "."
    done

    echo ""
    echo "❌ Timeout waiting for $description (${timeout_seconds}s elapsed)"
    return 1
}

# Example condition functions
vnc_port_ready() {
    nc -z localhost 5901 2>/dev/null
}

# Chained health checks
if wait_for_condition container_running 30 2 "container startup"; then
    if wait_for_condition vnc_port_ready 30 2 "VNC server"; then
        echo "🎉 Vibesbox fully operational!"
    fi
fi
```

**When to use**:
- After `docker compose up -d` to wait for container readiness
- VNC server startup verification
- Multi-layer health check orchestration
- Any async operation that needs timeout protection

**How to adapt**:
- Create vibesbox-specific condition functions:
  - `vibesbox_container_running()`
  - `vibesbox_vnc_ready()`
  - `vibesbox_display_accessible()` (xdpyinfo test)
  - `vibesbox_screenshot_works()` (ImageMagick test)
- Make timeouts environment-configurable: `${VIBESBOX_HEALTH_TIMEOUT:-30}`
- Add verbosity control for progress dots
- Integrate into ensure-vibesbox.sh health check phase

**Why this pattern**:
- Generic function is highly reusable across different health checks
- Configurable timeouts prevent indefinite hangs
- Progress indicators provide user feedback during waits
- Early exit on success optimizes check time
- Chaining allows multi-layer validation (container → VNC → screenshot)
- Return codes enable error handling in calling scripts

### Pattern 5: Multi-Layer Docker Health Validation
**Source**: `examples/devcontainer_vibesbox_integration/docker-health-check.sh`
**Relevance**: 9/10
**What it does**: Progressive validation pattern that checks Docker ecosystem at multiple layers (CLI → daemon → socket → permissions), providing actionable diagnostics at each level.

**Key Techniques**:
```bash
# Layer 1: CLI availability
if command -v docker &>/dev/null; then
    echo "✅ Docker CLI found: $(which docker)"

    # Layer 2: Daemon connectivity
    if docker info &>/dev/null; then
        echo "✅ Docker daemon accessible"
        echo "  Container runtime: $(docker info --format '{{.ServerVersion}}')"
    else
        echo "❌ Docker daemon not accessible"
    fi

    # Layer 3: Socket permissions
    if ls -la /var/run/docker.sock &>/dev/null; then
        if [ -w /var/run/docker.sock ]; then
            echo "✅ Docker socket is writable"
        else
            echo "⚠️  Docker socket is not writable - check group membership"
        fi
    fi
else
    echo "❌ Docker CLI not found"
fi
```

**When to use**:
- Vibesbox health check script (check-vibesbox.sh)
- Troubleshooting helper (vibesbox-diagnose)
- Pre-flight checks before starting container
- Post-start verification

**How to adapt for Vibesbox**:
- Replace layers with vibesbox-specific checks:
  - Layer 1: Container exists (docker ps -a | grep vibesbox)
  - Layer 2: Container running (docker ps | grep vibesbox)
  - Layer 3: VNC port accessible (nc -z localhost 5901)
  - Layer 4: X11 display working (DISPLAY=:1 xdpyinfo)
  - Layer 5: Screenshot capability (ImageMagick import test)
- Continue checking even if early layers fail (diagnostic completeness)
- Provide actionable error messages at each layer
- Return aggregated health score (5/5 checks passed)

**Why this pattern**:
- Progressive validation isolates failure points
- Non-blocking checks provide complete diagnostic picture
- Each layer targets specific potential failure
- Informative output aids troubleshooting
- Pattern scales well to multi-layer systems (like VNC stack)

## Naming Conventions

### File Naming
**Pattern**: `{action}-{target}.sh` for action scripts, `{feature}.sh` for utilities
**Examples**:
- `postCreate.sh` - Lifecycle hook script
- `setup-network.sh` - Network setup utility
- `test-docker.sh` - Docker validation script
- `test-network.sh` - Network connectivity test

**For Vibesbox**:
- `ensure-vibesbox.sh` - Main lifecycle management (auto-start, health checks)
- `check-vibesbox.sh` - Health check utility (callable separately)
- `vibesbox-cli.sh` - CLI helper functions (sourced via /etc/profile.d/)

### Function Naming
**Pattern**: `{verb}_{noun}` for actions, `{noun}_{adjective}` for state checks
**Examples**:
- `container_exists()` - State check
- `container_running()` - State check
- `get_container_status()` - Getter
- `wait_for_condition()` - Action function
- `detect_vibesbox_state()` - State detection

**For Vibesbox**:
- `vibesbox_exists()`, `vibesbox_running()` - State checks
- `ensure_network()` - Setup function
- `wait_for_vnc()` - Polling function
- `check_screenshot_capability()` - Validation function
- CLI helpers: `vibesbox-status`, `vibesbox-start`, `vibesbox-logs` (dash-separated for shell commands)

### Variable Naming
**Pattern**: `UPPERCASE_WITH_UNDERSCORES` for environment variables, `lowercase_with_underscores` for local variables
**Examples**:
```bash
# Environment variables (configurable)
VIBESBOX_NETWORK="${VIBESBOX_NETWORK:-vibes-network}"
VIBESBOX_CONTAINER_NAME="${VIBESBOX_CONTAINER_NAME:-mcp-vibesbox-server}"
VIBESBOX_HEALTH_TIMEOUT="${VIBESBOX_HEALTH_TIMEOUT:-30}"

# Local variables (script-scoped)
local container_state=""
local elapsed=0
local timeout_seconds="${2:-30}"
```

## File Organization

### Directory Structure
```
.devcontainer/
├── devcontainer.json                  # Main config (postCreateCommand hook)
├── docker-compose.yml                 # Devcontainer service definition
└── scripts/
    ├── postCreate.sh                  # Main lifecycle hook (calls ensure-vibesbox.sh)
    ├── ensure-vibesbox.sh             # NEW: Vibesbox lifecycle management
    ├── check-vibesbox.sh              # NEW: Health check utility
    ├── setup-network.sh               # Existing: Network setup (reused)
    ├── test-docker.sh                 # Existing: Docker validation
    └── test-network.sh                # Existing: Network validation

/etc/profile.d/
└── vibesbox-cli.sh                    # NEW: CLI helper functions

mcp/mcp-vibesbox-server/
├── docker-compose.yml                 # Vibesbox container definition
├── Dockerfile                         # Vibesbox image build
└── server.py                          # MCP server implementation
```

**Justification**:
- All devcontainer scripts in `.devcontainer/scripts/` (established pattern)
- Vibesbox-specific scripts isolated but co-located with lifecycle hooks
- CLI helpers in `/etc/profile.d/` for automatic shell sourcing
- Separation of concerns: `ensure-vibesbox.sh` (orchestration) vs `check-vibesbox.sh` (validation)

## Common Utilities to Leverage

### 1. Existing Helper Functions
**Location**: `.devcontainer/scripts/postCreate.sh` (lines 8-12)
**Purpose**: Colored terminal output for consistent UX
**Usage Example**:
```bash
# Source at top of every vibesbox script
source "$(dirname "$0")/postCreate.sh"  # or define inline

info "Starting vibesbox container..."
if docker compose up -d; then
    success "Vibesbox started successfully"
else
    error "Failed to start vibesbox - check logs"
fi
```

### 2. Network Setup Pattern
**Location**: `.devcontainer/scripts/setup-network.sh`
**Purpose**: Idempotent vibes-network creation
**Usage Example**:
```bash
# Call before vibesbox operations in ensure-vibesbox.sh
info "Ensuring vibes-network exists..."
bash /usr/local/share/setup-network.sh
```

### 3. Docker Compose CLI
**Location**: System-wide (`docker compose` command)
**Purpose**: Container lifecycle management
**Usage Example**:
```bash
COMPOSE_FILE="/workspace/vibes/mcp/mcp-vibesbox-server/docker-compose.yml"

# Start (or create and start)
docker compose -f "$COMPOSE_FILE" up -d

# Start existing stopped container
docker compose -f "$COMPOSE_FILE" start

# Stop container
docker compose -f "$COMPOSE_FILE" stop

# Restart container
docker compose -f "$COMPOSE_FILE" restart

# View logs
docker compose -f "$COMPOSE_FILE" logs -f
```
**Key Distinction**: Use `up -d` for initial build/create, `start` for resuming stopped containers.

### 4. Docker Inspect for State Detection
**Location**: System-wide (`docker inspect` command)
**Purpose**: Authoritative container state information
**Usage Example**:
```bash
# Get container status (running, exited, paused, etc.)
STATUS=$(docker inspect --format '{{.State.Status}}' mcp-vibesbox-server 2>/dev/null)

# Get health check status (if defined in Dockerfile)
HEALTH=$(docker inspect --format '{{.State.Health.Status}}' mcp-vibesbox-server 2>/dev/null)

# Check if container exists (exit code)
if docker inspect mcp-vibesbox-server &>/dev/null; then
    echo "Container exists"
fi
```

### 5. netcat (nc) for Port Checking
**Location**: System-wide (should be in devcontainer)
**Purpose**: Test if VNC port is accessible
**Usage Example**:
```bash
# Check if VNC server is listening on port 5901
if nc -z localhost 5901 2>/dev/null; then
    echo "VNC port accessible"
else
    echo "VNC port not accessible"
fi
```
**Fallback**: If nc not available, use: `timeout 1 bash -c "</dev/tcp/localhost/5901" 2>/dev/null`

### 6. xdpyinfo for X11 Display Testing
**Location**: Should be installed in devcontainer
**Purpose**: Verify X11 display is accessible
**Usage Example**:
```bash
# Test if DISPLAY :1 is accessible
if docker exec mcp-vibesbox-server sh -c "DISPLAY=:1 xdpyinfo" &>/dev/null; then
    echo "X11 display accessible"
else
    echo "X11 display not accessible"
fi
```

### 7. ImageMagick (import) for Screenshot Testing
**Location**: Should be installed in devcontainer (or call via docker exec)
**Purpose**: Test screenshot capability as final health check
**Usage Example**:
```bash
# Test screenshot capture from vibesbox container
TEST_FILE="/tmp/vibesbox-health-check.png"
if docker exec mcp-vibesbox-server sh -c "DISPLAY=:1 import -window root $TEST_FILE" &>/dev/null; then
    # Verify file exists and has size > 0
    if docker exec mcp-vibesbox-server sh -c "[ -s $TEST_FILE ]" &>/dev/null; then
        echo "Screenshot capability verified"
        docker exec mcp-vibesbox-server rm -f "$TEST_FILE"  # Cleanup
    fi
fi
```

## Testing Patterns

### Unit Test Structure
**Pattern**: Idempotency testing - run script multiple times, verify consistent results
**Example**: Test ensure-vibesbox.sh
**Key techniques**:
- Run 1: Container missing → builds and starts
- Run 2: Container running → no action, health checks pass
- Run 3: Container stopped → starts without rebuilding
- Run 4: Network missing → creates network, starts container

**Fixture Pattern**:
```bash
# test_ensure_vibesbox.sh
setup() {
    # Clean slate
    docker compose -f "$COMPOSE_FILE" down
    docker network rm vibes-network 2>/dev/null || true
}

test_missing_container() {
    setup
    bash ensure-vibesbox.sh
    # Assert: container exists and running
    container_running || exit 1
}

test_stopped_container() {
    setup
    docker compose up -d
    docker compose stop
    bash ensure-vibesbox.sh
    # Assert: container restarted
    container_running || exit 1
}

test_already_running() {
    setup
    docker compose up -d
    bash ensure-vibesbox.sh
    # Assert: no errors, health checks pass
}
```

### Integration Test Structure
**Pattern**: Full lifecycle test - devcontainer creation → vibesbox auto-start → health verification
**Example**: Test complete postCreateCommand flow
**Key techniques**:
```bash
# test_devcontainer_integration.sh
test_full_lifecycle() {
    # Simulate devcontainer creation
    bash postCreate.sh

    # Assert: vibesbox running
    [ "$(docker inspect --format '{{.State.Status}}' mcp-vibesbox-server)" = "running" ] || exit 1

    # Assert: VNC accessible
    nc -z localhost 5901 || exit 1

    # Assert: CLI helpers available
    type vibesbox-status &>/dev/null || exit 1
}
```

### Validation Pattern: ShellCheck
**Pattern**: Static analysis for bash scripts
**Tool**: ShellCheck (https://www.shellcheck.net/)
**Usage**:
```bash
# Run on all vibesbox scripts
shellcheck .devcontainer/scripts/ensure-vibesbox.sh
shellcheck .devcontainer/scripts/check-vibesbox.sh
shellcheck /etc/profile.d/vibesbox-cli.sh

# Common issues to fix:
# - SC2086: Quote variables to prevent word splitting
# - SC2164: Use 'cd ... || exit' for safe directory changes
# - SC2155: Declare and assign separately to avoid masking return values
```

## Anti-Patterns to Avoid

### 1. Blocking Devcontainer Startup on Vibesbox Failure
**What it is**: Using `set -e` or `exit 1` when vibesbox operations fail, causing devcontainer creation to abort
**Why to avoid**: Vibesbox is an enhancement, not a core dependency - devcontainer should work without it
**Found in**: Could happen if we're not careful in ensure-vibesbox.sh
**Better approach**:
```bash
# BAD: Blocks devcontainer
set -euo pipefail
docker compose up -d  # If this fails, script exits, devcontainer fails

# GOOD: Graceful degradation
if docker compose up -d &>/dev/null; then
    success "Vibesbox started"
else
    warn "Vibesbox failed to start - GUI automation unavailable"
    warn "Troubleshoot with: vibesbox-logs"
    # Continue devcontainer setup
fi
```

### 2. Using `docker compose up` for Restarting Stopped Containers
**What it is**: Using `docker compose up -d` when container already exists but is stopped
**Why to avoid**: `up` is for creating containers, `start` is for resuming existing ones. Using `up` can cause port conflicts or unnecessary rebuilds.
**Found in**: Common mistake when not checking container state first
**Better approach**:
```bash
# BAD: Always uses 'up'
docker compose up -d

# GOOD: State-aware command selection
if container_exists; then
    docker compose start  # Resume existing container
else
    docker compose up -d  # Create and start new container
fi
```

### 3. Hardcoding Timeouts Without Configurability
**What it is**: Fixed timeout values (e.g., `sleep 30`) hardcoded in scripts
**Why to avoid**: Different environments have different startup times (local vs CI vs cloud)
**Found in**: Could happen in initial implementation
**Better approach**:
```bash
# BAD: Hardcoded timeout
timeout=30

# GOOD: Environment-configurable with sensible default
timeout="${VIBESBOX_HEALTH_TIMEOUT:-30}"

# BETTER: Document in .env.example
# .env.example:
# VIBESBOX_HEALTH_TIMEOUT=30  # Seconds to wait for health checks
```

### 4. Silent Failures Without User Feedback
**What it is**: Errors suppressed with `2>/dev/null` without informing user
**Why to avoid**: User has no visibility into what went wrong, can't troubleshoot
**Found in**: Could happen when over-using stderr redirection
**Better approach**:
```bash
# BAD: Silent failure
docker compose up -d 2>/dev/null

# GOOD: Capture and report errors
if ! output=$(docker compose up -d 2>&1); then
    error "Failed to start vibesbox:"
    echo "$output" | head -5  # Show first 5 lines of error
    warn "Run 'vibesbox-logs' for full details"
fi
```

### 5. Mixing State Detection Methods
**What it is**: Using different commands inconsistently for checking container state (docker ps, docker inspect, docker-compose ps)
**Why to avoid**: Inconsistent results, harder to debug, redundant code
**Found in**: Likely to happen without clear pattern
**Better approach**:
```bash
# BAD: Mixed methods
if docker ps | grep vibesbox; then ...
if docker inspect vibesbox; then ...
if docker-compose ps | grep running; then ...

# GOOD: Consistent helper functions
container_exists() {
    docker ps -a --format '{{.Names}}' | grep -q "^${CONTAINER_NAME}$"
}

container_running() {
    docker ps --format '{{.Names}}' | grep -q "^${CONTAINER_NAME}$"
}

# All code uses these helpers
if container_running; then ...
```

### 6. Not Cleaning Up Test Resources
**What it is**: Health check creates test files (screenshots) but doesn't remove them
**Why to avoid**: Accumulates junk files, can mask future test failures
**Found in**: Screenshot capability testing
**Better approach**:
```bash
# BAD: No cleanup
docker exec vibesbox sh -c "DISPLAY=:1 import -window root /tmp/test.png"
# test.png left behind

# GOOD: Always cleanup with trap
TEST_FILE="/tmp/vibesbox-health-$$.png"
cleanup() { docker exec vibesbox rm -f "$TEST_FILE" 2>/dev/null || true; }
trap cleanup EXIT

docker exec vibesbox sh -c "DISPLAY=:1 import -window root $TEST_FILE"
# Automatically cleaned up on exit
```

### 7. VNC Display Race Condition
**What it is**: Checking VNC port immediately after container start without polling
**Why to avoid**: VNC server takes time to initialize - check will fail even if VNC is starting
**Found in**: Documented in feature-analysis.md gotchas
**Better approach**:
```bash
# BAD: Immediate check (likely to fail)
docker compose up -d
if nc -z localhost 5901; then ...

# GOOD: Poll with timeout
docker compose up -d
wait_for_condition vnc_port_ready 30 2 "VNC server"
```

## Implementation Hints from Existing Code

### Similar Features Found

1. **Network Setup (setup-network.sh)**:
   - **Similarity**: Prerequisite resource creation for container operations
   - **Lessons**: Check-before-create pattern works well, suppressing expected errors improves UX
   - **Differences**: Vibesbox needs more complex state management (network is simpler)
   - **Reuse**: Call setup-network.sh directly from ensure-vibesbox.sh

2. **Docker Testing (test-docker.sh)**:
   - **Similarity**: Multi-layer validation of Docker ecosystem
   - **Lessons**: Progressive checks with non-blocking failures provide complete diagnostics
   - **Differences**: Docker validation is one-time, vibesbox needs ongoing health monitoring
   - **Reuse**: Adapt multi-layer pattern for vibesbox health checks (container → VNC → screenshot)

3. **PostCreate Hook (postCreate.sh)**:
   - **Similarity**: Devcontainer lifecycle integration point
   - **Lessons**: Informative output, tool version reporting, conditional setup work well
   - **Differences**: postCreate is environment setup, vibesbox management is service lifecycle
   - **Reuse**: Helper functions (info/success/warn/error), environment variable patterns

## Recommendations for PRP

Based on pattern analysis:

1. **Follow helper function pattern** from postCreate.sh for all user-facing output
   - Source functions in all scripts: `source "$(dirname "$0")/helper-functions.sh"`
   - Maintain consistent color coding and symbols

2. **Reuse network setup pattern** from setup-network.sh for vibes-network prerequisite
   - Call directly: `bash /usr/local/share/setup-network.sh`
   - Or extract to reusable function if modifications needed

3. **Mirror state machine pattern** from container-state-detection.sh for lifecycle management
   - Create helper functions: `vibesbox_exists()`, `vibesbox_running()`, `detect_vibesbox_state()`
   - Use case statement for action dispatch based on detected state

4. **Adapt polling pattern** from polling-with-timeout.sh for health checks
   - Generic `wait_for_condition()` function with vibesbox-specific condition functions
   - Chain checks: container → VNC → display → screenshot

5. **Avoid non-blocking failures anti-pattern** for devcontainer robustness
   - Use `|| true` or conditional error handling
   - Warn user but don't block devcontainer startup

6. **Follow existing script organization**:
   - Place scripts in `.devcontainer/scripts/`
   - Name as `ensure-vibesbox.sh` (orchestration) and `check-vibesbox.sh` (validation)
   - Export CLI helpers via `/etc/profile.d/vibesbox-cli.sh`

7. **Make everything configurable** via environment variables:
   - Network name: `VIBESBOX_NETWORK`
   - Container name: `VIBESBOX_CONTAINER_NAME`
   - Timeouts: `VIBESBOX_HEALTH_TIMEOUT`, `VIBESBOX_BUILD_TIMEOUT`
   - Behavior: `VIBESBOX_AUTO_BUILD`
   - Document all in `.env.example`

8. **Use ShellCheck** validation before committing any bash scripts

9. **Test idempotency** - every script must be safe to run multiple times

10. **Provide actionable error messages** - always include troubleshooting steps

## Source References

### From Archon
- **c0e629a894699314**: Pydantic AI - Lifecycle management patterns (context managers, async operations) - Relevance 7/10
- **d60a71d62eb201d5**: Model Context Protocol - Server lifecycle patterns - Relevance 6/10
- Limited bash/Docker patterns in Archon - most relevant patterns are from local codebase

### From Local Codebase
- `.devcontainer/scripts/postCreate.sh:8-12` - Helper functions (info/success/warn/error)
- `.devcontainer/scripts/postCreate.sh:2` - Error handling (`set -euo pipefail`)
- `.devcontainer/scripts/setup-network.sh:1-26` - Idempotent network creation
- `.devcontainer/scripts/test-docker.sh:7-62` - Multi-layer validation pattern
- `.devcontainer/devcontainer.json:6` - postCreateCommand integration point
- `mcp/mcp-vibesbox-server/docker-compose.yml` - Vibesbox container configuration
- `examples/devcontainer_vibesbox_integration/*.sh` - Synthesized patterns for feature

### From Examples Directory (Already Extracted)
- `examples/devcontainer_vibesbox_integration/helper-functions.sh` - Colored output
- `examples/devcontainer_vibesbox_integration/container-state-detection.sh` - State machine
- `examples/devcontainer_vibesbox_integration/polling-with-timeout.sh` - Health polling
- `examples/devcontainer_vibesbox_integration/network-setup.sh` - Idempotent operations
- `examples/devcontainer_vibesbox_integration/docker-health-check.sh` - Multi-layer validation

## Next Steps for Assembler

When generating the PRP:

- **Reference these patterns in "Current Codebase Tree" section**:
  - List all `.devcontainer/scripts/*.sh` files
  - List `mcp/mcp-vibesbox-server/docker-compose.yml`
  - Note examples already extracted

- **Include key code snippets in "Implementation Blueprint"**:
  - Helper functions (copy verbatim)
  - State detection logic (adapt from examples)
  - Polling pattern (reference wait_for_condition)
  - Network setup (call existing script)

- **Add anti-patterns to "Known Gotchas" section**:
  - Blocking devcontainer startup
  - Using 'up' instead of 'start'
  - Hardcoded timeouts
  - Silent failures
  - VNC race condition

- **Use file organization for "Desired Codebase Tree"**:
  ```
  .devcontainer/scripts/
  ├── ensure-vibesbox.sh (NEW)
  ├── check-vibesbox.sh (NEW)
  └── postCreate.sh (MODIFIED - add call to ensure-vibesbox.sh)

  /etc/profile.d/
  └── vibesbox-cli.sh (NEW)
  ```

- **Task breakdown should follow**:
  1. Create helper-functions.sh (or inline in scripts)
  2. Create check-vibesbox.sh (health validation utility)
  3. Create ensure-vibesbox.sh (main lifecycle orchestration)
  4. Create vibesbox-cli.sh (CLI helper exports)
  5. Modify postCreate.sh (add call to ensure-vibesbox.sh)
  6. Create .env.example (document all environment variables)
  7. Test idempotency and validation

- **Validation gates should include**:
  - ShellCheck passes on all bash scripts
  - Idempotency test (run ensure-vibesbox.sh 3x, verify consistent state)
  - State transition tests (missing → running, stopped → running)
  - Health check tests (all 4 layers pass)
  - Graceful degradation test (vibesbox fails, devcontainer continues)

---

**Generated**: 2025-10-04
**Archon Project ID**: 96623e6d-eaa2-4325-beee-21e605255c32
**Research Phase**: Phase 2A - Codebase Research
**Lines**: 761
**Patterns Documented**: 5 major patterns + 7 anti-patterns
**Source Files Analyzed**: 10+ bash scripts
**Confidence**: High (existing codebase has excellent patterns to follow)
