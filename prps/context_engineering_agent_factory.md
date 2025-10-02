name: "Context Engineering Agent Factory - FULL Implementation"
description: |
  Complete agent factory system with 5 specialized subagents, parallel invocation,
  markdown communication protocol, and optional Archon integration. Transforms
  high-level user requests into production-ready Pydantic AI agents automatically.

---

## Goal
Build a complete AI Agent Factory in Vibes that automates the creation of production-ready Pydantic AI agents through a 5-phase workflow with specialized subagents, parallel execution, and comprehensive validation.

## Why
- **Automation**: Transform "build an agent that can X" into complete, tested agent automatically
- **Quality**: Ensure consistent, high-quality agents through specialized subagents and validation
- **Speed**: Parallel execution and clear workflow reduces agent development from hours to minutes
- **Scalability**: Reusable pattern applies to any AI agent, from simple to complex
- **Learning**: Demonstrates advanced context engineering patterns (subagents, parallel invocation, markdown communication)
- **Foundation**: Creates infrastructure for future multi-agent workflows beyond just agent creation

## What
Implement the complete agent factory pattern from coleam00/context-engineering-intro with:

### Core Components
1. **5 Specialized Subagents** in `.claude/agents/`:
   - `planner.md` - Requirements analysis and INITIAL.md creation
   - `prompt-engineer.md` - System prompt design and specifications
   - `tool-integrator.md` - Tool planning and API integrations
   - `dependency-manager.md` - Dependencies and configuration
   - `validator.md` - Testing, validation, and quality assurance

2. **Orchestration Workflow** in `.claude/orchestrators/`:
   - `agent-factory.md` - Complete 5-phase workflow orchestration
   - Trigger patterns, phase transitions, parallel invocation logic
   - Archon integration (optional) for project tracking

3. **Commands** in `.claude/commands/`:
   - `create-agent.md` - Invoke the agent factory workflow
   - Clear usage instructions and examples

4. **Examples** in `examples/`:
   - `subagents/simple-subagent.md` - Single subagent pattern
   - `subagents/parallel-workflow.md` - Parallel invocation example
   - `subagents/markdown-comms.md` - Communication protocol
   - `workflows/agent-factory-lite/` - Simplified 3-phase workflow
   - `agents/rag-agent-example/` - Complete factory output reference

5. **Templates** in `prps/templates/`:
   - `subagent_template.md` - Create new subagents
   - `agent_workflow.md` - Multi-phase workflow pattern
   - `parallel_pattern.md` - Parallel invocation template

### Success Criteria
- [ ] All 5 subagent definitions created and accurate
- [ ] Agent factory orchestrator created with complete workflow
- [ ] Can invoke planner subagent successfully
- [ ] Can invoke 3 subagents in parallel (single message)
- [ ] Markdown communication protocol works between phases
- [ ] Generated agents have complete structure (planning/, code, tests/)
- [ ] Validation subagent creates comprehensive test suite
- [ ] create-agent command functional
- [ ] All example categories populated with clear documentation
- [ ] Archon integration documented (with graceful degradation)
- [ ] End-to-end workflow tested

## All Needed Context

### Documentation & References
```yaml
# PRIMARY REFERENCES - Agent Factory Source
- url: https://github.com/coleam00/context-engineering-intro/tree/main/use-cases/agent-factory-with-subagents
  why: Complete agent factory implementation with all patterns
  critical: CLAUDE.md orchestration rules, 5 subagent definitions, example agent structure
  sections:
    - CLAUDE.md: Complete orchestration workflow (26KB)
    - .claude/agents/: All 5 subagent definitions
    - agents/rag_agent/: Complete example of factory output

- url: https://www.youtube.com/watch?v=HJ9VvIG3Rps
  title: "Cole's Agent Factory Video"
  why: Visual explanation of workflow, parallel invocation, markdown protocol
  critical: "Sub agents are just prompts, markdown prevents context pollution, parallel invocation is critical"

- url: https://docs.claude.com/en/docs/claude-code/subagents
  why: Official Claude Code subagent documentation
  critical: File format, invocation patterns, tool access, best practices
  sections:
    - Subagent file format (YAML frontmatter + markdown system prompt)
    - Automatic vs explicit invocation
    - Parallel execution patterns

# PYDANTIC AI REFERENCES
- url: https://ai.pydantic.dev/agents/
  why: Core Pydantic AI agent patterns
  critical: Agent creation, dependencies, tools, system prompts

- url: https://ai.pydantic.dev/tools/
  why: Function tools and toolsets patterns
  critical: @agent.tool vs @agent.tool_plain decorators, RunContext usage

- url: https://ai.pydantic.dev/multi-agent-applications/
  why: Multi-agent patterns and delegation
  critical: Agent coordination, result composition

# LOCAL REFERENCES - Existing Patterns
- file: /Users/jon/source/vibes/.claude/agents/documentation-manager.md
  why: Example of existing subagent structure to follow
  pattern: YAML frontmatter + markdown system prompt

- file: /Users/jon/source/vibes/.claude/agents/validation-gates.md
  why: Example validation specialist pattern

- file: /Users/jon/source/vibes/prps/templates/prp_base.md
  why: Template structure to follow for new templates

- file: /Users/jon/source/vibes/CLAUDE.md
  why: Global rules - CRITICAL: ARCHON-FIRST RULE, use Archon MCP not TodoWrite

# SOURCE FILES TO PORT
- file: /Users/jon/source/vibes/repos/context-engineering-intro/use-cases/agent-factory-with-subagents/CLAUDE.md
  why: Complete orchestration logic to port to agent-factory.md

- file: /Users/jon/source/vibes/repos/context-engineering-intro/use-cases/agent-factory-with-subagents/.claude/agents/pydantic-ai-planner.md
  why: Requirements planner subagent definition

- file: /Users/jon/source/vibes/repos/context-engineering-intro/use-cases/agent-factory-with-subagents/.claude/agents/pydantic-ai-prompt-engineer.md
  why: Prompt engineering subagent definition

- file: /Users/jon/source/vibes/repos/context-engineering-intro/use-cases/agent-factory-with-subagents/.claude/agents/pydantic-ai-tool-integrator.md
  why: Tool integration subagent definition

- file: /Users/jon/source/vibes/repos/context-engineering-intro/use-cases/agent-factory-with-subagents/.claude/agents/pydantic-ai-dependency-manager.md
  why: Dependency management subagent definition

- file: /Users/jon/source/vibes/repos/context-engineering-intro/use-cases/agent-factory-with-subagents/.claude/agents/pydantic-ai-validator.md
  why: Validation subagent definition

- file: /Users/jon/source/vibes/repos/context-engineering-intro/use-cases/agent-factory-with-subagents/agents/rag_agent/
  why: Complete example agent to port as reference
  includes: planning/ docs, agent.py, tools.py, tests/, README.md
```

