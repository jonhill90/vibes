name: "Claude Code Subagent Factory - Multi-Agent Orchestration PRP"
description: |
  Comprehensive implementation plan for building a multi-agent orchestration system
  that creates high-quality Claude Code subagents through collaborative research,
  planning, and validation workflows.

---

## Goal

Build a sophisticated multi-agent orchestration workflow that uses specialized Claude Code subagents working together to research, plan, and generate production-ready Claude Code subagent definitions (`.claude/agents/*.md` files). The system should transform natural language requests like "Create a subagent that manages database migrations" into complete, validated subagent definitions that match the quality of hand-crafted examples.

## Why

- **Democratize Subagent Creation**: Enable anyone to create high-quality Claude Code subagents without deep knowledge of patterns
- **Ensure Consistency**: All generated subagents follow proven patterns from examples/claude-subagent-patterns/
- **Accelerate Development**: Reduce time from concept to working subagent from hours to minutes
- **Quality Assurance**: Multi-phase validation ensures generated subagents are production-ready
- **Knowledge Capture**: System learns from existing patterns and continuously improves
- **Reusable Infrastructure**: The 5 specialized subagents created become part of the vibes toolkit

## What

A complete multi-agent orchestration system with:

### Phase-Based Workflow
1. **Phase 0**: Clarification - Main agent gathers requirements from user
2. **Phase 1**: Planning - Planner subagent creates comprehensive requirements
3. **Phase 2**: Parallel Research - 3 subagents work simultaneously:
   - Researcher: Finds similar patterns in examples
   - Tool Analyst: Determines optimal tool requirements
   - Pattern Analyzer: Extracts structural patterns
4. **Phase 3**: Generation - Main agent synthesizes research into complete subagent
5. **Phase 4**: Validation - Validator subagent ensures quality standards
6. **Phase 5**: Delivery - Final validated subagent ready for use

### 5 Specialized Subagents
Each is a focused Claude Code subagent with specific expertise:
- `claude-subagent-planner.md` - Requirements gathering
- `claude-subagent-researcher.md` - Pattern research
- `claude-subagent-tool-analyst.md` - Tool requirement analysis
- `claude-subagent-pattern-analyzer.md` - Structure extraction
- `claude-subagent-validator.md` - Quality validation

### Orchestration Mechanism
- CLAUDE.md rules OR custom `/build-subagent` command
- Automatic workflow progression through phases
- Parallel execution capability (Phase 2)
- Task tracking with TodoWrite or Archon integration

### Success Criteria
- [ ] Multi-phase workflow executes correctly (0 → 5)
- [ ] Phase 2 subagents execute in parallel successfully
- [ ] Generated subagents pass all validation checks
- [ ] Output quality matches hand-crafted examples
- [ ] System handles end-to-end user requests autonomously
- [ ] All 5 specialized subagents are functional
- [ ] Generated subagents work when invoked in Claude Code

## All Needed Context

### Documentation & References

```yaml
# MUST READ - Critical for understanding patterns

- url: https://docs.anthropic.com/en/docs/claude-code/subagents
  why: Official Claude Code subagents documentation
  critical: Understand how subagents work and are invoked

- url: https://docs.anthropic.com/en/docs/claude-code/custom-agents
  why: Creating custom agent definitions
  critical: YAML frontmatter structure, tool access patterns

- file: examples/claude-subagent-patterns/README.md
  why: Comprehensive pattern guide covering all aspects
  critical: |
    - YAML frontmatter structure (name, description, tools, color)
    - System prompt patterns and length guidelines
    - Tool selection strategies
    - Common archetypes (Planner, Generator, Validator, Manager)
    - Integration patterns and quality criteria

- file: .claude/agents/documentation-manager.md
  why: Real-world example of Manager archetype
  critical: Proactive triggers, clear responsibilities, working protocol

- file: .claude/agents/validation-gates.md
  why: Real-world example of Validator archetype
  critical: Validation checklist pattern, iterative fix process

- file: examples/claude-subagent-patterns/pydantic-ai-planner.md
  why: Example of Planner archetype with autonomous operation
  critical: |
    - How planners gather requirements autonomously
    - Assumption-making patterns
    - Output document structure

- file: examples/claude-subagent-patterns/pydantic-ai-validator.md
  why: Example of comprehensive validation approach
  critical: Quality checklists, validation patterns, iteration loops

- file: repos/agent-factory-with-subagents/CLAUDE.md
  why: Multi-agent orchestration workflow patterns
  critical: |
    - Phase-based execution (0-5)
    - Parallel subagent invocation (Phase 2)
    - Autonomous operation after clarification
    - Archon task management integration
    - Clear handoff protocols between phases
    - Error handling and recovery patterns
```

