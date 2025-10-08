# INITIAL: Codex Integration & Command Suite

## FEATURE

Integrate OpenAI Codex CLI as a parallel execution engine for PRP-driven development, enabling dual-agent workflows while maintaining clean separation between Codex and Claude pipelines.

**Why we care:**
- **Reusability**: Codex CLI provides complete MCP client/server stack – leverage it for heavy coding tasks without reinventing infrastructure
- **Dual-agent execution**: Run same PRP through both Claude and Codex for cross-validation and quality comparison
- **MCP delegation**: `codex mcp-server` exposes JSON-RPC API enabling programmatic task handoff, including Codex-to-Codex workflows
- **Approval model parity**: Codex sandbox/approval system matches Vibes' philosophy, enabling safe automation
- **Model flexibility**: Access to `gpt-5-codex`, `o4-mini`, `o3` for different reasoning/speed tradeoffs

**What "done" looks like:**
- Codex CLI installed and authenticated (npm, brew, or binary)
- Dedicated Codex profile in config isolating model, sandbox, approval, and MCP servers from Claude
- Codex-native commands (`codex-generate-prp`, `codex-execute-prp`) mirroring Vibes' five-phase workflow
- All Codex artifacts organized under `prps/{feature}/codex/` with clear separation from Claude outputs
- Documentation guiding when to use Codex vs Claude, how to compare results, and approval handling
- Validation strategy for Codex runs (logs, approval capture, failure recovery)

**Scope guardrails:**
- CLI-first integration (no VS Code extension work)
- Use Codex CLI + MCP interfaces; defer deep Rust modifications
- Keep Codex commands outside `.claude/commands/` (use `.codex/commands/` or `codex/prompts/`)
- Focus on planning and bootstrapping; implementation commands are separate deliverables

---

## CURRENT STATE CHECKLIST

**Repository & Setup:**
- [x] `repos/codex` cloned from https://github.com/openai/codex
- [ ] Document install paths: npm (`@openai/codex`), brew (`codex`), or release binaries
- [ ] Auth prerequisites and fallback instructions (ChatGPT login, API key)
- [ ] Environment requirements (Node.js version, OS compatibility, sandbox capabilities)

**Configuration:**
- [ ] Draft reference `config.toml` profile for Codex (`~/.codex/config.toml` or repo-local)
- [ ] Approval policy selection (`on-request` vs `on-failure` vs `never`)
- [ ] Sandbox mode defaults (`workspace-write` with network toggle)
- [ ] Model selection strategy (`gpt-5-codex` vs `o4-mini` vs `o3`)
- [ ] MCP server list for Codex runs (reuse Vibes servers or Codex-specific subset?)

**Architecture:**
- [ ] Clarify Codex CLI vs `codex mcp-server` interaction (when to use each)
- [ ] Define artifact handoff protocol (inputs/outputs between Claude and Codex)
- [ ] Approval escalation strategy (auto-approve workspace writes? escalate network requests?)
- [ ] Archon integration: separate projects for Codex runs or shared task IDs?

**Commands:**
- [ ] Command location decision (`.codex/commands/` vs `codex/prompts/` vs other)
- [ ] `codex-generate-prp` spec (phases, inputs, outputs, approval gates)
- [ ] `codex-execute-prp` spec (implementation, validation, report format)
- [ ] Logging and manifest format (`manifest.jsonl` per phase)

---

## DELIVERABLES

### 1. Bootstrap Documentation
**File:** `docs/codex-bootstrap.md`

**Contents:**
- Install routes (npm global, brew, binary download with version pinning)
- Auth setup (ChatGPT login, API key configuration, credential storage)
- Profile scaffolding (reference `config.toml` with inline comments)
- Verification steps (`codex login status`, `codex --version`, sandbox test)
- Troubleshooting common issues (auth failures, sandbox denials, timeout handling)

### 2. Configuration Reference
**File:** `docs/codex-config.md`

**Contents:**
- Profile structure (`[profiles.codex-prp]` with all settings explained)
- Config precedence rules (CLI flags > profile > root config > defaults)
- Approval policies:
  - `untrusted` → prompt for all operations
  - `on-request` → prompt before any tool use (recommended for PRP generation)
  - `on-failure` → auto-approve, prompt only on errors
  - `never` → full automation (use with caution)
- Sandbox modes:
  - `read-only` → no writes allowed
  - `workspace-write` → writes limited to workspace roots (default for PRP execution)
  - `danger-full-access` → unrestricted (avoid)
