# Agent Factory Lite - Simplified Workflow Example

A minimal 3-phase workflow demonstrating the core agent factory pattern without the complexity of the full 5-phase production implementation.

## Purpose

Learn the agent factory orchestration pattern through a simplified example:
- **Phase 1**: Planning (1 subagent)
- **Phase 2**: Design (2 subagents in parallel)
- **Phase 3**: Implementation (main Claude)

## Workflow Overview

```
Phase 1: Requirements
└─> planner creates requirements.md

Phase 2: Design (Parallel)
├─> tool-designer creates tools.md
└─> prompt-designer creates prompts.md

Phase 3: Implementation
└─> main Claude creates agent.py
```

## Key Concepts Demonstrated

### 1. Sequential Planning Phase

Phase 1 must complete before Phase 2 begins because Phase 2 agents need the requirements document.

### 2. Parallel Design Phase

Two designers work simultaneously:
- Both read the same `requirements.md`
- Both write to different files
- No dependencies between them
- 2x speedup!

### 3. Sequential Implementation

Phase 3 waits for Phase 2 because implementation needs both design documents.

## Files in This Example

- **[orchestrator.md](./orchestrator.md)** - The main workflow definition
- **[planner-agent.md](./planner-agent.md)** - Phase 1 requirements agent
- **[tool-designer-agent.md](./tool-designer-agent.md)** - Phase 2 tool design agent
- **[prompt-designer-agent.md](./prompt-designer-agent.md)** - Phase 2 prompt design agent
- **[sample-output/](./sample-output/)** - Example output from a run

## How to Use This Example

### Study the Workflow

1. **Read [orchestrator.md](./orchestrator.md)**
   - See phase definitions
   - Understand trigger patterns
   - Note parallel invocation in Phase 2

2. **Read subagent definitions**
   - [planner-agent.md](./planner-agent.md) - Sequential task
   - [tool-designer-agent.md](./tool-designer-agent.md) - Parallel task
   - [prompt-designer-agent.md](./prompt-designer-agent.md) - Parallel task

3. **Review sample output**
   - See actual workflow results
   - Understand file communication

### Adapt for Your Workflow

Copy and modify:

```bash
# Copy orchestrator as template
cp orchestrator.md .claude/orchestrators/my-workflow.md

# Copy agents as templates
cp planner-agent.md .claude/agents/my-planner.md
cp tool-designer-agent.md .claude/agents/my-designer-1.md
```

Then customize:
- Change trigger patterns
- Modify phase logic
- Adjust agent responsibilities
- Add/remove phases

## Comparison to Full Agent Factory

### Agent Factory Lite (This Example)

**Phases**: 3
- Planning
- Design (2 parallel agents)
- Implementation

**Purpose**: Learning and understanding core pattern

**Complexity**: Minimal - easy to follow

### Full Agent Factory (Production)

**Phases**: 5
- Clarification (interactive)
- Requirements planning
- Component design (3 parallel agents)
- Implementation
- Validation & testing

**Purpose**: Production-ready agent generation

**Complexity**: Complete - all quality gates

**Location**: [.claude/orchestrators/agent-factory.md](../../../.claude/orchestrators/agent-factory.md)

## Running This Workflow

### Manual Invocation

Trigger the workflow with a request pattern:

```
User: "Build a simple calculator agent"

Claude (recognizes pattern):
  Phase 1: Invoking planner...
  [creates requirements.md]

  Phase 2: Running designers in parallel...
  [invokes tool-designer AND prompt-designer simultaneously]
  [creates tools.md and prompts.md]

  Phase 3: Implementing agent...
  [reads all 3 files, creates agent.py]

  Done! Agent created.
```

### What Gets Created

```
simple_agent/
├── requirements.md    # From planner
├── tools.md          # From tool-designer
├── prompts.md        # From prompt-designer
└── agent.py          # From main Claude
```

## Learning Progression

### Start Here (Agent Factory Lite)

1. Understand basic 3-phase structure
2. Learn parallel invocation pattern
3. See markdown communication
4. Follow simple workflow

### Then Move to Full Factory

1. Add interactive clarification phase
2. Expand parallel design (3+ agents)
3. Add comprehensive validation
4. Include documentation phase
5. Integrate Archon tracking

## Key Takeaways

### Critical Patterns

**Sequential when dependencies exist**:
```
Phase 1 → requirements.md
         ↓
Phase 2 reads requirements.md
```

**Parallel when independent**:
```
requirements.md ──┬─> tool-designer → tools.md
                  └─> prompt-designer → prompts.md
```

**Markdown communication**:
```
Agent A writes structured markdown
         ↓
Agent B reads and extracts information
```

### Common Mistakes to Avoid

❌ **Running parallel agents sequentially**
```markdown
# WRONG - Three separate messages
<invoke tool-designer>
[wait]
<invoke prompt-designer>
```

✅ **Running parallel agents together**
```markdown
# RIGHT - One message, two invocations
<invoke tool-designer>
<invoke prompt-designer>
```

❌ **Creating dependencies in parallel phase**
```markdown
# WRONG
tool-designer creates tools.md
prompt-designer reads tools.md  # Dependency!
```

✅ **Keeping parallel tasks independent**
```markdown
# RIGHT
Both read requirements.md
Both write different outputs
No dependencies
```

## Next Steps

1. **Study this lite version** completely
2. **Review [sample-output/](./sample-output/)** to see results
3. **Read [parallel invocation pattern](../../agent-factory/parallel-workflow.md)**
4. **Examine [full agent factory](../../../.claude/orchestrators/agent-factory.md)**
5. **Build your own workflow** using templates

## Related Examples

- **Simple Subagent**: [examples/agent-factory/simple-subagent.md](../../agent-factory/simple-subagent.md)
- **Parallel Workflow**: [examples/agent-factory/parallel-workflow.md](../../agent-factory/parallel-workflow.md)
- **Markdown Communication**: [examples/agent-factory/markdown-comms.md](../../agent-factory/markdown-comms.md)
- **Complete Agent**: [examples/agents/rag-agent-example/](../../agents/rag-agent-example/)

---

**Master this lite version before tackling the full agent factory!**
