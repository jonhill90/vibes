# PRP: Codex Commands (Production-Ready PRP Generation & Execution)

**Generated**: 2025-10-07
**Based On**: prps/INITIAL_codex_commands.md
**Archon Project**: ab2be58d-7bd6-4b3d-a071-8b8281050132

---

## Goal

Implement production-ready Codex commands (`codex-generate-prp` and `codex-execute-prp`) that replicate Vibes' five-phase PRP workflow with **parallel Phase 2 execution** for 3x speedup (5min vs 15min sequential). Enable complete automation from INITIAL.md to validated implementation with battle-tested quality gates and comprehensive error handling.

**End State**:
- Two command files in `.codex/commands/` (generate-prp.md, execute-prp.md) with complete 5-phase prompts
- Bash orchestration scripts in `scripts/codex/` with parallel execution, timeout handling, security validation
- Integration tests proving parallel speedup (<10min total) and quality enforcement (≥8/10 PRP score)
- Reusable `scripts/codex/log-phase.sh` for JSONL manifest logging (ALREADY EXISTS)
- Complete end-to-end workflow: INITIAL.md → Codex PRP → Codex implementation → validated code

## Why

**Current Pain Points**:
- PRP generation workflow is Claude-specific (Task() subagents not available in Codex CLI)
- Sequential Phase 2 execution wastes 10+ minutes per PRP (no parallelization)
- No Codex-specific commands for developers preferring Codex over Claude
- Manual orchestration required (no automation from INITIAL.md to working code)

**Business Value**:
- **3x speedup**: Parallel Phase 2 reduces PRP generation from ~15min to ~5min
- **Model flexibility**: Use o4-mini for generation, gpt-5-codex for execution (cost optimization)
- **Developer choice**: Support both Claude and Codex workflows with same quality
- **Complete automation**: From INITIAL.md to validated implementation, no manual steps
- **Battle-tested quality**: Reuse Vibes' proven quality gates (≥8/10 PRP score, ≥70% test coverage)

## What

### Core Features

1. **Two Production Commands**:
   - `.codex/commands/codex-generate-prp.md` - Full 5-phase PRP generation prompt
   - `.codex/commands/codex-execute-prp.md` - PRP execution with validation loops

2. **Parallel Phase 2 Execution** (CRITICAL INNOVATION):
   - 3 independent agents run simultaneously: codebase researcher, doc hunter, example curator
   - Bash job control (`&` + `wait` + PID tracking) for parallelization
   - Target: 5min vs 15min sequential (64% faster)

3. **Bash Orchestration Infrastructure**:
   - `scripts/codex/codex-generate-prp.sh` - Command wrapper with orchestration
   - `scripts/codex/codex-execute-prp.sh` - Execution wrapper with validation loops
   - `scripts/codex/log-phase.sh` - **ALREADY EXISTS** (manifest JSONL logging)
   - `scripts/codex/parallel-exec.sh` - Phase 2 parallelization helper

4. **Quality Gates & Validation**:
   - PRP generation: Score ≥8/10 or regenerate (max 3 attempts)
   - PRP execution: Validation loop with ruff → mypy → pytest → retry on fail (max 5 attempts)
   - Coverage enforcement: ≥70% test coverage
   - Manifest logging: JSONL audit trail for all phases

5. **Integration Testing**:
   - `tests/codex/test_generate_prp.sh` - End-to-end PRP generation test
   - Verify parallel execution (concurrent timestamps in manifest)
   - Validate PRP quality ≥8/10
   - Duration <15min for typical feature

### Success Criteria

**PRP Generation Command Complete When**:
- [ ] `.codex/commands/codex-generate-prp.md` exists with full 5-phase prompt
- [ ] `scripts/codex/codex-generate-prp.sh` orchestrates phases correctly
- [ ] `scripts/codex/parallel-exec.sh` launches 3 Phase 2 agents simultaneously
- [ ] Manifest logs show concurrent timestamps (within 5s) for phase2a/2b/2c
- [ ] Speedup measured: parallel <10min vs sequential ~20min (at least 50% faster)
- [ ] Quality gate enforced: PRP score ≥8/10 or interactive regeneration option
- [ ] Integration test passes: `tests/codex/test_generate_prp.sh` succeeds
- [ ] All Phase 2 outputs created: `codebase-patterns.md`, `documentation-links.md`, `examples-to-include.md`

**PRP Execution Command Complete When**:
- [ ] `.codex/commands/codex-execute-prp.md` exists with execution + validation prompt
- [ ] `scripts/codex/codex-execute-prp.sh` orchestrates implementation + validation loop
- [ ] Validation loop proven: Inject linting error, verify automatic fix + retry
- [ ] Coverage gate enforced: Test with <70% coverage, verify failure + retry
- [ ] Completion report includes: files changed, quality score, coverage %, blockers
- [ ] Integration test passes: `tests/codex/test_execute_prp.sh` succeeds
- [ ] Max 5 validation attempts enforced, with clear user messaging after exhaustion

**Full Integration Success**:
- [ ] End-to-end workflow: INITIAL.md → Codex PRP → Codex implementation → validated code
- [ ] Total time <20min for typical feature (parallel speedup proven)
- [ ] Cross-validation possible: Same INITIAL.md through Claude and Codex, compare outputs
- [ ] Archon project created, tasks tracked, final PRP stored as document
- [ ] Manifest JSONL complete with all phases, durations, exit codes

---

## All Needed Context

### Documentation & References

