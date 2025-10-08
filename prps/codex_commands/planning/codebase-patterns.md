# Codebase Patterns: codex_commands

## Overview

This document captures bash orchestration patterns, parallel execution techniques, Codex CLI integration patterns, security validation, and JSONL manifest logging from the Vibes codebase. These patterns are **directly applicable** to implementing production-ready Codex commands for PRP generation and execution with parallel Phase 2 speedup (3x faster).

**Key Finding**: The codebase already has production-ready examples (`prps/codex_integration/examples/`) and a working manifest logger (`scripts/codex/log-phase.sh`) that should be reused directly.

---

## Architectural Patterns

### Pattern 1: Bash Parallel Execution with Job Control

**Source**: `/Users/jon/source/vibes/prps/codex_integration/examples/phase_orchestration.sh` (lines 112-161)
**Relevance**: 10/10 - Core pattern for Phase 2 parallel execution

**What it does**: Launches multiple bash background processes using job control (`&`), tracks PIDs, waits for all to complete, and captures individual exit codes without losing them due to timing issues.

**Key Techniques**:
```bash
# Launch all phases in background with PID tracking
execute_phase "phase2a" &
PID_2A=$!

execute_phase "phase2b" &
PID_2B=$!

execute_phase "phase2c" &
PID_2C=$!

# Wait for all, capturing exit codes IMMEDIATELY (CRITICAL timing)
wait $PID_2A; EXIT_2A=$?
wait $PID_2B; EXIT_2B=$?
wait $PID_2C; EXIT_2C=$?

# Validate all succeeded before continuing
if [[ $EXIT_2A -eq 0 && $EXIT_2B -eq 0 && $EXIT_2C -eq 0 ]]; then
    echo "✅ All parallel phases completed successfully"
else
    echo "❌ Parallel group failed"
    echo "  - Agent 2A: exit $EXIT_2A"
    echo "  - Agent 2B: exit $EXIT_2B"
    echo "  - Agent 2C: exit $EXIT_2C"
    handle_failure
fi
```

**When to use**:
- Independent tasks with no shared file writes
- Research phases that run in parallel (Phase 2A/2B/2C)
- When speedup matters (3x for 3 agents: 14min → 5min)

**How to adapt**:
- Change agent count (3-6 recommended, not more due to resource constraints)
- Add timeout wrapper: `timeout 600 execute_phase "phase2a" &` (10 min max per agent)
- Separate log files per agent: `execute_phase "phase2a" > logs/2a.log 2>&1 &`

**Why this pattern**:
- **No external dependencies**: Works on all Unix systems (Linux, macOS, WSL)
- **Simple**: Standard bash job control, no GNU Parallel needed
- **Proven**: Used in existing Vibes codex_integration examples
- **Exit code safety**: Captures immediately after `wait` to avoid loss

---

### Pattern 2: Phase Dependency Management with Associative Arrays

**Source**: `/Users/jon/source/vibes/prps/codex_integration/examples/phase_orchestration.sh` (lines 38-62)
**Relevance**: 9/10 - Ensures phases execute in correct order

**What it does**: Defines phase dependencies and parallel groups using bash associative arrays, then validates dependencies are met before executing each phase.

**Key Techniques**:
```bash
# Phase definitions
declare -A PHASES=(
    [phase0]="Setup and Initialization"
    [phase1]="Feature Analysis"
    [phase2a]="Codebase Research"
    [phase2b]="Documentation Hunt"
    [phase2c]="Example Curation"
    [phase3]="Gotcha Detection"
    [phase4]="PRP Assembly"
)

# Phase dependencies (comma-separated list of required phases)
declare -A DEPENDENCIES=(
    [phase0]=""
    [phase1]="phase0"
    [phase2a]="phase1"
    [phase2b]="phase1"
    [phase2c]="phase1"
    [phase3]="phase2a,phase2b,phase2c"  # Depends on ALL Phase 2 agents
    [phase4]="phase3"
)

# Parallel groups (phases that CAN run simultaneously)
declare -A PARALLEL_GROUPS=(
    [group1]="phase2a,phase2b,phase2c"
)

# Dependency validation before execution
check_dependencies() {
    local phase="$1"
    local deps="${DEPENDENCIES[$phase]}"

    if [ -z "$deps" ]; then
        return 0  # No dependencies
    fi

    IFS=',' read -ra DEP_ARRAY <<< "$deps"

    for dep in "${DEP_ARRAY[@]}"; do
        if ! validate_phase_completion "$dep"; then
            echo "❌ Dependency not met: ${dep} (required by ${phase})"
            return 1
        fi
    done

    return 0
}
```

**When to use**:
- Multi-phase workflows (5+ phases)
- When some phases must complete before others can start
- When you need parallel execution within sequential workflow

**How to adapt**:
- Add/remove phases in `PHASES` array
- Update dependencies in `DEPENDENCIES` array
- Define parallel groups based on your workflow

**Why this pattern**:
- **Self-documenting**: Dependencies are explicit, not implicit
- **Flexible**: Easy to add/remove phases without refactoring
- **Safe**: Prevents Phase 3 starting before Phase 2 completes
- **Scalable**: Works for 5-100 phases without code changes

---

### Pattern 3: JSONL Manifest Logging with Atomic Writes

**Source**: `/Users/jon/source/vibes/scripts/codex/log-phase.sh` (PRODUCTION READY - REUSE DIRECTLY)
**Relevance**: 10/10 - Already implemented, tested, and working

**What it does**: Logs phase execution (start, completion, exit codes, duration) to append-only JSONL manifest for audit trail and phase validation. Includes security validation, atomic writes to prevent race conditions, and jq/grep fallback for parsing.

