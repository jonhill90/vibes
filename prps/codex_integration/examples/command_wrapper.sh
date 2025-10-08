#!/bin/bash
# Source: Adapted from .claude/commands/generate-prp.md Phase 0 + Codex exec docs
# Pattern: Command wrapper script for Codex CLI execution
# Extracted: 2025-10-07
# Relevance: 10/10 - Core wrapper pattern for Codex command orchestration

set -e  # Exit on error

# =============================================================================
# PATTERN: Codex Command Wrapper with Validation & Logging
# =============================================================================
# Use Case: Execute Codex commands with pre-flight checks and result logging
# What to Mimic: Validation gates, error handling, manifest logging pattern
# What to Adapt: Feature name, phase count, prompt file paths
# What to Skip: Archon integration (optional in this example)

FEATURE_NAME="${1:-}"
CODEX_PROFILE="${2:-codex-prp}"
PHASE_COUNT=6

# Validation
if [ -z "$FEATURE_NAME" ]; then
    echo "Usage: $0 <feature_name> [codex_profile]"
    exit 1
fi

INITIAL_PRP="prps/INITIAL_${FEATURE_NAME}.md"
OUTPUT_DIR="prps/${FEATURE_NAME}/codex"
LOG_DIR="${OUTPUT_DIR}/logs"
MANIFEST="${LOG_DIR}/manifest.jsonl"

# =============================================================================
# Pre-flight Checks
# =============================================================================
echo "========================================="
echo "Codex PRP Generation: ${FEATURE_NAME}"
echo "Profile: ${CODEX_PROFILE}"
echo "========================================="

# Check 1: Codex CLI installed
if ! command -v codex &> /dev/null; then
    echo "❌ Codex CLI not found. Install: npm i -g @openai/codex"
    exit 1
fi
echo "✅ Codex CLI: $(codex --version)"

# Check 2: Authentication
if ! codex login status &> /dev/null; then
    echo "❌ Not authenticated. Run: codex login"
    exit 1
fi
echo "✅ Authentication verified"

# Check 3: INITIAL.md exists
if [ ! -f "$INITIAL_PRP" ]; then
    echo "❌ INITIAL.md not found: ${INITIAL_PRP}"
    exit 1
fi
echo "✅ INITIAL.md found: ${INITIAL_PRP}"

# Check 4: Profile configured
if ! codex config show --profile "$CODEX_PROFILE" &> /dev/null; then
    echo "⚠️  Profile not found: ${CODEX_PROFILE}"
    echo "Using default profile (consider creating dedicated profile)"
fi

# =============================================================================
# Setup Phase
# =============================================================================
echo ""
echo "Phase 0: Setup"
echo "-----------------------------------------"
mkdir -p "$OUTPUT_DIR" "$LOG_DIR"
echo "✅ Directories created: ${OUTPUT_DIR}, ${LOG_DIR}"

# Initialize manifest
echo '{"phase":"setup","timestamp":"'$(date -u +"%Y-%m-%dT%H:%M:%SZ")'","status":"started"}' > "$MANIFEST"

# =============================================================================
# Phase Execution Loop
# =============================================================================
for phase in $(seq 1 $PHASE_COUNT); do
    echo ""
    echo "Phase ${phase}/${PHASE_COUNT}: Executing"
    echo "-----------------------------------------"

    PHASE_PROMPT_FILE=".codex/commands/phase${phase}.md"

    if [ ! -f "$PHASE_PROMPT_FILE" ]; then
        echo "⚠️  Phase prompt not found: ${PHASE_PROMPT_FILE}"
        echo "Skipping phase ${phase}"
        continue
    fi

    # Execute Codex with explicit profile
    START_TIME=$(date +%s)

    if codex exec \
        --profile "$CODEX_PROFILE" \
        --prompt "$(cat $PHASE_PROMPT_FILE)" \
        2>&1 | tee "${LOG_DIR}/phase${phase}.log"; then
        EXIT_CODE=0
        STATUS="success"
        echo "✅ Phase ${phase} completed"
    else
        EXIT_CODE=$?
        STATUS="failed"
        echo "❌ Phase ${phase} failed with exit code: ${EXIT_CODE}"
    fi

    END_TIME=$(date +%s)
    DURATION=$((END_TIME - START_TIME))

    # Log to manifest (JSONL format)
    echo "{\"phase\":\"phase${phase}\",\"exit_code\":${EXIT_CODE},\"duration_sec\":${DURATION},\"timestamp\":\"$(date -u +"%Y-%m-%dT%H:%M:%SZ")\",\"status\":\"${STATUS}\"}" >> "$MANIFEST"

    # Fail fast
    if [ $EXIT_CODE -ne 0 ]; then
        echo ""
        echo "========================================="
        echo "❌ FAILURE: Phase ${phase} failed"
        echo "========================================="
        echo "Logs: ${LOG_DIR}/phase${phase}.log"
        echo "Manifest: ${MANIFEST}"
        exit $EXIT_CODE
    fi
done

# =============================================================================
# Completion
# =============================================================================
echo ""
echo "========================================="
echo "✅ SUCCESS: PRP Generation Complete"
echo "========================================="
echo "Output: ${OUTPUT_DIR}/prp_codex.md"
echo "Logs: ${LOG_DIR}/"
echo "Manifest: ${MANIFEST}"
echo ""
echo "Next steps:"
echo "  1. Review PRP: cat ${OUTPUT_DIR}/prp_codex.md"
echo "  2. Execute PRP: codex-execute-prp ${OUTPUT_DIR}/prp_codex.md"
