# Multi-Agent Claude Code Subagent Factory

## FEATURE: Multi-Agent Orchestration System for Building Claude Code Subagents

Build a comprehensive multi-agent orchestration workflow that uses specialized Claude Code subagents working together to research, plan, and generate high-quality Claude Code subagent definitions. Similar to repos/agent-factory-with-subagents but for creating `.claude/agents/*.md` files instead of Pydantic AI agents.

### Core Concept

Instead of a simple single-shot generator, this creates a sophisticated workflow where multiple Claude Code subagents collaborate to:
- Research existing patterns and best practices
- Analyze tool requirements
- Study similar subagents for structure
- Generate comprehensive, validated subagent definitions

### What This System Creates

Complete Claude Code subagent definition files (`.claude/agents/*.md`) through a multi-phase orchestration workflow.

## WORKFLOW ARCHITECTURE

```
User Request → Clarification → Planning → Parallel Research → Generation → Validation → Delivery
                                              ↓
                                    ┌─────────┴─────────┐
                                    │                   │
                        Research    │    Tool          │    Pattern
                        Subagent    │    Analyst       │    Analyzer
```

### Phase 0: Clarification
Main agent asks targeted questions to understand:
- What should the subagent do?
- What archetype? (Planner/Generator/Validator/Manager)
- What tools might it need?
- Any specific patterns to follow?

### Phase 1: Planning (Planner Subagent)
**Subagent**: `claude-subagent-planner.md` (to be created)

Creates comprehensive requirements document including:
- Subagent purpose and philosophy
- Core responsibilities breakdown
- Working protocol definition
- Integration requirements
- Success criteria

Output: `planning/INITIAL.md` with full requirements

### Phase 2: Parallel Research (3 Subagents Working Simultaneously)

**Subagent 1**: `claude-subagent-researcher.md` (to be created)
- Searches examples/claude-subagent-patterns/ for similar subagents
- Identifies best practices from existing definitions
- Finds relevant structural patterns
- Notes successful integration approaches

**Subagent 2**: `claude-subagent-tool-analyst.md` (to be created)
- Analyzes what tools the subagent needs
- Reviews tool combinations from examples
- Determines minimal tool set required
- Identifies security considerations

**Subagent 3**: `claude-subagent-pattern-analyzer.md` (to be created)
- Studies YAML frontmatter patterns
- Analyzes system prompt structures
- Reviews philosophy statements
- Examines working protocol formats

### Phase 3: Generation (Main Agent)
Main agent synthesizes all research to generate:
- Valid YAML frontmatter (name, description, tools, color)
- Focused system prompt (100-500 words)
- Clear responsibilities section
- Detailed working protocol
- Output standards
- Integration guidelines
- Remember section

Output: `.claude/agents/[name].md`

### Phase 4: Validation (Validator Subagent)
**Subagent**: `claude-subagent-validator.md` (to be created)

Validates generated subagent:
- YAML frontmatter structure and completeness
- System prompt length and focus
- All required sections present
- Tool selection appropriateness
- Pattern adherence to examples
- Markdown validity

Iterates until all checks pass.

### Phase 5: Delivery
- Final validated subagent saved to `.claude/agents/`
- Summary of what was created
- Usage instructions

## CORE FUNCTIONALITY

### Multi-Agent Coordination
- Main agent orchestrates the workflow
- Subagents work autonomously in their phase
- Phase 2 subagents execute in parallel
- Results synthesized before generation

### Research-Driven
- Analyzes 7 existing example subagents
- References pattern documentation
- Searches for similar implementations
- Identifies proven approaches

### Quality-Focused
- Multiple validation layers
- Iterative refinement
- Pattern adherence verification
- Comprehensive quality checks

### Context-Rich
- Gathers context from multiple sources
- Synthesizes research from specialized agents
- Creates comprehensive implementation plan
- Produces production-ready subagents

## EXAMPLES

### Existing Patterns (in examples/claude-subagent-patterns/)
These are the reference materials the research subagents will analyze:

**From agent-factory (Pydantic AI builders):**
- `pydantic-ai-planner.md` - Shows planner archetype pattern
- `pydantic-ai-prompt-engineer.md` - Shows generator archetype pattern
- `pydantic-ai-tool-integrator.md` - Shows analyzer archetype pattern
- `pydantic-ai-dependency-manager.md` - Shows manager archetype pattern
- `pydantic-ai-validator.md` - Shows validator archetype pattern

**From vibes:**
- `documentation-manager.md` - Shows proactive manager pattern
- `validation-gates.md` - Shows testing specialist pattern

**Pattern Documentation:**
- `examples/claude-subagent-patterns/README.md` - Comprehensive guide covering:
  - YAML frontmatter structure
  - System prompt patterns
  - Tool selection strategies
  - Common archetypes
  - Integration patterns
  - Quality criteria

