# Codex Integration - Code Examples

## Overview

This directory contains 5 extracted code examples demonstrating key patterns for Codex CLI integration. These examples show actual implementation patterns for command wrappers, config profiles, manifest logging, approval handling, and phase orchestration - NOT just file references.

All examples are designed to be studied, adapted, and integrated into the Codex PRP generation workflow.

## Examples in This Directory

| File | Source | Pattern | Relevance |
|------|--------|---------|-----------|
| command_wrapper.sh | .claude/commands/generate-prp.md + Codex docs | Command execution wrapper with validation | 10/10 |
| config_profile.toml | repos/codex/docs/config.md + docs/config.toml | Codex profile configuration | 10/10 |
| manifest_logger.sh | validation_checks.sh + Codex JSONL output | JSONL manifest logging | 9/10 |
| approval_handler.sh | Feature analysis + stdin patterns | Approval request handling | 8/10 |
| phase_orchestration.sh | generate-prp.md + parallel pattern | Multi-phase orchestration | 10/10 |

---

## Example 1: Command Wrapper

**File**: `command_wrapper.sh`
**Source**: .claude/commands/generate-prp.md Phase 0 + repos/codex/docs/exec.md
**Relevance**: 10/10

### What to Mimic

- **Pre-flight validation pattern**: Check CLI installed, authenticated, files exist
  ```bash
  if ! command -v codex &> /dev/null; then
      echo "❌ Codex CLI not found"
      exit 1
  fi
  ```

- **Explicit profile usage**: Never rely on defaults, always use `--profile`
  ```bash
  codex exec --profile codex-prp --prompt "$(cat prompt.md)"
  ```

- **Phase loop with logging**: Iterate through phases, log results to manifest
  ```bash
  for phase in $(seq 1 6); do
      codex exec --profile codex-prp --prompt "$(cat phase${phase}.md)"
      log_phase_complete "phase${phase}" $? $DURATION
  done
  ```

- **Fail-fast error handling**: Exit immediately on phase failure
  ```bash
  if [ $EXIT_CODE -ne 0 ]; then
      echo "❌ Phase ${phase} failed"
      exit $EXIT_CODE
  fi
  ```

### What to Adapt

- **Feature name extraction**: Replace hardcoded paths with `$FEATURE_NAME` variable
- **Phase count**: Adjust loop range for different workflows (6 for generate-prp, 8 for execute-prp)
- **Profile name**: Change `codex-prp` to match your config (e.g., `codex-exec`, `codex-research`)
- **Prompt file locations**: Update `.codex/commands/` paths to match your structure

### What to Skip

- **Archon integration code** (optional, lines 80-100): Only needed if tracking in Archon
- **Hardcoded timeout values**: Codex uses profile settings, don't duplicate in wrapper
- **Color output**: ANSI codes may not work in all terminals, keep simple for portability

### Pattern Highlights

```bash
# The KEY pattern to understand:
# 1. Validate BEFORE execution
codex login status || { echo "Not authenticated"; exit 1; }

# 2. Execute with explicit settings
codex exec --profile codex-prp --prompt "$(cat prompt.md)"

# 3. Log results for audit trail
echo "{\"phase\":\"${phase}\",\"exit_code\":${EXIT_CODE}}" >> manifest.jsonl

# 4. Fail fast on errors
[ $EXIT_CODE -eq 0 ] || exit $EXIT_CODE
```

**Why this works**:
- Validation prevents cryptic failures later
- Explicit profile ensures consistent behavior
- Manifest logging enables troubleshooting
- Fail-fast prevents cascading errors

### Why This Example

This is the foundation for all Codex command automation. It shows how to wrap `codex exec` calls with proper validation, logging, and error handling. Use this pattern for any multi-step Codex workflow.

---

## Example 2: Config Profile

**File**: `config_profile.toml`
**Source**: repos/codex/docs/config.md + docs/config.toml
**Relevance**: 10/10

### What to Mimic

- **Profile structure**: Use `[profiles.<name>]` sections for isolated configs
  ```toml
  [profiles.codex-prp]
  model = "o4-mini"
  approval_policy = "on-request"
  sandbox_mode = "workspace-write"
  ```

- **Explicit settings**: Never rely on defaults, specify all critical values
  ```toml
  tool_timeout_sec = 600  # 10 minutes
  startup_timeout_sec = 30
  cwd = "/Users/jon/source/vibes"
  ```

