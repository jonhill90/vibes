# Documentation Resources: codex_commands

## Overview

This document provides comprehensive documentation for implementing production-ready Codex commands with parallel execution orchestration. Coverage includes: Bash job control (background processes, wait, exit codes), GNU timeout (signal handling, process killing), JSONL concurrent write patterns, and existing Vibes PRP generation patterns. All sources validated with working code examples and specific sections identified for implementation.

## Primary Framework Documentation

### Bash Job Control (GNU Bash Manual)
**Official Docs**: https://www.gnu.org/software/bash/manual/html_node/Job-Control-Builtins.html
**Version**: Bash 4.0+ (wait -n requires Bash 4.3+, wait -p requires Bash 5.1+)
**Archon Source**: Not in Archon
**Relevance**: 10/10 - Core mechanism for parallel Phase 2 execution

**Sections to Read**:
1. **Job Control Builtins**: https://www.gnu.org/software/bash/manual/html_node/Job-Control-Builtins.html
   - **Why**: Explains `wait`, `jobs`, background process management
   - **Key Concepts**:
     - `wait [id]` waits for child processes and returns exit status
     - Each `id` can be PID or job specification (jobspec)
     - `wait` without args waits for all running background jobs
     - Returns exit status of last specified process
     - Returns 127 if no child processes match

2. **Job Control Basics**: https://www.gnu.org/software/bash/manual/html_node/Job-Control-Basics.html
   - **Why**: Explains background processes, process groups, job specifications
   - **Key Concepts**:
     - `&` operator launches command in background
     - `$!` holds PID of last background process
     - Process groups allow managing related processes
     - Job control enables foreground/background switching

**Code Examples from Docs**:
```bash
# Example 1: Wait for specific process
# Source: GNU Bash Manual
command1 &
pid=$!
wait $pid
echo "Exit code: $?"
```