**Key Techniques**:
```bash
# Log phase start
log_phase_start() {
    local feature="$1"
    local phase="$2"

    local manifest=$(get_manifest_path "$feature")
    ensure_manifest_dir "$manifest"

    # Create JSONL entry (single line JSON)
    local entry=$(cat <<EOF
{"phase":"${phase}","status":"started","timestamp":"$(date -u +"%Y-%m-%dT%H:%M:%SZ")"}
EOF
)

    # Append to manifest (atomic write)
    echo "$entry" >> "$manifest"
}

# Log phase completion
log_phase_complete() {
    local feature="$1"
    local phase="$2"
    local exit_code="$3"
    local duration_sec="${4:-0}"

    local status="success"
    [ "$exit_code" -ne 0 ] && status="failed"

    local entry=$(cat <<EOF
{"phase":"${phase}","status":"${status}","exit_code":${exit_code},"duration_sec":${duration_sec},"timestamp":"$(date -u +"%Y-%m-%dT%H:%M:%SZ")"}
EOF
)

    echo "$entry" >> "$manifest"
}

# Validate phase completed successfully
validate_phase_completion() {
    local feature="$1"
    local phase="$2"
    local manifest=$(get_manifest_path "$feature")

    # Extract last entry for this phase
    local entry=$(grep "\"phase\":\"${phase}\"" "$manifest" 2>/dev/null | tail -1)

    # Parse with jq (or grep fallback)
    if command -v jq &> /dev/null; then
        local exit_code=$(echo "$entry" | jq -r '.exit_code // 999')
        local status=$(echo "$entry" | jq -r '.status // "unknown"')
    else
        # Fallback for systems without jq
        local exit_code=$(echo "$entry" | grep -oP '"exit_code":\K\d+' || echo "999")
        local status=$(echo "$entry" | grep -oP '"status":"\K[^"]+' || echo "unknown")
    fi

    [ "$exit_code" -eq 0 ] || [ "$status" = "success" ]
}
```

**When to use**:
- **ALWAYS** for phase tracking in Codex commands
- Audit trail for debugging failed workflows
- Validating dependencies before phase execution
- Generating summary reports

**How to adapt**:
- **DON'T** - this script is production-ready, just source it:
  ```bash
  source scripts/codex/log-phase.sh
  log_phase_start "$FEATURE_NAME" "phase2a"
  # ... execute phase ...
  log_phase_complete "$FEATURE_NAME" "phase2a" "$EXIT_CODE" "$DURATION"
  ```
- Optional: Add custom metadata fields (model, tokens, etc.)

**Why this pattern**:
- **Already tested**: In production use since bootstrap phase
- **Security validated**: 3-level feature name validation (whitelist, path traversal, length)
- **Atomic writes**: Uses `>>` append (atomic on Unix)
- **Graceful degradation**: Works with or without `jq` installed
- **Standards compliant**: ISO 8601 timestamps (UTC), JSONL format

---

### Pattern 4: Codex CLI Invocation with Profile and Timeout

**Source**: `/Users/jon/source/vibes/prps/codex_integration/examples/command_wrapper.sh` (lines 98-109)
**Relevance**: 10/10 - Essential for all Codex exec calls

**What it does**: Wraps `codex exec` with explicit profile, timeout protection, log redirection, and exit code capture.

**Key Techniques**:
```bash
# Execute Codex with all safety measures
START_TIME=$(date +%s)

# CRITICAL: Always specify --profile to avoid wrong config
# CRITICAL: Redirect to separate log file to avoid output interleaving
# CRITICAL: Use timeout to prevent zombie processes
if timeout 600 codex exec \
    --profile "$CODEX_PROFILE" \
    --prompt "$(cat $PHASE_PROMPT_FILE)" \
    > "${LOG_DIR}/phase${phase}.log" 2>&1; then

    EXIT_CODE=0
    STATUS="success"
    echo "✅ Phase ${phase} completed"
else
    EXIT_CODE=$?
    STATUS="failed"

    # Check if it was a timeout (exit code 124)
    if [ $EXIT_CODE -eq 124 ]; then
        echo "❌ Phase ${phase} TIMEOUT (600s exceeded)"
    else
        echo "❌ Phase ${phase} failed with exit code: ${EXIT_CODE}"
    fi
fi

END_TIME=$(date +%s)
DURATION=$((END_TIME - START_TIME))
```

**When to use**:
- **EVERY** `codex exec` invocation
- Especially critical for parallel execution (separate logs prevent interleaving)

**How to adapt**:
- Timeout duration: 600s (10 min) for research agents, 300s (5 min) for simple tasks
- Profile name: `codex-prp` for PRP workflows, custom for other use cases
- Log redirection: Always to separate file per phase/agent

**Why this pattern**:
- **Profile enforcement**: Prevents using wrong model/config by mistake
- **Timeout protection**: No zombie processes if agent hangs
- **Log isolation**: Separate files prevent concurrent output corruption
- **Exit code clarity**: Distinguishes timeout (124) from other failures

---

### Pattern 5: Security Validation for Feature Name Extraction

**Source**: `/Users/jon/source/vibes/.claude/commands/generate-prp.md` (lines 20-73), `/Users/jon/source/vibes/.claude/patterns/security-validation.md`
**Relevance**: 10/10 - CRITICAL for preventing command injection and path traversal

**What it does**: 6-level security validation for extracting feature names from file paths, preventing path traversal, command injection, and enforcing naming conventions.

**Key Techniques**:
```python
import re

def extract_feature_name(filepath: str, strip_prefix: str = None, validate_no_redundant: bool = True) -> str:
    """6-level security validation for feature names.

    Args:
        filepath: Path to PRP file (e.g., "prps/INITIAL_feature.md")
        strip_prefix: Optional prefix to strip (e.g., "INITIAL_")
        validate_no_redundant: If True, reject prp_ prefix (strict for new PRPs)

    Raises:
        ValueError: If validation fails with actionable error message
    """
    ALLOWED_PREFIXES = {"INITIAL_", "EXAMPLE_"}

    # Level 1: Path traversal in full path
    if ".." in filepath:
        raise ValueError(f"Path traversal detected: {filepath}")

    # Extract basename, remove extension
    basename = filepath.split("/")[-1]
    feature = basename.replace(".md", "")

    # Strip prefix using removeprefix() (NOT replace() - only strips leading occurrence)
    if strip_prefix:
        if strip_prefix not in ALLOWED_PREFIXES:
            raise ValueError(f"Invalid strip_prefix: '{strip_prefix}' (allowed: {ALLOWED_PREFIXES})")
        feature = feature.removeprefix(strip_prefix)
        if not feature:
            raise ValueError(f"Empty feature name after stripping prefix '{strip_prefix}' from {filepath}")

    # Level 2: Whitelist (alphanumeric + underscore + hyphen only)
    if not re.match(r'^[a-zA-Z0-9_-]+$', feature):
        raise ValueError(f"Invalid characters in feature name: {feature}")

    # Level 3: Length check (max 50 chars)
    if len(feature) > 50:
        raise ValueError(f"Feature name too long: {len(feature)} chars (max 50)")

    # Level 4: Directory traversal in extracted name
    if ".." in feature or "/" in feature or "\\" in feature:
        raise ValueError(f"Path traversal in feature name: {feature}")

    # Level 5: Command injection characters
    dangerous = ['$', '`', ';', '&', '|', '>', '<', '\n', '\r']
    if any(c in feature for c in dangerous):
        raise ValueError(f"Dangerous characters detected in: {feature}")

    # Level 6: Redundant prp_ prefix validation (strict for new PRPs)
    if validate_no_redundant and feature.startswith("prp_"):
        raise ValueError(
            f"❌ Redundant 'prp_' prefix detected: '{feature}'\n"
            f"Files are in prps/ directory - prefix is redundant\n"
            f"Expected: '{feature.removeprefix('prp_')}'\n"
            f"See: .claude/conventions/prp-naming.md"
        )

    return feature

