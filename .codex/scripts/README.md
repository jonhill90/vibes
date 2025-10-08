# Codex Scripts - Technical Documentation

**Internal/technical documentation for Codex PRP generation and execution scripts**

---

## Architecture Overview

The Codex workflow consists of **5 core scripts** that orchestrate PRP generation and execution:

```
.codex/scripts/
├── codex-generate-prp.sh      # Main orchestrator (Phase 0-4)
├── codex-execute-prp.sh       # Validation loop orchestrator
├── parallel-exec.sh           # Phase 2 parallel execution
├── security-validation.sh     # 6-level feature name validation
├── quality-gate.sh            # PRP quality enforcement (≥8/10)
└── log-phase.sh               # JSONL manifest logging (PRODUCTION)
```

**Additional Scripts** (infrastructure):
- `validate-bootstrap.sh` - Validate initial setup
- `validate-config.sh` - Validate Codex profile configuration

---

## Dependency Graph

Shows which scripts call which:

```
codex-generate-prp.sh
├── sources: log-phase.sh
├── sources: security-validation.sh
├── sources: parallel-exec.sh
└── calls: codex exec (5 times: phase1, phase2a, phase2b, phase2c, phase3, phase4)

codex-execute-prp.sh
├── sources: log-phase.sh
├── sources: security-validation.sh
└── calls: ruff, mypy, pytest (validation loop)

parallel-exec.sh
├── sources: log-phase.sh
└── calls: codex exec (3 times in parallel: phase2a, phase2b, phase2c)

security-validation.sh
└── (no external dependencies - pure Bash)

quality-gate.sh
├── sources: security-validation.sh
└── (reads PRP files)

log-phase.sh
└── sources: security-validation.sh
```

**Key Insight**: All scripts source `security-validation.sh` (6-level validation foundation)

---

## Script 1: `codex-generate-prp.sh`

**Purpose**: Orchestrate full 5-phase PRP generation with parallel Phase 2

**Pattern Source**: `prps/codex_integration/examples/phase_orchestration.sh`

### Architecture

```bash
main()
├── validate input (security-validation.sh)
├── check Archon availability (graceful degradation)
└── execute phases sequentially:
    ├── execute_phase0_setup()           # Setup (60s)
    ├── execute_sequential_phase(phase1)  # Feature analysis (600s)
    ├── execute_phase2_parallel()        # PARALLEL (3 agents, 600s each) ← SPEEDUP
    ├── execute_sequential_phase(phase3)  # Gotcha detection (600s)
    └── execute_sequential_phase(phase4)  # PRP assembly (900s)
```

### Phase Execution Flow

```bash
execute_sequential_phase(feature, phase, prompt_file)
├── check_dependencies()           # Validate prerequisites
├── log_phase_start()              # JSONL manifest logging
├── timeout ... codex exec         # With timeout wrapper
├── log_phase_complete()           # JSONL manifest logging
└── handle_phase_failure()         # Interactive retry/skip/abort
```

### Parallel Phase 2 Flow

```bash
execute_phase2_parallel(feature)
├── check_dependencies()           # All Phase 2 agents
├── archon_update_task_status()    # Mark tasks "doing"
├── execute_parallel_group()       # FROM parallel-exec.sh
│   ├── timeout ... codex exec --profile codex-prp ... &   # Agent 2A
│   ├── timeout ... codex exec --profile codex-prp ... &   # Agent 2B
│   ├── timeout ... codex exec --profile codex-prp ... &   # Agent 2C
│   ├── wait $PID_2A; EXIT_2A=$?  # CRITICAL: immediate capture
│   ├── wait $PID_2B; EXIT_2B=$?
│   └── wait $PID_2C; EXIT_2C=$?
└── archon_update_task_status()    # Mark tasks "done"
```

### Configuration

```bash
# Timeouts (seconds)
PHASE0_TIMEOUT=60       # Setup
PHASE1_TIMEOUT=600      # Feature analysis
PHASE2_TIMEOUT=600      # Per Phase 2 agent (concurrent)
PHASE3_TIMEOUT=600      # Gotcha detection
PHASE4_TIMEOUT=900      # PRP assembly

# Codex profile
CODEX_PROFILE="${CODEX_PROFILE:-codex-prp}"

# Quality gate
MIN_PRP_SCORE=8
MAX_REGENERATION_ATTEMPTS=3
```

### Gotchas Addressed

