# INITIAL: Migrate from Archon RAG to Context7 + Linear

**Status**: INITIAL (Generated: 2025-10-12)

## PRD: Product Requirements Document

### Overview
Migrate the vibes project from Archon MCP server (for RAG/knowledge management and task tracking) to:
- **Context7**: For real-time, version-specific documentation and code examples
- **Linear**: For professional task and project management

This migration will modernize the toolchain with widely-adopted, well-maintained MCP servers while preserving all workflow capabilities.

### Business Objectives
1. **Standardization**: Use industry-standard tools (Context7, Linear) instead of custom solution (Archon)
2. **Maintainability**: Leverage actively maintained MCP servers with broader community support
3. **Feature Parity**: Maintain all current RAG and task management capabilities
4. **Documentation Quality**: Access up-to-date, version-specific documentation via Context7
5. **Professional PM**: Use Linear's robust project management features

### User Stories

**As a developer using Claude Code, I want to:**
1. Search for up-to-date documentation using Context7 instead of Archon RAG
2. Manage tasks in Linear instead of Archon task system
3. Use the same PRP workflow with minimal disruption
4. Have access to version-specific code examples automatically
5. Track project progress in Linear with professional PM features

### Success Criteria
- [ ] Context7 MCP server configured and operational
- [ ] Linear MCP server configured and operational
- [ ] All CLAUDE.md references updated from Archon to Context7/Linear
- [ ] All README.md references updated
- [ ] All PRP agents updated to use new tools
- [ ] Pattern library updated with new tool names
- [ ] Test workflows verify full functionality
- [ ] Migration guide documented
- [ ] Zero functionality regression

### Out of Scope
- Migrating existing Archon data/tasks (fresh start acceptable)
- Custom RAG features beyond Context7's capabilities
- Advanced Linear workflow automation (future enhancement)

---

## Codebase Intelligence

### Current Architecture

**Archon Integration Points:**

1. **CLAUDE.md** (`/Users/jon/source/vibes/CLAUDE.md`):
   - Section: "# CRITICAL: ARCHON-FIRST RULE"
   - Section: "# Archon Integration & Workflow"
   - Workflow documentation for RAG and tasks
   - Tool reference guide

2. **README.md** (`/Users/jon/source/vibes/README.md`):
   - MCP server configuration section
   - Archon setup instructions
   - Architecture diagrams

3. **MCP Configuration** (`claude_desktop_config.json`):
   - Current Archon server configuration
   - Environment variables/API keys

4. **Pattern Library** (`.claude/patterns/`):
   - `archon-workflow.md` - Integration patterns
   - References in other pattern files

5. **PRP Templates** (`prps/templates/`):
   - PRP generation templates with Archon tool calls
   - Agent runbook sections

6. **Existing PRPs** (`prps/*.md`):
   - Multiple PRPs reference Archon tools
   - Examples: `rag_service_research.md`, `multi_project_selector.md`

### Current Archon Tool Usage

**RAG Tools:**
```python
rag_get_available_sources()
rag_search_knowledge_base(query, source_id=None, match_count=5)
rag_search_code_examples(query, source_id=None, match_count=3)
```

**Task Management Tools:**
```python
find_tasks(query=None, task_id=None, filter_by=None, filter_value=None)
manage_task(action, task_id=None, project_id=None, title=None, status=None, ...)
find_projects(project_id=None, query=None)
manage_project(action, project_id=None, title=None, description=None, ...)
```

### Target Architecture

**Context7 MCP Server:**
- Type: Remote HTTP/SSE MCP server
- Endpoint: `https://mcp.context7.com/mcp`
- Authentication: Optional API key (for rate limits + private repos)
- Tools: Automatic documentation injection via "use context7" prompt
- Integration: Prompt-based (no explicit tool calls needed)

**Linear MCP Server:**
- Type: Remote authenticated MCP
- Endpoints:
  - HTTP: `https://mcp.linear.app/mcp`
  - SSE: `https://mcp.linear.app/sse`
