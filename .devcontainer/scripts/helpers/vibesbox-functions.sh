#!/usr/bin/env bash
# Vibesbox Helper Functions Module
# Source: vibes/examples/devcontainer_vibesbox_integration/
# Provides: Colored output, state detection, health checks, polling utilities

# Configuration (environment variable overrides with sensible defaults)
VIBESBOX_NETWORK="${VIBESBOX_NETWORK:-vibes-network}"
VIBESBOX_CONTAINER_NAME="${VIBESBOX_CONTAINER_NAME:-mcp-vibesbox-server}"
VIBESBOX_VNC_PORT="${VIBESBOX_VNC_PORT:-5901}"
VIBESBOX_HEALTH_TIMEOUT="${VIBESBOX_HEALTH_TIMEOUT:-30}"
COMPOSE_FILE="${VIBESBOX_COMPOSE_FILE:-/workspace/vibes/mcp/mcp-vibesbox-server/docker-compose.yml}"

#── Colored Output Functions ─────────────────────────────────────────
# Pattern: examples/devcontainer_vibesbox_integration/helper-functions.sh
# ANSI escape codes for terminal coloring with Unicode symbols

info()    { printf "\033[36mℹ [INFO]\033[0m  %s\n" "$*"; }
success() { printf "\033[32m✔ [OK]\033[0m    %s\n" "$*"; }
warn()    { printf "\033[33m⚠ [WARN]\033[0m  %s\n" "$*"; }
error()   { printf "\033[31m✖ [ERROR]\033[0m %s\n" "$*"; }

#── Container State Detection Functions ──────────────────────────────
# Pattern: examples/devcontainer_vibesbox_integration/container-state-detection.sh
# Detect container existence, running status, and detailed state

container_exists() {
    # Check if container exists (running or stopped)
    # Returns: 0 if exists, 1 if not
    docker ps -a --format '{{.Names}}' | grep -q "^${VIBESBOX_CONTAINER_NAME}$"
}

container_running() {
    # Check if container is currently running
    # Returns: 0 if running, 1 if not
    docker ps --format '{{.Names}}' | grep -q "^${VIBESBOX_CONTAINER_NAME}$"
}

get_container_status() {
    # Get detailed container status from docker inspect
    # Returns: status string (running, exited, created, etc.) or "missing"
    docker inspect --format '{{.State.Status}}' "$VIBESBOX_CONTAINER_NAME" 2>/dev/null || echo "missing"
}

detect_vibesbox_state() {
    # Detect and classify vibesbox container state
    # Returns: "missing", "running", or "stopped-<status>"
    if ! container_exists; then
        echo "missing"
    elif container_running; then
        echo "running"
    else
        local status
        status=$(get_container_status)
        echo "stopped-${status}"
    fi
}

#── Health Check Condition Functions ─────────────────────────────────
# Pattern: Progressive health validation for vibesbox
# Layer 1: Container running, Layer 2: VNC port, Layer 3: Display, Layer 4: Screenshot

vnc_port_ready() {
    # Check if VNC port is accessible
    # Returns: 0 if port open, 1 if not
    nc -z localhost "${VIBESBOX_VNC_PORT}" 2>/dev/null
}

display_accessible() {
    # Check if X11 display is accessible inside container
    # Returns: 0 if display working, 1 if not
    docker exec "$VIBESBOX_CONTAINER_NAME" sh -c "DISPLAY=:1 xdpyinfo" &>/dev/null
}

screenshot_works() {
    # Test screenshot capability (full health validation)
    # Returns: 0 if screenshot works, 1 if not
    local test_file="/tmp/vibesbox-health-$$.png"
    docker exec "$VIBESBOX_CONTAINER_NAME" sh -c "DISPLAY=:1 import -window root $test_file" &>/dev/null
    local result=$?
    # Cleanup test file
    docker exec "$VIBESBOX_CONTAINER_NAME" rm -f "$test_file" &>/dev/null || true
    return $result
}

#── Generic Polling with Timeout ─────────────────────────────────────
# Pattern: examples/devcontainer_vibesbox_integration/polling-with-timeout.sh
# Reusable function for waiting on async operations with timeout

wait_for_condition() {
    local condition_func="$1"
    local timeout_seconds="${2:-30}"
    local check_interval="${3:-2}"
    local description="${4:-condition}"

    local elapsed=0

    info "Waiting for $description (timeout: ${timeout_seconds}s)..."

    while [ $elapsed -lt $timeout_seconds ]; do
        if $condition_func; then
            success "$description ready (${elapsed}s elapsed)"
            return 0
        fi

        sleep "$check_interval"
        elapsed=$((elapsed + check_interval))

        # Progress indicator
        echo -n "."
    done

    echo ""
    error "Timeout waiting for $description (${timeout_seconds}s elapsed)"
    return 1
}
