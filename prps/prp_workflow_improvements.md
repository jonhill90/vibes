# PRP: PRP Workflow Improvements

**Generated**: 2025-10-04
**Based On**: prps/INITIAL_prp_workflow_improvements.md
**Archon Project**: 7ad558a1-dd1e-4fef-a1f2-5aad1636e915

---

## Goal

Transform generate-prp and execute-prp commands from sequential monolithic operations into fast, systematic multi-subagent workflows with parallel execution, code extraction, comprehensive quality gates, and Archon integration.

**End State**:
- generate-prp completes in <10 minutes (vs 15-20 minutes), produces 8+/10 scored PRPs, extracts actual code to examples/ directory
- execute-prp runs independent tasks in parallel, generates tests automatically, tracks progress in Archon
- Both commands use proven INITIAL.md factory patterns for orchestration

## Why

**Current Pain Points**:
- generate-prp: Sequential research (15-20 min), poor examples (references not code), limited Archon leverage
- execute-prp: Sequential task execution (2-3x slower), uses TodoWrite instead of Archon, no automated test generation
- Both: Manual quality assessment, no systematic validation gates

**Business Value**:
- **30-50% faster** end-to-end PRP workflow
- **Higher quality**: 8+/10 scored PRPs vs subjective assessment
- **Self-improving**: Learns from past implementations via Archon
- **Better reliability**: Automated testing reduces QA burden
- **Visibility**: Archon tracking enables retry and progress monitoring

## What

### Core Features

**Enhanced generate-prp Command**:
1. 5-phase orchestration (Phase 0 + 4 subagent phases like factory)
2. Parallel research in Phase 2 (3-4 subagents simultaneously)
3. Physical code extraction to examples/{feature}/ directory
4. Quality gates requiring 8+/10 score
5. Archon project/task tracking throughout

**Enhanced execute-prp Command**:
1. Task dependency analysis from PRP task list
2. Parallel execution of independent tasks
3. Automated test generation based on codebase patterns
4. Systematic validation gates with iteration loops
5. Archon task management (replaces TodoWrite)

**New Subagents** (10 total):
- generate-prp: 6 subagents (analyzer, researcher, hunter, curator, detective, assembler)
- execute-prp: 4 subagents (task-analyzer, implementer x2, test-generator, validator)

### Success Criteria

**Functional**:
- [ ] generate-prp extracts code files to examples/{feature}/ (not references)
- [ ] generate-prp searches Archon before web for similar PRPs
- [ ] generate-prp runs parallel research (Phase 2)
- [ ] generate-prp produces PRPs scoring 8+/10
- [ ] execute-prp analyzes task dependencies
- [ ] execute-prp executes independent tasks in parallel
- [ ] execute-prp generates tests from codebase patterns
- [ ] Both commands integrate with Archon (backward compatible if unavailable)

**Performance**:
- [ ] PRP generation time <10 minutes (from 15-20)
- [ ] PRP execution time reduced 30-50% via parallelization
- [ ] Generated PRPs score 8+/10 consistently
- [ ] Test generation achieves 70%+ coverage

**Quality**:
- [ ] Code examples include README with "what to mimic" guidance
- [ ] Validation gates catch errors before proceeding
- [ ] Graceful fallback when Archon unavailable

---

## All Needed Context

### Documentation & References

