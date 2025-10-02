name: "Context Engineering Agent Factory - Complete Implementation PRP"
description: |
  Complete integration of Cole's Agent Factory pattern with 5 specialized subagents,
  parallel workflow orchestration, and optional Archon integration for autonomous
  AI agent development in Vibes.

## Goal
Transform Vibes into a fully-functional AI agent factory that autonomously builds complete, tested Pydantic AI agents through a coordinated workflow of specialized subagents working in parallel. Users describe agents at a high level, and the system delivers production-ready implementations automatically.

## Why
- **Speed**: Reduce agent development from hours/days to minutes through parallel execution
- **Quality**: Specialized subagents ensure comprehensive planning, implementation, and testing
- **Consistency**: Standardized patterns produce reliable, well-documented agents
- **Learning**: Demonstrates advanced context engineering patterns (subagents, parallel invocation, markdown communication)
- **Integration**: Optional Archon integration adds task tracking and knowledge management

## What
A complete agent factory implementation with:

1. **5 Specialized Subagents** (.claude/agents/):
   - planner.md: Requirements analysis and INITIAL.md creation
   - prompt-engineer.md: System prompt design
   - tool-integrator.md: Tool planning and specifications
   - dependency-manager.md: Config and dependency management
   - validator.md: Testing and validation

2. **Orchestration System** (.claude/orchestrators/):
   - agent-factory.md: Complete 5-phase workflow logic
   - Phase 0: Clarification
   - Phase 1: Requirements (planner)
   - Phase 2: Parallel component design (3 subagents simultaneously)
   - Phase 3: Implementation (main Claude)
   - Phase 4: Validation (validator)
   - Phase 5: Delivery and documentation

3. **Commands & Templates**:
   - /create-agent command for user-friendly invocation
   - Subagent template for creating new specialized agents
   - Workflow templates for multi-phase patterns
   - Parallel invocation pattern template

4. **Examples & Documentation**:
   - Complete rag-agent as reference implementation
   - Subagent usage examples
   - Parallel workflow demonstrations
   - Agent factory lite (simplified 3-phase version)

### Success Criteria
- [ ] All 5 subagents created and functional
- [ ] Can invoke planner subagent successfully
- [ ] Can invoke 3 subagents in parallel (single message)
- [ ] Markdown communication works between phases
- [ ] Generated agent has complete structure (planning/, tests/, README, etc.)
- [ ] Validation subagent creates comprehensive tests
- [ ] Archon integration works when available
- [ ] System gracefully degrades without Archon
- [ ] /create-agent command works end-to-end

## All Needed Context

### Documentation & References
```yaml
# PRIMARY REFERENCES - Read these first
- file: /Users/jon/source/vibes/repos/context-engineering-intro/use-cases/agent-factory-with-subagents/CLAUDE.md
  why: Complete orchestration rules and workflow logic to port
  critical: Contains exact phase definitions, subagent invocation patterns, Archon integration protocol

- file: /Users/jon/source/vibes/repos/context-engineering-intro/use-cases/agent-factory-with-subagents/README.md
  why: Architecture overview and workflow visualization
  critical: Explains subagent benefits, parallel execution, modular design

- url: https://www.youtube.com/watch?v=HJ9VvIG3Rps
  why: Cole's video explaining the agent factory pattern
  critical: "Markdown files as communication layer prevents context pollution"

# SUBAGENT DEFINITIONS - Port these exactly
- file: /Users/jon/source/vibes/repos/context-engineering-intro/use-cases/agent-factory-with-subagents/.claude/agents/pydantic-ai-planner.md
  why: Requirements analysis specialist - creates INITIAL.md
  pattern: Autonomous work, MVP mindset, simple focused requirements

- file: /Users/jon/source/vibes/repos/context-engineering-intro/use-cases/agent-factory-with-subagents/.claude/agents/pydantic-ai-prompt-engineer.md
  why: System prompt design - creates prompts.md
  pattern: Clarity over complexity, 100-300 word prompts

- file: /Users/jon/source/vibes/repos/context-engineering-intro/use-cases/agent-factory-with-subagents/.claude/agents/pydantic-ai-tool-integrator.md
  why: Tool planning - creates tools.md
  pattern: Minimal tools (2-3), single purpose, simple parameters

- file: /Users/jon/source/vibes/repos/context-engineering-intro/use-cases/agent-factory-with-subagents/.claude/agents/pydantic-ai-dependency-manager.md
  why: Config and dependencies - creates dependencies.md
  pattern: Essential env vars only, minimal packages

- file: /Users/jon/source/vibes/repos/context-engineering-intro/use-cases/agent-factory-with-subagents/.claude/agents/pydantic-ai-validator.md
  why: Testing and validation - creates tests/ and VALIDATION_REPORT.md
  pattern: Uses TestModel and FunctionModel for comprehensive testing

# EXAMPLE AGENT - Use as reference
- file: /Users/jon/source/vibes/repos/context-engineering-intro/use-cases/agent-factory-with-subagents/agents/rag_agent/
  why: Complete agent produced by factory - shows desired output structure
  critical: Includes planning/, tests/, complete implementation

# EXISTING PATTERNS - Follow these
- file: /Users/jon/source/vibes/prps/templates/prp_base.md
  why: Current PRP template structure
  pattern: Context-rich, validation loops, progressive success

- file: /Users/jon/source/vibes/.claude/agents/validation-gates.md
  why: Existing subagent pattern in Vibes
  pattern: Tools, description, system prompt structure

# ARCHON INTEGRATION - Optional but powerful
- url: https://docs.claude.com/en/docs/claude-code/sub-agents
  why: Official subagent documentation
  critical: Parallel invocation patterns, tool usage

# PYDANTIC AI PATTERNS - For implementation
- url: https://ai.pydantic.dev/
  why: Framework documentation for agents being built
  section: Agent patterns, tools, testing with TestModel/FunctionModel
```