### Current Codebase Tree
```bash
/Users/jon/source/vibes/
├── .claude/
│   ├── agents/                    # ✅ 2 existing agents (documentation-manager, validation-gates)
│   ├── commands/                  # ✅ 5 existing commands including generate-prp, execute-prp
│   └── settings.local.json
├── prps/
│   ├── templates/
│   │   └── prp_base.md           # ✅ Base template exists
│   ├── active/                    # ✅ From foundation version
│   ├── completed/                 # ✅ From foundation version
│   ├── archived/                  # ✅ From foundation version
│   └── [existing PRPs]
├── agents/                        # ✅ Empty, ready for generated agents
├── examples/                      # ⚠️  Needs population with subagent/workflow examples
├── mcp/                          # MCP servers (vibesbox, vibes)
├── CLAUDE.md                     # ✅ Global rules
└── README.md
```

### Desired Codebase Tree
```bash
/Users/jon/source/vibes/
├── .claude/
│   ├── agents/                    # Subagent definitions
│   │   ├── README.md              # NEW: How subagents work
│   │   ├── planner.md             # NEW: Requirements analysis
│   │   ├── prompt-engineer.md     # NEW: System prompt design
│   │   ├── tool-integrator.md     # NEW: Tool planning
│   │   ├── dependency-manager.md  # NEW: Config & dependencies
│   │   ├── validator.md           # NEW: Testing & validation
│   │   ├── documentation-manager.md  # ✅ Exists
│   │   └── validation-gates.md    # ✅ Exists
│   ├── commands/
│   │   ├── create-agent.md        # NEW: Invoke agent factory
│   │   ├── list-prps.md           # NEW: From foundation version
│   │   └── [existing commands]
│   └── orchestrators/             # NEW: Workflow definitions
│       ├── README.md
│       └── agent-factory.md       # NEW: Main orchestration logic
│
├── agents/                        # Generated agents directory
│   └── [agent_name]/
│       ├── planning/              # Markdown communication layer
│       │   ├── INITIAL.md         # From planner
│       │   ├── prompts.md         # From prompt-engineer
│       │   ├── tools.md           # From tool-integrator
│       │   └── dependencies.md    # From dependency-manager
│       ├── agent.py               # Main agent
│       ├── cli.py
│       ├── tools.py
│       ├── prompts.py
│       ├── dependencies.py
│       ├── providers.py
│       ├── settings.py
│       ├── tests/                 # From validator
│       └── README.md
│
├── examples/
│   ├── README.md                  # NEW: Guide to examples
│   ├── subagents/
│   │   ├── simple-subagent.md     # NEW: Single specialized agent
│   │   ├── parallel-workflow.md   # NEW: 3 agents simultaneously
│   │   └── markdown-comms.md      # NEW: Communication protocol
│   ├── agents/
│   │   ├── minimal-agent/         # NEW: Simple Pydantic AI agent
│   │   └── rag-agent-example/     # NEW: Full factory output (port from source)
│   ├── workflows/
│   │   ├── agent-factory-lite/    # NEW: Simplified 3-phase
│   │   ├── parallel-invocation/   # NEW: How to invoke parallel
│   │   └── prp-with-subagents/    # NEW: PRP + subagents combo
│   └── tools/
│       ├── api_integration.py     # ✅ From foundation version
│       └── file_operations.py     # ✅ From foundation version
│
└── prps/
    └── templates/
        ├── prp_base.md            # ✅ Exists
        ├── subagent_template.md   # NEW: Create subagents
        ├── agent_workflow.md      # NEW: Multi-phase workflows
        └── parallel_pattern.md    # NEW: Parallel invocation
```

