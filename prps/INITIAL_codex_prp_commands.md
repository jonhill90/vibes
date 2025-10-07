# INITIAL: Codex PRP Command Suite

## FEATURE
Implement Codex-native equivalents of `/generate-prp` and `/execute-prp` that mirror Vibes’ five-phase workflow while keeping Codex isolated from Claude commands.

### Objectives
- Provide Codex-friendly slash commands or prompts (naming TBD) located outside `.claude/commands/` (e.g., `.codex/commands/` or `codex/commands/`).
- Each command orchestrates the same phases as the Claude versions (setup, research, assembly, execution, validation) but leverages Codex CLI / MCP server primitives exclusively.
- Preserve artifact output structure under `prps/{feature}/codex/…` so Codex-produced assets remain separate.
- Integrate approval, sandbox, and MCP settings from Codex `config.toml` profiles (per findings in `docs/config.md`).

## CURRENT UNDERSTANDING
- Codex CLI can run as:
  - **Interactive CLI** (`codex`),
  - **Batch executor** (`codex exec --prompt …`), and
  - **MCP server** (`codex mcp-server`) exposing JSON-RPC methods (see `codex-rs/docs/codex_mcp_interface.md`).
- Approval modes: `untrusted`, `on-request`, `on-failure`, `never` (per `docs/config.md`). `codex exec` defaults to `never`; we likely want `on-request` for parity with Vibes’ automation.
- Sandbox: `read-only`, `workspace-write`, `danger-full-access`. We should default to `workspace-write` with optional network toggle, mirroring Vibes harness.
- Profiles let us predefine model (`gpt-5-codex` or `o4-mini`), reasoning effort, approval policy, sandbox, and MCP server list.
- Codex MCP server requires clients to respond to approval requests (`applyPatchApproval`, `execCommandApproval`); our command wrappers must capture and relay decisions (automatic or human-in-loop).

## DELIVERABLES
1. **Command Specs** detailing arguments, environment assumptions, and phases for:
   - `codex-generate-prp` (or similar name) → research + PRP assembly.
   - `codex-execute-prp` → implementation, tests, validation, reports.
2. **Workflow Scripts/Prompts** implementing those specs using Codex CLI (likely via `codex exec` with embedded prompts and helper scripts).
3. **Config Guidance** describing required profile entries, sandbox tweaks, and MCP server hooks so commands run consistently.
4. **Artifact Contracts** documenting where outputs land (analysis, docs, gotchas, execution reports) and minimum data requirements.
5. **Validation Plan** specifying log capture, report coverage enforcement, failure handling (retries, fallbacks).

## SCOPE GUARDRAILS
- Do **not** modify `.claude/commands/*`; Codex commands must live in a new namespace.
- No deep Rust changes at this stage; rely on CLI/MCP interfaces.
- Keep Codex configuration isolated (`~/.codex/config.toml` profiles or command-line overrides).
- Ensure commands respect existing sandbox/approval policies in Vibes harness (workspace-write, network restricted by default).

## OPEN QUESTIONS
- Where should commands live? `.codex/commands/` vs `codex/commands/`? Need consensus before implementation.
- Should we drive Codex exclusively via `codex exec` or orchestrate via `codex mcp-server` for richer streaming control?
- How do we surface Codex approval prompts inside Vibes (auto-approve vs escalate to user)?
- Do we reuse Archon projects for Codex runs or create parallel ones?
- Which model defaults? `gpt-5-codex` vs `o4-mini` vs `o3` for higher reasoning accuracy?

## NEXT STEPS
1. Prototype minimal wrapper scripts calling `codex exec` for each phase to confirm feasibility and runtime expectations.
2. Draft command prompt templates that encode PRP phase instructions (setup, research, gotchas, assembly, validation loops).
3. Design approval-handling strategy (auto allow for workspace commands? escalate for network?).
4. Produce PRP document from Codex using new command pipeline on sample feature (e.g., `codex_integration`) to validate artifact layout.

## PROTOTYPE `codex exec` PROMPTS (DRAFT)

Assume a dedicated profile `codex-prp` in `~/.codex/config.toml`:

