# Codebase Patterns: Playwright Agent Integration

## Overview

This document extracts patterns from existing agent configurations and validation workflows to guide the Playwright browser tools integration. The patterns focus on YAML frontmatter syntax, agent description updates, validation loop structures, and pattern documentation formats found in `.claude/agents/` and `.claude/patterns/`.

## Architectural Patterns

### Pattern 1: Agent YAML Frontmatter Tool Declaration

**Source**: `/Users/jon/source/vibes/.claude/agents/validation-gates.md`, `/Users/jon/source/vibes/.claude/agents/prp-exec-validator.md`
**Relevance**: 10/10
**What it does**: Declares tools available to agents in YAML frontmatter at top of agent markdown files

**Key Techniques**:
```yaml
---
name: validation-gates
description: "Testing and validation specialist..."
tools: Bash, Read, Edit, MultiEdit, Grep, Glob, TodoWrite
---
```

```yaml
---
name: prp-exec-validator
description: "USE PROACTIVELY for systematic validation..."
tools: Bash, Read, Edit, Grep
color: cyan
---
```

**When to use**:
- All agent configuration files in `.claude/agents/`
- Tools are comma-separated list (no quotes around individual tools)
- Tool names are case-sensitive and match exact MCP server exports
- Optional `color` field for visual differentiation
- Description should mention key capabilities

**How to adapt**:
- Add browser tool names to existing `tools:` field
- Keep comma-separated format: `tools: Bash, Read, Edit, browser_navigate, browser_snapshot`
- Update description to mention "frontend validation" or "UI testing" capabilities
- Use full MCP tool names with server prefix when calling: `mcp__MCP_DOCKER__browser_navigate`

