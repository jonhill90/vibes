# Source: .claude/commands/create-initial.md (lines 126-185)
# Pattern: Parallel subagent execution pattern from INITIAL.md factory
# Purpose: Shows how factory invokes 3 subagents simultaneously in Phase 2

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

## Key Takeaway

The factory achieves 3x speedup in Phase 2 by:
1. Identifying 3 independent research tasks (codebase, docs, examples)
2. Preparing context for each subagent
3. Invoking ALL THREE in a SINGLE message with multiple Task calls
4. Collecting outputs after all complete

This pattern should be applied to execute-prp for parallel task execution.