### Known Gotchas & Library Quirks
```yaml
# CRITICAL PATTERNS
- CRITICAL: Parallel invocation MUST use SINGLE message with multiple Task tool calls
  ❌ WRONG: Invoke planner, wait, then invoke prompt-engineer, wait, then tool-integrator
  ✅ RIGHT: Single message with 3 Task tool invocations for Phase 2

- CRITICAL: Subagents output MARKDOWN specs during planning, NOT Python code
  Phase 2 subagents create planning/*.md files with specifications
  Phase 3 main Claude Code reads specs and implements Python

- CRITICAL: Folder name consistency - pass EXACT SAME folder name to all subagents
  Main agent determines folder name, passes to all subagents
  All subagents must use exact same path: agents/[FOLDER_NAME]/planning/

- CRITICAL: Archon integration is OPTIONAL - must work without it
  Check Archon availability first with mcp__archon__health_check
  If available: create project, tasks, use RAG
  If not: proceed with local tracking, web search only

- CRITICAL: Phase 0 MUST ask questions and WAIT for user response
  Don't create folders or invoke subagents until user answers
  Avoid assumptions to "keep process moving"

# SUBAGENT PATTERNS
- Pattern: Each subagent has "simplicity philosophy" - avoid over-engineering
  planner: Start simple, make it work, iterate
  prompt-engineer: Simple clear prompts, 100-300 words
  tool-integrator: 2-3 essential tools only
  dependency-manager: Minimal config, essential vars only
  validator: Comprehensive but focused tests

- Pattern: Subagent file format
  YAML frontmatter: name, description, tools, model, color
  Markdown body: System prompt with role, responsibilities, process

- Pattern: Tools specification format
  Context-aware: @agent.tool with RunContext[DepsType]
  Plain: @agent.tool_plain for simple functions
  All need clear docstrings for LLM understanding

# PYDANTIC AI GOTCHAS
- Gotcha: Use python-dotenv + load_dotenv() for env vars (not os.getenv alone)
- Gotcha: Agent.override() for testing with TestModel/FunctionModel
- Gotcha: result_type only needed for structured output, default is string
- Gotcha: Dependencies class for agent context (dataclass, not Pydantic model)
- Gotcha: Async patterns required for tools with external I/O

# VALIDATION GOTCHAS
- Gotcha: Validation gates must be executable by AI agent
  ✅ pytest tests/ -v (works)
  ❌ "manually test the endpoint" (doesn't work for AI)

- Gotcha: Markdown communication prevents context pollution
  Each subagent writes specs to planning/*.md
  Main agent reads all files at once in Phase 3
  Avoids passing large context between subagents
```

## Implementation Blueprint

### Phase 1: Core Infrastructure (MOST CRITICAL)
**Priority**: Highest - Foundation for everything else

```yaml
Task 1.1: Create Directory Structure
ACTION: Create directories
COMMANDS:
  - mkdir -p /Users/jon/source/vibes/.claude/orchestrators
  - mkdir -p /Users/jon/source/vibes/examples/subagents
  - mkdir -p /Users/jon/source/vibes/examples/workflows
  - mkdir -p /Users/jon/source/vibes/examples/agents
VERIFY: ls -R /Users/jon/source/vibes/.claude/ && ls -R /Users/jon/source/vibes/examples/

Task 1.2: Port Planner Subagent
CREATE: /Users/jon/source/vibes/.claude/agents/planner.md
PATTERN: Read source file, adapt to Vibes patterns
SOURCE: /Users/jon/source/vibes/repos/context-engineering-intro/use-cases/agent-factory-with-subagents/.claude/agents/pydantic-ai-planner.md
CONTENT:
  - YAML frontmatter: name: planner, description with "USE PROACTIVELY", tools, model, color
  - System prompt: Requirements analysis specialist philosophy
  - Responsibilities: Autonomous requirements gathering, INITIAL.md creation
  - Output: agents/[folder]/planning/INITIAL.md
  - Simplicity principles: Start simple, make it work, iterate
MODIFY: Update tools to match Vibes available tools (Read, Write, Grep, Glob, WebSearch)
CRITICAL: Emphasize SIMPLE, FOCUSED requirements (2-3 core features max)

Task 1.3: Port Prompt Engineer Subagent
CREATE: /Users/jon/source/vibes/.claude/agents/prompt-engineer.md
SOURCE: pydantic-ai-prompt-engineer.md
CONTENT:
  - YAML frontmatter with USE AUTOMATICALLY trigger
  - System prompt engineering specialist
  - Output: agents/[folder]/planning/prompts.md (MARKDOWN specs, not Python)
  - Philosophy: Simple, clear prompts (100-300 words)
CRITICAL: Output MARKDOWN file with prompt specifications, NOT Python code

Task 1.4: Port Tool Integrator Subagent
CREATE: /Users/jon/source/vibes/.claude/agents/tool-integrator.md
SOURCE: pydantic-ai-tool-integrator.md
CONTENT:
  - Tool development specialist
  - Output: agents/[folder]/planning/tools.md (MARKDOWN specs)
  - Philosophy: 2-3 essential tools only
  - Patterns: @agent.tool vs @agent.tool_plain
CRITICAL: Create tool SPECIFICATIONS in markdown, not implementations

Task 1.5: Port Dependency Manager Subagent
CREATE: /Users/jon/source/vibes/.claude/agents/dependency-manager.md
SOURCE: pydantic-ai-dependency-manager.md
CONTENT:
  - Dependency configuration specialist
  - Output: agents/[folder]/planning/dependencies.md
  - Philosophy: Minimal config, essential vars only
  - Use python-dotenv pattern

Task 1.6: Port Validator Subagent
CREATE: /Users/jon/source/vibes/.claude/agents/validator.md
SOURCE: pydantic-ai-validator.md
CONTENT:
  - Testing and validation specialist
  - Output: agents/[folder]/tests/ + VALIDATION_REPORT.md
  - Create comprehensive test suite
  - Test against INITIAL.md requirements
TOOLS: Bash (for running tests), Read, Write, Edit

Task 1.7: Create Subagents README
CREATE: /Users/jon/source/vibes/.claude/agents/README.md
CONTENT:
  - Overview of all subagents
  - When each is invoked (automatic vs explicit)
  - How they work together in agent factory
  - File format explanation
  - Best practices for creating new subagents
```