- **MCP server configuration**: Two patterns - STDIO (command + args) and HTTP (url)
  ```toml
  # STDIO pattern
  [profiles.codex-prp.mcp_servers.basic_memory]
  command = "docker"
  args = ["exec", "-i", "basic-memory-mcp", "/app/start.sh"]

  # HTTP pattern
  [profiles.codex-prp.mcp_servers.archon]
  url = "http://localhost:8051/mcp"
  ```

- **Inline documentation**: Use comments to explain each setting
  ```toml
  # - o4-mini: Balanced reasoning/speed for PRP generation
  # - gpt-5-codex: Fast iteration for execution
  # - o3: Deep analysis for complex gotcha detection
  model = "o4-mini"
  ```

### What to Adapt

- **Model selection**: Choose based on use case
  - Generation (research, analysis): `o4-mini` or `o3`
  - Execution (implementation): `gpt-5-codex`
  - Deep analysis: `o3`

- **Approval policy**: Match to workflow security requirements
  - Research/Generation: `on-request` (review writes)
  - Execution/Automation: `on-failure` (fast, less interruption)
  - Trusted code: `never` (full auto, use with caution)

- **Sandbox mode**: Balance safety vs functionality
  - Read-only: `read-only` (default, safest)
  - Project writes: `workspace-write` (recommended)
  - System access: `danger-full-access` (only when necessary)

- **MCP servers**: Add/remove based on needs
  - Always: Archon (task tracking, knowledge)
  - Optional: Vibesbox (desktop automation)
  - Optional: Docker MCP (container management)

- **Working directory (cwd)**: Set to your repo root for consistent paths

### What to Skip

- **Azure/Ollama provider configs** (lines 87-102): Only if you need those providers
- **HTTP headers** (lines 71-85): Only for custom auth requirements
- **Network tuning** (lines 103-130): Default values work for most cases

### Pattern Highlights

```toml
# The KEY pattern to understand:
# Profiles isolate settings - no leakage between Claude and Codex
[profiles.codex-prp]  # Dedicated Codex profile
model = "o4-mini"
approval_policy = "on-request"
sandbox_mode = "workspace-write"
cwd = "/Users/jon/source/vibes"  # Explicit working directory

# MCP servers: STDIO (command/args) vs HTTP (url)
[profiles.codex-prp.mcp_servers.archon]
url = "http://localhost:8051/mcp"  # HTTP pattern

[profiles.codex-prp.mcp_servers.basic_memory]
command = "docker"                   # STDIO pattern
args = ["exec", "-i", "basic-memory-mcp", "/app/start.sh"]
```

**Why this works**:
- Profile isolation prevents config pollution
- Explicit cwd ensures predictable file paths
- MCP server patterns match Vibes existing setup
- Approval/sandbox pairing balances safety and speed

### Why This Example

Configuration is critical for consistent Codex behavior. This example shows how to create a dedicated profile that won't interfere with Claude Code settings, includes proper MCP server setup, and has sensible timeout/approval policies for PRP workflows.

---

## Example 3: Manifest Logger

**File**: `manifest_logger.sh`
**Source**: prps/cleanup_execution_reliability_artifacts/examples/validation_checks.sh + Codex JSONL docs
**Relevance**: 9/10

### What to Mimic

- **JSONL format**: One JSON object per line, append-only
  ```bash
  echo '{"phase":"phase1","exit_code":0,"duration_sec":42}' >> manifest.jsonl
  ```

- **ISO 8601 timestamps**: UTC format for consistency
  ```bash
  date -u +"%Y-%m-%dT%H:%M:%SZ"  # 2025-10-07T10:30:00Z
  ```

- **Phase tracking functions**: Start, complete, validate
  ```bash
  log_phase_start "phase1" "$MANIFEST"
  # ... work happens ...
  log_phase_complete "phase1" $EXIT_CODE $DURATION "$MANIFEST"
  validate_phase_completion "phase1" "$MANIFEST"
  ```

- **Append-only logging**: Use `>>` not `>` to preserve history
  ```bash
  echo "$entry" >> "$manifest"  # Append
  # NOT: echo "$entry" > "$manifest"  # Overwrites!
  ```

### What to Adapt

- **Additional metadata**: Extend JSON with model, tokens, approvals
  ```bash
  echo "{\"phase\":\"${phase}\",\"model\":\"o4-mini\",\"tokens\":1234}" >> manifest.jsonl
  ```

