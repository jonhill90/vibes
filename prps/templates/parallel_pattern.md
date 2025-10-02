# Parallel Invocation Pattern for Claude Code Subagents

## Overview

This template documents the critical pattern for invoking multiple subagents in parallel using Claude Code. Parallel execution dramatically reduces workflow time by running independent tasks simultaneously.

## The Critical Pattern

### ✅ CORRECT: Single Message with Multiple Tool Calls

When you need to invoke multiple subagents that work independently, you MUST send a SINGLE message containing MULTIPLE Task tool invocations:

```
Send ONE response with THREE (or more) Task tool uses:

<response to user explaining what you're doing>

<tool_use>
  <tool_name>Task</tool_name>
  <parameters>
    <description>First subagent task</description>
    <prompt>Detailed instructions for subagent 1...</prompt>
    <subagent_type>subagent-1-name</subagent_type>
  </parameters>
</tool_use>

<tool_use>
  <tool_name>Task</tool_name>
  <parameters>
    <description>Second subagent task</description>
    <prompt>Detailed instructions for subagent 2...</prompt>
    <subagent_type>subagent-2-name</subagent_type>
  </parameters>
</tool_use>

<tool_use>
  <tool_name>Task</tool_name>
  <parameters>
    <description>Third subagent task</description>
    <prompt>Detailed instructions for subagent 3...</prompt>
    <subagent_type>subagent-3-name</subagent_type>
  </parameters>
</tool_use>
```

### ❌ WRONG: Sequential Invocation

DO NOT invoke subagents one at a time across multiple messages:

```
Message 1: Invoke subagent-1
[Wait for completion]

Message 2: Invoke subagent-2
[Wait for completion]

Message 3: Invoke subagent-3
[Wait for completion]
```

This is 3x slower and defeats the purpose of parallel execution!

## Real Example: Agent Factory Phase 2

In the agent factory workflow, Phase 2 requires three subagents to work in parallel:

### Correct Implementation

```markdown
I'm now building the agent components in parallel using three specialized subagents:

1. **Prompt Engineer**: Designing system prompts
2. **Tool Integrator**: Planning tool implementations
3. **Dependency Manager**: Configuring dependencies

All three will work simultaneously based on the INITIAL.md requirements...

<tool_use>
  <tool_name>Task</tool_name>
  <parameters>
    <description>Design system prompts</description>
    <prompt>
You are the pydantic-ai-prompt-engineer. Read the requirements from:
agents/web_search_agent/planning/INITIAL.md

Create a system prompt specification in:
agents/web_search_agent/planning/prompts.md

The prompt should be 100-300 words, focused on web search functionality.
    </prompt>
    <subagent_type>pydantic-ai-prompt-engineer</subagent_type>
  </parameters>
</tool_use>

<tool_use>
  <tool_name>Task</tool_name>
  <parameters>
    <description>Plan tool implementations</description>
    <prompt>
You are the pydantic-ai-tool-integrator. Read the requirements from:
agents/web_search_agent/planning/INITIAL.md

Create tool specifications in:
agents/web_search_agent/planning/tools.md

Specify 2-3 essential tools for web search functionality.
    </prompt>
    <subagent_type>pydantic-ai-tool-integrator</subagent_type>
  </parameters>
</tool_use>

<tool_use>
  <tool_name>Task</tool_name>
  <parameters>
    <description>Configure dependencies</description>
    <prompt>
You are the pydantic-ai-dependency-manager. Read the requirements from:
agents/web_search_agent/planning/INITIAL.md

Create dependency specifications in:
agents/web_search_agent/planning/dependencies.md

Specify minimal env vars, packages, and model provider configuration.
    </prompt>
    <subagent_type>pydantic-ai-dependency-manager</subagent_type>
  </parameters>
</tool_use>
```

## Why This Works

1. **True Parallelism**: Claude Code executes all tool calls simultaneously
2. **Faster Execution**: 3 tasks complete in the time of 1
3. **Independent Work**: Each subagent works on its own file without conflicts
4. **Atomic Operations**: Each subagent has clear inputs and outputs

## When to Use Parallel Invocation