```yaml
# MUST READ - Claude Code Subagents
- url: https://docs.claude.com/en/docs/claude-code/sub-agents
  sections:
    - "What are subagents?" - context preservation, specialized expertise
    - "Creating subagents" - file-based definition with frontmatter
    - "Configuration" - tools, system prompts, model selection
  why: Defines subagent architecture for all 10 new subagents
  critical_gotchas:
    - Each subagent has isolated context (prevents pollution)
    - Tool restrictions improve security/focus
    - "USE PROACTIVELY" enables automatic invocation
    - System prompts must be highly specific

# MUST READ - Claude Code Slash Commands
- url: https://docs.claude.com/en/docs/claude-code/slash-commands
  sections:
    - "Command file structure" - frontmatter, $ARGUMENTS
    - "Bash integration" - ! prefix for shell commands
    - "SlashCommand tool" - invoking from agents
  why: Defines command structure for enhanced generate-prp/execute-prp
  critical_gotchas:
    - Must have 'description' frontmatter field
    - Character budget limit: 15000 (configurable)
    - Use @file-reference for context injection

# Context Engineering & PRP Methodology
- url: https://github.com/coleam00/context-engineering-intro
  sections:
    - "PRP structure" - PRD + Codebase Intelligence + Runbook
    - "INITIAL.md → PRP workflow"
    - "Validation loop methodology"
    - "Examples directory best practices"
  why: Defines PRP methodology we're implementing
  critical_gotchas:
    - Context engineering > prompt engineering
    - Treat AI as junior dev needing comprehensive briefing
    - Validation is non-negotiable
    - Context is ongoing discipline

# Archon MCP Server
- url: https://github.com/coleam00/Archon
  sections:
    - "RAG knowledge base" - vector search with PGVector
    - "Task and project management"
    - "MCP tool integration"
  why: The MCP server for knowledge/task management
  critical_gotchas:
    - Beta version - expect some issues
    - Use 2-5 keyword queries (SHORT queries!)
    - Health check FIRST before operations
    - Graceful fallback when unavailable

# Parallel Multi-Agent Patterns
- url: https://medium.com/@codecentrevibe/claude-code-multi-agent-parallel-coding-83271c4675fa
  sections:
    - "Explicitly define delegation points"
    - "Multi-threaded programming analogy"
    - "Batch processing for >10 agents"
  why: Shows parallel subagent execution patterns
  critical: Similar to multi-threaded programming - orchestration matters

# ESSENTIAL LOCAL FILES
- file: examples/prp_workflow_improvements/README.md
  why: Comprehensive guide with "what to mimic" for all 6 patterns
  pattern: Shows how to apply factory patterns to PRP workflow

- file: examples/prp_workflow_improvements/factory_parallel_pattern.md
  why: THE KEY INNOVATION - parallel subagent invocation (3x speedup)
  pattern: Single message with multiple Task calls
  critical: Apply to both generate-prp (research) and execute-prp (tasks)

- file: examples/prp_workflow_improvements/subagent_structure.md
  why: Complete subagent definition template
  pattern: Frontmatter config + system prompt + responsibilities + output format

- file: examples/prp_workflow_improvements/archon_integration_pattern.md
  why: Project/task creation, status updates, document storage
  pattern: Health check → create project → create tasks → update status

- file: examples/prp_workflow_improvements/code_extraction_pattern.md
  why: Physical file extraction methodology (not references)
  pattern: Read source → Extract relevant → Write to examples/ → Add attribution

- file: .claude/commands/generate-prp.md
  why: Current baseline - shows Archon-first, ULTRATHINK pattern
  preserve: Health check, ULTRATHINK, quality checklist
  replace: Sequential research with parallel

- file: .claude/commands/execute-prp.md
  why: Current baseline - shows validation loop pattern
  preserve: Load → ULTRATHINK → Execute → Validate → Complete flow
  replace: TodoWrite with Archon, sequential with parallel

- file: .claude/commands/create-initial.md
  why: Proven 5-phase orchestrator pattern
  pattern: Phase 0 (YOU) → Phase 1 (1 agent) → Phase 2 (3 parallel) → Phase 3 (1 agent) → Phase 4 (1 agent) → Phase 5 (YOU)
  apply: Entire architecture to generate-prp

- file: .claude/agents/prp-initial-*.md (6 files)
  why: Working subagent definitions from factory
  pattern: Use as templates for 10 new subagents
```

### Current Codebase Tree

```
vibes/
├── .claude/
│   ├── agents/
│   │   ├── documentation-manager.md
│   │   ├── validation-gates.md
│   │   ├── prp-initial-feature-clarifier.md       # Factory subagent
│   │   ├── prp-initial-codebase-researcher.md     # Factory subagent
│   │   ├── prp-initial-documentation-hunter.md    # Factory subagent
│   │   ├── prp-initial-example-curator.md         # Factory subagent
│   │   ├── prp-initial-gotcha-detective.md        # Factory subagent
│   │   └── prp-initial-assembler.md               # Factory subagent
│   └── commands/
│       ├── generate-prp.md                         # To enhance
│       ├── execute-prp.md                          # To enhance
│       ├── create-initial.md                       # Proven pattern source
│       ├── execute-parallel.md
│       └── prep-parallel.md
├── prps/
│   ├── templates/
│   │   └── prp_base.md
│   ├── INITIAL_prp_workflow_improvements.md        # Source for this PRP
│   └── prp_workflow_improvements.md                # This file
├── examples/
│   └── prp_workflow_improvements/                  # Extracted patterns
│       ├── README.md
│       ├── current_generate_prp.md
│       ├── current_execute_prp.md
│       ├── factory_parallel_pattern.md
│       ├── subagent_structure.md
│       ├── archon_integration_pattern.md
│       └── code_extraction_pattern.md
└── CLAUDE.md                                       # ARCHON-FIRST RULE here
```

### Desired Codebase Tree

```
vibes/
├── .claude/
│   ├── agents/
│   │   ├── [existing agents unchanged]
│   │   ├── prp-gen-feature-analyzer.md           # NEW - Phase 1
│   │   ├── prp-gen-codebase-researcher.md        # NEW - Phase 2A
│   │   ├── prp-gen-documentation-hunter.md       # NEW - Phase 2B
│   │   ├── prp-gen-example-curator.md            # NEW - Phase 2C
│   │   ├── prp-gen-gotcha-detective.md           # NEW - Phase 3
│   │   ├── prp-gen-assembler.md                  # NEW - Phase 4
│   │   ├── prp-exec-task-analyzer.md             # NEW - Analyze deps
│   │   ├── prp-exec-implementer.md               # NEW - Execute tasks
│   │   ├── prp-exec-test-generator.md            # NEW - Generate tests
│   │   └── prp-exec-validator.md                 # NEW - Run validation
│   └── commands/
│       ├── generate-prp.md                        # ENHANCED - 5-phase orchestrator
│       └── execute-prp.md                         # ENHANCED - Parallel executor
```