### Current Codebase Structure
```bash
/Users/jon/source/vibes/
├── .claude/
│   ├── agents/                    # Currently 2 agents
│   │   ├── documentation-manager.md
│   │   └── validation-gates.md
│   ├── commands/                  # Existing commands
│   │   ├── generate-prp.md
│   │   ├── execute-prp.md
│   │   ├── prep-parallel.md
│   │   └── execute-parallel.md
│   └── settings.local.json
├── agents/                        # EMPTY - will hold generated agents
├── examples/                      # EMPTY - will hold examples
├── prps/
│   ├── templates/
│   │   └── prp_base.md           # Existing template
│   └── [various PRPs]
├── mcp/                          # MCP servers
├── repos/
│   └── context-engineering-intro/
│       └── use-cases/
│           └── agent-factory-with-subagents/  # Source to port from
└── [other directories]
```

### Desired Codebase Structure
```bash
/Users/jon/source/vibes/
├── .claude/
│   ├── agents/                    # 7 total agents (5 new + 2 existing)
│   │   ├── documentation-manager.md        # ✅ Exists
│   │   ├── validation-gates.md             # ✅ Exists
│   │   ├── planner.md                      # NEW: Requirements specialist
│   │   ├── prompt-engineer.md              # NEW: Prompt design
│   │   ├── tool-integrator.md              # NEW: Tool planning
│   │   ├── dependency-manager.md           # NEW: Dependencies
│   │   └── validator.md                    # NEW: Testing specialist
│   ├── commands/
│   │   ├── [existing commands]
│   │   └── create-agent.md                 # NEW: User-facing command
│   └── orchestrators/                      # NEW: Workflow definitions
│       ├── README.md
│       └── agent-factory.md                # Main orchestration logic
├── agents/                                  # Generated agents
│   └── [agent_name]/
│       ├── planning/                        # Markdown communication layer
│       │   ├── INITIAL.md                   # From planner
│       │   ├── prompts.md                   # From prompt-engineer
│       │   ├── tools.md                     # From tool-integrator
│       │   └── dependencies.md              # From dependency-manager
│       ├── agent.py
│       ├── tools.py
│       ├── prompts.py
│       ├── settings.py
│       ├── tests/                           # From validator
│       │   └── VALIDATION_REPORT.md
│       └── README.md
├── examples/
│   ├── README.md
│   ├── subagents/                           # NEW: Subagent patterns
│   │   ├── simple-subagent.md
│   │   ├── parallel-workflow.md
│   │   └── markdown-comms.md
│   ├── agents/                              # NEW: Reference agents
│   │   └── rag-agent-example/               # Port from use-case
│   └── workflows/                           # NEW: Workflow patterns
│       ├── agent-factory-lite/
│       └── parallel-invocation/
└── prps/
    └── templates/
        ├── prp_base.md                      # ✅ Exists
        ├── subagent_template.md             # NEW
        ├── agent_workflow.md                # NEW
        └── parallel_pattern.md              # NEW
```