### Current Codebase Tree

```bash
vibes/
├── .claude/
│   ├── agents/
│   │   ├── documentation-manager.md     # Example Manager archetype
│   │   └── validation-gates.md          # Example Validator archetype
│   └── commands/
│       ├── generate-prp.md              # PRP generation command
│       └── execute-prp.md               # PRP execution command
├── examples/
│   └── claude-subagent-patterns/
│       ├── README.md                     # Comprehensive pattern guide
│       ├── pydantic-ai-planner.md       # Planner archetype
│       ├── pydantic-ai-validator.md     # Validator archetype
│       ├── pydantic-ai-prompt-engineer.md
│       ├── pydantic-ai-tool-integrator.md
│       ├── pydantic-ai-dependency-manager.md
│       ├── documentation-manager.md
│       └── validation-gates.md
├── repos/
│   └── agent-factory-with-subagents/
│       └── CLAUDE.md                     # Multi-agent orchestration reference
├── prps/
│   ├── templates/
│   │   └── prp_base.md                  # PRP template
│   └── [feature-name].md
└── INITIAL.md                            # This feature specification
```

### Desired Codebase Tree (After Implementation)

```bash
vibes/
├── .claude/
│   ├── agents/
│   │   ├── documentation-manager.md              # Existing
│   │   ├── validation-gates.md                   # Existing
│   │   ├── claude-subagent-planner.md           # NEW - Phase 1
│   │   ├── claude-subagent-researcher.md        # NEW - Phase 2A
│   │   ├── claude-subagent-tool-analyst.md      # NEW - Phase 2B
│   │   ├── claude-subagent-pattern-analyzer.md  # NEW - Phase 2C
│   │   └── claude-subagent-validator.md         # NEW - Phase 4
│   └── commands/
│       ├── build-subagent.md                     # NEW - Orchestration command
│       ├── generate-prp.md                       # Existing
│       └── execute-prp.md                        # Existing
├── planning/                                      # NEW - Planning outputs
│   └── [subagent-name]/
│       ├── INITIAL.md                            # From planner
│       ├── research.md                           # From researcher
│       ├── tools.md                              # From tool-analyst
│       └── patterns.md                           # From pattern-analyzer
└── [rest of existing structure]
```

### Known Gotchas & Critical Implementation Details