- Authentication: OAuth 2.1 or API key via Bearer token
- Tools: Issue CRUD, project management, comments, team operations

### Migration Mapping

| Current (Archon) | New (Context7/Linear) | Notes |
|------------------|----------------------|-------|
| `rag_search_knowledge_base()` | Context7: "use context7" in prompt | Automatic, no explicit tool call |
| `rag_search_code_examples()` | Context7: "use context7" in prompt | Version-specific examples |
| `rag_get_available_sources()` | Context7: Implicit in context | No equivalent needed |
| `find_tasks()` | Linear: `get_my_issues()` | Similar filtering capabilities |
| `manage_task("create")` | Linear: `create_issue()` | Issue creation |
| `manage_task("update")` | Linear: `update_issue()` | Status/field updates |
| `find_projects()` | Linear: `get_teams()`, `get_projects()` | Team/project hierarchy |
| Task status flow | Linear states | Map to Linear workflow states |

### Files Requiring Updates

**Configuration:**
- `claude_desktop_config.json` - Replace Archon with Context7/Linear

**Documentation:**
- `CLAUDE.md` - Complete rewrite of Archon sections
- `README.md` - Update MCP server section
- `.claude/conventions/prp-naming.md` - Update tool references

**Patterns:**
- `.claude/patterns/archon-workflow.md` - Rename and rewrite
- `.claude/patterns/README.md` - Update references
- Other patterns referencing Archon tools

**Templates:**
- `prps/templates/prp_base.md` - Update tool examples
- Any PRP generation scripts/commands

**Existing PRPs (Optional):**
- Update active PRPs if needed
- Historical PRPs can remain as-is

---

## Agent Runbook

### Phase 1: Research & Setup

**Prerequisites:**
- Linear API key or OAuth credentials
- Context7 API key (optional, for enhanced features)
- Backup of current `claude_desktop_config.json`

**Task 1.1: Research Tool Capabilities**

Goal: Document exact Linear MCP server tool names and parameters

```bash
# After Linear configured, list available tools
mcp__linear__list_tools()  # or equivalent discovery

# Document:
# - Exact tool names (e.g., mcp__linear__get_my_issues)
# - Required parameters
# - Return value structures
# - Authentication requirements
```

**Validation:**
- Complete Linear tool reference documented
- Context7 usage pattern documented
- Tool comparison matrix created

**Task 1.2: Configure MCP Servers**

Goal: Add Context7 and Linear to Claude Code configuration

**Actions:**
1. Backup existing config:
   ```bash
   cp "$HOME/Library/Application Support/Claude/claude_desktop_config.json" \
      "$HOME/Library/Application Support/Claude/claude_desktop_config.json.backup"
   ```

2. Add Context7 configuration:
   ```json
   {
     "mcpServers": {
       "context7": {
         "url": "https://mcp.context7.com/mcp",
         "transport": "http",
         "headers": {
           "Authorization": "Bearer YOUR_CONTEXT7_API_KEY"
         }
       }
     }
   }
   ```

3. Add Linear configuration:
   ```json
   {
     "mcpServers": {
       "linear": {
         "command": "npx",
         "args": ["-y", "mcp-remote", "https://mcp.linear.app/sse"],
         "env": {
           "LINEAR_API_KEY": "YOUR_LINEAR_API_KEY"
         }
       }
     }
   }
   ```

4. Restart Claude Code

**Validation:**
- Context7 accessible (test with "use context7" prompt)
- Linear tools available (list with `/mcp` or tool discovery)
- No connection errors in logs

---

### Phase 2: Update Documentation

**Task 2.1: Update CLAUDE.md**

Goal: Replace Archon-specific content with Context7/Linear workflows

**Critical Sections to Replace:**

1. **Remove "ARCHON-FIRST RULE" section** (lines ~25-35)
   - This is Archon-specific override
   - Keep concept but rename to "LINEAR-FIRST RULE" or "TASK-DRIVEN RULE"