**New Files**:
- 10 subagent files (prp-gen-* and prp-exec-*)
- 2 enhanced command files (replacing existing)

### Known Gotchas & Library Quirks

```python
# CRITICAL: Parallel Task Invocation Pattern
# ❌ WRONG - Sequential invocation:
invoke_subagent("agent1", context1)  # Wait for completion
invoke_subagent("agent2", context2)  # Then invoke next
invoke_subagent("agent3", context3)  # Then invoke next

# ✅ RIGHT - Parallel invocation in SINGLE message:
# Use Task tool THREE times in ONE response
parallel_invoke([
    Task(agent="agent1", prompt=context1),
    Task(agent="agent2", prompt=context2),
    Task(agent="agent3", prompt=context3)
])
# All three execute simultaneously, reducing time by ~3x

# CRITICAL: Archon Query Length
# Vector search works best with 2-5 keywords, NOT sentences
# ❌ WRONG:
rag_search_knowledge_base(query="how to implement authentication with JWT tokens for API security")

# ✅ RIGHT:
rag_search_knowledge_base(query="authentication JWT API")

# CRITICAL: Code Extraction vs References
# Must extract ACTUAL code files to examples/, not just reference paths
# ❌ WRONG:
"""
See src/api/auth.py for authentication pattern
"""

# ✅ RIGHT:
Read("src/api/auth.py")  # Read source
Extract(lines 45-67)      # Extract relevant section
Write(f"examples/{feature}/auth_pattern.py", code)  # Physical file

# CRITICAL: ARCHON-FIRST RULE (from CLAUDE.md)
# NEVER use TodoWrite - always use Archon task management
# ❌ WRONG:
TodoWrite(todos=[...])

# ✅ RIGHT:
mcp__archon__manage_task("create", project_id="...", title="...", status="todo")
mcp__archon__manage_task("update", task_id="...", status="doing")
mcp__archon__manage_task("update", task_id="...", status="done")

# CRITICAL: Subagent Context Window Pollution
# Don't pass full context to all agents - filter to "need-to-know"
context_map = {
    'feature-analyzer': ['user_request', 'clarifications'],
    'codebase-researcher': ['feature_summary', 'tech_stack'],
    'example-curator': ['feature_summary', 'code_patterns'],
    'assembler': ['all_research']  # Only assembler sees everything
}

# CRITICAL: Quality Gate Bypass Prevention
# All subagent outputs must pass validation before proceeding
class QualityGate:
    required_sections: list  # e.g., ["Core Requirements", "Technical Components"]
    min_length: int          # e.g., 500 characters

    def validate(content):
        # Check all required sections present
        # Check minimum length met
        # Return errors if validation fails

# CRITICAL: Race Conditions in Parallel File Writes
# Phase 2 agents writing to same directory → use unique temp files
def parallel_safe_write(agent_name, content):
    temp_file = f"prps/research/.{agent_name}_{timestamp}.tmp"
    Write(temp_file, content)
    return temp_file

def merge_outputs(temp_files):
    # Merge all temp files to final locations
    # Delete temp files after merge

# CRITICAL: Graceful Archon Degradation
# Always check health, fallback to local tracking if unavailable
health = mcp__archon__health_check()
if health["status"] != "healthy":
    # Use local file-based task tracking
    # Continue workflow without Archon
    local_tasks = []
```

---

## Implementation Blueprint

### Phase 0: Planning & Understanding

**BEFORE starting implementation, complete these steps:**

1. **Read all example files**:
   - examples/prp_workflow_improvements/README.md (comprehensive guide)
   - All 6 extracted pattern files
   - Understand "what to mimic" vs "what to adapt"

2. **Study factory architecture**:
   - Read .claude/commands/create-initial.md (lines 1-531)
   - Understand 5-phase orchestration pattern
   - Note parallel invocation in Phase 2 (lines 126-185)
   - Note Archon integration pattern (lines 38-87)

3. **Review existing subagents**:
   - Read .claude/agents/prp-initial-feature-clarifier.md
   - Understand frontmatter structure
   - Note system prompt pattern
   - Note output format requirements

### Task List (Execute in Order)