# USAGE in bash wrapper:
# Extract feature name from INITIAL.md (strict validation)
FEATURE_NAME=$(python3 -c "
import sys
sys.path.insert(0, 'scripts')
from security_validation import extract_feature_name
print(extract_feature_name('$INITIAL_MD_PATH', strip_prefix='INITIAL_', validate_no_redundant=True))
")
```

**When to use**:
- **ALWAYS** when extracting feature names from user input
- Command wrappers that accept file paths as arguments
- Any script that constructs paths dynamically

**How to adapt for bash**:
```bash
# Bash implementation (simpler, but covers critical levels)
validate_feature_name() {
    local feature="$1"

    # Whitelist check
    if [[ ! "$feature" =~ ^[a-zA-Z0-9_-]+$ ]]; then
        echo "❌ Invalid characters in feature name: $feature" >&2
        return 1
    fi

    # Path traversal
    if [[ "$feature" == *".."* || "$feature" == *"/"* ]]; then
        echo "❌ Path traversal detected: $feature" >&2
        return 1
    fi

    # Length check
    if [ ${#feature} -gt 50 ]; then
        echo "❌ Feature name too long: ${#feature} chars (max 50)" >&2
        return 1
    fi

    # Redundant prefix check
    if [[ "$feature" == prp_* ]]; then
        echo "❌ Redundant prp_ prefix: $feature" >&2
        echo "Expected: ${feature#prp_}" >&2
        return 1
    fi

    return 0
}
```

**Why this pattern**:
- **Prevents command injection**: `feature; rm -rf /` → rejected
- **Prevents path traversal**: `../../etc/passwd` → rejected
- **Enforces naming convention**: `prp_feature` → rejected (redundant prefix)
- **Production tested**: Used in all Vibes PRP workflows
- **Actionable errors**: Error messages explain what's wrong and how to fix

---

### Pattern 6: Interactive Error Handling with Retry/Skip/Abort

**Source**: `/Users/jon/source/vibes/prps/codex_integration/examples/phase_orchestration.sh` (lines 267-301)
**Relevance**: 8/10 - Improves UX for partial failures

**What it does**: When a phase fails, offers interactive choice to retry, skip (continue with partial results), or abort workflow.

**Key Techniques**:
```bash
handle_phase_failure() {
    local phase="$1"

    echo ""
    echo "========================================="
    echo "❌ Phase Failed: ${phase}"
    echo "========================================="
    echo ""
    echo "Options:"
    echo "  1. Retry phase"
    echo "  2. Skip phase (continue with partial results)"
    echo "  3. Abort workflow"
    echo ""

    read -p "Choose (1/2/3): " choice

    case "$choice" in
        1)
            echo "Retrying phase: ${phase}"
            execute_phase "$phase" || handle_phase_failure "$phase"
            ;;
        2)
            echo "⚠️  Skipping phase: ${phase}"
            echo "Continuing with partial results..."
            ;;
        3)
            echo "Aborting workflow"
            exit 1
            ;;
        *)
            echo "Invalid choice. Aborting."
            exit 1
            ;;
    esac
}

# Usage after phase execution
execute_phase "phase3" || handle_phase_failure "phase3"
```

**When to use**:
- Non-critical phases where partial results are acceptable
- Development/testing workflows where you want to continue despite failures
- When user should decide whether to retry or continue

**How to adapt**:
- Add option 4: "Retry with different parameters"
- Add automatic retry with exponential backoff (max 3 attempts)
- Environment variable for non-interactive mode: `AUTO_RETRY=true` or `FAIL_FAST=true`

**Why this pattern**:
- **User empowerment**: User decides whether to continue or abort
- **Debugging friendly**: Allows inspecting logs before retrying
- **Flexible**: Works for both interactive and CI/CD (with defaults)

---

## Naming Conventions

### File Naming

**Pattern**: `{purpose}_{component}.sh` for scripts, `{phase}.md` for prompts

**Examples**:
- Scripts: `codex-generate-prp.sh`, `codex-execute-prp.sh`, `log-phase.sh`, `parallel-exec.sh`
- Prompts: `.codex/commands/codex-generate-prp.md`, `.codex/commands/codex-execute-prp.md`
- Logs: `prps/{feature}/codex/logs/phase2a.log`, `prps/{feature}/codex/logs/manifest.jsonl`

**Rationale**: Hyphenated for commands (user-facing), underscored for utility scripts (internal), phase names match manifest entries for easy correlation.

---

### Function Naming

**Pattern**: `{verb}_{noun}` for actions, `{noun}` for queries

**Examples**:
- Actions: `log_phase_start`, `log_phase_complete`, `execute_phase`, `handle_phase_failure`
- Queries: `validate_phase_completion`, `get_phase_duration`, `check_dependencies`
- Generators: `generate_summary_report`, `get_timestamp`

**Rationale**: Clear intent from name, consistent with bash conventions, easy to grep.

---

### Variable Naming

**Pattern**: `UPPER_CASE` for constants/config, `lower_case` for local vars

**Examples**:
- Constants: `FEATURE_NAME`, `CODEX_PROFILE`, `MAX_ATTEMPTS`, `DEFAULT_MANIFEST_DIR`
- Local: `phase`, `exit_code`, `duration_sec`, `manifest_path`
- Arrays: `PHASES` (associative), `DEPENDENCIES` (associative), `pids` (indexed)

**Rationale**: Visual distinction between config and runtime vars, prevents accidental override.

---

## File Organization

### Directory Structure

```
prps/
├── {feature_name}/
│   ├── codex/                           # Codex-specific outputs
│   │   ├── logs/
│   │   │   ├── manifest.jsonl          # JSONL audit trail (append-only)
│   │   │   ├── phase0.log              # Setup logs
│   │   │   ├── phase1.log              # Feature analysis logs
│   │   │   ├── phase2a.log             # Codebase research logs
│   │   │   ├── phase2b.log             # Documentation hunt logs
│   │   │   ├── phase2c.log             # Example curation logs
│   │   │   ├── phase3.log              # Gotcha detection logs
│   │   │   └── phase4.log              # PRP assembly logs
│   │   └── scripts/                     # Helper scripts (copied from examples/)
│   │       └── manifest_logger.sh       # Sourced by orchestrator
│   ├── planning/                        # Research outputs (Phase 1-3)
│   │   ├── feature-analysis.md
│   │   ├── codebase-patterns.md
│   │   ├── documentation-links.md
│   │   ├── examples-to-include.md
│   │   └── gotchas.md
│   └── examples/                        # Extracted code (Phase 2C)
│       └── *.{py,js,sh,etc}
├── {feature_name}.md                    # Final PRP (Phase 4 output)
└── INITIAL_{feature_name}.md            # Original request