| Gotcha | Implementation |
|--------|---------------|
| #1: Exit code timing | `wait $PID; EXIT=$?` (immediate) |
| #2: Security bypass | `extract_feature_name()` with 6-level validation |
| #3: Zombie processes | `timeout --kill-after=5s ${timeout}s codex exec` |
| #4: Profile omission | `--profile "$CODEX_PROFILE"` in all exec calls |
| #6: Sequential execution | `execute_phase2_parallel()` with `&` + `wait` |
| #11: Dependency validation | `check_dependencies()` before each phase |

### Error Handling

```bash
handle_phase_failure(feature, phase, exit_code)
├── Show last 20 lines of log
└── Offer interactive choices:
    ├── 1. Retry (same timeout)
    ├── 2. Retry (+50% timeout)
    ├── 3. Skip (continue with partial results)
    └── 4. Abort
```

### Archon Integration

```bash
# Check availability (graceful degradation)
check_archon_availability()
├── command -v archon              # CLI exists?
└── timeout 3s archon health-check # Server responding?

# Initialize project and tasks
archon_initialize_project(feature)
├── create project: "PRP: {feature}"
└── create tasks:
    ├── phase0 (priority 100)
    ├── phase1 (priority 95)
    ├── phase2a (priority 90)
    ├── phase2b (priority 85)
    ├── phase2c (priority 80)
    ├── phase3 (priority 75)
    └── phase4 (priority 70)

# Update task status
archon_update_task_status(phase, status)
├── Statuses: "todo", "doing", "done", "blocked"
└── Graceful: ignores errors to prevent workflow disruption
```

---

## Script 2: `codex-execute-prp.sh`

**Purpose**: Execute PRP with validation loop (ruff → mypy → pytest → coverage)

**Pattern Source**: `.claude/patterns/quality-gates.md`

### Architecture

```bash
main()
├── extract_feature_from_prp()     # Security validation
├── setup directories
├── log_phase_start()
├── run_validation_loop()          # Max 5 attempts
│   └── for each attempt:
│       ├── validate_level1_syntax()    # ruff + mypy
│       ├── validate_level2_tests()     # pytest
│       └── validate_level3_coverage()  # pytest --cov
├── log_phase_complete()
└── generate_completion_report()
```

### Validation Loop Flow

```bash
run_validation_loop(feature, prp_path)
├── extract_gotchas_from_prp()     # For error analysis
└── for attempt in 1..MAX_VALIDATION_ATTEMPTS:
    ├── validate_level1_syntax()
    │   ├── ruff check --fix        # Auto-fix linting
    │   └── mypy                     # Type checking
    ├── validate_level2_tests()
    │   └── pytest tests/ -v         # Unit tests
    ├── validate_level3_coverage()
    │   ├── pytest --cov             # Coverage measurement
    │   └── check ≥70% threshold
    └── on failure:
        ├── analyze_validation_error()  # Search gotchas
        └── pause for manual fixes
```

### Validation Levels

**Level 1: Syntax & Style** (timeout: 300s)
```bash
validate_level1_syntax(feature)
├── ruff check --fix .               # Python linter (auto-fix)
└── mypy . --config-file pyproject.toml  # Type checking
```

**Level 2: Unit Tests** (timeout: 600s)
```bash
validate_level2_tests(feature)
└── pytest tests/ -v                 # All tests must pass
```

**Level 3: Coverage** (timeout: 900s)
```bash
validate_level3_coverage(feature)
├── pytest --cov=. --cov-report=term-missing
└── extract coverage % and check ≥70%
```

### Error Analysis

```bash
analyze_validation_error(error_log, prp_gotchas, level)
├── Extract error type:
│   ├── import_error (ImportError, ModuleNotFoundError)
│   ├── type_error (TypeError, AttributeError)
│   ├── assertion_error (AssertionError)
│   ├── syntax_error (SyntaxError, IndentationError)
│   ├── timeout (TimeoutError)
│   ├── linting_error (ruff)
│   └── type_checking_error (mypy)
├── Show first 20 lines of error
└── Search PRP gotchas for relevant solution
```

### Completion Report

Generated at: `prps/{feature}/codex/logs/execution_report.md`

```markdown
# PRP Execution Completion Report

**Status**: success | partial | failed
**Validation Attempts**: X/5
**Test Coverage**: XX%

## Validation Results
- Level 1: ✅ PASSED
- Level 2: ✅ PASSED
- Level 3: ✅ PASSED

## Files Changed
- [list of modified files]

## Recommendations
[next steps based on status]
```

---

