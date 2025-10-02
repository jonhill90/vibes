# Parallel Workflow Pattern

This example demonstrates how to run multiple subagents simultaneously for maximum performance. **This is the most critical pattern for efficient multi-agent workflows.**

## Pattern Overview

**Concept**: Run independent tasks in parallel by invoking multiple subagents in a SINGLE message

**Performance Impact**: 3+ agents running in parallel = 3x+ speedup compared to sequential execution

## The Critical Rule

⚠️ **SINGLE MESSAGE WITH MULTIPLE TASK TOOL CALLS**

You MUST invoke all parallel subagents in ONE response containing MULTIPLE `<tool_use>` blocks.

### ✅ CORRECT: Parallel Execution

```markdown
I'm building the feature components in parallel using three specialized agents...

<tool_use>
  <tool_name>Task</tool_name>
  <parameters>
    <description>Design data model</description>
    <prompt>[Agent 1 instructions]</prompt>
    <subagent_type>data-modeler</subagent_type>
  </parameters>
</tool_use>

<tool_use>
  <tool_name>Task</tool_name>
  <parameters>
    <description>Design API endpoints</description>
    <prompt>[Agent 2 instructions]</prompt>
    <subagent_type>api-designer</subagent_type>
  </parameters>
</tool_use>

<tool_use>
  <tool_name>Task</tool_name>
  <parameters>
    <description>Design UI components</description>
    <prompt>[Agent 3 instructions]</prompt>
    <subagent_type>ui-designer</subagent_type>
  </parameters>
</tool_use>
```

**Result**: All 3 agents run simultaneously, total time ≈ time of slowest agent

### ❌ WRONG: Sequential Execution

```markdown
I'm designing the data model...

<tool_use>
  <tool_name>Task</tool_name>
  <parameters>
    <description>Design data model</description>
    <prompt>[Agent 1 instructions]</prompt>
    <subagent_type>data-modeler</subagent_type>
  </parameters>
</tool_use>
```

[Wait for completion...]

```markdown
Now I'm designing the API...

<tool_use>
  <tool_name>Task</tool_name>
  <parameters>
    <description>Design API endpoints</description>
    <prompt>[Agent 2 instructions]</prompt>
    <subagent_type>api-designer</subagent_type>
  </parameters>
</tool_use>
```

[Wait for completion...]

```markdown
Finally designing the UI...

<tool_use>
  <tool_name>Task</tool_name>
  <parameters>
    <description>Design UI components</description>
    <prompt>[Agent 3 instructions]</prompt>
    <subagent_type>ui-designer</subagent_type>
  </parameters>
</tool_use>
```

**Result**: 3x slower! Each agent waits for previous to finish.

## Real-World Example: E-Commerce Feature

### Scenario
Building a product catalog feature with search, filtering, and cart integration.

### Phase 1: Sequential Planning (Required)

```markdown
Phase 1: Requirements Planning

<tool_use>
  <tool_name>Task</tool_name>
  <parameters>
    <description>Analyze product catalog requirements</description>
    <prompt>
You are requirements-planner.

Analyze the user request for a product catalog feature and create detailed requirements.

Input: User described wanting product search, filtering by category/price, and cart integration
Output: projects/product-catalog/planning/INITIAL.md

Create comprehensive requirements document with:
- Functional requirements
- Technical requirements
- Integration points
- Success criteria
    </prompt>
    <subagent_type>requirements-planner</subagent_type>
  </parameters>
</tool_use>
```

**Wait for completion** - INITIAL.md is now available

### Phase 2: Parallel Component Design ⚡

Now that we have INITIAL.md, three design tasks can run **simultaneously**:

```markdown
Phase 2: Component Design (Parallel Execution)

All three design agents will work simultaneously, each reading INITIAL.md and producing their specialized design document...

<tool_use>
  <tool_name>Task</tool_name>
  <parameters>
    <description>Design database schema</description>
    <prompt>
You are data-model-designer.

**Input**: Read `projects/product-catalog/planning/INITIAL.md`
**Output**: Create `projects/product-catalog/planning/DATA_MODEL.md`
**Folder**: `product-catalog` (use EXACTLY as provided)

Design the database schema for the product catalog including:
- Products table with search-optimized fields
- Categories with hierarchical structure
- Price ranges for filtering
- Cart integration foreign keys

Include:
- Table definitions with types
- Indexes for search performance
- Relationships and constraints
    </prompt>
    <subagent_type>data-model-designer</subagent_type>
  </parameters>
</tool_use>

<tool_use>
  <tool_name>Task</tool_name>
  <parameters>
    <description>Design API endpoints</description>
    <prompt>
You are api-designer.

**Input**: Read `projects/product-catalog/planning/INITIAL.md`
**Output**: Create `projects/product-catalog/planning/API_SPEC.md`
**Folder**: `product-catalog` (use EXACTLY as provided)

Design REST API endpoints for product catalog including:
- GET /products (with search and filter params)
- GET /products/:id
- GET /categories
- POST /cart/items

Include:
- Endpoint paths and methods
- Request/response schemas
- Query parameters for search/filter
- Error responses
    </prompt>
    <subagent_type>api-designer</subagent_type>
  </parameters>
</tool_use>

<tool_use>
  <tool_name>Task</tool_name>
  <parameters>
    <description>Design UI components</description>
    <prompt>
You are ui-designer.

**Input**: Read `projects/product-catalog/planning/INITIAL.md`
**Output**: Create `projects/product-catalog/planning/UI_DESIGN.md`
**Folder**: `product-catalog` (use EXACTLY as provided)

Design UI components for product catalog including:
- ProductList component with search
- FilterPanel for categories/price
- ProductCard display
- CartButton integration

Include:
- Component hierarchy
- Props interfaces
- State management approach
- User interactions
    </prompt>
    <subagent_type>ui-designer</subagent_type>
  </parameters>
</tool_use>
```

**All 3 agents run at the same time!**

### Phase 3: Sequential Implementation (Required)

After Phase 2 completes, implementation reads **all three** design documents:

```markdown
Phase 3: Implementation

Now I'll implement the product catalog using the three design documents...

[Read DATA_MODEL.md]
[Read API_SPEC.md]
[Read UI_DESIGN.md]

[Implement based on all three designs]
```

## Performance Comparison

### Sequential Execution Timeline
```
00:00 - 03:00  data-model-designer   (3 minutes)
03:00 - 06:00  api-designer          (3 minutes)
06:00 - 09:00  ui-designer           (3 minutes)
────────────────────────────────────────────────
Total: 9 minutes
```

### Parallel Execution Timeline
```
00:00 - 03:00  data-model-designer   (3 minutes)  ─┐
00:00 - 03:00  api-designer          (3 minutes)   ├─ All run simultaneously
00:00 - 03:00  ui-designer           (3 minutes)  ─┘
────────────────────────────────────────────────────
Total: 3 minutes (3x speedup!)
```

## Requirements for Parallel Execution

### ✅ Tasks MUST Be Independent

**Good - Truly Independent**:
```
Agent A: Reads INITIAL.md → Creates DATA_MODEL.md
Agent B: Reads INITIAL.md → Creates API_SPEC.md
Agent C: Reads INITIAL.md → Creates UI_DESIGN.md

✅ All read the SAME input
✅ All write to DIFFERENT outputs
✅ No dependencies between them
```

**Bad - Sequential Dependencies**:
```
Agent A: Creates DATA_MODEL.md
Agent B: Reads DATA_MODEL.md → Creates API_SPEC.md  ❌ Depends on A
Agent C: Reads API_SPEC.md → Creates UI_DESIGN.md   ❌ Depends on B

Must run sequentially!
```

### ✅ Each Agent Needs Complete Context

**Every parallel agent must receive**:
- All input file paths
- Exact output file path
- Exact folder name (for consistency)
- Complete task instructions
- Quality standards

**Bad - Incomplete Context**:
```xml
<prompt>Design the API endpoints</prompt>
❌ No input specified
❌ No output specified
❌ No folder name
```

**Good - Complete Context**:
```xml
<prompt>
You are api-designer.

Input: projects/product-catalog/planning/INITIAL.md
Output: projects/product-catalog/planning/API_SPEC.md
Folder: product-catalog

Design REST API endpoints with search and filter capabilities...
</prompt>
```

### ✅ No File Conflicts

**Good - Different Output Files**:
```
Agent A → projects/catalog/DATA_MODEL.md     ✅
Agent B → projects/catalog/API_SPEC.md       ✅
Agent C → projects/catalog/UI_DESIGN.md      ✅
```

**Bad - Same Output File**:
```
Agent A → projects/catalog/DESIGN.md         ❌
Agent B → projects/catalog/DESIGN.md         ❌ Conflict!
```