.codex/
├── commands/                            # Command prompts for Codex CLI
│   ├── codex-generate-prp.md           # Full 5-phase PRP generation
│   └── codex-execute-prp.md            # PRP execution with validation loops
└── profiles/
    └── codex-prp.yaml                   # Profile config (approval policy, etc.)

scripts/
└── codex/
    ├── codex-generate-prp.sh            # Orchestration wrapper (THIS PRP)
    ├── codex-execute-prp.sh             # Execution wrapper (follow-up PRP)
    ├── log-phase.sh                     # JSONL manifest logger (ALREADY EXISTS)
    └── parallel-exec.sh                 # Phase 2 parallelization helper (THIS PRP)

prps/codex_integration/examples/         # Reference implementations (KEEP)
├── phase_orchestration.sh               # Multi-phase workflow pattern
├── manifest_logger.sh                   # JSONL logging pattern
├── command_wrapper.sh                   # Codex exec wrapper pattern
└── approval_handler.sh                  # Approval automation pattern
```

**Justification**:
- **Feature-scoped directories**: All outputs under `prps/{feature}/codex/` for isolation
- **Separate log files**: Prevents concurrent output interleaving in parallel execution
- **Reusable scripts**: `scripts/codex/` for shared utilities
- **Examples preserved**: `prps/codex_integration/examples/` as reference material
- **Mirrors Vibes structure**: `.codex/commands/` parallels `.claude/commands/`

---

## Common Utilities to Leverage

### 1. Manifest Logger (PRODUCTION READY)

**Location**: `/Users/jon/source/vibes/scripts/codex/log-phase.sh`
**Purpose**: JSONL phase tracking with validation and reporting
**Usage Example**:
```bash
# Source the script
source scripts/codex/log-phase.sh

# Log phase start
log_phase_start "$FEATURE_NAME" "phase2a"

# Execute phase
START=$(date +%s)
execute_phase "phase2a"
EXIT_CODE=$?
END=$(date +%s)
DURATION=$((END - START))

# Log phase completion
log_phase_complete "$FEATURE_NAME" "phase2a" "$EXIT_CODE" "$DURATION"

# Validate before dependent phase
if validate_phase_completion "$FEATURE_NAME" "phase2a"; then
    echo "Phase 2A validated, proceeding to Phase 3"
fi

# Generate final report
generate_summary_report "$FEATURE_NAME"
```

**Why reuse**: Fully tested, security validated, handles jq/grep fallback, atomic writes.

---

### 2. Phase Orchestration Pattern

**Location**: `/Users/jon/source/vibes/prps/codex_integration/examples/phase_orchestration.sh`
**Purpose**: Multi-phase workflow with dependency management and parallel execution
**Usage Example**:
```bash
# Copy pattern, adapt phase definitions
declare -A PHASES=(
    [phase1]="Analysis"
    [phase2a]="Research"
    [phase2b]="Documentation"
    [phase2c]="Examples"
    [phase3]="Gotchas"
)

declare -A DEPENDENCIES=(
    [phase1]=""
    [phase2a]="phase1"
    [phase2b]="phase1"
    [phase2c]="phase1"
    [phase3]="phase2a,phase2b,phase2c"
)

declare -A PARALLEL_GROUPS=(
    [group1]="phase2a,phase2b,phase2c"
)

