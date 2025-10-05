#!/usr/bin/env bash
# Vibesbox CLI Helper Functions
# Auto-loaded on shell startup via /etc/profile.d/
# Provides user-accessible commands: vibesbox-status, vibesbox-start, etc.

# Source helper functions if available (with fallback)
if [ -f /workspace/vibes/.devcontainer/scripts/helpers/vibesbox-functions.sh ]; then
    source /workspace/vibes/.devcontainer/scripts/helpers/vibesbox-functions.sh
else
    # Fallback: Simple colored output functions
    info()    { printf "\033[36mℹ [INFO]\033[0m  %s\n" "$*"; }
    success() { printf "\033[32m✔ [OK]\033[0m    %s\n" "$*"; }
    warn()    { printf "\033[33m⚠ [WARN]\033[0m  %s\n" "$*"; }
    error()   { printf "\033[31m✖ [ERROR]\033[0m %s\n" "$*"; }

    # Fallback configuration
    VIBESBOX_CONTAINER_NAME="${VIBESBOX_CONTAINER_NAME:-mcp-vibesbox-server}"
    VIBESBOX_VNC_PORT="${VIBESBOX_VNC_PORT:-5901}"
    COMPOSE_FILE="${VIBESBOX_COMPOSE_FILE:-/workspace/vibes/mcp/mcp-vibesbox-server/docker-compose.yml}"
fi

#── CLI Helper Functions ─────────────────────────────────────────────

vibesbox-status() {
    # Show comprehensive vibesbox status: container state, VNC port, health
    local status
    status=$(docker inspect --format='{{.State.Status}}' "$VIBESBOX_CONTAINER_NAME" 2>/dev/null || echo "missing")

    info "Vibesbox Status: $status"
    echo ""

    if [ "$status" = "running" ]; then
        success "Container: Running"
        success "VNC Port: $VIBESBOX_VNC_PORT"
        success "Display: :1"
        success "Connect: vnc://localhost:$VIBESBOX_VNC_PORT"
        echo ""

        # Show health status if check script available
        if [ -f /workspace/vibes/.devcontainer/scripts/check-vibesbox.sh ]; then
            info "Running health checks..."
            if bash /workspace/vibes/.devcontainer/scripts/check-vibesbox.sh 2>/dev/null; then
                success "Health: All checks passed"
            else
                warn "Health: Some checks failed (VNC may still be initializing)"
            fi
        fi
    elif [ "$status" = "missing" ]; then
        warn "Container not found"
        echo ""
        info "To create and start:"
        echo "  vibesbox-start"
        echo ""
        info "Or manually:"
        echo "  docker compose -f $COMPOSE_FILE up -d"
    else
        warn "Container exists but not running (status: $status)"
        echo ""
        info "To start:"
        echo "  vibesbox-start"
    fi
}

vibesbox-start() {
    # Start vibesbox container (create if missing, start if stopped)
    info "Starting vibesbox container..."
    echo ""

    if docker inspect "$VIBESBOX_CONTAINER_NAME" &>/dev/null; then
        # Container exists, just start it
        info "Container exists, starting..."
        if docker compose -f "$COMPOSE_FILE" start; then
            success "Container started"
            echo ""
            info "VNC available at: vnc://localhost:$VIBESBOX_VNC_PORT"
            info "Run 'vibesbox-status' to verify health"
        else
            error "Failed to start container"
            return 1
        fi
    else
        # Container doesn't exist, create and start
        info "Container not found, creating and starting..."
        if docker compose -f "$COMPOSE_FILE" up -d; then
            success "Container created and started"
            echo ""
            info "VNC available at: vnc://localhost:$VIBESBOX_VNC_PORT"
            info "Run 'vibesbox-status' to verify health"
        else
            error "Failed to create container"
            return 1
        fi
    fi
}

vibesbox-stop() {
    # Stop vibesbox container gracefully
    info "Stopping vibesbox container..."
    echo ""

    if docker compose -f "$COMPOSE_FILE" stop; then
        success "Container stopped"
    else
        error "Failed to stop container"
        return 1
    fi
}

vibesbox-restart() {
    # Restart vibesbox container (full restart cycle)
    info "Restarting vibesbox container..."
    echo ""

    if docker compose -f "$COMPOSE_FILE" restart; then
        success "Container restarted"
        echo ""
        info "VNC available at: vnc://localhost:$VIBESBOX_VNC_PORT"
        info "Run 'vibesbox-status' to verify health"
    else
        error "Failed to restart container"
        return 1
    fi
}

vibesbox-logs() {
    # Follow vibesbox container logs (tail -f style)
    info "Following vibesbox logs (Ctrl+C to exit)..."
    echo ""
    docker compose -f "$COMPOSE_FILE" logs -f "$@"
}

vibesbox-vnc() {
    # Display VNC connection information with usage examples
    info "VNC Connection Information:"
    echo ""
    success "Host: localhost"
    success "Port: $VIBESBOX_VNC_PORT"
    success "Display: :1"
    success "Connection string: vnc://localhost:$VIBESBOX_VNC_PORT"
    echo ""
    info "Connect with:"
    echo "  vncviewer localhost:$VIBESBOX_VNC_PORT"
    echo "  or use any VNC client (TigerVNC, RealVNC, etc.)"
    echo ""
    info "Via SSH tunnel (for remote access):"
    echo "  ssh -L $VIBESBOX_VNC_PORT:localhost:$VIBESBOX_VNC_PORT user@host"
    echo "  then connect to: vnc://localhost:$VIBESBOX_VNC_PORT"
}

#── Export Functions ─────────────────────────────────────────────────
# Make functions available in all shells (including subshells)

export -f vibesbox-status
export -f vibesbox-start
export -f vibesbox-stop
export -f vibesbox-restart
export -f vibesbox-logs
export -f vibesbox-vnc