```yaml
# MUST READ - Bash Job Control (Parallel Execution Foundation)
- url: https://www.gnu.org/software/bash/manual/html_node/Job-Control-Builtins.html
  sections:
    - "Job Control Builtins" - wait command, exit status capture, PID tracking
    - "Job Control Basics" - Background processes (&), $! variable, process groups
  why: Core mechanism for Phase 2 parallel execution with job control
  critical_gotchas:
    - "Exit code MUST be captured immediately after wait (lost on next command)"
    - "wait without args waits for ALL jobs, not just specific PID"
    - "Returns 127 if no matching child process"

# MUST READ - GNU Timeout (Zombie Process Prevention)
- url: https://man7.org/linux/man-pages/man1/timeout.1.html
  sections:
    - "Exit Codes" - 124 (timeout), 125 (timeout failed), 137 (SIGKILL)
    - "Signal Handling" - -s flag, -k kill-after flag
  why: Prevents hung codex exec processes from blocking workflow
  critical_gotchas:
    - "Exit 124 = timeout occurred (NOT generic failure)"
    - "Exit 125 = timeout command failed (check timeout installed)"
    - "Default TERM signal can be blocked - use -k for forceful kill"

# MUST READ - Parallel Process Management (Stack Overflow Patterns)
- url: https://stackoverflow.com/questions/356100/how-to-wait-in-bash-for-several-subprocesses-to-finish-and-return-exit-code-0
  why: Practical patterns for waiting on multiple background processes with exit code tracking
  pattern: "Store PIDs in array, wait on each, track failures"
  critical_gotchas:
    - "PID must be captured with $! immediately (before process can exit)"
    - "jobs -p has race condition - use PID array instead"

# ESSENTIAL LOCAL FILES - Vibes PRP Generation Pattern
- file: /Users/jon/source/vibes/.claude/commands/generate-prp.md
  why: Same 5-phase workflow structure, parallel Phase 2, quality gates, Archon integration
  pattern: "Phase 0-4 structure, Task() invocations for Claude (adapt to bash for Codex)"
  critical: "Feature name extraction requires 6-level security validation (lines 20-73)"

# ESSENTIAL LOCAL FILES - Bash Parallel Execution Pattern
- file: /Users/jon/source/vibes/prps/codex_integration/examples/phase_orchestration.sh
  why: Multi-phase workflow with parallel execution (Phase 2), PID tracking, exit code capture
  pattern: "Associative arrays for dependencies, execute_parallel_group() function (lines 112-161)"
  critical: "Exit code capture timing - wait $PID; EXIT=$? (immediate capture)"

# ESSENTIAL LOCAL FILES - JSONL Manifest Logging (PRODUCTION READY - REUSE)
- file: /Users/jon/source/vibes/scripts/codex/log-phase.sh
  why: ALREADY IMPLEMENTED - JSONL logging with security validation, phase tracking, reporting
  pattern: "log_phase_start(), log_phase_complete(), validate_phase_completion()"
  critical: "6-level feature name validation (whitelist, path traversal, length, injection, redundant prefix)"

# ESSENTIAL LOCAL FILES - Security Validation Pattern
- file: /Users/jon/source/vibes/.claude/patterns/security-validation.md
  why: 6-level feature name validation (prevents command injection, path traversal)
  pattern: "extract_feature_name() with whitelist, length check, dangerous chars, removeprefix()"
  critical: "Use removeprefix() NOT replace() - only strips from start, not all occurrences"

# ESSENTIAL LOCAL FILES - Quality Gates Pattern
- file: /Users/jon/source/vibes/.claude/patterns/quality-gates.md
  why: PRP quality scoring (≥8/10), validation loops (max 5 attempts), error analysis
  pattern: "Score extraction regex, interactive regeneration choice, coverage enforcement"
  critical: "NEVER accept <8/10 without user confirmation, ALWAYS iterate on failures"

# ESSENTIAL EXAMPLES - Pattern Library
- file: /Users/jon/source/vibes/prps/codex_commands/examples/README.md
  why: Comprehensive guide with extracted patterns, "what to mimic/adapt/skip" for each
  contains:
    - "phase_orchestration.sh" - Parallel execution (3x speedup pattern)
    - "manifest_logger.sh" - JSONL logging with security validation
    - "security_validation.py" - Feature name extraction (6-level validation)
    - "quality_gate.sh" - PRP quality enforcement (8+/10 minimum)
  critical: "Study before implementation - contains battle-tested patterns and critical gotchas"
```

### Current Codebase Tree

```
vibes/
├── .claude/
│   ├── commands/
│   │   └── generate-prp.md                 # MIRROR: Same 5-phase structure for Codex
│   └── patterns/
│       ├── parallel-subagents.md            # ADAPT: Bash job control instead of Task()
│       ├── quality-gates.md                 # REUSE: Same quality enforcement
│       └── security-validation.md           # REUSE: 6-level feature name validation
├── scripts/
│   └── codex/
│       └── log-phase.sh                     # REUSE DIRECTLY: JSONL manifest logger (PRODUCTION READY)
├── prps/
│   ├── codex_integration/
│   │   └── examples/
│   │       ├── phase_orchestration.sh       # ADAPT: Multi-phase workflow pattern
│   │       ├── manifest_logger.sh           # REFERENCE: JSONL logging (use production version)
│   │       └── command_wrapper.sh           # ADAPT: Codex exec wrapper with timeout
│   └── codex_commands/
│       ├── examples/                        # STUDY: Extracted patterns (4 code files + README)
│       │   ├── README.md
│       │   ├── phase_orchestration.sh
│       │   ├── manifest_logger.sh
│       │   ├── security_validation.py
│       │   └── quality_gate.sh
│       └── planning/                        # Research outputs (5 documents)
│           ├── feature-analysis.md
│           ├── codebase-patterns.md
│           ├── documentation-links.md
│           ├── examples-to-include.md
│           └── gotchas.md
└── tests/
    └── codex/
        └── (tests to be created)
```

### Desired Codebase Tree

```
vibes/
├── .codex/
│   └── commands/                            # NEW: Codex command prompts
│       ├── codex-generate-prp.md            # CREATE: 5-phase PRP generation prompt
│       └── codex-execute-prp.md             # CREATE: PRP execution with validation loops
├── scripts/
│   └── codex/
│       ├── codex-generate-prp.sh            # CREATE: Orchestration wrapper (parallel Phase 2)
│       ├── codex-execute-prp.sh             # CREATE: Execution wrapper (validation loop)
│       ├── parallel-exec.sh                 # CREATE: Phase 2 parallelization helper
│       └── log-phase.sh                     # EXISTS: Reuse directly
└── tests/
    └── codex/
        ├── test_generate_prp.sh             # CREATE: End-to-end PRP generation test
        ├── test_execute_prp.sh              # CREATE: PRP execution test
        └── test_parallel_timing.sh          # CREATE: Parallel execution validation

**New Files**:
1. `.codex/commands/codex-generate-prp.md` - Full 5-phase PRP generation prompt (adapt from .claude/commands/generate-prp.md)
2. `.codex/commands/codex-execute-prp.md` - PRP execution prompt with validation loops
3. `scripts/codex/codex-generate-prp.sh` - Main orchestration script (adapt from phase_orchestration.sh)
4. `scripts/codex/parallel-exec.sh` - Phase 2 parallel execution helper (extract from phase_orchestration.sh lines 112-161)
5. `scripts/codex/codex-execute-prp.sh` - Execution wrapper with validation loop (new pattern)
6. `tests/codex/test_generate_prp.sh` - Integration test for PRP generation
7. `tests/codex/test_execute_prp.sh` - Integration test for PRP execution
8. `tests/codex/test_parallel_timing.sh` - Parallel execution timing validation
```