### Known Gotchas & Critical Patterns
```python
# CRITICAL: Parallel invocation MUST use single message with multiple tool calls
# ❌ WRONG: Sequential invocation
invoke("prompt-engineer")  # Wait for completion
invoke("tool-integrator")  # Then invoke this
invoke("dependency-manager")  # Then invoke this

# ✅ RIGHT: Single message with 3 Task tool invocations
# In Claude Code, send ONE response containing THREE Task tool calls

# CRITICAL: Markdown files are communication protocol
# planner creates: agents/[name]/planning/INITIAL.md
# Other subagents READ this file and create their outputs
# Main Claude reads ALL planning/*.md files to implement

# CRITICAL: Archon integration is optional
if archon_available:
    # Create project and tasks
    # Use RAG for documentation lookup
else:
    # System works without Archon
    # Use file-based tracking instead

# CRITICAL: Subagent naming consistency
# Name in .claude/agents/FILE.md must match subagent "name" field
# Example: file is "planner.md", name field is "pydantic-ai-planner"
```

### Codebase Conventions from CLAUDE.md
```python
# From /Users/jon/source/vibes/CLAUDE.md:

# CRITICAL: ARCHON-FIRST RULE
# ALWAYS use Archon MCP server for task management if available
# Do NOT use TodoWrite - use Archon find_tasks and manage_task instead

# Research workflow:
# 1. Check Archon with health_check()
# 2. If available: use rag_search_knowledge_base() and rag_search_code_examples()
# 3. If not available: use web_search

# Task-driven development:
# 1. Get task: find_tasks(task_id="...") or find_tasks(filter_by="status", filter_value="todo")
# 2. Start work: manage_task("update", task_id="...", status="doing")
# 3. Research: Use Archon RAG
# 4. Implement: Write code
# 5. Complete: manage_task("update", task_id="...", status="done")
```

## Implementation Blueprint

### Phase 1: Core Infrastructure (PRIORITY 1 - Foundation)

**Task 1.1: Create orchestrators directory and README**
```bash
# Create new directory structure
mkdir -p /Users/jon/source/vibes/.claude/orchestrators

# CREATE .claude/orchestrators/README.md
# Explain purpose: Workflow definitions for multi-phase operations
# Document how orchestrators differ from commands
# Provide examples of when to create new orchestrators
```

**Task 1.2: Port planner subagent**
```bash
# CREATE .claude/agents/planner.md
# Port from: repos/context-engineering-intro/use-cases/agent-factory-with-subagents/.claude/agents/pydantic-ai-planner.md
# MODIFY: Update name to match Vibes conventions
# MODIFY: Change tools if needed (Vibes doesn't have all tools)
# PRESERVE: Core system prompt and philosophy
# PRESERVE: Simplicity principles and MVP mindset
```

**Task 1.3: Port prompt-engineer subagent**
```bash
# CREATE .claude/agents/prompt-engineer.md
# Port from: pydantic-ai-prompt-engineer.md
# MODIFY: Ensure Archon tools are referenced correctly
# PRESERVE: Brevity and clarity principles
# PRESERVE: System prompt structure
```

**Task 1.4: Port tool-integrator subagent**
```bash
# CREATE .claude/agents/tool-integrator.md
# Port from: pydantic-ai-tool-integrator.md
# PRESERVE: Minimal tools philosophy (2-3 only)
# PRESERVE: Single purpose, simple parameters approach
```

**Task 1.5: Port dependency-manager subagent**
```bash
# CREATE .claude/agents/dependency-manager.md
# Port from: pydantic-ai-dependency-manager.md
# PRESERVE: Essential env vars only
# PRESERVE: Minimal packages philosophy
```

**Task 1.6: Port validator subagent**
```bash
# CREATE .claude/agents/validator.md
# Port from: pydantic-ai-validator.md
# PRESERVE: TestModel and FunctionModel patterns
# PRESERVE: Comprehensive testing approach
```

### Phase 2: Orchestration Logic (PRIORITY 1 - Core Workflow)

**Task 2.1: Create agent-factory orchestrator**
```bash
# CREATE .claude/orchestrators/agent-factory.md
# Port from: repos/context-engineering-intro/use-cases/agent-factory-with-subagents/CLAUDE.md

# STRUCTURE:
# 1. Trigger patterns recognition
# 2. Phase 0: Clarification logic
# 3. Phase 1: Planner invocation
# 4. Phase 2: Parallel invocation (CRITICAL - single message pattern)
# 5. Phase 3: Implementation by main Claude
# 6. Phase 4: Validator invocation
# 7. Phase 5: Delivery and documentation
# 8. Archon integration protocol (optional)

# CRITICAL SECTIONS TO INCLUDE:
# - Exact parallel invocation pattern
# - Markdown communication protocol
# - Folder naming consistency rules
# - Error handling and graceful degradation
```

