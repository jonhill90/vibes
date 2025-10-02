# Parallel Invocation Pattern - Deep Dive

This example focuses exclusively on the parallel invocation pattern - the most critical optimization for multi-agent workflows.

## The Pattern

**Run multiple independent subagents simultaneously by invoking them in a SINGLE message with MULTIPLE Task tool calls.**

## Performance Impact

```
Sequential: Agent A (3min) → Agent B (3min) → Agent C (3min) = 9 minutes
Parallel:   Agent A (3min) ┐
            Agent B (3min) ├─ All run together        = 3 minutes
            Agent C (3min) ┘

Speedup: 3x faster!
```

## Files in This Example

- **[pattern-demo.md](./pattern-demo.md)** - The critical pattern explained
- **[correct-example.md](./correct-example.md)** - ✅ How to do it right
- **[wrong-example.md](./wrong-example.md)** - ❌ Common mistakes
- **[decision-tree.md](./decision-tree.md)** - When to use parallel vs sequential

## The Critical Rule

### ✅ CORRECT: Single Message, Multiple Tool Calls

```markdown
I'm running 3 tasks in parallel...

<tool_use>
  <tool_name>Task</tool_name>
  <parameters>
    <description>Task 1</description>
    <prompt>...</prompt>
    <subagent_type>agent-1</subagent_type>
  </parameters>
</tool_use>

<tool_use>
  <tool_name>Task</tool_name>
  <parameters>
    <description>Task 2</description>
    <prompt>...</prompt>
    <subagent_type>agent-2</subagent_type>
  </parameters>
</tool_use>

<tool_use>
  <tool_name>Task</tool_name>
  <parameters>
    <description>Task 3</description>
    <prompt>...</prompt>
    <subagent_type>agent-3</subagent_type>
  </parameters>
</tool_use>
```

**Result**: All 3 run simultaneously ⚡

### ❌ WRONG: Multiple Messages, One Tool Call Each

```markdown
Running task 1...

<tool_use>
  <tool_name>Task</tool_name>
  <parameters>
    <description>Task 1</description>
    <prompt>...</prompt>
    <subagent_type>agent-1</subagent_type>
  </parameters>
</tool_use>
```

[Wait for completion...]

```markdown
Running task 2...

<tool_use>
  <tool_name>Task</tool_name>
  <parameters>
    <description>Task 2</description>
    <prompt>...</prompt>
    <subagent_type>agent-2</subagent_type>
  </parameters>
</tool_use>
```

**Result**: Sequential execution - 3x slower! 🐌

## Requirements for Parallel Execution

### ✅ 1. Tasks Must Be Independent

**Good - Truly Independent**:
```
Agent A: Reads spec.md → Creates design-a.md
Agent B: Reads spec.md → Creates design-b.md
Agent C: Reads spec.md → Creates design-c.md

✅ All read SAME input
✅ All write DIFFERENT outputs
✅ No dependencies
```

**Bad - Has Dependencies**:
```
Agent A: Creates design-a.md
Agent B: Reads design-a.md → Creates design-b.md  ❌ Depends on A!
Agent C: Reads design-b.md → Creates design-c.md  ❌ Depends on B!

Must run sequentially!
```

### ✅ 2. No File Conflicts

**Good - Different Files**:
```
Agent A → output-a.md
Agent B → output-b.md
Agent C → output-c.md
```

**Bad - Same File**:
```
Agent A → output.md    ❌
Agent B → output.md    ❌ Conflict!
```

### ✅ 3. Complete Context for Each Agent

Every agent needs:
- Input file paths
- Output file paths
- Exact folder names
- Full instructions
- Quality standards

**Bad - Incomplete Context**:
```xml
<prompt>Design the tools</prompt>
❌ No input specified
❌ No output specified
```

**Good - Complete Context**:
```xml
<prompt>
You are tool-designer.

Input: project/spec.md
Output: project/tools.md
Folder: project (use EXACTLY)

Design 2-3 tools based on spec...
</prompt>
```

## When to Use Parallel vs Sequential

### Use PARALLEL When:
✅ Tasks are independent (no dependencies)
✅ Tasks work on different files
✅ All context can be provided upfront
✅ Performance matters

### Use SEQUENTIAL When:
❌ Task B needs Task A's output
❌ Tasks modify same file
❌ Need to review A before starting B
❌ Iterative refinement required

## Real Examples

### Example 1: Agent Factory Phase 2

**Scenario**: Create 3 design documents

**Parallel Execution** (CORRECT):
```markdown
Phase 2: Creating designs in parallel...

<tool_use> prompt-engineer   → prompts.md     </tool_use>
<tool_use> tool-integrator   → tools.md       </tool_use>
<tool_use> dependency-manager → dependencies.md </tool_use>
```

**Why it works**:
- All read same INITIAL.md
- All write different files
- No dependencies
- **3x speedup!**

