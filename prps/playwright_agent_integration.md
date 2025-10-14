# PRP: Playwright Browser Tools Integration for Validation Agents

**Generated**: 2025-10-13
**Based On**: prps/INITIAL_playwright_agent_integration.md
**Archon Project**: 61b423b5-8938-4fde-a781-b21313cac863
**Archon Task**: 6bdf6b8b-3b30-41dd-9da4-8b8db2a5c600

---

## Goal

Enable validation and testing agents to perform full-stack validation including React UI testing by adding Playwright browser automation tool access. This extends current backend-only validation to end-to-end frontend testing using MCP_DOCKER browser tools already available in the environment.

**End State**:
- `validation-gates` agent can validate frontend UIs via browser automation
- `prp-exec-validator` agent can run full-stack validation (backend + frontend)
- Browser validation integrated into existing quality-gates pattern
- Browser validation pattern documented in `.claude/patterns/browser-validation.md`
- All browser testing follows accessibility-first approach (tree-based, not screenshot-based)

---

## Why

**Current Pain Points**:
- Validation agents can only validate backend APIs (pytest, mypy, ruff)
- Frontend UI changes go unvalidated - manual testing required
- No automated verification that UIs work after backend changes
- No proof of working frontend in validation reports

**Business Value**:
- True end-to-end validation (not just backend contracts)
- Catch UI bugs before deployment
- Automated validation of user-facing features
- Reduced manual testing time
- Higher confidence in full-stack changes

---

## What

### Core Features

1. **Agent Configuration Updates** (High Priority)
   - Add browser tools to `validation-gates.md` tool list
   - Add browser tools to `prp-exec-validator.md` tool list
   - Update agent descriptions to mention frontend validation capability

2. **Browser Validation Pattern** (High Priority)
   - Create `.claude/patterns/browser-validation.md`
   - Document navigation → interaction → validation workflow
   - Include accessibility tree usage guidance
   - Integrate with existing quality-gates pattern

3. **Documentation Updates** (Medium Priority)
   - Update `.claude/patterns/quality-gates.md` with Level 3b browser testing section
   - Update `.claude/patterns/README.md` to index browser-validation pattern
   - Update CLAUDE.md with browser testing guidance for agents

### Success Criteria

- ✅ `validation-gates` agent has browser tools in YAML frontmatter
- ✅ `prp-exec-validator` agent has browser tools in YAML frontmatter
- ✅ `browser-validation.md` pattern created with complete workflows
- ✅ Agent can navigate to localhost:5173 and capture accessibility tree
- ✅ Agent can interact with UI elements (click, type, fill form)
- ✅ Agent can validate UI state using accessibility snapshots (not screenshots)
- ✅ Validation reports include browser test results
- ✅ All critical gotchas documented with solutions

---

## All Needed Context

### Documentation & References