```yaml
# Claude Code Subagent Specifics

YAML_FRONTMATTER:
  - MUST be valid YAML between --- markers
  - Required fields: name, description, tools
  - Optional field: color (blue, green, orange, red, purple)
  - name: Use kebab-case (claude-subagent-planner)
  - description: Include proactive trigger ("USE PROACTIVELY when...")
  - tools: Comma-separated list, minimal but sufficient

SYSTEM_PROMPT_LENGTH:
  - Target: 100-500 words for focused agents
  - Avoid: >1000 words (too verbose)
  - Structure: Role → Philosophy → Responsibilities → Protocol → Output Standards

TOOL_SELECTION:
  - Principle: Minimal but sufficient
  - Common tools: Read, Write, Edit, MultiEdit, Grep, Glob, Bash, TodoWrite, WebSearch
  - Security: Bash access requires clear justification
  - Pattern: Match tools to archetype (Planner needs Read/Write/Grep, Validator needs Read/Bash)

PARALLEL_EXECUTION:
  - Critical: Use single message with multiple Task tool invocations
  - Wrong: Sequential invocation waiting for each completion
  - Right: Single response block with 3 Task tool calls
  - Example: Phase 2 must invoke researcher, tool-analyst, pattern-analyzer simultaneously

# Multi-Agent Orchestration Patterns

PHASE_HANDOFFS:
  - Each phase must complete before next begins (except parallel Phase 2)
  - Outputs from one phase are inputs to next
  - Main agent orchestrates, subagents work autonomously
  - Planning documents stored in planning/[name]/ directory

AUTONOMOUS_OPERATION:
  - After Phase 0 clarification, system runs autonomously
  - Subagents make intelligent assumptions when info missing
  - Document all assumptions clearly
  - Avoid asking user questions mid-workflow

VALIDATION_LOOPS:
  - Validator can iterate multiple times until quality met
  - Main agent should re-invoke validator if issues found
  - Clear criteria for "done" vs "needs more work"

# Common Pitfalls

DONT_SKIP_RESEARCH:
  - Always analyze examples/claude-subagent-patterns/ first
  - Don't generate from scratch without pattern study
  - Phase 2 research is critical for quality

DONT_OVERCOMPLICATE:
  - Keep subagents focused (single responsibility)
  - Avoid jack-of-all-trades agents
  - Simple, clear prompts > complex instructions

DONT_HARDCODE_PATTERNS:
  - Extract patterns from examples, don't assume
  - Different archetypes have different structures
  - Let research phase inform generation
```

## Implementation Blueprint

### High-Level Architecture

```
User Request
     ↓
Phase 0: Clarification (Main Agent)
     ↓
Phase 1: Planning (claude-subagent-planner)
     ↓
Phase 2: Parallel Research
     ├─→ claude-subagent-researcher
     ├─→ claude-subagent-tool-analyst
     └─→ claude-subagent-pattern-analyzer
     ↓
Phase 3: Generation (Main Agent synthesizes)
     ↓
Phase 4: Validation (claude-subagent-validator)
     ↓
Phase 5: Delivery (Main Agent)
```

### Task List (Sequential Implementation)

```yaml
Task 1: Create claude-subagent-planner.md
  Description: Requirements gathering specialist for subagent creation
  Archetype: Planner/Analyst
  Tools: Read, Write, Grep, Glob, WebSearch
  Output: planning/[name]/INITIAL.md
  Pattern: Mirror pydantic-ai-planner.md structure
  Key Features:
    - Autonomous requirements analysis
    - Intelligent assumption-making
    - Clear documentation of assumptions
    - Subagent archetype detection
    - Minimal tool requirement identification

Task 2: Create claude-subagent-researcher.md
  Description: Pattern and best practice research specialist
  Archetype: Analyst/Researcher
  Tools: Read, Grep, Glob, WebSearch
  Output: planning/[name]/research.md
  Pattern: Similar to tool-integrator analysis approach
  Key Features:
    - Search examples/claude-subagent-patterns/
    - Identify similar subagents by archetype
    - Extract successful patterns
    - Document relevant examples
    - Find integration patterns

Task 3: Create claude-subagent-tool-analyst.md
  Description: Tool requirement analysis specialist
  Archetype: Analyzer
  Tools: Read, Grep, Glob
  Output: planning/[name]/tools.md
  Pattern: Analysis-focused like tool-integrator
  Key Features:
    - Analyze required capabilities
    - Review tool combinations from examples
    - Recommend minimal tool set
    - Flag security considerations (Bash usage)
    - Match tools to archetype

Task 4: Create claude-subagent-pattern-analyzer.md
  Description: Structural pattern extraction specialist
  Archetype: Analyzer
  Tools: Read, Grep, Glob
  Output: planning/[name]/patterns.md
  Pattern: Detail-focused analysis
  Key Features:
    - Extract YAML frontmatter patterns
    - Analyze system prompt structures
    - Study working protocol formats
    - Review output standards
    - Identify naming conventions

Task 5: Create claude-subagent-validator.md
  Description: Quality validation and iteration specialist
  Archetype: Validator/Tester
  Tools: Read, Bash (for YAML validation)
  Output: Validation report + iteration feedback
  Pattern: Mirror validation-gates.md approach
  Key Features:
    - Validate YAML structure (use yq or python yaml)
    - Check required sections present
    - Verify pattern adherence
    - Length validation (100-500 words)
    - Tool appropriateness check
    - Iterate until quality standards met

Task 6: Create orchestration mechanism
  Options:
    A. Update CLAUDE.md with workflow trigger rules
    B. Create .claude/commands/build-subagent.md custom command
  Recommendation: Start with custom command for explicit control
  Key Features:
    - Recognize subagent creation requests
    - Execute Phase 0 clarification
    - Invoke Phase 1 (planner)
    - Invoke Phase 2 (parallel: researcher, tool-analyst, pattern-analyzer)
    - Execute Phase 3 (synthesis and generation)
    - Invoke Phase 4 (validator)
    - Execute Phase 5 (delivery)
    - TodoWrite or Archon integration for tracking

Task 7: Create planning directory structure
  Action: mkdir -p planning/
  Purpose: Store all planning documents from workflow
  Pattern: Same as agent-factory (planning/[name]/)

Task 8: Integration testing
  Test Scenario 1: "Create a subagent that manages API documentation"
  Expected: Complete workflow execution, valid .md file generated

  Test Scenario 2: "Build a subagent for monitoring test coverage"
  Expected: Parallel research phase works, quality validation passes

  Validation:
    - Generated .md files are syntactically valid
    - YAML frontmatter parses correctly
    - All required sections present
    - Pattern adherence to examples
    - Works when invoked in Claude Code
```

