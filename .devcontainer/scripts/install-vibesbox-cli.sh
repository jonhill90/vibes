#!/usr/bin/env bash
# Install vibesbox CLI helper functions to /etc/profile.d/
# This script is called from postCreate.sh during devcontainer setup

set -e

SCRIPT_DIR="$(dirname "$0")"
SOURCE_FILE="$SCRIPT_DIR/vibesbox-cli.sh"
TARGET_FILE="/etc/profile.d/vibesbox-cli.sh"

# Helper functions
info()    { printf "\033[36mℹ [INFO]\033[0m  %s\n" "$*"; }
success() { printf "\033[32m✔ [OK]\033[0m    %s\n" "$*"; }
warn()    { printf "\033[33m⚠ [WARN]\033[0m  %s\n" "$*"; }
error()   { printf "\033[31m✖ [ERROR]\033[0m %s\n" "$*"; }

info "Installing vibesbox CLI helpers..."

# Check if source file exists
if [ ! -f "$SOURCE_FILE" ]; then
    error "Source file not found: $SOURCE_FILE"
    exit 1
fi

# Create /etc/profile.d/ if it doesn't exist (requires sudo in most cases)
if [ ! -d /etc/profile.d ]; then
    info "Creating /etc/profile.d/ directory..."
    if sudo mkdir -p /etc/profile.d 2>/dev/null; then
        success "Directory created"
    else
        warn "Failed to create directory (sudo not available or no permissions)"
        warn "CLI helpers will not be auto-loaded on shell startup"
        warn "You can manually source: source $SOURCE_FILE"
        exit 0
    fi
fi

# Copy file to /etc/profile.d/ (requires sudo)
info "Installing to $TARGET_FILE..."
if sudo cp "$SOURCE_FILE" "$TARGET_FILE" 2>/dev/null; then
    sudo chmod +x "$TARGET_FILE" 2>/dev/null || true
    success "CLI helpers installed successfully"
    success "Functions will be available in new shells"
    echo ""
    info "Available commands:"
    echo "  vibesbox-status   - Show container status and health"
    echo "  vibesbox-start    - Start vibesbox container"
    echo "  vibesbox-stop     - Stop vibesbox container"
    echo "  vibesbox-restart  - Restart vibesbox container"
    echo "  vibesbox-logs     - Follow container logs"
    echo "  vibesbox-vnc      - Display VNC connection info"
else
    warn "Failed to install (sudo not available or no permissions)"
    warn "CLI helpers will not be auto-loaded on shell startup"
    echo ""
    info "Workaround: Source manually in your shell:"
    echo "  source $SOURCE_FILE"
fi
