# INITIAL: Codex Command Implementation with Parallel Execution

## FEATURE

Implement production-ready Codex commands (`codex-generate-prp` and `codex-execute-prp`) that mirror Vibes' five-phase PRP workflow with **parallel Phase 2 execution** for 3x speedup.

**Why we care:**
- **Parallel execution**: Phase 2 research (codebase, docs, examples) runs simultaneously - 5 min vs 15 min sequential
- **Model flexibility**: Leverage o4-mini for generation, gpt-5-codex for execution, o3 for deep analysis
- **Cross-validation**: Run same PRP through Claude and Codex, compare quality scores
- **Proven patterns**: Reuse Vibes' battle-tested orchestration, validation, and quality gates
- **Complete automation**: End-to-end PRP workflow from INITIAL.md to validated implementation

**What "done" looks like:**
- `.codex/commands/codex-generate-prp.md` - Full prompt for 5-phase PRP generation
- `.codex/commands/codex-execute-prp.md` - Full prompt for PRP execution with validation loops
- Bash wrapper scripts in `scripts/codex/` for command orchestration
- **Parallel Phase 2**: 3 agents (codebase researcher, doc hunter, example curator) run simultaneously
- Manifest logging capturing all phases with timestamps
- Quality gates enforced (≥8/10 for PRPs, ≥70% coverage for code)
- Integration test proving end-to-end workflow in <15 min

**Scope guardrails:**
- Commands mirror `.claude/commands/generate-prp.md` structure (Phase 0-4)
- Use prototype commands from `prps/INITIAL_codex_integration.md` as starting point
- Parallel execution via bash job control (`&` + `wait`) or `codex exec` concurrent calls
- Reuse Vibes patterns: security validation, JSONL logging, quality gates, approval handling
- Phase 1 focus: Generate-PRP command with proven parallel pattern
- Phase 2 focus: Execute-PRP command with validation loops

---

## CURRENT STATE CHECKLIST

**Prerequisites (from Phase 1 - Bootstrap):**
- [x] Codex CLI installed and authenticated
- [x] Profile configured (`~/.codex/config.toml` with `[profiles.codex-prp]`)
- [x] Documentation complete (`docs/codex-bootstrap.md`, `docs/codex-config.md`)
- [x] Artifact structure defined (`prps/{feature}/codex/`)
- [x] Example code extracted (`prps/codex_integration/examples/`)

**Command Infrastructure:**
- [ ] Command location decision (use `.codex/commands/` per naming convention)
- [ ] Bash wrapper scripts in `scripts/codex/` for orchestration
- [ ] Logging helpers (`scripts/codex/log-phase.sh` for manifest updates)
- [ ] Approval handlers (`scripts/codex/handle-approval.sh` for stdin flow)
- [ ] Validation scripts (pre-flight checks, quality gates)

**Parallel Execution Pattern:**
- [ ] Understand bash job control (`&`, `wait`, `$!`, exit code capture)
- [ ] OR understand concurrent `codex exec` (multiple processes with log aggregation)
- [ ] Error handling for partial failures (1 of 3 agents fails)
- [ ] Output aggregation (merge Phase 2 results into planning/)
- [ ] Timeout handling (kill hung processes after threshold)

**Generate-PRP Command:**
- [ ] Phase 0: Setup & validation (auth, dirs, Archon project)
- [ ] Phase 1: Feature analysis (sequential)
- [ ] **Phase 2: Parallel research** (codebase + docs + examples simultaneously)
- [ ] Phase 3: Gotcha detection (sequential, uses Phase 2 outputs)
- [ ] Phase 4: PRP assembly (sequential, synthesizes all research)
- [ ] Quality gate: Score ≥8/10 or regenerate

**Execute-PRP Command:**
- [ ] Task analysis and dependency mapping
- [ ] Implementation with progress tracking
- [ ] Validation loop (ruff → pytest → retry on fail, max 3 attempts)
- [ ] Coverage enforcement (≥70%)
- [ ] Completion report with metrics