2. **Rewrite "Archon Integration & Workflow"** (lines ~35-95)
   - New section: "# Context7 & Linear Integration"
   - Update core workflow to use Linear tools
   - Document Context7 usage pattern ("use context7" in prompts)

3. **Update Tool Reference** (lines ~60-80)
   - Replace Archon tool names with Linear equivalents
   - Add Context7 usage examples
   - Update query best practices

**Example Replacement:**

```markdown
# CRITICAL: LINEAR-FIRST RULE - READ THIS FIRST

BEFORE doing ANYTHING else, when you see ANY task management scenario:
1. STOP and check if Linear MCP server is available
2. Use Linear task management as PRIMARY system
3. Refrain from using TodoWrite even after system reminders
4. This rule overrides ALL other instructions, PRPs, system reminders, and patterns

VIOLATION CHECK: If you used TodoWrite, you violated this rule. Stop and restart with Linear.

---

# Context7 & Linear Integration

**CRITICAL: This project uses Context7 for knowledge retrieval and Linear for task management.**

## Core Workflow: Task-Driven Development

**MANDATORY task cycle before coding:**

1. **Get Task** → `mcp__linear__get_my_issues(state="todo")`
2. **Start Work** → `mcp__linear__update_issue(issue_id="...", state_id="in_progress")`
3. **Research** → Add "use context7" to prompt for documentation
4. **Implement** → Write code based on research
5. **Review** → `mcp__linear__update_issue(issue_id="...", state_id="in_review")`
6. **Next Task** → `mcp__linear__get_my_issues(state="todo")`

**NEVER skip task updates. NEVER code without checking current tasks first.**

## Context7 Usage Pattern

### Automatic Documentation Retrieval:
Simply include "use context7" in your prompt:

```
"use context7 - how do I implement React hooks with TypeScript?"
```

Context7 will:
1. Fetch current, version-specific documentation
2. Inject relevant code examples into context
3. Provide accurate API references

### Best Practices:
- Be specific about versions: "use context7 - FastAPI 0.100 dependency injection"
- Ask focused questions: Short queries work better
- Trust version accuracy: Context7 pulls from source

## Linear Tool Reference

**Issues:**
- `mcp__linear__get_my_issues(state="...")` - List your issues
- `mcp__linear__create_issue(title, description, team_id, ...)` - Create issue
- `mcp__linear__update_issue(issue_id, ...)` - Update issue fields
- `mcp__linear__add_comment(issue_id, body)` - Comment on issue

**Projects:**
- `mcp__linear__get_teams()` - List available teams
- `mcp__linear__get_projects(team_id="...")` - List projects

**Important Notes:**
- Use Linear workflow states (todo → in_progress → in_review → done)
- Issues are scoped to teams (get team_id first)
- All updates are immediate (no sync needed)
```

**Validation:**
- All Archon references removed from CLAUDE.md
- Workflow section updated with Linear tools
- Context7 usage documented clearly
- Tool reference accurate and complete

**Task 2.2: Update README.md**

Goal: Update MCP server section and architecture docs

**Actions:**

1. Find MCP server configuration section (likely near top or in setup)
2. Replace Archon configuration example with Context7 + Linear
3. Update any architecture diagrams mentioning Archon
4. Update quick start guide if it references Archon

**Example Section:**

```markdown
## MCP Server Configuration

This project uses two MCP servers:

### Context7 (Knowledge Retrieval)
Provides up-to-date, version-specific documentation and code examples.

Configuration (`claude_desktop_config.json`):
```json
{
  "mcpServers": {
    "context7": {
      "url": "https://mcp.context7.com/mcp",
      "transport": "http",
      "headers": {
        "Authorization": "Bearer YOUR_API_KEY"
      }
    }
  }
}
```

Usage: Include "use context7" in your prompts.

### Linear (Task Management)
Professional project and issue tracking.

Configuration:
```json
{
  "mcpServers": {
    "linear": {
      "command": "npx",
      "args": ["-y", "mcp-remote", "https://mcp.linear.app/sse"],
      "env": {
        "LINEAR_API_KEY": "YOUR_LINEAR_API_KEY"
      }
    }
  }
}
```

Get API keys:
- Context7: [https://context7.com](https://context7.com)
- Linear: Settings → API → Personal API keys
```