```yaml
Task 1: Create 6 generate-prp subagents
RESPONSIBILITY: Define specialized subagents for PRP generation workflow
FILES TO CREATE:
  - .claude/agents/prp-gen-feature-analyzer.md
  - .claude/agents/prp-gen-codebase-researcher.md
  - .claude/agents/prp-gen-documentation-hunter.md
  - .claude/agents/prp-gen-example-curator.md
  - .claude/agents/prp-gen-gotcha-detective.md
  - .claude/agents/prp-gen-assembler.md

PATTERN TO FOLLOW: .claude/agents/prp-initial-feature-clarifier.md (subagent_structure.md)

FRONTMATTER TEMPLATE:
  ---
  name: prp-gen-{responsibility}
  description: USE PROACTIVELY for {purpose}. {what_it_does}. Works autonomously.
  tools: Read, Write, Grep, Glob, [Bash if needed], mcp__archon__*
  color: {blue|green|orange|purple|cyan|magenta}
  ---

SYSTEM PROMPT SECTIONS (in each file):
  1. Primary Objective (what this agent does)
  2. Archon-First Research Strategy (search Archon before web)
  3. Core Responsibilities (step-by-step process)
  4. Output Generation (exact format and file path)
  5. Quality Criteria (what makes output good)
  6. Error Handling (what to do if research fails)

SPECIFIC RESPONSIBILITIES:
  - feature-analyzer: Read INITIAL.md → analyze requirements → search Archon for similar PRPs → create prps/research/feature-analysis.md
  - codebase-researcher: Search local code patterns → search Archon code examples → create prps/research/codebase-patterns.md
  - documentation-hunter: Search Archon docs → web search for official docs → create prps/research/documentation-links.md
  - example-curator: EXTRACT code to examples/{feature}/ → create README with guidance → create prps/research/examples-to-include.md
  - gotcha-detective: Search Archon for issues → web search for pitfalls → create prps/research/gotchas.md
  - assembler: Read all 5 research docs → synthesize into PRP following prp_base.md → create prps/{feature}.md

CRITICAL FOR example-curator:
  Must EXTRACT actual code files, not references
  Use pattern from code_extraction_pattern.md
  Create physical files in examples/{feature}/
  Add source attribution comments
  Create README.md with "what to mimic" guidance

VALIDATION:
  - Each subagent file 200-300 lines
  - Clear input/output contracts
  - Archon-first search strategy documented
  - Error handling specified

Task 2: Create 4 execute-prp subagents
RESPONSIBILITY: Define specialized subagents for PRP execution workflow
FILES TO CREATE:
  - .claude/agents/prp-exec-task-analyzer.md
  - .claude/agents/prp-exec-implementer.md
  - .claude/agents/prp-exec-test-generator.md
  - .claude/agents/prp-exec-validator.md

PATTERN TO FOLLOW: Same subagent structure as Task 1

SPECIFIC RESPONSIBILITIES:
  - task-analyzer: Read PRP → parse task list → identify dependencies → create execution groups → create prps/execution-plan.md
  - implementer: Execute task group → implement code → follow PRP patterns → report completion
  - test-generator: Analyze implemented code → search for test patterns → generate test files → follow codebase conventions
  - validator: Run validation commands → collect errors → analyze failures → suggest fixes → iterate until pass

CRITICAL FOR task-analyzer:
  Must parse "after X" dependencies from PRP
  Create parallel execution groups
  Example:
    Group 1 (parallel): [Task A, Task B, Task C] - no dependencies
    Group 2 (parallel): [Task D, Task E] - depend on Group 1
    Group 3 (sequential): [Task F] - depends on Task E

CRITICAL FOR test-generator:
  Search for existing test patterns in codebase
  Extract test fixtures, mocking patterns
  Generate tests following same conventions
  Aim for 70%+ coverage of implemented functionality

VALIDATION:
  - task-analyzer creates valid execution plan
  - implementer follows PRP patterns exactly
  - test-generator creates passing tests
  - validator provides actionable fix suggestions

Task 3: Enhance generate-prp command
RESPONSIBILITY: Transform into 5-phase orchestrator with parallel execution
FILE TO MODIFY: .claude/commands/generate-prp.md

PRESERVE FROM CURRENT:
  - Archon health check pattern
  - ULTRATHINK before writing PRP
  - Quality checklist with 1-10 scoring
  - Using prp_base.md template

REPLACE WITH FACTORY PATTERN:
  - 5-phase orchestration (from create-initial.md)
  - Parallel Phase 2 invocation (3-4 agents simultaneously)
  - Archon project/task tracking
  - Quality gates requiring 8+/10
  - Code extraction to examples/ directory

NEW STRUCTURE:
  # Create PRP

  ## Feature file: $ARGUMENTS

  [Description and purpose]

  ## Phase 0: Recognition & Setup (YOU handle this)

  1. Read INITIAL.md file
  2. Extract feature name (snake_case)
  3. Create directories: prps/research/, examples/{feature}/
  4. Check Archon availability
  5. If Archon available:
     - Create project
     - Create 6 tasks (one per phase)
  6. Proceed to Phase 1

  ## Phase 1: Feature Analysis

  Invoke: prp-gen-feature-analyzer
  Input: INITIAL.md path, feature name, project_id
  Output: prps/research/feature-analysis.md
  Duration: ~2 minutes

  ## Phase 2: Parallel Research (CRITICAL)

  ⚠️ INVOKE ALL IN SINGLE MESSAGE - PARALLEL EXECUTION

  Invoke simultaneously:
    - prp-gen-codebase-researcher
    - prp-gen-documentation-hunter
    - prp-gen-example-curator

  Outputs:
    - prps/research/codebase-patterns.md
    - prps/research/documentation-links.md
    - prps/research/examples-to-include.md
    - examples/{feature}/ directory with code files

  Duration: ~3 minutes (not 9 minutes sequential)

  ## Phase 3: Gotcha Detection

  Invoke: prp-gen-gotcha-detective
  Input: All Phase 2 outputs
  Output: prps/research/gotchas.md
  Duration: ~2 minutes

  ## Phase 4: PRP Assembly

  Invoke: prp-gen-assembler
  Input: All 5 research documents
  Output: prps/{feature}.md
  Duration: ~1 minute

  ## Phase 5: Delivery & Quality Check (YOU handle this)

  1. Verify quality score >= 8/10
  2. If score < 8: Offer regeneration
  3. If score >= 8: Present results
  4. Update Archon project with completion notes
  5. Store PRP as Archon document

  ## Error Handling

  [Same pattern as create-initial.md lines 317-353]

PARALLEL INVOCATION CODE (Phase 2):
  ```python
  # Update all 3 tasks to "doing"
  if archon_available:
      for task_id in [task_ids[1], task_ids[2], task_ids[3]]:
          mcp__archon__manage_task("update", task_id=task_id, status="doing")

  # ⚠️ CRITICAL: Single message with 3 Task calls
  parallel_invoke([
      Task(agent="prp-gen-codebase-researcher", prompt=researcher_context),
      Task(agent="prp-gen-documentation-hunter", prompt=hunter_context),
      Task(agent="prp-gen-example-curator", prompt=curator_context)
  ])

  # After completion, mark all done
  if archon_available:
      for task_id in [task_ids[1], task_ids[2], task_ids[3]]:
          mcp__archon__manage_task("update", task_id=task_id, status="done")
  ```

VALIDATION:
  - Command file ~400-500 lines (similar to create-initial.md)
  - Phase 2 uses parallel invocation
  - Quality gates enforce 8+/10 minimum
  - Archon integration with graceful fallback

Task 4: Enhance execute-prp command
RESPONSIBILITY: Add parallel execution and Archon tracking
FILE TO MODIFY: .claude/commands/execute-prp.md

PRESERVE FROM CURRENT:
  - Load PRP → ULTRATHINK → Execute → Validate → Complete flow
  - Validation loop pattern (run, fix, re-run)
  - PRP re-reading capability

ADD NEW CAPABILITIES:
  - Phase 1: Task dependency analysis
  - Phase 2: Parallel task execution
  - Phase 3: Automated test generation
  - Phase 4: Systematic validation
  - Archon task tracking (NOT TodoWrite)

NEW STRUCTURE:
  # Execute PRP

  ## PRP File: $ARGUMENTS

  [Description and purpose]

  ## Phase 0: Load & Plan (YOU handle this)

  1. Read PRP file
  2. Check Archon availability
  3. If Archon available:
     - Create project for this implementation
     - Extract tasks from PRP
     - Create Archon task for each PRP task
  4. Invoke task-analyzer

  ## Phase 1: Dependency Analysis

  Invoke: prp-exec-task-analyzer
  Input: PRP file path, project_id
  Output: prps/execution-plan.md with task groups

  Execution plan format:
    Group 1 (parallel): [task_a, task_b, task_c]
    Group 2 (parallel): [task_d, task_e]
    Group 3 (sequential): [task_f]

  ## Phase 2: Parallel Implementation

  For each group in execution plan:
    If group is parallel:
      ⚠️ Invoke multiple prp-exec-implementer agents simultaneously
      Example for Group 1 with 3 tasks:
        parallel_invoke([
            Task(agent="prp-exec-implementer", prompt=task_a_context),
            Task(agent="prp-exec-implementer", prompt=task_b_context),
            Task(agent="prp-exec-implementer", prompt=task_c_context)
        ])

    If group is sequential:
      Invoke prp-exec-implementer for single task

    Update Archon tasks as each completes

  ## Phase 3: Test Generation

  Invoke: prp-exec-test-generator
  Input: List of implemented files, PRP validation requirements
  Output: Test files following codebase patterns

  ## Phase 4: Validation & Iteration

  Invoke: prp-exec-validator
  Input: Validation commands from PRP
  Process:
    1. Run all validation commands
    2. Collect errors
    3. Analyze root causes
    4. Suggest fixes
    5. Apply fixes
    6. Re-run validation
    7. Repeat until all pass

  ## Phase 5: Completion (YOU handle this)

  1. Verify all validation gates pass
  2. Update Archon project with completion notes
  3. Present summary to user

PARALLEL EXECUTION CODE (Phase 2):
  ```python
  execution_plan = Read("prps/execution-plan.md")

  for group in execution_plan.groups:
      if group.type == "parallel":
          # Update all group tasks to "doing"
          if archon_available:
              for task_id in group.task_ids:
                  mcp__archon__manage_task("update", task_id=task_id, status="doing")

          # ⚠️ CRITICAL: Parallel invocation
          tasks = [
              Task(agent="prp-exec-implementer", prompt=prepare_context(task))
              for task in group.tasks
          ]
          parallel_invoke(tasks)

          # Mark all complete
          if archon_available:
              for task_id in group.task_ids:
                  mcp__archon__manage_task("update", task_id=task_id, status="done")

      elif group.type == "sequential":
          # Execute one at a time
          for task in group.tasks:
              if archon_available:
                  mcp__archon__manage_task("update", task_id=task.id, status="doing")

              invoke_subagent("prp-exec-implementer", prepare_context(task))

              if archon_available:
                  mcp__archon__manage_task("update", task_id=task.id, status="done")
  ```

VALIDATION:
  - Command file ~300-400 lines
  - Parallel execution for independent tasks
  - Archon tracking (NO TodoWrite)
  - Validation loops iterate until pass

Task 5: Test generate-prp with sample INITIAL.md
RESPONSIBILITY: Validate enhanced command works end-to-end
STEPS:
  1. Use existing INITIAL file: prps/INITIAL_prp_workflow_improvements.md
  2. Run: /generate-prp prps/INITIAL_prp_workflow_improvements.md
  3. Verify Phase 2 runs in parallel (3 agents simultaneously)
  4. Verify code extracted to examples/prp_workflow_improvements/
  5. Verify PRP scored 8+/10
  6. Verify Archon project created and updated
  7. Fix any errors discovered
  8. Re-run until successful

EXPECTED OUTPUTS:
  - prps/prp_workflow_improvements.md (this file regenerated)
  - examples/prp_workflow_improvements/ with new code files
  - prps/research/ with 5 research documents
  - Archon project with completed tasks

VALIDATION:
  - Total time <10 minutes
  - Quality score >= 8/10
  - All 5 research docs created
  - Examples directory populated with code files

Task 6: Test execute-prp with generated PRP
RESPONSIBILITY: Validate enhanced command executes PRPs correctly
STEPS:
  1. Create simple test PRP with parallel tasks
  2. Run: /execute-prp prps/test-feature.md
  3. Verify task dependency analysis
  4. Verify parallel execution for independent tasks
  5. Verify tests generated automatically
  6. Verify validation loops iterate
  7. Verify Archon tracking (NO TodoWrite used)
  8. Fix any errors discovered
  9. Re-run until successful

TEST PRP STRUCTURE:
  Tasks:
    - Task A: Create model (no dependencies)
    - Task B: Create validator (no dependencies)
    - Task C: Create API endpoint (after A, B)

  Expected execution:
    Group 1 (parallel): A, B
    Group 2 (sequential): C

VALIDATION:
  - Tasks A and B execute simultaneously
  - Task C executes after A and B complete
  - Tests generated for all three tasks
  - All validation gates pass
  - Archon tasks created and updated

Task 7: Documentation updates
RESPONSIBILITY: Update CLAUDE.md with new workflow guidance
FILE TO MODIFY: CLAUDE.md

ADD SECTIONS:
  - Enhanced PRP workflow overview
  - When to use generate-prp vs create-initial
  - Parallel execution benefits
  - Quality score interpretation
  - Troubleshooting common issues

UPDATE SECTIONS:
  - "Working with PRPs" - new 5-phase approach
  - "Common Development Workflows" - add timing expectations

VALIDATION:
  - CLAUDE.md updated with accurate information
  - Examples included for both commands
  - Troubleshooting section comprehensive
```