---

## DELIVERABLES

### 1. Generate-PRP Command
**File:** `.codex/commands/codex-generate-prp.md`

**Contents:**
```markdown
# Create PRP with Codex

[Prompt that orchestrates 5 phases using Codex exec]

## Phase 0: Setup
- Extract feature name from INITIAL path
- Create directories (planning/, examples/)
- Verify Codex auth + profile
- Initialize Archon project

## Phase 1: Feature Analysis
- Read INITIAL.md
- Search Archon for similar PRPs
- Extract requirements + assumptions
- Output: planning/feature-analysis.md

## Phase 2: Parallel Research (3x SPEEDUP)
**Launch 3 agents simultaneously:**

### 2A: Codebase Researcher
- Search Archon code examples
- Search local codebase patterns
- Output: planning/codebase-patterns.md

### 2B: Documentation Hunter
- Search Archon knowledge base
- Find official docs with examples
- Output: planning/documentation-links.md

### 2C: Example Curator
- Extract actual code to examples/
- Create README with guidance
- Output: examples/*, planning/examples-to-include.md

**Execution:**
```bash
# Option A: Bash job control
codex exec --profile codex-prp --prompt "$(cat phase2a.txt)" > logs/2a.log 2>&1 &
PID_2A=$!
codex exec --profile codex-prp --prompt "$(cat phase2b.txt)" > logs/2b.log 2>&1 &
PID_2B=$!
codex exec --profile codex-prp --prompt "$(cat phase2c.txt)" > logs/2c.log 2>&1 &
PID_2C=$!

wait $PID_2A $PID_2B $PID_2C
EXIT_2A=$?; EXIT_2B=$?; EXIT_2C=$?
# Check exit codes, handle failures
```

OR

```bash
# Option B: Concurrent codex exec (if supported)
codex exec --parallel \
  --task "2a:phase2a.txt" \
  --task "2b:phase2b.txt" \
  --task "2c:phase2c.txt"
```

## Phase 3: Gotcha Detection
- Read all Phase 2 outputs
- Search for security/performance issues
- Output: planning/gotchas.md

## Phase 4: PRP Assembly
- Synthesize all research
- Follow prp_base.md structure
- Score PRP (must be ≥8/10)
- Output: prps/{feature}.md
- Store in Archon

## Quality Gate
If score < 8/10:
1. Identify weak sections
2. Re-run specific phases
3. Re-assemble
4. Re-score (max 3 attempts)
```

### 2. Execute-PRP Command
**File:** `.codex/commands/codex-execute-prp.md`

**Contents:**
```markdown
# Execute PRP with Codex

[Prompt that implements PRP with validation loops]

## Phase 1: Task Analysis
- Read PRP task list
- Identify dependencies
- Create execution groups (parallel-safe tasks)
- Output: execution/execution-plan.md

## Phase 2: Implementation
- Execute tasks per plan
- Track progress in Archon
- Capture all file changes

## Phase 3: Validation Loop
**Iteration (max 5 attempts):**
1. Run linters (ruff, mypy, shellcheck)
2. Run tests (pytest with coverage)
3. If failures:
   - Analyze errors
   - Fix issues
   - Retry from step 1
4. If success:
   - Verify ≥70% coverage
   - Proceed to completion

## Phase 4: Completion Report
- List all changes (files created/modified)
- Quality score with justification
- Coverage metrics
- Known blockers/tech debt
- Output: execution/completion-report.md
```

### 3. Bash Orchestration Scripts
**Directory:** `scripts/codex/`

#### `codex-generate-prp.sh`
```bash
#!/usr/bin/env bash
set -euo pipefail

# Wrapper for .codex/commands/codex-generate-prp.md
# Handles:
# - Profile enforcement (--profile codex-prp)
# - Logging (manifest.jsonl updates)
# - Error recovery (retry logic)
# - Quality gate enforcement

INITIAL_PATH="$1"
# ... implementation
```