### Workflow Example

**User Request**: "Create a subagent that manages database migrations"

**Phase 0 - Clarification**:
Main agent asks:
- What databases? (PostgreSQL, MySQL, etc.)
- What migration tool? (Alembic, Django migrations, etc.)
- Should it auto-detect changes or be manually triggered?

**Phase 1 - Planning**:
Planner subagent creates requirements:
- Purpose: Safe, automated database migration management
- Philosophy: "Reversible migrations preserve data integrity"
- Responsibilities: Detect changes, create migrations, validate, apply
- Tools needed: Read, Write, Edit, Bash, Grep

**Phase 2 - Parallel Research**:
- Researcher: Finds validation-gates.md has similar testing patterns
- Tool Analyst: Determines needs Bash for migration commands, Read/Write for files
- Pattern Analyzer: Notes validation-gates uses green color, has clear working protocol

**Phase 3 - Generation**:
Main agent creates complete subagent definition combining all research

**Phase 4 - Validation**:
Validator checks structure, validates YAML, ensures pattern adherence

**Phase 5 - Delivery**:
`database-migration-manager.md` ready to use in `.claude/agents/`

## DOCUMENTATION

### Claude Code Resources
- Subagents guide: https://docs.anthropic.com/en/docs/claude-code/subagents
- Custom agents: https://docs.anthropic.com/en/docs/claude-code/custom-agents
- Claude Code docs: https://docs.anthropic.com/en/docs/claude-code

### Reference Repositories
- Agent Factory patterns: repos/agent-factory-with-subagents/
  - Study the multi-agent orchestration workflow
  - Learn parallel subagent execution
  - Understand phase-based architecture
- Context Engineering: repos/context-engineering-intro/
  - PRP methodology
  - Validation loops
  - Quality gates

### Pattern Resources
- Vibes examples: examples/claude-subagent-patterns/
- Vibes existing agents: .claude/agents/documentation-manager.md, validation-gates.md
- Pattern guide: examples/claude-subagent-patterns/README.md

## SUBAGENTS TO CREATE

The system needs these specialized Claude Code subagents:

### 1. claude-subagent-planner.md
**Purpose**: Requirements gathering and planning for new subagents
**Tools**: Read, Write, Grep, Glob, WebSearch
**Archetype**: Planner/Analyst
**Key Responsibilities**:
- Analyze user requirements
- Research similar subagents
- Create comprehensive INITIAL.md
- Define success criteria

### 2. claude-subagent-researcher.md
**Purpose**: Research existing patterns and best practices
**Tools**: Read, Grep, Glob, WebSearch
**Archetype**: Analyst/Researcher
**Key Responsibilities**:
- Search examples directory
- Identify similar subagents
- Extract successful patterns
- Document findings

### 3. claude-subagent-tool-analyst.md
**Purpose**: Determine optimal tool requirements
**Tools**: Read, Grep, Glob
**Archetype**: Analyzer
**Key Responsibilities**:
- Analyze required capabilities
- Review tool combinations in examples
- Recommend minimal tool set
- Flag security considerations

### 4. claude-subagent-pattern-analyzer.md
**Purpose**: Study structural patterns from examples
**Tools**: Read, Grep, Glob
**Archetype**: Analyzer
**Key Responsibilities**:
- Analyze YAML frontmatter patterns
- Study system prompt structures
- Review working protocols
- Extract naming conventions

### 5. claude-subagent-validator.md
**Purpose**: Validate generated subagent quality
**Tools**: Read, Bash (for YAML validation)
**Archetype**: Validator/Tester
**Key Responsibilities**:
- Validate YAML structure
- Check required sections
- Verify pattern adherence
- Iterate until quality standards met

## ORCHESTRATION MECHANISM

### How the Workflow Gets Triggered

The orchestration should be triggered by CLAUDE.md rules or a custom command that recognizes patterns like:
- "Create a subagent that..."
- "I need a Claude agent for..."
- "Build a subagent to..."

### Phase Execution

**Sequential Phases**: 0 → 1 → 2 → 3 → 4 → 5

**Parallel Within Phase 2**: Research + Tool Analysis + Pattern Analysis happen simultaneously

### Output Location

- Planning documents: `planning/[subagent-name]/INITIAL.md`
- Final subagent: `.claude/agents/[subagent-name].md`

### Integration with Existing System

- Uses existing PRP methodology where applicable
- Leverages TodoWrite for task tracking
- Can integrate with Archon if available (optional)
- Works within vibes' existing workflow

## SUCCESS CRITERIA