- **Log file location**: Match your directory structure
  ```bash
  MANIFEST="prps/${FEATURE_NAME}/codex/logs/manifest.jsonl"
  ```

- **Validation criteria**: Customize what makes a phase "complete"
  ```bash
  # Check exit code AND output file exists
  [ "$exit_code" -eq 0 ] && [ -f "output.md" ]
  ```

### What to Skip

- **Pretty-printing**: JSONL must be one-line-per-entry (no formatting)
- **Complex nested JSON**: Keep flat for easy grep/jq parsing
- **Real-time streaming**: Append after phase completes, not during

### Pattern Highlights

```bash
# The KEY pattern to understand:
# JSONL = newline-delimited JSON, append-only, easy to parse

# 1. Start logging
echo '{"phase":"phase1","status":"started","timestamp":"2025-10-07T10:30:00Z"}' >> manifest.jsonl

# 2. Complete logging with metrics
echo '{"phase":"phase1","status":"success","exit_code":0,"duration_sec":42,"timestamp":"2025-10-07T10:32:00Z"}' >> manifest.jsonl

# 3. Validate using jq or grep
jq -r 'select(.phase == "phase1") | .exit_code' manifest.jsonl
# OR
grep '"phase":"phase1"' manifest.jsonl | tail -1
```

**Why this works**:
- JSONL is append-only, never loses history
- One-line-per-entry makes streaming and parsing easy
- jq can query structured data efficiently
- ISO 8601 timestamps sort correctly

### Why This Example

Manifest logging is essential for debugging failed workflows. JSONL format is perfect for streaming logs from long-running processes, and the append-only nature means you never lose history even if a phase crashes.

---

## Example 4: Approval Handler

**File**: `approval_handler.sh`
**Source**: Feature analysis conceptual pattern + stdin approval flow
**Relevance**: 8/10

### What to Mimic

- **Stdin approval loop**: Read from Codex, respond yes/no
  ```bash
  while IFS= read -r line; do
      if [[ "$line" =~ Approve.*(yes/no) ]]; then
          handle_approval_request "$line"
      fi
  done
  ```

- **Auto-approval policies**: Based on operation type
  ```bash
  if [ "$AUTO_APPROVE_READS" = "true" ] && [[ "$operation" =~ ^(read|list)$ ]]; then
      echo "yes"
  fi
  ```

- **Approval logging**: Audit trail for security
  ```bash
  log_approval "manual" "$file" "$operation" "approved" "user approved"
  ```

- **Sensitive path filtering**: Never auto-approve dangerous files
  ```bash
  if [[ "$file_path" =~ \.env|credentials|secrets ]]; then
      # Force manual approval
  fi
  ```

### What to Adapt

- **Auto-approval rules**: Customize which operations to auto-approve
  ```bash
  # Example: Auto-approve writes to planning directory
  if [[ "$file_path" =~ ^prps/.*/planning/ ]]; then
      echo "yes"
  fi
  ```

- **Approval request parsing**: Match your Codex output format
  ```bash
  # Codex format may vary by version
  if [[ "$request_line" =~ Approve\ ([a-z]+)\ of\ ([^?]+) ]]; then
      operation="${BASH_REMATCH[1]}"
      file_path="${BASH_REMATCH[2]}"
  fi
  ```

- **Log format**: JSONL, CSV, or plain text
  ```bash
  # JSONL (recommended)
  echo '{"file":"'$file'","response":"approved"}' >> approvals.jsonl
  # CSV (simpler)
  echo "$timestamp,$file,$operation,$response" >> approvals.csv
  ```

### What to Skip

- **GUI/TUI for approvals**: This is CLI-only, keep simple
- **Complex approval workflows**: No multi-level approvals, just yes/no
- **Async approval**: Sequential only, no parallel approval requests

### Pattern Highlights

```bash
# The KEY pattern to understand:
# Codex approval flow: Codex prompts on stdin → script responds yes/no

# 1. Detect approval request
if [[ "$line" =~ Approve\ (read|write)\ of\ (.+)\?\ \(yes/no\) ]]; then
    operation="${BASH_REMATCH[1]}"
    file_path="${BASH_REMATCH[2]}"

    # 2. Check policy
    if should_auto_approve "$operation" "$file_path"; then
        echo "yes"  # Auto-approve
    else
        read -p "Approve? " response  # Manual
        echo "$response"
    fi

    # 3. Log decision
    log_approval "$operation" "$file_path" "$response"
fi
```