**Why this pattern**:
- Declarative tool access (agents don't request tools, they receive them)
- Tools automatically available during agent execution
- No code changes needed in agent logic
- YAML frontmatter parsed by agent invocation system

---

### Pattern 2: Validation Loop with Fix Iterations (Max 5 Attempts)

**Source**: `/Users/jon/source/vibes/.claude/agents/prp-exec-validator.md` (lines 92-116), `.claude/patterns/quality-gates.md` (lines 49-70)
**Relevance**: 10/10
**What it does**: Iterative validation pattern that runs validation commands, analyzes failures, applies fixes, and retries up to 5 times

**Key Techniques**:
```python
MAX_ATTEMPTS = 5

for attempt in range(1, MAX_ATTEMPTS + 1):
    result = run_validation(level, commands)

    if result.success:
        print(f"✅ Level {level} passed")
        break

    print(f"❌ Attempt {attempt}/{MAX_ATTEMPTS} failed: {result.error}")

    if attempt < MAX_ATTEMPTS:
        # Analyze error against PRP gotchas, apply fix
        error_analysis = analyze_error(result.error, prp_gotchas)
        fix_attempt = apply_fix(error_analysis)
        print(f"Applied fix: {fix_attempt.description}")
    else:
        print(f"⚠️ Max attempts reached - manual intervention required")
```

**Example from prp-exec-validator.md**:
```python
for level in validation_levels:
    max_attempts = 5
    attempt = 0

    while attempt < max_attempts:
        result = run_validation(level)

        if result.passed:
            print(f"✅ {level} passed")
            break
        else:
            print(f"❌ {level} failed (attempt {attempt + 1})")
            errors = parse_errors(result)
            fixes = determine_fixes(errors)
            apply_fixes(fixes)
            attempt += 1

    if attempt == max_attempts:
        print(f"⚠️ {level} failed after {max_attempts} attempts")
```

**When to use**:
- Browser validation can fail due to timeouts, element not found, frontend not running
- Same 5-attempt pattern applies to browser tests as backend tests
- Browser failures often require different fixes (wait longer, check service health)

**How to adapt**:
- Apply same loop structure to browser validation steps
- Error patterns specific to browser:
  - "Connection refused" → Check if frontend running (docker-compose ps)
  - "Element not found" → Wait longer or use semantic queries
  - "Browser not installed" → Run `browser_install` tool
  - "Timeout" → Increase wait duration or check service health

**Why this pattern**:
- Prevents giving up after first failure (browser tests more flaky than unit tests)
- Systematic fix approach (analyze → fix → retry)
- Max attempts prevents infinite loops
- Documents all fix attempts for learning

---

### Pattern 3: Multi-Level Quality Gates (Syntax → Unit → Integration)

**Source**: `.claude/patterns/quality-gates.md` (lines 1-48), `.claude/agents/validation-gates.md` (lines 33-43)
**Relevance**: 10/10
**What it does**: Hierarchical validation gates that must pass in sequence, with browser tests fitting at Level 3 (Integration)

**Key Techniques**:
```bash
# Level 1: Syntax & Style (fast checks)
ruff check --fix src/ && mypy src/  # Python
eslint --fix src/                   # JavaScript

# Level 2: Unit Tests
pytest tests/ -v

# Level 3: Integration Tests
# Project-specific (from PRP)
docker-compose up -d && ./integration_tests.sh
```

**Validation Gates Checklist** (from validation-gates.md):
```markdown
Before marking any task as complete, ensure:
- [ ] All unit tests pass
- [ ] Integration tests pass (if applicable)
- [ ] Linting produces no errors
- [ ] Type checking passes (for typed languages)
- [ ] Code formatting is correct
- [ ] Build succeeds without warnings
- [ ] No security vulnerabilities detected
- [ ] Performance benchmarks met (if applicable)
```

**When to use**:
- Browser tests fit at **Level 3: Integration Tests**
- Browser tests should come AFTER unit tests pass (they're slower)
- Browser tests validate end-to-end flows (navigation → interaction → validation)

**How to adapt for browser validation**:
```markdown
### Level 3: Integration Tests

#### API Integration Tests
```bash
pytest tests/integration/ -v
```

#### Frontend Integration Tests (NEW)
```bash
# Ensure frontend running
docker-compose ps | grep "Up" || docker-compose up -d

# Browser validation
# 1. Navigate to frontend
browser_navigate(url="http://localhost:5173")

# 2. Capture accessibility tree
snapshot = browser_snapshot()

# 3. Verify expected elements
assert "DocumentList" in snapshot

# 4. Interact with UI
browser_click(element="Upload button")

# 5. Validate state change
browser_wait_for(text="Upload successful")

# 6. Capture proof screenshot
browser_take_screenshot(filename="validation-proof.png")
```
```

**Why this pattern**:
- Fast tests first (syntax), slow tests last (browser)
- Browser tests depend on backend working (Level 2 must pass first)
- Integration level is correct place for full-stack validation
- Validates actual user workflows, not just API contracts

---

### Pattern 4: Agent Description Update Pattern

**Source**: All agents in `.claude/agents/` directory
**Relevance**: 9/10
**What it does**: Agent descriptions explain capabilities, mention tool access, guide when to invoke agent

**Key Techniques**:

**validation-gates description** (before):
```yaml
description: "Testing and validation specialist. Proactively runs tests, validates code changes, ensures quality gates are met, and iterates on fixes until all tests pass. Call this agent after you implement features and need to validate that they were implemented correctly. Be very specific with the features that were implemented and a general idea of what needs to be tested."
```

**Recommended after** (for browser capability):
```yaml
description: "Testing and validation specialist. Proactively runs tests (backend + frontend UI), validates code changes, ensures quality gates are met, and iterates on fixes until all tests pass. Can perform browser automation for end-to-end testing. Call this agent after you implement features and need to validate that they were implemented correctly, including UI validation."
```

**prp-exec-validator description** (before):
```yaml
description: "USE PROACTIVELY for systematic validation. Runs validation gates from PRP, analyzes failures, suggests fixes, iterates until all pass. Works autonomously with fix loops."
```

**Recommended after**:
```yaml
description: "USE PROACTIVELY for systematic validation. Runs validation gates from PRP (backend + frontend UI), analyzes failures, suggests fixes, iterates until all pass. Works autonomously with fix loops. Can perform browser validation for full-stack testing."
```

**When to use**:
- Update description when adding major new capability
- Keep description concise (1-2 sentences)
- Mention key tools or capabilities (e.g., "browser automation", "UI testing")
- Guide invocation context ("Call this agent after...")

**How to adapt**:
- Add "(backend + frontend UI)" or similar qualifier
- Mention "browser automation" or "end-to-end testing"
- Keep existing structure and tone
- Don't list all tools in description (tools field does that)

**Why this pattern**:
- Description helps users know when to invoke agent
- Mentions new capability without overwhelming detail
- Maintains consistency with existing agent descriptions

---

### Pattern 5: Archon Workflow Integration (Health Check + Graceful Degradation)

**Source**: `.claude/patterns/archon-workflow.md` (lines 10-21)
**Relevance**: 8/10
**What it does**: Checks Archon availability, uses it for tracking when available, gracefully degrades when unavailable

**Key Techniques**:
```python
# 1. Health check (ALWAYS FIRST)
health = mcp__archon__health_check()
archon_available = health["status"] == "healthy"

# 2. Graceful fallback - never fail workflow if Archon unavailable
if not archon_available:
    project_id = None
    task_ids = []
    print("ℹ️ Archon MCP not available - proceeding without project tracking")
else:
    # 3. Create project
    project = mcp__archon__manage_project("create",
        title=f"PRP Generation: {feature_name}",
        description="Creating comprehensive PRP from INITIAL.md"
    )
    project_id = project["project"]["id"]
```

**When to use**:
- When agent needs to track work in Archon (validation results, task status)
- Always check health before using Archon tools
- Never fail if Archon unavailable (graceful degradation)

**How to adapt for browser validation**:
- Can track browser validation results in Archon tasks
- Document browser test outcomes as task notes
- Update task status: "doing" → "done" after browser validation
- No Archon integration required for basic browser tool usage

**Why this pattern**:
- Ensures workflow works with or without Archon
- Provides audit trail when Archon available
- No dependency on external service for core functionality

---

### Pattern 6: Parallel Subagent Execution (3x Speedup)

**Source**: `.claude/patterns/parallel-subagents.md`
**Relevance**: 7/10
**What it does**: Invokes multiple independent agents simultaneously in single response for parallel execution

**Key Techniques**:
```python
# RIGHT - Parallel (max of task times)
Task(subagent_type="researcher", ...)
Task(subagent_type="hunter", ...)
Task(subagent_type="curator", ...)
# ALL in SAME response = parallel, Total: 5 min

# WRONG - Sequential (sum of task times)
Task(subagent_type="researcher", ...)  # [waits]
Task(subagent_type="hunter", ...)      # Total: 14 min
```

**When to use**:
- Browser validation CAN run in parallel with API tests if:
  - Tests are independent (no shared state)
  - No file conflicts
  - Frontend already running
- Example: Backend API tests + Frontend UI tests simultaneously

**How to adapt**:
```python
# Can invoke multiple validation agents in parallel
Task(subagent_type="validation-gates",
     prompt="Validate backend API endpoints")
Task(subagent_type="validation-gates",
     prompt="Validate frontend UI at localhost:5173")
# Both run simultaneously
```

**Why this pattern**:
- Browser tests often slower than API tests (10x)
- Running in parallel reduces total validation time
- Must ensure tests don't interfere with each other

---

## Naming Conventions

### File Naming

**Pattern**: `{agent-name}.md` in `.claude/agents/` directory
**Examples**:
- `validation-gates.md`
- `prp-exec-validator.md`
- `prp-exec-implementer.md`
- `documentation-manager.md`

**For new pattern file**:
- `browser-validation.md` in `.claude/patterns/` directory

### Agent Name Convention

**Pattern**: `{role}-{scope}` using kebab-case
**Examples**:
- `validation-gates` (role: validation, scope: gates)
- `prp-exec-validator` (role: prp-exec, scope: validator)
- `prp-gen-codebase-researcher` (role: prp-gen, scope: codebase-researcher)

**No changes needed** - existing agent names remain the same

### Tool Name Convention

**Pattern**: MCP tools use `mcp__{SERVER}__{tool_name}` format
**Examples**:
- `mcp__MCP_DOCKER__browser_navigate`
- `mcp__MCP_DOCKER__browser_snapshot`
- `mcp__MCP_DOCKER__browser_click`

**But in agent tools field**: Use short names (agent system adds prefix)
- `tools: browser_navigate, browser_snapshot, browser_click`

---

## File Organization

### Agent Directory Structure

```
.claude/
├── agents/
│   ├── validation-gates.md           # Update: Add browser tools
│   ├── prp-exec-validator.md         # Update: Add browser tools
│   ├── prp-exec-implementer.md       # Optional: Add browser tools
│   ├── documentation-manager.md      # Optional: Add browser tools
│   └── README.md                     # Update: Document browser testing
└── patterns/
    ├── quality-gates.md              # Update: Add Level 3 browser testing
    ├── archon-workflow.md            # No changes needed
    ├── parallel-subagents.md         # No changes needed
    ├── security-validation.md        # No changes needed
    ├── browser-validation.md         # NEW: Create browser testing pattern
    └── README.md                     # Update: Add browser-validation to index
```

**Justification**: Follows existing pattern library structure with agents in `.claude/agents/` and reusable patterns in `.claude/patterns/`

---

## Common Utilities to Leverage

### 1. Quality Gates Validation Loop

**Location**: `.claude/patterns/quality-gates.md` (lines 49-100)
**Purpose**: Provides reusable validation loop with max attempts and error analysis
**Usage Example**:
```python
from patterns.quality_gates import run_validation_loop

result = run_validation_loop(
    level="Browser Integration",
    command="browser_navigate http://localhost:5173",
    max_attempts=5,
    error_patterns=browser_error_patterns
)
```

### 2. Error Analysis Pattern

**Location**: `.claude/patterns/quality-gates.md` (lines 73-100)
**Purpose**: Matches errors against known patterns and suggests fixes
**Usage Example**:
```python
def analyze_error(error_message: str, prp_gotchas: str) -> dict:
    # Error patterns
    patterns = {
        "browser_not_installed": r"Browser.*not found",
        "connection_refused": r"Connection refused|ECONNREFUSED",
        "element_not_found": r"Element.*not found",
        "timeout": r"TimeoutError|timeout",
    }

    # Identify type and suggest fix
    for error_type, pattern in patterns.items():
        if re.search(pattern, error_message):
            return suggest_fix(error_type)
```

### 3. Archon Health Check

**Location**: `.claude/patterns/archon-workflow.md` (lines 10-18)
**Purpose**: Checks if Archon available before using tracking features
**Usage Example**:
```python
health = mcp__archon__health_check()
if health["status"] == "healthy":
    # Track validation results in Archon
    mcp__archon__manage_task("update", task_id=task_id,
                             status="done",
                             description="Browser validation passed")
```

### 4. Parallel Execution Conflict Check

**Location**: `.claude/patterns/parallel-subagents.md` (lines 100-117)
**Purpose**: Ensures parallel tasks don't have file conflicts
**Usage Example**:
```python
def can_run_in_parallel(tasks):
    all_files = set()
    for task in tasks:
        if all_files & set(task.get('files',[])):
            return False
        all_files.update(task.get('files',[]))
    return True
```

---

## Testing Patterns

### Unit Test Structure

**Pattern**: No unit tests for agent configuration (declarative YAML)
**Example**: Agent markdown files are configuration, not code
**Key techniques**:
- Test by invoking agents with test tasks
- Verify agent can access declared tools
- Validate agent follows documented patterns

### Integration Test Structure

**Pattern**: Manual testing via agent invocation
**Example**: Test validation-gates agent with browser validation task
**Key workflow**:
```bash
# 1. Start frontend service
docker-compose up -d

# 2. Invoke agent with browser validation task
claude --agent validation-gates "Validate RAG service frontend at localhost:5173"

# 3. Verify agent uses browser tools
# - Agent navigates to URL
# - Agent captures accessibility snapshot
# - Agent interacts with UI elements
# - Agent validates expected state
# - Agent takes screenshot for proof

# 4. Check validation report
cat prps/validation-report.md
```

---

## Anti-Patterns to Avoid

### 1. Hardcoding Port Numbers in Agent Definitions

**What it is**: Putting specific ports (5173, 5174) in agent markdown files
**Why to avoid**: Ports may differ across environments or projects
**Found in**: None currently (good!)
**Better approach**: Pass ports as parameters when invoking agents
```markdown
# Bad: "Validate frontend at localhost:5173"
# Good: "Validate frontend at {url}" where url provided by caller
```

### 2. Listing Full MCP Tool Names in Agent Tools Field

**What it is**: Using `mcp__MCP_DOCKER__browser_navigate` in tools field
**Why to avoid**: Agent system adds prefix automatically, creates duplication error
**Found in**: None currently
**Better approach**: Use short names
```yaml
# Bad:
tools: Bash, Read, mcp__MCP_DOCKER__browser_navigate

# Good:
tools: Bash, Read, browser_navigate
```

### 3. Skipping Health Checks for External Services

**What it is**: Calling browser tools without checking if frontend running
**Why to avoid**: Fails immediately instead of gracefully, wastes validation attempts
**Found in**: Not applicable yet (pattern not implemented)
**Better approach**: Check service health before browser validation
```python
# Before browser tests
result = Bash("docker-compose ps | grep rag-service")
if "Up" not in result.stdout:
    print("⚠️ Frontend not running, starting services...")
    Bash("docker-compose up -d")
    time.sleep(5)  # Wait for services to be ready
```

### 4. Using Element References Instead of Semantic Queries

**What it is**: Hard-coding element refs like `ref="e5"` that change between renders
**Why to avoid**: Flaky tests, references change on every page load
**Found in**: Example in INITIAL.md (for demonstration)
**Better approach**: Use semantic queries
```python
# Bad:
browser_click(element="button", ref="e5")

# Good:
browser_click(element="button containing 'Upload'")
browser_click(element="Upload button")  # Semantic description
```

### 5. Taking Screenshots for Agent Validation

**What it is**: Using `browser_take_screenshot` for agent to "see" UI
**Why to avoid**: Agents cannot parse visual images, only accessibility trees
**Found in**: Feature analysis correctly notes this limitation
**Better approach**: Use `browser_snapshot` for validation, screenshots for humans
```python
# For agent validation:
snapshot = browser_snapshot()
assert "expected text" in snapshot

# For human verification (optional):
browser_take_screenshot(filename="proof.png")
```

---

## Implementation Hints from Existing Code

### Similar Features Found

#### 1. **Quality Gates Pattern** (`.claude/patterns/quality-gates.md`)

- **Similarity**: Browser validation fits into existing quality gates framework
- **Lessons**:
  - Max 5 attempts per validation level works well
  - Error analysis against known gotchas prevents repeated mistakes
  - Multi-level gates (syntax → unit → integration) logical progression
- **Differences**: Browser tests slower (100-500ms vs 10-50ms for unit tests)
- **Integration**: Add browser testing as Level 3b subsection

#### 2. **Agent Tool Declaration** (All agents in `.claude/agents/`)

- **Similarity**: All agents declare tools in YAML frontmatter
- **Lessons**:
  - Comma-separated list format consistent across all agents
  - No quotes around individual tool names
  - Description mentions key capabilities
  - Optional color field for visual distinction
- **Differences**: Browser tools longer list than typical (9 tools vs 4-7)
- **Integration**: Add browser tools to existing tools lists

#### 3. **Validation Loop Pattern** (`prp-exec-validator.md`)

- **Similarity**: Iterative validation with failure analysis
- **Lessons**:
  - Clear attempt tracking (1/5, 2/5, etc.)
  - Document all fixes applied
  - Report remaining issues after max attempts
  - Check PRP gotchas before generic fixes
- **Differences**: Browser errors have specific patterns (timeout, element not found)
- **Integration**: Add browser-specific error patterns to analysis

---

## Recommendations for PRP

Based on pattern analysis:

1. **Follow YAML Frontmatter Pattern** for agent tool declarations
   - Add browser tools as comma-separated list: `tools: Bash, Read, Edit, browser_navigate, browser_snapshot, browser_click, browser_type, browser_take_screenshot, browser_evaluate, browser_wait_for, browser_fill_form, browser_tabs, browser_install`
   - Update descriptions to mention "frontend UI validation" or "browser automation"
   - Keep existing tool list, append browser tools

2. **Reuse Quality Gates Validation Loop** instead of reimplementing
   - Apply same 5-attempt max to browser tests
   - Add browser-specific error patterns:
     - "Connection refused" → Check service health
     - "Browser not installed" → Run browser_install
     - "Element not found" → Use semantic queries
     - "Timeout" → Increase wait duration
   - Document browser validation in Level 3 (Integration Tests)

3. **Mirror Pattern Library Structure** for consistency
   - Create `browser-validation.md` in `.claude/patterns/`
   - Follow same format as `quality-gates.md` and `parallel-subagents.md`
   - Include: Quick reference, core pattern, rules (DO/DON'T), examples
   - Update `.claude/patterns/README.md` index

4. **Adapt Validation Loop Pattern** for browser validation
   - Same structure as backend validation (attempt → fail → analyze → fix → retry)
   - Browser-specific fixes documented in Known Gotchas
   - Use accessibility snapshots for validation (not screenshots)
   - Screenshots optional for human verification only

5. **Avoid Hard-coding Environment Details** based on existing anti-patterns
   - Don't hardcode ports in agent definitions
   - Pass URLs/ports as parameters when invoking
   - Check service health before browser tests
   - Use semantic element queries (not refs)

---

## Source References

### From Archon

- **b8565aff9938938b**: Agent configuration and tool setup patterns - Relevance 4/10
  - Task setup patterns (not directly applicable to agent config)
  - Multi-agent coordination examples

### From Local Codebase

- **`.claude/agents/validation-gates.md:1-7`**: YAML frontmatter tool declaration pattern
- **`.claude/agents/prp-exec-validator.md:1-6`**: Agent description and color field pattern
- **`.claude/agents/prp-exec-validator.md:92-116`**: Validation loop with max 5 attempts
- **`.claude/patterns/quality-gates.md:1-129`**: Multi-level quality gates and validation loops
- **`.claude/patterns/archon-workflow.md:10-21`**: Health check and graceful degradation
- **`.claude/patterns/parallel-subagents.md:1-151`**: Parallel execution for speedup
- **`.claude/patterns/README.md:1-64`**: Pattern library structure and index format
- **`prps/INITIAL_playwright_agent_integration.md:28-39`**: MCP_DOCKER browser tools list
- **`prps/INITIAL_playwright_agent_integration.md:132-164`**: Browser validation workflow examples
- **`prps/playwright_agent_integration/planning/feature-analysis.md:118-131`**: Agent tool configuration pattern from similar PRPs

---

## Next Steps for Assembler

When generating the PRP:

1. **Reference these patterns in "Current Codebase Tree" section**:
   - List `.claude/agents/validation-gates.md` and `.claude/agents/prp-exec-validator.md` as files to modify
   - List `.claude/patterns/quality-gates.md` as pattern to extend
   - Note `.claude/patterns/browser-validation.md` as new file to create

2. **Include key code snippets in "Implementation Blueprint"**:
   - YAML frontmatter pattern for adding tools
   - Validation loop pattern adapted for browser tests
   - Browser-specific error patterns and fixes
   - Accessibility snapshot validation (not screenshots)

3. **Add anti-patterns to "Known Gotchas" section**:
   - Don't use full MCP tool names in tools field (use short names)
   - Don't hardcode ports in agent definitions
   - Don't use element refs (use semantic queries)
   - Don't use screenshots for agent validation (use snapshots)
   - Don't skip service health checks

4. **Use file organization for "Desired Codebase Tree"**:
   ```
   .claude/
   ├── agents/
   │   ├── validation-gates.md           # MODIFY: Add browser tools
   │   ├── prp-exec-validator.md         # MODIFY: Add browser tools
   │   └── README.md                     # UPDATE: Document browser testing
   └── patterns/
       ├── quality-gates.md              # UPDATE: Add Level 3 browser section
       ├── browser-validation.md         # CREATE: New browser pattern
       └── README.md                     # UPDATE: Add to index
   ```

5. **Document validation strategy**:
   - Manual testing by invoking agents with browser tasks
   - Verify agents can access browser tools
   - Test against running frontend (localhost:5173, localhost:5174)
   - Capture screenshots for proof of validation

---

**Summary**: All patterns extracted from existing codebase. Primary focus on YAML frontmatter syntax (Pattern 1), validation loop structure (Pattern 2), quality gates integration (Pattern 3), and agent description updates (Pattern 4). Browser tools integrate into existing patterns without breaking changes.