Use this pattern when:
- ✅ Tasks are **independent** (don't depend on each other's output)
- ✅ Tasks work on **different files** (no conflicts)
- ✅ Tasks can be **clearly specified upfront** (no iterative refinement needed)
- ✅ You want to **minimize total execution time**

Don't use this pattern when:
- ❌ Task B depends on output from Task A
- ❌ Tasks modify the same file
- ❌ You need to review Task A before starting Task B
- ❌ Tasks require sequential coordination

## Common Mistakes

### Mistake 1: Forgetting to Pass Context

```markdown
❌ WRONG:
<prompt>Create system prompts for the agent</prompt>

✅ RIGHT:
<prompt>
You are pydantic-ai-prompt-engineer.
Read requirements from: agents/web_search_agent/planning/INITIAL.md
Create output at: agents/web_search_agent/planning/prompts.md
Use the EXACT folder name "web_search_agent" in your output path.
</prompt>
```

### Mistake 2: Not Using Exact Folder Names

All subagents must use the **EXACT SAME** folder name:

```markdown
✅ All use: agents/web_search_agent/planning/
❌ Mixed: agents/web_search/, agents/search_agent/, agents/websearch/
```

### Mistake 3: Creating Dependencies Between Parallel Tasks

```markdown
❌ WRONG:
Subagent 1: Analyze requirements and create summary
Subagent 2: Read summary from Subagent 1 and create implementation

✅ RIGHT:
Subagent 1: Analyze requirements and create INITIAL.md
Subagent 2: Read INITIAL.md (already exists) and create prompts.md
Subagent 3: Read INITIAL.md (already exists) and create tools.md
```

## Debugging Parallel Execution

If parallel invocation isn't working:

1. **Check message structure**: Ensure all Task tools are in ONE message
2. **Verify independence**: Confirm tasks don't depend on each other
3. **Check file paths**: Ensure no path conflicts
4. **Review prompts**: Each subagent should have complete context

## Performance Comparison

**Sequential Execution**:
- Task 1: 3 minutes
- Task 2: 3 minutes
- Task 3: 3 minutes
- **Total: 9 minutes**

**Parallel Execution**:
- All tasks: ~3 minutes (simultaneous)
- **Total: 3 minutes**

**Speedup: 3x faster!**

## Integration with Workflows

### Agent Factory Pattern

```
Phase 1 (Sequential):
└─> planner creates INITIAL.md

Phase 2 (Parallel):
├─> prompt-engineer reads INITIAL.md → creates prompts.md
├─> tool-integrator reads INITIAL.md → creates tools.md
└─> dependency-manager reads INITIAL.md → creates dependencies.md

Phase 3 (Sequential):
└─> main Claude reads all 4 files → implements agent
```

### Multi-Feature Development Pattern

```
Parallel feature implementation:
├─> Feature 1: Auth system
├─> Feature 2: API endpoints
└─> Feature 3: Database models

Each works on separate files, can run in parallel.
```

## Best Practices

1. **Clear Separation**: Each subagent should have a distinct responsibility
2. **Complete Context**: Pass all necessary information in the prompt
3. **Explicit Outputs**: Specify exact file paths for outputs
4. **Shared Inputs**: All parallel tasks can read the same input file(s)
5. **No Side Effects**: Subagents shouldn't modify shared state

## Template for Your Workflows

```markdown
I'm executing [N] tasks in parallel:

[Brief explanation of what each task does]

<tool_use>
  <tool_name>Task</tool_name>
  <parameters>
    <description>[5-10 word description]</description>
    <prompt>
You are [subagent-name].

Input: [What to read]
Output: [Where to write]
Task: [What to do]

[Detailed instructions...]
    </prompt>
    <subagent_type>[subagent-type]</subagent_type>
  </parameters>
</tool_use>

[Repeat for each parallel task]
```

## Remember

- **One Message**: All tool calls in single response
- **Independence**: Tasks must not depend on each other
- **Clear Context**: Each subagent gets complete instructions
- **Exact Names**: Use identical folder/file names across all tasks
- **Performance**: 3+ parallel tasks = significant time savings

---

Master this pattern to build fast, efficient multi-agent workflows!