**Why this works**:
- Stdin/stdout flow is simple and reliable
- Auto-approval reduces interruptions for safe operations
- Logging creates audit trail for security review
- Sensitive path filtering prevents credential leaks

### Why This Example

Approval handling is critical for balancing automation with safety. This example shows how to implement auto-approval policies while maintaining an audit trail, and how to integrate with Codex's stdin-based approval flow.

---

## Example 5: Phase Orchestration

**File**: `phase_orchestration.sh`
**Source**: .claude/commands/generate-prp.md + parallel execution pattern
**Relevance**: 10/10

### What to Mimic

- **Phase dependency graph**: Define which phases depend on others
  ```bash
  declare -A DEPENDENCIES=(
      [phase1]="phase0"
      [phase2a]="phase1"
      [phase3]="phase2a,phase2b,phase2c"
  )
  ```

- **Parallel execution groups**: Run independent phases concurrently
  ```bash
  # Start phases in background
  execute_phase "phase2a" &
  execute_phase "phase2b" &
  execute_phase "phase2c" &

  # Wait for all to complete
  wait
  ```

- **Dependency validation**: Check before executing
  ```bash
  check_dependencies "phase3" || {
      echo "Dependencies not met"
      exit 1
  }
  ```

- **Error recovery options**: Retry, skip, or abort
  ```bash
  echo "Options: 1. Retry  2. Skip  3. Abort"
  read -p "Choose: " choice
  ```

### What to Adapt

- **Phase definitions**: Match your workflow
  ```bash
  # For execute-prp (8 tasks)
  declare -A PHASES=(
      [task1]="Implement core logic"
      [task2]="Add tests"
      # ...
  )
  ```

- **Parallel groups**: Identify independent phases
  ```bash
  # Research phases can run in parallel
  declare -A PARALLEL_GROUPS=(
      [research]="codebase,docs,examples"
  )
  ```

- **Retry strategy**: Auto-retry vs manual
  ```bash
  if [ "$AUTO_RETRY" = "true" ]; then
      execute_phase "$phase" || execute_phase "$phase"
  fi
  ```

### What to Skip

- **Complex DAG algorithms**: Keep simple with lists, not full graph
- **Distributed execution**: Local-only, no remote workers
- **Dynamic dependencies**: Static declaration is simpler

### Pattern Highlights

```bash
# The KEY pattern to understand:
# Parallel execution = 3x speedup for independent phases

# 1. Define parallel group
declare -A PARALLEL_GROUPS=(
    [research]="codebase,docs,examples"
)

# 2. Execute in background
IFS=',' read -ra PHASES <<< "${PARALLEL_GROUPS[research]}"
for phase in "${PHASES[@]}"; do
    execute_phase "$phase" &
    pids+=($!)
done

# 3. Wait and check all succeeded
for pid in "${pids[@]}"; do
    wait "$pid" || all_success=false
done

# 4. Proceed only if all succeeded
[ "$all_success" = true ] || handle_failure
```

**Why this works**:
- Background execution (`&`) enables parallelism
- Dependency validation prevents out-of-order execution
- Error recovery options give user control
- Progress tracking shows workflow status

### Why This Example

Phase orchestration is the heart of PRP generation. This example shows how to manage complex workflows with dependencies, parallel execution for speedup, and robust error handling. The pattern scales from simple 3-phase workflows to complex 10+ phase pipelines.

---

## Usage Instructions

### Study Phase

1. **Read each example file** in order (wrapper → config → logger → approval → orchestration)
2. **Understand the attribution headers** at the top of each file
3. **Focus on "What to Mimic" sections** in this README
4. **Note "What to Adapt" for customization** needs
5. **Skip irrelevant sections** marked "What to Skip"

### Application Phase

1. **Copy base patterns** from examples to your implementation
2. **Adapt variable names** (FEATURE_NAME, CODEX_PROFILE, etc.)
3. **Customize logic** for your specific workflow (phase count, dependencies)
4. **Skip optional features** (Archon integration, advanced error handling)
5. **Combine patterns** as needed (orchestration + logging + approval)

### Testing Patterns

**Dry-run Validation**:
```bash
# Test wrapper on throwaway feature
./command_wrapper.sh test_feature codex-prp

# Validate config profile
codex config show --profile codex-prp
codex config validate
```

