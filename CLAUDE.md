# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Repository Overview

See [../README.md](../README.md) for complete architecture, directory structure, MCP server details, and quick start guide.

**Key differences for Claude Code**: This file contains project rules and workflows only. For setup, architecture, and component details, consult README.md.

---

# Skills System

**This project uses Claude Code Skills for modular, reusable domain expertise.**

## What Are Skills?

Skills are specialized knowledge modules that auto-activate based on context. They provide targeted guidance without loading entire pattern libraries.

**Key Concept**: Skills are documentation, not code. Claude reads and follows guidance in SKILL.md files when relevant to your task.

**Available Skills**:
- **task-management**: Task decomposition, dependency analysis, parallel execution patterns
- **terraform-basics**: Infrastructure-as-code with Terraform for AWS/Azure
- **azure-basics**: Azure cloud services, CLI patterns, resource management

See `.claude/skills/README.md` for complete Skills documentation.

---

# Domain Expert Architecture

**This project uses specialized domain expert agents instead of generic implementers.**

## Available Domain Experts

**Orchestration Experts**:
- **task-manager**: Task decomposition and workflow orchestration
- **knowledge-curator**: Knowledge base curation (basic-memory integration)
- **context-engineer**: Claude context optimization and efficiency

**Infrastructure Experts**:
- **terraform-expert**: Terraform IaC provisioning and state management
- **azure-engineer**: Azure cloud services and resource management

See `.claude/agents/README.md` for complete agent catalog.

## How Domain Experts Work

1. **Auto-Selection**: Commands like `/execute-prp` auto-select appropriate experts based on technical components
2. **Skills Integration**: Experts compose relevant Skills for domain knowledge
3. **Tool Scoping**: Each expert has minimal necessary tools (principle of least privilege)
4. **No Recursion**: Domain experts cannot spawn other agents (orchestration happens at main agent level)

---

# Knowledge Management

**This project uses basic-memory MCP for persistent knowledge storage.**

## Basic-Memory Integration (v0.15.0+)

```python
# Search notes (CRITICAL: explicit project parameter required in v0.15.0+)
mcp__basic_memory__search_notes(
    query="task decomposition patterns",
    project="obsidian",  # Required in v0.15.0+
    page_size=5
)

# Read note
mcp__basic_memory__read_note(
    identifier="note_id",
    project="obsidian"  # Required in v0.15.0+
)

# List directory
mcp__basic_memory__list_directory(
    project="obsidian",
    folder="01-notes/01r-research/"
)
```

**Important**: v0.15.0 breaking change requires explicit `project` parameter for all operations.

---

# Task Tracking

**This project uses file-based task tracking with abstraction layer.**

## TaskTracker Pattern

Tasks are tracked in `prps/{feature_name}/execution/state.json` with the following structure:

```json
{
  "project_id": "uuid",
  "name": "feature_name",
  "tasks": {
    "task-uuid": {
      "title": "Task 1: Description",
      "status": "todo|doing|review|done",
      "created_at": "timestamp"
    }
  }
}
```

**Task Status Flow**: `todo` → `doing` → `review` → `done`

See `.claude/patterns/task-tracking.md` for complete abstraction layer documentation.

---

## Pattern Library

`.claude/patterns/` has reusable PRP patterns. Check [.claude/patterns/README.md](.claude/patterns/README.md).

**Key Patterns**:
- **task-tracking** (file-based state management with abstraction layer)
- **parallel-subagents** (3x speedup for independent tasks)
- **quality-gates** (multi-level validation loops)
- **domain-expert-selection** (auto-select appropriate experts)

---

## PRP-Driven Development

**Workflow**: `/generate-prp` → `/execute-prp` → validate → document

**PRP Structure**: PRD + Codebase Intelligence + Agent Runbook

**Philosophy**: Treat Claude as junior dev - be specific, provide context, define validation.

**Details**: See README.md

---

# Agent Generation

**This project supports 4 methods for creating new domain expert agents.**

## Method 1: Interactive Command (/create-agent)

**Best for**: Quick agent creation with guided prompts

```bash
/create-agent
# or
/create-agent terraform-validator
```

**Workflow**:
1. **Clarification**: Domain/role, responsibilities, tools, skills
2. **Generation**: Auto-generates agent definition with frontmatter
3. **Validation**: Checks syntax, tool scoping, skills references
4. **Testing**: Provides test invocation command

## Method 2: Agent Factory (Planned)

**Best for**: Complex agents requiring multiple specialists

**Pattern**: Planner → Parallel Specialists → Validator → Assembly

See `prps/agent_architecture_modernization/examples/agent_factory_planner.md` for pattern.

## Method 3: Skill-Based Auto-Invoked (Planned)

**Best for**: Auto-generated agents based on task requirements

**Trigger**: Skills with generation capability auto-create agents when needed

## Method 4: Template-Based Domain Profiles (Planned)

**Best for**: Standard domain experts following established patterns

**Usage**: Copy template, fill in domain-specific knowledge

---

## Agent Creation Best Practices

**Do's**:
- ✅ Use explicit `tools` field (never omit - security risk)
- ✅ Minimal tool list (principle of least privilege)
- ✅ Specific description with 2-3 usage examples
- ✅ Compose relevant Skills for domain knowledge
- ✅ Add `allowed_commands` and `blocked_commands`
- ✅ No `Task` tool in domain experts (recursion limitation)

**Don'ts**:
- ❌ Generic "does everything" agents
- ❌ Vague descriptions (hurts auto-delegation)
- ❌ Over-permissioned tool access
- ❌ Missing frontmatter fields (name, description, tools)

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