### Phase 2: Orchestration Workflow

```yaml
Task 2.1: Create Orchestrator Directory README
CREATE: /Users/jon/source/vibes/.claude/orchestrators/README.md
CONTENT:
  - What orchestrators are (workflow coordination files)
  - How they differ from subagents
  - When to use orchestrators vs commands
  - List of available orchestrators

Task 2.2: Create Agent Factory Orchestrator
CREATE: /Users/jon/source/vibes/.claude/orchestrators/agent-factory.md
SOURCE: Port from agent-factory-with-subagents/CLAUDE.md
CONTENT:
  - 🎯 Primary Directive: Trigger patterns, workflow enforcement
  - 🔄 Complete Factory Workflow:
    - Phase 0: Request Recognition & Clarification (ask questions, WAIT for answers)
    - Phase 1: Requirements Planning (invoke planner subagent)
    - Phase 2: Parallel Component Planning (invoke 3 subagents IN PARALLEL)
    - Phase 3: Agent Implementation (main Claude Code reads all planning/*.md)
    - Phase 4: Validation & Testing (invoke validator subagent)
    - Phase 5: Delivery & Documentation (main Claude Code)
  - 📋 Archon Task Management Protocol (optional):
    - Create project after Phase 0
    - Create 7 tasks for each phase
    - Update task status as progressing
    - Use RAG for documentation lookup
  - 🎭 Subagent Invocation Rules:
    - Automatic invocation based on phase
    - Manual override patterns
    - Parallel invocation pattern (CRITICAL: single message, multiple Task tools)
  - 📁 Output Directory Structure
  - 🚀 Quick Start Examples
  - 🛡️ Quality Assurance checklist

CRITICAL SECTION - Parallel Invocation Pattern:
```markdown
## Phase 2: Parallel Component Development ⚡

⚠️ CRITICAL: Use parallel tool invocation

Execute ALL THREE subagents SIMULTANEOUSLY in a SINGLE message:

❌ WRONG: Sequential calls
```python
invoke("prompt-engineer")  # Wait for result
invoke("tool-integrator")  # Wait for result
invoke("dependency-manager")  # Wait for result
```

✅ RIGHT: Parallel invocation
```python
# Single message with three Task tool invocations:
Task(subagent="prompt-engineer", ...)
Task(subagent="tool-integrator", ...)
Task(subagent="dependency-manager", ...)
# All three execute in parallel
```

Input for all: planning/INITIAL.md (each reads independently)
Output: planning/prompts.md, planning/tools.md, planning/dependencies.md
```

Task 2.3: Implement Archon Integration Pattern
LOCATION: Within agent-factory.md
CONTENT:
  - Health check pattern: mcp__archon__health_check
  - Project creation: manage_project("create", ...)
  - Task creation: 7 tasks (one per phase + sub-phases)
  - Task updates: status="doing" when starting, status="done" when complete
  - RAG usage: rag_search_knowledge_base for Pydantic AI patterns
  - Graceful degradation: If Archon unavailable, use local tracking
EXAMPLE:
```python
# After Phase 0, check Archon
health = mcp__archon__health_check()
if health.success:
    # Create project
    project = manage_project("create",
        title=f"{agent_name} Agent Development",
        description=f"Agent factory workflow for {agent_name}")

    # Create tasks
    tasks = [
        {"title": "Requirements Analysis", "assignee": "planner"},
        {"title": "System Prompt Design", "assignee": "prompt-engineer"},
        # ... (7 tasks total)
    ]
    # Update status as progressing
else:
    # Continue without Archon
```
```

### Phase 3: Parallel Workflow Implementation

