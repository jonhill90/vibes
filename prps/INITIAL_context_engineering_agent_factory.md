# Context Engineering Agent Factory Integration

## FEATURE:
Integrate the complete Agent Factory pattern with subagents from coleam00/context-engineering-intro. This is the **FULL** version implementing Cole's 5-phase workflow with specialized subagents, parallel invocation, and optional Archon integration.

## GOAL:
Transform Vibes into an agent factory where:
1. Users describe agents at high level
2. Specialized subagents handle planning, design, and validation
3. Parallel workflow speeds up development
4. Markdown files serve as communication protocol
5. Optional Archon provides task tracking and knowledge
6. Complete, tested agents delivered automatically

## EXAMPLES:

**From Cole's Video & agent-factory-with-subagents:**

The 5-Phase Workflow:
```
Phase 0: Clarification
└─> Ask 2-3 questions, create agent folder

Phase 1: Requirements Planning
└─> pydantic-ai-planner → planning/INITIAL.md

Phase 2: Parallel Component Planning (ALL AT ONCE)
├─> pydantic-ai-prompt-engineer → planning/prompts.md
├─> pydantic-ai-tool-integrator → planning/tools.md  
└─> pydantic-ai-dependency-manager → planning/dependencies.md

Phase 3: Implementation
└─> Main Claude Code reads all 4 .md files, implements

Phase 4: Validation
└─> pydantic-ai-validator → tests/, VALIDATION_REPORT.md

Phase 5: Delivery
└─> Documentation, cleanup, handoff
```

**Desired Structure:**
```
/workspace/vibes/
├── .claude/
│   ├── agents/                    # Subagent definitions
│   │   ├── README.md              # How subagents work
│   │   ├── planner.md             # Requirements analysis
│   │   ├── prompt-engineer.md     # System prompt design
│   │   ├── tool-integrator.md     # Tool planning
│   │   ├── dependency-manager.md  # Config & dependencies
│   │   └── validator.md           # Testing & validation
│   ├── commands/
│   │   ├── generate-prp.md        # ✅ Exists
│   │   ├── execute-prp.md         # ✅ Exists
│   │   ├── create-agent.md        # NEW: Invoke agent factory
│   │   └── list-prps.md           # NEW: List PRPs
│   └── orchestrators/             # NEW: Workflow definitions
│       ├── README.md
│       └── agent-factory.md       # Main orchestration logic
│
├── agents/                        # Generated agents go here
│   └── [agent_name]/
│       ├── planning/              # Markdown communication layer
│       │   ├── INITIAL.md
│       │   ├── prompts.md
│       │   ├── tools.md
│       │   └── dependencies.md
│       ├── agent.py
│       ├── cli.py
│       ├── tools.py
│       ├── prompts.py
│       ├── dependencies.py
│       ├── providers.py
│       ├── settings.py
│       ├── tests/
│       └── README.md
│
├── examples/
│   ├── README.md
│   ├── subagents/
│   │   ├── simple-subagent.md     # Single specialized agent
│   │   ├── parallel-workflow.md   # 3 agents simultaneously
│   │   └── markdown-comms.md      # Communication protocol
│   ├── agents/
│   │   ├── minimal-agent/         # Simple Pydantic AI agent
│   │   └── rag-agent-example/     # Full factory output
│   ├── workflows/
│   │   ├── agent-factory-lite/    # Simplified 3-phase
│   │   ├── parallel-invocation/   # How to invoke parallel
│   │   └── prp-with-subagents/    # PRP + subagents combo
│   └── tools/
│       ├── api_integration.py
│       └── file_operations.py
│
└── prps/
    ├── templates/
    │   ├── prp_base.md            # ✅ Exists
    │   ├── subagent_template.md   # NEW: Create subagents
    │   ├── agent_workflow.md      # NEW: Multi-phase workflows
    │   └── parallel_pattern.md    # NEW: Parallel invocation
    ├── active/                     # ✅ From foundation version
    ├── completed/                  # ✅ From foundation version
    └── archived/                   # ✅ From foundation version
```

## DOCUMENTATION:

**Primary References:**
- https://www.youtube.com/watch?v=HJ9VvIG3Rps (Cole's video)
- /workspace/vibes/repos/context-engineering-intro/use-cases/agent-factory-with-subagents/
  - CLAUDE.md (16KB orchestration rules)
  - .claude/agents/ (all 5 subagent definitions)
  - agents/rag_agent/ (example generated agent)
- https://docs.claude.com/en/docs/claude-code/subagents

**Video Transcript Key Insights:**
- "Sub agents are really just prompts, but the highly structured approach is a thing of beauty"
- "Markdown files as communication layer prevents context window pollution"
- "Parallel invocation in SINGLE message is critical"
- "Archon optional but adds significant value for task tracking"

## KEY REQUIREMENTS:

### 1. Subagent Infrastructure

**Create 5 Core Subagents** (port from agent-factory-with-subagents):

**.claude/agents/planner.md:**
```markdown
name: "Requirements Planner"
description: "Analyzes requirements and creates comprehensive INITIAL.md specification. Use when starting any agent development to define scope and architecture."
tools: ["web_search", "archon:rag_search_knowledge_base"]
model: "claude-sonnet-4-5"
color: "blue"

# System Prompt
You are a requirements analysis specialist...
[Port from pydantic-ai-planner.md]
```

**.claude/agents/prompt-engineer.md:**
```markdown
name: "Prompt Engineer"
description: "Designs system prompts for AI agents. Creates prompts.md with static and dynamic prompt specifications."
tools: ["web_search", "archon:rag_search_knowledge_base"]
model: "claude-sonnet-4-5"
color: "orange"

# System Prompt
You are a prompt engineering specialist...
[Port from pydantic-ai-prompt-engineer.md]
```

**.claude/agents/tool-integrator.md:**
```markdown
name: "Tool Integrator"
description: "Plans tool integrations for agents. Creates tools.md with tool specifications and implementation guidance."
tools: ["web_search", "archon:rag_search_knowledge_base"]
model: "claude-sonnet-4-5"
color: "green"

# System Prompt
You are a tool integration specialist...
[Port from pydantic-ai-tool-integrator.md]
```

**.claude/agents/dependency-manager.md:**
```markdown
name: "Dependency Manager"
description: "Manages dependencies and configuration. Creates dependencies.md with env vars, packages, and setup requirements."
tools: ["web_search"]
model: "claude-sonnet-4-5"
color: "purple"

# System Prompt
You are a dependency management specialist...
[Port from pydantic-ai-dependency-manager.md]
```

**.claude/agents/validator.md:**
```markdown
name: "Agent Validator"
description: "Creates comprehensive test suites and validates agent implementations. Generates validation report."
tools: ["vibes:run_command"]
model: "claude-sonnet-4-5"
color: "red"

# System Prompt
You are a testing and validation specialist...
[Port from pydantic-ai-validator.md]
```

### 2. Orchestration Workflow

**.claude/orchestrators/agent-factory.md:**
Port the complete workflow from agent-factory-with-subagents/CLAUDE.md:

```markdown
# Agent Factory Orchestration

## Trigger Patterns
When user request contains:
- "Build an AI agent that..."
- "Create an agent for..."
- "I want an agent that can..."

## Phase 0: Clarification
1. Recognize agent creation request
2. Ask 2-3 targeted questions
3. STOP and WAIT for responses
4. Create agents/[agent_name]/ directory
5. Determine if Archon is available

## Phase 1: Requirements Planning
Invoke: planner subagent
Input: User request + clarifications
Output: agents/[agent_name]/planning/INITIAL.md

## Phase 2: Parallel Component Planning
⚠️ CRITICAL: Invoke ALL THREE in SINGLE message

Invoke simultaneously:
- prompt-engineer → planning/prompts.md
- tool-integrator → planning/tools.md
- dependency-manager → planning/dependencies.md

Input for all: planning/INITIAL.md
Context: Each reads INITIAL.md independently

## Phase 3: Implementation
Actor: Main Claude Code (not subagent)
1. Read all 4 planning markdown files
2. Use Archon RAG for Pydantic AI patterns (if available)
3. Implement complete agent
4. Create all supporting files

## Phase 4: Validation
Invoke: validator subagent
Input: Complete agent implementation
Output: tests/ directory + VALIDATION_REPORT.md

## Phase 5: Delivery
Actor: Main Claude Code
1. Final documentation
2. README generation
3. Update Archon project (if available)
4. Summary report to user

## Archon Integration (Optional)
If Archon available:
1. Create project for agent
2. Create 7 tasks (one per phase)
3. Update task status as progressing
4. Use RAG for documentation lookup
5. Store planning docs in Archon
```