- MCP server configuration (`[mcp_servers.<id>]` entries, environment variables)
- Timeout tuning (`startup_timeout_sec`, `tool_timeout_sec` – recommend 600s for long runs)

### 3. MCP Server Strategy
**File:** `docs/codex-mcp-delegation.md`

**Contents:**
- How `codex mcp-server` exposes JSON-RPC API (methods: `newConversation`, `sendUserMessage`, approval handlers)
- Delegation patterns:
  - **Pattern A:** Parent agent (Claude or orchestrator) spawns `codex mcp-server`, sends tasks via MCP
  - **Pattern B:** Codex instance delegates subtasks to another `codex mcp-server` process
  - **Pattern C:** Parallel Codex runs (multiple features simultaneously)
- Approval request handling (`applyPatchApproval`, `execCommandApproval`) – capture, relay, or auto-approve based on policy
- Security considerations (stdin for sensitive commands, approval logs)
- No implementation yet – planning artifact only

### 4. Artifact Directory Structure
**File:** `docs/codex-artifacts.md`

**Contents:**
```
prps/{feature}/codex/
├── logs/
│   ├── phase0-setup.md
│   ├── phase1-analysis.md
│   ├── phase2-research.md
│   ├── phase3-gotchas.md
│   ├── phase4-assembly.md
│   ├── phase5-execution.md
│   └── manifest.jsonl         # Phase completion tracking
├── planning/
│   ├── feature-analysis.md
│   ├── codebase-patterns.md
│   ├── documentation-links.md
│   └── gotchas.md
├── examples/
│   └── README.md               # Example summaries + adaptations
├── execution/
│   ├── execution-plan.md
│   ├── completion-report.md
│   └── validation-results.md
└── prp_codex.md                # Final assembled PRP
```

**Naming conventions:**
- All Codex artifacts under `codex/` subdirectory
- Logs include ISO timestamps in manifest
- Examples cite original file paths
- Reports include quality scores and justifications

### 5. Command Specifications
**Files:** `.codex/commands/codex-generate-prp.md`, `.codex/commands/codex-execute-prp.md`

#### `codex-generate-prp` Spec
**Purpose:** Research and assemble PRP using Codex

**Inputs:**
- `{prp_path}` – path to INITIAL PRP (e.g., `prps/INITIAL_{feature}.md`)
- `{feature_name}` – feature identifier (extracted from PRP path)

**Phases:**
1. **Setup & Validation** → verify auth, sandbox, directories; log to `logs/phase0-setup.md`
2. **Feature Analysis** → extract goals, risks, Codex-specific constraints; write `planning/feature-analysis.md`
3. **Codebase Research** → search for patterns using ripgrep/fd; write `planning/codebase-patterns.md`
4. **Documentation Links** → aggregate official docs (prefer `repos/codex/docs/`); write `planning/documentation-links.md`
5. **Example Extraction** → copy relevant snippets to `examples/` with README
6. **Gotcha Detection** → synthesize failure modes; write `planning/gotchas.md`
7. **PRP Assembly** → combine all research into `prp_codex.md` using `prps/templates/prp_base.md`

**Outputs:**
- `prps/{feature}/codex/prp_codex.md` (quality score ≥8/10)
- All planning artifacts in structured directories
- `logs/manifest.jsonl` tracking phase completion

**Approval gates:**
- Phase 2-3: auto-approve file reads (sandbox read-only acceptable)
- Phase 5-6: prompt before creating examples (workspace-write)
- Phase 7: prompt before final PRP write

#### `codex-execute-prp` Spec
**Purpose:** Implement feature from Codex-generated PRP

**Inputs:**
- `{prp_path}` – path to `prps/{feature}/codex/prp_codex.md`
- `{feature_name}` – feature identifier

**Phases:**
1. **Task Analysis** → extract dependencies, create parallel execution groups; write `execution/execution-plan.md`
2. **Implementation** → execute tasks per plan, capture outputs
3. **Validation Loop:**
   - Run linters (ruff, mypy, shellcheck as applicable)
   - Run tests (pytest with coverage ≥70%)
   - Capture failures, iterate fixes
4. **Completion Report** → write `execution/completion-report.md` with metrics, quality score, blockers

**Outputs:**
- Feature code (location varies per PRP)
- Tests achieving ≥70% coverage
- `execution/completion-report.md`
- `logs/manifest.jsonl` updated