```yaml
# MUST READ - Playwright Python API
- url: https://playwright.dev/python/docs/library
  sections:
    - "Getting Started - Library" - Sync and async API patterns, browser launch
    - "Page Class API" - Navigation, interaction, element selection
  why: Core browser automation framework, essential setup patterns
  critical_gotchas:
    - Thread safety: Playwright sync API is NOT thread-safe (use multiprocessing)
    - Browser binaries: Must run `playwright install` after pip install
    - Auto-waiting: Built-in smart waiting eliminates need for sleep()

- url: https://playwright.dev/docs/locators
  sections:
    - "Locators Guide" - Semantic element selection strategies
  why: Resilient element selection critical for agent validation
  critical_gotchas:
    - Never use element refs (e.g., ref="e5") - they change between renders
    - Use semantic queries: get_by_role(), get_by_text(), get_by_label()
    - Locators are strict by default - must handle multiple matches

- url: https://playwright.dev/docs/accessibility-testing
  sections:
    - "Accessibility Testing" - Accessibility tree usage for validation
  why: Agents validate via accessibility tree, not screenshots
  critical_gotchas:
    - Agents cannot parse visual screenshots (just base64 to them)
    - Use accessibility snapshots for validation (~500 tokens)
    - Screenshots only for human verification (~2000 tokens)

- url: https://playwright.dev/docs/test-timeouts
  sections:
    - "Timeouts Configuration" - Default and custom timeout settings
  why: Error handling for slow operations
  critical_gotchas:
    - Default test timeout: 30s, assertion timeout: 5s
    - Only increase when necessary (indicates design issues)
    - Use auto-wait instead of manual time.sleep()

- url: https://playwright.dev/python/docs/api-testing
  sections:
    - "API Testing Guide" - Hybrid API + browser testing approach
  why: Integration between API and browser testing
  critical_gotchas:
    - Use API for data setup (fast), browser for UI validation (slow)
    - Browser tests are 10x slower than API tests
    - Hybrid approach is optimal

# MUST READ - MCP Protocol
- url: https://modelcontextprotocol.io/
  sections:
    - "MCP Overview" - How MCP connects AI applications to tools
    - "MCP Specification" - Protocol requirements for tool integration
  why: Understanding how agents access browser tools
  critical_gotchas:
    - Tool names follow: mcp__{SERVER}__{tool_name} pattern
    - Tools are declarative (listing in YAML grants access)
    - Security: implement user approval controls

- url: https://github.com/microsoft/playwright-mcp
  sections:
    - "Microsoft Playwright MCP" - Official MCP implementation
  why: Specific MCP server implementation for browser automation
  critical_gotchas:
    - Uses accessibility trees, not pixel-based interactions
    - Fast and lightweight, LLM-friendly structured data
    - Supports headless or headed modes

# ESSENTIAL LOCAL FILES
- file: prps/playwright_agent_integration/examples/README.md
  why: Comprehensive guide with 6 extracted code examples
  pattern: Navigation → Interaction → Validation workflow
  critical: All examples are copy-paste ready, not pseudocode

- file: prps/playwright_agent_integration/examples/01_agent_tool_configuration.md
  why: YAML frontmatter pattern for adding browser tools to agents
  pattern: Comma-separated tool list in agent YAML header
  critical: Use short tool names (browser_navigate), not full MCP names

- file: prps/playwright_agent_integration/examples/02_browser_navigation_pattern.md
  why: Navigate and capture accessibility tree
  pattern: browser_navigate() → browser_snapshot() → validate tree
  critical: Always capture accessibility tree after navigation

- file: prps/playwright_agent_integration/examples/03_browser_interaction_pattern.md
  why: Interact with UI elements (click, type, fill form)
  pattern: Semantic queries (text-based, not refs)
  critical: Never hard-code element refs - use "button containing 'Upload'"

- file: prps/playwright_agent_integration/examples/04_browser_validation_pattern.md
  why: Validate UI state using accessibility tree
  pattern: Tree validation + proof screenshot
  critical: Agents validate via tree, humans verify via screenshot

- file: prps/playwright_agent_integration/examples/05_validation_loop_with_browser.md
  why: Integrate browser tests into multi-level validation
  pattern: Syntax → Tests → Integration → Browser validation
  critical: Same 5-attempt retry pattern for browser as backend

- file: prps/playwright_agent_integration/examples/06_browser_error_handling.md
  why: Handle browser-specific errors (not installed, frontend down, etc.)
  pattern: Pre-flight checks → Execute → Handle errors → Retry
  critical: Check frontend running before navigation

- file: .claude/agents/validation-gates.md
  why: Current agent configuration pattern
  pattern: YAML frontmatter with tools list
  critical: Follow exact format for tool declarations

- file: .claude/agents/prp-exec-validator.md
  why: Validation loop pattern with max 5 attempts
  pattern: For attempt in range(1, MAX_ATTEMPTS + 1): run → analyze → fix → retry
  critical: Same pattern applies to browser validation

- file: .claude/patterns/quality-gates.md
  why: Multi-level validation structure (syntax → unit → integration)
  pattern: Level 1 (fast) → Level 2 (medium) → Level 3 (slow)
  critical: Browser tests fit at Level 3 (integration tests)
```

### Current Codebase Tree

```
.claude/
├── agents/
│   ├── validation-gates.md           # MODIFY: Add browser tools
│   ├── prp-exec-validator.md         # MODIFY: Add browser tools
│   ├── prp-exec-implementer.md       # Optional: Add browser tools (post-MVP)
│   └── documentation-manager.md      # Optional: Add screenshot tool (post-MVP)
└── patterns/
    ├── quality-gates.md              # UPDATE: Add Level 3b browser section
    ├── archon-workflow.md            # No changes needed
    ├── parallel-subagents.md         # No changes needed
    └── README.md                     # UPDATE: Add browser-validation to index

prps/
├── playwright_agent_integration/
│   ├── planning/
│   │   ├── feature-analysis.md       # Read for requirements
│   │   ├── codebase-patterns.md      # Read for existing patterns
│   │   ├── documentation-links.md    # Read for documentation URLs
│   │   └── gotchas.md                # Read for all 12 gotchas
│   └── examples/
│       ├── README.md                 # Read for comprehensive examples
│       ├── 01_agent_tool_configuration.md
│       ├── 02_browser_navigation_pattern.md
│       ├── 03_browser_interaction_pattern.md
│       ├── 04_browser_validation_pattern.md
│       ├── 05_validation_loop_with_browser.md
│       └── 06_browser_error_handling.md
```

### Desired Codebase Tree

```
.claude/
├── agents/
│   ├── validation-gates.md           # MODIFIED: Browser tools added
│   ├── prp-exec-validator.md         # MODIFIED: Browser tools added
│   └── README.md                     # UPDATED: Document browser capability
└── patterns/
    ├── quality-gates.md              # UPDATED: Level 3b browser section
    ├── browser-validation.md         # NEW: Complete browser testing pattern
    └── README.md                     # UPDATED: Index browser-validation

README.md                             # MINOR UPDATE: Mention browser capability (optional)
CLAUDE.md                             # UPDATED: Browser testing guidance for agents

**New Files**:
- .claude/patterns/browser-validation.md - Complete browser testing pattern with examples
- .claude/agents/README.md - Agent documentation with browser testing guidance (if doesn't exist)
```

### Known Gotchas & Library Quirks

