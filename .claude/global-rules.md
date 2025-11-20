# Global Rules for Claude Code

**These rules apply to ALL interactions in this codebase.**

---

## Skills System Usage

**ALWAYS**:
- Skills auto-activate based on description triggers (no manual invocation needed)
- Skills provide guidance, not executable code (follow patterns, don't expect execution)
- Progressive disclosure: Main SKILL.md under 500 lines, resource files for details
- Specific descriptions for accurate activation (avoid vague triggers)

**NEVER**:
- Don't expect Skills to execute operations (use MCP tools for execution)
- Don't create Skills >500 lines without resource files
- Don't use vague skill descriptions that activate too broadly

See `.claude/skills/README.md` for complete Skills documentation.

---

## Domain Expert Selection

**ALWAYS**:
- Use domain experts for specialized tasks (terraform-expert, azure-engineer, etc.)
- Let commands like `/execute-prp` auto-select appropriate experts
- Check agent exists before invocation (graceful fallback to generic implementer)
- Invoke parallel experts in single response (NOT sequential loop)

**NEVER**:
- Don't use generic implementer when domain expert available
- Don't invoke domain experts sequentially (loses parallelization)
- Don't add `Task` tool to domain experts (recursion limitation)

See `.claude/agents/README.md` for agent catalog.

---

## Basic-Memory Integration (v0.15.0+)

**CRITICAL**: v0.15.0 breaking change requires explicit `project` parameter.

**ALWAYS**:
```python
# Search notes (explicit project required)
mcp__basic_memory__search_notes(
    query="task patterns",
    project="obsidian",  # REQUIRED in v0.15.0+
    page_size=5
)

# Read note (explicit project required)
mcp__basic_memory__read_note(
    identifier="note_id",
    project="obsidian"  # REQUIRED in v0.15.0+
)
```

**NEVER**:
- Don't omit `project` parameter (will fail or use wrong project)
- Don't use write operations in read-only agents (security risk)
- Don't use queries >5 keywords (reduces accuracy)

---

## Task Tracking

**ALWAYS**:
- Use file-based state in `prps/{feature_name}/execution/state.json`
- Follow task status flow: `todo` → `doing` → `review` → `done`
- Validate feature names (6-level security validation) before file paths
- Use atomic file writes (temp file + rename) for concurrent safety

**NEVER**:
- Don't skip feature name validation (path traversal risk)
- Don't use direct writes for state updates (race condition)
- Don't use `replace()` for prefix stripping (use `removeprefix()`)

See `.claude/patterns/task-tracking.md` for abstraction layer.

---

## Parallel Execution

**CRITICAL**: ALL Task() calls in SINGLE response for parallelization.

**ALWAYS**:
```python
# RIGHT - Parallel (max of task times)
Task(subagent_type="researcher", prompt=ctx1)
Task(subagent_type="hunter", prompt=ctx2)
Task(subagent_type="curator", prompt=ctx3)
# Time = max(T1, T2, T3) = 5 min
```

**NEVER**:
```python
# WRONG - Sequential (sum of task times)
for agent in ["researcher", "hunter", "curator"]:
    Task(subagent_type=f"prp-gen-{agent}", prompt=ctx)
# Time = T1 + T2 + T3 = 14 min
```

See `.claude/patterns/parallel-subagents.md` for complete pattern.

---

## Security Rules

**Tool Scoping**:
- ALWAYS include explicit `tools` field in agent definitions
- Minimal tool list (principle of least privilege)
- Never omit `tools` field (inherits ALL MCP tools - security risk)

**Command Safety**:
- Use `allowed_commands` and `blocked_commands` in agent definitions
- Block destructive commands: `terraform destroy`, `rm`, `dd`, `mkfs`
- Validate all file paths before filesystem operations

**Feature Name Security** (6-Level Validation):
1. Path traversal in full path check (`..` detection)
2. Whitelist validation (alphanumeric + `_` + `-` only)
3. Length check (max 50 chars)
4. Directory traversal in extracted name
5. Command injection characters (`;`, `&`, `|`, `$`, `` ` ``)
6. Redundant prefix validation

See `.claude/conventions/prp-naming.md` for validation implementation.

---

## Quality Standards

**Code Quality**:
- Run `ruff check --fix` before committing (Python)
- Run `mypy` for type checking (Python)
- Comprehensive error handling (try/catch for external calls)
- Docstrings for all functions/classes

**Testing**:
- Level 1: Syntax & style checks (fast, ~5s)
- Level 2: Unit tests (medium, ~30s)
- Level 3a: API integration tests (medium, ~60s)
- Level 3b: Browser integration tests (slow, ~120s)

**Documentation**:
- Update CLAUDE.md for workflow changes
- Update pattern files for new patterns
- Create completion reports for task implementations
- Document gotchas as they're discovered

See `.claude/patterns/quality-gates.md` for validation loops.

---

## Anti-Patterns to Avoid

**Generic Agents**:
- ❌ "Does everything" agents without specialization
- ✅ Domain experts with specific expertise

**Tool Inheritance**:
- ❌ Missing `tools` field (access to ALL MCP tools)
- ✅ Explicit minimal tool list

**Sequential Execution**:
- ❌ Task invocation in loop (sequential)
- ✅ All Task() calls in single response (parallel)

**Hard Dependencies**:
- ❌ Direct external service calls without fallback
- ✅ Abstraction layer with graceful degradation

**Archon References** (Deprecated):
- ❌ `mcp__archon__*` calls (removed)
- ✅ File-based task tracking or basic-memory

---

## Migration Notes

**Archon → Skills/Basic-Memory Migration**:
- Task tracking: Use file-based state (`.claude/patterns/task-tracking.md`)
- Knowledge search: Use basic-memory with explicit `project` parameter
- Agent generation: Use `/create-agent` command
- This migration completed in `prps/agent_architecture_modernization.md`

See `docs/migration-archon-to-skills.md` for complete migration guide.

---

## Quick Reference

**Skills**: `.claude/skills/README.md`
**Agents**: `.claude/agents/README.md`
**Patterns**: `.claude/patterns/README.md`
**Commands**: `.claude/commands/*.md`
**Conventions**: `.claude/conventions/prp-naming.md`
**Migration**: `docs/migration-archon-to-skills.md`