**Gotchas from Documentation**:
- Exit code must be captured immediately after `wait` (it's lost on next command)
- `wait` without args waits for ALL background jobs (may be unexpected)
- Returns 127 if no matching child processes (check this explicitly)
- Signal-interrupted `wait` returns status > 128

---

### GNU Timeout (GNU Coreutils)
**Official Docs**: https://man7.org/linux/man-pages/man1/timeout.1.html
**Version**: GNU Coreutils 8.0+ (kill-after requires 8.13+)
**Archon Source**: Not in Archon
**Relevance**: 10/10 - Critical for preventing zombie processes in parallel execution

**Sections to Read**:
1. **timeout(1) Manual Page**: https://man7.org/linux/man-pages/man1/timeout.1.html
   - **Why**: Complete reference for timeout command, signal handling, exit codes
   - **Key Concepts**:
     - Syntax: `timeout [OPTION] DURATION COMMAND [ARG]...`
     - Default signal: TERM (can be changed with `-s`)
     - Duration suffixes: s (seconds), m (minutes), h (hours), d (days)
     - Exit code 124 = timeout occurred
     - Exit code 125 = timeout command itself failed
     - Exit code 137 = killed by KILL signal (128+9)

2. **Signal Handling Options**: https://man7.org/linux/man-pages/man1/timeout.1.html
   - **Why**: Explains graceful vs forceful termination
   - **Key Concepts**:
     - `-s, --signal=SIGNAL`: Specify signal (default TERM)
     - `-k, --kill-after=DURATION`: Send KILL if still running after initial timeout
     - `-v, --verbose`: Report signals sent to stderr
     - `-p, --preserve-status`: Exit with same status as command (not timeout codes)

**Code Examples from Docs**:
```bash
# Example 1: Basic timeout (10 seconds)
# Source: https://man7.org/linux/man-pages/man1/timeout.1.html
timeout 10s long_running_command

# Example 2: Timeout with forceful kill after 5s
# Source: https://man7.org/linux/man-pages/man1/timeout.1.html
timeout -k 5s 10s slow_process

# Example 3: Check for timeout specifically
# Source: Derived from man page exit codes
timeout 10s command
exit_code=$?
if [ $exit_code -eq 124 ]; then
    echo "Command timed out"
elif [ $exit_code -eq 0 ]; then
    echo "Command succeeded"
else
    echo "Command failed with exit $exit_code"
fi
```

**Gotchas from Documentation**:
- Exit code 124 specifically means timeout (NOT general failure)
- Exit code 125 means timeout command failed (check command exists)
- Duration "0" disables timeout (use with caution)
- Default TERM signal can be blocked/caught by processes (use `-k` for guarantee)
- Timeout occurs AFTER duration, not at exact duration (small delay possible)

---

## Library Documentation

### 1. Bash Background Process Management (Stack Overflow)
**Official Docs**: https://stackoverflow.com/questions/356100/how-to-wait-in-bash-for-several-subprocesses-to-finish-and-return-exit-code-0
**Purpose**: Practical patterns for waiting on multiple background processes
**Archon Source**: Not in Archon
**Relevance**: 10/10 - Direct application to Phase 2 parallel execution

**Key Pages**:
- **Wait for Multiple Processes with Exit Code Tracking**: https://stackoverflow.com/questions/356100/how-to-wait-in-bash-for-several-subprocesses-to-finish-and-return-exit-code-0
  - **Use Case**: Exact pattern needed for Phase 2 (launch 3 agents, wait for all, check exits)
  - **Example**: Store PIDs in array, wait on each
  ```bash
  pids=()
  for i in $n_procs; do
      ./procs[${i}] &
      pids[${i}]=$!
  done

  for pid in "${pids[@]}"; do
      wait $pid
  done
  ```

- **Failure Tracking Pattern**:
  - **Use Case**: Count how many Phase 2 agents failed
  - **Example**: Track failures with counter
  ```bash
  FAIL=0
  for job in `jobs -p`; do
      wait $job || let "FAIL+=1"
  done

  if [ "$FAIL" == "0" ]; then
      echo "YAY!"
  else
      echo "FAIL! ($FAIL)"
  fi
  ```

**API Reference**:
- **`$!`**: PID of last background process
  - **Signature**: Special variable (read-only)
  - **Returns**: Integer PID
  - **Example**:
  ```bash
  command &
  pid=$!
  echo "Started PID: $pid"
  ```

- **`wait $pid`**: Wait for specific process
  - **Signature**: `wait [id ...]`
  - **Returns**: Exit status of process
  - **Example**:
  ```bash
  wait $pid
  exit_code=$?
  ```

---

### 2. File Locking with flock (Linux Manual)
**Official Docs**: https://man7.org/linux/man-pages/man2/flock.2.html
**Purpose**: Prevent JSONL manifest corruption from concurrent writes
**Archon Source**: Not in Archon
**Relevance**: 8/10 - Alternative to atomic write pattern for manifest logging

**Key Pages**:
- **flock(1) Command Line Tool**: https://linux.die.net/man/1/flock
  - **Use Case**: Lock manifest file during Phase 2 concurrent writes
  - **Example**: Script integration method
  ```bash
  #!/bin/bash
  (
    flock -n 200 || exit 1
    # Write to manifest here (protected)
    echo '{"phase":"phase2a",...}' >> manifest.jsonl
  ) 200>/var/tmp/manifest.lock
  ```

- **Non-Blocking Lock with Error Handling**: https://unix.stackexchange.com/questions/184259/how-to-use-flock-and-file-descriptors-to-lock-a-file-and-write-to-the-locked-fil
  - **Use Case**: Fail fast if manifest is locked (don't block parallel agents)
  - **Example**: Alternative syntax
  ```bash
  #!/bin/bash
  exec 200>/var/lock/manifest.lock
  flock -n 200 || exit 1
  # Protected write
  echo "$entry" >> manifest.jsonl
  # Lock auto-released on exit
  ```

**Applicable patterns**:
- Exclusive locks (LOCK_EX) for writes to manifest
- Non-blocking mode (-n) to avoid deadlocks in parallel execution
- File descriptor approach (200>) for scoped locking
- Auto-release on script exit (no manual unlock needed)

---

### 3. Atomic File Writes (Unix Stack Exchange)
**Resource**: https://unix.stackexchange.com/questions/322038/is-mv-atomic-on-my-fs
**Type**: Community Standard (Unix conventions)
**Relevance**: 9/10 - Alternative to flock for manifest integrity

**Key Practices**:
1. **Write-then-Rename Pattern**:
   - **Why**: `rename()` system call is atomic on same filesystem
   - **Example**:
   ```bash
   # Write to temp file
   echo '{"phase":"phase2a","status":"success",...}' > /tmp/manifest.$$

   # Atomic append via rename
   cat /tmp/manifest.$$ >> manifest.jsonl
   rm /tmp/manifest.$$
   ```

2. **Same Filesystem Requirement**:
   - **Why**: Cross-filesystem renames are NOT atomic (copy + delete)
   - **Example**: Create temp in same directory as target
   ```bash
   # CORRECT: Same directory (same filesystem)
   temp_file="prps/${feature}/codex/logs/.manifest.tmp.$$"
   target_file="prps/${feature}/codex/logs/manifest.jsonl"
   echo "$entry" > "$temp_file"
   cat "$temp_file" >> "$target_file"  # Atomic if same FS
   rm "$temp_file"
   ```

3. **Flush Before Rename**:
   - **Why**: Ensure data actually written to disk before rename
   - **Example**: Use `sync` or ensure file descriptor closed
   ```bash
   echo "$entry" > "$temp_file"
   sync  # Flush to disk
   mv "$temp_file" "$target_file"
   ```

---

## Integration Guides

### Bash Parallel Execution with Timeout (Phase Orchestration Example)
**Guide URL**: /Users/jon/source/vibes/prps/codex_integration/examples/phase_orchestration.sh
**Source Type**: Local Codebase Example
**Quality**: 10/10
**Archon Source**: N/A (local file)

**What it covers**:
- Multi-phase workflow with dependency management
- Parallel group execution (Phase 2: 3 agents simultaneously)
- PID tracking and exit code capture
- Error handling with retry/skip/abort options
- Progress reporting and status tracking

**Code examples**:
```bash
# Source: prps/codex_integration/examples/phase_orchestration.sh (lines 112-161)
execute_parallel_group() {
    local group_name="$1"
    local phases="${PARALLEL_GROUPS[$group_name]}"

    IFS=',' read -ra PHASE_ARRAY <<< "$phases"

    # Start all phases in background
    local pids=()
    local phase_names=()

    for phase in "${PHASE_ARRAY[@]}"; do
        echo "🚀 Starting: ${phase}"
        execute_phase "$phase" &
        pids+=($!)
        phase_names+=("$phase")
    done

    # Wait for all phases to complete
    local all_success=true
    local failed_phases=()

    for i in "${!pids[@]}"; do
        local pid="${pids[$i]}"
        local phase="${phase_names[$i]}"

        if wait "$pid"; then
            echo "✅ Completed: ${phase}"
        else
            echo "❌ Failed: ${phase}"
            all_success=false
            failed_phases+=("$phase")
        fi
    done

    if [ "$all_success" = false ]; then
        echo "❌ Parallel group failed. Failed phases:"
        printf '  - %s\n' "${failed_phases[@]}"
        return 1
    fi

    return 0
}
```

**Applicable patterns**:
- PID array storage for multiple background processes
- Associative arrays for phase dependencies
- Loop over PIDs with `wait` to capture exit codes
- Aggregate success/failure tracking
- User-friendly error reporting with failed phase names

---

### JSONL Manifest Logging (Existing Script)
**Guide URL**: /Users/jon/source/vibes/scripts/codex/log-phase.sh
**Source Type**: Production Script (REUSE DIRECTLY)
**Quality**: 10/10 - Already battle-tested
**Archon Source**: N/A (local file)

**What it covers**:
- Phase start/complete logging to JSONL
- Feature name security validation (6 levels)
- ISO 8601 UTC timestamps
- Phase validation and coverage checking
- Summary report generation from manifest

**Code examples**:
```bash
# Source: scripts/codex/log-phase.sh (lines 73-94)
log_phase_start() {
    local feature="$1"
    local phase="$2"

    validate_feature_name "$feature" || return 1

    local manifest=$(get_manifest_path "$feature")
    ensure_manifest_dir "$manifest"

    local entry=$(cat <<EOF
{"phase":"${phase}","status":"started","timestamp":"$(get_timestamp)"}
EOF
)

    # Append to manifest (atomic write)
    echo "$entry" >> "$manifest"

    echo "📝 Logged phase start: ${phase}" >&2
}

# Source: scripts/codex/log-phase.sh (lines 97-130)
log_phase_complete() {
    local feature="$1"
    local phase="$2"
    local exit_code="$3"
    local duration_sec="${4:-0}"

    validate_feature_name "$feature" || return 1

    local manifest=$(get_manifest_path "$feature")
    ensure_manifest_dir "$manifest"

    local status="success"
    if [ "$exit_code" -ne 0 ]; then
        status="failed"
    fi

    local entry=$(cat <<EOF
{"phase":"${phase}","status":"${status}","exit_code":${exit_code},"duration_sec":${duration_sec},"timestamp":"$(get_timestamp)"}
EOF
)

    echo "$entry" >> "$manifest"
}
```

**Applicable patterns**:
- Simple `>>` append for JSONL (each line is valid JSON)
- Manifest path: `prps/{feature}/codex/logs/manifest.jsonl`
- Security validation before any file operations
- ISO 8601 timestamps: `date -u +"%Y-%m-%dT%H:%M:%SZ"`
- Status tracking: "started" | "success" | "failed"

---

## Best Practices Documentation

### Feature Name Security Validation (6-Level Pattern)
**Resource**: /Users/jon/source/vibes/.claude/commands/generate-prp.md (lines 24-69)
**Type**: Official Vibes Pattern
**Relevance**: 10/10 - MUST implement for security

**Key Practices**:
1. **Path Traversal Check**: Reject `..` in feature name or filepath
   - **Why**: Prevents directory traversal attacks
   - **Example**: `if ".." in filepath: raise ValueError(...)`

2. **Whitelist Characters**: Only alphanumeric, underscore, hyphen
   - **Why**: Prevents shell injection
   - **Example**: `if not re.match(r'^[a-zA-Z0-9_-]+$', feature): raise ValueError(...)`

3. **Length Limit**: Max 50 characters
   - **Why**: Prevents buffer overflows, filesystem limits
   - **Example**: `if len(feature) > 50: raise ValueError(...)`

4. **Dangerous Characters Check**: Reject `$`, `` ` ``, `;`, `&`, `|`, etc.
   - **Why**: Prevents command injection
   - **Example**:
   ```python
   dangerous = ['$', '`', ';', '&', '|', '>', '<', '\n', '\r']
   if any(c in feature for c in dangerous): raise ValueError(...)
   ```

5. **Use removeprefix() Not replace()**: Strip INITIAL_ prefix safely
   - **Why**: `replace()` removes ALL occurrences (e.g., "INITIAL_INITIAL_test" → "test")
   - **Why**: `removeprefix()` only removes from start (PEP 616)
   - **Example**:
   ```python
   # CORRECT
   feature = basename.removeprefix("INITIAL_")

   # WRONG - removes all occurrences
   feature = basename.replace("INITIAL_", "")
   ```

6. **Redundant prp_ Prefix Check**: Reject if feature starts with "prp_"
   - **Why**: Files in `prps/` directory don't need "prp_" prefix (redundant)
   - **Example**:
   ```python
   if validate_no_redundant and feature.startswith("prp_"):
       raise ValueError(f"Redundant 'prp_' prefix: {feature}")
   ```

---

### Parallel Subagent Execution Pattern
**Resource**: /Users/jon/source/vibes/.claude/patterns/parallel-subagents.md
**Type**: Official Vibes Pattern
**Relevance**: 9/10 - Theory for Phase 2 parallelization

**Key Practices**:
1. **All Task() Calls in SINGLE Response**: For parallel execution
   - **Why**: Loop over Task() = sequential (sum of times)
   - **Why**: Multiple Task() in one response = parallel (max of times)
   - **Example**: See generate-prp.md lines 152-175 (3 Task() calls together)

2. **Archon Batch Updates**: Before/after parallel group, not interleaved
   - **Why**: Archon updates during parallel tasks breaks parallelism
   - **Example**:
   ```python
   # CORRECT: Update all to "doing" BEFORE parallel tasks
   for i in [1, 2, 3]:
       mcp__archon__manage_task("update", task_id=task_ids[i], status="doing")

   # Launch 3 Task() calls in single response
   Task(...)
   Task(...)
   Task(...)

   # Update all to "done" AFTER parallel tasks
   for i in [1, 2, 3]:
       mcp__archon__manage_task("update", task_id=task_ids[i], status="done")
   ```

3. **No File Conflicts**: Validate outputs don't overlap
   - **Why**: Race conditions if multiple tasks write same file
   - **Example**: Phase 2 outputs to different files:
     - 2A: `codebase-patterns.md`
     - 2B: `documentation-links.md`
     - 2C: `examples-to-include.md` + `examples/*.sh`

4. **Limit to 3-6 Tasks**: Per parallel group
   - **Why**: Too many = resource contention, harder debugging
   - **Example**: Phase 2 = exactly 3 tasks (optimal for research phase)

---

### Exit Code Capture Timing (CRITICAL GOTCHA)
**Resource**: prps/codex_integration/examples/phase_orchestration.sh + INITIAL.md gotchas
**Type**: Implementation Gotcha
**Relevance**: 10/10 - MUST get this right or lose exit codes

**Key Practices**:
1. **Capture Exit Code IMMEDIATELY After wait**:
   - **Why**: Exit code lost on next command
   - **Example**:
   ```bash
   # CORRECT - immediate capture
   wait $PID_2A; EXIT_2A=$?
   wait $PID_2B; EXIT_2B=$?
   wait $PID_2C; EXIT_2C=$?

   # WRONG - exit codes lost
   wait $PID_2A
   wait $PID_2B
   wait $PID_2C
   EXIT_2A=$?  # This captures exit code of LAST wait only!
   ```

2. **Don't Reuse $? Variable**:
   - **Why**: Overwritten by every command
   - **Example**: Store in named variables immediately

3. **Validate Before Phase 3**:
   - **Why**: Phase 3 depends on Phase 2 outputs
   - **Example**:
   ```bash
   [[ $EXIT_2A -eq 0 && $EXIT_2B -eq 0 && $EXIT_2C -eq 0 ]] || {
       echo "Phase 2 failed"
       handle_failure
   }
   ```

---

## Testing Documentation

### Bash Script Testing (ShellCheck)
**Official Docs**: https://www.shellcheck.net/
**Archon Source**: Not in Archon

**Relevant Sections**:
- **ShellCheck Wiki**: https://github.com/koalaman/shellcheck/wiki
  - **How to use**: Run `shellcheck script.sh` for static analysis
  - **Common Issues**: SC2086 (unquoted variables), SC2034 (unused variables)

**Test Examples**:
```bash
# Validate all orchestration scripts
shellcheck scripts/codex/*.sh

# Check for specific issues
shellcheck -e SC2086 phase_orchestration.sh
```

---

### Integration Testing Pattern (Parallel Execution Validation)
**Resource**: Derived from feature-analysis.md success criteria
**Type**: Test Strategy
**Relevance**: 10/10

**Test Pattern**:
```bash
#!/bin/bash
# tests/codex/test_generate_prp.sh

# Test 1: Parallel execution proven (concurrent timestamps)
test_parallel_execution() {
    ./scripts/codex/codex-generate-prp.sh prps/INITIAL_test_feature.md

    manifest="prps/test_feature/codex/logs/manifest.jsonl"

    # Extract phase2a/2b/2c start timestamps
    ts_2a=$(grep '"phase":"phase2a"' "$manifest" | grep '"status":"started"' | jq -r '.timestamp')
    ts_2b=$(grep '"phase":"phase2b"' "$manifest" | grep '"status":"started"' | jq -r '.timestamp')
    ts_2c=$(grep '"phase":"phase2c"' "$manifest" | grep '"status":"started"' | jq -r '.timestamp')

    # Convert to epoch seconds
    epoch_2a=$(date -d "$ts_2a" +%s)
    epoch_2b=$(date -d "$ts_2b" +%s)
    epoch_2c=$(date -d "$ts_2c" +%s)

    # Verify all started within 5 seconds (proof of parallelism)
    max_diff=$(( $(echo "$epoch_2a $epoch_2b $epoch_2c" | tr ' ' '\n' | sort -n | tail -1) - $(echo "$epoch_2a $epoch_2b $epoch_2c" | tr ' ' '\n' | sort -n | head -1) ))

    if [ $max_diff -le 5 ]; then
        echo "✅ Parallel execution verified (max diff: ${max_diff}s)"
    else
        echo "❌ Sequential execution detected (max diff: ${max_diff}s)"
        exit 1
    fi
}

# Test 2: Speedup measurement
test_speedup() {
    # Get total Phase 2 duration (max of 3 agents)
    dur_2a=$(get_phase_duration "test_feature" "phase2a")
    dur_2b=$(get_phase_duration "test_feature" "phase2b")
    dur_2c=$(get_phase_duration "test_feature" "phase2c")

    parallel_duration=$(echo "$dur_2a $dur_2b $dur_2c" | tr ' ' '\n' | sort -n | tail -1)
    sequential_duration=$(( dur_2a + dur_2b + dur_2c ))

    speedup=$(echo "scale=2; $sequential_duration / $parallel_duration" | bc)

    echo "Parallel: ${parallel_duration}s"
    echo "Sequential: ${sequential_duration}s (estimated)"
    echo "Speedup: ${speedup}x"

    # Verify at least 2x speedup
    if (( $(echo "$speedup >= 2.0" | bc -l) )); then
        echo "✅ Speedup target met"
    else
        echo "❌ Insufficient speedup"
        exit 1
    fi
}
```

---

## Additional Resources

### Tutorials with Code
1. **Bash Job Control Basics**: https://www.digitalocean.com/community/tutorials/how-to-use-bash-s-job-control-to-manage-foreground-and-background-processes
   - **Format**: Tutorial (text + examples)
   - **Quality**: 8/10
   - **What makes it useful**: Beginner-friendly explanation of jobs, background processes, fg/bg commands

2. **Timeout Command Tutorial**: https://linuxize.com/post/timeout-command-in-linux/
   - **Format**: Tutorial (text + examples)
   - **Quality**: 9/10
   - **What makes it useful**: Practical examples of timeout usage, clear exit code explanations

3. **Wait Command Tutorial**: https://linuxize.com/post/bash-wait/
   - **Format**: Tutorial (text + examples)
   - **Quality**: 9/10
   - **What makes it useful**: Covers wait basics, PID tracking, parallel process management

### API References
1. **Bash Manual - Job Control**: https://www.gnu.org/software/bash/manual/html_node/Job-Control.html
   - **Coverage**: Complete job control subsystem (fg, bg, jobs, wait, suspend)
   - **Examples**: Yes (command syntax and basic usage)

2. **GNU Coreutils - Timeout**: https://www.gnu.org/software/coreutils/timeout
   - **Coverage**: timeout command specification, all options, exit codes
   - **Examples**: Yes (basic usage patterns)

### Community Resources
1. **Bash Wait Multiple Processes Gist**: https://gist.github.com/jzawodn/27452
   - **Type**: GitHub Gist
   - **Why included**: Concise example of parallel wait pattern with exit code checking

2. **Unix Stack Exchange - Bash Parallel Exit Codes**: https://unix.stackexchange.com/questions/344360/collect-exit-codes-of-parallel-background-processes-sub-shells
   - **Type**: Q&A (Stack Exchange)
   - **Why included**: Multiple approaches to capturing parallel exit codes, community-vetted solutions

---

## Documentation Gaps

**Not found in Archon or Web**:
- **Codex CLI Official Documentation**: No public documentation found for `codex exec` command
  - **Recommendation**: Rely on existing examples in `prps/codex_integration/`, infer from observed behavior
  - **Assumption**: Exit codes follow standard Unix conventions (0=success, non-zero=failure)
  - **Assumption**: `--profile` flag behaves like Claude CLI profiles
  - **Validation**: Test actual Codex CLI behavior in prototype scripts

**Outdated or Incomplete**:
- **Bash wait -p and -f options**: Limited documentation (new in Bash 5.x)
  - **Issue**: Most tutorials cover Bash 4.x features only
  - **Suggested alternative**: Use Bash 4.x compatible patterns (PID arrays) for broader compatibility
  - **Workaround**: Test on target system Bash version before using advanced features

- **JSONL Concurrent Write Locking**: No definitive best practice
  - **Issue**: Conflicting recommendations (flock vs atomic writes vs separate files)
  - **Suggested alternative**: Use simplest approach (atomic append with temp file) for MVP
  - **Rationale**: Phase 2 agents complete at different times (natural serialization), rare true concurrency

---

## Quick Reference URLs

For easy copy-paste into PRP:

```yaml
Framework Docs:
  - Bash Job Control: https://www.gnu.org/software/bash/manual/html_node/Job-Control-Builtins.html
  - Bash Job Control Basics: https://www.gnu.org/software/bash/manual/html_node/Job-Control-Basics.html
  - GNU Timeout: https://man7.org/linux/man-pages/man1/timeout.1.html

Library Docs:
  - flock(1): https://linux.die.net/man/1/flock
  - flock(2): https://man7.org/linux/man-pages/man2/flock.2.html

Integration Guides:
  - Phase Orchestration Example: prps/codex_integration/examples/phase_orchestration.sh
  - Manifest Logger Script: scripts/codex/log-phase.sh
  - Vibes Generate-PRP Command: .claude/commands/generate-prp.md

Testing Docs:
  - ShellCheck: https://www.shellcheck.net/

Tutorials:
  - Bash Wait Multiple Processes: https://stackoverflow.com/questions/356100
  - Atomic mv Operations: https://unix.stackexchange.com/questions/322038
  - flock File Locking: https://unix.stackexchange.com/questions/184259
```

---

## Recommendations for PRP Assembly

When generating the PRP:

1. **Include these URLs** in "Documentation & References" section:
   - Bash Job Control Builtins (official reference)
   - GNU timeout man page (exit code reference)
   - Phase orchestration example (implementation pattern)

2. **Extract code examples** shown above into PRP context:
   - Parallel PID tracking pattern (from phase_orchestration.sh lines 124-150)
   - Exit code capture timing (from Stack Overflow + gotchas)
   - Timeout with kill-after pattern (from GNU timeout docs)
   - Feature name validation (from generate-prp.md lines 24-69)

3. **Highlight gotchas** from documentation in "Known Gotchas" section:
   - Exit code loss if not captured immediately after `wait`
   - Timeout exit code 124 vs 125 vs 137 (different meanings)
   - Manifest concurrent write corruption (need atomic append OR flock)
   - Profile omission (`--profile codex-prp` required for all `codex exec`)
   - removeprefix() vs replace() for INITIAL_ stripping

4. **Reference specific sections** in implementation tasks:
   - Task: "Implement parallel Phase 2 execution"
     - See: phase_orchestration.sh lines 112-161 (execute_parallel_group)
     - See: Bash Job Control docs on `wait` command
   - Task: "Add timeout wrapper for agents"
     - See: GNU timeout man page, especially exit codes section
     - Use: `timeout -k 5s 600s codex exec ...`
   - Task: "Validate feature name security"
     - See: generate-prp.md lines 24-69 (6-level validation)
     - Reuse: extract_feature_name() pattern verbatim

5. **Note gaps** so implementation can compensate:
   - Codex CLI undocumented: Add defensive error handling, log full output
   - JSONL locking ambiguous: Start with simplest approach (separate log files per agent)
   - Bash 5.x features: Use Bash 4.x compatible patterns for broader compatibility

---

## Archon Ingestion Candidates

**Documentation not in Archon but should be**:
- https://www.gnu.org/software/bash/manual/html_node/Job-Control.html - Comprehensive bash job control reference, essential for parallel orchestration patterns
- https://man7.org/linux/man-pages/man1/timeout.1.html - GNU timeout official manual, critical for process timeout handling
- https://stackoverflow.com/questions/356100 - Practical bash parallel wait patterns, community-validated solutions
- https://www.shellcheck.net/ - Bash script linting, essential for quality validation

**Why these are valuable for future PRPs**:
- Bash orchestration is common pattern in automation workflows
- Timeout handling prevents zombie processes (recurring issue)
- Exit code patterns reusable across many scripting tasks
- ShellCheck validation should be standard in all bash-based PRPs

---

## Implementation Notes

**Critical Patterns to Extract**:

1. **Parallel Execution with Exit Code Capture** (HIGHEST PRIORITY):
```bash
# Launch 3 agents in background with timeout
timeout 600 codex exec --profile codex-prp --prompt "$(cat phase2a.txt)" > logs/2a.log 2>&1 &
PID_2A=$!

timeout 600 codex exec --profile codex-prp --prompt "$(cat phase2b.txt)" > logs/2b.log 2>&1 &
PID_2B=$!

timeout 600 codex exec --profile codex-prp --prompt "$(cat phase2c.txt)" > logs/2c.log 2>&1 &
PID_2C=$!

# CRITICAL: Capture exit codes IMMEDIATELY after each wait
wait $PID_2A; EXIT_2A=$?
wait $PID_2B; EXIT_2B=$?
wait $PID_2C; EXIT_2C=$?

# Validate all succeeded
if [[ $EXIT_2A -eq 0 && $EXIT_2B -eq 0 && $EXIT_2C -eq 0 ]]; then
    echo "✅ All agents succeeded"
else
    echo "❌ Agent failures: 2A=$EXIT_2A, 2B=$EXIT_2B, 2C=$EXIT_2C"
    handle_failure
fi
```

2. **Timeout Exit Code Handling**:
```bash
timeout 600 codex exec --profile codex-prp --prompt "$prompt" > log.txt 2>&1
exit_code=$?

if [ $exit_code -eq 124 ]; then
    echo "❌ Agent timed out (>600s)"
elif [ $exit_code -eq 0 ]; then
    echo "✅ Agent succeeded"
else
    echo "❌ Agent failed (exit: $exit_code)"
fi
```

3. **JSONL Manifest Logging** (REUSE EXISTING):
```bash
# Source existing script
source scripts/codex/log-phase.sh

# Log phase start
log_phase_start "$feature_name" "phase2a"

# Execute phase
start_time=$(date +%s)
# ... run agent ...
end_time=$(date +%s)
duration=$((end_time - start_time))

# Log phase completion
log_phase_complete "$feature_name" "phase2a" "$exit_code" "$duration"
```

4. **Feature Name Validation** (COPY VERBATIM):
```bash
# Extract from .claude/commands/generate-prp.md lines 24-69
# Implement all 6 validation levels
# MUST use removeprefix() not replace()
# MUST reject prp_ prefix
```

**Validation Checklist**:
- [ ] Parallel timestamps within 5s (proof of parallelism)
- [ ] Speedup ≥2x vs sequential (target: 3x)
- [ ] All Phase 2 outputs created (3 files)
- [ ] Manifest JSONL valid (no corruption)
- [ ] Exit codes captured correctly (not lost)
- [ ] Timeout exit code 124 handled differently than general failure
- [ ] Feature name validation rejects all 6 attack vectors
- [ ] Profile `codex-prp` used in all `codex exec` calls

**Dependencies to Install**:
- GNU timeout (part of coreutils, pre-installed on most systems)
- jq (optional, for manifest parsing - has grep fallback)
- shellcheck (for validation, optional but recommended)

**No External Dependencies Needed For**:
- Bash job control (built-in, Bash 4.0+)
- Background processes & wait (POSIX standard)
- PID tracking with $! (built-in variable)