#### `codex-execute-prp.sh`
```bash
#!/usr/bin/env bash
set -euo pipefail

# Wrapper for .codex/commands/codex-execute-prp.md
# Handles:
# - Validation loop orchestration
# - Coverage checking
# - Archon task updates

PRP_PATH="$1"
# ... implementation
```

#### `log-phase.sh`
```bash
#!/usr/bin/env bash
# Append phase completion to manifest.jsonl
# Usage: log-phase.sh <phase> <exit_code> <feature>

PHASE=$1
EXIT_CODE=$2
FEATURE=$3

jq -nc \
  --arg phase "$PHASE" \
  --argjson exit "$EXIT_CODE" \
  --arg ts "$(date -u +%Y-%m-%dT%H:%M:%SZ)" \
  '{phase: $phase, exit_code: $exit, timestamp: $ts}' \
  >> "prps/$FEATURE/codex/logs/manifest.jsonl"
```

#### `parallel-exec.sh`
```bash
#!/usr/bin/env bash
# Execute multiple codex commands in parallel
# Usage: parallel-exec.sh <feature> <phase2a.txt> <phase2b.txt> <phase2c.txt>

FEATURE=$1
PROMPT_2A=$2
PROMPT_2B=$3
PROMPT_2C=$4

# Launch all 3 in background
codex exec --profile codex-prp --prompt "$(cat "$PROMPT_2A")" \
  > "prps/$FEATURE/codex/logs/phase2a.log" 2>&1 &
PID_2A=$!

codex exec --profile codex-prp --prompt "$(cat "$PROMPT_2B")" \
  > "prps/$FEATURE/codex/logs/phase2b.log" 2>&1 &
PID_2B=$!

codex exec --profile codex-prp --prompt "$(cat "$PROMPT_2C")" \
  > "prps/$FEATURE/codex/logs/phase2c.log" 2>&1 &
PID_2C=$!

# Wait for all, capture exit codes
wait $PID_2A; EXIT_2A=$?
wait $PID_2B; EXIT_2B=$?
wait $PID_2C; EXIT_2C=$?

# Log results
./log-phase.sh "phase2a" "$EXIT_2A" "$FEATURE"
./log-phase.sh "phase2b" "$EXIT_2B" "$FEATURE"
./log-phase.sh "phase2c" "$EXIT_2C" "$FEATURE"

# Exit with failure if any failed
[[ $EXIT_2A -eq 0 && $EXIT_2B -eq 0 && $EXIT_2C -eq 0 ]] || exit 1
```

### 4. Integration Test
**File:** `tests/codex/test_generate_prp.sh`