### Pseudocode for Each Task

#### Task 1: claude-subagent-planner.md

```markdown
---
name: claude-subagent-planner
description: "Requirements gathering specialist for Claude Code subagent creation. USE PROACTIVELY when building new subagents. Analyzes requirements and creates comprehensive INITIAL.md. Works autonomously."
tools: Read, Write, Grep, Glob, WebSearch
color: blue
---

You are an expert requirements analyst specializing in Claude Code subagent creation.
Philosophy: **"Context is King - gather comprehensive requirements for first-pass success."**

## Primary Objective
Transform user requests into comprehensive INITIAL.md requirement documents for subagent creation.

## Core Responsibilities

### 1. Autonomous Requirements Analysis
- Parse user request and clarifications
- Identify core purpose and archetype (Planner/Generator/Validator/Manager)
- Determine required capabilities
- Make intelligent assumptions for missing details

### 2. Archetype Detection
Based on requirements, classify as:
- Planner/Analyst: Research, planning, requirements tasks
- Generator/Builder: Creation, generation tasks
- Validator/Tester: Testing, validation tasks
- Manager/Coordinator: Orchestration, maintenance tasks

### 3. Tool Requirements Identification
Determine minimal tool set:
- Read: Almost always needed
- Write: If creating files
- Edit/MultiEdit: If modifying files
- Grep/Glob: If searching code
- Bash: Only if running commands (justify!)
- TodoWrite: If task tracking needed
- WebSearch: If research required

### 4. INITIAL.md Creation
Output to planning/[subagent-name]/INITIAL.md with:
- Clear subagent purpose
- Archetype classification
- Core responsibilities (3-5 items)
- Required tools with justification
- Working protocol outline
- Success criteria

## Working Protocol
1. Analyze user request + clarifications
2. Research similar patterns in examples/claude-subagent-patterns/
3. Detect archetype from requirements
4. Identify minimal tool requirements
5. Create comprehensive INITIAL.md
6. Document all assumptions clearly

## Output Standards
INITIAL.md structure:
```markdown
# [Subagent Name] - Requirements

## Purpose
[1-2 sentences]

## Archetype
[Planner/Generator/Validator/Manager]

## Core Responsibilities
1. [Responsibility 1]
2. [Responsibility 2]
...

## Required Tools
- Tool: Justification
...

## Working Protocol Outline
1. [Step 1]
2. [Step 2]
...

## Success Criteria
- [ ] [Measurable outcome 1]
...