```python
# CRITICAL: Browser Binaries Not Installed (Gotcha #1)
# Playwright requires separate browser binary installation
# ❌ WRONG:
pip install playwright
# Then try: browser_navigate(url="...") → FAILS: "Browser not found"

# ✅ RIGHT:
pip install playwright
playwright install  # Downloads browser binaries (~300MB)
# For Docker/CI: playwright install --with-deps

# For MCP_DOCKER tool usage:
result = browser_install()  # Use this tool if browser not installed
# Wait 30-60 seconds, then proceed with navigation

# CRITICAL: Frontend Service Not Running (Gotcha #2)
# Navigation fails if docker-compose services aren't up
# ❌ WRONG:
browser_navigate(url="http://localhost:5173")  # FAILS: Connection refused

# ✅ RIGHT:
# Check service health first
result = Bash("docker-compose ps | grep rag-service")
if "Up" not in result.stdout:
    print("⚠️ Frontend not running, starting services...")
    Bash("docker-compose up -d")
    time.sleep(10)  # Wait for services to be healthy
browser_navigate(url="http://localhost:5173")

# CRITICAL: Thread Safety Violations (Gotcha #3)
# Playwright sync API is NOT thread-safe
# ❌ WRONG:
from concurrent.futures import ThreadPoolExecutor
playwright = sync_playwright().start()  # GLOBAL
browser = playwright.chromium.launch()
def validate(url):
    page = browser.new_page()  # SHARED - CRASHES
    page.goto(url)
with ThreadPoolExecutor(max_workers=4) as executor:
    executor.map(validate, urls)  # DEADLOCK

# ✅ RIGHT:
from multiprocessing import Pool
def validate(url):
    with sync_playwright() as p:  # SEPARATE INSTANCE PER PROCESS
        browser = p.chromium.launch()
        page = browser.new_page()
        page.goto(url)
        browser.close()
with Pool(processes=4) as pool:
    pool.map(validate, urls)  # SAFE

# CRITICAL: Element References Change Between Renders (Gotcha #4)
# Accessibility tree assigns refs like "e5" that change on every render
# ❌ WRONG:
snapshot = browser_snapshot()  # Returns: {"role": "button", "ref": "e5"}
browser_click(ref="e5")  # FAILS next render (ref changes to "e7")

# ✅ RIGHT:
browser_click(element="button containing 'Upload'")  # Semantic query
browser_click(element="Upload button")  # Natural language
page.get_by_role("button", name="Upload").click()  # Playwright API

# CRITICAL: Timeout Errors (Gotcha #5)
# Default timeouts may be too short for slow operations
# ❌ WRONG:
page.goto("http://localhost:5173")  # Default 30s
# Heavy API call takes 45s → TimeoutError

# ✅ RIGHT:
from playwright.sync_api import TimeoutError
context.set_default_timeout(60000)  # 60s for slow operations
page.goto("http://localhost:5173", timeout=10000)  # 10s for fast page
page.wait_for_selector(".upload-complete", timeout=15000)  # Explicit timeout

# With retry pattern:
def wait_with_retry(page, selector, max_attempts=3, timeout=5000):
    for attempt in range(max_attempts):
        try:
            page.wait_for_selector(selector, timeout=timeout)
            return True
        except TimeoutError:
            if attempt == max_attempts - 1:
                raise
            print(f"⚠️ Attempt {attempt + 1} failed, retrying...")
            time.sleep(1)
    return False

# CRITICAL: Agent Token Budget Exhaustion (Gotcha #6)
# Screenshots consume 4x more tokens than snapshots
# ❌ WRONG:
browser_navigate(url="http://localhost:5173")
screenshot = browser_take_screenshot(filename="validation.png")
# Agent cannot validate UI from screenshot (~2000 tokens, no value)

# ✅ RIGHT:
browser_navigate(url="http://localhost:5173")
snapshot = browser_snapshot()  # Structured JSON (~500 tokens)
# Agent can validate: "DocumentList" in snapshot
# Agent can check: snapshot["role"] == "main"

# ✅ ACCEPTABLE: One screenshot at end for human verification
# ... perform validation with snapshots ...
browser_take_screenshot(filename="validation-proof.png")
print("Screenshot saved for human review only")

# CRITICAL: Using Fixed Waits Instead of Auto-Wait (Gotcha #7)
# Manual sleep() makes tests slower and less reliable
# ❌ WRONG:
import time
page.goto("http://localhost:5173")
time.sleep(3)  # Arbitrary wait
page.click("#upload-button")
time.sleep(2)  # Another arbitrary wait

# ✅ RIGHT:
page.goto("http://localhost:5173")  # Auto-waits for page load
page.click("#upload-button")  # Auto-waits for element ready
page.wait_for_selector(".upload-complete", state="visible")  # Explicit condition

# CRITICAL: Not Managing Browser Context Lifecycle (Gotcha #8)
# Leaving browsers open causes memory leaks
# ❌ WRONG:
playwright = sync_playwright().start()
browser = playwright.chromium.launch()
page = browser.new_page()
# Script ends, browser still running

# ✅ RIGHT:
with sync_playwright() as p:
    with p.chromium.launch() as browser:
        with browser.new_page() as page:
            page.goto("http://localhost:5173")
# All cleaned up automatically

# CRITICAL: Testing Implementation Details (Gotcha #9)
# Tests should verify user-visible behavior, not CSS/DOM
# ❌ WRONG:
assert page.locator(".modal-open").is_visible()  # CSS class
assert page.locator("div > div > span").count() == 3  # DOM structure

# ✅ RIGHT:
expect(page.get_by_role("dialog")).to_be_visible()  # What user sees
expect(page.get_by_text("Upload successful")).to_be_visible()  # What user reads

# CRITICAL: MCP Tool Naming Confusion (Gotcha #10)
# Agent YAML uses short names, but full names when calling
# ❌ WRONG in YAML:
tools: Bash, Read, mcp__MCP_DOCKER__browser_navigate  # Full name

# ✅ RIGHT in YAML:
tools: Bash, Read, browser_navigate  # Short name (system adds prefix)

# In agent code, tool invocation automatically prefixes:
browser_navigate(url="...")  # Agent system resolves to mcp__MCP_DOCKER__browser_navigate

# CRITICAL: Port Conflicts (Gotcha #11)
# Wrong service may be running on expected port
# ❌ WRONG:
page.goto("http://localhost:5173")
# Could be different app if port conflict

# ✅ RIGHT:
page.goto("http://localhost:5173")
title = page.title()
if "RAG Service" not in title:
    raise AssertionError(f"Wrong service at port 5173. Got: {title}")

# CRITICAL: Mixing Sync and Async APIs (Gotcha #12)
# Don't mix Playwright sync and async APIs
# ❌ WRONG:
import asyncio
from playwright.sync_api import sync_playwright
async def test():
    with sync_playwright() as p:  # Sync API in async context
        page.goto("http://localhost:5173")  # Blocking call

# ✅ RIGHT:
import asyncio
from playwright.async_api import async_playwright
async def test():
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        page = await browser.new_page()
        await page.goto("http://localhost:5173")
```

