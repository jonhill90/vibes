#!/bin/bash
# Codex Configuration Validation Script
# Purpose: Validate Codex profile configuration against v0.20+ requirements
# Pattern: Codebase patterns Pattern 4 (validation loops)
# Usage: ./.codex/scripts/validate-config.sh [profile_name]

set -euo pipefail

# Default profile name
PROFILE_NAME="${1:-codex-prp}"

# Color output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Progress tracking
declare -i total_checks=0
declare -i passed_checks=0
declare -i warnings=0

echo "========================================="
echo "Codex Configuration Validation"
echo "========================================="
echo "Profile: ${PROFILE_NAME}"
echo ""

# =============================================================================
# CHECK 1: Profile Exists
# =============================================================================
echo "Check 1/6: Profile exists"
total_checks=$((total_checks + 1))

if ! codex config show --profile "$PROFILE_NAME" &>/dev/null; then
    echo -e "${RED}❌ Profile not found: ${PROFILE_NAME}${NC}"
    echo ""
    echo "Create profile in ~/.codex/config.toml:"
    echo ""
    echo "[profiles.${PROFILE_NAME}]"
    echo "model = \"o4-mini\""
    echo "approval_policy = \"on-request\""
    echo "sandbox_mode = \"workspace-write\""
    echo "cwd = \"$(pwd)\""
    echo ""
    echo "See: docs/codex-config.md"
    exit 1
else
    echo -e "${GREEN}✅ Profile exists${NC}"
    passed_checks=$((passed_checks + 1))
fi
echo ""

# Get profile config for remaining checks
PROFILE_CONFIG=$(codex config show --profile "$PROFILE_NAME" 2>&1)

# =============================================================================
# CHECK 2: Required Fields Present
# =============================================================================
echo "Check 2/6: Required fields"
total_checks=$((total_checks + 1))

required_fields=("model" "approval_policy" "sandbox_mode" "cwd")
missing_fields=()

for field in "${required_fields[@]}"; do
    if ! echo "$PROFILE_CONFIG" | grep -q "$field"; then
        missing_fields+=("$field")
    fi
done