**Contents:**
```bash
#!/usr/bin/env bash
# End-to-end test of codex-generate-prp

set -euo pipefail

FEATURE="test_parallel_$(date +%s)"
INITIAL="prps/INITIAL_${FEATURE}.md"

# 1. Create minimal INITIAL.md
cat > "$INITIAL" <<'EOF'
# INITIAL: Test Parallel Execution

## FEATURE
Test that Phase 2 runs in parallel.

## DELIVERABLES
1. Proof of parallel execution (logs show concurrent timestamps)
EOF

# 2. Run command
START=$(date +%s)
./scripts/codex/codex-generate-prp.sh "$INITIAL"
END=$(date +%s)
DURATION=$((END - START))

# 3. Validate results
echo "Testing PRP generation with parallel Phase 2..."

# Check: All Phase 2 logs exist
[[ -f "prps/$FEATURE/codex/logs/phase2a.log" ]] || { echo "❌ Missing 2a log"; exit 1; }
[[ -f "prps/$FEATURE/codex/logs/phase2b.log" ]] || { echo "❌ Missing 2b log"; exit 1; }
[[ -f "prps/$FEATURE/codex/logs/phase2c.log" ]] || { echo "❌ Missing 2c log"; exit 1; }

# Check: Timestamps are concurrent (within 5 seconds of each other)
TS_2A=$(jq -r 'select(.phase=="phase2a") | .timestamp' "prps/$FEATURE/codex/logs/manifest.jsonl")
TS_2B=$(jq -r 'select(.phase=="phase2b") | .timestamp' "prps/$FEATURE/codex/logs/manifest.jsonl")
TS_2C=$(jq -r 'select(.phase=="phase2c") | .timestamp' "prps/$FEATURE/codex/logs/manifest.jsonl")

# Convert to epoch, check delta < 5 seconds
# ... timestamp comparison logic

# Check: Duration < 15 min (parallel should be fast)
[[ $DURATION -lt 900 ]] || { echo "⚠️ Took ${DURATION}s (>15min)"; }

# Check: PRP quality ≥8/10
SCORE=$(grep -oP 'Score: \K\d+' "prps/${FEATURE}.md" || echo 0)
[[ $SCORE -ge 8 ]] || { echo "❌ Quality score $SCORE < 8"; exit 1; }

echo "✅ All tests passed!"
echo "   - Parallel execution: verified"
echo "   - Duration: ${DURATION}s"
echo "   - Quality score: $SCORE/10"

# Cleanup
rm -rf "prps/$FEATURE"
```

---

## REFERENCE PATTERNS

**From Vibes Codebase:**
- `.claude/commands/generate-prp.md` → Phase structure, subagent prompts (lines 1-200)
- `.claude/patterns/parallel-subagents.md` → Parallelization theory
- `prps/codex_integration/examples/phase_orchestration.sh` → Bash parallel execution
- `prps/codex_integration/examples/manifest_logger.sh` → JSONL logging
- `prps/codex_integration/examples/approval_handler.sh` → Approval flow

**From Codex Integration Bootstrap:**
- `prps/INITIAL_codex_integration.md` (lines 342-560) → Prototype commands
- `docs/codex-config.md` → Profile configuration
- `docs/codex-validation.md` → Pre-flight checks, quality gates

**Parallelization Resources:**
- GNU Parallel documentation (if using `parallel` command)
- Bash job control (`man bash`, search for "Job Control")
- Exit code handling with multiple background processes

---

## GOTCHAS & MITIGATIONS

| Issue | Impact | Detection | Resolution | Confidence |
|-------|--------|-----------|------------|------------|
| **Partial Phase 2 Failure** | 1 of 3 agents fails, output incomplete | Check all 3 exit codes after `wait` | Retry failed agent only, OR fail entire phase and retry | HIGH |
| **Output Interleaving** | Parallel logs corrupt console output | Mixed output to stdout | Redirect each agent to separate log file (2a.log, 2b.log, 2c.log) | HIGH |
| **Zombie Processes** | Background job hangs, never completes | `wait` blocks forever | Add timeout: `timeout 600 codex exec ...` OR trap + kill | MEDIUM |
| **Exit Code Loss** | `wait` without capturing $? loses exit codes | Can't detect failures | Capture immediately: `wait $PID; EXIT=$?` per process | HIGH |
| **Race Condition** | Agents write to same file simultaneously | Corrupted output files | Ensure each agent writes to unique files, merge after | HIGH |
| **Sequential Dependency** | Phase 3 starts before Phase 2 completes | Gotcha detection has no inputs | Explicit `wait` before Phase 3, check all exit codes | HIGH |
| **Manifest Corruption** | Concurrent `>>` to manifest.jsonl | Interleaved JSON lines | Atomic writes via temp file + `mv`, OR use `flock` for file locking | MEDIUM |
| **Approval Blocking** | One agent waits for stdin, others proceed | Hung process, partial results | Use `approval_policy = "on-failure"` OR pre-approve Phase 2 reads | MEDIUM |
| **Memory Exhaustion** | 3 Codex processes + MCP servers | OOM kill, incomplete results | Monitor with `ps aux`, set ulimit, OR run agents sequentially if low memory | LOW |

