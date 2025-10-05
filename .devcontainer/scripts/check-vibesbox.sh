#!/usr/bin/env bash
# Vibesbox Health Check Utility
# Source: Task 2 - Multi-layer health verification
# Pattern: examples/devcontainer_vibesbox_integration/docker-health-check.sh
# Usage: ./check-vibesbox.sh

set -euo pipefail

#── Source Helper Functions ──────────────────────────────────────────
SCRIPT_DIR="$(dirname "$0")"
# shellcheck source=.devcontainer/scripts/helpers/vibesbox-functions.sh
source "$SCRIPT_DIR/helpers/vibesbox-functions.sh"

#── Main Health Check Function ───────────────────────────────────────
check_vibesbox_health() {
    info "Checking vibesbox health..."
    echo ""

    # Layer 1: Container running
    info "[1/4] Checking container status..."
    if ! container_running; then
        error "Container not running"
        local status
        status=$(get_container_status)
        if [ "$status" = "missing" ]; then
            error "Container does not exist - run: vibesbox-start"
        else
            error "Container exists but not running (status: $status)"
            error "Start with: docker compose -f $COMPOSE_FILE start"
        fi
        return 1
    fi
    success "Container is running"
    echo ""

    # Layer 2: VNC port accessible
    info "[2/4] Checking VNC port accessibility..."
    if ! wait_for_condition vnc_port_ready "${VIBESBOX_HEALTH_TIMEOUT}" 2 "VNC port ${VIBESBOX_VNC_PORT}"; then
        echo ""
        error "VNC port not accessible"
        error "Troubleshoot:"
        error "  1. Check if port is in use: lsof -i :${VIBESBOX_VNC_PORT}"
        error "  2. Check container logs: docker logs ${VIBESBOX_CONTAINER_NAME}"
        error "  3. Verify VNC server started: docker exec ${VIBESBOX_CONTAINER_NAME} ps aux | grep vnc"
        return 1
    fi
    echo ""

    # Layer 3: X11 display working
    info "[3/4] Checking X11 display accessibility..."
    if ! wait_for_condition display_accessible "${VIBESBOX_HEALTH_TIMEOUT}" 2 "X11 display :1"; then
        echo ""
        error "X11 display not accessible"
        error "Troubleshoot:"
        error "  1. Check Xvfb running: docker exec ${VIBESBOX_CONTAINER_NAME} ps aux | grep Xvfb"
        error "  2. Check display socket: docker exec ${VIBESBOX_CONTAINER_NAME} ls -la /tmp/.X11-unix/"
        error "  3. Install xdpyinfo if missing: docker exec ${VIBESBOX_CONTAINER_NAME} apt-get install x11-utils"
        return 1
    fi
    echo ""

    # Layer 4: Screenshot capability
    info "[4/4] Checking screenshot capability..."
    if ! wait_for_condition screenshot_works "${VIBESBOX_HEALTH_TIMEOUT}" 2 "screenshot capability"; then
        echo ""
        error "Screenshot capability not working"
        error "Troubleshoot:"
        error "  1. Check ImageMagick installed: docker exec ${VIBESBOX_CONTAINER_NAME} which import"
        error "  2. Test manually: docker exec ${VIBESBOX_CONTAINER_NAME} sh -c 'DISPLAY=:1 import -window root /tmp/test.png'"
        error "  3. Check file permissions in /tmp"
        return 1
    fi
    echo ""

    success "All health checks passed!"
    success "Vibesbox is fully operational"
    echo ""
    info "VNC Connection:"
    info "  Host: localhost"
    info "  Port: ${VIBESBOX_VNC_PORT}"
    info "  Display: :1"
    info "  URL: vnc://localhost:${VIBESBOX_VNC_PORT}"

    return 0
}

#── Main Execution ───────────────────────────────────────────────────
# Run health check and propagate exit code
if check_vibesbox_health; then
    exit 0
else
    exit 1
fi