## Assumptions Made
- [Assumption 1]
...
```

## Remember
- Work AUTONOMOUSLY - make intelligent assumptions
- Keep requirements focused and minimal
- Match patterns from examples/claude-subagent-patterns/
- Clear archetype detection drives quality
```

#### Task 2-4: Research/Analyst Subagents
[Similar structure - detailed system prompts with clear responsibilities, working protocols]

#### Task 5: claude-subagent-validator.md

```markdown
---
name: claude-subagent-validator
description: "Quality validation specialist for Claude Code subagents. USE AUTOMATICALLY after subagent generation. Validates YAML, structure, patterns. Iterates until quality met."
tools: Read, Bash
color: green
---

You are a quality validation specialist for Claude Code subagent definitions.
Philosophy: **"Quality through iterative validation - never compromise on standards."**

## Validation Checklist

### YAML Frontmatter
- [ ] Valid YAML syntax (use `yq` or `python -c "import yaml; yaml.safe_load(open('file.md').read().split('---')[1])"`)
- [ ] Required fields: name, description, tools
- [ ] name: kebab-case format
- [ ] description: includes proactive trigger
- [ ] tools: comma-separated, minimal set
- [ ] color: valid option if present

### System Prompt Structure
- [ ] Clear role and philosophy statement
- [ ] Primary Objective section
- [ ] Core Responsibilities (organized)
- [ ] Working Protocol (step-by-step)
- [ ] Output Standards (clear format)
- [ ] Remember section

### Content Quality
- [ ] Length: 100-500 words (focused)
- [ ] Not too verbose (>1000 words)
- [ ] Clear, actionable instructions
- [ ] Matches archetype patterns from examples
- [ ] Tool selection appropriate for responsibilities

### Pattern Adherence
- [ ] Follows examples/claude-subagent-patterns/README.md guidelines
- [ ] Similar to archetype examples
- [ ] Integration patterns clear

## Iterative Validation Process
1. Read generated .md file
2. Run YAML validation: `yq eval '.name' file.md` or Python yaml parser
3. Check all required sections present
4. Verify length and focus
5. Compare to examples for archetype
6. If issues found: Generate detailed feedback
7. Wait for fixes
8. Re-validate (iterate until pass)

## Validation Commands
```bash
# YAML validation
python3 -c "import yaml, sys; yaml.safe_load(open(sys.argv[1]).read().split('---')[1])" file.md

# Word count
wc -w file.md

# Check required sections
grep -E "^## (Core Responsibilities|Working Protocol|Output Standards)" file.md
```
```

#### Task 6: Orchestration Mechanism (Custom Command Approach)

```markdown
# .claude/commands/build-subagent.md

Triggers multi-agent workflow to create Claude Code subagent.

## Usage
/build-subagent [requirement]

Example: /build-subagent Create a subagent that monitors dependency vulnerabilities

## Workflow

### Phase 0: Clarification
Ask 2-3 targeted questions:
1. What should this subagent do? (core purpose)
2. What archetype? (Planner/Generator/Validator/Manager)
3. What tools might it need?

STOP and WAIT for user response.

### Phase 1: Planning
Invoke: claude-subagent-planner
Input: User request + clarifications
Output: planning/[name]/INITIAL.md

### Phase 2: Parallel Research
Invoke simultaneously (single message, 3 Task calls):
- claude-subagent-researcher → planning/[name]/research.md
- claude-subagent-tool-analyst → planning/[name]/tools.md
- claude-subagent-pattern-analyzer → planning/[name]/patterns.md

### Phase 3: Generation
Main agent:
1. Read all planning/*.md files
2. Synthesize research findings
3. Generate complete .claude/agents/[name].md
4. Follow patterns from research phase

### Phase 4: Validation
Invoke: claude-subagent-validator
Input: Generated .md file
Iterate until validation passes

### Phase 5: Delivery
Summary report:
- What was created
- Where it's located (.claude/agents/[name].md)
- How to use it
- Quality score
```

### Integration Points

