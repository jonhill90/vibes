#!/bin/bash
# Pre-flight validation for Codex CLI execution
# Source: Pattern 7 (Comprehensive Validation Suite) from codebase-patterns.md
# Purpose: Run before any codex exec command to ensure environment is ready
# Usage: ./.codex/scripts/validate-bootstrap.sh [profile_name]

set -euo pipefail

# Configuration
PROFILE_NAME="${1:-codex-prp}"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "${SCRIPT_DIR}/../.." && pwd)"

# Color output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Progress tracking
declare -i total_checks=6
declare -i passed_checks=0

# =============================================================================
# Validation Functions
# =============================================================================

validate_cli_installed() {
    echo -e "${BLUE}CHECK 1/${total_checks}: Codex CLI Installation${NC}"
    echo "-----------------------------------------"

    if ! command -v codex &> /dev/null; then
        echo -e "${RED}❌ Codex CLI not found${NC}"
        echo ""
        echo "Install using one of these methods:"
        echo "  - npm:   npm install -g @openai/codex"
        echo "  - brew:  brew install openai-codex"
        echo "  - binary: Download from https://github.com/openai/codex/releases"
        echo ""
        echo "See: docs/codex-bootstrap.md"
        return 1
    fi

    local version
    version=$(codex --version 2>&1 | head -1)
    echo -e "${GREEN}✅ Codex CLI installed: ${version}${NC}"
    return 0
}

validate_authentication() {
    echo ""
    echo -e "${BLUE}CHECK 2/${total_checks}: Authentication Status${NC}"
    echo "-----------------------------------------"

    if ! codex login status >/dev/null 2>&1; then
        echo -e "${RED}❌ Not authenticated${NC}"
        echo ""
        echo "Authenticate using one of these methods:"
        echo "  - ChatGPT login: codex login"
        echo "  - API key: Create ~/.codex/auth.json manually"
        echo ""
        echo "Troubleshooting:"
        echo "  - If browser login fails: Try SSH port forwarding"
        echo "  - If token expired: Run 'codex login' again"
        echo ""
        echo "See: docs/codex-bootstrap.md#authentication"
        return 1
    fi

    echo -e "${GREEN}✅ Authenticated${NC}"
    return 0
}

validate_profile() {
    echo ""
    echo -e "${BLUE}CHECK 3/${total_checks}: Profile Configuration${NC}"
    echo "-----------------------------------------"
    echo "Profile: ${PROFILE_NAME}"

    # Check profile exists
    if ! codex config show --profile "$PROFILE_NAME" &>/dev/null; then
        echo -e "${RED}❌ Profile not found: ${PROFILE_NAME}${NC}"
        echo ""
        echo "Create profile in ~/.codex/config.toml:"
        echo "  [profiles.${PROFILE_NAME}]"
        echo "  model = \"o4-mini\""
        echo "  approval_policy = \"on-request\""
        echo "  sandbox_mode = \"workspace-write\""
        echo "  bypass_approvals = true"
        echo "  bypass_sandbox = true"
        echo "  trusted_workspace = true"
        echo "  cwd = \"$(pwd)\""
        echo ""
        echo "See: docs/codex-config.md"
        return 1
    fi

    # Get profile config
    local config
    config=$(codex config show --profile "$PROFILE_NAME" 2>&1)

    # Check required fields
    local missing_fields=()

    if ! echo "$config" | grep -q "model"; then
        missing_fields+=("model")
    fi

    if ! echo "$config" | grep -q "approval_policy"; then
        missing_fields+=("approval_policy")
    fi

    if ! echo "$config" | grep -q "sandbox_mode"; then
        missing_fields+=("sandbox_mode")
    fi

    if [ ${#missing_fields[@]} -gt 0 ]; then
        echo -e "${RED}❌ Profile missing required fields: ${missing_fields[*]}${NC}"
        echo ""
        echo "Add to ~/.codex/config.toml [profiles.${PROFILE_NAME}]:"
        for field in "${missing_fields[@]}"; do
            case "$field" in
                model)
                    echo "  model = \"o4-mini\"  # or gpt-5-codex, o3"
                    ;;
                approval_policy)
                    echo "  approval_policy = \"on-request\"  # or on-failure, never"
                    ;;
                sandbox_mode)
                    echo "  sandbox_mode = \"workspace-write\"  # or read-only, danger-full-access"
                    ;;
            esac
        done
        echo ""
        echo "See: docs/codex-config.md"
        return 1
    fi

    echo -e "${GREEN}✅ Profile configured: ${PROFILE_NAME}${NC}"
    return 0
}