**Task 2.2: Test single subagent invocation**
```bash
# VALIDATION: Manually test planner subagent
# Create test folder: agents/test_agent/
# Invoke planner with simple request
# Verify: planning/INITIAL.md is created correctly
# Verify: Contains all required sections
```

### Phase 3: Parallel Workflow Implementation (PRIORITY 1 - Critical Feature)

**Task 3.1: Implement parallel invocation pattern documentation**
```bash
# CREATE prps/templates/parallel_pattern.md
# Document: Single message with multiple Task tool calls
# Include: Example code showing correct pattern
# Include: Common mistakes and how to avoid them
# Include: Debugging tips for parallel execution
```

**Task 3.2: Test parallel invocation**
```bash
# VALIDATION: Test 3 subagents in parallel
# Setup: Ensure planner has created INITIAL.md
# Execute: Invoke prompt-engineer, tool-integrator, dependency-manager in SINGLE message
# Verify: All 3 create their planning/*.md files
# Verify: No race conditions or conflicts
# Verify: Files have correct content based on INITIAL.md
```

### Phase 4: Commands & Templates (PRIORITY 2 - User Interface)

**Task 4.1: Create /create-agent command**
```bash
# CREATE .claude/commands/create-agent.md
# PURPOSE: User-friendly entry point to agent factory
# TRIGGER: User says "create an agent" or similar
# WORKFLOW:
#   1. Activate orchestrator
#   2. Pass control to agent-factory.md workflow
#   3. Handle user interaction for clarifications
#   4. Return final agent location to user
```

**Task 4.2: Create subagent template**
```bash
# CREATE prps/templates/subagent_template.md
# Include: Standard frontmatter (name, description, tools, color)
# Include: System prompt structure
# Include: Input/output specifications
# Include: Quality standards checklist
# Include: Integration points with other subagents
```

**Task 4.3: Create agent workflow template**
```bash
# CREATE prps/templates/agent_workflow.md
# Template for: Creating multi-phase workflows
# Include: Phase definitions
# Include: Subagent invocation patterns
# Include: Parallel vs sequential decision tree
# Include: Markdown communication setup
# Include: Error handling strategies
```

### Phase 5: Examples & Documentation (PRIORITY 2 - Learning Resources)

**Task 5.1: Create examples directory structure**
```bash
# CREATE examples/README.md
# Explain: Purpose of examples directory
# Document: How to use each example category
# Link: To relevant documentation

mkdir -p examples/subagents
mkdir -p examples/agents
mkdir -p examples/workflows
```

**Task 5.2: Create subagent examples**
```bash
# CREATE examples/subagents/simple-subagent.md
# Show: Single-purpose subagent creation
# Include: Complete example with all sections
# Include: Usage instructions

# CREATE examples/subagents/parallel-workflow.md
# Show: How to invoke multiple subagents at once
# Include: Single message pattern demonstration
# Include: Coordination and handoff logic

# CREATE examples/subagents/markdown-comms.md
# Show: Markdown communication protocol
# Include: How planning files work
# Include: Read/write patterns between phases
```

**Task 5.3: Port rag-agent as reference**
```bash
# CREATE examples/agents/rag-agent-example/
# Copy from: repos/context-engineering-intro/use-cases/agent-factory-with-subagents/agents/rag_agent/
# Include: Complete structure with planning/, tests/, implementation
# Update: README to explain this is a factory output example
# Highlight: Key patterns and structure to emulate
```

**Task 5.4: Create workflow examples**
```bash
# CREATE examples/workflows/agent-factory-lite/
# Purpose: Simplified 3-phase workflow for learning
# Phases: Plan -> Implement -> Validate
# Include: Complete working example
# Include: README explaining simplifications

# CREATE examples/workflows/parallel-invocation/
# Purpose: Demonstrate parallel execution pattern
# Include: Working example of single message, multiple tool calls
# Include: Debugging guide
# Include: Performance comparison (parallel vs sequential)
```

### Phase 6: Archon Integration (PRIORITY 3 - Optional Enhancement)