```yaml
Task 3.1: Test Single Subagent Invocation
ACTION: Create test workflow
STEPS:
  1. Create test request: "Build a simple hello world agent"
  2. Verify planner can be invoked via Task tool
  3. Check output: agents/hello_world_agent/planning/INITIAL.md exists
  4. Validate content: INITIAL.md has all required sections
VALIDATION:
  - Subagent responds correctly
  - Output file created in correct location
  - Content follows expected structure

Task 3.2: Implement Parallel Invocation Pattern
ACTION: Create parallel invocation logic
PATTERN:
  - After Phase 1 (INITIAL.md created)
  - Invoke 3 subagents in SINGLE message:
    - prompt-engineer
    - tool-integrator
    - dependency-manager
  - All receive same input: planning/INITIAL.md
  - All output to planning/ directory
CODE PATTERN:
```python
# Phase 2: Parallel Component Planning
# CRITICAL: Single message with 3 Task tool invocations

# Update Archon tasks (if available)
if archon_available:
    update_task(task_2_id, status="doing")
    update_task(task_3_id, status="doing")
    update_task(task_4_id, status="doing")

# Invoke all three subagents in parallel
message_with_three_task_calls = f"""
Now executing Phase 2: Parallel Component Planning

Invoking three subagents simultaneously:
1. Prompt Engineer - will create planning/prompts.md
2. Tool Integrator - will create planning/tools.md
3. Dependency Manager - will create planning/dependencies.md

All subagents will read from planning/INITIAL.md independently.
"""

# Tool calls in single message:
Task(subagent="prompt-engineer", prompt=f"Create prompt specs for {agent_name}...")
Task(subagent="tool-integrator", prompt=f"Create tool specs for {agent_name}...")
Task(subagent="dependency-manager", prompt=f"Create dependency specs for {agent_name}...")
```

Task 3.3: Coordinate Phase Transitions
ACTION: Implement workflow coordination
PHASES:
  Phase 0 → Phase 1: After user responds to questions
  Phase 1 → Phase 2: After INITIAL.md created
  Phase 2 → Phase 3: After all 3 subagents complete
  Phase 3 → Phase 4: After agent implemented
  Phase 4 → Phase 5: After tests pass
CRITICAL: Each phase has clear completion criteria
PATTERN: Check outputs exist before proceeding
```

### Phase 4: Examples & Templates

```yaml
Task 4.1: Create Subagent Examples
CREATE: /Users/jon/source/vibes/examples/subagents/simple-subagent.md
CONTENT:
  - Complete example of single-purpose subagent
  - YAML frontmatter with all fields explained
  - System prompt structure breakdown
  - Input/output specifications
  - Usage examples
  - When to use this pattern

CREATE: /Users/jon/source/vibes/examples/subagents/parallel-workflow.md
CONTENT:
  - Demonstrates parallel invocation pattern
  - How to invoke multiple subagents at once
  - Single message pattern with code example
  - Coordination and handoff between subagents
  - Markdown communication protocol
  - Benefits of parallel execution

CREATE: /Users/jon/source/vibes/examples/subagents/markdown-comms.md
CONTENT:
  - Explains markdown communication protocol
  - Why it prevents context pollution
  - How subagents write specs, main agent implements
  - File structure and naming conventions
  - Best practices for spec writing

Task 4.2: Create Workflow Examples
CREATE: /Users/jon/source/vibes/examples/workflows/agent-factory-lite/
STRUCTURE:
  - README.md: Simplified 3-phase workflow explanation
  - phase-1-plan.md: Planning phase example
  - phase-2-implement.md: Implementation phase example
  - phase-3-validate.md: Validation phase example
PURPOSE: Learning the pattern before full 5-phase factory

CREATE: /Users/jon/source/vibes/examples/workflows/parallel-invocation/
CONTENT:
  - README.md: How parallel invocation works
  - example-workflow.md: Step-by-step parallel pattern
  - common-mistakes.md: What NOT to do
  - best-practices.md: Optimization tips

CREATE: /Users/jon/source/vibes/examples/workflows/prp-with-subagents/
CONTENT:
  - How to use PRPs with subagents
  - When to use generate-prp vs create-agent
  - Combining both approaches
  - Example workflow

Task 4.3: Port RAG Agent Example
ACTION: Copy complete agent as reference
SOURCE: /Users/jon/source/vibes/repos/context-engineering-intro/use-cases/agent-factory-with-subagents/agents/rag_agent/
TARGET: /Users/jon/source/vibes/examples/agents/rag-agent-example/
INCLUDE:
  - planning/ directory with all 4 markdown files
  - Complete Python implementation
  - Tests directory
  - README.md
  - All supporting files
PURPOSE: Shows what agent factory produces

CREATE: /Users/jon/source/vibes/examples/agents/minimal-agent/
CONTENT:
  - Simple Pydantic AI agent (50 lines)
  - Basic structure example
  - Single tool example
  - Minimal dependencies
PURPOSE: Starting point for learning

Task 4.4: Create examples/README.md
CREATE: /Users/jon/source/vibes/examples/README.md
CONTENT:
  - Overview of all example categories
  - How to use examples (reference, not copy-paste)
  - Directory structure explanation
  - Learning path: minimal-agent → agent-factory-lite → full factory
  - Cross-references to relevant documentation
```

