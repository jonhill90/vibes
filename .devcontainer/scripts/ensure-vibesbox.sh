#!/usr/bin/env bash
# Vibesbox Lifecycle Orchestration Script
# Source: PRP devcontainer_vibesbox_integration.md - Task 3
# Responsibility: Auto-detect vibesbox state, take appropriate action, verify health
#
# Pattern: examples/devcontainer_vibesbox_integration/container-state-detection.sh (state machine)
#          examples/devcontainer_vibesbox_integration/network-setup.sh (idempotent network)
#          examples/devcontainer_vibesbox_integration/interactive-prompt.sh (build confirmation)

set -euo pipefail

#── Error Handler (Non-blocking) ─────────────────────────────────────
# CRITICAL: Graceful degradation - devcontainer must continue even if vibesbox fails
# Pattern: trap ERR for error handling, but exit 0 (not exit 1) to prevent blocking

handle_error() {
    local line=$1
    warn "Vibesbox setup encountered an issue at line $line"
    warn "GUI automation will be unavailable"
    warn "Troubleshoot with: docker logs ${VIBESBOX_CONTAINER_NAME}"
    warn "Or run: vibesbox-start (after devcontainer loads)"
    exit 0  # Non-blocking exit - allow devcontainer to continue
}
trap 'handle_error $LINENO' ERR

#── Source Helper Functions ──────────────────────────────────────────
# Pattern: Centralized helpers for colored output and state detection

SCRIPT_DIR="$(dirname "$0")"
# shellcheck source=.devcontainer/scripts/helpers/vibesbox-functions.sh
source "$SCRIPT_DIR/helpers/vibesbox-functions.sh"

#── Main Orchestration Flow ──────────────────────────────────────────
# Five-step process: Network → Detect → Action → Health → Report

info "Starting vibesbox lifecycle management..."
echo ""

# ═══════════════════════════════════════════════════════════════════
# Step 1: Ensure vibes-network exists
# ═══════════════════════════════════════════════════════════════════
# Pattern: examples/devcontainer_vibesbox_integration/network-setup.sh
# Idempotent network creation - check before create, graceful "already exists" handling

info "[1/5] Ensuring network '${VIBESBOX_NETWORK}' exists..."

if docker network ls --format '{{.Name}}' | grep -q "^${VIBESBOX_NETWORK}$"; then
    success "Network '${VIBESBOX_NETWORK}' already exists"
else
    info "Creating network '${VIBESBOX_NETWORK}'..."
    if docker network create "$VIBESBOX_NETWORK" 2>/dev/null; then
        success "Created network '${VIBESBOX_NETWORK}'"
    else
        warn "Network creation failed (may already exist) - continuing anyway"
    fi
fi

echo ""

# ═══════════════════════════════════════════════════════════════════
# Step 2: Detect vibesbox container state
# ═══════════════════════════════════════════════════════════════════
# Pattern: examples/devcontainer_vibesbox_integration/container-state-detection.sh
# Returns: "missing", "running", or "stopped-<status>"

info "[2/5] Detecting vibesbox container state..."

STATE=$(detect_vibesbox_state)
info "Current state: $STATE"

echo ""

# ═══════════════════════════════════════════════════════════════════
# Step 3: Take action based on state
# ═══════════════════════════════════════════════════════════════════
# Pattern: State machine with case statement
# missing      → Prompt to build (or auto-build if VIBESBOX_AUTO_BUILD=true)
# stopped-*    → docker compose start (resume existing container)
# running      → Skip to health checks

info "[3/5] Taking appropriate action for state: $STATE"