---

## IMPLEMENTATION PHASES

### Phase 1: Generate-PRP Command (THIS PRP)
**Deliverables:**
- [ ] `.codex/commands/codex-generate-prp.md` (full prompt)
- [ ] `scripts/codex/codex-generate-prp.sh` (orchestration wrapper)
- [ ] `scripts/codex/log-phase.sh` (manifest logging)
- [ ] `scripts/codex/parallel-exec.sh` (Phase 2 parallelization)
- [ ] `tests/codex/test_generate_prp.sh` (integration test)

**Validation:**
- Run test on sample INITIAL.md
- Verify Phase 2 runs in parallel (log timestamps)
- Confirm PRP quality ≥8/10
- Duration <15 min for typical feature

### Phase 2: Execute-PRP Command (FOLLOW-UP PRP)
**Deliverables:**
- [ ] `.codex/commands/codex-execute-prp.md` (full prompt)
- [ ] `scripts/codex/codex-execute-prp.sh` (orchestration wrapper)
- [ ] Validation loop implementation (max 5 attempts)
- [ ] Coverage enforcement script
- [ ] `tests/codex/test_execute_prp.sh` (integration test)

**Validation:**
- Run on generated PRP from Phase 1
- Verify linters pass
- Confirm ≥70% coverage
- Test retry logic (inject failure, verify fix loop)

---

## OPEN QUESTIONS

1. **Parallel execution method**: Bash job control vs GNU Parallel vs Codex native?
   - **Recommendation**: Start with bash job control (simpler, no deps)
   - Test with 3 agents, measure speedup
   - Consider GNU Parallel if need advanced features (retry, load balancing)

2. **Error handling for partial failures**: Retry failed agent only vs retry entire phase?
   - **Recommendation**: Retry failed agent only (faster)
   - Fallback: If retry fails, retry entire Phase 2 (max 2 total attempts)

3. **Output aggregation**: Real-time streaming vs post-process merge?
   - **Recommendation**: Post-process merge (simpler)
   - Each agent writes to separate log, display all after `wait`

4. **Timeout values**: How long before killing hung Phase 2 agent?
   - **Recommendation**: 600s (10 min) per agent
   - Total Phase 2 timeout: 600s (agents run in parallel)

5. **Archon task tracking**: One task for Phase 2 or 3 separate tasks (2A/2B/2C)?
   - **Recommendation**: 3 separate tasks for visibility
   - Update all to "doing" before parallel launch
   - Update to "done" after successful completion

---

## PROTOTYPE COMMANDS

### Phase 2 Parallel Execution (Core Innovation)

