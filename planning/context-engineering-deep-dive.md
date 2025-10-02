# Context Engineering Deep Dive - Planning Document

## Video Summary: "I Built My Claude Code Subagents DREAM TEAM"

### Key Insights from Cole's Workflow

**Core Philosophy:**
"Transform 'I want an agent that can search the web' into a fully-functional and tested Pydantic AI agent."

**The Workflow is an Agent Factory:**
1. User makes high-level request
2. Claude asks clarifying questions (Phase 0)
3. Creates Archon project and distributes tasks
4. Invokes specialized subagents in sequence/parallel
5. Delivers complete, tested agent

### The 5 Phases:

#### Phase 0: Clarification
- Recognize agent creation request
- Ask 2-3 targeted questions
- STOP and WAIT for user responses
- Create agent folder (snake_case naming)

#### Phase 1: Requirements Planning
- **Subagent:** pydantic-ai-planner
- Output: `agents/[agent_name]/planning/INITIAL.md`
- Does web research, looks at docs
- Creates focused, MVP-style requirements

#### Phase 2: Parallel Component Planning (ALL AT ONCE)
- **pydantic-ai-prompt-engineer** → `planning/prompts.md`
- **pydantic-ai-tool-integrator** → `planning/tools.md`
- **pydantic-ai-dependency-manager** → `planning/dependencies.md`
- CRITICAL: Invoke all three in SINGLE message for true parallelism

#### Phase 3: Implementation
- **Main Claude Code** (not a subagent)
- Reads all 4 markdown files from planning/
- Uses Archon RAG for Pydantic AI patterns
- Creates full agent implementation

#### Phase 4: Validation
- **Subagent:** pydantic-ai-validator
- Creates comprehensive test suite
- Validates against INITIAL.md requirements
- Generates validation report

#### Phase 5: Delivery
- Main Claude Code
- Documentation and final polish
- Update Archon with completion

## Agent Factory Structure Analysis

### From agent-factory-with-subagents Use Case:

**Directory Structure:**
```
agent-factory-with-subagents/
├── CLAUDE.md                  # Global orchestration rules (16KB!)
├── .claude/
│   └── agents/                # Subagent definitions
│       ├── pydantic-ai-planner.md
│       ├── pydantic-ai-prompt-engineer.md
│       ├── pydantic-ai-tool-integrator.md
│       ├── pydantic-ai-dependency-manager.md
│       └── pydantic-ai-validator.md
└── agents/                    # Generated agent implementations
    └── rag_agent/             # Example output
        ├── planning/          # All planning docs
        │   ├── INITIAL.md
        │   ├── prompts.md
        │   ├── tools.md
        │   └── dependencies.md
        ├── agent.py
        ├── cli.py
        ├── tools.py
        ├── prompts.py
        ├── dependencies.py
        ├── providers.py
        ├── settings.py
        ├── tests/
        └── README.md
```

### Key Patterns:

**1. Markdown Files as Communication Layer**
- Subagents don't share context
- Planning docs are the handoff mechanism
- Each subagent reads initial.md, outputs its own md

**2. CLAUDE.md is the Orchestrator**
- Defines trigger patterns
- Specifies phase sequence
- Describes Archon integration
- Contains all workflow logic

**3. Archon Integration (Optional but Powerful)**
- Creates project for agent being built
- Creates tasks for each workflow phase
- Updates task status as phases complete
- Provides RAG access to Pydantic AI docs
- Tracks all context in database

**4. Subagent Specifications**
Each subagent markdown has:
```yaml
name: "Agent Name"
description: "What it does (for triggering)"
tools: ["list", "of", "tools"]
model: "claude-sonnet-4-5"
color: "blue"

# Then the full system prompt
```

## What This Means for Vibes

### Current Understanding:

**We Have:**
- Basic PRP workflow (generate-prp, execute-prp)
- prps/templates/prp_base.md
- EXAMPLE_multi_agent_prp.md
- Empty agents/ and examples/ directories

**We Need to Add:**

### 1. Subagent Infrastructure
```
/workspace/vibes/.claude/agents/
├── README.md                    # How to create/use subagents
├── research-agent.md            # For web research tasks
├── documentation-agent.md       # For doc generation
├── code-reviewer-agent.md       # For PR reviews
├── test-writer-agent.md         # For test generation
└── architecture-planner.md      # For system design
```

### 2. Examples Directory Structure
```
/workspace/vibes/examples/
├── README.md                    # Philosophy and patterns
├── subagents/
│   ├── simple-subagent.md       # Minimal subagent example
│   └── specialized-subagent.md  # Complex subagent with tools
├── agents/
│   ├── simple_agent.py          # Single agent pattern
│   └── multi_agent_workflow.py  # Agent delegation
├── workflows/
│   ├── prp-workflow.md          # Full PRP example
│   └── parallel-agents.md       # Parallel subagent pattern
└── tools/
    ├── api_integration.py       # API tool pattern
    └── file_operations.py       # File tool pattern
```

### 3. Templates for Agent Creation
```
/workspace/vibes/prps/templates/
├── prp_base.md                  # ✅ Already exists
├── subagent_template.md         # NEW: For creating subagents
├── agent_prp_template.md        # NEW: For agent projects
└── workflow_template.md         # NEW: For complex workflows
```

