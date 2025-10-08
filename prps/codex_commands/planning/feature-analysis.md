# Feature Analysis: codex_commands

## INITIAL.md Summary

Implement production-ready Codex commands (`codex-generate-prp` and `codex-execute-prp`) that replicate Vibes' five-phase PRP workflow with **parallel Phase 2 execution** for 3x speedup (5min vs 15min sequential). Enable model flexibility (o4-mini for generation, gpt-5-codex for execution) and complete automation from INITIAL.md to validated implementation with battle-tested quality gates.

## Core Requirements

### Explicit Requirements (From INITIAL.md)

1. **Two Production Commands**:
   - `.codex/commands/codex-generate-prp.md` - Full 5-phase PRP generation prompt
   - `.codex/commands/codex-execute-prp.md` - PRP execution with validation loops

2. **Parallel Phase 2 Execution** (CRITICAL INNOVATION):
   - 3 independent agents run simultaneously: codebase researcher, doc hunter, example curator
   - Target: 5min vs 15min sequential (64% faster)
   - Implementation: Bash job control (`&` + `wait`) OR concurrent `codex exec` calls

3. **Bash Orchestration Infrastructure**:
   - `scripts/codex/codex-generate-prp.sh` - Command wrapper with orchestration
   - `scripts/codex/codex-execute-prp.sh` - Execution wrapper with validation loops
   - `scripts/codex/log-phase.sh` - **ALREADY EXISTS** (manifest JSONL logging)
   - `scripts/codex/parallel-exec.sh` - Phase 2 parallelization handler

4. **Quality Gates & Validation**:
   - PRP generation: Score ≥8/10 or regenerate (max 3 attempts)
   - PRP execution: Validation loop with ruff → pytest → retry on fail (max 5 attempts)
   - Coverage enforcement: ≥70% test coverage
   - Manifest logging: JSONL audit trail for all phases

5. **Integration Testing**:
   - `tests/codex/test_generate_prp.sh` - End-to-end PRP generation test
   - Verify parallel execution (concurrent timestamps in manifest)
   - Validate PRP quality ≥8/10
   - Duration <15min for typical feature

### Implicit Requirements (Inferred)

1. **Codex Profile Management**:
   - Use `--profile codex-prp` for all `codex exec` invocations
   - Profile already configured (from Bootstrap Phase 1)
   - Approval policy: `on-failure` for non-blocking reads

2. **Directory Structure**:
   - Command files: `.codex/commands/` (mirrors `.claude/commands/`)
   - Scripts: `scripts/codex/` for bash orchestration
   - Logs: `prps/{feature}/codex/logs/` for manifest + phase logs
   - Planning: `prps/{feature}/planning/` for research outputs

3. **Error Handling**:
   - Partial Phase 2 failures: Retry failed agent only, OR retry entire phase
   - Output interleaving: Separate log files per agent (phase2a.log, phase2b.log, phase2c.log)
   - Zombie processes: Timeout handling (600s per agent)
   - Exit code tracking: Capture immediately after `wait` to avoid loss

4. **Archon Integration**:
   - Create Archon project for PRP generation tracking
   - 3 separate tasks for Phase 2 agents (2A/2B/2C) for visibility
   - Update to "doing" before parallel launch, "done" after success
   - Store final PRP as document in Archon

5. **Reuse Vibes Patterns**:
   - Phase structure from `.claude/commands/generate-prp.md`
   - Parallel subagent pattern from `.claude/patterns/parallel-subagents.md`
   - Quality gates from `.claude/patterns/quality-gates.md`
   - Security validation for feature name extraction

## Technical Components

### Data Models

**Manifest Schema (JSONL)**:
```json
{"phase":"phase1","status":"started","timestamp":"2025-10-07T10:30:00Z"}
{"phase":"phase1","status":"success","exit_code":0,"duration_sec":42,"timestamp":"2025-10-07T10:31:42Z"}
{"phase":"phase2a","status":"success","exit_code":0,"duration_sec":300,"timestamp":"2025-10-07T10:36:42Z"}
```

**Phase Definitions**:
```bash
declare -A PHASES=(
    [phase0]="Setup and Initialization"
    [phase1]="Feature Analysis"
    [phase2a]="Codebase Research"
    [phase2b]="Documentation Hunt"
    [phase2c]="Example Curation"
    [phase3]="Gotcha Detection"
    [phase4]="PRP Assembly"
)
```