### Known Gotchas & Library Quirks

```bash
# CRITICAL GOTCHA 1: Exit Code Loss from Timing Race Condition
# Source: codebase-patterns.md lines 996-1026, Stack Overflow (https://stackoverflow.com/questions/356100)
# Issue: Bash only preserves exit code of most recent wait command
# Impact: Silent failures - Phase 2 agents can fail without detection

# ❌ WRONG - Only captures last exit code
wait $PID_2A
wait $PID_2B
wait $PID_2C
EXIT_CODE=$?  # Only has exit code from PID_2C! 2A and 2B are lost.

# ✅ RIGHT - Capture exit code IMMEDIATELY after each wait
wait $PID_2A; EXIT_2A=$?  # Semicolon ensures immediate capture
wait $PID_2B; EXIT_2B=$?
wait $PID_2C; EXIT_2C=$?

# Validate all exit codes
[[ $EXIT_2A -eq 0 && $EXIT_2B -eq 0 && $EXIT_2C -eq 0 ]] || {
    echo "❌ Agent failures: 2A=$EXIT_2A, 2B=$EXIT_2B, 2C=$EXIT_2C"
    handle_partial_failure
}

# CRITICAL GOTCHA 2: Security Validation Bypass via Path Traversal
# Source: security-validation.md, OWASP (https://owasp.org/www-community/attacks/Path_Traversal)
# Issue: Unvalidated feature names enable command injection and path traversal
# Impact: System compromise, arbitrary file overwrite

# ❌ WRONG - No validation, vulnerable
FEATURE=$(basename "$INITIAL_MD" .md)
FEATURE="${FEATURE#INITIAL_}"
mkdir -p "prps/${FEATURE}/planning"  # DANGER: Could create ../../etc/passwd/planning

# ✅ RIGHT - 6-level security validation
validate_feature_name() {
    local feature="$1"

    # Level 1: Path traversal
    [[ "$feature" == *".."* || "$feature" == *"/"* || "$feature" == *"\\"* ]] && return 1

    # Level 2: Whitelist (alphanumeric + underscore + hyphen only)
    [[ ! "$feature" =~ ^[a-zA-Z0-9_-]+$ ]] && return 1

    # Level 3: Length check (max 50 chars)
    [ ${#feature} -gt 50 ] && return 1

    # Level 4: Command injection characters
    local dangerous='$`;&|><'
    local char
    for (( i=0; i<${#dangerous}; i++ )); do
        char="${dangerous:$i:1}"
        [[ "$feature" == *"$char"* ]] && return 1
    done

    # Level 5: Redundant prp_ prefix
    [[ "$feature" == prp_* ]] && return 1

    return 0
}

# CRITICAL: Use removeprefix() in Python, ${var#prefix} in bash
# NOT replace() or ${var//pattern/} - those remove ALL occurrences
basename="INITIAL_INITIAL_test"
feature="${basename#INITIAL_}"  # Result: "INITIAL_test" (correct)
# NOT: feature="${basename//INITIAL_/}"  # Result: "test" (wrong - removes both)

# CRITICAL GOTCHA 3: Zombie Processes from Missing Timeout Wrapper
# Source: Feature-analysis.md lines 517-518, GNU timeout manual
# Issue: Hung codex exec processes block workflow indefinitely
# Impact: Workflow hangs, no error message, no recovery

# ❌ WRONG - No timeout, can hang forever
codex exec --profile codex-prp --prompt "..." &
wait $PID  # May wait forever if agent hangs

# ✅ RIGHT - Timeout wrapper with graceful then forceful kill
TIMEOUT_SEC=600  # 10 minutes for research agents
KILL_AFTER=5     # Force kill 5 seconds after initial timeout

timeout --kill-after=${KILL_AFTER}s ${TIMEOUT_SEC}s \
    codex exec --profile codex-prp --prompt "$(cat prompt.md)" \
    > log.txt 2>&1 &
PID=$!
wait $PID; EXIT=$?

# Interpret exit code
case $EXIT in
    0)   echo "✅ Success" ;;
    124) echo "❌ TIMEOUT (exceeded ${TIMEOUT_SEC}s)" ;;
    125) echo "❌ TIMEOUT COMMAND FAILED (timeout not installed?)" ;;
    137) echo "❌ KILLED (SIGKILL - process didn't respond to TERM)" ;;
    *)   echo "❌ Failed (exit $EXIT)" ;;
esac

# CRITICAL GOTCHA 4: Profile Omission in Codex Exec Calls
# Source: Feature-analysis.md lines 536-538, codebase-patterns.md lines 1062-1081
# Issue: Using default profile instead of codex-prp profile
# Impact: Wrong model, wrong MCP servers, wrong approval policy, cost explosion

# ❌ WRONG - Uses default profile
codex exec --prompt "..."  # Unpredictable behavior

# ✅ RIGHT - Always explicit profile
CODEX_PROFILE="${CODEX_PROFILE:-codex-prp}"
codex exec --profile "$CODEX_PROFILE" --prompt "..."

# CRITICAL GOTCHA 5: Output Interleaving from Concurrent Writes
# Source: Codebase-patterns.md lines 1030-1058, feature-analysis.md line 379
# Issue: Multiple parallel processes writing to same stdout/stderr
# Impact: Corrupted logs, impossible to debug

# ❌ WRONG - All agents write to same stdout
codex exec --prompt "agent 2a" &
codex exec --prompt "agent 2b" &
codex exec --prompt "agent 2c" &
# Output is interleaved garbage

# ✅ RIGHT - Separate log file per agent
codex exec --prompt "agent 2a" > logs/phase2a.log 2>&1 &
codex exec --prompt "agent 2b" > logs/phase2b.log 2>&1 &
codex exec --prompt "agent 2c" > logs/phase2c.log 2>&1 &

# CRITICAL GOTCHA 6: Sequential Execution of Independent Tasks (Anti-Pattern)
# Source: Parallel-subagents.md, codebase-patterns.md lines 1149-1175
# Issue: Running Phase 2 agents sequentially instead of in parallel
# Impact: Wastes 9 minutes (64% slower), defeats entire purpose

