# Create INITIAL.md Command

Orchestrates the INITIAL.md factory workflow: a multi-subagent system that creates comprehensive INITIAL.md files through systematic research and analysis.

## Trigger Patterns

When the user says ANY of these, activate this workflow:
- "Help me create INITIAL.md for [feature]"
- "I need to build INITIAL.md for [feature]"
- "Create INITIAL.md for [feature]"
- "Generate INITIAL requirements for [feature]"
- "Write INITIAL.md for [feature]"
- "I want to make an INITIAL.md for [feature]"

## Recognition & Activation

When you detect an INITIAL.md creation request:

1. ✅ **STOP** any other work immediately
2. ✅ **ACKNOWLEDGE**: "I'll help create a comprehensive INITIAL.md using the factory workflow"
3. ✅ **PROCEED** to Phase 0 (don't ask for permission)
4. ✅ **NEVER** skip Phase 0 clarifications
5. ✅ **NEVER** try to write INITIAL.md directly yourself

## The 5-Phase Workflow

### Phase 0: Recognition & Basic Clarification (YOU handle this)

**Immediate Actions**:

1. ✅ Acknowledge the request
2. ✅ Ask 2-3 clarifying questions:
   - Primary use case: What problem does this solve?
   - Technical preferences: Specific technologies or should I recommend?
   - Integration needs: Any existing systems to integrate with?
3. ✅ **CRITICAL: WAIT for user response** - DO NOT PROCEED until user answers

**After User Responds**:

```python
# 1. Determine feature name (snake_case)
feature_name = user_input_to_snake_case()  # e.g., "web_scraper", "auth_system"

# 2. Create directories
Bash("mkdir -p prps/research")
Bash(f"mkdir -p examples/{feature_name}")

# 3. Check Archon availability
health = mcp__archon__health_check()
archon_available = health["status"] == "healthy"

# 4. If Archon available, create project and tasks
if archon_available:
    # Create project
    project = mcp__archon__manage_project("create",
        title=f"INITIAL.md: {feature_display_name}",
        description=f"Creating comprehensive INITIAL.md for {feature_description}"
    )
    project_id = project["project"]["id"]

    # Create 6 tasks
    tasks = [
        {"title": "Phase 1: Requirements Analysis", "assignee": "prp-initial-feature-clarifier", "order": 100},
        {"title": "Phase 2A: Codebase Research", "assignee": "prp-initial-codebase-researcher", "order": 90},
        {"title": "Phase 2B: Documentation Hunt", "assignee": "prp-initial-documentation-hunter", "order": 85},
        {"title": "Phase 2C: Example Curation", "assignee": "prp-initial-example-curator", "order": 80},
        {"title": "Phase 3: Gotcha Analysis", "assignee": "prp-initial-gotcha-detective", "order": 75},
        {"title": "Phase 4: Assembly", "assignee": "prp-initial-assembler", "order": 70}
    ]

    task_ids = []
    for task_def in tasks:
        task = mcp__archon__manage_task("create",
            project_id=project_id,
            title=task_def["title"],
            description=f"{task_def['assignee']} - Autonomous execution",
            status="todo",
            assignee=task_def["assignee"],
            task_order=task_def["order"]
        )
        task_ids.append(task["task"]["id"])
else:
    project_id = None
    task_ids = []

# 5. Proceed to Phase 1
```

---

### Phase 1: Deep Feature Analysis

**Subagent**: `prp-initial-feature-clarifier`
**Mode**: AUTONOMOUS - Works without user interaction
**Duration**: 2-3 minutes

**Your Actions**:

```python
# 1. Update Archon task to "doing"
if archon_available:
    mcp__archon__manage_task("update", task_id=task_ids[0], status="doing")

# 2. Prepare context for subagent
context = {
    "user_request": original_user_request,
    "clarifications": user_responses_from_phase_0,
    "feature_name": feature_name,
    "archon_project_id": project_id if archon_available else None
}

# 3. Invoke clarifier
invoke_subagent("prp-initial-feature-clarifier", context)

# 4. Wait for completion - subagent will create prps/research/feature-analysis.md

# 5. Mark task complete
if archon_available:
    mcp__archon__manage_task("update", task_id=task_ids[0], status="done")
```

**Expected Output**: `prps/research/feature-analysis.md`

---

### Phase 2: Parallel Research (CRITICAL PHASE)

**Subagents**: THREE simultaneously
- `prp-initial-codebase-researcher`
- `prp-initial-documentation-hunter`
- `prp-initial-example-curator`

**Mode**: PARALLEL EXECUTION
**Duration**: 3-5 minutes (all run in parallel)

⚠️ **CRITICAL**: Invoke all three in SINGLE message with multiple Task tool calls

**Your Actions**:

```python
# 1. Update all three Archon tasks to "doing"
if archon_available:
    for i in [1, 2, 3]:  # Tasks 2A, 2B, 2C
        mcp__archon__manage_task("update", task_id=task_ids[i], status="doing")

# 2. Prepare context for each subagent
researcher_context = {
    "feature_analysis": "prps/research/feature-analysis.md",
    "feature_name": feature_name,
    "archon_project_id": project_id if archon_available else None
}

hunter_context = {
    "feature_analysis": "prps/research/feature-analysis.md",
    "feature_name": feature_name,
    "archon_project_id": project_id if archon_available else None
}

curator_context = {
    "feature_analysis": "prps/research/feature-analysis.md",
    "feature_name": feature_name,
    "examples_dir": f"examples/{feature_name}/",
    "archon_project_id": project_id if archon_available else None
}

# 3. ⚠️ CRITICAL: Parallel invocation - SINGLE message with multiple Task calls
# Use the Task tool THREE times in a SINGLE response
parallel_invoke([
    Task(agent="prp-initial-codebase-researcher", prompt=researcher_context),
    Task(agent="prp-initial-documentation-hunter", prompt=hunter_context),
    Task(agent="prp-initial-example-curator", prompt=curator_context)
])

# 4. After all three complete, mark tasks done
if archon_available:
    for i in [1, 2, 3]:
        mcp__archon__manage_task("update", task_id=task_ids[i], status="done")
```

**Expected Outputs**:
- `prps/research/codebase-patterns.md`
- `prps/research/documentation-links.md`
- `prps/research/examples-to-include.md`
- `examples/{feature_name}/` directory with 2-4 code files + README.md

---

### Phase 3: Gotcha Analysis

**Subagent**: `prp-initial-gotcha-detective`
**Mode**: AUTONOMOUS
**Duration**: 2 minutes

**Your Actions**:

```python
# 1. Update Archon task
if archon_available:
    mcp__archon__manage_task("update", task_id=task_ids[4], status="doing")

# 2. Prepare context
context = {
    "feature_analysis": "prps/research/feature-analysis.md",
    "codebase_patterns": "prps/research/codebase-patterns.md",
    "documentation": "prps/research/documentation-links.md",
    "archon_project_id": project_id if archon_available else None
}

# 3. Invoke detective
invoke_subagent("prp-initial-gotcha-detective", context)

# 4. Wait for completion

# 5. Mark complete
if archon_available:
    mcp__archon__manage_task("update", task_id=task_ids[4], status="done")
```

**Expected Output**: `prps/research/gotchas.md`

---

### Phase 4: Final Assembly

**Subagent**: `prp-initial-assembler`
**Mode**: AUTONOMOUS
**Duration**: 1-2 minutes

**Your Actions**:

```python
# 1. Update Archon task
if archon_available:
    mcp__archon__manage_task("update", task_id=task_ids[5], status="doing")

# 2. Prepare context
context = {
    "feature_name": feature_name,
    "research_dir": "prps/research/",
    "examples_dir": f"examples/{feature_name}/",
    "archon_project_id": project_id if archon_available else None
}

# 3. Invoke assembler
invoke_subagent("prp-initial-assembler", context)

# 4. Wait for completion

# 5. Mark complete
if archon_available:
    mcp__archon__manage_task("update", task_id=task_ids[5], status="done")
```

**Expected Output**: `prps/INITIAL_{feature_name}.md`

---

### Phase 5: Delivery & Next Steps (YOU handle this)

**Your Actions**:

```markdown
✅ **INITIAL.md Created Successfully!**

**Generated Files**:
- 📄 `prps/INITIAL_{feature_name}.md` - Comprehensive requirements document
- 📁 `examples/{feature_name}/` - Extracted code examples ({count} files)
- 📋 `prps/research/` - Supporting research (5 documents)

**Quality Check**:
- Feature description: ✅ Comprehensive
- Examples: ✅ {count} relevant examples extracted
- Documentation: ✅ {count} official sources referenced
- Gotchas: ✅ {count} important considerations documented
- PRP-Ready Score: {X}/10

**Next Steps**:

1. **Review the INITIAL.md** (recommended):
   ```bash
   cat prps/INITIAL_{feature_name}.md
   ```

2. **Review extracted examples** (optional but helpful):
   ```bash
   cat examples/{feature_name}/README.md
   ```

3. **Generate the PRP** (when ready):
   ```bash
   /generate-prp prps/INITIAL_{feature_name}.md
   ```

4. **Execute the feature** (after PRP generation):
   ```bash
   /execute-prp prps/PRP_{feature_name}.md
   ```

Would you like me to review any specific section, or shall we proceed to PRP generation?
```

**Update Archon** (if available):

```python
# 1. Add final notes to project
mcp__archon__manage_project("update",
    project_id=project_id,
    description=f"COMPLETED: Generated INITIAL.md with {example_count} examples, quality score: {score}/10"
)

# 2. INITIAL.md already stored by assembler as document
# No additional action needed
```

---

## Error Handling

### If Subagent Fails

```python
try:
    invoke_subagent("agent-name", context)
except SubagentError as e:
    # Log error
    logger.error(f"Phase X failed: {e}")

    # Update Archon if available
    if archon_available:
        mcp__archon__manage_task("update", task_id=task_id,
            description=f"ERROR: {e}",
            status="todo"  # Reset to allow retry
        )

    # Inform user
    print(f"⚠️ Phase X encountered an issue: {e}")
    print("Would you like me to:")
    print("1. Retry this phase")
    print("2. Continue with partial results")
    print("3. Abort workflow")

    # Wait for user decision
```

### If Archon Unavailable

```python
# Proceed without tracking
# Workflow continues normally, just no Archon project/task updates
if not archon_available:
    print("ℹ️ Archon MCP not available - proceeding without project tracking")
```

---

## Quality Gates

Before delivering INITIAL.md to user, verify:

```python
quality_checks = [
    "Feature description comprehensive (not vague)",
    "Examples extracted to examples/{feature}/ directory",
    "Examples have 'what to mimic' guidance in README",
    "Documentation includes working examples and specific URLs",
    "Gotchas documented with solutions (not just warnings)",
    "INITIAL.md follows INITIAL_EXAMPLE.md structure",
    "Ready for immediate /generate-prp",
    "Quality score >= 8/10"
]

# Verify each check
for check in quality_checks:
    if not passes_check(check):
        issues.append(check)

if issues:
    print(f"⚠️ Quality issues detected: {issues}")
    print("Would you like me to:")
    print("1. Fix these issues")
    print("2. Proceed anyway (not recommended)")
    print("3. Regenerate specific phases")
```

---

## Success Metrics

Track and report:
- ✅ Total time: {X} minutes (target: <10 minutes)
- ✅ Quality score: {X}/10 (target: >= 8/10)
- ✅ Examples extracted: {count} (target: 2-4)
- ✅ Documentation sources: {count} (target: 3-5)
- ✅ Gotchas documented: {count} (target: 2-5)
- ✅ PRP generation ready: {yes/no}

---

## Parallel Execution Implementation

**CRITICAL**: Phase 2 must use parallel tool invocation.

**How to invoke multiple subagents in parallel:**

In a SINGLE message, use the Task tool THREE times:

```
I'm now invoking all three Phase 2 subagents in parallel:

<use Task tool with agent="prp-initial-codebase-researcher">
<use Task tool with agent="prp-initial-documentation-hunter">
<use Task tool with agent="prp-initial-example-curator">

All three agents are now working simultaneously on their respective research tasks.
```

**DO NOT**:
- Invoke one agent, wait for completion, then invoke next
- Use sequential execution for Phase 2
- Ask user to wait between agents

**DO**:
- Send all three Task tool invocations in a single message
- Let agents work in parallel
- Report completion when all three finish

---

## Example Full Execution

**User**: "Help me create INITIAL.md for web scraper with rate limiting"

**Phase 0** (YOU):
```
I'll help create a comprehensive INITIAL.md using the factory workflow. Let me ask a few questions:

1. What will you primarily scrape? (web pages, APIs, specific sites)
2. Where should results be stored? (database, files, other)
3. Any specific anti-detection requirements? (rotating IPs, headers, etc)
```

**User responds**: "Web pages for price monitoring, store in PostgreSQL, need user-agent rotation"

**Phase 0 continued** (YOU):
```
Perfect! Creating INITIAL.md for web_scraper feature.

📁 Setting up directories...
✅ Created prps/research/
✅ Created examples/web_scraper/

🔗 Checking Archon MCP...
✅ Archon available
✅ Created project: "INITIAL.md: Web Scraper"
✅ Created 6 workflow tasks

📋 Phase 1: Requirements Analysis...
```

**Phase 1** (prp-initial-feature-clarifier):
- Analyzes requirements
- Searches Archon for similar scrapers
- Creates feature-analysis.md
- ~2 minutes

**Phase 2** (3 agents in parallel):
```
⚡ Phase 2: Parallel Research (3 agents working simultaneously)...

🔍 Codebase Researcher: Searching for scraping patterns...
📚 Documentation Hunter: Finding official docs...
📦 Example Curator: Extracting code examples...
```

- All three work simultaneously
- ~3 minutes total (not 9 minutes sequential)

**Phase 3** (prp-initial-gotcha-detective):
```
🚨 Phase 3: Gotcha Analysis...
Researching security issues, rate limiting, common pitfalls...
```
- ~2 minutes

**Phase 4** (prp-initial-assembler):
```
📝 Phase 4: Final Assembly...
Synthesizing all research into INITIAL.md...
```
- ~1 minute

**Phase 5** (YOU):
```
✅ **INITIAL.md Created Successfully!**

**Generated Files**:
- 📄 `prps/INITIAL_web_scraper.md` - Comprehensive requirements document
- 📁 `examples/web_scraper/` - Extracted code examples (3 files)
- 📋 `prps/research/` - Supporting research (5 documents)

**Quality Check**:
- Feature description: ✅ Comprehensive
- Examples: ✅ 3 relevant examples extracted
- Documentation: ✅ 5 official sources referenced
- Gotchas: ✅ 8 important considerations documented
- PRP-Ready Score: 9/10

**Next Steps**:
1. Review: `cat prps/INITIAL_web_scraper.md`
2. Generate PRP: `/generate-prp prps/INITIAL_web_scraper.md`
3. Execute: `/execute-prp prps/PRP_web_scraper.md`

Total time: 8 minutes

Would you like me to review any section or proceed to PRP generation?
```

---

## Remember

- Phase 0: YOU ask questions and WAIT for user
- Phase 1: Single subagent (feature-clarifier)
- Phase 2: THREE subagents in PARALLEL (critical!)
- Phase 3: Single subagent (gotcha-detective)
- Phase 4: Single subagent (assembler)
- Phase 5: YOU deliver results and next steps
- Always update Archon tasks if available
- Quality score must be >= 8/10
- Total time target: <10 minutes