**Approval gates:**
- Phase 2: prompt for each file write (workspace-write)
- Phase 3: auto-approve test runs, prompt for fixes
- Retry limit: 3 attempts per validation gate

### 6. Validation Plan
**File:** `docs/codex-validation.md`

**Contents:**
- **Pre-flight checks:** auth status, sandbox verification, config validation
- **Phase logging:** append to `manifest.jsonl` after each `codex exec`:
  ```json
  {"phase": "phase1", "command": "codex exec ...", "exit_code": 0, "duration_sec": 42, "timestamp": "2025-10-07T10:30:00Z"}
  ```
- **Approval capture:** log all approval prompts and responses for audit trail
- **Failure handling:**
  - Exit code ≠ 0 → capture stderr to `logs/phase{N}-error.log`
  - Timeout → extend `tool_timeout_sec` or split into smaller phases
  - Auth failure → guide user through re-authentication
  - Sandbox denial → escalate to user with override instructions
- **Quality gates:**
  - PRP assembly: must score ≥8/10 or regenerate
  - Code validation: ruff + mypy clean, pytest ≥70% coverage
  - Report completeness: all phases logged, no missing artifacts
- **Fallback:** if Codex unavailable (auth issue, binary missing), document graceful degradation to Claude-only workflow

---

## REFERENCE PATTERNS

**From `repos/codex/docs/`:**
- `config.md` → configuration precedence, profiles, sandbox/approval, MCP server wiring
- `codex-rs/docs/codex_mcp_interface.md` → JSON-RPC API for `codex mcp-server` (delegation patterns)
- `advanced.md` → quickstart for `codex mcp-server` with MCP Inspector

**From Vibes codebase:**
- `.claude/commands/generate-prp.md` → comparison point for phase structure (do NOT modify)
- `.claude/commands/execute-prp.md` → validation loop patterns, quality gates
- `prps/templates/prp_base.md` → template for PRP assembly

**MCP specs:**
- Model Context Protocol documentation for server integration
- Approval request/response flows

---

## GOTCHAS & MITIGATIONS

| Issue | Impact | Detection | Resolution | Confidence |
|-------|--------|-----------|------------|------------|
| **Auth failure** | Blocks all Codex runs | `codex login status` exit ≠ 0 | Guide user through ChatGPT login or API key setup | HIGH |
| **Sandbox denial** | Writes to critical paths fail | Permission errors in stderr | Adjust `workspace-write` roots or escalate to `danger-full-access` with warning | HIGH |
| **Timeout on long runs** | Phase incomplete, partial artifacts | Exit code timeout (124) | Increase `tool_timeout_sec` to 600s or split phase | MEDIUM |
| **Binary availability** | `codex` command not found | Shell `which codex` fails | Install via npm/brew or use `npx @openai/codex` with path override | HIGH |
| **Artifact path pollution** | Outputs in wrong directory | Files outside `prps/{feature}/codex/` | Enforce `cwd` in profile + validation script checking paths | MEDIUM |
| **Profile drift** | Claude settings leak to Codex | Unexpected model or MCP servers | Use `--profile codex-prp` explicitly, never rely on defaults | HIGH |
| **Approval escalation** | Human not available for prompt | Codex blocks waiting for stdin | Use `approval_policy = "on-failure"` for automation, `on-request` for manual runs | MEDIUM |
| **MCP delegation loop** | Codex delegates to itself infinitely | Hung process, resource exhaustion | Implement delegation depth limit (max 2 levels), timeout circuit breaker | LOW |
| **Model unavailable** | API returns 503/quota error | Stderr "model not available" | Fallback to `o4-mini` or defer to Claude with note in manifest | MEDIUM |

---

## OPEN QUESTIONS

**Prioritized for resolution before implementation:**

1. **Command location:** Where should Codex commands live?
   - **Option A:** `.codex/commands/` (mirrors `.claude/commands/`)
   - **Option B:** `codex/prompts/` (emphasizes prompt-first design)
   - **Option C:** `scripts/codex/` (executable wrappers around `codex exec`)
   - **Decision criteria:** ease of discovery, IDE integration, automation tooling

2. **Execution mode:** Direct CLI vs MCP server orchestration?
   - **CLI (`codex exec`):** Simpler, stateless, easier debugging
   - **MCP server:** Richer streaming, approval control, enables delegation
   - **Recommendation:** Start with `codex exec` for MVP, migrate to MCP server for advanced delegation