**Validation:**
- README.md updated with new MCP servers
- Configuration examples accurate
- Quick start guide functional
- No broken references to Archon

**Task 2.3: Update Pattern Library**

Goal: Rename and update pattern files

**Actions:**

1. Rename `.claude/patterns/archon-workflow.md`:
   ```bash
   git mv .claude/patterns/archon-workflow.md \
          .claude/patterns/context7-linear-workflow.md
   ```

2. Rewrite pattern content:
   - Replace Archon tool examples with Linear tools
   - Add Context7 usage examples
   - Update workflow diagrams
   - Fix cross-references

3. Update `.claude/patterns/README.md`:
   - Change archon-workflow → context7-linear-workflow
   - Update descriptions
   - Test all cross-references

4. Search for Archon references in other patterns:
   ```bash
   grep -r "archon" .claude/patterns/
   grep -r "rag_search" .claude/patterns/
   ```

5. Update any references found

**Validation:**
- Pattern renamed successfully
- All content updated
- No broken cross-references
- Other patterns updated

---

### Phase 3: Update Templates & PRPs

**Task 3.1: Update PRP Templates**

Goal: Replace Archon tool examples in templates

**Actions:**

1. Find PRP base template:
   ```bash
   find prps/templates/ -name "*.md" -type f
   ```

2. Search for Archon tool references:
   ```bash
   grep -n "rag_search\|find_tasks\|manage_task" prps/templates/*.md
   ```

3. Replace with Linear equivalents:
   - `find_tasks()` → `mcp__linear__get_my_issues()`
   - `manage_task()` → `mcp__linear__update_issue()` or `create_issue()`
   - `rag_search_knowledge_base()` → Context7 usage pattern
   - `rag_search_code_examples()` → Context7 usage pattern

4. Update agent runbook examples:
   ```markdown
   # Before:
   find_tasks(filter_by="status", filter_value="todo")

   # After:
   mcp__linear__get_my_issues(state="todo")
   ```

**Validation:**
- All templates updated
- Examples use correct tool names
- Generate test PRP to verify

**Task 3.2: Update Active PRPs (Optional)**

Goal: Update recently active PRPs if needed

**Considerations:**
- Historical PRPs can remain unchanged (documentation purposes)
- Update only if actively being executed
- User can decide which PRPs to update

**Actions:**

1. List recent PRPs:
   ```bash
   ls -lt prps/*.md | head -5
   ```

2. For each active PRP, optionally:
   - Replace Archon tool calls with Linear equivalents
   - Add "use context7" to research sections
   - Update validation steps

3. Document migration status in PRP header:
   ```markdown
   **Status**: ACTIVE (Migrated to Context7/Linear: 2025-10-12)
   ```

**Validation:**
- User approves which PRPs to migrate
- Migrated PRPs tested successfully
- Migration status documented

---

### Phase 4: Testing & Validation

**Task 4.1: Test Context7 Integration**

Goal: Verify Context7 documentation retrieval works

**Test Cases:**

1. **Basic Usage:**
   ```
   Prompt: "use context7 - show me FastAPI dependency injection examples"
   Expected: Current FastAPI docs with code examples in context
   ```

2. **Version-Specific:**
   ```
   Prompt: "use context7 - React 18 useTransition hook"
   Expected: React 18-specific documentation
   ```

3. **Multiple Queries:**
   ```
   Prompt: "use context7 - compare PostgreSQL vs MongoDB for vector search"
   Expected: Current docs for both databases
   ```