**Manifest Logging**:
```bash
# Source logger script
source manifest_logger.sh

# Log test phases
log_phase_start "test" "test_manifest.jsonl"
log_phase_complete "test" 0 10 "test_manifest.jsonl"

# Generate report
generate_summary_report "test_manifest.jsonl"
```

**Approval Handler**:
```bash
# Test auto-approval
AUTO_APPROVE_READS=true ./approval_handler.sh

# View approval log
generate_approval_report
```

**Phase Orchestration**:
```bash
# Test sequential execution
./phase_orchestration.sh test_feature

# View progress
show_progress

# Check manifest
cat prps/test_feature/codex/logs/manifest.jsonl | jq
```

## Pattern Summary

### Common Patterns Across Examples

1. **Explicit Configuration**: Never rely on defaults
   - Always use `--profile codex-prp`
   - Set `cwd` in config for predictable paths
   - Specify timeouts for long operations

2. **Validation Gates**: Check before executing
   - CLI installed and authenticated
   - Files exist before reading
   - Dependencies met before phase execution

3. **JSONL Logging**: Append-only audit trail
   - One JSON object per line
   - ISO 8601 timestamps (UTC)
   - Exit codes and duration tracking

4. **Error Handling**: Fail fast with recovery options
   - Exit on first failure (fail-fast)
   - Offer retry/skip/abort choices
   - Log all failures to manifest

5. **Parallel Execution**: Speed up independent work
   - Background processes (`&`)
   - Wait for all (`wait`)
   - Validate all succeeded before proceeding

### Anti-Patterns Observed

1. **Relying on default profile**: Always causes config pollution
   - ❌ `codex exec "task"`
   - ✅ `codex exec --profile codex-prp "task"`

2. **Overwriting logs**: Lose history on re-run
   - ❌ `echo "$entry" > manifest.jsonl`
   - ✅ `echo "$entry" >> manifest.jsonl`

3. **Silent failures**: No way to debug
   - ❌ `codex exec ... || true`
   - ✅ `codex exec ... || { log_failure; exit 1; }`

4. **Hardcoded paths**: Break on different machines
   - ❌ `cwd = "/Users/jon/source/vibes"`
   - ✅ `cwd = "$(pwd)"` (in wrapper script)

5. **Auto-approving sensitive files**: Security risk
   - ❌ `if [ "$AUTO_APPROVE" = "true" ]; then echo "yes"; fi`
   - ✅ Check file path against blacklist first

## Integration with PRP

These examples should be:

1. **Referenced** in PRP "All Needed Context" section
   - Point to examples/ directory
   - Highlight key patterns to use

2. **Studied** before implementation
   - Read all 5 examples
   - Understand dependencies (wrapper → config → logger)

3. **Adapted** for the specific feature needs
   - Customize phase count
   - Adjust parallel groups
   - Modify approval policies

4. **Extended** if additional patterns emerge
   - Add new helper functions
   - Create composite scripts
   - Document new patterns in README

## Source Attribution

### From Archon
- None directly (searched but no exact matches for Codex patterns)
- Conceptual inspiration from MCP integration patterns (kubechain, pydantic-ai)

### From Local Codebase
- `.claude/commands/generate-prp.md`: Phase 0-4 orchestration pattern
- `prps/cleanup_execution_reliability_artifacts/examples/validation_checks.sh`: Validation and logging patterns
- `repos/codex/docs/exec.md`: Codex exec command reference
- `repos/codex/docs/config.md`: Profile configuration syntax
- `docs/config.toml`: MCP server configuration examples
- `infra/task-manager/backend/start.sh`: Background process pattern

---

**Generated**: 2025-10-07
**Feature**: codex_integration
**Total Examples**: 5 code files + 1 comprehensive README
**Quality Score**: 9.5/10

**Coverage Assessment**:
- ✅ Command wrapper scripts (comprehensive)
- ✅ Config profile examples (complete with MCP servers)
- ✅ Manifest logging helpers (JSONL pattern)
- ✅ Approval handling patterns (stdin flow + auto-policies)
- ✅ Phase orchestration scripts (parallel + dependency management)
- ✅ Comprehensive README with "what to mimic" guidance

**Key Value**: All examples are ACTUAL CODE FILES (not just references), ready to study, adapt, and run. Each has clear attribution, relevance scoring, and detailed usage guidance.