### Implementation Pseudocode

```python
# Task 1: Create generate-prp subagents

for subagent_name in [
    "prp-gen-feature-analyzer",
    "prp-gen-codebase-researcher",
    "prp-gen-documentation-hunter",
    "prp-gen-example-curator",
    "prp-gen-gotcha-detective",
    "prp-gen-assembler"
]:
    # Read template subagent for structure
    template = Read(".claude/agents/prp-initial-feature-clarifier.md")

    # Adapt for new responsibility
    frontmatter = create_frontmatter(
        name=subagent_name,
        description=get_description(subagent_name),
        tools=get_required_tools(subagent_name),
        color=assign_color(subagent_name)
    )

    system_prompt = create_system_prompt(
        primary_objective=define_objective(subagent_name),
        archon_strategy=standard_archon_first_pattern,
        responsibilities=list_responsibilities(subagent_name),
        output_format=define_output_format(subagent_name),
        quality_criteria=define_quality(subagent_name)
    )

    # Write new subagent file
    Write(f".claude/agents/{subagent_name}.md",
          frontmatter + system_prompt)

# Task 3: Enhance generate-prp command

# PATTERN: Read factory command for structure
factory_pattern = Read(".claude/commands/create-initial.md")

# PATTERN: Extract parallel invocation code (lines 126-185)
parallel_pattern = extract_lines(factory_pattern, 126, 185)

# PATTERN: Extract Archon integration (lines 38-87)
archon_pattern = extract_lines(factory_pattern, 38, 87)

# Create new enhanced command
enhanced_command = f"""
# Create PRP

## Feature file: $ARGUMENTS

{standard_description}

## Phase 0: Recognition & Setup (YOU handle this)

{archon_pattern}  # Health check, create project, create tasks

## Phase 1: Feature Analysis

invoke_subagent("prp-gen-feature-analyzer", context)

## Phase 2: Parallel Research (CRITICAL)

{parallel_pattern}  # Parallel invocation of 3 agents

## Phase 3: Gotcha Detection

invoke_subagent("prp-gen-gotcha-detective", context)

## Phase 4: PRP Assembly

invoke_subagent("prp-gen-assembler", context)

## Phase 5: Delivery & Quality Check (YOU handle this)

{quality_check_pattern}
"""

Write(".claude/commands/generate-prp.md", enhanced_command)

# Task 4: Enhance execute-prp command

# PATTERN: Task dependency analysis
def analyze_dependencies(prp_tasks):
    """
    Parse PRP task list, identify "after X" dependencies
    Return execution groups
    """
    groups = []
    current_group = {"type": "parallel", "tasks": []}

    for task in prp_tasks:
        if "after" in task.description:
            # This task has dependency - new group
            if current_group["tasks"]:
                groups.append(current_group)
            current_group = {"type": "parallel", "tasks": []}

        current_group["tasks"].append(task)

    if current_group["tasks"]:
        groups.append(current_group)

    return groups

# PATTERN: Parallel execution
def execute_groups(groups, archon_project_id):
    """
    Execute task groups, parallelize when possible
    """
    for group in groups:
        if group["type"] == "parallel" and len(group["tasks"]) > 1:
            # ⚠️ CRITICAL: Single message with multiple Task calls
            tasks = [
                Task(
                    agent="prp-exec-implementer",
                    prompt=prepare_context(task, archon_project_id)
                )
                for task in group["tasks"]
            ]
            parallel_invoke(tasks)
        else:
            # Sequential execution
            for task in group["tasks"]:
                invoke_subagent("prp-exec-implementer",
                              prepare_context(task, archon_project_id))
```

