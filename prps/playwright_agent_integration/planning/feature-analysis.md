# Feature Analysis: Playwright Browser Tools Integration for Validation Agents

## INITIAL.md Summary

Enable validation and testing agents (`validation-gates` and `prp-exec-validator`) to perform full-stack validation including React UI testing by adding Playwright browser automation tool access. This extends their current backend-only validation capabilities to include end-to-end frontend testing using the MCP_DOCKER browser tools already available in the environment.

## Core Requirements

### Explicit Requirements

1. **Update Agent Tool Access**
   - Add Playwright browser tools to `validation-gates` agent tool list
   - Add Playwright browser tools to `prp-exec-validator` agent tool list
   - Tools to add: `browser_navigate`, `browser_snapshot`, `browser_click`, `browser_type`, `browser_take_screenshot`, `browser_evaluate`, `browser_wait_for`, `browser_fill_form`, `browser_tabs`, `browser_install`

2. **Update Agent Descriptions**
   - Modify agent descriptions to mention frontend/UI testing capabilities
   - Clarify when to use browser testing vs API testing
   - Add browser automation as core capability

3. **Document Browser Validation Patterns**
   - Create browser validation pattern in `.claude/patterns/`
   - Document full-stack testing workflow
   - Add screenshot assertion patterns
   - Include accessibility tree usage guidance

4. **Update Agent Documentation**
   - Update `.claude/agents/README.md` (if exists) with browser testing guidance
   - Add example browser validation workflows
   - Document when to use browser tools vs API testing

5. **Optionally Extend to Other Agents**
   - Consider adding browser tools to `prp-exec-implementer` (medium priority)
   - Consider adding to `documentation-manager` for UI screenshots (medium priority)
   - Skip for PRP generation agents (not needed)

### Implicit Requirements

1. **Maintain Backward Compatibility**
   - Existing validation workflows must continue to work
   - Browser tools are additive, not replacing existing tools
   - Agents should gracefully handle browser unavailability

2. **Integration with Existing Patterns**
   - Browser validation should fit into existing quality-gates pattern
   - Should work with parallel-subagents pattern
   - Must align with validation loop pattern (max 5 attempts)

3. **Performance Considerations**
   - Browser operations are slower than API calls
   - Document when browser testing is appropriate
   - Prefer accessibility snapshots over screenshots for efficiency

4. **Error Handling**
   - Handle browser not installed scenario
   - Handle frontend not running scenario
   - Handle element reference changes
   - Document all error patterns and fixes

5. **Documentation Standards**
   - Follow existing agent markdown format
   - Maintain consistency with other agent descriptions
   - Use same tool naming conventions

## Technical Components

### Data Models

**No new data models required** - This is purely configuration/documentation update:
- Agent markdown files (YAML frontmatter + markdown content)
- Pattern documentation (markdown)
- README updates (markdown)

### External Integrations

1. **MCP_DOCKER Server** (Already Available)
   - Tool prefix: `mcp__MCP_DOCKER__browser_*`
   - Browser automation via Playwright
   - No additional installation needed in environment
   - May need browser installation first time (use `browser_install` tool)

2. **Frontend Services** (Already Deployed)
   - RAG Service UI: `http://localhost:5173`
   - Task Manager UI: `http://localhost:5174`
   - Require `docker-compose up` to be running

### Core Logic

**No code changes required** - This feature is purely configuration/documentation:

1. **Agent Configuration Updates**
   - Modify YAML frontmatter `tools:` field
   - Add browser tool names to list
   - Update description text

2. **Pattern Documentation**
   - Create new browser-validation.md pattern
   - Document navigation → interaction → validation workflow
   - Include example code snippets

3. **Agent Instruction Updates**
   - Add browser testing examples to agent bodies
   - Document browser tool usage patterns
   - Add gotchas and best practices

### UI/CLI Requirements

**No UI/CLI changes** - Agents are invoked via existing mechanisms:
- `claude --agent validation-gates "Validate RAG service frontend"`
- `claude --agent prp-exec-validator "Run full-stack validation"`
- No new commands or interfaces needed

## Similar Implementations Found in Archon