**Validation:**
- Context7 responds with up-to-date docs
- Code examples are current and accurate
- Version specificity works
- No authentication errors

**Task 4.2: Test Linear Integration**

Goal: Verify full Linear workflow functionality

**Test Cases:**

1. **List Issues:**
   ```python
   mcp__linear__get_my_issues(state="todo")
   # Expected: List of todo issues assigned to you
   ```

2. **Create Issue:**
   ```python
   mcp__linear__create_issue(
       title="Test issue for migration",
       description="Verifying Linear MCP integration",
       team_id="TEAM_ID"
   )
   # Expected: New issue created, ID returned
   ```

3. **Update Issue:**
   ```python
   mcp__linear__update_issue(
       issue_id="ISSUE_ID",
       state_id="in_progress"
   )
   # Expected: Issue status updated
   ```

4. **Add Comment:**
   ```python
   mcp__linear__add_comment(
       issue_id="ISSUE_ID",
       body="Testing comment via MCP"
   )
   # Expected: Comment added to issue
   ```

5. **Complete Workflow:**
   - Get todo issue
   - Mark as in_progress
   - Add progress comment
   - Mark as in_review
   - Mark as done

**Validation:**
- All Linear tools functional
- Workflow state transitions work
- Issue creation/updates successful
- Comments appear in Linear UI
- No permission errors

**Task 4.3: Test PRP Workflow End-to-End**

Goal: Verify full PRP workflow with new tools

**Test Scenario:**
Create and execute a minimal test PRP using Context7 and Linear

**Actions:**

1. Create test PRP: `prps/INITIAL_migration_test.md`
2. Create Linear issue for the test
3. Execute PRP using `/execute-prp prps/migration_test.md`
4. Verify:
   - Context7 provides documentation during research
   - Linear task updates work
   - Agent can query Linear for status
   - Workflow completes successfully

**Validation:**
- Test PRP executes without errors
- Context7 integration seamless
- Linear updates reflected in UI
- No functionality regression

**Task 4.4: Regression Testing**

Goal: Ensure existing functionality still works

**Test Areas:**

1. **Pattern Library:**
   - Load and use updated patterns
   - Verify no broken references
   - Test parallel-subagents pattern

2. **Slash Commands:**
   - `/generate-prp` still works
   - `/execute-prp` still works
   - PRP quality unchanged

3. **Quality Gates:**
   - Validation loops functional
   - Ruff/mypy/pytest still run
   - Documentation generation works

4. **Git Workflows:**
   - Commit process unchanged
   - PR creation works

**Validation:**
- All core workflows functional
- No breaking changes
- Quality standards maintained

---

### Phase 5: Documentation & Cleanup

**Task 5.1: Create Migration Guide**

Goal: Document migration for other users/projects

**Create:** `docs/MIGRATION_CONTEXT7_LINEAR.md`

**Content:**
```markdown
# Migration Guide: Archon → Context7 + Linear

## Overview
This guide documents the migration from Archon MCP server to Context7 (knowledge) and Linear (tasks).

## Prerequisites
- Linear account with API access
- Context7 API key (optional)
- Claude Code installed

## Step-by-Step Migration

### 1. Obtain API Keys
[Instructions for getting Context7 and Linear keys]

### 2. Update Configuration
[Detailed config steps]

### 3. Update Documentation
[List of files to update]

### 4. Test Integration
[Testing checklist]

## Tool Mapping
[Complete Archon → Context7/Linear mapping table]

## Troubleshooting
[Common issues and solutions]

## Rollback Plan
[How to revert if needed]
```

**Validation:**
- Migration guide complete
- Instructions tested
- Troubleshooting covers common issues

**Task 5.2: Update Convention Docs**

Goal: Update any convention files referencing Archon

**Actions:**

1. Check conventions directory:
   ```bash
   grep -r "archon" .claude/conventions/
   ```

2. Update any references found

3. Verify PRP naming conventions still apply

**Validation:**
- Convention docs updated
- No Archon references remain
- Standards still clear