### 3. Commands

**.claude/commands/create-agent.md:**
```markdown
# Create Agent

Invokes the agent factory workflow to create a complete AI agent.

## Usage
Describe the agent you want to build at a high level.
Example: "Build an agent that can search the web and summarize results"

## Workflow
This command triggers the full agent factory orchestration:
1. Clarifying questions
2. Requirements planning (planner subagent)
3. Parallel design (3 subagents simultaneously)
4. Implementation (main Claude)
5. Validation (validator subagent)
6. Delivery and documentation

## Output
Complete agent in agents/[agent_name]/ directory with:
- Planning documentation
- Full implementation
- Test suite
- README and usage examples
```

### 4. Examples

**examples/subagents/simple-subagent.md:**
Complete example of creating a single-purpose subagent:
- Name, description, tools, model
- System prompt structure
- Input/output specifications
- Usage examples

**examples/subagents/parallel-workflow.md:**
Demonstrates parallel invocation:
- How to invoke multiple subagents at once
- Single message pattern
- Coordination and handoff
- Markdown communication

**examples/workflows/agent-factory-lite/**
Simplified 3-phase workflow:
- Plan (1 subagent)
- Implement (main)
- Validate (1 subagent)

Good for learning before full 5-phase factory.

**examples/agents/rag-agent-example/**
Port the complete rag_agent from use-cases as reference:
- Shows what agent factory produces
- Complete structure
- Planning documentation
- Tests and validation

### 5. Templates

**prps/templates/subagent_template.md:**
```markdown
name: "Subagent Name"
description: "What this subagent does and when to invoke it. Include examples."
tools: ["tool1", "tool2"]
model: "claude-sonnet-4-5"
color: "blue"

# System Prompt

You are a [specialization] specialist for [purpose].

## Your Role
[Detailed role description]

## Input
You will receive: [specify input format]

## Output
You must create: [specify output file and format]

## Process
1. [Step 1]
2. [Step 2]
...

## Quality Standards
- [Criterion 1]
- [Criterion 2]
```

**prps/templates/agent_workflow.md:**
Template for creating multi-phase workflows:
- Phase definitions
- Subagent invocation patterns
- Parallel vs sequential
- Markdown communication
- Error handling

**prps/templates/parallel_pattern.md:**
Template specifically for parallel invocation:
- Single message structure
- Multiple tool calls
- Context management
- Output coordination

## SUCCESS CRITERIA:

### Structure
- [ ] 5 subagent definitions created in .claude/agents/
- [ ] agent-factory.md orchestrator created
- [ ] create-agent.md command created
- [ ] All example categories populated

### Functionality
- [ ] Can invoke planner subagent successfully
- [ ] Can invoke 3 subagents in parallel
- [ ] Markdown communication works between phases
- [ ] Generated agent has complete structure
- [ ] Validation subagent creates tests

### Examples & Documentation
- [ ] Each subagent has clear documentation
- [ ] Parallel invocation example works
- [ ] Agent factory lite demonstrates workflow
- [ ] rag-agent example is complete reference
- [ ] All templates are comprehensive

### Optional Archon
- [ ] Archon integration documented
- [ ] Task creation pattern shown
- [ ] RAG usage demonstrated
- [ ] Can work without Archon (graceful degradation)

## CONSTRAINTS:

**Critical Requirements:**
- Port subagents accurately from agent-factory use case
- Maintain markdown communication protocol
- Implement parallel invocation correctly
- Keep Archon optional (graceful degradation)

**Don't Break:**
- Existing PRP workflow
- Current .claude/commands/
- CLAUDE.md global rules
- prps/templates/prp_base.md

**Use:**
- vibes:run_command for all file operations
- Existing Vibes patterns and conventions
- Context from /workspace/vibes/repos/context-engineering-intro/

## VALIDATION:

```bash
# Verify subagent structure
ls -la /workspace/vibes/.claude/agents/
cat /workspace/vibes/.claude/agents/planner.md

# Check orchestrator
cat /workspace/vibes/.claude/orchestrators/agent-factory.md

# Verify commands
cat /workspace/vibes/.claude/commands/create-agent.md

# Check examples
ls -R /workspace/vibes/examples/subagents/
ls -R /workspace/vibes/examples/workflows/
ls -R /workspace/vibes/examples/agents/

# Verify templates
ls /workspace/vibes/prps/templates/
cat /workspace/vibes/prps/templates/subagent_template.md

# Test workflow (if possible)
# /create-agent "Build a simple web search agent"
```

## IMPLEMENTATION PHASES:

### Phase 1: Core Infrastructure (Most Important)
1. Create .claude/agents/ directory structure
2. Port all 5 subagent definitions
3. Create .claude/orchestrators/
4. Port agent-factory orchestration logic
5. Test single subagent invocation

### Phase 2: Parallel Workflow
1. Implement parallel invocation pattern
2. Test with 3 subagents simultaneously
3. Verify markdown communication
4. Ensure proper coordination

### Phase 3: Complete Workflow
1. Implement Phase 0 (clarification)
2. Wire up all 5 phases
3. Test end-to-end flow
4. Handle errors gracefully

### Phase 4: Examples & Templates
1. Create subagent examples
2. Add workflow examples
3. Port rag-agent as reference
4. Create all templates

### Phase 5: Commands & Documentation
1. Create create-agent.md command
2. Document Archon integration
3. Update main README
4. Write usage guides

## ARCHON INTEGRATION:

**If Archon Available:**
```python
# Phase 0: Create project
archon:manage_project("create", 
    title=f"{agent_name} Development",
    description=f"Agent factory workflow for {agent_name}")

# Create tasks for each phase
phases = [
    ("Requirements Analysis", "planner"),
    ("System Prompt Design", "prompt-engineer"),
    ("Tool Development Planning", "tool-integrator"),
    ("Dependency Configuration", "dependency-manager"),
    ("Agent Implementation", "Claude Code"),
    ("Validation & Testing", "validator"),
    ("Documentation & Delivery", "Claude Code")
]

for title, assignee in phases:
    archon:manage_task("create",
        project_id=project_id,
        title=title,
        assignee=assignee,
        status="todo")

# Update status as progressing
archon:manage_task("update",
    task_id=task_id,
    status="doing")  # or "done"

# Use RAG for documentation
archon:rag_search_knowledge_base(
    query="Pydantic AI agent patterns")
```

**If Archon Not Available:**
- Workflow still functions completely
- Use local file tracking instead
- Log progress to console
- No knowledge RAG (rely on web search)

## WHY THIS VERSION:

**Maximum Power Approach:**
- Complete agent factory capability
- Specialized subagents for each concern
- Parallel execution speeds development
- Professional-grade agent generation
- Optional but powerful Archon integration

**Real-World Value:**
- Automate agent creation completely
- Consistent, high-quality agents
- Comprehensive testing built-in
- Documentation generated automatically
- Scales to any agent complexity

**Learning Opportunity:**
- Master subagent patterns
- Understand workflow orchestration
- See parallel execution in action
- Learn markdown communication protocol
- Experience complete context engineering

## NOTES:

**From Video:**
- Cole emphasizes this workflow applies to ANY software, not just agents
- Can adapt pattern for: front-end apps, APIs, full-stack projects
- Key is splitting into plannable components with specialized subagents
- Markdown prevents context pollution (major benefit)
- Archon adds project management layer (optional but powerful)

**Critical Success Factor:**
The parallel invocation pattern MUST be implemented correctly:
```
❌ WRONG: Sequential calls to 3 subagents
✅ RIGHT: Single message with 3 tool invocations
```

This is emphasized multiple times in Cole's video and CLAUDE.md.