### For the Orchestration System
- [ ] Multi-phase workflow executes correctly (0 → 5)
- [ ] Phase 2 subagents can execute in parallel
- [ ] Main agent successfully orchestrates all phases
- [ ] Generated subagents pass validation
- [ ] System handles user requests end-to-end

### For Generated Subagents
- [ ] Valid YAML frontmatter with all required fields
- [ ] System prompt is focused (100-500 words)
- [ ] All 7 required sections present
- [ ] Tool selection is minimal and appropriate
- [ ] Follows patterns from examples
- [ ] Works when invoked in Claude Code
- [ ] Matches quality of hand-crafted examples
- [ ] Saved to correct location

### For the Research Process
- [ ] Planner subagent creates comprehensive requirements
- [ ] Researcher finds relevant patterns
- [ ] Tool analyst provides appropriate recommendations
- [ ] Pattern analyzer extracts useful structures
- [ ] Validator catches quality issues

## TECHNICAL SETUP

### Input Format
User makes natural language request:
```
"Create a subagent that manages API documentation updates"
"I need an agent to monitor test coverage and suggest improvements"
"Build a subagent for dependency vulnerability scanning"
```

### Workflow Trigger
Either:
- **CLAUDE.md rules** that detect subagent creation requests
- **Custom command**: `/build-subagent [requirement]`
- **Proactive detection**: Main agent recognizes pattern

### Output Structure
```
.claude/agents/[subagent-name].md
planning/[subagent-name]/
├── INITIAL.md (from planner)
├── research.md (from researcher)
├── tools.md (from tool analyst)
└── patterns.md (from pattern analyzer)
```

## OTHER CONSIDERATIONS

### Complexity Management
- Start with Phase 0-1-3-4 (skip parallel research initially if needed)
- Add Phase 2 parallel execution once basic workflow works
- Can scale complexity as system proves itself

### Subagent Reusability
The 5 specialized subagents created for this system:
- Are themselves Claude Code subagents
- Can be used independently for other tasks
- Follow the same patterns they help create
- Become part of the vibes toolkit

### Quality Over Speed
- Emphasis on research and validation
- Multiple review layers
- Iterative refinement
- Production-ready output

### Learning from Agent-Factory
Key patterns to adopt:
- Phase-based architecture
- Parallel execution in Phase 2
- Autonomous subagent operation
- Validation loops
- Clear handoffs between phases

### Integration Points
- Uses examples/claude-subagent-patterns/ for research
- Stores planning docs in planning/
- Outputs to .claude/agents/
- Can leverage existing validation-gates agent
- Works with vibes' PRP system

### Archetype Detection
System should recognize requirements map to archetypes:
- "Planner/Analyst": Requirements, planning, research tasks
- "Generator/Builder": Creation, generation, building tasks
- "Validator/Tester": Testing, validation, checking tasks
- "Manager/Coordinator": Orchestration, maintenance, monitoring tasks

## ASSUMPTIONS

1. All 5 specialized subagents need to be created first
2. Parallel execution in Phase 2 is achievable with Claude Code subagents
3. Main agent can orchestrate the workflow via CLAUDE.md or custom command
4. Planning documents stored in planning/ directory
5. System will improve as more subagents are created (more examples to learn from)
6. Initial implementation may be simpler (fewer phases) and scale up
7. TodoWrite or Archon used for task tracking across phases

## WHAT MAKES THIS DIFFERENT

### vs. Simple /generate-subagent Command
- **Multi-agent**: Uses 5+ specialized subagents vs single command
- **Research-driven**: Deep analysis vs template-filling
- **Iterative**: Validation loops vs one-shot generation
- **Context-rich**: Gathers comprehensive context vs basic patterns

### vs. Agent-Factory (Pydantic AI)
- **Target**: Creates Claude Code subagents (.md files) vs Pydantic AI agents (Python packages)
- **Output**: Single markdown file vs full Python project
- **Complexity**: Simpler (one file) vs complex (multiple files, tests, dependencies)
- **Same Approach**: Multi-phase orchestration with specialized subagents

## EXPECTED OUTCOME

A system where you can say:
```
"Create a subagent that automatically refactors code for better performance"
```

And the system:
1. Clarifies requirements
2. Researches patterns via specialized subagents
3. Analyzes tools and structures in parallel
4. Generates comprehensive subagent definition
5. Validates quality
6. Delivers production-ready `.claude/agents/performance-refactoring-agent.md`

All with the same quality and thoroughness as the agent-factory creates Pydantic AI agents.

---

**Generated**: 2025-10-01
**Purpose**: Create multi-agent orchestration for building Claude Code subagents
**Methodology**: Adapted from agent-factory workflow for Claude subagent creation
**Next Step**: Run `/generate-prp INITIAL.md` to create comprehensive implementation plan