validate_sandbox() {
    echo ""
    echo -e "${BLUE}CHECK 4/${total_checks}: Sandbox Dry-Run Test${NC}"
    echo "-----------------------------------------"

    # Test read-only sandbox first (safest)
    if ! codex exec --profile "$PROFILE_NAME" --sandbox read-only \
         --prompt "echo 'sandbox test'" >/dev/null 2>&1; then
        echo -e "${RED}❌ Sandbox test failed (read-only mode)${NC}"
        echo ""
        echo "Check profile settings in ~/.codex/config.toml:"
        echo "  [profiles.${PROFILE_NAME}]"
        echo "  sandbox_mode = \"read-only\"  # Start with safest mode"
        echo "  bypass_approvals = true"
        echo "  bypass_sandbox = true"
        echo "  trusted_workspace = true"
        echo ""
        echo "See: docs/codex-config.md#sandbox-modes"
        return 1
    fi

    echo -e "${GREEN}✅ Sandbox test passed${NC}"
    return 0
}

validate_mcp_servers() {
    echo ""
    echo -e "${BLUE}CHECK 5/${total_checks}: MCP Server Availability${NC}"
    echo "-----------------------------------------"

    # Check if any MCP servers configured
    local config
    config=$(codex config show --profile "$PROFILE_NAME" 2>&1)

    if ! echo "$config" | grep -q "mcp_servers"; then
        echo -e "${YELLOW}⚠️  No MCP servers configured${NC}"
        echo "   This is optional but recommended for task tracking"
        echo "   Consider adding Archon MCP server"
        # Treat as informational, not a failure
        echo -e "${GREEN}✅ MCP check completed (none configured)${NC}"
        return 0
    fi

    # If MCP servers are configured, they should be accessible
    # Note: We can't easily test MCP server connectivity without running a command
    # So we just verify the configuration exists
    echo -e "${GREEN}✅ MCP servers configured in profile${NC}"
    return 0
}

validate_file_structure() {
    echo ""
    echo -e "${BLUE}CHECK 6/${total_checks}: File Structure Writability${NC}"
    echo "-----------------------------------------"

    cd "$REPO_ROOT"

    # Check prps/ directory exists and is writable
    if [ ! -d "prps" ]; then
        echo -e "${YELLOW}⚠️  prps/ directory not found - will create on first use${NC}"
        echo -e "${GREEN}✅ File structure check passed (with warning)${NC}"
        return 0
    fi

    # Test write permission
    local test_file="prps/.codex_write_test_$$"

    if ! touch "$test_file" 2>/dev/null; then
        echo -e "${RED}❌ Cannot write to prps/ directory${NC}"
        echo ""
        echo "Check permissions:"
        echo "  ls -ld prps/"
        echo ""
        echo "Fix with:"
        echo "  chmod u+w prps/"
        return 1
    fi

    rm -f "$test_file"
    echo -e "${GREEN}✅ File structure writable${NC}"
    return 0
}

# =============================================================================
# Main Validation
# =============================================================================

main() {
    echo "========================================="
    echo "Codex Pre-Flight Validation"
    echo "========================================="
    echo "Profile: ${PROFILE_NAME}"
    echo "Repository: ${REPO_ROOT}"
    echo ""

    # Check 1: CLI installed
    if validate_cli_installed; then
        ((passed_checks++))
    fi

    # Check 2: Authenticated
    if validate_authentication; then
        ((passed_checks++))
    fi

    # Check 3: Profile configured
    if validate_profile; then
        ((passed_checks++))
    fi

    # Check 4: Sandbox test
    if validate_sandbox; then
        ((passed_checks++))
    fi

    # Check 5: MCP servers
    if validate_mcp_servers; then
        ((passed_checks++))
    fi

    # Check 6: File structure
    if validate_file_structure; then
        ((passed_checks++))
    fi

    # Summary
    echo ""
    echo "========================================="
    echo "Validation Summary"
    echo "========================================="
    echo "Checks passed: ${passed_checks}/${total_checks}"

    local success_rate=$(( (passed_checks * 100) / total_checks ))
    echo "Success rate: ${success_rate}%"
    echo ""

    if [ "$passed_checks" -eq "$total_checks" ]; then
        echo -e "${GREEN}✅ ALL CHECKS PASSED - Ready for Codex execution${NC}"
        echo ""
        echo "Next steps:"
        echo "  1. Run codex commands: codex exec --profile ${PROFILE_NAME} --prompt '...'"
        echo "  2. See documentation: docs/codex-bootstrap.md"
        exit 0
    elif [ "$passed_checks" -ge 4 ]; then
        echo -e "${YELLOW}⚠️  SOME CHECKS FAILED - Review errors above${NC}"
        echo "You may proceed with caution or fix issues first"
        exit 1
    else
        echo -e "${RED}❌ CRITICAL FAILURES DETECTED - Fix before proceeding${NC}"
        echo "Review errors above and consult docs/codex-validation.md"
        exit 1
    fi
}

# Export functions for use in other scripts
export -f validate_cli_installed
export -f validate_authentication
export -f validate_profile
export -f validate_sandbox
export -f validate_mcp_servers
export -f validate_file_structure

# Run main if executed directly
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    main
fi