**Task 6.1: Document Archon integration in orchestrator**
```bash
# MODIFY .claude/orchestrators/agent-factory.md
# Add section: "Archon Integration Protocol"
# Include:
#   - health_check() before starting
#   - Project creation pattern
#   - Task creation for each phase
#   - Status update logic (todo -> doing -> done)
#   - RAG usage for documentation lookup
#   - Graceful degradation when unavailable
```

**Task 6.2: Create Archon integration example**
```bash
# CREATE examples/workflows/archon-agent-factory/
# Show: Complete workflow WITH Archon
# Include: Project creation
# Include: Task management
# Include: RAG usage for research
# Include: Comparison: with vs without Archon
```

## Validation Loop

### Level 1: Structure Validation
```bash
# Verify directory structure
ls -la .claude/agents/ | grep -E "(planner|prompt-engineer|tool-integrator|dependency-manager|validator)"
ls -la .claude/orchestrators/
ls -la .claude/commands/ | grep create-agent
ls -la examples/subagents/
ls -la examples/agents/
ls -la examples/workflows/
ls -la prps/templates/ | grep -E "(subagent|workflow|parallel)"

# Expected: All directories and files exist
```

### Level 2: Subagent Validation
```bash
# Validate subagent structure
for agent in planner prompt-engineer tool-integrator dependency-manager validator; do
  echo "Checking $agent..."
  grep -q "^name:" .claude/agents/$agent.md || echo "Missing name field"
  grep -q "^description:" .claude/agents/$agent.md || echo "Missing description"
  grep -q "^tools:" .claude/agents/$agent.md || echo "Missing tools"
  grep -q "# System Prompt" .claude/agents/$agent.md || echo "Missing system prompt"
done

# Expected: All agents have required fields
```

### Level 3: Functional Testing
```bash
# Test 1: Single subagent invocation
# In Claude Code, manually invoke planner
# Provide simple agent request
# Verify INITIAL.md is created with correct structure

# Test 2: Parallel invocation
# Manually invoke 3 subagents in single message
# Verify all 3 planning files created
# Verify no conflicts or errors

# Test 3: End-to-end workflow
# Use /create-agent command
# Provide simple agent spec (e.g., "web search agent")
# Verify complete agent generated in agents/ directory
# Verify all phases complete successfully
```

### Level 4: Archon Integration Testing
```bash
# If Archon available:
# Run agent factory workflow
# Verify Archon project created
# Verify 7 tasks created (one per phase)
# Verify tasks updated to "doing" and "done" correctly
# Verify RAG used for documentation lookup

# If Archon unavailable:
# Run agent factory workflow
# Verify system works without errors
# Verify graceful degradation (no Archon features)
```

## Final Validation Checklist
- [ ] All 5 subagent files created in .claude/agents/
- [ ] Orchestrator file created in .claude/orchestrators/
- [ ] /create-agent command functional
- [ ] Planner subagent works standalone
- [ ] Parallel invocation of 3 subagents works (single message)
- [ ] Markdown communication verified (planning/*.md files)
- [ ] End-to-end agent generation successful
- [ ] Generated agent has correct structure
- [ ] Validator creates tests and VALIDATION_REPORT.md
- [ ] All examples created and documented
- [ ] All templates created
- [ ] Archon integration documented and tested (if available)
- [ ] Graceful degradation verified (without Archon)
- [ ] README updated with agent factory usage

## Anti-Patterns to Avoid
- ❌ Don't invoke subagents sequentially when parallel execution is needed
- ❌ Don't skip Phase 0 clarification - always ask questions first
- ❌ Don't create planning files in wrong directory (must be planning/ subdirectory)
- ❌ Don't assume Archon is available - always check with health_check()
- ❌ Don't use inconsistent folder names across phases
- ❌ Don't skip validation phase - testing is critical
- ❌ Don't over-engineer - follow simplicity principles from source
- ❌ Don't modify subagent philosophies (MVP mindset, clarity over complexity, etc.)

---

## PRP Confidence Score: 9/10

**Reasoning:**
- ✅ Complete context provided (all source files, patterns, documentation)
- ✅ Clear implementation tasks in logical order
- ✅ Executable validation gates for each phase
- ✅ Known gotchas and critical patterns documented
- ✅ Anti-patterns explicitly called out
- ✅ Archon integration well-documented with graceful degradation
- ✅ Examples and templates for learning
- ⚠️ -1 point: Parallel invocation is complex and error-prone, may need iteration

**Success Probability:**
With this PRP, an AI agent should achieve working implementation in first pass, with possible minor adjustments needed for parallel invocation pattern (the most complex part). All context, patterns, and pitfalls are documented for self-correction during implementation.