### Phase 5: Templates & Commands

```yaml
Task 5.1: Create Subagent Template
CREATE: /Users/jon/source/vibes/prps/templates/subagent_template.md
CONTENT:
```markdown
---
name: "Subagent Name"
description: "What this subagent does and when to invoke it. USE PROACTIVELY when [trigger]. Include examples."
tools: ["tool1", "tool2"]
model: "claude-sonnet-4-5"
color: "blue"
---

# Subagent Title

You are a [specialization] specialist for [purpose].

## Your Role
[Detailed role description - what you do, how you help the workflow]

## Input
You will receive: [specify input format, files, context]

## Output
You must create: [specify output file path and format]

### Output Format
```[language]
# Example output structure
```

## Process
1. [Step 1 - what to do first]
2. [Step 2 - next action]
3. [Step 3 - final deliverable]

## Quality Standards
- [Criterion 1 - what makes output good]
- [Criterion 2 - what to avoid]
- [Criterion 3 - validation check]

## Integration
Your output serves as input for: [downstream subagents/phases]
You work in parallel with: [other subagents if applicable]

## Remember
- [Key reminder 1]
- [Key reminder 2]
- [Critical pattern or gotcha]
```

Task 5.2: Create Agent Workflow Template
CREATE: /Users/jon/source/vibes/prps/templates/agent_workflow.md
CONTENT:
  - Multi-phase workflow structure template
  - Phase definition pattern
  - Subagent invocation patterns
  - Parallel vs sequential decision guide
  - Markdown communication setup
  - Error handling patterns
  - Quality gates and validation

Task 5.3: Create Parallel Pattern Template
CREATE: /Users/jon/source/vibes/prps/templates/parallel_pattern.md
CONTENT:
  - Parallel invocation template
  - Single message structure with multiple Task calls
  - Context management for parallel execution
  - Output coordination pattern
  - Error handling for parallel failures
  - Performance considerations

Task 5.4: Create create-agent Command
CREATE: /Users/jon/source/vibes/.claude/commands/create-agent.md
CONTENT:
```markdown
# Create Agent

Invokes the agent factory workflow to create a complete AI agent.

## Usage

Describe the agent you want to build at a high level.

Example: `/create-agent` then describe: "Build an agent that can search the web and summarize results"

## How It Works

This command triggers the full agent factory orchestration defined in `.claude/orchestrators/agent-factory.md`:

### Phase 0: Clarification
- Ask 2-3 targeted questions about your agent
- Wait for your responses
- Determine agent folder name

### Phase 1: Requirements Planning
- Invoke `planner` subagent
- Create comprehensive INITIAL.md specification
- Define scope, features, dependencies

### Phase 2: Parallel Component Planning
- Invoke 3 subagents simultaneously:
  - `prompt-engineer` → prompts.md
  - `tool-integrator` → tools.md
  - `dependency-manager` → dependencies.md

### Phase 3: Implementation
- Main Claude Code reads all planning docs
- Implement complete agent with all components
- Create agent.py, tools.py, settings.py, etc.

### Phase 4: Validation
- Invoke `validator` subagent
- Create comprehensive test suite
- Run tests and generate validation report

### Phase 5: Delivery
- Generate documentation
- Create README with usage examples
- Provide deployment instructions

## Output

Complete agent in `agents/[agent_name]/` directory with:
- `planning/` - All planning documentation (4 markdown files)
- `agent.py` - Main agent implementation
- `tools.py` - Tool implementations
- `settings.py` - Configuration
- `tests/` - Complete test suite
- `README.md` - Documentation and examples

## Optional: Archon Integration

If Archon MCP server is available:
- Creates project for agent development
- Tracks tasks for each phase
- Uses RAG for documentation lookup
- Provides project management layer

Without Archon, workflow still functions completely.

## Examples

**Simple Agent:**
```
/create-agent
"Build a web search agent that uses Brave API"
```

**Complex Agent:**
```
/create-agent
"Create a database query agent that connects to PostgreSQL, executes queries, and explains results in natural language"
```

## Tips

- Be specific about core functionality
- Mention any required APIs or integrations
- Specify output format preferences
- The factory will ask clarifying questions

## See Also

- `.claude/orchestrators/agent-factory.md` - Complete workflow logic
- `examples/agents/rag-agent-example/` - Example of factory output
- `examples/workflows/agent-factory-lite/` - Simplified workflow
```
```

### Phase 6: Documentation & Integration

```yaml
Task 6.1: Update Main README.md
ACTION: Add Agent Factory section
LOCATION: /Users/jon/source/vibes/README.md
CONTENT:
  - Find appropriate location (after PRP section or before Future Vision)
  - Add ## Agent Factory section
  - Explain what the agent factory does
  - Show 5-phase workflow diagram
  - Usage examples with /create-agent command
  - Link to examples and documentation
  - Mention optional Archon integration
PATTERN: Follow existing README.md style and structure

Task 6.2: Update CLAUDE.md
ACTION: Add Agent Factory orchestration reference
LOCATION: /Users/jon/source/vibes/CLAUDE.md
ADDITION:
  - Add reference to .claude/orchestrators/agent-factory.md
  - Explain when agent factory triggers (user requests to build AI agent)
  - Note that it's an advanced pattern built on top of PRP system
  - Link to subagent documentation
KEEP: All existing rules, especially ARCHON-FIRST RULE
```