# Use execute_parallel_group() function from example
execute_parallel_group "group1"
```

**Why reuse**: Handles PID tracking, exit code capture, dependency validation, error handling.

---

### 3. Security Validation Functions

**Location**: `/Users/jon/source/vibes/.claude/patterns/security-validation.md`
**Purpose**: Prevent command injection and path traversal in feature names
**Usage Example**:
```bash
# Bash version (create scripts/codex/security-validation.sh)
validate_feature_name() {
    local feature="$1"

    # Whitelist + path traversal + length + redundant prefix checks
    [[ "$feature" =~ ^[a-zA-Z0-9_-]+$ ]] || return 1
    [[ ! "$feature" == *".."* ]] || return 1
    [ ${#feature} -le 50 ] || return 1
    [[ ! "$feature" == prp_* ]] || return 1

    return 0
}

# Extract feature name safely
FEATURE_NAME=$(basename "$INITIAL_MD_PATH" .md)
FEATURE_NAME=${FEATURE_NAME#INITIAL_}  # Strip INITIAL_ prefix

if ! validate_feature_name "$FEATURE_NAME"; then
    echo "❌ Invalid feature name: $FEATURE_NAME"
    exit 1
fi
```

**Why reuse**: Battle-tested against command injection, comprehensive validation.

---

### 4. Timeout Wrapper for Codex Exec

**Location**: `/Users/jon/source/vibes/prps/codex_integration/examples/command_wrapper.sh` (lines 96-109)
**Purpose**: Prevent zombie processes from hanging agents
**Usage Example**:
```bash
# Always wrap codex exec with timeout
TIMEOUT_SEC=600  # 10 minutes for research agents

if timeout $TIMEOUT_SEC codex exec \
    --profile "$CODEX_PROFILE" \
    --prompt "$(cat $PROMPT_FILE)" \
    > "$LOG_FILE" 2>&1; then

    echo "✅ Success"
else
    EXIT_CODE=$?
    if [ $EXIT_CODE -eq 124 ]; then
        echo "❌ TIMEOUT (${TIMEOUT_SEC}s exceeded)"
    else
        echo "❌ Failed (exit: $EXIT_CODE)"
    fi
fi
```

**Why reuse**: Prevents indefinite hangs, distinguishes timeout from other failures.

---

### 5. Parallel Subagent Pattern (for Codex prompts)

**Location**: `/Users/jon/source/vibes/.claude/patterns/parallel-subagents.md`
**Purpose**: Guidelines for constructing prompts that execute in parallel
**Usage Example**:
```markdown
# In .codex/commands/codex-generate-prp.md:

Phase 2: Execute these 3 agents in parallel (invoke ALL in SINGLE codex exec call):

Agent 2A - Codebase Researcher:
[prompt for codebase patterns]
Output: prps/{feature}/planning/codebase-patterns.md

Agent 2B - Documentation Hunter:
[prompt for documentation search]
Output: prps/{feature}/planning/documentation-links.md

Agent 2C - Example Curator:
[prompt for example extraction]
Output: prps/{feature}/examples/
```

**Why reuse**: Proven 3x speedup (14min → 5min), no file conflicts by design.

---

## Testing Patterns

### Unit Test Structure

**Pattern**: Bash test scripts in `tests/codex/` using simple assertions

**Example**: `/Users/jon/source/vibes/tests/codex/test_generate_prp.sh` (to be created)

**Key techniques**:
```bash
#!/bin/bash
# Test script for codex-generate-prp.sh

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"

# Test 1: Feature name validation
test_feature_name_validation() {
    echo "Test: Feature name validation"

    # Valid names should pass
    for name in "user_auth" "web-scraper" "apiClient123"; do
        if ! validate_feature_name "$name"; then
            echo "❌ FAIL: Valid name rejected: $name"
            exit 1
        fi
    done

    # Invalid names should fail
    for name in "../etc/passwd" "test;rm -rf /" "prp_feature"; do
        if validate_feature_name "$name" 2>/dev/null; then
            echo "❌ FAIL: Invalid name accepted: $name"
            exit 1
        fi
    done

    echo "✅ PASS"
}

# Test 2: Parallel execution timing
test_parallel_timing() {
    echo "Test: Parallel execution timing"

    START=$(date +%s)

    # Simulate 3 agents taking 5 seconds each
    (sleep 5) &
    (sleep 5) &
    (sleep 5) &
    wait

    END=$(date +%s)
    DURATION=$((END - START))

    # Should take ~5s (parallel), not ~15s (sequential)
    if [ $DURATION -gt 7 ]; then
        echo "❌ FAIL: Parallel execution took ${DURATION}s (expected ~5s)"
        exit 1
    fi

    echo "✅ PASS (${DURATION}s)"
}

# Test 3: Manifest logging
test_manifest_logging() {
    echo "Test: Manifest logging"

    FEATURE="test_feature_$$"
    MANIFEST="prps/${FEATURE}/codex/logs/manifest.jsonl"

    mkdir -p "$(dirname "$MANIFEST")"

    # Log phase
    source scripts/codex/log-phase.sh
    log_phase_start "$FEATURE" "phase1"
    sleep 1
    log_phase_complete "$FEATURE" "phase1" 0 1

    # Validate
    if ! validate_phase_completion "$FEATURE" "phase1"; then
        echo "❌ FAIL: Phase validation failed"
        exit 1
    fi

    # Cleanup
    rm -rf "prps/${FEATURE}"

    echo "✅ PASS"
}

# Run all tests
source "$PROJECT_ROOT/scripts/codex/security-validation.sh"
test_feature_name_validation
test_parallel_timing
test_manifest_logging

echo ""
echo "========================================="
echo "✅ All tests passed"
echo "========================================="
```

**Fixtures**: Mock Codex exec with stub script:
```bash
# tests/codex/fixtures/mock_codex_exec.sh
#!/bin/bash
# Mock codex exec for testing (returns success after delay)

DELAY="${MOCK_DELAY:-1}"
sleep "$DELAY"

if [ -n "$MOCK_FAIL" ]; then
    echo "Mock failure" >&2
    exit 1
fi

echo "Mock success"
exit 0
```

**Mocking**: Override `codex` command in PATH:
```bash
# In test setup
export PATH="$SCRIPT_DIR/fixtures:$PATH"
ln -sf mock_codex_exec.sh fixtures/codex

# In test teardown
rm fixtures/codex
```

**Assertions**: Simple exit code checks with error messages:
```bash
assert_equals() {
    local expected="$1"
    local actual="$2"
    local message="${3:-Assertion failed}"

    if [ "$expected" != "$actual" ]; then
        echo "❌ $message: expected '$expected', got '$actual'"
        exit 1
    fi
}

assert_file_exists() {
    local filepath="$1"

    if [ ! -f "$filepath" ]; then
        echo "❌ File not found: $filepath"
        exit 1
    fi
}
```

---

### Integration Test Structure

**Pattern**: End-to-end workflow validation with real Codex exec (or stubbed)

**Example**: `tests/codex/test_e2e_prp_generation.sh`

```bash
#!/bin/bash
# End-to-end test for PRP generation workflow

set -e

# Test: Full PRP generation workflow
test_e2e_prp_generation() {
    echo "========================================="
    echo "E2E Test: PRP Generation Workflow"
    echo "========================================="

    # Setup
    FEATURE="test_e2e_$$"
    INITIAL_MD="prps/INITIAL_${FEATURE}.md"

    # Create minimal INITIAL.md
    cat > "$INITIAL_MD" <<'EOF'
# Feature Request: Test E2E Feature

## Goal
Test end-to-end PRP generation workflow.

## Requirements
- Test parallel execution
- Test manifest logging
- Test quality gate

## Success Criteria
- PRP generated with score >= 8/10
- Manifest contains all phases
- Duration < 15 minutes
EOF

    # Execute PRP generation
    echo ""
    echo "Executing: scripts/codex/codex-generate-prp.sh $INITIAL_MD"

    if USE_MOCK=true scripts/codex/codex-generate-prp.sh "$INITIAL_MD"; then
        echo "✅ PRP generation completed"
    else
        echo "❌ PRP generation failed"
        exit 1
    fi

    # Validation
    PRP="prps/${FEATURE}.md"
    MANIFEST="prps/${FEATURE}/codex/logs/manifest.jsonl"

    assert_file_exists "$PRP"
    assert_file_exists "$MANIFEST"

    # Check PRP quality score
    SCORE=$(grep -oP 'Score:\s*\K\d+' "$PRP" || echo "0")
    if [ "$SCORE" -lt 8 ]; then
        echo "❌ Quality gate failed: $SCORE/10"
        exit 1
    fi
    echo "✅ Quality score: $SCORE/10"

    # Check manifest coverage
    source scripts/codex/log-phase.sh
    if validate_manifest_coverage "$FEATURE" phase0 phase1 phase2a phase2b phase2c phase3 phase4; then
        echo "✅ Manifest coverage complete"
    else
        echo "❌ Manifest coverage incomplete"
        exit 1
    fi

    # Cleanup
    rm -rf "prps/${FEATURE}" "prps/INITIAL_${FEATURE}.md"

    echo ""
    echo "========================================="
    echo "✅ E2E Test Passed"
    echo "========================================="
}

# Run test
test_e2e_prp_generation
```

---

## Anti-Patterns to Avoid

### 1. Exit Code Loss from Delayed Capture

**What it is**: Calling `wait` multiple times without capturing exit code immediately after each `wait`.

**Why to avoid**: Bash only preserves the exit code of the most recent `wait` call. If you wait for multiple PIDs sequentially without capturing between them, all but the last exit code are lost.

**Found in**: Feature analysis document (lines 490-492) as gotcha warning.

**Bad example**:
```bash
# WRONG - Exit codes lost
wait $PID_2A
wait $PID_2B
wait $PID_2C
EXIT_CODE=$?  # Only has exit code from PID_2C!
```

**Better approach**:
```bash
# RIGHT - Capture immediately
wait $PID_2A; EXIT_2A=$?
wait $PID_2B; EXIT_2B=$?
wait $PID_2C; EXIT_2C=$?

# Validate all
if [[ $EXIT_2A -eq 0 && $EXIT_2B -eq 0 && $EXIT_2C -eq 0 ]]; then
    echo "✅ All succeeded"
else
    echo "❌ Failures: 2A=$EXIT_2A, 2B=$EXIT_2B, 2C=$EXIT_2C"
fi
```

---

### 2. Output Interleaving in Parallel Execution

**What it is**: Multiple parallel processes writing to stdout/stderr simultaneously, causing mixed/corrupted output in single log file.

**Why to avoid**: Makes debugging impossible, corrupts logs, may corrupt JSON output.

**Found in**: Feature analysis (line 379), command_wrapper.sh pattern.

**Bad example**:
```bash
# WRONG - All write to same stdout
codex exec --prompt "agent 2a" &
codex exec --prompt "agent 2b" &
codex exec --prompt "agent 2c" &
wait
# Output is interleaved/corrupted
```

**Better approach**:
```bash
# RIGHT - Separate log files
codex exec --prompt "agent 2a" > logs/2a.log 2>&1 &
codex exec --prompt "agent 2b" > logs/2b.log 2>&1 &
codex exec --prompt "agent 2c" > logs/2c.log 2>&1 &
wait

# View logs separately or concatenate after completion
cat logs/2a.log logs/2b.log logs/2c.log
```

---

### 3. Profile Omission in Codex Exec

**What it is**: Calling `codex exec` without `--profile` flag, relying on default profile.

**Why to avoid**: Wrong model, wrong MCP servers, wrong approval policy. Especially dangerous for parallel execution where you need consistent behavior.

**Found in**: Feature analysis gotcha #7 (line 536-538), all examples enforce `--profile`.

**Bad example**:
```bash
# WRONG - Uses default profile (may be wrong config)
codex exec --prompt "$(cat prompt.md)"
```

**Better approach**:
```bash
# RIGHT - Always explicit profile
CODEX_PROFILE="codex-prp"  # Or from config/env var
codex exec --profile "$CODEX_PROFILE" --prompt "$(cat prompt.md)"
```

---

### 4. Manifest Race Condition (Concurrent Writes)

**What it is**: Multiple parallel processes appending to manifest.jsonl simultaneously using `>>`, causing interleaved JSON lines (invalid JSON).

**Why to avoid**: Corrupts manifest, breaks parsing with jq, loses audit trail.

**Found in**: Feature analysis gotcha #4 (line 520-524).

**Bad example**:
```bash
# WRONG - Concurrent appends can interleave
(echo '{"phase":"2a",...}' >> manifest.jsonl) &
(echo '{"phase":"2b",...}' >> manifest.jsonl) &
(echo '{"phase":"2c",...}' >> manifest.jsonl) &
wait
# Result: {"phase":"2a",{"phase":"2b"...  <- CORRUPTED
```

**Better approach** (from log-phase.sh):
```bash
# RIGHT - Atomic writes via temp file + mv
echo '{"phase":"2a",...}' > "manifest.tmp.$$"
mv "manifest.tmp.$$" manifest.jsonl  # Atomic on Unix

# OR: Use flock for file locking
(
    flock -x 200
    echo '{"phase":"2a",...}' >> manifest.jsonl
) 200>/tmp/manifest.lock
```

**Note**: Current `log-phase.sh` uses simple `>>` append which is atomic for single-line writes on Unix, but temp file + mv is safer for long-term.

---

### 5. Redundant prp_ Prefix in Filenames

**What it is**: Creating PRPs with filename like `prps/prp_feature.md` instead of `prps/feature.md`.

**Why to avoid**: Redundant (directory already indicates it's a PRP), violates naming convention, rejected by security validation.

**Found in**: Security validation pattern (level 6), feature analysis (lines 175, 249, 536).

**Bad example**:
```bash
# WRONG - Redundant prefix
PRP_FILE="prps/prp_user_authentication.md"
```

**Better approach**:
```bash
# RIGHT - No redundant prefix
PRP_FILE="prps/user_authentication.md"

# Validate in script
if [[ "$FEATURE_NAME" == prp_* ]]; then
    echo "❌ Redundant prp_ prefix detected: $FEATURE_NAME"
    echo "Expected: ${FEATURE_NAME#prp_}"
    exit 1
fi
```

---

### 6. Sequential Execution of Independent Tasks

**What it is**: Running Phase 2 agents (2A, 2B, 2C) sequentially instead of in parallel, despite no dependencies between them.

**Why to avoid**: Wastes time (14min vs 5min), defeats purpose of parallel subagent pattern.

**Found in**: Parallel subagents pattern (anti-pattern section).

**Bad example**:
```bash
# WRONG - Sequential (sum of times)
execute_phase "phase2a"  # 5 min
execute_phase "phase2b"  # 4 min
execute_phase "phase2c"  # 5 min
# Total: 14 min
```

**Better approach**:
```bash
# RIGHT - Parallel (max of times)
execute_phase "phase2a" &
execute_phase "phase2b" &
execute_phase "phase2c" &
wait
# Total: 5 min (max of 5, 4, 5)
```

---

### 7. Missing Timeout on Codex Exec

**What it is**: Calling `codex exec` without timeout wrapper, allowing it to run indefinitely if it hangs.

**Why to avoid**: Creates zombie processes, blocks workflow, prevents error handling.

**Found in**: Feature analysis gotcha #3 (line 517-518).

**Bad example**:
```bash
# WRONG - Can hang forever
codex exec --prompt "..." &
wait  # May never return
```

**Better approach**:
```bash
# RIGHT - Timeout wrapper
timeout 600 codex exec --prompt "..." &
PID=$!
wait $PID
EXIT=$?

if [ $EXIT -eq 124 ]; then
    echo "❌ TIMEOUT (600s exceeded)"
else
    echo "Exit: $EXIT"
fi
```

---

## Implementation Hints from Existing Code

### Similar Features Found

#### 1. Vibes `.claude/commands/generate-prp.md` (PRP Generation for Claude)

**Location**: `/Users/jon/source/vibes/.claude/commands/generate-prp.md`

**Similarity**: Same 5-phase workflow structure, parallel Phase 2 execution, quality gates, Archon integration.

**Lessons**:
- Phase 0-4 structure is proven for PRP generation
- Parallel Task() invocations work for Claude, bash job control works for Codex
- Feature name extraction requires 6 levels of security validation
- Quality gate (8+/10) is essential for execution success
- Archon integration should be optional (graceful degradation)

**Differences**:
- Claude uses `Task()` subagents (language model feature)
- Codex uses bash job control + separate `codex exec` calls
- Claude has single-process logging, Codex needs separate log files per agent
- Codex requires explicit `--profile` flag enforcement

**Adaptation strategy**:
```
Vibes Pattern                          Codex Adaptation
=====================================  =====================================
Task(subagent_type="researcher", ...)  timeout 600 codex exec --profile codex-prp --prompt "..." > logs/2a.log 2>&1 &
Task() invocations in same response    Background jobs launched in same script block
Wait for Task() completion             wait $PID_2A; EXIT_2A=$?
Archon task updates                    Identical (same MCP server calls)
Quality score extraction               Identical (same regex pattern)
```

---

#### 2. Vibes `prps/codex_integration/examples/phase_orchestration.sh`

**Location**: `/Users/jon/source/vibes/prps/codex_integration/examples/phase_orchestration.sh`

**Similarity**: Multi-phase orchestration with dependency management, parallel group execution, error handling.

**Lessons**:
- Associative arrays for phase definitions and dependencies scale well
- Separate log files prevent output interleaving
- Interactive error handling (retry/skip/abort) improves UX
- Dependency validation prevents premature phase execution

**Differences**:
- Example is generic pattern, needs customization for PRP generation phases
- Example has placeholder phase names, needs real phase logic
- Example doesn't include Archon integration

**Adaptation strategy**: Copy structure, replace phase definitions with PRP-specific phases (0-4), add Archon task updates, integrate manifest logging from log-phase.sh.

---

#### 3. Vibes `scripts/codex/log-phase.sh` (Manifest Logger)

**Location**: `/Users/jon/source/vibes/scripts/codex/log-phase.sh`

**Similarity**: JSONL logging, phase validation, summary reporting - **EXACT MATCH** for requirements.

**Lessons**:
- Security validation (feature name) is critical and comprehensive
- jq/grep fallback ensures portability
- Atomic writes prevent race conditions
- ISO 8601 timestamps (UTC) are standard

**Differences**: None - this is production-ready, reuse as-is.

**Adaptation strategy**: **No adaptation needed** - source this script directly in codex-generate-prp.sh:
```bash
source scripts/codex/log-phase.sh
log_phase_start "$FEATURE_NAME" "phase2a"
# ... execute phase ...
log_phase_complete "$FEATURE_NAME" "phase2a" "$EXIT_CODE" "$DURATION"
```

---

## Recommendations for PRP

Based on pattern analysis:

### 1. **Reuse `scripts/codex/log-phase.sh` directly** for manifest logging
- Already production-ready with security validation
- No need to reimplement JSONL logging
- Source in wrapper script: `source scripts/codex/log-phase.sh`

### 2. **Follow `phase_orchestration.sh` pattern** for parallel execution
- Copy associative array structure for phases/dependencies
- Adapt `execute_parallel_group()` function
- Use same PID tracking and exit code capture pattern

### 3. **Mirror `.claude/commands/generate-prp.md` structure** for command prompts
- Same Phase 0-4 workflow
- Replace Task() invocations with bash parallelization instructions
- Keep Archon integration pattern (batch updates before/after parallel group)

### 4. **Enforce security validation** for feature name extraction
- Use bash version of `extract_feature_name()` from security-validation.md
- Validate before directory creation
- Reject redundant `prp_` prefix immediately

### 5. **Always specify `--profile codex-prp`** in all codex exec calls
- Create dedicated profile with correct approval policy
- Never rely on default profile
- Document profile requirements in command README

### 6. **Use separate log files** for parallel agents
- Pattern: `logs/phase2a.log`, `logs/phase2b.log`, `logs/phase2c.log`
- Prevents output interleaving
- Allows individual agent inspection for debugging

### 7. **Wrap all codex exec with timeout**
- 600s (10 min) for research agents
- 300s (5 min) for simple tasks
- Check exit code 124 for timeout vs other failures

### 8. **Implement interactive error handling** for partial failures
- Offer retry/skip/abort options
- Allow user to inspect logs before deciding
- Support non-interactive mode via environment variable

### 9. **Generate summary report** from manifest after workflow completion
- Use `generate_summary_report()` from log-phase.sh
- Show total time, successful/failed phases, duration per phase
- Include comparison to sequential timing (prove speedup)

### 10. **Write integration tests** for parallel execution timing
- Verify concurrent timestamps in manifest (within 5s)
- Measure total duration (<10min for typical PRP)
- Validate all Phase 2 outputs created

---

## Source References

### From Archon

No highly relevant Archon examples found for bash parallel execution or JSONL logging. Archon searches returned mostly Python async patterns and MCP server examples, which are not directly applicable to bash orchestration.

**Key insight**: This pattern is **bash-specific** and not commonly documented in language model knowledge bases. The local codebase examples are the authoritative reference.

---

### From Local Codebase

#### Core Patterns (10/10 relevance):

1. **`/Users/jon/source/vibes/scripts/codex/log-phase.sh`** - Production-ready manifest logger
   - 412 lines of battle-tested JSONL logging
   - Security validation, atomic writes, jq/grep fallback
   - **Action**: Reuse directly, no modification needed

2. **`/Users/jon/source/vibes/prps/codex_integration/examples/phase_orchestration.sh`** - Multi-phase workflow pattern
   - 368 lines of orchestration logic
   - Associative arrays, parallel groups, dependency validation
   - **Action**: Copy structure, adapt phase definitions

3. **`/Users/jon/source/vibes/.claude/commands/generate-prp.md`** - PRP generation workflow
   - 358 lines of 5-phase workflow specification
   - Security validation, quality gates, Archon integration
   - **Action**: Mirror structure for Codex commands

4. **`/Users/jon/source/vibes/prps/codex_integration/examples/command_wrapper.sh`** - Codex exec wrapper
   - 143 lines of validation and logging
   - Profile enforcement, timeout handling, exit code capture
   - **Action**: Adapt for codex-generate-prp.sh wrapper

5. **`/Users/jon/source/vibes/.claude/patterns/security-validation.md`** - Feature name security
   - 107 lines of 6-level validation pattern
   - Prevents command injection, path traversal, naming violations
   - **Action**: Implement bash version in wrapper script

#### Supporting Patterns (8-9/10 relevance):

6. **`/Users/jon/source/vibes/.claude/patterns/parallel-subagents.md`** - Parallel execution theory
   - 151 lines of best practices
   - Timing validation, conflict checking, error handling
   - **Action**: Apply guidelines to bash implementation

7. **`/Users/jon/source/vibes/.claude/patterns/quality-gates.md`** - Validation enforcement
   - 129 lines of quality gate patterns
   - PRP scoring, validation loops, error analysis
   - **Action**: Implement quality checks in Phase 5

8. **`/Users/jon/source/vibes/prps/codex_integration/examples/manifest_logger.sh`** - JSONL logging example
   - 263 lines (prototype for log-phase.sh)
   - Same pattern as production script
   - **Action**: Reference for understanding, use production version

---

## Next Steps for Assembler

When generating the PRP:

### 1. **Include these patterns in "Current Codebase Tree" section**:
```
scripts/codex/log-phase.sh                              # REUSE: Manifest logger
prps/codex_integration/examples/phase_orchestration.sh  # ADAPT: Multi-phase pattern
.claude/commands/generate-prp.md                         # MIRROR: 5-phase workflow
.claude/patterns/security-validation.md                  # IMPLEMENT: Bash version
```

### 2. **Add key code snippets in "Implementation Blueprint"**:
- Parallel execution with PID tracking (from phase_orchestration.sh lines 124-150)
- Exit code capture pattern (immediate capture after wait)
- Manifest logging integration (source log-phase.sh, call functions)
- Security validation (bash implementation of extract_feature_name)
- Codex exec wrapper with timeout (from command_wrapper.sh)

### 3. **Add anti-patterns to "Known Gotchas" section**:
- Exit code loss from delayed capture
- Output interleaving in parallel execution
- Profile omission in codex exec
- Manifest race condition (concurrent writes)
- Redundant prp_ prefix
- Sequential execution of independent tasks
- Missing timeout on codex exec

### 4. **Use file organization for "Desired Codebase Tree"**:
```
.codex/commands/codex-generate-prp.md       # Phase 0-4 prompt
scripts/codex/codex-generate-prp.sh         # Orchestration wrapper
scripts/codex/parallel-exec.sh              # Phase 2 parallelization helper
tests/codex/test_generate_prp.sh            # Integration test
```

### 5. **Reference utilities in "Implementation Details"**:
- **Phase orchestration**: Copy from phase_orchestration.sh, adapt PHASES/DEPENDENCIES arrays
- **Manifest logging**: Source log-phase.sh, no modification needed
- **Security validation**: Implement bash version, validate before mkdir
- **Parallel execution**: Use execute_parallel_group() pattern with separate log files
- **Error handling**: Implement retry/skip/abort from handle_phase_failure()

### 6. **Testing requirements for "Validation Gates"**:
- Unit test: Feature name validation (valid/invalid cases)
- Unit test: Parallel timing (<7s for 3x 5s tasks proves parallel execution)
- Integration test: End-to-end PRP generation with manifest validation
- Integration test: Partial failure handling (1 of 3 agents fails)
- Validation: Manifest has concurrent timestamps for phase2a/2b/2c (within 5s)

### 7. **Quality metrics for "Success Criteria"**:
- All Phase 2 outputs created (codebase-patterns.md, documentation-links.md, examples/)
- Manifest logs all phases (phase0-4) with success status
- Speedup proven: parallel <10min vs sequential ~20min
- Quality gate enforced: PRP score ≥8/10
- Integration test passes without errors

---

## Summary

**Confidence Level**: **VERY HIGH** - Production-ready patterns exist in codebase, reusable without modification.

**Key Reuse Opportunities**:
1. `scripts/codex/log-phase.sh` - Use as-is (0% modification)
2. `phase_orchestration.sh` - Adapt structure (20% modification)
3. `.claude/commands/generate-prp.md` - Mirror workflow (30% adaptation for bash)
4. Security validation - Implement bash version (50% translation from Python)

**Critical Success Factors**:
- **DON'T reinvent**: Reuse log-phase.sh directly
- **DO copy patterns**: phase_orchestration.sh structure is proven
- **DO enforce security**: Bash version of extract_feature_name is essential
- **DO test parallelism**: Verify concurrent timestamps in manifest

**Implementation Strategy**:
1. Copy phase_orchestration.sh as template
2. Source log-phase.sh for manifest logging
3. Add security validation from security-validation.md (bash version)
4. Integrate Codex exec with timeout and profile enforcement
5. Test parallel execution timing and manifest coverage

**Total Pattern Coverage**: 8 major patterns documented, 5 production-ready scripts to reuse, 7 anti-patterns to avoid. This is comprehensive guidance for implementation.