---

## Implementation Blueprint

### Phase 0: Planning & Understanding

**BEFORE starting implementation, complete these steps:**

1. **Read ALL research documents**:
   - prps/playwright_agent_integration/planning/feature-analysis.md (requirements)
   - prps/playwright_agent_integration/planning/codebase-patterns.md (existing patterns)
   - prps/playwright_agent_integration/planning/documentation-links.md (all documentation URLs)
   - prps/playwright_agent_integration/planning/gotchas.md (all 12 gotchas with solutions)
   - prps/playwright_agent_integration/examples/README.md (comprehensive examples guide)

2. **Study all 6 code examples**:
   - 01_agent_tool_configuration.md - YAML frontmatter pattern
   - 02_browser_navigation_pattern.md - Navigate and capture state
   - 03_browser_interaction_pattern.md - Interact with UI elements
   - 04_browser_validation_pattern.md - Validate UI state
   - 05_validation_loop_with_browser.md - Multi-level validation
   - 06_browser_error_handling.md - Error patterns and recovery

3. **Understand critical concepts**:
   - This is configuration/documentation only (no code changes)
   - Browser tools already available via MCP_DOCKER
   - Accessibility tree over screenshots for agent validation
   - Semantic locators over element refs for resilience
   - Browser tests fit at Level 3 (Integration) in quality-gates

### Task List (Execute in Order)