# ❌ WRONG - Sequential execution
execute_phase "phase2a"  # 5 min
execute_phase "phase2b"  # 4 min
execute_phase "phase2c"  # 5 min
# Total: 14 min

# ✅ RIGHT - Parallel execution
execute_phase "phase2a" &
execute_phase "phase2b" &
execute_phase "phase2c" &
wait  # Total: 5 min (max of 3)

# HIGH PRIORITY GOTCHA 7: Race Condition in Process Spawning
# Source: Web search (https://unix.stackexchange.com/questions/344360)
# Issue: Fast-failing agent exits before PID is captured
# Impact: Silent failure - agent fails but never gets waited on

# ❌ WRONG - Race condition if job exits before jobs -p
execute_phase "phase2a" &
execute_phase "phase2b" &
execute_phase "phase2c" &
for pid in $(jobs -p); do  # RACE: If phase2a fails fast, it's missing from list
    wait $pid
done

# ✅ RIGHT - Capture PIDs immediately
execute_phase "phase2a" &
PID_2A=$!  # Capture immediately
execute_phase "phase2b" &
PID_2B=$!
execute_phase "phase2c" &
PID_2C=$!
# Now safe to wait on all PIDs

# HIGH PRIORITY GOTCHA 8: Timeout Exit Code Confusion
# Source: GNU timeout manual, Stack Overflow (https://stackoverflow.com/questions/42615374)
# Issue: Treating timeout (124) same as generic failure
# Impact: Wrong retry logic, misleading error messages

# Exit code reference:
# 0   = Success
# 124 = Timeout occurred
# 125 = Timeout command failed
# 137 = SIGKILL sent (128 + 9)
# Use case statement to handle each specifically (see gotcha #3)

# MEDIUM PRIORITY GOTCHA 9: JSONL Manifest Corruption from Concurrent Writes
# Source: Feature-analysis.md lines 520-524
# Issue: Multiple Phase 2 agents appending to manifest.jsonl simultaneously
# Impact: Invalid JSON, corrupted audit trail

# ✅ SOLUTION: Use separate manifest files per agent, merge after Phase 2
log_phase_start_separate() {
    local feature="$1"
    local phase="$2"
    local manifest="prps/${feature}/codex/logs/manifest_${phase}.jsonl"
    echo "$entry" >> "$manifest"  # No collision - different files
}

# After Phase 2 completes, merge all manifests
cat manifest_phase2a.jsonl manifest_phase2b.jsonl manifest_phase2c.jsonl >> manifest.jsonl

# MEDIUM PRIORITY GOTCHA 10: Approval Policy Blocking Parallel Execution
# Source: Feature-analysis.md lines 404-409
# Issue: Profile uses approval_policy: on-request for Phase 2 (read-only operations)
# Impact: Workflow hangs waiting for approval in background process

# ✅ SOLUTION: Use on-failure approval for Phase 2 (reads only)
# .codex/profiles/codex-prp.yaml
approval_policy: on-failure  # Only prompts if tool fails
# Phase 2 agents are read-only (Archon search, file reads) - safe to auto-approve

# MEDIUM PRIORITY GOTCHA 11: Dependency Validation Omission
# Source: Codebase-patterns.md lines 67-139
# Issue: Phase 3 starts before Phase 2 completes
# Impact: Phase 3 has no inputs to work with, generates poor output

# ✅ SOLUTION: Validate dependencies before executing phase
check_dependencies() {
    local feature="$1"
    local phase="$2"
    local deps="${DEPENDENCIES[$phase]}"

    IFS=',' read -ra DEP_ARRAY <<< "$deps"
    for dep in "${DEP_ARRAY[@]}"; do
        validate_phase_completion "$feature" "$dep" || return 1
    done
}

# LOW PRIORITY GOTCHA 12: Redundant prp_ Prefix in Feature Names
# Source: Codebase-patterns.md lines 1120-1145
# Issue: Creating PRPs like prps/prp_feature.md
# Impact: Redundant (directory already says "prps"), violates naming convention

# ✅ RIGHT: prps/feature.md (no prp_ prefix)
# ❌ WRONG: prps/prp_feature.md (redundant)

# LOW PRIORITY GOTCHA 13: removeprefix() vs replace() for INITIAL_ Stripping
# Source: Security-validation.md, codebase-patterns.md lines 420-430
# Issue: Using replace() removes ALL occurrences, not just prefix
# Impact: INITIAL_INITIAL_test.md → test (should be INITIAL_test)

# ✅ RIGHT - Bash remove prefix
feature="${basename#INITIAL_}"  # Only removes from start
# ❌ WRONG - Bash replace all
feature="${basename//INITIAL_/}"  # Removes ALL occurrences
```

---

## Implementation Blueprint

### Phase 0: Planning & Understanding

**BEFORE starting implementation, complete these steps:**

1. **Study Examples Directory**: Read `prps/codex_commands/examples/README.md`
   - Focus on "What to Mimic" sections for each pattern
   - Understand critical gotchas (exit code timing, security validation, timeout handling)
   - Run example code in isolation to verify understanding

2. **Review Vibes PRP Generation Pattern**: Read `.claude/commands/generate-prp.md`
   - Understand 5-phase structure (Phase 0-4)
   - Note parallel Phase 2 execution with Task() subagents
   - Identify what to adapt for Codex (bash job control instead of Task())

3. **Study Existing Infrastructure**: Examine `scripts/codex/log-phase.sh`
   - PRODUCTION READY - reuse directly, no modification needed
   - Understand JSONL logging pattern, security validation, phase tracking

### Task List (Execute in Order)

```yaml
Task 1: Create Bash Security Validation Script
RESPONSIBILITY: Prevent command injection and path traversal in feature names
FILES TO CREATE:
  - scripts/codex/security-validation.sh

PATTERN TO FOLLOW: .claude/patterns/security-validation.md (6-level validation)