3. **Approval strategy:** How to handle Codex approval prompts?
   - **Auto-approve workspace writes:** Fast, matches Vibes philosophy
   - **Escalate to user:** Safer, slower, breaks automation
   - **Hybrid:** Auto-approve reads/tests, escalate writes/network
   - **Recommendation:** Start with `on-request` for generation, `on-failure` for execution

4. **Archon integration:** Separate or shared project tracking?
   - **Separate projects:** Clean isolation, easier comparison
   - **Shared task IDs:** Unified view, cross-agent coordination
   - **Recommendation:** Separate projects with naming convention `{feature}_codex` vs `{feature}_claude`

5. **Model defaults:** Which model for which phase?
   - `gpt-5-codex` → fast iteration, lower cost
   - `o4-mini` → balanced reasoning and speed
   - `o3` → deep analysis, slower but more accurate
   - **Recommendation:** `o4-mini` for generation, `gpt-5-codex` for execution

6. **Cross-validation workflow:** How to compare Claude vs Codex PRPs?
   - Run both, diff outputs, score quality independently
   - Use Claude to review Codex PRP (or vice versa)
   - Manual review with scoring rubric
   - **Deferred:** Needs separate PRP for comparison pipeline

---

## IMPLEMENTATION PHASES

### Phase 1: Bootstrap (THIS PRP)
**Deliverables:** Documentation + configuration setup
- [x] Codex repo cloned
- [ ] Install documentation (`docs/codex-bootstrap.md`)
- [ ] Config reference (`docs/codex-config.md`)
- [ ] Artifact structure (`docs/codex-artifacts.md`)
- [ ] Validation plan (`docs/codex-validation.md`)

**Validation:**
- `codex --version` succeeds
- Auth configured (`codex login status`)
- Profile created (`~/.codex/config.toml` with `[profiles.codex-prp]`)
- Test run: `codex exec --profile codex-prp --prompt "echo hello"` succeeds

### Phase 2: Command Specs (FOLLOW-UP PRP)
**Deliverables:** Command prompt design
- [ ] `.codex/commands/codex-generate-prp.md` (full prompt text)
- [ ] `.codex/commands/codex-execute-prp.md` (full prompt text)
- [ ] Logging helpers (`scripts/codex/log-phase.sh`)
- [ ] Approval handlers (`scripts/codex/handle-approval.sh`)

**Validation:**
- Dry-run both commands on throwaway feature
- Verify artifact structure matches spec
- Confirm approval prompts appear at expected gates

### Phase 3: End-to-End Validation (FOLLOW-UP PRP)
**Deliverables:** Proven workflow
- [ ] Run `codex-generate-prp` on sample INITIAL (e.g., `INITIAL_codex_integration.md`)
- [ ] Run `codex-execute-prp` on generated PRP
- [ ] Compare Codex vs Claude outputs (quality, coverage, time)
- [ ] Document lessons learned (`docs/codex-lessons.md`)

**Validation:**
- PRP quality ≥8/10
- Code passes validation gates (ruff, mypy, pytest ≥70%)
- Completion report includes all required sections
- Manifest logs all phases

### Phase 4: MCP Delegation (FUTURE)
**Deliverables:** Advanced orchestration
- [ ] Launch `codex mcp-server` programmatically
- [ ] Delegate subtasks via JSON-RPC API
- [ ] Handle approval requests in parent agent
- [ ] Implement Codex-to-Codex handoffs

**Deferred until Phases 1-3 proven.**

---

## PROTOTYPE COMMANDS

### Recommended Profile (`~/.codex/config.toml`)
```toml
[profiles.codex-prp]
model = "o4-mini"                    # Balanced reasoning/speed
approval_policy = "on-request"       # Prompt before tool use
sandbox_mode = "workspace-write"     # Restrict writes to workspace
startup_timeout_sec = 30
tool_timeout_sec = 600               # 10 minutes for long phases
cwd = "/Users/jon/source/vibes"      # Adjust to repo root

# MCP servers (reuse Vibes servers or subset)
[profiles.codex-prp.mcp_servers.archon]
command = "uvx"
args = ["archon"]
env = { ARCHON_ENV = "production" }

[profiles.codex-prp.mcp_servers.memory]
command = "uvx"
args = ["basic-memory"]
```