```yaml
Task 1: Update validation-gates Agent Configuration
RESPONSIBILITY: Add browser tools to validation-gates agent for frontend UI validation
FILES TO MODIFY:
  - .claude/agents/validation-gates.md (lines 1-7)

PATTERN TO FOLLOW: Example 01_agent_tool_configuration.md

SPECIFIC STEPS:
  1. Read .claude/agents/validation-gates.md (current YAML frontmatter)
  2. Locate `tools:` field in YAML header
  3. Add browser tools to comma-separated list:
     - browser_navigate
     - browser_snapshot
     - browser_click
     - browser_type
     - browser_take_screenshot
     - browser_evaluate
     - browser_wait_for
     - browser_fill_form
     - browser_tabs
     - browser_install
  4. Update `description:` field to mention "frontend UI validation" capability
  5. Keep existing tools (Bash, Read, Edit, Grep, Glob, TodoWrite)
  6. Do NOT use full MCP names (mcp__MCP_DOCKER__*) in YAML - use short names only

VALIDATION:
  - YAML frontmatter still valid (check --- delimiters)
  - All tools on single line, comma-separated
  - Description updated to mention browser/UI capability
  - No duplicate tool names

Task 2: Update prp-exec-validator Agent Configuration
RESPONSIBILITY: Add browser tools to prp-exec-validator agent for full-stack validation
FILES TO MODIFY:
  - .claude/agents/prp-exec-validator.md (lines 1-6)

PATTERN TO FOLLOW: Example 01_agent_tool_configuration.md

SPECIFIC STEPS:
  1. Read .claude/agents/prp-exec-validator.md (current YAML frontmatter)
  2. Locate `tools:` field in YAML header
  3. Add same browser tools as Task 1 (see list above)
  4. Update `description:` field to mention "end-to-end UI validation" capability
  5. Keep existing tools (Bash, Read, Edit, Grep)
  6. Keep existing `color:` field if present

VALIDATION:
  - YAML frontmatter still valid
  - All tools on single line, comma-separated
  - Description updated appropriately
  - Color field preserved if present

Task 3: Create Browser Validation Pattern Document
RESPONSIBILITY: Document complete browser testing pattern with examples
FILES TO CREATE:
  - .claude/patterns/browser-validation.md (new file)

PATTERN TO FOLLOW: .claude/patterns/quality-gates.md structure

SPECIFIC STEPS:
  1. Create .claude/patterns/browser-validation.md
  2. Include these sections:
     - ## Overview: What browser validation is and why use it
     - ## Quick Reference: Common browser tool commands
     - ## Core Pattern: Navigation → Interaction → Validation
     - ## Rules (DO/DON'T): Best practices and anti-patterns
     - ## Integration with Quality Gates: How it fits at Level 3
     - ## Examples: Complete validation workflows
     - ## Gotchas: Top 12 gotchas with solutions
     - ## Error Patterns: Common errors and fixes
     - ## Pre-Flight Checks: Environment validation before tests
  3. Extract code examples from examples/ directory
  4. Include all 12 gotchas with solutions from gotchas.md
  5. Cross-reference quality-gates.md for multi-level validation
  6. Document accessibility tree approach (not screenshot approach)

VALIDATION:
  - Pattern structure matches quality-gates.md format
  - All code examples are copy-paste ready (not pseudocode)
  - Gotchas section has 12+ documented issues with fixes
  - Integration with quality-gates clearly explained
  - Examples cover navigation, interaction, validation, loops, errors

Task 4: Update Quality Gates Pattern
RESPONSIBILITY: Add browser testing as Level 3b in existing quality-gates pattern
FILES TO MODIFY:
  - .claude/patterns/quality-gates.md (add new section after Level 3)

PATTERN TO FOLLOW: Existing Level 1, 2, 3 structure

SPECIFIC STEPS:
  1. Read .claude/patterns/quality-gates.md (current structure)
  2. Find Level 3: Integration Tests section
  3. Add new subsection "Level 3b: Browser Integration Tests"
  4. Document when to use browser tests (user-facing features)
  5. Include example browser validation workflow
  6. Note performance considerations (10x slower than API)
  7. Reference browser-validation.md for detailed patterns
  8. Keep same 5-attempt max pattern

VALIDATION:
  - New section fits existing structure
  - Clear guidance on when to use browser vs API tests
  - Example workflow is complete and runnable
  - Cross-reference to browser-validation.md included

Task 5: Update Pattern Library Index
RESPONSIBILITY: Add browser-validation pattern to README index
FILES TO MODIFY:
  - .claude/patterns/README.md (add new entry)

PATTERN TO FOLLOW: Existing pattern index entries

SPECIFIC STEPS:
  1. Read .claude/patterns/README.md (current index)
  2. Add entry for browser-validation.md:
     - Name: "Browser Validation"
     - File: browser-validation.md
     - Description: "Browser automation patterns for frontend UI validation"
     - When to use: "Testing React frontends, validating user-facing features"
  3. Maintain alphabetical or logical ordering
  4. Keep same format as other entries

VALIDATION:
  - New entry follows existing format
  - File path is correct (browser-validation.md)
  - Description is clear and concise

Task 6: Update CLAUDE.md with Browser Testing Guidance
RESPONSIBILITY: Add browser testing section to agent guidance
FILES TO MODIFY:
  - CLAUDE.md (add new section)

PATTERN TO FOLLOW: Existing CLAUDE.md structure

SPECIFIC STEPS:
  1. Read CLAUDE.md (current structure)
  2. Add new section "Browser Testing for Agents"
  3. Include:
     - When to use browser validation vs API testing
     - How to invoke agents with browser tasks
     - Common browser validation workflows
     - Reference to browser-validation.md pattern
     - Key gotchas to remember
  4. Keep existing tone and format
  5. Add to appropriate location (after PRP section, before Pattern Library)

VALIDATION:
  - Section fits existing structure
  - Clear guidance for when to use browser testing
  - Example commands provided
  - Cross-references to patterns included

Task 7: Create Agent Documentation (if needed)
RESPONSIBILITY: Document browser testing capability in agent README
FILES TO CREATE/MODIFY:
  - .claude/agents/README.md (create if doesn't exist, update if exists)

PATTERN TO FOLLOW: Standard README structure

SPECIFIC STEPS:
  1. Check if .claude/agents/README.md exists
  2. If not exists: create with agent overview + browser capability section
  3. If exists: add browser testing section
  4. Include:
     - List of agents with browser tools
     - Example browser validation invocations
     - When to use browser validation
     - Common workflows
  5. Reference browser-validation.md for detailed patterns

VALIDATION:
  - README exists and is well-structured
  - Browser testing section is clear
  - Examples are complete
  - Cross-references to patterns

Task 8: End-to-End Validation Test
RESPONSIBILITY: Test agent browser validation with actual frontend
FILES TO MODIFY: None (testing only)

PATTERN TO FOLLOW: Example 05_validation_loop_with_browser.md

SPECIFIC STEPS:
  1. Start frontend services: `docker-compose up -d`
  2. Verify services running: `docker-compose ps | grep Up`
  3. Wait for health: `curl http://localhost:5173/health`
  4. Invoke validation-gates agent with browser task:
     `claude --agent validation-gates "Validate RAG service frontend at localhost:5173"`
  5. Verify agent:
     - Navigates to frontend successfully
     - Captures accessibility tree
     - Interacts with UI elements
     - Validates UI state
     - Takes screenshot for proof
     - Reports validation results
  6. Check validation report for browser test results
  7. Test with Task Manager: repeat for localhost:5174

VALIDATION:
  - Agent successfully accesses browser tools
  - Navigation works (no connection refused)
  - Accessibility tree captured and parsed
  - UI interactions succeed
  - Validation report includes browser results
  - Screenshots generated for proof