### 1. Agent Tool Configuration Pattern
- **Relevance**: 9/10
- **Archon Source**: Multiple AI agent frameworks documentation
- **Key Patterns**:
  - Tools defined in YAML frontmatter as comma-separated list
  - Tool access declarative, not imperative
  - Tool names follow `mcp__{server}__{tool}` convention
- **Example from codebase**:
  ```yaml
  ---
  name: validation-gates
  tools: Bash, Read, Edit, MultiEdit, Grep, Glob, TodoWrite
  ---
  ```
- **Application**: Same pattern for browser tools - just add to comma-separated list
- **Gotchas**: Tool names are case-sensitive, must match exact MCP server export

### 2. Multi-Level Validation Pattern (quality-gates.md)
- **Relevance**: 10/10
- **Location**: `/Users/jon/source/vibes/.claude/patterns/quality-gates.md`
- **Key Patterns**:
  - Level 1: Syntax & Style (fast checks)
  - Level 2: Unit Tests
  - Level 3: Integration Tests
  - Level 4: Performance Tests (optional)
  - Max 5 attempts per level
- **Application**: Browser testing fits at Level 3 (Integration Tests)
- **Gotchas**: Browser tests are slower - should be last in integration suite

### 3. Validation Loop with Fix Iterations (prp-exec-validator.md)
- **Relevance**: 10/10
- **Location**: `/Users/jon/source/vibes/.claude/agents/prp-exec-validator.md`
- **Key Patterns**:
  ```python
  for attempt in range(1, MAX_ATTEMPTS + 1):
      result = run_validation(level, commands)
      if result.success:
          break
      # Parse errors, check PRP gotchas, apply fix
      error_analysis = analyze_error(result.error, prp_gotchas)
      apply_fix(error_analysis)
  ```
- **Application**: Same pattern for browser validation failures
- **Gotchas**: Browser errors often timeout-related - need specific error patterns

### 4. CI/CD Agent Tool Integration (Claude Code Documentation)
- **Relevance**: 7/10
- **Archon Source**: Claude Code GitLab/GitHub Actions documentation
- **Key Patterns**:
  - Specify allowed tools in agent invocation
  - Tools must be available in environment
  - Graceful degradation when tools unavailable
- **Application**: Document browser tool availability requirements
- **Gotchas**: MCP_DOCKER server must be running, browser may need installation

### 5. Frontend Validation Examples (RAG Service PRP)
- **Relevance**: 8/10
- **Location**: `/Users/jon/source/vibes/prps/rag_service_research.md`
- **Key Patterns**:
  - Frontend runs on localhost:5173
  - Requires docker-compose up
  - React component testing via UI interaction
- **Application**: Same pattern for browser validation examples
- **Gotchas**: Port conflicts if multiple frontends, services must be healthy

## Recommended Technology Stack

**No new technology stack required** - Using existing tools:

### Browser Automation
- **Tool**: MCP_DOCKER browser tools (Playwright-based)
- **Why**: Already integrated in environment, no installation needed
- **Documentation**: Playwright API docs (https://playwright.dev/python/docs/api/class-playwright)

### Agent Configuration
- **Format**: YAML frontmatter + Markdown
- **Why**: Existing agent format, no changes needed
- **Pattern**: Same as existing agents in `.claude/agents/`

### Pattern Documentation
- **Format**: Markdown
- **Location**: `.claude/patterns/browser-validation.md`
- **Why**: Consistent with existing patterns (quality-gates, parallel-subagents, archon-workflow)

### Testing Approach
- **Backend Tests**: Continue using pytest, ruff, mypy (no change)
- **Frontend Tests**: Add browser automation via Playwright tools
- **Integration**: Both within same validation loop

## Assumptions Made

### 1. **MCP_DOCKER Server Availability**
   - **Assumption**: MCP_DOCKER server is configured and running in vibes environment
   - **Reasoning**: INITIAL.md references MCP_DOCKER tools, implies setup already complete
   - **Source**: INITIAL.md line 27-38 lists available tools
   - **Risk**: Low - documented in INITIAL
   - **Validation**: Check MCP server config, test tool invocation

### 2. **Browser Installation Handled**
   - **Assumption**: Either browser is pre-installed OR `browser_install` tool will handle it
   - **Reasoning**: Playwright requires browser binaries, tool provided for installation
   - **Source**: INITIAL.md line 38 mentions `browser_install` tool
   - **Risk**: Medium - first-time setup may need manual intervention
   - **Validation**: Document browser installation process in pattern

### 3. **Frontend Services Deployable**
   - **Assumption**: RAG service (5173) and Task Manager (5174) can be deployed via docker-compose
   - **Reasoning**: INITIAL.md references these ports, existing PRP docs show docker-compose usage
   - **Source**: INITIAL.md lines 43-65, RAG service PRP docker-compose patterns
   - **Risk**: Low - documented in project
   - **Validation**: Add prerequisite check to browser validation pattern

### 4. **Accessibility Tree Sufficient for Validation**
   - **Assumption**: Agents can validate UI via accessibility tree (`browser_snapshot`), don't need visual parsing
   - **Reasoning**: INITIAL.md line 211-215 notes "Agents cannot see visual screenshots directly"
   - **Source**: INITIAL.md "Agent Limitations" section
   - **Risk**: Low - accessibility tree is structured data suitable for agents
   - **Validation**: Prefer browser_snapshot over browser_take_screenshot in examples

### 5. **No Changes to Agent Invocation**
   - **Assumption**: Existing agent invocation mechanism automatically grants access to listed tools
   - **Reasoning**: Current agents work with their tool lists, adding tools should work same way
   - **Source**: Pattern from existing agent configurations
   - **Risk**: Low - declarative tool access is standard
   - **Validation**: Test agent invocation after config update

### 6. **Two Agents Sufficient for MVP**
   - **Assumption**: Updating `validation-gates` and `prp-exec-validator` is sufficient for initial release
   - **Reasoning**: INITIAL.md marks these as "High Priority", others as "Medium/Low Priority"
   - **Source**: INITIAL.md lines 92-106 "Agents to Update"
   - **Risk**: Low - can iterate on other agents later
   - **Validation**: User feedback after initial deployment

### 7. **Pattern Library Structure Stable**
   - **Assumption**: Adding `browser-validation.md` to `.claude/patterns/` follows established pattern
   - **Reasoning**: Existing patterns directory has quality-gates, parallel-subagents, archon-workflow
   - **Source**: Codebase `/Users/jon/source/vibes/.claude/patterns/`
   - **Risk**: Very Low - directory exists and documented
   - **Validation**: Follow same structure as quality-gates.md

### 8. **No Agent Code Changes**
   - **Assumption**: Agents receive tools via configuration, no prompt/code changes needed internally
   - **Reasoning**: Tools are provided via MCP, agents use them via function calling
   - **Source**: Best practice from 12-factor-agents, MCP protocol design
   - **Risk**: Very Low - tool access is declarative
   - **Validation**: Test agent with new tools, verify function calling works

## Success Criteria

### Phase 1: Agent Configuration Updates (validation-gates)
- ✅ `validation-gates.md` updated with browser tools in YAML frontmatter
- ✅ Agent description mentions "frontend UI validation" capability
- ✅ Example browser validation workflow added to agent body
- ✅ Agent can be invoked with browser validation task
- ✅ Browser tools accessible during validation run

### Phase 2: Agent Configuration Updates (prp-exec-validator)
- ✅ `prp-exec-validator.md` updated with browser tools in YAML frontmatter
- ✅ Agent description mentions "end-to-end UI validation" capability
- ✅ UI validation loop pattern documented
- ✅ Screenshot capture pattern included for proof of validation
- ✅ Agent can run full-stack validation with browser steps

### Phase 3: Pattern Documentation
- ✅ `browser-validation.md` created in `.claude/patterns/`
- ✅ Navigation → Interaction → Validation workflow documented
- ✅ Code examples for browser tool usage included
- ✅ Gotchas and error patterns documented
- ✅ Integration with quality-gates pattern explained

### Phase 4: Integration Documentation
- ✅ `.claude/agents/README.md` updated (if exists) with browser testing guidance
- ✅ Clear guidance on when to use browser vs API testing
- ✅ Browser tool availability requirements documented
- ✅ Example validation commands provided
- ✅ Integration with existing patterns documented

### Validation Tests
- ✅ Invoke `validation-gates` agent with RAG service frontend validation task
- ✅ Agent successfully navigates to localhost:5173
- ✅ Agent captures accessibility tree snapshot
- ✅ Agent interacts with UI elements (click, type)
- ✅ Agent validates UI state changes
- ✅ Agent takes screenshot for human verification
- ✅ Validation report includes browser test results

### Quality Metrics
- **Documentation completeness**: 100% (all 4 phases complete)
- **Pattern consistency**: Matches existing pattern structure
- **Example coverage**: 3+ browser validation examples
- **Gotcha documentation**: 5+ known issues documented
- **Integration clarity**: Works with quality-gates, parallel-subagents patterns

## Next Steps for Downstream Agents

### Codebase Researcher
**Focus Areas**:
1. Search for existing frontend validation patterns in PRPs
   - Query: `Grep "localhost:5173|localhost:5174" glob="*.md"`
   - Identify validation approaches already documented
2. Find agent configuration examples
   - Read all files in `.claude/agents/` for pattern consistency
   - Extract tool list formatting conventions
3. Locate MCP_DOCKER documentation
   - Search for MCP server configuration files
   - Document browser tool parameters and return types

**Expected Findings**:
- RAG service and Task Manager PRP docs with frontend references
- Consistent agent YAML frontmatter pattern across 12 agents
- MCP_DOCKER tool documentation or examples

### Documentation Hunter
**Focus Areas**:
1. **Playwright Documentation**
   - Find: Python API docs, accessibility testing guides
   - URLs: Already provided in INITIAL (https://playwright.dev/)
   - Extract: Navigation, interaction, assertion patterns
2. **MCP Protocol Documentation**
   - Find: Tool invocation patterns, error handling
   - Context: How agents call MCP tools, parameter passing
3. **Browser Testing Best Practices**
   - Find: When to use E2E tests, performance considerations
   - Context: Balance between API and browser testing

**Expected Deliverables**:
- 5+ documentation links for browser testing
- Best practices document for browser vs API testing
- Error handling patterns from Playwright docs

### Example Curator
**Focus Areas**:
1. **Browser Navigation Examples**
   ```python
   browser_navigate(url="http://localhost:5173")
   snapshot = browser_snapshot()
   # Parse accessibility tree for validation
   ```
2. **UI Interaction Examples**
   ```python
   browser_click(element="Upload button", ref="e5")
   browser_fill_form(fields=[...])
   browser_wait_for(text="Upload successful")
   ```
3. **Validation Examples**
   ```python
   browser_take_screenshot(filename="proof.png")
   result = browser_evaluate(function="() => ...")
   ```
4. **Error Handling Examples**
   - Browser not installed → Use browser_install
   - Element not found → Wait with timeout
   - Frontend not running → Check docker-compose

**Expected Deliverables**:
- 3+ complete browser validation workflows
- Error handling examples for each gotcha
- Integration with existing validation loop pattern

### Gotcha Detective
**Focus Areas**:
1. **Browser Availability Gotchas**
   - Browser binaries not installed
   - MCP_DOCKER server not running
   - Browser installation requires permissions
2. **Frontend Availability Gotchas**
   - Services not running (docker-compose down)
   - Port conflicts (5173/5174 already in use)
   - Health check failures before testing
3. **Element Reference Gotchas**
   - Accessibility tree references change between renders
   - Use semantic queries (text, role) not ref numbers
   - Wait for elements with explicit timeouts
4. **Performance Gotchas**
   - Browser operations 10x slower than API calls
   - Screenshots consume large token budget
   - Prefer accessibility snapshots for validation
5. **Agent Limitation Gotchas**
   - Agents cannot parse visual screenshots directly
   - Must use accessibility tree (structured data)
   - Screenshots for human verification only

**Expected Deliverables**:
- 5-10 documented gotchas with fixes
- Error patterns and detection strategies
- Mitigation approaches for each gotcha

## File Changes Required

### Agent Files (`.claude/agents/`)

**High Priority**:
1. **validation-gates.md** - Add browser tools, update description, add examples
2. **prp-exec-validator.md** - Add browser tools, add UI validation patterns

**Medium Priority** (Post-MVP):
3. **prp-exec-implementer.md** - Add browser tools for self-validation
4. **documentation-manager.md** - Add browser tools for UI screenshots

**No Changes Needed**:
- All `prp-gen-*` agents (research/generation only)
- Task analyzer, test generator (no UI validation)

### Pattern Files (`.claude/patterns/`)

**New Files**:
1. **browser-validation.md** - NEW: Complete browser testing pattern
   - Navigation workflow
   - Interaction patterns
   - Validation strategies
   - Error handling
   - Integration with quality-gates

**Updated Files**:
2. **quality-gates.md** - UPDATE: Add Level 3 browser testing section
3. **README.md** - UPDATE: Add browser-validation to pattern index

### Documentation Files

**Root Documentation**:
1. **README.md** - MINOR UPDATE: Mention browser testing capability (optional)
2. **CLAUDE.md** - ADD SECTION: Browser testing guidance for agents

**Agent Documentation** (if exists):
3. **.claude/agents/README.md** - CREATE/UPDATE: Browser testing guidance

## Integration with Existing Patterns

### Works With: quality-gates.md
**Integration Point**: Level 3 - Integration Tests
```markdown
## Level 3: Integration Tests

### API Integration Tests
```bash
pytest tests/integration/ -v
```

### Frontend Integration Tests (NEW)
```bash
# Invoke validation-gates agent with browser validation task
claude --agent validation-gates "Validate RAG service frontend at localhost:5173"
```

**Validation Loop**: Same max 5 attempts pattern applies to browser tests
**Error Analysis**: Check PRP gotchas for browser-specific issues
```

### Works With: parallel-subagents.md
**Integration Point**: Browser tests can run in parallel with API tests
```markdown
## Example: Parallel Validation

Can invoke multiple validation agents simultaneously:
- validation-gates → Backend API tests
- validation-gates → Frontend browser tests
- validation-gates → Integration smoke tests

**Benefit**: 3x speedup when browser and API tests independent
**Caveat**: Ensure frontend is running before parallel browser tests
```

### Works With: archon-workflow.md
**Integration Point**: Task tracking for validation phases
```markdown
## Validation Task Tracking

Before browser validation:
1. Update task status: "doing"
2. Run browser validation commands
3. Document results in Archon
4. Update task status: "review" or "done"

**Archon Integration**: Browser validation results stored as task notes
**Benefit**: Full audit trail of UI validation history
```

## Updates Needed to Existing Patterns

### quality-gates.md
**Section to Add**: "Level 3b: Browser Integration Tests"
**Content**:
- When to use browser tests (user-facing features)
- Performance considerations (slower than API)
- Error patterns (browser not available, frontend not running)
- Integration with validation loop (same 5 attempt max)

### INITIAL Template (for future PRPs)
**Section to Add**: Frontend validation option in success criteria
**Example**:
```markdown
## Success Criteria

### Functional Requirements
- [ ] Backend API endpoints return correct data
- [ ] Frontend UI displays data correctly (browser validation)
- [ ] User interactions trigger expected state changes
```

### PRP Template Base
**Section to Add**: Browser validation commands in validation loop
**Example**:
```markdown
### Level 3: Integration Tests

#### API Integration
```bash
pytest tests/integration/ -v
```

#### Frontend Integration (if UI feature)
```bash
# Agent-driven browser validation
claude --agent validation-gates "Validate {feature} UI at localhost:{port}"
```
```

## Risk Mitigation

### High Risk Areas

#### 1. Browser Not Installed
**Risk Level**: High
**Impact**: Validation fails immediately, blocks testing
**Likelihood**: Medium (fresh environments, CI/CD)

**Mitigation**:
- Document `browser_install` tool usage prominently
- Add prerequisite check to pattern documentation
- Provide error pattern for detection
- Include fix command in gotchas

**Validation**:
- Test on fresh environment (no browser pre-installed)
- Verify browser_install tool works
- Document installation time (30-60 seconds)

**Reference**: MCP_DOCKER browser tools documentation

#### 2. Frontend Not Running
**Risk Level**: High
**Impact**: Navigation fails, all browser tests fail
**Likelihood**: Medium (forgot docker-compose up)

**Mitigation**:
- Document prerequisite: `docker-compose up -d` before validation
- Add health check step to validation workflow
- Provide error pattern for connection refused
- Include docker-compose commands in gotchas

**Validation**:
- Test with services down
- Verify error message is clear
- Check health endpoint before browser tests

**Reference**: RAG service PRP docker-compose patterns

#### 3. Element References Change
**Risk Level**: Medium
**Impact**: Browser interactions fail, validation flaky
**Likelihood**: High (React re-renders change tree)

**Mitigation**:
- Use semantic queries (text, role) not ref numbers
- Document in pattern: "Never hard-code ref='e5'"
- Add wait strategies for dynamic content
- Test with multiple UI states

**Validation**:
- Test same validation twice (element refs will differ)
- Verify semantic queries work consistently

**Reference**: Playwright accessibility testing docs

#### 4. Agent Token Budget
**Risk Level**: Medium
**Impact**: Validation incomplete, costs increase
**Likelihood**: Low (only if excessive screenshots)

**Mitigation**:
- Limit screenshot usage (critical validations only)
- Prefer accessibility snapshots (more efficient)
- Document in pattern: "Screenshots for humans, snapshots for agents"
- Monitor token consumption

**Validation**:
- Count tokens for browser_snapshot vs browser_take_screenshot
- Compare efficiency (snapshot ~500 tokens, screenshot ~2000)

**Reference**: Claude token usage documentation

### Medium Risk Areas

#### 5. Port Conflicts
**Risk Level**: Medium
**Impact**: Frontend unavailable on expected port
**Likelihood**: Low (controlled environment)

**Mitigation**: Document expected ports, check docker-compose config

#### 6. Performance Degradation
**Risk Level**: Low
**Impact**: Validation takes longer (10x slower than API tests)
**Likelihood**: High (browser inherently slow)

**Mitigation**: Document performance expectations, reserve browser tests for critical paths

### Low Risk Areas

#### 7. MCP_DOCKER Server Down
**Risk Level**: Low
**Impact**: All browser tools unavailable
**Likelihood**: Very Low (managed service)

**Mitigation**: Document MCP server health check, provide restart instructions

## Archon Project Tracking

**Project ID**: 61b423b5-8938-4fde-a781-b21313cac863
**Feature Name**: playwright_agent_integration
**Status**: Planning Complete → Ready for Implementation

### Archon Task Recommendations

**Task 1**: Update validation-gates agent configuration
- **Subtasks**: Add tools to YAML, update description, add examples
- **Estimated Time**: 30 minutes
- **Validation**: Test agent invocation with browser task

**Task 2**: Update prp-exec-validator agent configuration
- **Subtasks**: Add tools to YAML, add UI validation patterns
- **Estimated Time**: 30 minutes
- **Validation**: Test full-stack validation loop

**Task 3**: Create browser-validation.md pattern
- **Subtasks**: Document workflow, add examples, list gotchas
- **Estimated Time**: 60 minutes
- **Validation**: Pattern structure matches quality-gates.md

**Task 4**: Update integration documentation
- **Subtasks**: Update pattern README, update CLAUDE.md
- **Estimated Time**: 30 minutes
- **Validation**: Documentation complete and consistent

**Task 5**: End-to-end validation test
- **Subtasks**: Test RAG service validation, test Task Manager validation
- **Estimated Time**: 45 minutes
- **Validation**: Both frontends validated successfully

**Total Estimated Time**: 3 hours 15 minutes

## Quality Assurance Checklist

Before marking feature complete, verify:

### Agent Configuration
- ✅ Both agents have complete browser tool list
- ✅ Tool names match MCP_DOCKER exports exactly
- ✅ YAML frontmatter valid and parseable
- ✅ Agent descriptions updated accurately
- ✅ Examples provided for browser validation

### Pattern Documentation
- ✅ browser-validation.md follows existing pattern structure
- ✅ Code examples are copy-paste ready
- ✅ Gotchas section has 5+ documented issues
- ✅ Integration with quality-gates explained
- ✅ Pattern indexed in README.md

### Integration Documentation
- ✅ CLAUDE.md updated with browser testing guidance
- ✅ Clear guidance on when to use browser vs API tests
- ✅ Prerequisites documented (docker-compose, browser install)
- ✅ Example commands provided
- ✅ Error patterns documented

### Validation Testing
- ✅ Agent invocable with browser task
- ✅ Browser tools accessible during run
- ✅ Frontend navigation successful
- ✅ UI interaction working
- ✅ Validation results captured correctly

### Documentation Quality
- ✅ No broken links
- ✅ Consistent formatting
- ✅ Code blocks have language tags
- ✅ Examples are complete (not pseudocode)
- ✅ Cross-references accurate

## Appendix: Tool Reference

### MCP_DOCKER Browser Tools (Available)

| Tool Name | Purpose | Key Parameters | Returns |
|-----------|---------|----------------|---------|
| `browser_navigate` | Navigate to URL | `url: string` | Page load confirmation |
| `browser_snapshot` | Accessibility tree | None | Structured tree (JSON) |
| `browser_click` | Click element | `element: string, ref: string` | Click confirmation |
| `browser_type` | Type text | `text: string, element: string` | Type confirmation |
| `browser_take_screenshot` | Visual capture | `filename: string` | File path |
| `browser_evaluate` | Run JavaScript | `function: string` | Function result |
| `browser_fill_form` | Fill multiple fields | `fields: array` | Fill confirmation |
| `browser_wait_for` | Wait for condition | `text: string, timeout: number` | Wait confirmation |
| `browser_tabs` | Manage tabs | `action: string` | Tab list/switch |
| `browser_install` | Install browser | None | Install confirmation |

### Recommended Tool Usage Patterns

**Navigation Pattern**:
```python
# 1. Navigate to frontend
browser_navigate(url="http://localhost:5173")

# 2. Capture initial state
initial_state = browser_snapshot()

# 3. Verify page loaded
assert "DocumentList" in initial_state  # Check for expected component
```

**Interaction Pattern**:
```python
# 1. Click element (semantic query)
browser_click(element="button containing 'Upload'")

# 2. Fill form fields
browser_fill_form(fields=[
    {"name": "title", "value": "Test Document"},
    {"name": "file", "value": "/path/to/test.pdf"}
])

# 3. Wait for result
browser_wait_for(text="Upload successful", timeout=5000)
```

**Validation Pattern**:
```python
# 1. Capture final state
final_state = browser_snapshot()

# 2. Verify expected elements present
assert "Test Document" in final_state

# 3. Take proof screenshot (optional, for humans)
browser_take_screenshot(filename="validation-proof.png")
```

**Error Recovery Pattern**:
```python
# 1. Try navigation
try:
    browser_navigate(url="http://localhost:5173")
except ConnectionError:
    # 2. Check if frontend running
    result = Bash("docker-compose ps | grep rag-service")
    if "Up" not in result.stdout:
        # 3. Start services
        Bash("docker-compose up -d")
        # 4. Wait for health
        browser_wait_for(timeout=10000)
        # 5. Retry navigation
        browser_navigate(url="http://localhost:5173")
```

---

## Summary

This feature adds browser automation capabilities to validation agents through configuration updates only - no code changes required. By adding MCP_DOCKER browser tools to agent tool lists and documenting usage patterns, we enable full-stack validation (backend + frontend) within the existing validation workflow. The implementation is low-risk, follows established patterns, and provides immediate value for validating React frontends in RAG service and Task Manager projects.

**Key Insight**: Browser testing capability unlocks true end-to-end validation, ensuring not just that APIs work, but that users can actually accomplish tasks in the UI.

**Next Action**: Proceed to implementation phase with codebase researcher, documentation hunter, example curator, and gotcha detective working in parallel to gather patterns and examples for PRP assembly.