### Phase 0: Setup & Validation
```bash
codex exec --profile codex-prp --prompt "$(cat <<'PROMPT'
Goal: Prepare Codex workspace for PRP execution.
- Input PRP: prps/INITIAL_codex_integration.md
- Feature name: codex_integration

Tasks:
1. Verify auth: run `codex login status`, capture output
2. Confirm sandbox mode + approval policy from profile
3. Create directories: prps/codex_integration/codex/{logs,planning,examples,execution}
4. Write setup summary to prps/codex_integration/codex/logs/phase0-setup.md with:
   - Auth status
   - Sandbox mode
   - Approval policy
   - Detected constraints (network disabled?, writable roots)
   - Timestamp

Exit with code 0 if ready, 1 if auth or sandbox issues detected.
PROMPT
)"
```

### Phase 1: Feature Analysis
```bash
codex exec --profile codex-prp --prompt "$(cat <<'PROMPT'
Read prps/INITIAL_codex_integration.md.

Produce prps/codex_integration/codex/planning/feature-analysis.md with:

# Feature Analysis

## Goals & Success Criteria
[Extract from INITIAL PRP "What done looks like"]

## Existing Assets
[Search codebase for reusable patterns, list file paths + relevance]

## Risks & Unknowns
| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
[Include at least: auth failure, sandbox denial, timeout]

## Codex-Specific Considerations
- Approval gates: [list phases requiring prompts]
- Sandbox constraints: [network access, writable paths]
- Model selection: [recommend model per phase with justification]

## Quality Score
[Rate 1-10 with justification]
PROMPT
)"
```

### Phase 2A: Codebase Research
```bash
codex exec --profile codex-prp --prompt "$(cat <<'PROMPT'
Search repository for patterns relevant to Codex integration.

Use tools:
- `rg "codex" --type md` → find existing Codex mentions
- `fd config.toml` → locate config examples
- `rg "approval_policy|sandbox_mode"` → find sandbox patterns
- Search `.claude/commands/` for PRP generation patterns (DO NOT MODIFY)

Write prps/codex_integration/codex/planning/codebase-patterns.md:

# Codebase Patterns

## Pattern 1: [Name]
**File:** [path:line]
**Snippet:**
```[lang]
[≤30 lines]
```
**Relevance:** [why useful for Codex integration]
**Adaptation:** [how to reuse for this feature]

[Repeat for 3-5 patterns]
PROMPT
)"
```

### Phase 2B: Documentation Links
```bash
codex exec --profile codex-prp --prompt "$(cat <<'PROMPT'
Aggregate official documentation for Codex integration.

Prioritize:
1. repos/codex/docs/ (config.md, codex_mcp_interface.md, advanced.md)
2. MCP specifications
3. OpenAI Codex API docs (if applicable)

Write prps/codex_integration/codex/planning/documentation-links.md:

# Documentation Links

| Source | URL | Topic | Relevance | Key Sections |
|--------|-----|-------|-----------|--------------|
[Add 5-10 entries with inline notes]

## Missing Documentation
[List gaps requiring web search or experimentation]
PROMPT
)"
```

### Phase 2C: Example Extraction
```bash
codex exec --profile codex-prp --prompt "$(cat <<'PROMPT'
Identify concrete examples to emulate for Codex integration.

Search for:
- Existing command wrappers (`.claude/commands/`)
- Config profiles (if any `config.toml` examples exist)
- MCP server integration patterns
- Approval handling scripts

Copy minimal snippets to prps/codex_integration/codex/examples/ with structure:
examples/
├── command-wrapper.sh
├── config-profile.toml
├── mcp-delegation.py
└── README.md

README.md includes:
- Example purpose
- Original file path citation
- Key APIs/patterns
- Adaptation instructions for Codex integration

Ensure snippets are ≤50 lines each, cite sources.
PROMPT
)"
```

### Phase 3: Gotcha Detection
```bash
codex exec --profile codex-prp --prompt "$(cat <<'PROMPT'
Synthesize failure modes from analysis + research.

Produce prps/codex_integration/codex/planning/gotchas.md:

# Gotchas

| Issue | Impact | Detection | Resolution | Confidence |
|-------|--------|-----------|------------|------------|
[Include ALL from "GOTCHAS & MITIGATIONS" section of INITIAL PRP]
[Add any new gotchas discovered during research]

## Critical Blockers
[List issues that would prevent Codex integration entirely]

## Workarounds
[Document fallback strategies if Codex unavailable]
PROMPT
)"
```