Task 9: Documentation Quality Check
RESPONSIBILITY: Ensure all documentation is complete, consistent, and cross-referenced
FILES TO REVIEW: All modified/created files

SPECIFIC STEPS:
  1. Verify all agent YAML frontmatter is valid
  2. Check all cross-references resolve (no broken links)
  3. Ensure code examples are consistent across documents
  4. Verify all 12 gotchas documented with solutions
  5. Check pattern library index is complete
  6. Test example commands are runnable
  7. Ensure terminology is consistent (e.g., "accessibility tree" not "accessibility snapshot")

VALIDATION:
  - No broken links or invalid references
  - All code examples are copy-paste ready
  - Gotchas have solutions documented
  - Terminology consistent across docs
  - Pattern library complete and indexed
```

### Implementation Pseudocode

```python
# Task 1 & 2: Agent Configuration Update Pattern
# DO NOT WRITE CODE - Just update YAML frontmatter in markdown files

# Current format (validation-gates.md):
"""
---
name: validation-gates
description: "Testing and validation specialist..."
tools: Bash, Read, Edit, MultiEdit, Grep, Glob, TodoWrite
---
"""

# Updated format:
"""
---
name: validation-gates
description: "Testing and validation specialist. Validates backend + frontend UI, ensures quality gates are met. Can perform browser automation for end-to-end testing."
tools: Bash, Read, Edit, MultiEdit, Grep, Glob, TodoWrite, browser_navigate, browser_snapshot, browser_click, browser_type, browser_take_screenshot, browser_evaluate, browser_wait_for, browser_fill_form, browser_tabs, browser_install
---
"""

# Key principles:
# - Add browser tools to END of existing tools list (preserve existing tools)
# - Update description to mention "frontend UI" or "browser automation"
# - Use short tool names (browser_navigate), NOT full MCP names
# - Keep all on single line, comma-separated

# Task 3: Browser Validation Pattern Structure
# Create .claude/patterns/browser-validation.md with this structure:

"""
# Browser Validation Pattern

## Overview
[What, why, when to use browser validation]

## Quick Reference
```bash
# Navigate to frontend
browser_navigate(url="http://localhost:5173")

# Capture accessibility tree
snapshot = browser_snapshot()

# Validate UI state
if "ExpectedElement" in snapshot:
    print("✅ Validation passed")
```

## Core Pattern: Navigation → Interaction → Validation

### Step 1: Navigate and Capture Initial State
[Example from 02_browser_navigation_pattern.md]

### Step 2: Interact with UI
[Example from 03_browser_interaction_pattern.md]

### Step 3: Validate Final State
[Example from 04_browser_validation_pattern.md]

## Rules

### DO:
- ✅ Use accessibility tree for validation (browser_snapshot)
- ✅ Use semantic locators ("button containing 'Upload'")
- ✅ Check frontend running before navigation
- ✅ Use auto-wait, not time.sleep()
- ✅ Take screenshots for human verification only

### DON'T:
- ❌ Use screenshots for agent validation (agents can't parse)
- ❌ Hard-code element refs (ref="e5" changes every render)
- ❌ Use CSS selectors (.class-name breaks on refactor)
- ❌ Skip service health checks
- ❌ Mix sync and async APIs

## Integration with Quality Gates

Browser validation fits at **Level 3: Integration Tests**:

```python
# Level 1: Syntax & Style (fast)
ruff check && mypy .

# Level 2: Unit Tests (medium)
pytest tests/unit/

# Level 3a: API Integration (medium)
pytest tests/integration/

# Level 3b: Browser Integration (slow)
# Agent-driven browser validation
validate_frontend_browser()
```

## Examples

### Example 1: Document Upload Validation
[Complete workflow from examples/README.md]

### Example 2: Task Creation Validation
[Adapted workflow for task manager]

### Example 3: Error Handling
[From 06_browser_error_handling.md]

## Gotchas

[Include all 12 gotchas from gotchas.md with solutions]

## Error Patterns

### "Connection refused"
**Cause**: Frontend not running
**Fix**: `docker-compose up -d && sleep 10`

### "Browser not found"
**Cause**: Browser binaries not installed
**Fix**: `browser_install()` or `playwright install`

[... all error patterns ...]

## Pre-Flight Checks

Before browser validation:
1. Check browser installed
2. Check frontend running
3. Check port available
4. Verify service identity

[Code example from 06_browser_error_handling.md]
"""

# Task 8: End-to-End Validation Test
# This is manual testing - no code to write
# Follow validation workflow:

def validate_browser_integration():
    """End-to-end test of browser validation capability."""

    # 1. Start services
    subprocess.run(["docker-compose", "up", "-d"])
    time.sleep(10)

    # 2. Verify services
    result = subprocess.run(["docker-compose", "ps"])
    assert "Up" in result.stdout

    # 3. Invoke agent with browser task
    subprocess.run([
        "claude", "--agent", "validation-gates",
        "Validate RAG service frontend at localhost:5173"
    ])

    # 4. Check validation report
    # - Look for browser navigation logs
    # - Verify accessibility tree captured
    # - Check UI interactions succeeded
    # - Confirm validation results present
    # - Find screenshot proof file

    # 5. Manual verification
    # - Open screenshot: validation-proof.png
    # - Verify UI looks correct
    # - Check validation report matches screenshot