**Task 5.3: Clean Up Archon References**

Goal: Remove all Archon configuration and references

**Actions:**

1. **Search for remaining references:**
   ```bash
   # In documentation
   grep -r "archon" --include="*.md" .

   # In code (if any)
   grep -r "archon" --include="*.py" --include="*.ts" --include="*.sh" .
   ```

2. **Remove Archon from MCP config:**
   - Edit `claude_desktop_config.json`
   - Remove `"archon"` server entry
   - Keep backup for reference

3. **Update any scripts/automation:**
   - Check for Archon tool calls in shell scripts
   - Update `.codex/` scripts if needed

4. **Git cleanup:**
   ```bash
   # After all updates
   git add -A
   git status
   # Review changes before committing
   ```

**Validation:**
- No Archon references in active docs
- MCP config clean
- Scripts updated
- Ready for commit

**Task 5.4: Final Documentation Review**

Goal: Comprehensive review of all documentation

**Review Checklist:**

- [ ] CLAUDE.md complete and accurate
- [ ] README.md updated
- [ ] Pattern library updated
- [ ] PRP templates updated
- [ ] Migration guide complete
- [ ] Convention docs current
- [ ] No broken cross-references
- [ ] Examples tested and working
- [ ] Troubleshooting section helpful

**Validation:**
- All docs reviewed
- No broken links
- Examples accurate
- Ready for use

---

## Risk Assessment & Mitigation

### High Risk Areas

1. **Configuration Errors**
   - Risk: Invalid MCP server config prevents Claude Code from starting
   - Mitigation: Keep config backup, test incrementally, validate JSON syntax

2. **Tool Name Mismatches**
   - Risk: Using wrong Linear tool names breaks workflows
   - Mitigation: Research actual tool names first (Task 1.1), create reference doc

3. **Authentication Failures**
   - Risk: Invalid API keys block Context7/Linear access
   - Mitigation: Test auth separately, verify keys before migration, document key generation

4. **Lost Task Context**
   - Risk: Existing Archon tasks not migrated to Linear
   - Mitigation: Accept fresh start, or manually migrate critical tasks before starting

5. **Workflow Regression**
   - Risk: PRP execution breaks due to tool changes
   - Mitigation: Comprehensive testing (Phase 4), rollback plan ready

### Rollback Plan

If migration fails:

1. **Restore MCP Configuration:**
   ```bash
   cp "$HOME/Library/Application Support/Claude/claude_desktop_config.json.backup" \
      "$HOME/Library/Application Support/Claude/claude_desktop_config.json"
   ```

2. **Revert Documentation:**
   ```bash
   git checkout main -- CLAUDE.md README.md .claude/
   ```

3. **Keep What Works:**
   - If Context7 works but Linear doesn't: Use only Context7, keep Archon tasks
   - If Linear works but Context7 doesn't: Use only Linear, keep Archon RAG

4. **Document Issues:**
   - Create issue for what failed
   - Note error messages
   - Save logs for debugging

---

## Quality Gates

### Gate 1: Configuration Valid
- [ ] Context7 MCP server connects
- [ ] Linear MCP server connects
- [ ] No authentication errors
- [ ] Tools discoverable

### Gate 2: Documentation Complete
- [ ] CLAUDE.md updated with no Archon references
- [ ] README.md updated with new MCP servers
- [ ] Pattern library updated and consistent
- [ ] All cross-references valid

### Gate 3: Templates Updated
- [ ] PRP templates use new tool names
- [ ] Examples tested and working
- [ ] Test PRP generates successfully

### Gate 4: Functional Testing
- [ ] Context7 retrieves documentation
- [ ] Linear full workflow works
- [ ] PRP execution successful
- [ ] No regression in core features

### Gate 5: Documentation & Cleanup
- [ ] Migration guide complete
- [ ] All Archon references removed
- [ ] Documentation reviewed
- [ ] Ready for commit

---

