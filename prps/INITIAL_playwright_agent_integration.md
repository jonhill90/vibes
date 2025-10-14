# INITIAL: Playwright Browser Tools Integration for Validation Agents

## FEATURE

Update validation and testing agents to have access to Playwright browser tools for end-to-end frontend testing and validation.

**Core Goal**: Enable `validation-gates` and `prp-exec-validator` agents to perform full-stack validation including React UI testing, not just backend API testing.

**Output**: Updated agent configurations with Playwright tools access and validation patterns that include browser automation.

## EXAMPLES

### Current Agent Limitations

**validation-gates agent** (`.claude/agents/validation-gates.md`):
- Currently has: Bash, Read, Edit, MultiEdit, Grep, Glob, TodoWrite
- **Missing**: Browser automation tools
- **Impact**: Cannot validate frontend UI, only backend/API

**prp-exec-validator agent** (`.claude/agents/prp-exec-validator.md`):
- Currently has: Bash, Read, Edit, Grep
- **Missing**: Browser automation tools
- **Impact**: Cannot run end-to-end UI validation loops

### Playwright Tools Available

From MCP_DOCKER server:
```
mcp__MCP_DOCKER__browser_navigate       - Navigate to URLs
mcp__MCP_DOCKER__browser_snapshot       - Capture accessibility tree
mcp__MCP_DOCKER__browser_take_screenshot - Visual screenshots
mcp__MCP_DOCKER__browser_click          - Click UI elements
mcp__MCP_DOCKER__browser_type           - Type text input
mcp__MCP_DOCKER__browser_evaluate       - Run JavaScript
mcp__MCP_DOCKER__browser_fill_form      - Fill multiple form fields
mcp__MCP_DOCKER__browser_wait_for       - Wait for conditions
mcp__MCP_DOCKER__browser_tabs           - Manage browser tabs
mcp__MCP_DOCKER__browser_install        - Install browser if needed
```

### Example Validation Scenarios

**RAG Service Frontend Validation** (infra/rag-service):
```markdown
1. Navigate to http://localhost:5173
2. Verify DocumentList component renders
3. Click "Upload Document" button
4. Fill form with test PDF
5. Wait for upload success message
6. Navigate to Search page
7. Type "test query" in SearchBar
8. Verify SearchResults component shows results
9. Take screenshot for visual verification
```

**Task Manager Frontend Validation** (infra/task-manager):
```markdown
1. Navigate to http://localhost:5174
2. Click "Create Task" button
3. Fill form: title="Test Task", description="Testing"
4. Submit form
5. Wait for task to appear in list
6. Verify task card displays correctly
7. Take screenshot
```

## DOCUMENTATION

### Agent Configuration Pattern

**Tool Access in Agent Markdown**:
```markdown
Available agent types and the tools they have access to:
- validation-gates: Testing and validation specialist. (Tools: Bash, Read, Edit, MultiEdit, Grep, Glob, TodoWrite, **browser_navigate, browser_snapshot, browser_click, browser_type, browser_take_screenshot, browser_evaluate, browser_wait_for**)
```

### Playwright Documentation

**Playwright for Testing**:
- Docs: https://playwright.dev/
- Python API: https://playwright.dev/python/docs/api/class-playwright
- Assertions: https://playwright.dev/python/docs/test-assertions
- Accessibility snapshots: https://playwright.dev/docs/accessibility-testing

**MCP Browser Tools**:
- Already integrated via MCP_DOCKER server
- No additional installation needed
- Access via `mcp__MCP_DOCKER__browser_*` tools

## OTHER CONSIDERATIONS

### Agents to Update

**High Priority** (validation/testing agents):
1. **validation-gates** - Runs tests, validates code changes, quality gates
2. **prp-exec-validator** - Systematic validation with fix loops
3. **prp-exec-implementer** - May need to validate own implementations

**Medium Priority** (could benefit from browser access):
4. **documentation-manager** - Could screenshot UI for documentation
5. **general-purpose** - General research and multi-step tasks