### 4. Workflow Commands
```
/workspace/vibes/.claude/commands/
├── generate-prp.md              # ✅ Exists
├── execute-prp.md               # ✅ Exists
├── spawn-subagent.md            # NEW: Create new subagent
├── create-agent-workflow.md     # NEW: Set up agent factory
└── validate-agent.md            # NEW: Run validation suite
```

### 5. Planning Directories
```
/workspace/vibes/prps/
├── templates/
├── active/                      # NEW: Current PRPs
├── completed/                   # NEW: Finished PRPs
└── archived/                    # NEW: Old/deprecated PRPs
```

## Critical Insights from Video:

### 1. **Sub agents != New Technology**
"Sub agents are really just prompts" - but the structured approach is key

### 2. **Context Window Management**
- Subagents don't pollute main conversation
- Prevents hitting autocompact in Claude Code
- Markdown files as explicit communication

### 3. **Parallel Invocation Pattern**
Must invoke multiple subagents in SINGLE message for true parallelism:
```
❌ WRONG: Invoke planner, wait, invoke prompt engineer
✅ RIGHT: Single message with three tool invocations
```

### 4. **Archon as Optional Enhancement**
- Not required but adds significant value
- Task management across agents
- Knowledge base for patterns
- Tracking and documentation

### 5. **Workflow Adaptability**
"This workflow will apply no matter what you want to create"
- Front-end apps: components, CSS, dependencies
- Backend APIs: routes, middleware, database
- Any software: split into plannable components

## Examples to Port to Vibes:

From context-engineering-intro repo:

### 1. agent-factory-with-subagents (PRIMARY)
**Port These:**
- CLAUDE.md workflow orchestration pattern
- All 5 subagent definitions
- Planning folder structure
- Generated agent structure (rag_agent as reference)

### 2. pydantic-ai use case
**Port These:**
- Agent creation patterns
- Tool integration examples
- Provider configuration
- Testing patterns

### 3. mcp-server use case
**Study for:**
- MCP server patterns
- Tool definitions
- Server architecture

### 4. template-generator use case
**Study for:**
- Template creation patterns
- Dynamic generation approaches

## Recommended Examples for Vibes:

### Simple Examples (Start Here):
1. **simple-subagent-example/**
   - Single subagent doing one thing
   - Clear input/output with markdown
   - Minimal dependencies

2. **basic-agent-workflow/**
   - 3-phase workflow (plan → implement → validate)
   - Shows markdown communication
   - No Archon complexity

3. **api-tool-integration/**
   - How to add external API as tool
   - Environment variable management
   - Error handling patterns

### Intermediate Examples:
4. **parallel-subagents-example/**
   - Multiple subagents invoked at once
   - Shows proper parallel pattern
   - Task coordination

5. **agent-with-tools/**
   - Complete Pydantic AI agent
   - Multiple tools
   - Structured output

### Advanced Examples:
6. **agent-factory-mini/**
   - Simplified version of Cole's factory
   - 3 subagents instead of 5
   - Works without Archon

7. **prp-with-subagents/**
   - Combines PRP methodology
   - Uses subagents for implementation
   - Complete workflow demo

## Action Items for INITIAL.md Update:

### Add These Sections:

**1. Subagent Examples Section:**
- Simple subagent (single purpose)
- Specialized subagent (with tools)
- Parallel subagent coordination
- Markdown communication patterns

**2. Workflow Examples Section:**
- PRP + subagents integration
- Agent factory pattern (simplified)
- Parallel vs sequential invocation
- Context passing strategies

**3. Tool Integration Examples:**
- API tool pattern
- File operation tools
- MCP server tools
- Custom tool creation

**4. Templates to Create:**
- subagent_template.md (from agent-factory pattern)
- agent_workflow_template.md (simplified factory)
- tool_template.md (for tool creation)

**5. Commands to Create:**
- spawn-subagent.md
- create-agent-workflow.md
- validate-workflow.md

## Files to Reference in Updated INITIAL.md:

### From Cloned Repo:
```yaml
primary_reference:
  - path: use-cases/agent-factory-with-subagents/CLAUDE.md
    why: Complete workflow orchestration pattern
  
  - path: use-cases/agent-factory-with-subagents/.claude/agents/
    why: All 5 subagent definitions as templates
  
  - path: use-cases/agent-factory-with-subagents/agents/rag_agent/
    why: Example of generated agent structure

secondary_references:
  - path: use-cases/pydantic-ai/
    why: Pydantic AI patterns and examples
  
  - path: use-cases/mcp-server/
    why: MCP server architecture patterns
  
  - path: claude-code-full-guide/
    why: Advanced Claude Code patterns
```

## Key Differences from Original INITIAL.md:

**Original Focus:**
- Basic directory structure
- Simple templates
- Minimal examples

**Enhanced Focus (Based on Deep Dive):**
- **Subagent infrastructure** (most important!)
- **Workflow orchestration patterns**
- **Parallel invocation strategies**
- **Markdown-based communication**
- **Optional Archon integration**
- **Complete agent generation examples**

## Next Steps:

1. **Update INITIAL.md** with subagent focus
2. **Generate comprehensive PRP** including all patterns
3. **Port key examples** from agent-factory
4. **Create subagent templates**
5. **Test workflow** with simple agent creation

---

**Key Takeaway:** 
The agent-factory pattern with subagents is MORE important than we initially thought. This should be a primary focus of the integration, not just an afterthought.

The workflow: User Request → Clarify → Parallel Planning → Implementation → Validation
The key: Markdown files as communication, subagents as specialists, orchestrator in CLAUDE.md