**Dependency Graph**:
```bash
declare -A DEPENDENCIES=(
    [phase0]=""
    [phase1]="phase0"
    [phase2a]="phase1"
    [phase2b]="phase1"
    [phase2c]="phase1"
    [phase3]="phase2a,phase2b,phase2c"
    [phase4]="phase3"
)
```

### External Integrations

1. **Codex CLI**:
   - Command: `codex exec --profile codex-prp --prompt "..."`
   - Exit codes: 0 = success, non-zero = failure
   - Output: Separate log files per agent to avoid interleaving
   - Timeout: 600s per agent (10 min max)

2. **Archon MCP Server** (Optional):
   - Project creation: `mcp__archon__manage_project("create", ...)`
   - Task tracking: `mcp__archon__manage_task("update", status="doing|done")`
   - Document storage: `mcp__archon__manage_document("create", ...)`
   - Graceful degradation: Proceed without Archon if unavailable

3. **Validation Tools**:
   - Linters: `ruff check --fix`, `mypy`, `shellcheck`
   - Tests: `pytest --cov` with ≥70% coverage threshold
   - Quality scoring: Regex extraction from PRP content

### Core Logic

**Phase 2 Parallel Execution** (CRITICAL PATTERN):
```bash
# Launch all 3 agents in background
timeout 600 codex exec --profile codex-prp --prompt "$(cat phase2a.txt)" > logs/2a.log 2>&1 &
PID_2A=$!

timeout 600 codex exec --profile codex-prp --prompt "$(cat phase2b.txt)" > logs/2b.log 2>&1 &
PID_2B=$!

timeout 600 codex exec --profile codex-prp --prompt "$(cat phase2c.txt)" > logs/2c.log 2>&1 &
PID_2C=$!

# Wait for all, capture exit codes (CRITICAL: capture immediately)
wait $PID_2A; EXIT_2A=$?
wait $PID_2B; EXIT_2B=$?
wait $PID_2C; EXIT_2C=$?

# Validate all succeeded
[[ $EXIT_2A -eq 0 && $EXIT_2B -eq 0 && $EXIT_2C -eq 0 ]] || handle_failure
```

**Validation Loop** (Execute-PRP):
```bash
MAX_ATTEMPTS=5
for attempt in 1..$MAX_ATTEMPTS; do
    # Run validation suite
    ruff check src/ && mypy src/ && pytest tests/ --cov --cov-report=term

    if [ $? -eq 0 ]; then
        # Check coverage threshold
        coverage=$(pytest --cov --cov-report=term | grep "TOTAL" | awk '{print $NF}' | sed 's/%//')
        [ $coverage -ge 70 ] && break
    fi

    # Retry with fix
    [ $attempt -lt $MAX_ATTEMPTS ] && apply_fix_from_prp_gotchas
done
```

**Feature Name Extraction** (Security):
```python
def extract_feature_name(filepath: str) -> str:
    # 6-level security validation (from generate-prp.md)
    # 1. Path traversal check
    # 2. Whitelist characters: [a-zA-Z0-9_-]
    # 3. Length check: max 50 chars
    # 4. Dangerous chars: $, `, ;, &, |, etc.
    # 5. Strip INITIAL_ prefix using removeprefix() (NOT replace())
    # 6. Redundant prp_ prefix check (CRITICAL: reject immediately)

    if ".." in filepath: raise ValueError("Path traversal")
    basename = filepath.split("/")[-1].replace(".md", "")
    feature = basename.removeprefix("INITIAL_")
    if not re.match(r'^[a-zA-Z0-9_-]+$', feature): raise ValueError("Invalid chars")
    if len(feature) > 50: raise ValueError("Too long")
    if feature.startswith("prp_"): raise ValueError("Redundant prp_ prefix")
    return feature
```

### UI/CLI Requirements

**Command Invocation**:
```bash
# Generate PRP
./scripts/codex/codex-generate-prp.sh prps/INITIAL_feature.md

# Execute PRP
./scripts/codex/codex-execute-prp.sh prps/feature.md
```

**Progress Reporting**:
```bash
========================================
Codex PRP Generation Workflow
========================================
Feature: user_authentication
Profile: codex-prp
Output: prps/user_authentication/codex