**File:** `phase2-parallel.sh`
```bash
#!/usr/bin/env bash
set -euo pipefail

FEATURE="$1"
PROFILE="codex-prp"
TIMEOUT=600

# Prepare prompts (extract from generate-prp.md)
PROMPT_2A="$(cat .codex/commands/prompts/phase2a-codebase.txt)"
PROMPT_2B="$(cat .codex/commands/prompts/phase2b-docs.txt)"
PROMPT_2C="$(cat .codex/commands/prompts/phase2c-examples.txt)"

echo "🚀 Starting Phase 2 (parallel execution)..."

# Launch all 3 agents in background
timeout "$TIMEOUT" codex exec --profile "$PROFILE" \
  --prompt "$PROMPT_2A" \
  > "prps/$FEATURE/codex/logs/phase2a.log" 2>&1 &
PID_2A=$!

timeout "$TIMEOUT" codex exec --profile "$PROFILE" \
  --prompt "$PROMPT_2B" \
  > "prps/$FEATURE/codex/logs/phase2b.log" 2>&1 &
PID_2B=$!

timeout "$TIMEOUT" codex exec --profile "$PROFILE" \
  --prompt "$PROMPT_2C" \
  > "prps/$FEATURE/codex/logs/phase2c.log" 2>&1 &
PID_2C=$!

echo "   Agent 2A (codebase): PID $PID_2A"
echo "   Agent 2B (docs):     PID $PID_2B"
echo "   Agent 2C (examples): PID $PID_2C"
echo "   Waiting for completion..."

# Wait for all, capture exit codes
wait $PID_2A; EXIT_2A=$?
wait $PID_2B; EXIT_2B=$?
wait $PID_2C; EXIT_2C=$?

# Log to manifest
./scripts/codex/log-phase.sh "phase2a-codebase" "$EXIT_2A" "$FEATURE"
./scripts/codex/log-phase.sh "phase2b-docs" "$EXIT_2B" "$FEATURE"
./scripts/codex/log-phase.sh "phase2c-examples" "$EXIT_2C" "$FEATURE"

# Check results
if [[ $EXIT_2A -eq 0 && $EXIT_2B -eq 0 && $EXIT_2C -eq 0 ]]; then
  echo "✅ Phase 2 complete (all agents succeeded)"

  # Verify outputs exist
  [[ -f "prps/$FEATURE/codex/planning/codebase-patterns.md" ]] || { echo "❌ Missing codebase-patterns.md"; exit 1; }
  [[ -f "prps/$FEATURE/codex/planning/documentation-links.md" ]] || { echo "❌ Missing documentation-links.md"; exit 1; }
  [[ -f "prps/$FEATURE/codex/planning/examples-to-include.md" ]] || { echo "❌ Missing examples-to-include.md"; exit 1; }

  exit 0
else
  echo "❌ Phase 2 failed:"
  [[ $EXIT_2A -ne 0 ]] && echo "   - Agent 2A (codebase) exit $EXIT_2A"
  [[ $EXIT_2B -ne 0 ]] && echo "   - Agent 2B (docs) exit $EXIT_2B"
  [[ $EXIT_2C -ne 0 ]] && echo "   - Agent 2C (examples) exit $EXIT_2C"

  # Display failed logs
  [[ $EXIT_2A -ne 0 ]] && echo "=== Agent 2A Log ===" && tail -20 "prps/$FEATURE/codex/logs/phase2a.log"
  [[ $EXIT_2B -ne 0 ]] && echo "=== Agent 2B Log ===" && tail -20 "prps/$FEATURE/codex/logs/phase2b.log"
  [[ $EXIT_2C -ne 0 ]] && echo "=== Agent 2C Log ===" && tail -20 "prps/$FEATURE/codex/logs/phase2c.log"

  exit 1
fi
```

---

## SUCCESS METRICS

**Phase 1 (Generate-PRP) complete when:**
- [ ] `.codex/commands/codex-generate-prp.md` executable via wrapper
- [ ] Phase 2 parallel execution proven (concurrent timestamps in manifest)
- [ ] Speedup measured: parallel <10 min vs sequential ~20 min
- [ ] Quality gate enforced (test with low-quality PRP, verify regeneration)
- [ ] Integration test passes (end-to-end on sample INITIAL)

**Phase 2 (Execute-PRP) complete when:**
- [ ] `.codex/commands/codex-execute-prp.md` executable via wrapper
- [ ] Validation loop proven (inject linting error, verify fix retry)
- [ ] Coverage gate enforced (test with <70% coverage, verify failure)
- [ ] Completion report includes all required metrics
- [ ] Integration test passes (implement sample PRP to completion)

**Full Integration Success:**
- [ ] Generate PRP with Codex in <15 min (proven parallel speedup)
- [ ] Execute PRP with Codex, pass all validation gates
- [ ] Compare Claude vs Codex outputs (quality, time, coverage)
- [ ] Document lessons learned for cross-agent workflows
- [ ] Prove end-to-end: INITIAL.md → Codex PRP → Codex implementation → validated code