SPECIFIC STEPS:
  1. Create validate_feature_name() function with 6 validation levels:
     - Level 1: Path traversal check (.., /, \)
     - Level 2: Whitelist (alphanumeric + underscore + hyphen only)
     - Level 3: Length check (max 50 chars)
     - Level 4: Dangerous characters ($, `, ;, &, |, etc.)
     - Level 5: Redundant prp_ prefix check
     - Level 6: Reserved names (., .., CON, NUL, etc.)
  2. Create extract_feature_name() function:
     - Check for path traversal in full path
     - Extract basename, remove .md extension
     - Strip INITIAL_ prefix using ${var#prefix} (NOT ${var//pattern/})
     - Call validate_feature_name()
  3. Add comprehensive error messages for each validation failure
  4. Source this script in all wrapper scripts

VALIDATION:
  - Test with valid names: user_auth, web-scraper, apiClient123
  - Test with invalid names: ../../etc/passwd, test;rm -rf /, prp_feature
  - Verify error messages are actionable

---

Task 2: Create Phase 2 Parallel Execution Helper
RESPONSIBILITY: Launch 3 Phase 2 agents simultaneously, track PIDs, capture exit codes
FILES TO CREATE:
  - scripts/codex/parallel-exec.sh

PATTERN TO FOLLOW: prps/codex_integration/examples/phase_orchestration.sh (lines 112-161)

SPECIFIC STEPS:
  1. Create execute_parallel_group() function:
     - Accept group name (e.g., "phase2")
     - Launch all agents in background with timeout wrapper
     - Capture PIDs immediately with $!
     - Redirect each agent to separate log file
  2. Wait for all agents, capturing exit codes:
     - wait $PID_2A; EXIT_2A=$?
     - wait $PID_2B; EXIT_2B=$?
     - wait $PID_2C; EXIT_2C=$?
  3. Validate all succeeded:
     - Check all exit codes are 0
     - If any failed, list which agents failed with exit codes
  4. Handle timeout exit codes specially:
     - 124 = timeout (different message)
     - 125 = timeout command failed
     - 137 = SIGKILL (severe hang)
  5. Log all phases to manifest (use log-phase.sh)

VALIDATION:
  - Test with 3 mock agents that succeed (sleep 2)
  - Test with 1 agent failing (exit 1)
  - Test with 1 agent timing out (sleep 1000 with 5s timeout)
  - Verify all exit codes captured correctly
  - Verify separate log files created

---

Task 3: Create PRP Generation Orchestration Script
RESPONSIBILITY: Orchestrate full 5-phase PRP generation workflow with parallel Phase 2
FILES TO CREATE:
  - scripts/codex/codex-generate-prp.sh

PATTERN TO FOLLOW: prps/codex_integration/examples/phase_orchestration.sh

SPECIFIC STEPS:
  1. Parse command-line arguments:
     - Accept INITIAL.md file path
     - Extract and validate feature name (use security-validation.sh)
  2. Define phase dependencies:
     - PHASES associative array (phase0-phase4)
     - DEPENDENCIES associative array (phase3 depends on phase2a,phase2b,phase2c)
     - PARALLEL_GROUPS associative array (group1=phase2a,phase2b,phase2c)
  3. Execute phases sequentially with dependency validation:
     - Phase 0: Setup (create directories, initialize manifest)
     - Phase 1: Feature Analysis (sequential)
     - Phase 2: Parallel execution (use parallel-exec.sh)
     - Phase 3: Gotcha Detection (sequential, after Phase 2 validates)
     - Phase 4: PRP Assembly (sequential)
  4. Implement check_dependencies() function:
     - Parse comma-separated dependency list
     - Validate each dependency completed successfully (use log-phase.sh)
     - Return error if any dependency not met
  5. Add interactive error handling:
     - If phase fails, offer retry/skip/abort
     - For timeout, offer to increase timeout and retry
  6. Generate summary report:
     - Total duration
     - Phase durations
     - Speedup calculation (sequential vs parallel)
     - Final PRP path

VALIDATION:
  - Test with real INITIAL.md (create test case)
  - Verify all phases execute in correct order
  - Verify Phase 2 runs in parallel (timestamps within 5s)
  - Test with injected failure in Phase 2, verify handling
  - Verify manifest JSONL is valid and complete

---

Task 4: Create PRP Generation Command Prompt
RESPONSIBILITY: Full 5-phase PRP generation prompt for Codex CLI
FILES TO CREATE:
  - .codex/commands/codex-generate-prp.md

PATTERN TO FOLLOW: .claude/commands/generate-prp.md (adapt Task() to bash instructions)

SPECIFIC STEPS:
  1. Copy structure from .claude/commands/generate-prp.md
  2. Adapt Phase 2 from Task() invocations to bash instructions:
     - ORIGINAL: "Invoke 3 Task() calls in single response"
     - ADAPTED: "Execute 3 codex exec calls in background with &, wait for all"
  3. Include security validation instructions:
     - Reference 6-level validation pattern
     - Emphasize removeprefix() vs replace()
  4. Add quality gate enforcement:
     - Extract PRP score with regex
     - If <8/10, offer regeneration (max 3 attempts)
  5. Add Archon integration instructions:
     - Create project for PRP generation tracking
     - Create 3 tasks for Phase 2 agents (2A/2B/2C)
     - Update tasks to "doing" before parallel launch
     - Update to "done" after success
     - Store final PRP as document
  6. Include all 13 gotchas in prompt:
     - Exit code timing (CRITICAL)
     - Security validation (CRITICAL)
     - Timeout wrapper (CRITICAL)
     - And all others from gotchas.md

VALIDATION:
  - Dry-run with codex CLI (test prompt syntax)
  - Verify prompt is <50KB (Codex limit)
  - Review for clarity and completeness

---

Task 5: Create PRP Execution Validation Loop Script
RESPONSIBILITY: Orchestrate PRP execution with validation loop (ruff → mypy → pytest)
FILES TO CREATE:
  - scripts/codex/codex-execute-prp.sh

PATTERN TO FOLLOW: .claude/patterns/quality-gates.md (validation loop pattern)

SPECIFIC STEPS:
  1. Parse command-line arguments:
     - Accept PRP file path
     - Extract feature name
  2. Implement validation loop (max 5 attempts):
     - Level 1: Syntax & Style (ruff check --fix, mypy)
     - Level 2: Unit Tests (pytest tests/)
     - Level 3: Coverage (pytest --cov, verify ≥70%)
  3. On validation failure:
     - Extract error messages from logs
     - Check PRP "Known Gotchas" section for solutions
     - Apply fix based on gotcha pattern
     - Retry validation (increment attempt counter)
  4. After max attempts:
     - Generate completion report:
       - Files changed
       - Quality score (if extractable)
       - Coverage percentage
       - Blockers (what's still failing)
     - Offer user choices:
       - Continue anyway (accept partial implementation)
       - Manual intervention (pause for user fixes)
       - Abort workflow
  5. Log all validation attempts to manifest

VALIDATION:
  - Test with PRP that passes all validations
  - Test with injected linting error (verify auto-fix)
  - Test with failing test (verify retry)
  - Test with <70% coverage (verify failure + retry)
  - Verify max 5 attempts enforced

---

Task 6: Create PRP Execution Command Prompt
RESPONSIBILITY: PRP execution prompt with validation loops for Codex CLI
FILES TO CREATE:
  - .codex/commands/codex-execute-prp.md

PATTERN TO FOLLOW: .claude/patterns/quality-gates.md + new execution pattern

SPECIFIC STEPS:
  1. Read PRP file and extract all sections:
     - Goal, Why, What
     - Implementation Blueprint (tasks)
     - Known Gotchas (reference during fixes)
     - Validation Loop (commands to run)
  2. Execute tasks in order:
     - Create data models first (Pydantic, ORM)
     - Implement core logic
     - Add integration points
     - Write tests
  3. Run validation loop after implementation:
     - Follow PRP "Validation Loop" section
     - Apply gotchas from "Known Gotchas" section on errors
     - Retry until all validations pass (max 5 attempts)
  4. Generate completion report:
     - What was implemented
     - All validation results
     - Test coverage percentage
     - Any remaining blockers
  5. Update Archon project with completion status

VALIDATION:
  - Test with simple PRP (2-3 tasks)
  - Verify tasks executed in correct order
  - Verify validation loop runs
  - Test with complex PRP (10+ tasks)

---

Task 7: Create Integration Tests
RESPONSIBILITY: Validate end-to-end workflows and parallel execution
FILES TO CREATE:
  - tests/codex/test_generate_prp.sh
  - tests/codex/test_execute_prp.sh
  - tests/codex/test_parallel_timing.sh

PATTERN TO FOLLOW: Feature-analysis.md success criteria

SPECIFIC STEPS:
  1. test_generate_prp.sh:
     - Create minimal INITIAL.md test fixture
     - Execute codex-generate-prp.sh
     - Validate PRP created
     - Validate manifest JSONL complete
     - Validate PRP quality score ≥8/10
     - Validate all Phase 2 outputs exist
  2. test_parallel_timing.sh:
     - Extract Phase 2 start timestamps from manifest
     - Convert to epoch seconds
     - Verify all started within 5 seconds (proof of parallelism)
     - Calculate speedup (sequential estimate vs actual parallel)
     - Verify speedup ≥2x
  3. test_execute_prp.sh:
     - Create minimal PRP test fixture
     - Execute codex-execute-prp.sh
     - Validate all tasks completed
     - Validate all validation gates passed
     - Verify test coverage ≥70%

VALIDATION:
  - Run all tests in CI/CD environment
  - Verify tests are idempotent (can run multiple times)
  - Verify cleanup happens after tests

---

Task 8: Create Quality Gate Script
RESPONSIBILITY: Extract PRP quality score and enforce ≥8/10 minimum
FILES TO CREATE:
  - scripts/codex/quality-gate.sh

PATTERN TO FOLLOW: prps/codex_commands/examples/quality_gate.sh

SPECIFIC STEPS:
  1. Create extract_prp_score() function:
     - Read PRP file
     - Search for "Score: X/10" pattern (regex)
     - Extract numeric score
     - Return score (or 0 if not found)
  2. Create enforce_quality_gate() function:
     - Call extract_prp_score()
     - If score <8/10, offer choices:
       - Regenerate (increment attempt counter)
       - Accept anyway (with warning)
       - Abort workflow
     - Max 3 regeneration attempts
  3. Add scoring guidance:
     - List what makes a 10/10 PRP
     - List common reasons for <8/10
     - Suggest how to improve score

VALIDATION:
  - Test with PRP score 10/10 (passes)
  - Test with PRP score 6/10 (offers regeneration)
  - Test with PRP score 0/10 (no score found, prompts user)

---

Task 9: Add Archon Integration to Generate Script
RESPONSIBILITY: Track PRP generation in Archon with tasks for each phase
FILES TO MODIFY:
  - scripts/codex/codex-generate-prp.sh

PATTERN TO FOLLOW: .claude/patterns/archon-workflow.md

SPECIFIC STEPS:
  1. Check if Archon MCP server available (graceful degradation)
  2. If available, create Archon project:
     - Title: "PRP: {feature_name}"
     - Store project_id for task creation
  3. Create tasks for each phase:
     - Phase 0: Setup (priority 100)
     - Phase 1: Analysis (priority 95)
     - Phase 2A: Codebase Research (priority 90)
     - Phase 2B: Documentation Hunt (priority 85)
     - Phase 2C: Example Curation (priority 80)
     - Phase 3: Gotcha Detection (priority 75)
     - Phase 4: PRP Assembly (priority 70)
  4. Update task status:
     - Before phase execution: status="doing"
     - After phase success: status="done"
     - After phase failure: status="blocked"
  5. Store final PRP as document:
     - Title: "PRP: {feature_name}"
     - Type: "prp"
     - Content: Full PRP markdown

VALIDATION:
  - Test with Archon available (verify tasks created)
  - Test with Archon unavailable (verify graceful degradation)
  - Verify task statuses update correctly

---

Task 10: Add Documentation
RESPONSIBILITY: Document usage, configuration, and troubleshooting
FILES TO CREATE:
  - .codex/README.md
  - scripts/codex/README.md

SPECIFIC STEPS:
  1. .codex/README.md:
     - Overview of Codex commands
     - Installation and setup
     - Profile configuration (codex-prp.yaml)
     - Usage examples
     - Comparison with Claude commands
  2. scripts/codex/README.md:
     - Architecture overview (5 scripts)
     - Dependency graph (which scripts call which)
     - Troubleshooting guide (common errors)
     - Performance tuning (timeout values, parallel limits)
     - Testing guide

VALIDATION:
  - Follow README to set up from scratch
  - Verify all examples work
  - Check for clarity and completeness
```

### Implementation Pseudocode

```bash
# scripts/codex/codex-generate-prp.sh - Main orchestration flow

#!/bin/bash
set -euo pipefail

# Import dependencies
source "$(dirname "$0")/log-phase.sh"
source "$(dirname "$0")/security-validation.sh"
source "$(dirname "$0")/parallel-exec.sh"

# Configuration
CODEX_PROFILE="${CODEX_PROFILE:-codex-prp}"
MAX_REGENERATION_ATTEMPTS=3

main() {
    local initial_md="$1"

    # Step 1: Validate input and extract feature name
    validate_initial_md "$initial_md" || exit 1
    local feature_name=$(extract_feature_name "$initial_md") || exit 1

    echo "=========================================="
    echo "Codex PRP Generation Workflow"
    echo "=========================================="
    echo "Feature: $feature_name"
    echo "Profile: $CODEX_PROFILE"
    echo "Output: prps/${feature_name}/codex"
    echo ""

    # Step 2: Setup directories and manifest
    execute_phase0_setup "$feature_name" "$initial_md"

    # Step 3: Execute Phase 1 (Feature Analysis)
    execute_phase1_analysis "$feature_name" "$initial_md"

    # Step 4: Execute Phase 2 (Parallel Research)
    execute_phase2_parallel "$feature_name"

    # Step 5: Validate Phase 2 outputs before Phase 3
    validate_phase2_outputs "$feature_name" || {
        echo "❌ Phase 2 outputs incomplete"
        handle_phase2_failure "$feature_name"
    }

    # Step 6: Execute Phase 3 (Gotcha Detection)
    execute_phase3_gotchas "$feature_name"

    # Step 7: Execute Phase 4 (PRP Assembly)
    execute_phase4_assembly "$feature_name"

    # Step 8: Quality gate enforcement
    enforce_quality_gate "$feature_name" || {
        echo "❌ Quality gate failed"
        exit 1
    }

    # Step 9: Generate summary report
    generate_summary_report "$feature_name"

    echo ""
    echo "=========================================="
    echo "✅ PRP Generation Complete"
    echo "=========================================="
    echo "PRP: prps/${feature_name}.md"
    echo "Manifest: prps/${feature_name}/codex/logs/manifest.jsonl"
}

execute_phase2_parallel() {
    local feature_name="$1"

    echo "🚀 Starting Phase 2 (parallel execution)..."

    # Start timestamp
    local start_time=$(date +%s)

    # Log phase starts (separate manifests to avoid race condition)
    log_phase_start_separate "$feature_name" "phase2a"
    log_phase_start_separate "$feature_name" "phase2b"
    log_phase_start_separate "$feature_name" "phase2c"

    # Launch all 3 agents in background with timeout
    local timeout_sec=600  # 10 minutes per agent

    timeout --kill-after=5s ${timeout_sec}s codex exec \
        --profile "$CODEX_PROFILE" \
        --prompt "$(cat .codex/prompts/phase2a.txt)" \
        > "prps/${feature_name}/codex/logs/phase2a.log" 2>&1 &
    local PID_2A=$!
    echo "   Agent 2A (codebase): PID $PID_2A"

    timeout --kill-after=5s ${timeout_sec}s codex exec \
        --profile "$CODEX_PROFILE" \
        --prompt "$(cat .codex/prompts/phase2b.txt)" \
        > "prps/${feature_name}/codex/logs/phase2b.log" 2>&1 &
    local PID_2B=$!
    echo "   Agent 2B (docs):     PID $PID_2B"

    timeout --kill-after=5s ${timeout_sec}s codex exec \
        --profile "$CODEX_PROFILE" \
        --prompt "$(cat .codex/prompts/phase2c.txt)" \
        > "prps/${feature_name}/codex/logs/phase2c.log" 2>&1 &
    local PID_2C=$!
    echo "   Agent 2C (examples): PID $PID_2C"

    echo "   Waiting for completion..."

    # CRITICAL: Capture exit codes IMMEDIATELY after each wait
    wait $PID_2A; local EXIT_2A=$?
    wait $PID_2B; local EXIT_2B=$?
    wait $PID_2C; local EXIT_2C=$?

    # End timestamp
    local end_time=$(date +%s)
    local duration_2a=$((end_time - start_time))
    local duration_2b=$((end_time - start_time))
    local duration_2c=$((end_time - start_time))

    # Log phase completions
    log_phase_complete_separate "$feature_name" "phase2a" "$EXIT_2A" "$duration_2a"
    log_phase_complete_separate "$feature_name" "phase2b" "$EXIT_2B" "$duration_2b"
    log_phase_complete_separate "$feature_name" "phase2c" "$EXIT_2C" "$duration_2c"

    # Merge separate manifests into main manifest
    merge_phase2_manifests "$feature_name"

    # Validate all succeeded
    if [[ $EXIT_2A -eq 0 && $EXIT_2B -eq 0 && $EXIT_2C -eq 0 ]]; then
        echo "✅ Phase 2 complete (all agents succeeded)"
        echo "   - 2A: ${duration_2a}s"
        echo "   - 2B: ${duration_2b}s"
        echo "   - 2C: ${duration_2c}s"
        echo "   - Total: $((end_time - start_time))s"
        return 0
    else
        echo "❌ Phase 2 failed:"
        echo "   - Agent 2A (codebase) exit $EXIT_2A"
        echo "   - Agent 2B (docs)     exit $EXIT_2B"
        echo "   - Agent 2C (examples) exit $EXIT_2C"
        return 1
    fi
}

# Pattern from: phase_orchestration.sh lines 112-161
# Gotcha avoided: Exit code timing (wait $PID; EXIT=$? immediate capture)
# Gotcha avoided: Output interleaving (separate log files)
# Gotcha avoided: Zombie processes (timeout wrapper)
# Gotcha avoided: Profile omission (--profile explicit)
```

---

## Validation Loop

### Level 1: Syntax & Style Checks

```bash
# Bash scripts
shellcheck scripts/codex/*.sh

# Fix common issues
shellcheck -e SC2086 scripts/codex/*.sh  # Ignore unquoted variables if intentional
```

### Level 2: Unit Tests

```bash
# Test security validation
bash tests/codex/test_security_validation.sh

# Test parallel execution timing
bash tests/codex/test_parallel_timing.sh

# Expected: All tests pass
```

### Level 3: Integration Tests

```bash
# End-to-end PRP generation
bash tests/codex/test_generate_prp.sh

# End-to-end PRP execution
bash tests/codex/test_execute_prp.sh

# Expected: PRPs generated with score ≥8/10, all validations pass
```

---

## Final Validation Checklist

**Functionality**:
- [ ] PRP generation workflow completes end-to-end (INITIAL.md → PRP)
- [ ] Phase 2 executes in parallel (concurrent timestamps in manifest)
- [ ] Quality gate enforced (PRP score ≥8/10 or regeneration offered)
- [ ] All 5 Phase 2 outputs created (feature-analysis, codebase-patterns, documentation-links, examples, gotchas)
- [ ] PRP execution workflow completes (PRP → validated implementation)
- [ ] Validation loop iterates (max 5 attempts with fixes)
- [ ] Test coverage ≥70% enforced

**Quality**:
- [ ] All bash scripts pass shellcheck
- [ ] Security validation rejects all attack vectors (path traversal, injection)
- [ ] Exit codes captured correctly (no silent failures)
- [ ] Timeout wrapper prevents zombie processes
- [ ] Profile enforcement consistent (codex-prp in all exec calls)
- [ ] Logs are clean and parseable (no output interleaving)

**Performance**:
- [ ] Parallel speedup ≥2x measured (sequential estimate vs actual)
- [ ] Total PRP generation <15min for typical feature
- [ ] Phase 2 completes in <10min (parallel execution)

**Integration**:
- [ ] Archon project created with tasks (if Archon available)
- [ ] Manifest JSONL valid and complete (all phases logged)
- [ ] Final PRP stored in Archon as document
- [ ] All tests pass in CI/CD environment

**Documentation**:
- [ ] README files complete with usage examples
- [ ] Troubleshooting guide covers common errors
- [ ] Profile configuration documented (codex-prp.yaml)

---

## Anti-Patterns to Avoid

**Critical Anti-Patterns** (Will break workflow):
- ❌ **Exit code loss**: Multiple `wait` calls without immediate `$?` capture → Silent failures
- ❌ **No timeout**: `codex exec` without timeout wrapper → Zombie processes hang workflow
- ❌ **Security bypass**: No feature name validation → Command injection, path traversal
- ❌ **Sequential execution**: Phase 2 agents in loop without `&` → 64% slower, defeats purpose

**High Priority Anti-Patterns** (Will cause issues):
- ❌ **Profile omission**: `codex exec` without `--profile` → Wrong model, wrong config
- ❌ **Output interleaving**: Shared stdout for parallel agents → Corrupted logs
- ❌ **PID race condition**: Using `jobs -p` instead of immediate `$!` capture → Silent failures
- ❌ **Generic timeout handling**: Treating exit 124 same as other failures → Wrong retry logic

**Medium Priority Anti-Patterns** (May cause issues):
- ❌ **Manifest corruption**: Concurrent writes to same file → Invalid JSON
- ❌ **No dependency validation**: Phase 3 starts before Phase 2 completes → Missing inputs
- ❌ **Approval blocking**: `on-request` policy for Phase 2 → Workflow hangs on approval

**Low Priority Anti-Patterns** (Code smell):
- ❌ **Redundant prefix**: `prp_` in feature name → Violates naming convention
- ❌ **Wrong prefix stripping**: `replace()` instead of `removeprefix()` → Edge case bugs

---

## Success Metrics

**PRP Generation**:
- PRP generated with score ≥8/10 in <15 minutes
- Parallel speedup ≥2x measured (target: 3x)
- All 5 research documents created and comprehensive
- Manifest JSONL valid with all phases logged

**PRP Execution**:
- Implementation passes all validation gates in ≤5 attempts
- Test coverage ≥70% achieved
- All tasks completed in order with no manual intervention

**Overall**:
- End-to-end workflow (INITIAL.md → validated code) in <30 minutes
- Cross-validation: Same INITIAL.md through Claude and Codex produces equivalent PRPs
- Integration tests pass 100% in CI/CD

---

## PRP Quality Self-Assessment

**Score: 9/10** - High confidence in one-pass implementation success

**Reasoning**:
- ✅ **Comprehensive context**: All 5 research documents thorough and detailed
  - Feature analysis: Clear requirements, technical components, success criteria
  - Codebase patterns: 6 major patterns documented, production-ready examples
  - Documentation: 10+ URLs with specific sections, local file references
  - Examples: 4 code files + comprehensive README (1000+ lines)
  - Gotchas: 13 documented with solutions (3 Critical, 5 High, 3 Medium, 2 Low)

- ✅ **Clear task breakdown**: 10 tasks with specific steps, patterns, and validation
  - Security validation script → Pattern from security-validation.md
  - Parallel execution helper → Pattern from phase_orchestration.sh
  - Main orchestration script → Adapts proven structure
  - Command prompts → Mirrors .claude/commands/generate-prp.md
  - Integration tests → Proves parallel speedup and quality enforcement

- ✅ **Proven patterns**: Reusing battle-tested Vibes infrastructure
  - `log-phase.sh` PRODUCTION READY - use as-is (0% modification)
  - `phase_orchestration.sh` - adapt structure (20% modification)
  - Security validation - bash version of proven Python pattern
  - Quality gates - same enforcement logic as Claude workflow

- ✅ **Validation strategy**: Multi-level gates with clear pass/fail criteria
  - Shellcheck for bash syntax
  - Unit tests for security validation, parallel timing
  - Integration tests for end-to-end workflows
  - Performance validation (speedup ≥2x, duration <15min)

- ✅ **Error handling**: All 13 gotchas documented with detection and solutions
  - Critical gotchas have code examples (exit code timing, security, timeout)
  - High-priority gotchas explained with alternatives
  - Medium/low priority gotchas documented for awareness

**Deduction reasoning** (-1 from perfect 10/10):
- **Codex CLI behavior undocumented**: No official docs for `codex exec` command
  - Assumption: Exit codes follow Unix conventions (0=success, non-zero=failure)
  - Assumption: `--profile` flag works like Claude CLI profiles
  - Mitigation: Defensive error handling, log full output, test actual behavior
- **JSONL concurrent write atomicity**: Assumes POSIX O_APPEND for small writes
  - May not hold on NFS or non-POSIX filesystems
  - Mitigation: Document local filesystem requirement OR use flock (included as option)

**Mitigations**:
- Add explicit Codex CLI behavior validation in tests (verify assumptions)
- Document system requirements (Bash 4.0+, local filesystem, GNU coreutils)
- Include alternative patterns (flock for manifest, separate files for Phase 2)
- Add defensive error handling for unknown Codex CLI exit codes

**Overall Confidence**: HIGH - This PRP provides everything needed for successful implementation. The -1 deduction is for Codex CLI uncertainty, which is mitigated through testing and defensive coding.