## Validation Loop

### Level 1: Structure Verification
```bash
# Verify subagent definitions
ls -la /Users/jon/source/vibes/.claude/agents/
# Expected: planner.md, prompt-engineer.md, tool-integrator.md, dependency-manager.md, validator.md, README.md + existing 2

cat /Users/jon/source/vibes/.claude/agents/planner.md
# Expected: YAML frontmatter + comprehensive system prompt

# Verify orchestrator
ls -la /Users/jon/source/vibes/.claude/orchestrators/
cat /Users/jon/source/vibes/.claude/orchestrators/agent-factory.md
# Expected: Complete 5-phase workflow with parallel invocation pattern

# Verify commands
cat /Users/jon/source/vibes/.claude/commands/create-agent.md
# Expected: Clear instructions, workflow explanation

# Verify examples structure
ls -R /Users/jon/source/vibes/examples/
# Expected: subagents/, workflows/, agents/ with all files

# Verify templates
ls /Users/jon/source/vibes/prps/templates/
# Expected: prp_base.md + 3 new templates (subagent, workflow, parallel)

# Expected: All files exist with correct structure
```

### Level 2: Content Quality Check
```bash
# Check subagent quality
for file in planner prompt-engineer tool-integrator dependency-manager validator; do
  echo "Checking $file..."
  grep -q "^---" /Users/jon/source/vibes/.claude/agents/$file.md && echo "✅ YAML frontmatter" || echo "❌ Missing frontmatter"
  grep -q "description:" /Users/jon/source/vibes/.claude/agents/$file.md && echo "✅ Has description" || echo "❌ Missing description"
done

# Verify orchestrator has critical sections
grep -q "Phase 0: Request Recognition" /Users/jon/source/vibes/.claude/orchestrators/agent-factory.md && echo "✅ Phase 0 defined"
grep -q "Parallel" /Users/jon/source/vibes/.claude/orchestrators/agent-factory.md && echo "✅ Parallel pattern documented"
grep -q "Archon" /Users/jon/source/vibes/.claude/orchestrators/agent-factory.md && echo "✅ Archon integration included"

# Check examples completeness
test -f /Users/jon/source/vibes/examples/README.md && echo "✅ Examples README exists"
test -d /Users/jon/source/vibes/examples/agents/rag-agent-example && echo "✅ RAG agent example ported"

# Expected: All quality checks pass
```

### Level 3: Single Subagent Test
```bash
# Test workflow (manual in Claude Code)
# 1. Start simple agent creation
# 2. Invoke planner subagent via Task tool
# 3. Verify output file created

# Expected commands to run:
mkdir -p /Users/jon/source/vibes/agents/test_agent/planning
# Then invoke planner subagent
# Then verify:
test -f /Users/jon/source/vibes/agents/test_agent/planning/INITIAL.md && echo "✅ Planner output created"

# Check INITIAL.md content
cat /Users/jon/source/vibes/agents/test_agent/planning/INITIAL.md
# Expected: Agent classification, requirements, dependencies, success criteria

# Cleanup
rm -rf /Users/jon/source/vibes/agents/test_agent
```

### Level 4: Parallel Invocation Test
```bash
# Test parallel workflow (manual in Claude Code)
# 1. Create INITIAL.md manually for test
# 2. Invoke 3 subagents in SINGLE message
# 3. Verify all 3 outputs created

# Setup
mkdir -p /Users/jon/source/vibes/agents/parallel_test/planning
echo "# Test Requirements" > /Users/jon/source/vibes/agents/parallel_test/planning/INITIAL.md

# Invoke in parallel (single message with 3 Task tool calls)
# Task(subagent="prompt-engineer", ...)
# Task(subagent="tool-integrator", ...)
# Task(subagent="dependency-manager", ...)

# Verify outputs
test -f /Users/jon/source/vibes/agents/parallel_test/planning/prompts.md && echo "✅ Prompts created"
test -f /Users/jon/source/vibes/agents/parallel_test/planning/tools.md && echo "✅ Tools created"
test -f /Users/jon/source/vibes/agents/parallel_test/planning/dependencies.md && echo "✅ Dependencies created"

# Verify timing - all should complete around same time (parallel execution)

# Cleanup
rm -rf /Users/jon/source/vibes/agents/parallel_test
```

### Level 5: End-to-End Workflow Test
```bash
# Full agent creation test using /create-agent command
# 1. Use command: /create-agent
# 2. Request: "Build a simple greeting agent"
# 3. Answer clarifying questions
# 4. Let workflow complete all 5 phases

# Expected outputs:
# Phase 0: Questions asked, folder name determined
# Phase 1: planning/INITIAL.md created
# Phase 2: planning/prompts.md, tools.md, dependencies.md created (parallel)
# Phase 3: agent.py, tools.py, settings.py, etc. created
# Phase 4: tests/ directory created with test suite
# Phase 5: README.md and documentation created

# Verify complete structure
ls -R /Users/jon/source/vibes/agents/greeting_agent/
# Expected: planning/, agent.py, tools.py, settings.py, tests/, README.md

# Run tests
cd /Users/jon/source/vibes/agents/greeting_agent
python -m pytest tests/ -v
# Expected: Tests pass

# Cleanup after verification
rm -rf /Users/jon/source/vibes/agents/greeting_agent
```