case "$STATE" in
    missing)
        warn "Vibesbox container not found"
        echo ""

        # Pattern: examples/devcontainer_vibesbox_integration/interactive-prompt.sh
        # Check for auto-build environment variable first
        if [ "${VIBESBOX_AUTO_BUILD:-false}" = "true" ]; then
            info "Auto-build enabled (VIBESBOX_AUTO_BUILD=true)"
            info "Building vibesbox container (estimated: 60-120s)..."
            echo ""

            if docker compose -f "$COMPOSE_FILE" up -d --build; then
                success "Container built and started"
            else
                error "Build failed - check docker-compose.yml at: $COMPOSE_FILE"
                warn "GUI automation unavailable"
                exit 0
            fi
        else
            # Interactive prompt
            warn "The vibesbox container provides GUI automation via VNC"
            info "Building will take approximately 60-120 seconds"
            echo ""

            read -r -p "Build vibesbox container now? [Y/n]: " response
            response="${response,,}"  # Convert to lowercase

            if [[ "$response" =~ ^(y|yes|)$ ]]; then
                info "Building vibesbox container..."
                echo ""

                if docker compose -f "$COMPOSE_FILE" up -d --build; then
                    success "Container built and started"
                else
                    error "Build failed - check docker-compose.yml at: $COMPOSE_FILE"
                    warn "GUI automation unavailable"
                    exit 0
                fi
            else
                warn "Vibesbox build skipped - GUI automation unavailable"
                info "To build later, run: vibesbox-start"
                info "To auto-build next time: export VIBESBOX_AUTO_BUILD=true"
                exit 0
            fi
        fi
        ;;

    stopped-*)
        info "Starting stopped vibesbox container..."
        echo ""

        # CRITICAL: Use 'docker compose start' not 'up' for existing containers
        # Pattern: PRP Gotcha - 'up' recreates containers, 'start' resumes them
        if docker compose -f "$COMPOSE_FILE" start; then
            success "Container started"
        else
            error "Failed to start container"
            warn "Try: docker compose -f $COMPOSE_FILE up -d"
            exit 0
        fi
        ;;

    running)
        success "Vibesbox already running"
        ;;

    *)
        warn "Unexpected state: $STATE"
        warn "Manual intervention may be required"
        exit 0
        ;;
esac

echo ""

# ═══════════════════════════════════════════════════════════════════
# Step 4: Verify health (call check-vibesbox.sh)
# ═══════════════════════════════════════════════════════════════════
# Pattern: Multi-layer validation via dedicated health check script
# Four layers: Container → VNC port → X11 display → Screenshot capability

info "[4/5] Verifying vibesbox health..."
echo ""

CHECK_SCRIPT="$SCRIPT_DIR/check-vibesbox.sh"

if [ -f "$CHECK_SCRIPT" ]; then
    # Run health checks with graceful degradation
    if bash "$CHECK_SCRIPT"; then
        echo ""
        success "All health checks passed"
    else
        echo ""
        warn "Health checks failed - vibesbox may not be fully operational"
        warn "VNC or display services might still be initializing"
        warn "Wait 30-60 seconds and run: vibesbox-status"
        # Don't exit - allow continuation with warning
    fi
else
    warn "Health check script not found at: $CHECK_SCRIPT"
    warn "Skipping health validation"
fi

echo ""

# ═══════════════════════════════════════════════════════════════════
# Step 5: Report status and connection info
# ═══════════════════════════════════════════════════════════════════
# Pattern: Clear success message with actionable connection information

info "[5/5] Vibesbox lifecycle management complete"
echo ""

success "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
success "  Vibesbox Ready"
success "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
info "VNC Connection:"
info "  • URL:     vnc://localhost:${VIBESBOX_VNC_PORT}"
info "  • Port:    ${VIBESBOX_VNC_PORT}"
info "  • Display: :1"
echo ""
info "CLI Helpers Available:"
info "  • vibesbox-status   - Show current status and health"
info "  • vibesbox-start    - Start stopped container"
info "  • vibesbox-stop     - Stop running container"
info "  • vibesbox-restart  - Restart container"
info "  • vibesbox-logs     - Follow container logs"
info "  • vibesbox-vnc      - Display VNC connection info"
echo ""
success "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

exit 0