## Common Patterns for Parallel Execution

### Pattern 1: Multi-Component Design (Agent Factory)

**When**: Designing different aspects of same feature
**Example**: Prompts, Tools, Dependencies

```markdown
<tool_use> prompt-engineer   → prompts.md     </tool_use>
<tool_use> tool-integrator   → tools.md       </tool_use>
<tool_use> dependency-manager → dependencies.md </tool_use>
```

### Pattern 2: Multi-Service Implementation

**When**: Implementing independent microservices
**Example**: Auth service, Payment service, Notification service

```markdown
<tool_use> auth-implementer    → auth-service/    </tool_use>
<tool_use> payment-implementer → payment-service/ </tool_use>
<tool_use> notify-implementer  → notify-service/  </tool_use>
```

### Pattern 3: Multi-Layer Development

**When**: Building different architectural layers
**Example**: Database, API, Frontend

```markdown
<tool_use> db-developer       → database/       </tool_use>
<tool_use> api-developer      → backend/        </tool_use>
<tool_use> frontend-developer → frontend/       </tool_use>
```

## Decision Tree: Parallel vs Sequential

```
Does Task B need output from Task A?
    YES → Must run sequentially (A then B)
    NO  → Can run in parallel
        ↓
Do tasks modify the same file?
    YES → Must run sequentially
    NO  → Can run in parallel
        ↓
Can both tasks be fully specified upfront?
    YES → Should run in parallel! ✅
    NO  → Must run sequentially
```

## Troubleshooting

### Problem: Parallel invocation not working

**Symptom**: Agents run one at a time instead of simultaneously

**Solution**: Check your message structure
```markdown
✅ Correct:
- ONE message containing MULTIPLE <tool_use> blocks

❌ Wrong:
- Multiple messages, each with one <tool_use>
```

### Problem: Agents using different folder names

**Symptom**: Agent A creates `catalog/design.md`, Agent B looks for `product-catalog/design.md`

**Solution**: Pass EXACT folder name to every agent
```markdown
<prompt>
Folder: product-catalog (use EXACTLY as provided)
Output: projects/product-catalog/planning/design.md
</prompt>
```

### Problem: Agent can't find previous agent's output

**Symptom**: Agent B reports "file not found" for Agent A's output

**Diagnosis**: Check if tasks have dependencies
- If Agent B needs Agent A's output → They're NOT independent → Must run sequentially

## Validation Checklist

Before using parallel invocation:

- [ ] All agents work on independent tasks
- [ ] All agents read from EXISTING files (shared inputs OK)
- [ ] All agents write to DIFFERENT files (no conflicts)
- [ ] Each agent has complete context in its prompt
- [ ] All agents receive the EXACT SAME folder name
- [ ] No agent depends on another parallel agent's output
- [ ] All Task tool calls in SINGLE message

## Integration with Archon

When using Archon for task tracking:

```markdown
Phase 2: Parallel Component Design

# Update ALL task statuses to "doing" BEFORE invoking agents
mcp__archon__manage_task(action="update", task_id="task-1", status="doing")
mcp__archon__manage_task(action="update", task_id="task-2", status="doing")
mcp__archon__manage_task(action="update", task_id="task-3", status="doing")

# Then invoke all agents in parallel
<tool_use> agent-1 </tool_use>
<tool_use> agent-2 </tool_use>
<tool_use> agent-3 </tool_use>

# After completion, update ALL statuses to "done"
mcp__archon__manage_task(action="update", task_id="task-1", status="done")
mcp__archon__manage_task(action="update", task_id="task-2", status="done")
mcp__archon__manage_task(action="update", task_id="task-3", status="done")
```

## Summary

**Parallel Workflow Pattern**:
- ✅ 3x+ performance improvement
- ✅ Single message with multiple Task tool calls
- ✅ Independent tasks only
- ✅ Shared inputs, different outputs
- ✅ Complete context for each agent
- ✅ Exact folder names across all agents

**When to use**:
- Multiple independent tasks
- Different output files
- Tasks fully specifiable upfront
- Performance matters

**When NOT to use**:
- Task dependencies exist
- Same output file
- Iterative refinement needed
- Tasks require coordination

---

See [markdown-comms.md](./markdown-comms.md) for the communication protocol that enables these patterns.

For reference implementation, see [.claude/orchestrators/agent-factory.md](../../.claude/orchestrators/agent-factory.md) Phase 2.