if [ ${#missing_fields[@]} -gt 0 ]; then
    echo -e "${RED}❌ Missing required fields: ${missing_fields[*]}${NC}"
    echo ""
    echo "Add to ~/.codex/config.toml [profiles.${PROFILE_NAME}]:"
    echo ""
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
            cwd)
                echo "  cwd = \"$(pwd)\"  # Repo root"
                ;;
        esac
    done
    echo ""
    echo "See: docs/codex-config.md#profile-structure"
    exit 1
else
    echo -e "${GREEN}✅ All required fields present${NC}"
    passed_checks=$((passed_checks + 1))
fi
echo ""

# =============================================================================
# CHECK 3: v0.20+ Four-Setting Requirement
# =============================================================================
echo "Check 3/6: v0.20+ automation settings"
total_checks=$((total_checks + 1))

# These settings are required for full automation (v0.20+)
automation_settings=("bypass_approvals" "bypass_sandbox" "trusted_workspace")
missing_automation=()

for setting in "${automation_settings[@]}"; do
    if ! echo "$PROFILE_CONFIG" | grep -q "$setting"; then
        missing_automation+=("$setting")
    fi
done

if [ ${#missing_automation[@]} -gt 0 ]; then
    echo -e "${YELLOW}⚠️  v0.20+ automation settings missing: ${missing_automation[*]}${NC}"
    echo ""
    echo "For automated workflows, add to ~/.codex/config.toml [profiles.${PROFILE_NAME}]:"
    echo ""
    echo "  approval_policy = \"never\"  # Full automation"
    echo "  bypass_approvals = true"
    echo "  bypass_sandbox = true"
    echo "  trusted_workspace = true"
    echo ""
    echo "NOTE: These settings bypass approval prompts. Only use with trusted code."
    echo "For manual workflows, current config is acceptable."
    echo ""
    echo "See: docs/codex-config.md#approval-policies (Gotcha: v0.20+ Four-Setting Requirement)"
    warnings=$((warnings + 1))
else
    echo -e "${GREEN}✅ v0.20+ automation settings configured${NC}"
    passed_checks=$((passed_checks + 1))
fi
echo ""

# =============================================================================
# CHECK 4: MCP Servers Configured
# =============================================================================
echo "Check 4/6: MCP servers"
total_checks=$((total_checks + 1))

if ! echo "$PROFILE_CONFIG" | grep -q "mcp_servers"; then
    echo -e "${YELLOW}⚠️  No MCP servers configured${NC}"
    echo ""
    echo "Consider adding MCP servers for enhanced functionality:"
    echo ""
    echo "[profiles.${PROFILE_NAME}.mcp_servers.archon]"
    echo "url = \"http://localhost:8051/mcp\"  # HTTP transport"
    echo ""
    echo "# OR"
    echo ""
    echo "[profiles.${PROFILE_NAME}.mcp_servers.archon_stdio]"
    echo "command = \"uvx\""
    echo "args = [\"archon\"]"
    echo "startup_timeout_sec = 90"
    echo ""
    echo "See: docs/codex-config.md#mcp-server-configuration"
    warnings=$((warnings + 1))
else
    echo -e "${GREEN}✅ MCP servers configured${NC}"
    passed_checks=$((passed_checks + 1))
fi
echo ""

# =============================================================================
# CHECK 5: Timeout Recommendations
# =============================================================================
echo "Check 5/6: Timeout configuration"
total_checks=$((total_checks + 1))

# Extract timeout values (if present)
startup_timeout=$(echo "$PROFILE_CONFIG" | grep -oP 'startup_timeout_sec\s*=\s*\K\d+' || echo "0")
tool_timeout=$(echo "$PROFILE_CONFIG" | grep -oP 'tool_timeout_sec\s*=\s*\K\d+' || echo "0")

timeout_warnings=()

# Check startup timeout (should be >= 60 for Docker/uvx servers)
if [ "$startup_timeout" -lt 60 ] && [ "$startup_timeout" -gt 0 ]; then
    timeout_warnings+=("startup_timeout_sec = ${startup_timeout} (recommend >= 60)")
fi

# Check tool timeout (should be >= 600 for complex PRP phases)
if [ "$tool_timeout" -lt 600 ] && [ "$tool_timeout" -gt 0 ]; then
    timeout_warnings+=("tool_timeout_sec = ${tool_timeout} (recommend >= 600)")
fi

if [ ${#timeout_warnings[@]} -gt 0 ]; then
    echo -e "${YELLOW}⚠️  Timeout settings may be too short:${NC}"
    for warning in "${timeout_warnings[@]}"; do
        echo "  - $warning"
    done
    echo ""
    echo "Recommended settings for PRP workflows:"
    echo ""
    echo "[profiles.${PROFILE_NAME}]"
    echo "startup_timeout_sec = 60   # Allow time for MCP server startup"
    echo "tool_timeout_sec = 600     # 10 minutes for complex phases"
    echo ""
    echo "See: docs/codex-config.md#timeout-configuration"
    warnings=$((warnings + 1))
else
    echo -e "${GREEN}✅ Timeout configuration adequate${NC}"
    passed_checks=$((passed_checks + 1))
fi
echo ""

# =============================================================================
# CHECK 6: Network Access (for workspace-write mode)
# =============================================================================
echo "Check 6/6: Network access configuration"
total_checks=$((total_checks + 1))

if echo "$PROFILE_CONFIG" | grep -q 'sandbox_mode.*workspace-write'; then
    if ! echo "$PROFILE_CONFIG" | grep -q 'network_access.*true'; then
        echo -e "${YELLOW}⚠️  Network access not enabled in workspace-write mode${NC}"
        echo ""
        echo "WebSearch and API calls will fail without network access."
        echo "To enable, add to ~/.codex/config.toml:"
        echo ""
        echo "[profiles.${PROFILE_NAME}.sandbox_workspace_write]"
        echo "network_access = true"
        echo ""
        echo "See: docs/codex-config.md#workspace-write-configuration"
        warnings=$((warnings + 1))
    else
        echo -e "${GREEN}✅ Network access enabled${NC}"
        passed_checks=$((passed_checks + 1))
    fi
else
    echo -e "${GREEN}✅ Network access check skipped (not using workspace-write)${NC}"
    passed_checks=$((passed_checks + 1))
fi
echo ""

# =============================================================================
# SUMMARY
# =============================================================================
echo "========================================="
echo "Validation Summary"
echo "========================================="
echo "Profile: ${PROFILE_NAME}"
echo "Checks passed: ${passed_checks}/${total_checks}"

if [ $warnings -gt 0 ]; then
    echo -e "${YELLOW}Warnings: ${warnings}${NC}"
fi

success_rate=$(( (passed_checks * 100) / total_checks ))
echo "Success rate: ${success_rate}%"
echo ""

if [ "$passed_checks" -eq "$total_checks" ]; then
    echo -e "${GREEN}✅ Configuration validated - ready for use${NC}"
    echo ""
    echo "Test with:"
    echo "  codex exec --profile ${PROFILE_NAME} --prompt \"echo 'test'\""
    exit 0
elif [ "$passed_checks" -ge 2 ]; then
    echo -e "${YELLOW}⚠️  Configuration has warnings but may be usable${NC}"
    echo ""
    echo "Review warnings above and consider updating config."
    echo "See: docs/codex-config.md"
    exit 1
else
    echo -e "${RED}❌ Configuration validation failed${NC}"
    echo ""
    echo "Fix critical errors above before using this profile."
    echo "See: docs/codex-config.md"
    exit 1
fi