### Example 2: Multi-Service Implementation

**Scenario**: Implement 3 microservices

**Parallel Execution** (CORRECT):
```markdown
Implementing services in parallel...

<tool_use> auth-service-impl   → auth-service/    </tool_use>
<tool_use> payment-service-impl → payment-service/ </tool_use>
<tool_use> user-service-impl    → user-service/    </tool_use>
```

**Why it works**:
- Services are independent
- Different directories
- Can all be specified upfront
- **3x speedup!**

### Example 3: Data Processing Pipeline (WRONG)

**Scenario**: Process data through pipeline

**Sequential Required** (Can't parallelize):
```markdown
Phase 1: Extract data → raw.json
Phase 2: Transform data (reads raw.json) → processed.json
Phase 3: Load data (reads processed.json) → database

❌ Can't run in parallel - each depends on previous!
```

## Common Mistakes and Fixes

### Mistake 1: Invoking Sequentially

**Problem**:
```markdown
# Message 1
<invoke agent-1>

# Message 2 (after waiting)
<invoke agent-2>

# Message 3 (after waiting)
<invoke agent-3>
```

**Fix**:
```markdown
# One message
<invoke agent-1>
<invoke agent-2>
<invoke agent-3>
```

### Mistake 2: Creating Dependencies

**Problem**:
```markdown
<tool_use>
  Agent A: Create output.md
</tool_use>

<tool_use>
  Agent B: Read output.md from Agent A  ❌
</tool_use>
```

**Fix**:
```markdown
<tool_use>
  Agent A: Read input.md → Create output-a.md
</tool_use>

<tool_use>
  Agent B: Read input.md → Create output-b.md
</tool_use>
```

### Mistake 3: Inconsistent Folder Names

**Problem**:
```markdown
<tool_use>
  Agent A: Output to projects/catalog/design.md
</tool_use>

<tool_use>
  Agent B: Output to projects/product-catalog/design.md  ❌ Different name!
</tool_use>
```

**Fix**:
```markdown
<tool_use>
  Agent A: Folder = "catalog", Output to projects/catalog/design-a.md
</tool_use>

<tool_use>
  Agent B: Folder = "catalog", Output to projects/catalog/design-b.md
</tool_use>
```

## Validation Checklist

Before using parallel invocation:

- [ ] All agents work on independent tasks
- [ ] All agents read from EXISTING files (no dependencies on parallel outputs)
- [ ] All agents write to DIFFERENT files
- [ ] Each agent has complete context in prompt
- [ ] All agents receive EXACT SAME folder name
- [ ] No agent depends on another parallel agent's output
- [ ] All Task tool calls in SINGLE message

## Integration with Archon

Track parallel tasks:

```markdown
# Before parallel execution
mcp__archon__manage_task("update", task_id="task-a", status="doing")
mcp__archon__manage_task("update", task_id="task-b", status="doing")
mcp__archon__manage_task("update", task_id="task-c", status="doing")

# Invoke all in parallel
<tool_use> agent-a </tool_use>
<tool_use> agent-b </tool_use>
<tool_use> agent-c </tool_use>

# After completion
mcp__archon__manage_task("update", task_id="task-a", status="done")
mcp__archon__manage_task("update", task_id="task-b", status="done")
mcp__archon__manage_task("update", task_id="task-c", status="done")
```

## Debugging Parallel Execution

### Problem: Not running in parallel

**Check**:
1. Are all tool calls in ONE message?
2. Look at your response structure - multiple messages?

**Fix**: Combine all tool calls into single response

### Problem: Agent can't find file

**Check**:
1. Does the file exist before agent runs?
2. Is it output from a parallel agent? (won't exist yet!)

**Fix**: Only read EXISTING files; parallel agents can't depend on each other

### Problem: File conflicts

**Check**:
1. Are multiple agents writing to same file?

**Fix**: Each agent needs unique output file

## Summary

**The Pattern**:
- One message
- Multiple Task tool calls
- Independent tasks only
- Shared inputs OK, different outputs required

**The Benefit**:
- N agents in parallel = Nx speedup
- Dramatically faster workflows
- Same quality results

**The Rule**:
- **ALWAYS** check for dependencies first
- **NEVER** run parallel if dependencies exist
- **ALWAYS** use single message for parallel execution

## Related Resources

- **Parallel Pattern Template**: [prps/templates/parallel_pattern.md](../../../prps/templates/parallel_pattern.md)
- **Parallel Workflow Example**: [examples/agent-factory/parallel-workflow.md](../../agent-factory/parallel-workflow.md)
- **Agent Factory Phase 2**: [.claude/orchestrators/agent-factory.md](../../../.claude/orchestrators/agent-factory.md)
- **Agent Factory Lite**: [examples/workflows/agent-factory-lite/](../agent-factory-lite/)

---

**Master this pattern for 3x+ performance improvements in multi-agent workflows!**