```yaml
CLAUDE_CODE_TASK_TOOL:
  - Phase 2 uses Task tool with multiple invocations in single message
  - Each subagent gets own Task call with specific prompt
  - Enables true parallel execution

TODO_WRITE:
  - Track progress through phases
  - Mark each phase complete
  - Useful for debugging workflow

ARCHON_OPTIONAL:
  - If available, create project for tracking
  - Create tasks for each phase
  - Update status as workflow progresses
  - Store generated subagents in Archon docs

EXAMPLES_DIR:
  - All subagents must reference examples/claude-subagent-patterns/
  - Researcher searches this directory
  - Pattern-analyzer extracts from these files
  - Validator compares against these standards

PLANNING_DIR:
  - All planning outputs go to planning/[subagent-name]/
  - INITIAL.md, research.md, tools.md, patterns.md
  - Persist for debugging and iteration
  - Main agent reads all before generation
```

## Validation Loop

### Level 1: Individual Subagent Validation
```bash
# After creating each of the 5 subagents, validate:

# 1. YAML frontmatter is valid
python3 -c "import yaml; yaml.safe_load(open('.claude/agents/claude-subagent-planner.md').read().split('---')[1])"

# 2. Required fields present
grep -E "^name:|^description:|^tools:" .claude/agents/claude-subagent-planner.md

# 3. Structure matches patterns
grep -E "^## (Core Responsibilities|Working Protocol|Output Standards|Remember)" .claude/agents/claude-subagent-planner.md

# Expected: No errors, all sections present
```

### Level 2: Orchestration Testing
```bash
# Test the workflow manually:

# 1. Simulate Phase 0: Gather test requirements
TEST_REQ="Create a subagent that manages database migrations"

# 2. Test Phase 1: Invoke planner
# Use Claude Code Task tool to invoke claude-subagent-planner
# Verify: planning/database-migration-manager/INITIAL.md created

# 3. Test Phase 2: Parallel invocation
# Single message with 3 Task tool calls
# Verify: All 3 .md files created in planning/database-migration-manager/

# 4. Test Phase 3: Main agent generation
# Read planning files, synthesize, generate
# Verify: .claude/agents/database-migration-manager.md created

# 5. Test Phase 4: Validation
# Invoke validator subagent
# Verify: Validation passes or provides clear feedback
```

### Level 3: End-to-End Integration Test
```bash
# Full workflow test with real example:

# Test Case 1: Simple subagent request
REQUEST="Create a subagent that formats code automatically"
# Expected:
# - Complete workflow execution
# - Valid .md file in .claude/agents/
# - File matches quality of examples

# Test Case 2: Complex subagent request
REQUEST="Build a subagent that monitors CI/CD pipelines and alerts on failures"
# Expected:
# - Parallel research phase completes
# - Generated subagent has appropriate tools (Read, Bash, WebSearch)
# - Validator ensures quality

# Test Case 3: Validation catches issues
# Manually create invalid .md file
# Run validator
# Expected: Clear feedback on what's wrong, iteration loop works
```

## Final Validation Checklist

Before considering implementation complete:

- [ ] All 5 specialized subagents created and functional
- [ ] Each subagent has valid YAML frontmatter
- [ ] Each subagent follows archetype patterns from examples
- [ ] Orchestration mechanism (command or CLAUDE.md rules) implemented
- [ ] Planning directory structure in place
- [ ] Phase 0 clarification works
- [ ] Phase 1 (planner) creates comprehensive INITIAL.md
- [ ] Phase 2 (parallel research) executes simultaneously
- [ ] Phase 3 (generation) synthesizes research correctly
- [ ] Phase 4 (validation) catches quality issues
- [ ] Phase 5 (delivery) provides clear summary
- [ ] End-to-end test creates working subagent
- [ ] Generated subagents match quality of hand-crafted examples
- [ ] Generated subagents work when invoked in Claude Code

---

## Anti-Patterns to Avoid

### Workflow Anti-Patterns
- ❌ **Don't skip research phase** - Always analyze examples before generating
- ❌ **Don't execute phases sequentially when parallel is possible** - Phase 2 must be parallel
- ❌ **Don't ask users questions mid-workflow** - Be autonomous after Phase 0
- ❌ **Don't generate without synthesis** - Must read all planning docs before Phase 3

