# INITIAL: Codex Integration

## FEATURE

Add first-class support for running OpenAI Codex alongside Vibes without intermixing it with Claude-driven flows. Goal: keep Codex pipelines decoupled while making it easy to hand off features to Codex-only execution.

**Why we care**
- Codex CLI already provides a complete MCP client/server and CLI automation stack – we can reuse it for heavy coding tasks.
- Vibes currently orchestrates Claude-focused PRPs; integrating Codex unlocks dual-agent execution and cross-validation, as long as we keep the pipelines cleanly separated.
- Codex’s approval/sandbox model matches ours, so we can tap into its shell automation without breaking safety.
- Codex exposes an experimental Rust MCP server (`codex mcp-server`) that can take JSON-RPC tasks from other agents, including other Codex instances – ideal for delegated subagent work.

**What “done” looks like**
- Codex repository vendored under `repos/codex` (✅ done) plus bootstrap notes for acquiring the CLI (npm, brew, or release binary).
- Codex-specific profile in `$CODEX_HOME/config.toml` (or CLI flags) that sets model, approval policy, sandbox mode, and MCP server list without touching Claude configs.
- Documentation + templates directing implementers when to call Codex vs Claude, and how to pass artifacts back **without sharing command files**.
- OPTIONAL: Scripts that trigger Codex workflows from Vibes, but only after separate INITIAL/PRP work defines `/generate-prp` and `/execute-prp` equivalents for Codex.

**Scope guardrails**
- CLI-first integration (no VS Code extension wiring).
- Use Codex CLI + MCP interfaces; no deep Rust modifications yet.
- Keep Codex artifacts under `prps/{feature}/codex/` and avoid editing `.claude/commands/*`.
- Ship planning artifacts first; implementation of commands/prompts is deferred to dedicated INITIALs.

## CURRENT STATE CHECKLIST
- [x] `repos/codex` cloned (fresh from https://github.com/openai/codex).
- [ ] Document install paths: `npm install -g @openai/codex`, `brew install codex`, or download release binaries.
- [ ] Draft reference `config.toml` snippet with Codex-specific profile (model, approval policy, sandbox_mode, MCP servers).
- [ ] Clarify how Codex CLI and Codex MCP server interact (single instance vs delegating tasks to additional codex-mcp-server processes).
- [ ] Define artifact hand-off protocol (PRP inputs, outputs) living under `prps/{feature}/codex/`.
- [ ] Validation strategy for Codex runs (capture outputs, approvals, failure handling).

## DELIVERABLES
1. **Bootstrap Notes** – document install routes, profile scaffolding, and auth prerequisites derived from `docs/config.md`.
2. **MCP Server Strategy** – outline how to launch `codex mcp-server` in parallel, including how one Codex instance can hand tasks to another through MCP (no implementation yet).
3. **Artifact Directory** – define the folder structure + file naming for Codex outputs (analysis, patterns, gotchas, transcripts) under `prps/{feature}/codex/`.
4. **Validation Plan** – checklists + fallback for when Codex can’t run (e.g., sandbox restrictions, auth issues).
5. **Follow-up INITIALs** – prepare separate INITIAL docs for building `/generate-prp` and `/execute-prp` equivalents tailored to Codex (see “Next Steps”).

## REFERENCE PATTERNS
- `docs/config.md` (Codex repo) → configuration precedence, profiles, sandbox/approval, MCP server wiring. Pay special attention to `sandbox_mode`, `approval_policy`, and `[mcp_servers.*]` blocks.
- `codex-rs/docs/codex_mcp_interface.md` → JSON-RPC API exposures for `codex mcp-server` (start conversations, send turns, approvals, login). Shows how Codex can be controlled programmatically, including the possibility of one Codex instance delegating to another.
- `docs/advanced.md` → quickstart for `codex mcp-server` using MCP Inspector.
- `.claude/commands/generate-prp.md` & `.claude/commands/execute-prp.md` → comparison point for eventual Codex-specific equivalents (but do **not** modify these).

## GOTCHAS TO PLAN FOR
- **Authentication** – Codex expects ChatGPT login or API key; need clear fallback instructions.
- **Sandboxing** – ensure approval policies line up with our `workspace-write` model; double-check env vars like `CODEX_SANDBOX`.
- **Timeouts** – Codex runs may take minutes (docs recommend 600s); build patience/retry logic into the command.
- **Binary availability** – decide whether to rely on globally installed `codex` binary or run via `npx @openai/codex`.
- **Artifact paths** – keep outputs inside `prps/{feature}/codex/` to avoid polluting repo root.
- **Profile drift** – Codex uses layered config precedence (`--config`, profile, config.toml, defaults). We must document a canonical profile to avoid leaking Claude-specific settings.
- **MCP delegation** – `codex mcp-server` requires clients to respond to approval requests; any orchestration must either auto-approve via policy or forward prompts back to humans.

## CONFIG & MCP NOTES (FROM `docs/config.md` + `codex_mcp_interface.md`)
- Config precedence: CLI flags > `--config key=value` > selected profile > root config > built-in defaults. Profiles (“[profiles.name]”) let us bundle model + sandbox for Codex-specific runs.
- Approval policies: `untrusted`, `on-request`, `on-failure`, `never`. `codex exec` defaults to `never`; we likely want `on-request` or `on-failure` for delegated workflows.
- Sandbox modes: `read-only`, `workspace-write`, `danger-full-access`. Additional knobs for `workspace-write` (extra writable roots, network toggle). Codex enforces `.git/` read-only by default.
- MCP servers: `[mcp_servers.<id>]` entries define `command`, `args`, `env`; also supports streamable HTTP via `url` + `bearer_token`. `experimental_use_rmcp_client` switches to the Rust SDK client.
- MCP server binary: `codex mcp-server` exposes JSON-RPC methods (`newConversation`, `sendUserMessage`, approvals). Clients must handle approval requests (`applyPatchApproval`, `execCommandApproval`).
- Delegation idea: a parent Codex instance (or other agent) can spawn `codex mcp-server`, send tasks via MCP, and optionally relay approvals; enables Codex-to-Codex handoffs without Claude.

## OPEN QUESTIONS
- Should Codex be invoked per-phase (e.g., Codex handles research while Claude assembles), or as a full replacement PRP executor?
- Do we maintain separate Archon projects for Codex runs, or reuse Claude’s existing project/task IDs?
- How do we compare/merge Codex-produced PRPs with Claude’s version (diff pipeline, scoring)?
- What’s the minimal viable setup for auth in CI/automation contexts?

## NEXT STEPS
1. Prototype direct CLI invocation: `codex exec -p '<prompt>'` inside a throwaway directory, capture outputs.
2. Map PRP phases to Codex capabilities (research, implementation, validation) and decide hand-off boundaries.
3. Implement the new command/prompt with fallback logging and approval-handling aligned to Vibes standards.
4. Validate end-to-end with sample feature (e.g., `codex_integration`) and document lessons learned.