**Low Priority** (likely don't need browser tools):
- prp-gen-* agents (research/generation only)
- statusline-setup, output-style-setup (config only)

### Implementation Steps

**Phase 1: Update Agent Definitions**
1. Read `.claude/agents/validation-gates.md`
2. Add Playwright tools to tool list
3. Add browser validation examples
4. Update agent description with frontend testing capabilities

**Phase 2: Update prp-exec-validator**
1. Read `.claude/agents/prp-exec-validator.md`
2. Add Playwright tools to tool list
3. Add UI validation loop patterns
4. Document screenshot capture for proof of validation

**Phase 3: Update Documentation**
1. Update `.claude/agents/README.md` with browser testing guidance
2. Add example browser validation workflows
3. Document when to use browser tools vs API testing

**Phase 4: Update Validation Patterns**
1. Create browser validation pattern in `.claude/patterns/`
2. Document full-stack testing workflow
3. Add screenshot assertion patterns

### Browser Tool Usage Patterns

**Navigation Pattern**:
```python
# Navigate to frontend
browser_navigate(url="http://localhost:5173")

# Capture page state
browser_snapshot()
```

**Interaction Pattern**:
```python
# Click element
browser_click(element="Upload button", ref="e5")

# Fill form
browser_fill_form(fields=[
    {"name": "title", "type": "textbox", "ref": "e6", "value": "Test Doc"},
    {"name": "file", "type": "file", "ref": "e7", "value": "/path/to/test.pdf"}
])

# Wait for success
browser_wait_for(text="Upload successful")
```

**Validation Pattern**:
```python
# Take screenshot for visual proof
browser_take_screenshot(filename="validation-proof.png")

# Run JavaScript assertion
browser_evaluate(function="() => document.querySelectorAll('.task-card').length")
```

### Success Criteria

**Phase 1 Complete When**:
- [ ] validation-gates agent has Playwright tools listed
- [ ] Agent description mentions frontend testing capability
- [ ] Example browser validation workflow documented

**Phase 2 Complete When**:
- [ ] prp-exec-validator agent has Playwright tools listed
- [ ] UI validation loop pattern documented
- [ ] Screenshot capture pattern included

**Phase 3 Complete When**:
- [ ] .claude/agents/README.md updated with browser testing guidance
- [ ] Browser tool usage examples provided
- [ ] Clear guidance on when to use browser vs API testing

**Phase 4 Complete When**:
- [ ] Browser validation pattern created in .claude/patterns/
- [ ] Full-stack testing workflow documented
- [ ] Pattern includes screenshot assertions

### Validation Strategy

**Test Agent Updates**:
1. Launch validation-gates agent with browser task
2. Verify agent can access browser tools
3. Test navigation to localhost:5173
4. Test element interaction
5. Verify screenshot capture works

**Integration Testing**:
1. Run RAG service (Phase 1 complete)
2. Launch validation-gates to validate frontend
3. Verify agent navigates, interacts, validates
4. Check screenshots generated
5. Confirm validation loop works with UI testing

### Known Constraints

**Browser Availability**:
- MCP_DOCKER server must be running
- Browser may need installation (use browser_install tool)
- Tests require frontend to be running (docker-compose up)

**Agent Limitations**:
- Agents cannot see visual screenshots directly
- Must rely on accessibility tree (browser_snapshot)
- Screenshot files for human verification only

**Performance**:
- Browser operations slower than API calls
- Use browser testing for critical UI flows only
- Prefer API testing for backend validation

### Risk Mitigation

**High Risk Areas**:

1. **Browser Not Installed**
   - Mitigation: Document browser_install tool usage
   - Validation: Test on fresh environment
   - Reference: MCP_DOCKER browser tools

2. **Frontend Not Running**
   - Mitigation: Document prerequisite (docker-compose up)
   - Validation: Check health endpoint before browser tests
   - Reference: Phase 1 validation checklist

3. **Element References Change**
   - Mitigation: Use semantic queries (text, role) not refs
   - Validation: Test with multiple UI states
   - Reference: Playwright accessibility testing

4. **Agent Token Budget**
   - Mitigation: Limit screenshot usage (only critical validations)
   - Validation: Monitor token consumption
   - Reference: Accessibility snapshots more efficient than screenshots

### Integration with Existing Patterns

**Works With**:
- `.claude/patterns/validation-gates.md` - Add browser testing section
- `.claude/patterns/parallel-subagents.md` - Can run browser tests in parallel
- `.claude/patterns/quality-gates.md` - Add frontend quality gate

**Updates Needed**:
- PRP validation sections should mention frontend validation option
- INITIAL templates should include frontend validation success criteria
- Quality gates should include "frontend accessible" check

### File Changes Required

**Agent Files** (`.claude/agents/`):
```
validation-gates.md          - Add Playwright tools
prp-exec-validator.md        - Add Playwright tools
prp-exec-implementer.md      - Add Playwright tools (optional)
documentation-manager.md     - Add Playwright tools (optional)
README.md                    - Add browser testing guidance
```

**Pattern Files** (`.claude/patterns/`):
```
browser-validation.md        - NEW: Browser testing pattern
validation-gates.md          - UPDATE: Add browser testing section
quality-gates.md             - UPDATE: Add frontend quality gate
```

**Documentation Files**:
```
README.md (root)             - Mention browser testing capability
CLAUDE.md                    - Add browser testing guidance
```

### Example Agent Description Update

**Before**:
```markdown
- validation-gates: Testing and validation specialist. Proactively runs tests,
  validates code changes, ensures quality gates are met, and iterates on fixes
  until all tests pass. (Tools: Bash, Read, Edit, MultiEdit, Grep, Glob, TodoWrite)
```

**After**:
```markdown
- validation-gates: Testing and validation specialist. Proactively runs tests,
  validates code changes (backend + frontend UI), ensures quality gates are met,
  and iterates on fixes until all tests pass. Can perform browser automation for
  end-to-end testing. (Tools: Bash, Read, Edit, MultiEdit, Grep, Glob, TodoWrite,
  browser_navigate, browser_snapshot, browser_click, browser_type,
  browser_take_screenshot, browser_evaluate, browser_wait_for)
```

### Future Enhancements (Not This INITIAL)

**Post-MVP**:
- Visual regression testing (screenshot diff)
- Performance testing (browser metrics)
- Accessibility testing (WCAG validation)
- Cross-browser testing (Chromium, Firefox, WebKit)
- Mobile viewport testing
- Network mocking for offline testing

### Next Steps After This INITIAL

1. Execute this INITIAL to update agent configurations
2. Test updated agents with RAG service frontend validation
3. Document browser testing best practices based on results
4. Create reusable browser validation pattern
5. Update PRP templates to include frontend validation criteria