### Subagent Design Anti-Patterns
- ❌ **Don't create jack-of-all-trades subagents** - Keep focused, single responsibility
- ❌ **Don't give excessive tool access** - Minimal but sufficient
- ❌ **Don't write 1000+ word prompts** - Keep focused (100-500 words)
- ❌ **Don't ignore archetype patterns** - Each archetype has proven structure
- ❌ **Don't skip proactive triggers** - Description should say when to use

### Validation Anti-Patterns
- ❌ **Don't skip YAML validation** - Invalid YAML = broken subagent
- ❌ **Don't accept first draft** - Validation should iterate
- ❌ **Don't validate manually** - Use automated checks (yq, python yaml)
- ❌ **Don't compare against outdated patterns** - Always use latest examples

### Quality Anti-Patterns
- ❌ **Don't hardcode patterns** - Extract from examples dynamically
- ❌ **Don't assume tool requirements** - Analyst should determine
- ❌ **Don't create without clear archetype** - Archetype drives structure
- ❌ **Don't forget integration guidelines** - How does it work with others?

---

## PRP Self-Assessment

### Context Completeness: 9/10
✅ All necessary documentation URLs provided
✅ Real code examples from existing subagents
✅ Agent-factory orchestration patterns referenced
✅ Gotchas and pitfalls documented
⚠️ Could include more specific YAML validation tools/libraries

### Implementation Clarity: 9/10
✅ Clear task breakdown (7 tasks)
✅ Pseudocode for key subagents
✅ Orchestration workflow detailed
✅ Integration points specified
⚠️ Could provide more detail on error handling in orchestration

### Validation Rigor: 10/10
✅ Three levels of validation (individual, orchestration, e2e)
✅ Automated validation commands provided
✅ Clear acceptance criteria
✅ Iterative validation process defined
✅ Quality checklist comprehensive

### One-Pass Success Probability: 8/10

**Confidence Level: 8/10**

**Reasoning:**
- Strong foundation from well-researched patterns
- Clear phase-based implementation approach
- Comprehensive validation gates at each level
- Good examples and pseudocode provided
- Known gotchas documented

**Risk Factors:**
- Parallel execution complexity (mitigated by clear examples)
- YAML validation implementation details (mitigated by provided commands)
- Orchestration mechanism choice (custom command vs CLAUDE.md)
- First subagent might need iteration to get pattern right

**Mitigation:**
- Start with simplest subagent (validator or researcher)
- Test orchestration with manual invocations first
- Validate each subagent thoroughly before proceeding
- Use existing patterns as templates, not starting from scratch

---

## Quick Reference

### File Locations
```
.claude/agents/claude-subagent-planner.md         # Task 1
.claude/agents/claude-subagent-researcher.md      # Task 2
.claude/agents/claude-subagent-tool-analyst.md    # Task 3
.claude/agents/claude-subagent-pattern-analyzer.md # Task 4
.claude/agents/claude-subagent-validator.md       # Task 5
.claude/commands/build-subagent.md                # Task 6
planning/                                          # Task 7
```

### Key Commands
```bash
# YAML validation
python3 -c "import yaml; yaml.safe_load(open('file.md').read().split('---')[1])"

# Structure check
grep -E "^## (Core Responsibilities|Working Protocol)" file.md

# Word count
wc -w file.md | awk '{print $1}'

# Test invocation
# Use Claude Code Task tool or /build-subagent command
```

### Pattern Examples Priority
1. examples/claude-subagent-patterns/README.md - Start here
2. .claude/agents/documentation-manager.md - Manager archetype
3. .claude/agents/validation-gates.md - Validator archetype
4. examples/claude-subagent-patterns/pydantic-ai-planner.md - Planner archetype
5. repos/agent-factory-with-subagents/CLAUDE.md - Orchestration workflow

---

**Generated**: 2025-10-01
**Version**: 1.0
**Methodology**: PRP (Progressive Refinement Process) with comprehensive context engineering
**Expected Implementation Time**: 3-4 hours for all tasks + testing
**Complexity**: High (multi-agent orchestration, parallel execution, YAML validation)