## Script 3: `parallel-exec.sh`

**Purpose**: Execute multiple phases in parallel with PID tracking and exit code capture

**Pattern Source**: `prps/codex_integration/examples/phase_orchestration.sh` (lines 112-161)

### Core Function

```bash
execute_parallel_group(feature, group_name, phase1, phase2, phase3, ...)
├── Setup log directory
├── log_phase_start() for each phase  # Separate manifests (GOTCHA #9)
├── Launch agents in parallel:
│   ├── timeout ... codex exec ... > log_2a.log 2>&1 &
│   ├── PID_2A=$!  # CRITICAL: immediate capture (GOTCHA #7)
│   ├── timeout ... codex exec ... > log_2b.log 2>&1 &
│   ├── PID_2B=$!
│   ├── timeout ... codex exec ... > log_2c.log 2>&1 &
│   └── PID_2C=$!
├── Wait for each PID:
│   ├── wait $PID_2A; EXIT_2A=$?  # CRITICAL: immediate (GOTCHA #1)
│   ├── wait $PID_2B; EXIT_2B=$?
│   └── wait $PID_2C; EXIT_2C=$?
├── log_phase_complete() for each phase
└── Report success/failure with exit codes
```

### Exit Code Interpretation

```bash
case $exit_code in
    0)   "✅ SUCCESS"
    124) "❌ TIMEOUT (exceeded ${timeout}s)"      # GNU timeout
    125) "❌ TIMEOUT COMMAND FAILED"              # timeout not installed
    137) "❌ KILLED (SIGKILL)"                    # Force killed
    *)   "❌ FAILED (exit ${exit_code})"
esac
```

### Speedup Calculation

```bash
calculate_speedup(feature, phases...)
├── Get duration for each phase
├── total_sequential = sum of all durations
├── max_parallel = max of all durations
└── speedup = (total_sequential / max_parallel) * 100
```

**Example**:
- Phase 2A: 5 minutes
- Phase 2B: 4 minutes
- Phase 2C: 5 minutes
- Sequential: 14 minutes
- Parallel: 5 minutes (max)
- **Speedup: 280% (2.8x)**

### Gotchas Addressed

| Gotcha | Implementation |
|--------|---------------|
| #1: Exit code timing | `wait $PID; EXIT=$?` semicolon ensures immediate capture |
| #3: Timeout wrapper | All agents wrapped with `timeout --kill-after=5s` |
| #5: Output interleaving | Separate log file per agent: `> log_${phase}.log 2>&1` |
| #7: PID race condition | PIDs captured with `$!` immediately after `&` |
| #8: Timeout exit codes | Case statement for 124, 125, 137 special handling |

---

## Script 4: `security-validation.sh`

**Purpose**: Prevent path traversal and command injection in feature names

**Pattern Source**: `.claude/patterns/security-validation.md`

### 6-Level Validation