---

## Validation Loop

### Level 1: Syntax & File Checks

```bash
# Verify all subagent files created
ls .claude/agents/prp-gen-*.md | wc -l
# Expected: 6

ls .claude/agents/prp-exec-*.md | wc -l
# Expected: 4

# Verify frontmatter valid in all files
for file in .claude/agents/prp-*.md; do
    grep -q "^---$" "$file" || echo "Missing frontmatter: $file"
    grep -q "^name:" "$file" || echo "Missing name: $file"
    grep -q "^description:" "$file" || echo "Missing description: $file"
    grep -q "^tools:" "$file" || echo "Missing tools: $file"
done

# Verify commands enhanced
grep -q "Phase 2: Parallel Research" .claude/commands/generate-prp.md || echo "Missing parallel pattern"
grep -q "prp-exec-task-analyzer" .claude/commands/execute-prp.md || echo "Missing task analyzer"
```

### Level 2: Functional Testing - generate-prp

```bash
# Test enhanced generate-prp command
# Use existing INITIAL file as test input
/generate-prp prps/INITIAL_prp_workflow_improvements.md

# Verify outputs created:
# 1. Research documents
ls prps/research/*.md | wc -l
# Expected: 5 files

# 2. Examples directory
ls examples/prp_workflow_improvements/*.md
# Expected: Multiple files with source attribution

# 3. Final PRP
test -f prps/prp_workflow_improvements.md
# Expected: File exists

# 4. Quality score check
grep "Score:" prps/prp_workflow_improvements.md
# Expected: Score >= 8/10

# 5. Archon project created
# Manually verify in Archon MCP or check command output
```