```toml
[profiles.codex-prp]
model = "gpt-5-codex"
approval_policy = "on-request"
sandbox_mode = "workspace-write"
cwd = "{repo_root}"
startup_timeout_sec = 30
tool_timeout_sec = 600
```

### Phase 0 – Setup & Validation
```bash
codex exec --profile codex-prp --prompt "$(cat <<'PROMPT'
Goal: Prepare Codex workspace for PRP execution.
- Input PRP path: {prp_path}
- Feature name: {feature_name}

Tasks:
1. Verify codex CLI auth via `codex login status`.
2. Confirm sandbox mode + approval policy, log results to prps/{feature_name}/codex/logs/phase0.md.
3. Ensure directories exist: planning/, examples/, execution/, codex/.
4. Summarize detected environment constraints (network disabled?, approvals?).

Output: prps/{feature_name}/codex/logs/setup-summary.md
PROMPT
)"
```

### Phase 1 – Feature Analysis
```bash
codex exec --profile codex-prp --prompt "$(cat <<'PROMPT'
Read {prp_path}. Produce prps/{feature_name}/codex/feature-analysis.md with:
- Goals & success criteria
- Existing assets / reusable patterns
- Risks & unknowns (label RED/AMBER/GREEN)
- Codex-specific considerations (approvals, sandbox limits)
PROMPT
)"
```

### Phase 2A – Codebase Research
```bash
codex exec --profile codex-prp --prompt "$(cat <<'PROMPT'
Search repository for patterns relevant to {feature_name}.
Use `rg`, `fd`, or Python scripts as needed.
Document findings in prps/{feature_name}/codex/codebase-patterns.md:
- File path
- Snippet (≤30 lines)
- Why relevant / how to reuse
- Validation or test hooks
PROMPT
)"
```

### Phase 2B – Documentation Links
```bash
codex exec --profile codex-prp --prompt "$(cat <<'PROMPT'
Aggregate authoritative documentation (official docs, API refs, MCP specs).
Prefer URLs already present in repos/codex/docs/.
Write Markdown table to prps/{feature_name}/codex/documentation-links.md with columns:
Source | URL | Topic | Relevance | Notes
PROMPT
)"
```

### Phase 2C – Example Extraction
```bash
codex exec --profile codex-prp --prompt "$(cat <<'PROMPT'
Identify concrete code/config examples to emulate.
Copy minimal snippets into prps/{feature_name}/codex/examples/, include README.md summarizing:
- Example purpose
- Key APIs / libraries
- How to adapt for {feature_name}
Ensure snippets cite original file paths.
PROMPT
)"
```

### Phase 3 – Gotcha Detection
```bash
codex exec --profile codex-prp --prompt "$(cat <<'PROMPT'
Synthesize gotchas from analysis + research.
Produce prps/{feature_name}/codex/gotchas.md with table:
Issue | Impact | Detection | Resolution | Confidence
Include at least: auth failure, sandbox denial, MCP delegation failure.
PROMPT
)"
```

### Phase 4 – PRP Assembly
```bash
codex exec --profile codex-prp --prompt "$(cat <<'PROMPT'
Assemble Codex-focused PRP using template prps/templates/prp_base.md.
Incorporate outputs from feature-analysis, patterns, docs, examples, gotchas.
Save as prps/{feature_name}/codex/prp_codex.md.
Assign quality score (1-10) + justification.
PROMPT
)"
```

### Phase 5 – Execution Plan Stub
```bash
codex exec --profile codex-prp --prompt "$(cat <<'PROMPT'
From prps/{feature_name}/codex/prp_codex.md, draft execution blueprint:
- Task list with dependencies
- Completion report expectations
- Validation gates (tests, lint, coverage)
Write to prps/{feature_name}/codex/execution-plan.md.
PROMPT
)"
```

### Logging & Validation Hook
After each `codex exec`, append status to `prps/{feature_name}/codex/logs/manifest.jsonl`:
```json
{ "phase": "phase1", "command": "codex exec …", "exit_code": 0, "timestamp": "…" }
```

These prompts are starting points; refine wording once we observe Codex behaviour, especially around approvals and sandbox constraints.