🚀 Starting Phase 2 (parallel execution)...
   Agent 2A (codebase): PID 12345
   Agent 2B (docs):     PID 12346
   Agent 2C (examples): PID 12347
   Waiting for completion...

✅ Phase 2 complete (all agents succeeded)
   - 2A: 298s
   - 2B: 245s
   - 2C: 312s
   - Total: 312s (vs 855s sequential)
```

**Error Handling** (Interactive):
```bash
❌ Phase 2 failed:
   - Agent 2A (codebase) exit 0
   - Agent 2B (docs) exit 1
   - Agent 2C (examples) exit 0

Options:
  1. Retry phase
  2. Skip phase (continue with partial results)
  3. Abort workflow

Choose (1/2/3):
```

## Similar Implementations Found in Archon

### 1. Vibes `.claude/commands/generate-prp.md`
- **Relevance**: 10/10 (Direct template for Codex commands)
- **Archon ID**: N/A (local codebase file)
- **Key Patterns**:
  - 5-phase workflow structure (Phase 0-4)
  - Phase 2 parallel execution with 3 Task() calls in single response
  - Feature name extraction with 6-level security validation
  - Archon integration with graceful degradation
  - Quality gate enforcement (≥8/10 score)
- **Gotchas**:
  - Must use `removeprefix()` not `replace()` to avoid stripping all occurrences
  - Parallel tasks MUST be in SINGLE response, not loop
  - Archon updates MUST be batched (before/after parallel group)
  - Redundant `prp_` prefix MUST be rejected immediately

### 2. Vibes `prps/codex_integration/examples/phase_orchestration.sh`
- **Relevance**: 9/10 (Bash orchestration pattern)
- **Archon ID**: N/A (local example file)
- **Key Patterns**:
  - Phase dependency tracking with associative arrays
  - Parallel group execution with PID tracking
  - Exit code capture immediately after `wait`
  - Progress reporting with phase status
  - Error handling with retry/skip/abort options
- **Gotchas**:
  - Exit codes LOST if not captured immediately: `wait $PID; EXIT=$?`
  - Parallel jobs need separate log files to avoid output interleaving
  - Dependency validation MUST occur before phase execution
  - Timeout MUST wrap `codex exec` to prevent zombie processes

### 3. Vibes `scripts/codex/log-phase.sh`
- **Relevance**: 10/10 (ALREADY EXISTS - reuse directly)
- **Archon ID**: N/A (local script)
- **Key Patterns**:
  - JSONL manifest logging (append-only, one JSON per line)
  - ISO 8601 timestamps (UTC)
  - Feature name security validation
  - Phase completion validation functions
  - Summary report generation from manifest
- **Gotchas**:
  - Manifest MUST use `>>` not `>` (append-only)
  - Concurrent writes need atomic operations (temp file + `mv` OR `flock`)
  - jq optional with grep fallback for parsing

### 4. Vibes `.claude/patterns/parallel-subagents.md`
- **Relevance**: 10/10 (Core parallelization theory)
- **Archon ID**: N/A (local pattern doc)
- **Key Patterns**:
  - All Task() calls in SINGLE response = parallel (max of times)
  - Loop over Task() = sequential (sum of times)
  - Speedup: 14min → 5min (64% faster)
  - Archon batch updates before/after group
- **Gotchas**:
  - NEVER use loop for parallel tasks
  - NEVER interleave Archon updates with task invocations
  - ALWAYS validate no file conflicts before parallelizing
  - ALWAYS limit to 3-6 tasks per parallel group

### 5. Vibes `.claude/patterns/quality-gates.md`
- **Relevance**: 9/10 (Validation enforcement)
- **Archon ID**: N/A (local pattern doc)
- **Key Patterns**:
  - PRP quality: ≥8/10 minimum with interactive choice
  - Validation loop: max 5 attempts with error analysis
  - Error patterns: regex matching against known gotchas
  - Coverage enforcement: ≥70% threshold
- **Gotchas**:
  - NEVER skip validation levels (syntax → unit → integration)
  - NEVER accept <8/10 without user confirmation
  - ALWAYS check PRP gotchas first when fixing errors
  - ALWAYS iterate on failures (up to max attempts)

## Recommended Technology Stack

**Based on Vibes Patterns and Codex Integration**:

- **Command Framework**: Markdown prompts in `.codex/commands/` (mirrors `.claude/commands/`)
- **Orchestration**: Bash scripts in `scripts/codex/` with job control
- **Logging**: JSONL manifest via existing `scripts/codex/log-phase.sh`
- **Validation**:
  - Python: `ruff`, `mypy`, `pytest` (reuse Vibes toolchain)
  - Bash: `shellcheck` for script validation
- **Parallel Execution**: Bash job control (`&`, `wait`, PID tracking)
- **Timeout Handling**: GNU `timeout` command (standard on Linux/macOS)
- **JSON Parsing**: `jq` (with grep fallback if unavailable)
- **Testing Framework**: Bash integration tests in `tests/codex/`

**Why These Choices**:
- **Bash**: Native to all Unix systems, no dependencies, proven for orchestration
- **Job Control**: Standard bash feature, no external tools needed
- **JSONL**: Append-only, greppable, jq-parseable, proven in examples
- **Existing Tools**: Reuse Vibes' ruff/mypy/pytest setup, no new dependencies

## Assumptions Made

### 1. **Parallel Execution Method**: Bash Job Control
- **Reasoning**:
  - No external dependencies (GNU Parallel not needed)
  - Proven pattern in `phase_orchestration.sh` example
  - Simple PID tracking and exit code capture
  - Works on all Unix systems (Linux, macOS, WSL)
- **Source**: `prps/codex_integration/examples/phase_orchestration.sh` (lines 112-161)

### 2. **Timeout Value**: 600s (10 min) per Agent
- **Reasoning**:
  - Phase 2 agents are research-heavy (Archon search, codebase grep, file I/O)
  - Sequential Phase 2 takes ~15min, parallel target is ~5min
  - Individual agent timeouts should be 2x expected average (5min avg → 10min timeout)
  - Total Phase 2 timeout = max(agent timeouts) = 10min
- **Source**: INITIAL.md target (<15min total), conservative buffer

### 3. **Error Handling Strategy**: Retry Failed Agent Only
- **Reasoning**:
  - Faster than retrying entire Phase 2 (1 agent vs 3 agents)
  - Preserves successful agent outputs (no wasted work)
  - Fallback: If retry fails, offer to retry entire Phase 2 OR continue with partial results
- **Source**: INITIAL.md "Open Questions" section preference for speed

### 4. **Output Aggregation**: Post-Process Merge
- **Reasoning**:
  - Simpler than real-time streaming (no complex multiplexing)
  - Each agent writes to separate log file (no race conditions)
  - Display all logs after `wait` completes
  - User can inspect individual agent logs if needed
- **Source**: INITIAL.md recommendation, `phase_orchestration.sh` pattern

### 5. **Archon Task Granularity**: 3 Separate Tasks for Phase 2
- **Reasoning**:
  - Better visibility in Archon UI (see which agent is running/done)
  - Easier debugging (identify which Phase 2 agent failed)
  - Aligns with Vibes generate-prp.md pattern (lines 90-101)
  - Task order priority: 100 (Phase 1), 90 (2A), 85 (2B), 80 (2C)
- **Source**: `.claude/commands/generate-prp.md` lines 86-101, `.claude/patterns/archon-workflow.md`

### 6. **Command Location**: `.codex/commands/` (Not `commands/codex/`)
- **Reasoning**:
  - Mirrors `.claude/commands/` directory structure
  - Clear separation: `.codex/` for Codex, `.claude/` for Claude
  - Existing pattern in bootstrap: `docs/codex-*.md`, `scripts/codex/`
  - Consistent with convention: tool-specific directories at root
- **Source**: INITIAL.md "Command Infrastructure" checklist item

### 7. **Validation Loop Max Attempts**: 5 for Execute-PRP
- **Reasoning**:
  - Enough iterations to fix common issues (linting, type errors, test failures)
  - Not so many that it loops indefinitely on broken code
  - Aligns with Vibes quality-gates.md pattern (max 5 attempts)
  - User can manually intervene after 5 if needed
- **Source**: `.claude/patterns/quality-gates.md` lines 49-70

### 8. **Coverage Threshold**: 70%
- **Reasoning**:
  - Standard industry threshold for good coverage
  - Achievable for most features without excessive boilerplate
  - Aligns with INITIAL.md requirement ("≥70% coverage")
  - Can be overridden per-PRP if needed
- **Source**: INITIAL.md line 70, quality-gates.md line 122

### 9. **Manifest Concurrent Write Handling**: Atomic Writes with Temp File
- **Reasoning**:
  - Prevents JSON corruption from simultaneous `>>` operations
  - Pattern: Write to temp file, `mv` to manifest (atomic on Unix)
  - Alternative: Use `flock` for file locking (more complex)
  - Simpler than process coordination
- **Source**: INITIAL.md gotcha "Manifest Corruption" (line 384), standard Unix pattern

### 10. **Approval Policy**: `on-failure` for Phase 2 Reads
- **Reasoning**:
  - Phase 2 agents are read-only (Archon search, codebase grep, file reads)
  - No writes = low risk, can auto-approve
  - Prevents approval blocking in parallel execution
  - Write operations (Phase 1, 4) use `on-request` for safety
- **Source**: INITIAL.md gotcha "Approval Blocking" (line 385), codex config pattern

## Success Criteria

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

## Next Steps for Downstream Agents

### For Codebase Researcher
**Focus Areas**:
1. **Bash Orchestration Patterns**:
   - Search: `grep -r "wait \$PID" scripts/ prps/`
   - Extract: Parallel execution with PID tracking and exit code capture
   - Pattern: Dependency management with associative arrays

2. **Codex CLI Integration**:
   - Search: `grep -r "codex exec" prps/codex_integration/`
   - Extract: Profile usage (`--profile codex-prp`), timeout wrapping, log redirection
   - Pattern: Error handling with retry logic

3. **Security Validation**:
   - Search: `grep -r "extract_feature_name" .claude/`
   - Extract: 6-level validation pattern from generate-prp.md
   - Pattern: `removeprefix()` vs `replace()`, redundant prefix check

### For Documentation Hunter
**Primary Documentation**:
1. **Codex CLI Official Docs**:
   - URL: Search Archon for "Codex CLI reference" or "codex exec documentation"
   - Focus: `codex exec` flags, exit codes, profile configuration, approval policies
   - Critical: Session management, timeout behavior, parallel invocation limits

2. **Bash Job Control**:
   - URL: `man bash` section on Job Control
   - Focus: Background processes (`&`), `wait` command, PID variables (`$!`)
   - Critical: Exit code capture timing, zombie process handling

3. **GNU Timeout**:
   - URL: `man timeout` or GNU coreutils docs
   - Focus: Signal handling, exit codes (124 = timeout, 125 = timeout error)
   - Critical: Graceful vs forceful termination

### For Example Curator
**Extract to `prps/codex_commands/examples/`**:

1. **`phase_orchestration.sh`** (ALREADY EXISTS):
   - Source: `prps/codex_integration/examples/phase_orchestration.sh`
   - Why: Complete multi-phase workflow with parallel execution pattern
   - Extract: Lines 64-161 (parallel group execution)

2. **`manifest_logger.sh`** (ALREADY EXISTS):
   - Source: `prps/codex_integration/examples/manifest_logger.sh`
   - Why: JSONL logging, phase validation, summary reports
   - Extract: Core functions for reuse in new commands

3. **`parallel_minimal.sh`** (CREATE NEW):
   - Source: Synthesize from INITIAL.md lines 450-522 (prototype)
   - Why: Minimal viable parallel execution example
   - Extract: Just the core pattern (launch 3, wait all, check exits)

4. **`validation_loop.sh`** (CREATE NEW):
   - Source: Synthesize from quality-gates.md + execute-prp requirements
   - Why: Validation iteration with max attempts
   - Extract: Ruff → mytest → pytest loop with error analysis

5. **`quality_gate.sh`** (CREATE NEW):
   - Source: Synthesize from quality-gates.md lines 7-32
   - Why: PRP score extraction and enforcement
   - Extract: Regex score parsing, interactive choice handling

### For Gotcha Detective
**Investigate These Known Problem Areas**:

1. **Exit Code Loss** (HIGH SEVERITY):
   - Issue: `wait` without immediate capture loses exit codes
   - Detection: Multiple `wait` calls without `EXIT=$?` between them
   - Solution: Pattern from line 490-492 of INITIAL.md: `wait $PID; EXIT=$?` per process

2. **Output Interleaving** (HIGH SEVERITY):
   - Issue: Parallel agents writing to stdout/stderr corrupt console output
   - Detection: Mixed output in single log file
   - Solution: Separate log files per agent (line 379 of INITIAL.md)

3. **Zombie Processes** (MEDIUM SEVERITY):
   - Issue: Background job hangs, never completes, blocks `wait` forever
   - Detection: `wait` blocks longer than expected timeout
   - Solution: Wrap `codex exec` with GNU `timeout` command (line 381)

4. **Race Condition on Manifest** (MEDIUM SEVERITY):
   - Issue: Concurrent `>>` to manifest.jsonl can interleave JSON lines
   - Detection: Invalid JSON in manifest, parsing errors
   - Solution: Atomic writes via temp file + `mv` (line 384)

5. **Approval Blocking** (MEDIUM SEVERITY):
   - Issue: One Phase 2 agent waits for approval, others complete, workflow hangs
   - Detection: Process stuck on stdin read
   - Solution: Use `approval_policy = "on-failure"` for Phase 2 reads (line 385)

6. **Sequential Dependency Violation** (HIGH SEVERITY):
   - Issue: Phase 3 starts before Phase 2 completes, has no inputs
   - Detection: Gotcha detection runs with missing research docs
   - Solution: Explicit `wait` after parallel group, validate all exit codes before Phase 3

7. **Profile Omission** (HIGH SEVERITY):
   - Issue: `codex exec` without `--profile codex-prp` uses wrong config
   - Detection: Wrong model, wrong MCP servers, wrong approval policy
   - Solution: Always include `--profile codex-prp` in wrapper scripts (gotchas.md line 653)

8. **Timeout Exit Code Confusion** (MEDIUM SEVERITY):
   - Issue: Timeout exit code 124 treated as agent failure, not timeout
   - Detection: Retry logic triggers on timeout instead of reporting timeout
   - Solution: Check `$? == 124` specifically for timeout handling

---

## Summary for PRP Assembler

**This feature is a DIRECT REPLICATION of Vibes' Claude-based PRP generation workflow, adapted for Codex CLI**:

1. **Same 5-Phase Structure**: Phase 0 (setup) → Phase 1 (analysis) → Phase 2 (parallel research) → Phase 3 (gotchas) → Phase 4 (assembly)

2. **Key Innovation**: Bash-based parallel execution (not Task() subagents) with job control for 3x speedup

3. **Existing Infrastructure**:
   - `scripts/codex/log-phase.sh` ALREADY EXISTS (reuse directly)
   - Examples in `prps/codex_integration/examples/` provide patterns
   - Bootstrap complete (Codex CLI installed, profile configured)

4. **Implementation Strategy**:
   - **Phase 1**: Build generate-prp command (THIS PRP)
   - **Phase 2**: Build execute-prp command (FOLLOW-UP PRP)
   - Test each in isolation before integration

5. **Quality Gates**:
   - PRP generation: ≥8/10 score
   - PRP execution: ≥70% coverage
   - Integration: <20min end-to-end

6. **Gotchas to Document**:
   - Exit code capture timing (CRITICAL)
   - Output interleaving prevention
   - Manifest race conditions
   - Approval policy for parallel reads
   - Profile enforcement in all scripts

7. **Testing Requirements**:
   - Parallel execution verification (concurrent timestamps)
   - Quality gate enforcement (reject <8/10)
   - Validation loop iteration (max 5 attempts)
   - Partial failure handling (1 of 3 agents fails)

**Confidence Level**: HIGH - Clear requirements, proven patterns in codebase, existing infrastructure (log-phase.sh, examples), well-defined success criteria.

**Risk Areas**:
- Bash parallelization complexity (mitigated by examples)
- Codex CLI behavior under parallel load (mitigated by timeout + retry)
- Manifest race conditions (mitigated by atomic writes)

**Recommendation**: Proceed with implementation. Start with `codex-generate-prp.sh` wrapper script, validate parallel execution, then build command prompts.