## Browser Testing for Agents

**Purpose**: Extend validation beyond backend APIs to full-stack UI testing using Playwright browser automation.

### When to Use Browser Testing

**Use browser validation when**:
- ✅ Testing user-facing UI features (document upload, task creation)
- ✅ Validating end-to-end workflows (frontend + backend integration)
- ✅ Verifying React component interactions
- ✅ Testing accessibility and user experience

**Use API testing when**:
- ❌ Backend-only validation (10x faster than browser tests)
- ❌ Data validation (no UI interaction needed)
- ❌ Performance testing (browser adds overhead)

**Key Principle**: Browser tests are Level 3 (Integration) tests - use after API validation passes.

### Quick Start: Browser Validation

```python
# Pre-flight: Ensure services running
Bash("docker-compose up -d")

# Navigate to frontend
browser_navigate(url="http://localhost:5173")

# Capture accessibility tree (agent-parseable structured data)
snapshot = browser_snapshot()

# Validate UI state
if "ExpectedElement" in snapshot:
    print("✅ Validation passed")

# Take screenshot for human proof only
browser_take_screenshot(filename="validation-proof.png")
```

### Available Browser Tools

Agents with browser capability have these MCP tools available:
- `browser_navigate` - Navigate to URL
- `browser_snapshot` - Capture accessibility tree (for validation)
- `browser_click` - Click element using semantic query
- `browser_type` - Type into input field
- `browser_fill_form` - Fill multiple form fields
- `browser_wait_for` - Wait for specific text/element
- `browser_take_screenshot` - Capture screenshot (human proof only)
- `browser_evaluate` - Execute JavaScript
- `browser_install` - Install browser binaries (if needed)

### Common Workflows

#### Document Upload Validation
```python
# Navigate and capture initial state
browser_navigate(url="http://localhost:5173")
initial_state = browser_snapshot()

# Interact with UI
browser_click(element="button containing 'Upload'")
browser_wait_for(text="Select a document", timeout=5000)

# Fill form and submit
browser_fill_form(fields=[
    {"name": "file", "type": "file", "value": "/tmp/test.pdf"}
])
browser_click(element="button containing 'Submit'")
browser_wait_for(text="Upload successful", timeout=30000)

# Validate final state
final_state = browser_snapshot()
if "test.pdf" in final_state:
    print("✅ Document uploaded successfully")
    browser_take_screenshot(filename="upload-proof.png")
```

#### Task Creation Validation
```python
browser_navigate(url="http://localhost:5174")
browser_click(element="button containing 'Create Task'")
browser_fill_form(fields=[
    {"name": "title", "type": "textbox", "value": "Test Task"}
])
browser_click(element="button containing 'Create'")
browser_wait_for(text="Task created", timeout=10000)

# Verify task appears in list
state = browser_snapshot()
if "Test Task" in state:
    print("✅ Task created and visible")
```

### Critical Browser Testing Gotchas

**1. Browser Binaries Not Installed**
```python
# Check browser installed before use
try:
    browser_navigate(url="about:blank")
except Exception:
    print("Installing browser binaries...")
    browser_install()
    time.sleep(30)  # Wait for installation
```

**2. Frontend Service Not Running**
```python
# Always check service health first
result = Bash("docker-compose ps | grep rag-service")
if "Up" not in result.stdout:
    Bash("docker-compose up -d")
    time.sleep(10)
```

**3. Use Accessibility Tree, Not Screenshots**
```python
# ❌ WRONG - Agents can't parse screenshots
screenshot = browser_take_screenshot("validation.png")
# Agent cannot validate from image

# ✅ RIGHT - Use structured accessibility data
snapshot = browser_snapshot()
if "ExpectedElement" in snapshot:
    print("✅ Validated")
```

**4. Element Refs Change Every Render**
```python
# ❌ WRONG - Hard-coded refs break
browser_click(ref="e5")

# ✅ RIGHT - Use semantic queries
browser_click(element="button containing 'Upload'")
```

**5. Use Auto-Wait, Not sleep()**
```python
# ❌ WRONG - Manual waits
time.sleep(3)

# ✅ RIGHT - Conditional waits
browser_wait_for(text="Upload complete", timeout=30000)
```

### Integration with Quality Gates

Browser tests fit at **Level 3b: Browser Integration** in the quality-gates pattern:

```python
# Level 1: Syntax & Style (fast, ~5s)
ruff check && mypy .

# Level 2: Unit Tests (medium, ~30s)
pytest tests/unit/

# Level 3a: API Integration (medium, ~60s)
pytest tests/integration/

# Level 3b: Browser Integration (slow, ~120s)
# Agent-driven browser validation
validate_frontend_browser()
```

### Agents with Browser Capability

- **validation-gates** - Testing and validation specialist, can validate frontend UIs
- **prp-exec-validator** - Full-stack validation (backend + frontend)

### Resources

**Complete Pattern Documentation**: `.claude/patterns/browser-validation.md`
**Agent Configurations**: `.claude/agents/validation-gates.md`, `.claude/agents/prp-exec-validator.md`
**Quality Gates Integration**: `.claude/patterns/quality-gates.md` (Level 3b)
**Code Examples**: `prps/playwright_agent_integration/examples/`

---

## Quality Standards

- Follow existing patterns
- Comprehensive error handling
- Tests for all functionality
- Proactive documentation
- Validation loops (ruff/mypy → pytest → integration)
- Prefer editing over creating files