# No actual code implementation needed - this is configuration/documentation only
```

---

## Validation Loop

### Level 1: YAML Syntax & Format Checks

```bash
# Validate YAML frontmatter in agent files
python -c "
import yaml
files = ['.claude/agents/validation-gates.md', '.claude/agents/prp-exec-validator.md']
for f in files:
    with open(f) as file:
        content = file.read()
        frontmatter = content.split('---')[1]
        yaml.safe_load(frontmatter)
        print(f'✅ {f} YAML valid')
"

# Check for common mistakes
grep -r "mcp__MCP_DOCKER__browser" .claude/agents/
# Should return NOTHING (agents should use short names)

# Check tools are comma-separated single line
grep "^tools:" .claude/agents/*.md
# Should show single line per agent
```

### Level 2: Documentation Completeness

```bash
# Check all required files exist
test -f .claude/patterns/browser-validation.md || echo "❌ Missing browser-validation.md"
test -f .claude/agents/validation-gates.md || echo "❌ Missing validation-gates.md"
test -f .claude/agents/prp-exec-validator.md || echo "❌ Missing prp-exec-validator.md"

# Verify pattern indexed
grep "browser-validation" .claude/patterns/README.md || echo "❌ Pattern not indexed"

# Check cross-references exist
grep "browser-validation.md" .claude/patterns/quality-gates.md || echo "⚠️ No cross-reference"
grep "browser-validation" CLAUDE.md || echo "⚠️ No guidance in CLAUDE.md"

# Verify all 12 gotchas documented
python -c "
with open('.claude/patterns/browser-validation.md') as f:
    content = f.read()
    gotcha_count = content.count('Gotcha #') + content.count('### Gotcha')
    if gotcha_count < 12:
        print(f'❌ Only {gotcha_count} gotchas documented (need 12)')
    else:
        print(f'✅ All {gotcha_count} gotchas documented')
"
```

### Level 3: Integration Tests

```bash
# Ensure frontend running
docker-compose up -d
docker-compose ps | grep "Up" || exit 1
sleep 10  # Wait for services healthy

# Test RAG service reachable
curl --fail http://localhost:5173/health || exit 1

# Test Task Manager reachable
curl --fail http://localhost:5174/health || exit 1

# Invoke agent with browser task (manual test)
echo "🧪 Testing validation-gates agent with browser task..."
echo "Run: claude --agent validation-gates 'Validate RAG service frontend at localhost:5173'"
echo "Expected: Agent navigates, captures tree, validates UI, takes screenshot"
echo "Check: Validation report includes browser test results"
echo "Verify: Screenshot file exists (validation-proof.png or similar)"

# Invoke prp-exec-validator (manual test)
echo "🧪 Testing prp-exec-validator agent with full-stack validation..."
echo "Run: claude --agent prp-exec-validator 'Run full-stack validation for RAG service'"
echo "Expected: Multi-level validation including browser tests at Level 3"
echo "Check: Browser validation runs after API tests pass"
echo "Verify: Final report includes all validation levels"
```

---

## Final Validation Checklist

Before marking complete, verify:

### Agent Configuration
- [ ] validation-gates.md has all browser tools in YAML frontmatter
- [ ] prp-exec-validator.md has all browser tools in YAML frontmatter
- [ ] Tool names are short form (browser_navigate), not full MCP names
- [ ] YAML frontmatter is valid (can be parsed)
- [ ] Agent descriptions mention browser/UI capability
- [ ] No duplicate tool names in lists

### Pattern Documentation
- [ ] browser-validation.md created with complete structure
- [ ] Pattern follows quality-gates.md format
- [ ] All 12 gotchas documented with solutions
- [ ] Code examples are copy-paste ready (not pseudocode)
- [ ] Integration with quality-gates explained
- [ ] Error patterns documented with fixes
- [ ] Pre-flight checks documented

### Integration Documentation
- [ ] quality-gates.md updated with Level 3b browser testing
- [ ] patterns/README.md indexes browser-validation pattern
- [ ] CLAUDE.md has browser testing guidance section
- [ ] agents/README.md documents browser capability
- [ ] All cross-references valid (no broken links)
- [ ] Consistent terminology across all docs

### Validation Testing
- [ ] Agent can be invoked with browser task
- [ ] Browser tools accessible during run
- [ ] Frontend navigation successful (no connection refused)
- [ ] Accessibility tree captured and parsed
- [ ] UI interactions working (click, type, fill)
- [ ] Validation results captured correctly
- [ ] Screenshots generated for proof

### Documentation Quality
- [ ] No broken links or invalid file paths
- [ ] Code examples consistent across documents
- [ ] All 12 gotchas have solutions documented
- [ ] Pattern library complete and indexed
- [ ] Example commands are runnable
- [ ] Terminology consistent (accessibility tree, not snapshot)

---

## Anti-Patterns to Avoid

### Configuration Anti-Patterns

❌ **Using Full MCP Tool Names in YAML**
```yaml
# WRONG:
tools: Bash, Read, mcp__MCP_DOCKER__browser_navigate
```
✅ **Use Short Names**
```yaml
# RIGHT:
tools: Bash, Read, browser_navigate
```

❌ **Multi-Line Tool Lists**
```yaml
# WRONG:
tools:
  - Bash
  - Read
  - browser_navigate
```
✅ **Single Line, Comma-Separated**
```yaml
# RIGHT:
tools: Bash, Read, browser_navigate
```

### Validation Anti-Patterns

❌ **Screenshots for Agent Validation**
```python
# WRONG: Agents can't parse images
screenshot = browser_take_screenshot("validation.png")
# Agent tries to validate from screenshot - fails
```
✅ **Accessibility Tree for Validation**
```python
# RIGHT: Agents parse structured data
snapshot = browser_snapshot()
if "ExpectedElement" in snapshot:
    print("✅ Validation passed")
```

❌ **Hard-Coded Element Refs**
```python
# WRONG: Refs change every render
browser_click(ref="e5")
```
✅ **Semantic Queries**
```python
# RIGHT: Text-based, stable
browser_click(element="button containing 'Upload'")
```

❌ **Skipping Pre-Flight Checks**
```python
# WRONG: Navigate without checking service
browser_navigate(url="http://localhost:5173")  # May fail
```
✅ **Check Service Health First**
```python
# RIGHT: Verify frontend running
ensure_frontend_running("http://localhost:5173")
browser_navigate(url="http://localhost:5173")
```

❌ **Using Fixed sleep() Calls**
```python
# WRONG: Arbitrary waits
page.goto("http://localhost:5173")
time.sleep(5)  # Too long or too short
```
✅ **Use Auto-Wait or Explicit Conditions**
```python
# RIGHT: Smart waiting
page.goto("http://localhost:5173")  # Auto-waits
page.wait_for_selector(".content", state="visible")
```

### Documentation Anti-Patterns

❌ **Pseudocode Instead of Real Examples**
```markdown
# WRONG:
// Navigate to page
browser_navigate(...)
// Do something
```
✅ **Copy-Paste Ready Code**
```markdown
# RIGHT:
browser_navigate(url="http://localhost:5173")
snapshot = browser_snapshot()
if "DocumentList" in snapshot:
    print("✅ Validation passed")
```

❌ **Documenting Without Gotchas**
```markdown
# WRONG:
## Browser Navigation
Use browser_navigate to navigate.
```
✅ **Include Gotchas and Solutions**
```markdown
# RIGHT:
## Browser Navigation
Use browser_navigate to navigate.

**Gotcha**: Connection refused if frontend not running
**Fix**: Check service health first:
```bash
docker-compose ps | grep Up
```

---

## Success Metrics

### Functional Success
- ✅ Agents can validate frontend UIs via browser automation
- ✅ Browser validation integrated into quality-gates pattern
- ✅ All 12 critical gotchas documented with solutions
- ✅ Complete browser validation pattern available in `.claude/patterns/`

### Quality Success
- ✅ All agent YAML frontmatter valid
- ✅ All code examples are runnable (not pseudocode)
- ✅ All documentation cross-references valid
- ✅ Pattern structure consistent with existing patterns

### Operational Success
- ✅ Agent can navigate to localhost:5173 and localhost:5174
- ✅ Agent can capture accessibility tree
- ✅ Agent can interact with UI elements
- ✅ Agent can validate UI state
- ✅ Validation reports include browser test results

---

## PRP Quality Self-Assessment

**Score: 9/10** - High confidence in one-pass implementation success

**Reasoning**:
- ✅ Comprehensive context: All 5 research docs thorough (788 lines feature analysis, 726 lines codebase patterns, 897 lines documentation, 805 lines examples guide, 1463 lines gotchas)
- ✅ Clear task breakdown: 9 well-defined tasks with validation criteria
- ✅ Proven patterns: 6 extracted code examples, all copy-paste ready
- ✅ Validation strategy: 3-level validation (YAML → Documentation → Integration)
- ✅ Error handling: 12 gotchas documented with solutions

**Deduction (-1 point) reasoning**:
- MCP_DOCKER specific tools lack official documentation (referenced in INITIAL but no official docs found)
- First-time browser setup may require manual intervention (browser_install timing)
- Agent testing is semi-manual (need to actually invoke agents and verify)

**Mitigations**:
- Test browser_install tool empirically during Task 8
- Document browser installation timing in browser-validation.md
- Provide clear validation checklist for manual testing steps
- Include debug patterns for common setup issues

**Strengths**:
1. **Configuration-only**: No code changes = low risk
2. **Comprehensive examples**: 6 copy-paste ready examples covering all scenarios
3. **Complete gotcha coverage**: All 12 critical gotchas with solutions
4. **Proven patterns**: All patterns extracted from production code
5. **Clear validation gates**: 3-level validation ensures quality

**Implementation Readiness**:
- All required documentation URLs included
- All local file paths provided
- All examples extracted and annotated
- All gotchas documented with solutions
- All validation commands provided
- Clear task ordering and dependencies

**Expected Implementation Time**: 2-3 hours
- Task 1-2 (Agent config): 30 minutes
- Task 3 (Browser pattern): 60 minutes
- Task 4-7 (Documentation): 30 minutes
- Task 8-9 (Testing): 30 minutes

**Risk Level**: Low
- No code changes (documentation only)
- Browser tools already available (MCP_DOCKER)
- Patterns proven in production (quality-gates, validation-gates)
- Comprehensive gotcha coverage reduces surprises

**Recommendation**: Proceed with implementation. PRP is comprehensive and implementation-ready.

