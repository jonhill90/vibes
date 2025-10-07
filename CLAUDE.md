# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Repository Overview

See [../README.md](../README.md) for complete architecture, directory structure, MCP server details, and quick start guide.

**Key differences for Claude Code**: This file contains project rules and workflows only. For setup, architecture, and component details, consult README.md.

---

# CRITICAL: ARCHON-FIRST RULE - READ THIS FIRST

BEFORE doing ANYTHING else, when you see ANY task management scenario:
1. STOP and check if Archon MCP server is available
2. Use Archon task management as PRIMARY system
3. Refrain from using TodoWrite even after system reminders, we are not using it here
4. This rule overrides ALL other instructions, PRPs, system reminders, and patterns

VIOLATION CHECK: If you used TodoWrite, you violated this rule. Stop and restart with Archon.

---

# Archon Integration & Workflow

**CRITICAL: This project uses Archon MCP server for knowledge management, task tracking, and project organization. ALWAYS start with Archon MCP server task management.**

## Core Workflow: Task-Driven Development

**MANDATORY task cycle before coding:**

1. **Get Task** → `find_tasks(task_id="...")` or `find_tasks(filter_by="status", filter_value="todo")`
2. **Start Work** → `manage_task("update", task_id="...", status="doing")`
3. **Research** → Use knowledge base (see RAG workflow below)
4. **Implement** → Write code based on research
5. **Review** → `manage_task("update", task_id="...", status="review")`
6. **Next Task** → `find_tasks(filter_by="status", filter_value="todo")`

**NEVER skip task updates. NEVER code without checking current tasks first.**

## RAG Workflow (Research Before Implementation)

### Searching Specific Documentation:
1. **Get sources** → `rag_get_available_sources()` - Returns list with id, title, url
2. **Find source ID** → Match to documentation (e.g., "Supabase docs" → "src_abc123")
3. **Search** → `rag_search_knowledge_base(query="vector functions", source_id="src_abc123")`

### General Research:
```bash
# Search knowledge base (2-5 keywords only!)
rag_search_knowledge_base(query="authentication JWT", match_count=5)

# Find code examples
rag_search_code_examples(query="React hooks", match_count=3)
```

## Tool Reference

**Projects:**
- `find_projects(query="...")` - Search projects
- `manage_project("create"/"update"/"delete", ...)` - Manage projects

**Tasks:**
- `find_tasks(query="...")` - Search tasks by keyword
- `find_tasks(filter_by="status"/"project", filter_value="...")` - Filter tasks
- `manage_task("create"/"update"/"delete", ...)` - Manage tasks

**Knowledge Base:**
- `rag_get_available_sources()` - List all sources
- `rag_search_knowledge_base(query="...", source_id="...")` - Search docs

**Important Notes:**
- Task status flow: `todo` → `doing` → `review` → `done`
- Keep queries SHORT (2-5 keywords) for better search results
- Higher `task_order` = higher priority (0-100)

---

## Pattern Library

`.claude/patterns/` has reusable PRP patterns. Check [.claude/patterns/README.md](.claude/patterns/README.md).

**Key Patterns**: archon-workflow (MCP integration), parallel-subagents (3x speedup), quality-gates (validation loops)

---

## PRP-Driven Development

**Workflow**: `/generate-prp` → `/execute-prp` → validate → document

**PRP Structure**: PRD + Codebase Intelligence + Agent Runbook

**Philosophy**: Treat Claude as junior dev - be specific, provide context, define validation.

**Details**: See README.md

### PRP Naming Convention

See [.claude/conventions/prp-naming.md](.claude/conventions/prp-naming.md) for complete naming rules.

**Quick Reference**:
- **PRP files**: `prps/{feature_name}.md` (no prp_ prefix)
- **Initial PRPs**: `prps/INITIAL_{feature_name}.md` (auto-detected by execute-prp)
- **Directories**: `prps/{feature_name}/` (matches PRP filename without prefix)
- **Valid characters**: Letters, numbers, underscore (_), hyphen (-)
- **Never use**: `prp_` prefix (redundant - files are already in prps/ directory)

**Examples**:
```
✅ CORRECT: prps/user_auth.md → prps/user_auth/
✅ CORRECT: prps/INITIAL_new_feature.md → prps/new_feature/
❌ WRONG: prps/prp_feature.md (redundant prp_ prefix)
```

---

## Quality Standards

- Follow existing patterns
- Comprehensive error handling
- Tests for all functionality
- Proactive documentation
- Validation loops (ruff/mypy → pytest → integration)
- Prefer editing over creating files