**If any validation fails**:
1. Read error messages carefully
2. Check which phase failed
3. Review corresponding subagent implementation
4. Fix issues in subagent or command file
5. Re-run validation

### Level 3: Functional Testing - execute-prp

```bash
# Create simple test PRP
cat > prps/test-parallel-execution.md << 'EOF'
# Test PRP: Parallel Execution

## Tasks

Task A: Create data model
CREATE src/models/test_model.py:
- Simple Pydantic model
- Two fields: name (str), value (int)

Task B: Create validator
CREATE src/validators/test_validator.py:
- Validate name is not empty
- Validate value is positive

Task C: Create API endpoint (after A, B)
CREATE src/api/test_endpoint.py:
- Import model and validator
- POST endpoint that uses both
- Return validated data

## Validation Loop

```bash
# Syntax
ruff check src/

# Tests
pytest tests/test_*.py -v
```
EOF

# Run execute-prp
/execute-prp prps/test-parallel-execution.md

# Verify:
# 1. Tasks A and B executed in parallel (check timing in output)
# 2. Task C executed after A and B
# 3. All three files created
test -f src/models/test_model.py
test -f src/validators/test_validator.py
test -f src/api/test_endpoint.py

# 4. Tests generated
ls tests/test_*.py | wc -l
# Expected: At least 3 test files

# 5. All validation passes
ruff check src/
pytest tests/test_*.py -v
# Expected: All pass

# 6. Archon tasks created and completed
# Manually verify in Archon MCP
```

**If validation fails**:
1. Check execution plan created by task-analyzer
2. Verify parallel invocation occurred (timing in logs)
3. Check Archon task updates
4. Fix issues in execute-prp command or subagents
5. Re-run validation