### Phase 4: PRP Assembly
```bash
codex exec --profile codex-prp --prompt "$(cat <<'PROMPT'
Assemble comprehensive PRP using template prps/templates/prp_base.md.

Inputs:
- prps/codex_integration/codex/planning/feature-analysis.md
- prps/codex_integration/codex/planning/codebase-patterns.md
- prps/codex_integration/codex/planning/documentation-links.md
- prps/codex_integration/codex/planning/gotchas.md
- prps/codex_integration/codex/examples/README.md

Output: prps/codex_integration/codex/prp_codex.md

Structure (follow prp_base.md):
1. FEATURE (goals, scope, success criteria)
2. CURRENT STATE (checklist from research)
3. DELIVERABLES (concrete artifacts)
4. IMPLEMENTATION STEPS (task breakdown with dependencies)
5. VALIDATION GATES (linting, tests, coverage thresholds)
6. GOTCHAS (from planning/gotchas.md)
7. REFERENCES (from planning/documentation-links.md + codebase-patterns.md)

Quality requirements:
- All sections complete (no [TODO] placeholders)
- Code examples cited with file:line references
- Validation gates measurable (exit codes, coverage %)
- Gotchas include detection + resolution
- Score ≥8/10

At end of PRP, include:
## Quality Self-Assessment
**Score:** [1-10]
**Justification:** [why this score, what's missing for 10/10]
**Confidence:** [HIGH/MEDIUM/LOW that implementer can execute without clarification]
PROMPT
)"
```

### Logging Hook (run after each phase)
```bash
#!/bin/bash
# scripts/codex/log-phase.sh
PHASE=$1
EXIT_CODE=$2
FEATURE=$3

jq -nc \
  --arg phase "$PHASE" \
  --arg cmd "$CODEX_LAST_CMD" \
  --argjson exit "$EXIT_CODE" \
  --arg ts "$(date -u +%Y-%m-%dT%H:%M:%SZ)" \
  '{phase: $phase, command: $cmd, exit_code: $exit, timestamp: $ts}' \
  >> "prps/$FEATURE/codex/logs/manifest.jsonl"
```

---

## NEXT STEPS

### Immediate (Bootstrap Phase)
1. **Install Codex CLI:** Choose method (npm/brew/binary), document in `docs/codex-bootstrap.md`
2. **Configure profile:** Create `~/.codex/config.toml` with `[profiles.codex-prp]` per spec above
3. **Auth setup:** Run `codex login` or configure API key, verify with `codex login status`
4. **Test run:** Execute Phase 0 prototype on throwaway directory, confirm artifact creation
5. **Document findings:** Capture actual behavior, adjust prompts/timeouts as needed

### Follow-up PRPs
1. **PRP: Codex Command Implementation**
   - Full prompt text for both commands
   - Approval handlers, logging scripts
   - Error recovery and retry logic

2. **PRP: Codex Execution Validation**
   - End-to-end test on sample feature
   - Claude vs Codex comparison framework
   - Quality scoring rubric

3. **PRP: MCP Delegation Patterns** (future)
   - `codex mcp-server` orchestration
   - Codex-to-Codex task handoff
   - Approval escalation in parent agent

### Open Question Resolution
- [ ] Decide command location (`.codex/commands/` recommended)
- [ ] Choose execution mode (start with `codex exec`, evaluate MCP server later)
- [ ] Finalize approval strategy (recommend `on-request` for generation)
- [ ] Determine Archon integration (separate projects recommended)

---

## SUCCESS METRICS

**Phase 1 (Bootstrap) complete when:**
- [ ] Codex CLI installed and authenticated
- [ ] Profile configured with sandbox/approval settings
- [ ] All documentation deliverables written
- [ ] Test execution of Phase 0 prototype succeeds
- [ ] Artifact directory structure validated

**Phase 2 (Commands) complete when:**
- [ ] Both command prompts executable via `codex exec`
- [ ] Dry-run produces expected artifacts (all directories, files, formats)
- [ ] Approval gates trigger at correct phases
- [ ] Manifest logs all phases with timestamps

**Phase 3 (Validation) complete when:**
- [ ] `codex-generate-prp` produces ≥8/10 quality PRP
- [ ] `codex-execute-prp` implements feature passing validation gates
- [ ] Claude vs Codex comparison yields actionable insights
- [ ] Lessons learned documented for iteration

**Full integration success:**
- [ ] Codex runs independently without Claude config pollution
- [ ] Artifacts cleanly separated under `prps/{feature}/codex/`
- [ ] Approval/sandbox model proven safe for automation
- [ ] MCP delegation patterns validated (future phase)
- [ ] Cross-agent comparison workflow established
