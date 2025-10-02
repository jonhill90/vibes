# Orchestrators

Orchestrators are workflow definitions for complex, multi-phase operations in Vibes. They coordinate the execution of multiple subagents and define the logic for autonomous workflows.

## What are Orchestrators?

Orchestrators differ from commands in that they:
- Define complex multi-phase workflows
- Coordinate multiple subagents working in parallel or sequence
- Handle state management across workflow phases
- Implement pattern-based recognition and automatic triggering
- Include graceful error handling and fallback strategies

## When to Create an Orchestrator

Create an orchestrator when you need to:
1. **Multi-Phase Workflows**: Coordinate 3+ distinct phases of work
2. **Parallel Execution**: Run multiple subagents simultaneously
3. **State Management**: Track progress across multiple steps
4. **Pattern Recognition**: Automatically trigger based on user requests
5. **Complex Coordination**: Manage handoffs between different agents

## Current Orchestrators

### agent-factory.md
Complete 5-phase workflow for autonomous AI agent development:
- Phase 0: Clarification (ask user questions)
- Phase 1: Requirements planning (planner subagent)
- Phase 2: Parallel component design (3 subagents simultaneously)
- Phase 3: Implementation (main Claude Code)
- Phase 4: Validation (validator subagent)
- Phase 5: Delivery and documentation

**Trigger Patterns**:
- "Build an AI agent that..."
- "Create an agent for..."
- "I need an agent that..."

## Orchestrator Structure

A well-designed orchestrator includes:

### 1. Trigger Patterns
```markdown
## Trigger Patterns
When user request contains:
- "pattern 1"
- "pattern 2"
- ...
```

### 2. Phase Definitions
```markdown
## Phase X: Phase Name
**Actor**: [Subagent name or "Main Claude"]
**Trigger**: [When this phase executes]
**Mode**: [AUTONOMOUS | INTERACTIVE | PARALLEL]

Actions:
1. Step 1
2. Step 2
...

Success Criteria:
- [ ] Criterion 1
- [ ] Criterion 2
```

### 3. Integration Points
```markdown
## Integration Points
- Archon (optional): Task tracking, RAG queries
- File System: State persistence
- Subagents: Invocation patterns
```

### 4. Error Handling
```markdown
## Error Handling
- If Phase X fails: [Fallback strategy]
- If resource unavailable: [Graceful degradation]
- If timeout: [Recovery approach]
```

## Best Practices

1. **Atomic Phases**: Each phase should be independently testable
2. **Clear Handoffs**: Document what each phase produces and consumes
3. **Parallel When Possible**: Use parallel execution for independent work
4. **Graceful Degradation**: Always have fallbacks for optional dependencies
5. **State Tracking**: Use Archon or files to track workflow progress
6. **Documentation**: Include examples of successful workflow execution

## Example: Parallel Invocation Pattern

For Phase 2 of agent-factory, we invoke 3 subagents in parallel:

```markdown
⚠️ CRITICAL: Use parallel tool invocation
Invoke ALL THREE in SINGLE message with multiple tool uses:
- prompt-engineer → planning/prompts.md
- tool-integrator → planning/tools.md
- dependency-manager → planning/dependencies.md

❌ WRONG: Sequential invocation (3 separate messages)
✅ RIGHT: Single message with 3 Task tool calls
```

## Creating a New Orchestrator

1. Create `[name].md` in this directory
2. Include trigger patterns for automatic recognition
3. Define all phases with clear success criteria
4. Document integration points and dependencies
5. Add error handling and fallback strategies
6. Test end-to-end workflow
7. Update this README with new orchestrator details

## Orchestrators vs Commands

**Commands** (`/.claude/commands/`):
- User-facing entry points
- Simple, direct actions
- Often delegate to orchestrators
- Example: `/create-agent` → triggers `agent-factory.md`

**Orchestrators** (`/.claude/orchestrators/`):
- Complex workflow definitions
- Multi-phase coordination
- Subagent management
- Example: `agent-factory.md` → 5-phase autonomous workflow

## Future Orchestrators

Potential orchestrators to create:
- `feature-implementation.md`: Multi-step feature development
- `bug-fix-workflow.md`: Issue analysis, fix, test, validate
- `documentation-update.md`: Comprehensive doc updates across files
- `refactoring-pipeline.md`: Safe, tested code refactoring