### Level 4: Performance Validation

```bash
# Measure generate-prp performance
time /generate-prp prps/INITIAL_prp_workflow_improvements.md
# Expected: <10 minutes total
# Expected: Phase 2 shows ~3 minutes (not ~9 minutes)

# Measure execute-prp performance with parallel tasks
time /execute-prp prps/test-parallel-execution.md
# Expected: Tasks A+B execute simultaneously (check logs)
# Expected: Total time < sequential execution time
```

### Level 5: Integration Testing

```bash
# End-to-end workflow test
# 1. Create INITIAL.md for new feature
echo "Create INITIAL.md for user authentication with JWT"
/create-initial  # Use factory

# 2. Generate PRP from INITIAL.md
/generate-prp prps/INITIAL_user_authentication.md
# Verify: Score >= 8/10

# 3. Execute PRP
/execute-prp prps/user_authentication.md
# Verify: All tasks complete, tests pass

# 4. Verify Archon tracking throughout
# Check Archon MCP for:
# - INITIAL.md project with 6 completed tasks
# - PRP generation project with 6 completed tasks
# - PRP execution project with N completed tasks
```

---

## Final Validation Checklist

- [ ] All 10 subagent files created (.claude/agents/prp-*.md)
- [ ] All subagents have valid frontmatter (name, description, tools)
- [ ] generate-prp.md enhanced with 5-phase orchestration
- [ ] generate-prp uses parallel invocation in Phase 2
- [ ] execute-prp.md enhanced with task dependency analysis
- [ ] execute-prp uses parallel execution for independent tasks
- [ ] Archon integration in both commands (health check, project/task tracking)
- [ ] Code extraction to examples/ directory (not just references)
- [ ] Quality gates enforce 8+/10 minimum for PRPs
- [ ] No TodoWrite usage (Archon only per ARCHON-FIRST RULE)
- [ ] Test generate-prp completes in <10 minutes
- [ ] Test execute-prp parallelizes independent tasks
- [ ] Test validation loops iterate until pass
- [ ] Documentation updated in CLAUDE.md
- [ ] All validation commands pass

---

## Anti-Patterns to Avoid

- ❌ **Sequential execution in Phase 2** - MUST use parallel invocation for 3x speedup
- ❌ **Using TodoWrite** - Violates ARCHON-FIRST RULE, use Archon task management
- ❌ **Referencing code instead of extracting** - Must create physical files in examples/
- ❌ **Long Archon queries** - Use 2-5 keywords, not full sentences
- ❌ **Skipping quality gates** - Always enforce 8+/10 minimum for PRPs
- ❌ **Context window pollution** - Filter context to "need-to-know" per subagent
- ❌ **Race conditions in file writes** - Use unique temp files for parallel agents
- ❌ **Bypassing validation loops** - Always iterate until all tests pass
- ❌ **Hardcoding values** - Use variables for feature names, paths, etc.
- ❌ **Missing error handling** - Always handle Archon unavailable gracefully
- ❌ **Ignoring existing patterns** - Study examples/ directory first
- ❌ **Creating new patterns unnecessarily** - Reuse factory patterns

---

## Success Metrics

**After implementation, verify these metrics**:

- ✅ generate-prp time: <10 minutes (baseline: 15-20 minutes) = **33-50% faster**
- ✅ execute-prp time: 30-50% faster via parallelization
- ✅ PRP quality scores: 8+/10 consistently (vs subjective before)
- ✅ Code examples: Physical files extracted (vs references before)
- ✅ Test coverage: 70%+ for executed PRPs (vs manual before)
- ✅ Archon adoption: 100% of workflows tracked (vs 0% before)
- ✅ Validation pass rate: >90% first attempt (quality gates working)

---

## PRP Quality Self-Assessment

**Score: 9/10** - Confidence in one-pass implementation success

**Reasoning**:
- ✅ Comprehensive context: All documentation, examples, patterns provided
- ✅ Clear task breakdown: 7 tasks with specific responsibilities
- ✅ Proven patterns: Reusing factory architecture (already working)
- ✅ Validation strategy: 5 levels of validation with specific commands
- ✅ Error handling: Documented gotchas with solutions
- ✅ Examples directory: 6 extracted patterns with detailed guidance
- ⚠️ Complexity: 10 new subagents + 2 enhanced commands is significant scope

**Deduction reasoning**:
- -1 point for scope/complexity (10 new files is substantial)
- Could be split into two PRPs (generate-prp enhancements, then execute-prp enhancements) for easier implementation
- However, both enhancements follow same factory pattern so can be done together

**Mitigations**:
- Start with generate-prp (6 subagents + 1 command) first
- Validate thoroughly before starting execute-prp
- Use examples/ directory extensively - patterns are proven
- Leverage Archon for task tracking throughout

**Recommendation**: Execute in two phases if needed:
1. Phase A: Enhanced generate-prp (Tasks 1, 3, 5)
2. Phase B: Enhanced execute-prp (Tasks 2, 4, 6)

This maintains quality while reducing implementation complexity per phase.