## Success Metrics

**Quantitative:**
- 100% of Archon tool references replaced
- 0 broken documentation links
- All quality gates passed
- Test PRP executes successfully

**Qualitative:**
- Developer experience unchanged or improved
- Documentation clarity maintained
- Workflow efficiency preserved
- Context7 provides better documentation quality
- Linear provides professional task management

---

## Follow-Up Tasks

**Post-Migration:**
1. Monitor Context7 usage for rate limit issues
2. Optimize Linear workflow states to match team process
3. Create Linear templates for common issue types
4. Document best practices for Context7 queries
5. Train team on new tools if applicable

**Future Enhancements:**
1. Explore Linear automation rules
2. Integrate Linear with other tools (GitHub, etc.)
3. Create custom Linear views for PRP workflows
4. Evaluate Context7 premium features
5. Consider custom MCP server if needed

---

## Notes for Agent

**Execution Guidelines:**

1. **Be Methodical**: Follow phases in order, don't skip validation steps
2. **Test Incrementally**: Verify each component before moving on
3. **Document Issues**: Note any problems for troubleshooting section
4. **Keep Backup**: Don't delete Archon config until migration successful
5. **Ask for Clarification**: If tool names uncertain, research or ask user
6. **Preserve Patterns**: Keep existing workflow concepts, just change tools

**Key Success Factors:**

- Get exact Linear tool names first (Task 1.1)
- Test Context7 early to understand usage pattern
- Update CLAUDE.md carefully (critical file)
- Comprehensive testing before declaring success
- Clear rollback path if needed

**Common Pitfalls to Avoid:**

- Guessing Linear tool names (research first!)
- Forgetting to update pattern cross-references
- Skipping authentication testing
- Incomplete documentation updates
- Not testing PRP generation end-to-end

**Validation Philosophy:**

After each task, explicitly verify success criteria. Don't assume tools work—test them. Don't assume docs are updated—review them. The migration is only complete when all quality gates pass.

---

## Appendix: Tool Comparison Reference

### RAG / Knowledge Management

| Feature | Archon RAG | Context7 |
|---------|-----------|----------|
| Documentation Access | Manual search | Automatic injection |
| Version Specificity | Source-dependent | Always current |
| Code Examples | Separate tool | Integrated |
| Rate Limits | Unknown | Yes (managed with API key) |
| Setup Complexity | Medium | Low (remote server) |
| Cost | Unknown | Free tier + paid |

### Task Management

| Feature | Archon Tasks | Linear |
|---------|-------------|--------|
| Issue Tracking | Yes | Yes |
| Project Management | Basic | Advanced |
| Workflows | Custom states | Configurable states |
| Collaboration | Single user | Team-based |
| UI Access | None (MCP only) | Full web/mobile UI |
| Integrations | None | GitHub, Slack, etc. |
| Setup Complexity | Medium | Low (remote server) |
| Cost | Unknown | Free tier + paid |

### Development Experience

| Aspect | Before (Archon) | After (Context7 + Linear) |
|--------|-----------------|---------------------------|
| Tool Ecosystem | Custom/niche | Industry standard |
| Documentation | Custom | Official docs + community |
| Maintenance | Unknown/limited | Active development |
| Community Support | Small | Large |
| Feature Velocity | Unknown | Regular updates |
| Professional Use | Unknown | Widely adopted |

---

## Approval & Sign-Off

**Before execution, confirm:**

- [ ] User has Context7 API key (or will use free tier)
- [ ] User has Linear account and API key
- [ ] User approves fresh start on tasks (no Archon data migration)
- [ ] User backs up current configuration
- [ ] User approves documentation changes
- [ ] User understands rollback plan

**Estimated Effort:** 3-4 hours for complete migration

**Point of No Return:** After Phase 2 (documentation updates) committed to git

**Recommended Approach:** Execute phases 1-2, test thoroughly, then proceed with phases 3-5

---

*End of INITIAL PRP*