## Final Validation Checklist
- [ ] All 5 subagent definitions created and accurate to source
- [ ] .claude/agents/README.md explains all subagents
- [ ] agent-factory.md orchestrator created with complete 5-phase workflow
- [ ] Parallel invocation pattern correctly documented (single message, multiple Task calls)
- [ ] Archon integration included with graceful degradation
- [ ] create-agent.md command created and functional
- [ ] All example categories populated (subagents/, workflows/, agents/)
- [ ] examples/README.md provides clear learning path
- [ ] RAG agent example ported as complete reference
- [ ] 3 new templates created (subagent, workflow, parallel)
- [ ] Main README.md updated with Agent Factory section
- [ ] CLAUDE.md references agent factory orchestrator
- [ ] Single subagent invocation works
- [ ] Parallel invocation (3 subagents) works correctly
- [ ] End-to-end workflow tested and produces complete agent
- [ ] All validation gates pass
- [ ] Documentation is comprehensive and clear
- [ ] Examples demonstrate all key patterns

---

## Anti-Patterns to Avoid
- ❌ Don't invoke subagents sequentially in Phase 2 - MUST use parallel invocation
- ❌ Don't create Python files in planning phase - subagents output MARKDOWN specs
- ❌ Don't skip Phase 0 clarification questions - always ask and wait for answers
- ❌ Don't assume Archon is available - always check and handle gracefully
- ❌ Don't use different folder names across subagents - maintain exact consistency
- ❌ Don't modify existing working files (prp_base.md, existing commands, CLAUDE.md rules)
- ❌ Don't over-engineer subagents - follow "simplicity philosophy" from source
- ❌ Don't skip validation phase - comprehensive testing is required
- ❌ Don't create incomplete examples - each must be fully documented and working

## Implementation Notes

### Markdown Communication Protocol
**Why it matters**: Prevents context window pollution by using files instead of passing data

**How it works**:
1. Subagents write specifications to planning/*.md files
2. Main agent reads all files at once in Phase 3
3. Each subagent works independently, no direct communication
4. Clear separation: specs (markdown) vs implementation (Python)

**Benefits**:
- Reduces context usage significantly
- Enables true parallel execution
- Clear audit trail of decisions
- Modular and maintainable

### Parallel Invocation Critical Pattern
**The Problem**: Sequential invocation is slow and wastes time

**The Solution**: Single message with multiple Task tool calls
```python
# ❌ WRONG - Sequential (slow)
result1 = invoke_subagent("prompt-engineer")
wait_for_completion()
result2 = invoke_subagent("tool-integrator")
wait_for_completion()
result3 = invoke_subagent("dependency-manager")
wait_for_completion()

# ✅ RIGHT - Parallel (fast)
# Single message with 3 tool invocations:
Task(subagent="prompt-engineer", ...)
Task(subagent="tool-integrator", ...)
Task(subagent="dependency-manager", ...)
# All execute simultaneously
```

### Archon Integration Strategy
**Check availability first**:
```python
health = mcp__archon__health_check()
if health.success:
    # Full Archon workflow
    create_project()
    create_tasks()
    update_task_status()
    use_rag()
else:
    # Graceful degradation
    use_local_tracking()
    use_web_search()
```

**Benefits when available**:
- Project management and tracking
- Task status visibility
- RAG for documentation lookup
- Knowledge base integration

**Works without Archon**:
- Workflow completes normally
- Uses web search instead of RAG
- Local file tracking for progress

### Simplicity Philosophy
Each subagent follows "start simple, make it work, iterate" approach:
- **Planner**: 2-3 core features max, avoid over-scoping
- **Prompt Engineer**: 100-300 word prompts, clear and focused
- **Tool Integrator**: 2-3 essential tools only, single purpose
- **Dependency Manager**: Minimal config, essential vars only
- **Validator**: Comprehensive but focused tests

This ensures generated agents are maintainable and functional.

## Confidence Score: 8/10

**High confidence due to**:
- ✅ Excellent source material (complete working example)
- ✅ Clear patterns to follow (subagents, orchestrator, examples)
- ✅ Well-documented workflow (CLAUDE.md is comprehensive)
- ✅ Existing Vibes patterns to build on
- ✅ Detailed validation strategy

**Minor uncertainty**:
- Parallel invocation implementation details (need to test Task tool behavior)
- Archon integration edge cases (health check reliability)
- Subagent tool access in Vibes environment

**Mitigation strategies**:
- Test parallel invocation early in Phase 3
- Document Archon fallback patterns clearly
- Verify tool availability during subagent porting
- Iterate based on testing results

**Expected outcome**: Complete, working agent factory that can create production-ready Pydantic AI agents from high-level user requests in 10-15 minutes per agent.