```bash
validate_feature_name(feature)
├── Level 1: Path traversal (.., /, \)
├── Level 2: Whitelist (alphanumeric + _ + - only)
├── Level 3: Length check (max 50 chars)
├── Level 4: Dangerous characters ($, `, ;, &, |, <, >)
├── Level 5: Redundant prp_ prefix (optional check)
└── Level 6: Reserved names (., .., CON, NUL, etc.)
```

### Feature Name Extraction

```bash
extract_feature_name(filepath, strip_prefix, validate_no_redundant)
├── Check for path traversal in full path
├── Extract basename: ${filepath##*/}
├── Remove .md extension: ${basename%.md}
├── Strip prefix: ${feature#"$strip_prefix"}  # GOTCHA #13: NOT ${//}
└── validate_feature_name()
```

### Critical Gotcha: removeprefix() vs replace()

```bash
# ❌ WRONG - Removes ALL occurrences
basename="INITIAL_INITIAL_test"
feature="${basename//INITIAL_/}"
# Result: "test" (wrong! removed both)

# ✅ RIGHT - Only removes from start (like Python's removeprefix())
feature="${basename#INITIAL_}"
# Result: "INITIAL_test" (correct! only prefix)
```

### Examples

**Valid**:
- `user_auth` ✅
- `web-scraper` ✅
- `apiClient123` ✅
- `TEST_Feature-v2` ✅

**Invalid**:
- `../../etc/passwd` ❌ (path traversal)
- `test;rm -rf /` ❌ (command injection)
- `test$(whoami)` ❌ (command injection)
- `prp_feature` ❌ (redundant prefix)
- `very_long_feature_name_that_exceeds_the_maximum_length_limit_of_fifty_characters` ❌ (too long)
- `.` ❌ (reserved name)
- `CON` ❌ (reserved Windows name)

---

## Script 5: `quality-gate.sh`

**Purpose**: Extract PRP quality score and enforce ≥8/10 minimum

**Pattern Source**: `prps/codex_commands/examples/quality_gate.sh`

### Score Extraction

```bash
extract_prp_score(prp_file)
├── Read PRP file
├── Search for pattern: "Score: X/10" (case-insensitive)
├── Extract numeric score with sed
└── Validate 0-10 range
```

**Regex Pattern**:
```bash
grep -iE '\*?\*?[Ss]core[[:space:]]*:[[:space:]]*[0-9]+/10' "$prp_file"
```

**Matches**:
- `Score: 8/10` ✅
- `**Score: 9/10**` ✅
- `Score:10/10` ✅
- `score : 7/10` ✅

### Quality Gate Enforcement

```bash
enforce_quality_gate(prp_file, min_score=8, max_attempts=3, current_attempt=1)
├── extract_prp_score()
├── if score ≥ min_score: return 0 (PASS)
├── if score < min_score:
│   ├── show_scoring_guidance()
│   ├── if current_attempt < max_attempts:
│   │   ├── Offer: Regenerate (1)
│   │   ├── Offer: Accept anyway (2)
│   │   └── Offer: Abort (3)
│   └── if current_attempt ≥ max_attempts:
│       └── Offer: Accept or abort
└── return exit code (0=pass, 1=fail)
```

### Scoring Guidance

**10/10 PRP has**:
- ✅ Comprehensive context from all 5 phases
- ✅ Clear task breakdown with specific steps
- ✅ Proven patterns with file references
- ✅ All gotchas documented with solutions
- ✅ Complete validation strategy
- ✅ Example code from codebase
- ✅ Documentation links with sections
- ✅ Error handling patterns included

**Common reasons for <8/10**:
- ❌ Missing research documents (Phase 2 incomplete)
- ❌ No codebase patterns identified
- ❌ No example code included
- ⚠️ Vague task descriptions (not actionable)
- ⚠️ Missing gotcha documentation
- ⚠️ No validation commands specified
- ⚠️ Generic patterns (not project-specific)

---

## Script 6: `log-phase.sh`

**Purpose**: JSONL manifest logging with security validation

**Status**: **PRODUCTION READY** (reused from Codex integration bootstrap)

### Core Functions

```bash
log_phase_start(feature, phase)
├── validate_feature_name()           # 6-level security
├── create manifest file if missing
└── append JSON entry:
    {
      "phase": "phase1",
      "status": "started",
      "timestamp": "2025-10-07T12:34:56Z",
      "pid": 12345
    }
```

```bash
log_phase_complete(feature, phase, exit_code, duration)
├── validate_feature_name()
└── append JSON entry:
    {
      "phase": "phase1",
      "status": "completed",
      "exit_code": 0,
      "duration": 120,
      "timestamp": "2025-10-07T12:36:56Z"
    }
```

```bash
validate_phase_completion(feature, phase)
├── Read manifest
├── Check for "status": "completed" with exit_code 0
└── Return 0 (success) or 1 (failure/missing)
```

### Manifest Format

**Location**: `prps/{feature}/codex/logs/manifest.jsonl`

**Format**: JSONL (JSON Lines) - one JSON object per line

**Example**:
```jsonl
{"phase":"phase0","status":"started","timestamp":"2025-10-07T12:30:00Z","pid":10001}
{"phase":"phase0","status":"completed","exit_code":0,"duration":5,"timestamp":"2025-10-07T12:30:05Z"}
{"phase":"phase1","status":"started","timestamp":"2025-10-07T12:30:05Z","pid":10002}
{"phase":"phase1","status":"completed","exit_code":0,"duration":300,"timestamp":"2025-10-07T12:35:05Z"}
{"phase":"phase2a","status":"started","timestamp":"2025-10-07T12:35:05Z","pid":10003}
{"phase":"phase2b","status":"started","timestamp":"2025-10-07T12:35:06Z","pid":10004}
{"phase":"phase2c","status":"started","timestamp":"2025-10-07T12:35:07Z","pid":10005}
{"phase":"phase2a","status":"completed","exit_code":0,"duration":280,"timestamp":"2025-10-07T12:39:45Z"}
{"phase":"phase2b","status":"completed","exit_code":0,"duration":240,"timestamp":"2025-10-07T12:39:06Z"}
{"phase":"phase2c","status":"completed","exit_code":0,"duration":285,"timestamp":"2025-10-07T12:39:52Z"}
```

**Proof of Parallelism**: Phase 2 start timestamps within 5 seconds (12:35:05, 12:35:06, 12:35:07)

---

## Testing Guide

### Unit Tests (Per Script)

**Security Validation Tests**:
```bash
# Test valid names
test_valid_names() {
    for name in "user_auth" "web-scraper" "apiClient123"; do
        if validate_feature_name "$name"; then
            echo "✅ $name valid"
        else
            echo "❌ $name should be valid"
        fi
    done
}

# Test invalid names
test_invalid_names() {
    for name in "../../etc" "test;rm" "prp_feature"; do
        if ! validate_feature_name "$name"; then
            echo "✅ $name rejected correctly"
        else
            echo "❌ $name should be rejected"
        fi
    done
}

# Run tests
source .codex/scripts/security-validation.sh
test_valid_names
test_invalid_names
```

**Parallel Execution Tests**:
```bash
# Run built-in self-tests
bash .codex/scripts/parallel-exec.sh --test
# ✅ Test 1 PASSED: All agents succeeded
# ✅ Parallel execution confirmed (2s ≤ 3s)
# ✅ Test 2 PASSED: Exit codes captured correctly
# ✅ All Tests Passed
```

---

### Integration Tests

**Test 1: End-to-End PRP Generation**:
```bash
#!/bin/bash
# tests/codex/test_generate_prp.sh

set -euo pipefail

# Create test INITIAL.md
cat > prps/INITIAL_test_feature.md <<'EOF'
# INITIAL: Test Feature
Simple test feature for validation
EOF

# Run generation
./.codex/scripts/codex-generate-prp.sh prps/INITIAL_test_feature.md

# Validate PRP created
if [ ! -f "prps/test_feature.md" ]; then
    echo "❌ PRP not created"
    exit 1
fi

# Validate quality score
score=$(grep "Score:" prps/test_feature.md | sed 's/.*Score: \([0-9]\+\).*/\1/')
if [ "$score" -lt 8 ]; then
    echo "❌ Quality gate failed: $score/10 < 8/10"
    exit 1
fi

# Validate Phase 2 outputs
for file in codebase-patterns.md documentation-links.md examples-to-include.md; do
    if [ ! -f "prps/test_feature/codex/planning/$file" ]; then
        echo "❌ Missing Phase 2 output: $file"
        exit 1
    fi
done

# Validate manifest
if [ ! -f "prps/test_feature/codex/logs/manifest.jsonl" ]; then
    echo "❌ Manifest not created"
    exit 1
fi

echo "✅ All validations passed"
```

**Test 2: Parallel Timing Validation**:
```bash
#!/bin/bash
# tests/codex/test_parallel_timing.sh

# Extract Phase 2 start timestamps from manifest
manifest="prps/test_feature/codex/logs/manifest.jsonl"

ts_2a=$(grep '"phase":"phase2a"' "$manifest" | grep '"status":"started"' | grep -o '"timestamp":"[^"]*"' | cut -d'"' -f4)
ts_2b=$(grep '"phase":"phase2b"' "$manifest" | grep '"status":"started"' | grep -o '"timestamp":"[^"]*"' | cut -d'"' -f4)
ts_2c=$(grep '"phase":"phase2c"' "$manifest" | grep '"status":"started"' | grep -o '"timestamp":"[^"]*"' | cut -d'"' -f4)

# Convert to epoch seconds
epoch_2a=$(date -j -f "%Y-%m-%dT%H:%M:%SZ" "$ts_2a" "+%s")
epoch_2b=$(date -j -f "%Y-%m-%dT%H:%M:%SZ" "$ts_2b" "+%s")
epoch_2c=$(date -j -f "%Y-%m-%dT%H:%M:%SZ" "$ts_2c" "+%s")

# Calculate max time difference
max_diff=0
diff_ab=$((epoch_2a - epoch_2b))
[ ${diff_ab#-} -gt $max_diff ] && max_diff=${diff_ab#-}
diff_bc=$((epoch_2b - epoch_2c))
[ ${diff_bc#-} -gt $max_diff ] && max_diff=${diff_bc#-}

# Verify started within 5 seconds (proof of parallelism)
if [ $max_diff -le 5 ]; then
    echo "✅ Parallel execution confirmed (max diff: ${max_diff}s ≤ 5s)"
else
    echo "❌ Agents not parallel (max diff: ${max_diff}s > 5s)"
    exit 1
fi

# Calculate speedup
dur_2a=$(grep '"phase":"phase2a"' "$manifest" | grep '"status":"completed"' | grep -o '"duration":[0-9]*' | cut -d':' -f2)
dur_2b=$(grep '"phase":"phase2b"' "$manifest" | grep '"status":"completed"' | grep -o '"duration":[0-9]*' | cut -d':' -f2)
dur_2c=$(grep '"phase":"phase2c"' "$manifest" | grep '"status":"completed"' | grep -o '"duration":[0-9]*' | cut -d':' -f2)

sequential=$((dur_2a + dur_2b + dur_2c))
parallel=$dur_2a
[ $dur_2b -gt $parallel ] && parallel=$dur_2b
[ $dur_2c -gt $parallel ] && parallel=$dur_2c

speedup=$((sequential * 100 / parallel))
echo "Speedup: ${speedup}% ($((speedup - 100))% faster)"

if [ $speedup -ge 200 ]; then
    echo "✅ Target speedup achieved (≥2x)"
else
    echo "⚠️  Below target (expected ≥2x, got ${speedup}%)"
fi
```

**Test 3: PRP Execution Validation**:
```bash
#!/bin/bash
# tests/codex/test_execute_prp.sh

# Create minimal PRP test fixture
# ... (create test PRP with tasks)

# Execute PRP
./.codex/scripts/codex-execute-prp.sh prps/test_feature.md

# Validate completion report
if [ ! -f "prps/test_feature/codex/logs/execution_report.md" ]; then
    echo "❌ Completion report not generated"
    exit 1
fi

# Validate status
status=$(grep "Final Status:" prps/test_feature/codex/logs/execution_report.md | cut -d: -f2 | xargs)
if [ "$status" != "success" ]; then
    echo "❌ Execution failed: status=$status"
    exit 1
fi

# Validate coverage
coverage=$(grep "Test Coverage:" prps/test_feature/codex/logs/execution_report.md | grep -o '[0-9]\+%' | sed 's/%//')
if [ "$coverage" -lt 70 ]; then
    echo "❌ Coverage too low: $coverage% < 70%"
    exit 1
fi

echo "✅ All validations passed"
```

---

### Running All Tests

```bash
#!/bin/bash
# tests/codex/run_all_tests.sh

echo "========================================="
echo "Running All Codex Tests"
echo "========================================="

# Unit tests
echo ""
echo "1. Security Validation Tests"
bash .codex/tests/test_security_validation.sh || exit 1

echo ""
echo "2. Parallel Execution Tests"
bash .codex/scripts/parallel-exec.sh --test || exit 1

# Integration tests
echo ""
echo "3. PRP Generation Test"
bash .codex/tests/test_generate_prp.sh || exit 1

echo ""
echo "4. Parallel Timing Test"
bash .codex/tests/test_parallel_timing.sh || exit 1

echo ""
echo "5. PRP Execution Test"
bash .codex/tests/test_execute_prp.sh || exit 1

echo ""
echo "========================================="
echo "✅ All Tests Passed"
echo "========================================="
```

---

## Performance Tuning

### Timeout Values

**Current Defaults**:
```bash
PHASE0_TIMEOUT=60       # Setup (fast)
PHASE1_TIMEOUT=600      # Feature analysis (research-heavy)
PHASE2_TIMEOUT=600      # Per Phase 2 agent (concurrent)
PHASE3_TIMEOUT=600      # Gotcha detection (research-heavy)
PHASE4_TIMEOUT=900      # PRP assembly (synthesis)
```

**Tuning Guidelines**:

1. **Complex Features** (large codebase, extensive docs):
   ```bash
   PHASE1_TIMEOUT=900 PHASE2_TIMEOUT=900 ./.codex/scripts/codex-generate-prp.sh ...
   ```

2. **Simple Features** (small, well-defined):
   ```bash
   PHASE1_TIMEOUT=300 PHASE2_TIMEOUT=300 ./.codex/scripts/codex-generate-prp.sh ...
   ```

3. **Slow Codex Server**:
   ```bash
   # Increase all timeouts by 50%
   PHASE1_TIMEOUT=900 \
   PHASE2_TIMEOUT=900 \
   PHASE3_TIMEOUT=900 \
   PHASE4_TIMEOUT=1350 \
   ./.codex/scripts/codex-generate-prp.sh ...
   ```

### Parallel Limits

**Current**: 3 agents (Phase 2A, 2B, 2C)

**Why 3**:
- Optimal for most systems (CPU cores, memory)
- Matches PRP generation structure (codebase, docs, examples)
- Prevents Codex server overload

**Increasing** (not recommended):
- Would require splitting Phase 2 into more subphases
- Diminishing returns (setup overhead, coordination)
- Risk of Codex server rate limiting

**Decreasing** (fallback for slow systems):
```bash
# Run Phase 2 sequentially (no parallelism)
# Modify codex-generate-prp.sh to call execute_sequential_phase() for each
# Instead of execute_phase2_parallel()
```

---

## Troubleshooting Reference

All 13 gotchas from PRP with solutions:

| # | Gotcha | Symptoms | Solution | Script |
|---|--------|----------|----------|--------|
| 1 | Exit code loss | Silent failures, wrong exit codes | `wait $PID; EXIT=$?` (immediate) | `parallel-exec.sh` |
| 2 | Security bypass | Command injection, path traversal | 6-level validation | `security-validation.sh` |
| 3 | Zombie processes | Hung workflow, no timeout | `timeout --kill-after=5s` wrapper | All exec calls |
| 4 | Profile omission | Wrong model, wrong config | `--profile codex-prp` explicit | All exec calls |
| 5 | Output interleaving | Corrupted logs | Separate log files per agent | `parallel-exec.sh` |
| 6 | Sequential execution | Slow (64% slower), no speedup | `&` + `wait` for Phase 2 | `parallel-exec.sh` |
| 7 | PID race condition | Silent failures, missing agents | `$!` immediate after `&` | `parallel-exec.sh` |
| 8 | Timeout exit codes | Wrong retry logic, misleading errors | Case statement for 124/125/137 | All exec calls |
| 9 | JSONL corruption | Invalid JSON, corrupted audit | Separate manifests, merge after | `log-phase.sh` |
| 10 | Approval blocking | Workflow hangs on approval | `on-failure` policy in profile | Profile config |
| 11 | Dependency validation | Phase runs before prerequisites | `check_dependencies()` | `codex-generate-prp.sh` |
| 12 | Redundant prp_ prefix | Naming convention violation | Validation rejects `prp_*` | `security-validation.sh` |
| 13 | removeprefix() error | Wrong prefix stripping | `${var#prefix}` NOT `${var//}` | `security-validation.sh` |

---

## Code Patterns Reference

### Pattern 1: Timeout Wrapper

```bash
# CRITICAL: Prevents zombie processes (GOTCHA #3)
# CRITICAL: Explicit profile (GOTCHA #4)
timeout --kill-after=5s ${timeout_sec}s \
    codex exec \
    --profile "$CODEX_PROFILE" \
    --prompt "$(cat "$prompt_file")" \
    > "$log_file" 2>&1
```

### Pattern 2: Exit Code Capture

```bash
# CRITICAL: Must capture IMMEDIATELY after wait (GOTCHA #1)
wait $PID_2A; EXIT_2A=$?  # Semicolon ensures immediate execution
wait $PID_2B; EXIT_2B=$?
wait $PID_2C; EXIT_2C=$?

# ❌ WRONG - Only captures last exit code
wait $PID_2A
wait $PID_2B
wait $PID_2C
EXIT_CODE=$?  # Only has exit code from PID_2C!
```

### Pattern 3: PID Capture

```bash
# CRITICAL: Capture immediately after & (GOTCHA #7)
codex exec ... > log.txt 2>&1 &
PID_2A=$!  # Capture immediately

# ❌ WRONG - Race condition
codex exec ... &
codex exec ... &
for pid in $(jobs -p); do  # May miss fast-failing jobs
    wait $pid
done
```

### Pattern 4: Security Validation

```bash
# CRITICAL: 6-level validation (GOTCHA #2)
feature=$(extract_feature_name "$filepath" "INITIAL_" "true") || {
    echo "❌ Feature name extraction failed"
    exit 1
}

# CRITICAL: Use ${var#prefix} NOT ${var//pattern/} (GOTCHA #13)
feature="${basename#INITIAL_}"  # Only removes from start
# NOT: feature="${basename//INITIAL_/}"  # Removes ALL occurrences
```

### Pattern 5: Dependency Validation

```bash
# CRITICAL: Check before executing phase (GOTCHA #11)
check_dependencies() {
    local feature="$1"
    local phase="$2"
    local deps="${DEPENDENCIES[$phase]}"

    [ -z "$deps" ] && return 0

    IFS=',' read -ra DEP_ARRAY <<< "$deps"
    for dep in "${DEP_ARRAY[@]}"; do
        validate_phase_completion "$feature" "$dep" || return 1
    done

    return 0
}
```

### Pattern 6: Timeout Exit Code Handling

```bash
# CRITICAL: Special handling for timeout codes (GOTCHA #8)
case $exit_code in
    0)   status="✅ SUCCESS" ;;
    124) status="❌ TIMEOUT (exceeded ${timeout}s)" ;;
    125) status="❌ TIMEOUT COMMAND FAILED (timeout not installed?)" ;;
    137) status="❌ KILLED (SIGKILL - process didn't respond to TERM)" ;;
    *)   status="❌ FAILED (exit ${exit_code})" ;;
esac
```

---

## Maintenance Guide

### Adding New Phase

1. **Update Phase Definitions** (`codex-generate-prp.sh`):
   ```bash
   PHASES[phase5]="New Phase Description"
   DEPENDENCIES[phase5]="phase4"  # After Phase 4
   TIMEOUTS[phase5]=600
   ```

2. **Create Prompt File**:
   ```bash
   cat > .codex/prompts/phase5.md <<'EOF'
   # Phase 5: New Phase
   [instructions]
   EOF
   ```

3. **Add to Orchestration** (`codex-generate-prp.sh` main()):
   ```bash
   execute_sequential_phase "$feature" "phase5" ".codex/prompts/phase5.md"
   ```

4. **Update Archon Integration** (if desired):
   ```bash
   # Add to archon_initialize_project()
   task_priorities[phase5]=65
   ```

### Modifying Validation Levels

1. **Add New Level** (`codex-execute-prp.sh`):
   ```bash
   validate_level4_security() {
       local feature="$1"
       local log_file="prps/${feature}/codex/logs/validation_level4.log"

       # Run security scanner
       bandit -r . > "$log_file" 2>&1
       return $?
   }
   ```

2. **Add to Validation Loop**:
   ```bash
   # In run_validation_loop()
   if validate_level4_security "$feature"; then
       log_phase_complete "$feature" "validation_level4_attempt${attempt}" 0 0
   else
       # Handle failure
   fi
   ```

### Updating Security Validation

1. **Add New Validation Level** (`security-validation.sh`):
   ```bash
   # Level 7: Check for emoji (example)
   if [[ "$feature" =~ [😀-🙏] ]]; then
       echo "❌ ERROR: Emoji detected in feature name: '$feature'" >&2
       return 1
   fi
   ```

2. **Update Documentation**:
   - Update `show_usage()` in `security-validation.sh`
   - Update both README files
   - Update PRP (if regenerating)

---

## Files Quick Reference

| File | Purpose | Status | Lines |
|------|---------|--------|-------|
| `codex-generate-prp.sh` | Main PRP generation orchestrator | Production | ~788 |
| `codex-execute-prp.sh` | Validation loop orchestrator | Production | ~747 |
| `parallel-exec.sh` | Phase 2 parallel execution | Production | ~448 |
| `security-validation.sh` | 6-level security validation | Production | ~285 |
| `quality-gate.sh` | PRP quality enforcement | Production | ~450 |
| `log-phase.sh` | JSONL manifest logging | Production | ~400 |
| `validate-bootstrap.sh` | Setup validation | Production | ~300 |
| `validate-config.sh` | Config validation | Production | ~300 |

**Total**: ~3,718 lines of battle-tested Bash

---

## Support

**Questions?**
1. Check this README (technical docs)
2. Check `.codex/README.md` (user-facing docs)
3. Check PRP: `prps/codex_commands.md` (complete specification)
4. Check examples: `prps/codex_commands/examples/README.md`

**Contributing?**
1. Follow existing patterns (see Code Patterns Reference)
2. Address all relevant gotchas (see Gotchas Reference)
3. Add tests (see Testing Guide)
4. Update both READMEs

**Debugging?**
1. Check individual phase logs: `prps/{feature}/codex/logs/phase*.log`
2. Check manifest: `prps/{feature}/codex/logs/manifest.jsonl`
3. Run with debug: `bash -x .codex/scripts/codex-generate-prp.sh ...`

---

**Last Updated**: 2025-10-07
**Version**: 1.0.0 (Production Ready)
**Maintainer**: Vibes Team
