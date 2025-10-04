# Codebase Patterns: prp_workflow_improvements

## Search Summary

### Archon Code Examples Searched
- Query 1: "parallel subagent execution" → 5 results found
- Query 2: "command slash implementation" → 5 results found
- Query 3: "task validation loops" → 5 results found
- Query 4: "code extraction curator" → 5 results found
- Query 5: "agent definition yaml frontmatter" → 3 results found
- Query 6: "validation gates testing" → 3 results found

### Local Codebase Searches
- Pattern 1: "async.*def.*tool" in **/*.py → 0 matches (not Python focus)
- Pattern 2: "prp-initial-*.md" in .claude/agents/ → 6 matches (all factory subagents)
- Pattern 3: "pytest|test.*fixture" in **/*.py → 10 matches (test files)
- Pattern 4: "parallel.*execution|concurrent.*agents" in **/*.md → 3 matches

### Total Patterns Found
- Archon Examples: 26
- Local Examples: 19
- Combined Insights: 12 documented patterns

## Similar Implementations Found

### Pattern 1: INITIAL.md Factory Workflow (Complete Multi-Subagent System)

**Source**: [Local Files: CLAUDE.md lines 105-297, prps/PRP_create_initial_md_workflow.md]

**What It Demonstrates**:
Fully implemented 6-subagent orchestration system with parallel execution, Archon integration, autonomous operation, and quality gates. This is the PRIMARY pattern to follow.

**Code Structure**:
```
.claude/
├── agents/                                    # Subagent definitions
│   ├── prp-initial-feature-clarifier.md      # Phase 1: Analysis
│   ├── prp-initial-codebase-researcher.md    # Phase 2A: Patterns
│   ├── prp-initial-documentation-hunter.md   # Phase 2B: Docs
│   ├── prp-initial-example-curator.md        # Phase 2C: Code extraction
│   ├── prp-initial-gotcha-detective.md       # Phase 3: Pitfalls
│   └── prp-initial-assembler.md              # Phase 4: Synthesis
├── commands/
│   └── create-initial.md                     # Orchestrator (would be created)
└── CLAUDE.md                                  # Workflow documentation
```

**Key Code Pattern - Subagent Definition**:
```markdown
---
name: prp-initial-example-curator
description: USE PROACTIVELY for code example extraction and organization. Searches Archon and local codebase, EXTRACTS actual code to examples/{feature}/ directory, creates README with usage guidance. NOT just references - actual code files.
tools: Read, Write, Glob, Grep, Bash, mcp__archon__rag_search_code_examples
color: orange
---

# PRP INITIAL.md Example Curator

You are a code example extraction and organization specialist...

## Primary Objective

Search Archon and local codebase for relevant code examples, **EXTRACT** actual code to physical files in `examples/{feature}/` directory...
```

**Naming Convention**:
- Files: `prp-initial-{responsibility}.md` (kebab-case)
- Subagent names: `prp-initial-{responsibility}` (matches filename)
- Output files: `{feature}-analysis.md`, `codebase-patterns.md` (kebab-case)
- Directories: `prps/research/`, `examples/{feature}/` (snake_case for feature)
- Tools: `Read, Write, Grep, Glob, Bash, mcp__archon__*` (exact names)
- Colors: `orange, blue, green, purple, red, yellow` (subagent visual identity)

**What to Mimic**:
- YAML frontmatter structure (`name`, `description`, `tools`, `color`)
- "USE PROACTIVELY" in description for autonomous behavior
- Archon-first search strategy (check health, then search)
- Short queries to Archon (2-5 keywords maximum)
- Separate context windows per subagent (prevents pollution)
- Phase-based execution (0=clarify, 1=analyze, 2=parallel research, 3=gotchas, 4=assemble, 5=deliver)
- Quality gates (8+/10 required before proceeding)
- Research document structure (`prps/research/{document}.md`)
- Example extraction to physical files (not just references)

**What to Adapt**:
- Naming: Use `prp-gen-*` for generate-prp subagents, `prp-exec-*` for execute-prp subagents
- Responsibilities: Tailor to PRP generation/execution needs vs INITIAL.md creation
- Output locations: PRPs go to `prps/{feature}.md` not `prps/INITIAL_{feature}.md`
- Tools: Execute-prp needs validation tools (Bash for running tests), generate-prp needs research tools

### Pattern 2: Parallel Execution with Function Calls

**Source**: [Archon: pydantic-ai ProcessPoolExecutor example, Local: CLAUDE.md Phase 2 section]

**What It Demonstrates**:
How to invoke multiple subagents in a SINGLE message using parallel function_calls to achieve true concurrent execution.

**Example from Codebase**:
```markdown
# From CLAUDE.md lines 172-181
#### Phase 2: Parallel Research (CRITICAL PHASE)

**Subagents**: THREE simultaneously
- `prp-initial-codebase-researcher`
- `prp-initial-documentation-hunter`
- `prp-initial-example-curator`

⚠️ **CRITICAL**: Invoke all three in SINGLE message using parallel tool invocation
```

**Key Code Pattern**:
```python
# Conceptual pattern (actual implementation in Claude Code orchestrator)
# From feature-analysis.md lines 150-169
invoke_agents([
    {
        "name": "prp-gen-codebase-researcher",
        "input": "prps/research/feature-analysis.md",
        "output": "prps/research/codebase-patterns.md"
    },
    {
        "name": "prp-gen-documentation-hunter",
        "input": "prps/research/feature-analysis.md",
        "output": "prps/research/documentation-links.md"
    },
    {
        "name": "prp-gen-example-curator",
        "input": "prps/research/feature-analysis.md",
        "output": ["prps/research/examples-to-include.md", "examples/{feature}/*"]
    }
])
```

**Naming Convention**:
- Parallel phase naming: `Phase 2: Parallel {Context}` (uppercase Phase)
- Subagent invocation: Use agent name exactly as defined in frontmatter
- Input/output specification: Always document what each agent reads/writes

**What to Mimic**:
- Single message invocation for parallel execution (critical for speed)
- Clear input/output contracts for each subagent
- Three agents maximum in parallel phase (proven to work)
- Document which agents run in parallel vs sequential
- Use Phase 2 for parallel work (after initial analysis, before final assembly)

**What to Adapt**:
- For execute-prp: Parallel task execution groups (not research agents)
- Different agents: Code implementers vs researchers
- Dependency analysis: Determine which tasks can run in parallel

### Pattern 3: Archon MCP Integration

**Source**: [Local: .claude/commands/generate-prp.md lines 12-50, CLAUDE.md Archon section]

**What It Demonstrates**:
How to integrate Archon MCP for knowledge base search, project tracking, and task management. Always check health first, use as primary source, fallback to web search.

**Example from Codebase**:
```markdown
# From generate-prp.md lines 12-25
### 0. Check Knowledge Sources (FIRST)
```bash
# CRITICAL: Check if Archon MCP is available
mcp__archon__health_check()
```

**If Archon Available:**
- Use Archon RAG as PRIMARY research source
- Benefits: Faster, more accurate, curated documentation
- Web search only for gaps in Archon knowledge

**If Archon Not Available:**
- Use web_search as primary source
- Document URLs for future Archon ingestion
```

**Key Code Pattern**:
```python
# From CLAUDE.md Archon Integration section
# Always check health first
health = health_check()
archon_available = health["status"] == "healthy"

# If Archon available
if archon_available:
    # Create project for tracking
    project = manage_project("create", title="Feature", description="...")

    # Create tasks (one per phase)
    task1 = manage_task("create", project_id=project_id, title="Phase 1", task_order=10)

    # Update task status: "todo" → "doing" → "done"
    manage_task("update", task_id=task1.id, status="doing")

    # Search knowledge base (SHORT QUERIES!)
    results = rag_search_knowledge_base(query="async patterns", match_count=5)

    # Search code examples
    examples = rag_search_code_examples(query="FastAPI route", match_count=3)

    # Store final output
    manage_document("create", title="PRP", content="...", project_id=project_id)
```

**Naming Convention**:
- MCP tools: `mcp__archon__{function_name}` (double underscore prefix)
- Health check: Always `mcp__archon__health_check()` first
- Queries: 2-5 keywords maximum (e.g., "async patterns" not "how to implement async patterns in Python")
- Task status: `"todo"`, `"doing"`, `"review"`, `"done"` (exact database values)
- Task order: 0-100 (higher = higher priority)

**What to Mimic**:
- Health check FIRST before any Archon operations
- Short, focused search queries (2-5 keywords)
- Use RAG for documentation, code examples separately
- Create Archon project for each workflow execution
- Update task status as work progresses
- Store final artifacts in Archon (PRPs, INITIAL.md files)
- Pass project_id to subagents for context

**What to Adapt**:
- For execute-prp: Track implementation tasks in Archon
- For generate-prp: Track research tasks in Archon
- Different query patterns: PRP generation vs execution needs
- Task breakdown: Research phases vs implementation phases

### Pattern 4: Code Extraction to Physical Files

**Source**: [Local: .claude/agents/prp-initial-example-curator.md]

**What It Demonstrates**:
How to EXTRACT actual code to physical files instead of just referencing them. Critical for usability - developers need runnable code, not just pointers.

**Code Structure**:
```bash
examples/{feature_name}/
├── README.md                    # Comprehensive usage guide
├── {pattern_1}.py               # Extracted code file 1
├── {pattern_2}.py               # Extracted code file 2
├── {pattern_3}.py               # Extracted code file 3
└── test_{pattern}.py            # Test example if found
```

**Key Code Pattern**:
```python
# From prp-initial-example-curator.md lines 73-101
# Create examples directory
Bash(f"mkdir -p examples/{feature_name}")

# For each example found:
# 1. Read source
source_content = Read("path/to/source/file.py")

# 2. Extract relevant section (lines or full file)
if specific_pattern:
    # Extract specific lines
    code = extract_lines(source_content, start_line, end_line)
else:
    # Use entire file if small and relevant
    code = source_content

# 3. Create physical file in examples directory
Write(f"examples/{feature_name}/pattern_name.py", code)

# 4. Add source attribution as comment
attribution = f"""# Source: {original_file}
# Lines: {start_line}-{end_line}
# Pattern: {what_it_demonstrates}

{code}
"""
```

**README.md Structure**:
```markdown
# {Feature Name} - Code Examples

## Overview
This directory contains extracted code examples to reference during {feature_name} implementation. These are REAL code files extracted from working implementations, not pseudocode.

## Files in This Directory

| File | Source | Purpose | Relevance |
|------|--------|---------|-----------|
| {file1}.py | {source_path}:{lines} | {what_it_shows} | {X/10} |

## Detailed Example Guidance

### {file1}.py - {Pattern Name}

**Source**: `{original_file_path}` (lines {X}-{Y})

**What to Mimic**:
- {Specific technique 1}
- {Specific technique 2}

**What to Adapt**:
- {Different requirements}
```

**Naming Convention**:
- Directory: `examples/{feature_name}/` (snake_case)
- Files: `{descriptive_pattern_name}.py` (snake_case, descriptive)
- README: Always `README.md` (uppercase)
- Attribution comments: `# Source:`, `# Lines:`, `# Pattern:` (exact format)

**What to Mimic**:
- EXTRACT to physical files, not just markdown references
- Include source attribution in every file
- Create comprehensive README with "what to mimic" guidance
- Table of contents in README showing all files
- Relevance score (X/10) for each example
- Detailed guidance per file explaining the pattern

**What to Adapt**:
- For generate-prp: Extract implementation patterns from codebase
- For execute-prp: Not applicable (execute uses examples, doesn't create them)
- Different file types: .ts, .tsx, .py, .md depending on tech stack
- Example relevance: Score based on similarity to new feature

### Pattern 5: Current generate-prp Command Structure

**Source**: [Local: .claude/commands/generate-prp.md]

**What It Demonstrates**:
Existing PRP generation approach - sequential research with Archon integration. Shows current state to improve upon.

**Key Code Pattern**:
```markdown
# From generate-prp.md lines 10-56
## Research Process

### 0. Check Knowledge Sources (FIRST)
# CRITICAL: Check if Archon MCP is available

### 1. Knowledge Research (Archon-First Approach)
**When Archon is Available:**
1. Search knowledge base for relevant documentation
2. Search for code examples and implementations
3. Use web_search ONLY for gaps

### 2. Codebase Analysis
- Search for similar features/patterns in the codebase
- Identify files to reference in PRP
- Note existing conventions to follow

### 3. User Clarification (if needed)
```

**Naming Convention**:
- Command files: `{action}-{noun}.md` (kebab-case, e.g., `generate-prp.md`)
- Research phases: Numbered (0, 1, 2, 3...)
- Output location: `PRPs/{feature-name}.md`
- Template: `PRPs/templates/prp_base.md`

**What to Mimic**:
- Archon health check FIRST (line 14)
- Research phases structure (0-3)
- Archon-first approach with web fallback
- ULTRATHINK step before writing PRP (lines 94-96)
- Quality checklist at end (lines 101-107)
- Confidence scoring (1-10 scale, line 108)

**What to Adapt**:
- SEQUENTIAL → PARALLEL research (apply factory Phase 2 pattern)
- Reference → EXTRACT code examples (apply curator pattern)
- Single agent → Multi-subagent (apply factory architecture)
- Manual research → Systematic (apply 6-subagent workflow)
- No gotcha detection → Dedicated detective subagent

### Pattern 6: Current execute-prp Command Structure

**Source**: [Local: .claude/commands/execute-prp.md]

**What It Demonstrates**:
Existing PRP execution approach - sequential with validation loops. Shows current state to improve upon.

**Key Code Pattern**:
```markdown
# From execute-prp.md
## Execution Process

1. **Load PRP**
   - Read the specified PRP file
   - Understand all context and requirements

2. **ULTRATHINK**
   - Think hard before you execute the plan
   - Break down complex tasks into smaller steps using TodoWrite
   - Identify implementation patterns from existing code

3. **Execute the plan**
   - Implement all the code

4. **Validate**
   - Run each validation command
   - Fix any failures
   - Re-run until all pass

5. **Complete**
   - Ensure all checklist items done
   - Run final validation suite
```

**Naming Convention**:
- Command: `execute-{noun}.md` (kebab-case)
- Process steps: Numbered (1-6)
- Validation: "Run → Fix → Re-run" loop pattern
- Task tracking: TodoWrite (but should be Archon per ARCHON-FIRST RULE)

**What to Mimic**:
- ULTRATHINK phase before implementation (line 16-20)
- Validation loops until passing (lines 26-29)
- Final checklist verification (lines 31-35)
- Can reference PRP again during execution (lines 37-39)

**What to Adapt**:
- TodoWrite → Archon task management (ARCHON-FIRST RULE)
- SEQUENTIAL → PARALLEL execution (task dependency analysis)
- Manual validation → Automated quality gates
- No test generation → Automated test generation based on patterns
- Single executor → Multiple parallel executors for independent tasks

### Pattern 7: Validation Gate Patterns

**Source**: [Local: infra/archon/python/tests/test_rag_simple.py, Archon: validation testing examples]

**What It Demonstrates**:
How to structure automated validation with pytest, fixtures, and quality gates.

**Example from Codebase**:
```python
# From test_rag_simple.py lines 24-42
@pytest.fixture
def mock_supabase():
    """Mock supabase client"""
    client = MagicMock()
    client.rpc.return_value.execute.return_value.data = []
    return client

@pytest.fixture
def rag_service(mock_supabase):
    """Create RAGService with mocked dependencies"""
    with patch("src.server.utils.get_supabase_client", return_value=mock_supabase):
        from src.server.services.search.rag_service import RAGService
        service = RAGService(supabase_client=mock_supabase)
        return service

class TestRAGServiceCore:
    """Core RAGService functionality tests"""

    def test_initialization(self, rag_service):
        """Test RAGService initializes correctly"""
        assert rag_service is not None
        assert hasattr(rag_service, "search_documents")
```

**Validation Commands Pattern**:
```bash
# From generate-prp.md lines 85-92
# Syntax/Style
ruff check --fix && mypy .

# Unit Tests
uv run pytest tests/ -v
```

**Naming Convention**:
- Test files: `test_{module}.py` (snake_case with test_ prefix)
- Fixtures: `mock_{service}`, `{service}_fixture` (descriptive)
- Test classes: `Test{Module}{Aspect}` (PascalCase)
- Test methods: `test_{scenario}` (snake_case)
- Validation levels: Syntax → Unit → Integration (progressive)

**What to Mimic**:
- Progressive validation levels (syntax, unit, integration)
- Fixture pattern for shared test setup
- MagicMock for external dependencies
- Context managers (with patch) for isolation
- Descriptive test docstrings
- Class-based test organization
- Assert patterns (assert not None, assert hasattr)

**What to Adapt**:
- For generate-prp: Validate PRP quality (completeness, references, structure)
- For execute-prp: Validate implementation (syntax, tests, integration)
- Auto-generate tests based on codebase patterns
- Iterative validation loops (run → fail → fix → re-run)

### Pattern 8: Agent Orchestrator Pattern

**Source**: [Local: CLAUDE.md INITIAL.md Factory section lines 127-157, 218-229]

**What It Demonstrates**:
How the main orchestrator (YOU, main Claude Code) coordinates subagents across phases.

**Key Code Pattern**:
```markdown
# From CLAUDE.md lines 129-157
### Immediate Recognition Actions

When you detect an INITIAL.md creation request:

1. ✅ **STOP** any other work immediately
2. ✅ **ACKNOWLEDGE**: "I'll help create a comprehensive INITIAL.md using the factory workflow"
3. ✅ **PROCEED** to Phase 0 (don't ask for permission)
4. ✅ **NEVER** skip Phase 0 clarifications
5. ✅ **NEVER** try to write INITIAL.md directly

### The 5-Phase Workflow

#### Phase 0: Recognition & Basic Clarification
**Who handles this**: YOU (main Claude Code)

**Your Actions**:
1. Ask 2-3 clarifying questions
2. ⚠️ **CRITICAL**: WAIT for user response - DO NOT PROCEED
3. After user responds:
   - Determine feature name (snake_case)
   - Create directories: `prps/research/`, `examples/{feature}/`
   - Check Archon: `health_check()`
   - Create Archon project and 6 tasks if available
   - Proceed to Phase 1
```

**Delivery Pattern**:
```markdown
# From CLAUDE.md lines 218-229
#### Phase 5: Delivery & Next Steps

**Who handles this**: YOU

**Your Actions**:
1. Present summary to user
2. Show file locations
3. Quality check summary
4. Provide next steps (/generate-prp, /execute-prp)
5. Update Archon with completion notes
6. Store INITIAL.md as Archon document
```

**Naming Convention**:
- Phases: `Phase 0` through `Phase 5` (numbered)
- Orchestrator role: "YOU (main Claude Code)" - explicit
- User interaction: Phase 0 only (autonomous after)
- Critical markers: `⚠️ **CRITICAL**:`, `✅ **action**`, `❌ **DON'T**`

**What to Mimic**:
- Immediate recognition of trigger patterns
- Explicit orchestrator responsibilities ("YOU handles this")
- Phase 0 clarifications BEFORE autonomous work
- Directory creation at start of workflow
- Archon setup (project + tasks) if available
- Final delivery with summary and next steps
- Storing results in Archon for future reference

**What to Adapt**:
- For generate-prp: Recognize INITIAL.md file as input trigger
- For execute-prp: Recognize PRP file as input trigger
- Different phases: Research vs Implementation vs Testing
- Quality gates between phases (don't proceed if score < 8/10)

### Pattern 9: Error Handling and Fallbacks

**Source**: [Local: CLAUDE.md lines 263-277, feature-analysis.md Assumption 4]

**What It Demonstrates**:
Graceful degradation when Archon unavailable, error handling patterns, fallback strategies.

**Example from Codebase**:
```markdown
# From CLAUDE.md lines 259-262
#### If Unavailable
- Proceed without tracking
- Workflow continues normally

### Error Handling
If subagent fails:
1. Log error with context
2. Continue with partial results
3. Document what's missing
4. Offer regeneration option
```

**Archon Fallback Pattern**:
```python
# From feature-analysis.md lines 283-286 (Assumption 4)
# Always check Archon health first, use as primary research source
# Fall back to web search only when needed

health = health_check()
if health["status"] == "healthy":
    # Use Archon RAG
    results = rag_search_knowledge_base(query="topic")
else:
    # Fallback to web search
    results = web_search("topic documentation")
    # Document URLs for future Archon ingestion
```

**Naming Convention**:
- Error states: Document failures clearly
- Fallback strategy: Primary → Secondary → Tertiary
- Partial results: Continue with what worked
- Regeneration: Offer option to retry

**What to Mimic**:
- Health check determines strategy (Archon vs web)
- Workflows continue even if features unavailable
- Log errors with context (which subagent, which phase)
- Partial results better than no results
- Offer regeneration for quality issues

**What to Adapt**:
- For execute-prp: Validation failures → iterative fixes
- For generate-prp: Research failures → alternative sources
- Task failures: Continue other parallel tasks, document failed ones
- Quality failures: Regenerate specific phase, not entire workflow

### Pattern 10: Quality Gates and Scoring

**Source**: [Local: CLAUDE.md lines 279-296, generate-prp.md lines 101-109]

**What It Demonstrates**:
How to implement quality gates that prevent low-quality outputs from proceeding to next phase.

**Example from Codebase**:
```markdown
# From CLAUDE.md lines 279-296
### Quality Gates

Before delivery, verify:
- [ ] Feature description comprehensive
- [ ] Examples extracted with guidance
- [ ] Documentation includes working examples
- [ ] Gotchas documented with solutions
- [ ] Follows INITIAL_EXAMPLE.md structure
- [ ] Quality score: 8+/10

### Success Metrics

- ✅ Total time: <10 minutes
- ✅ Quality: 8+/10
- ✅ Examples: 2-4 extracted
- ✅ Documentation: 3-5 sources
- ✅ Gotchas: 2-5 documented
- ✅ PRP generation works first attempt
```

**Scoring Pattern**:
```markdown
# From generate-prp.md lines 108-109
Score the PRP on a scale of 1-10 (confidence level to succeed in one-pass implementation using claude codes)
```

**Naming Convention**:
- Checklists: `- [ ]` markdown checkboxes
- Metrics: `✅` for success criteria
- Scoring: 1-10 scale (8+ required to proceed)
- Time limits: `<10 minutes` for INITIAL.md, adjust per workflow

**What to Mimic**:
- Checklist-based quality verification
- Quantitative metrics (time, count, score)
- 8+/10 threshold for quality
- Regeneration option if below threshold
- Success criteria measurable and specific

**What to Adapt**:
- For generate-prp: PRP completeness checklist
- For execute-prp: Implementation validation gates
- Different scoring criteria per phase
- Time targets: Research vs Implementation vs Testing

### Pattern 11: File Organization and Naming

**Source**: [Local: All factory files, CLAUDE.md structure]

**What It Demonstrates**:
Consistent file organization across commands, subagents, research outputs, and examples.

**Directory Structure**:
```
.claude/
├── agents/                    # All subagent definitions
│   ├── prp-initial-*.md      # Factory subagents
│   ├── prp-gen-*.md          # Generate-prp subagents (NEW)
│   └── prp-exec-*.md         # Execute-prp subagents (NEW)
├── commands/                  # Command entry points
│   ├── create-initial.md     # Factory orchestrator
│   ├── generate-prp.md       # Current (to enhance)
│   └── execute-prp.md        # Current (to enhance)

prps/
├── research/                  # Research artifacts
│   ├── feature-analysis.md
│   ├── codebase-patterns.md
│   ├── documentation-links.md
│   ├── examples-to-include.md
│   └── gotchas.md
├── templates/
│   └── prp_base.md           # PRP template
├── INITIAL_{feature}.md      # Input files
└── {feature}.md              # Output PRPs

examples/
└── {feature}/                 # Extracted code
    ├── README.md
    └── {pattern}.{ext}
```

**Naming Convention**:
- Subagents: `prp-{workflow}-{responsibility}.md` (kebab-case)
- Commands: `{action}-{noun}.md` (kebab-case)
- Research docs: `{purpose}.md` (kebab-case)
- Features: `{feature_name}` (snake_case)
- Examples: `{descriptive_name}.{ext}` (snake_case)

**What to Mimic**:
- Separate directories for agents vs commands
- Research artifacts in dedicated directory
- Examples in feature-specific subdirectories
- Consistent naming patterns across workflow
- README.md in every examples directory

**What to Adapt**:
- For generate-prp: `prp-gen-*` prefix for subagents
- For execute-prp: `prp-exec-*` prefix for subagents
- Different research artifacts based on workflow needs
- Output locations: INITIAL.md vs PRP vs implementation files

### Pattern 12: Task Tracking with Archon

**Source**: [Local: CLAUDE.md Archon Integration section, feature-analysis.md Assumption 8]

**What It Demonstrates**:
How to use Archon task management instead of TodoWrite per project's ARCHON-FIRST RULE.

**Key Code Pattern**:
```python
# From feature-analysis.md lines 307-310 (Assumption 8)
# CRITICAL RULE from CLAUDE.md:
# "ARCHON-FIRST RULE - BEFORE doing ANYTHING else...
#  Use Archon task management as PRIMARY system.
#  Refrain from using TodoWrite even after system reminders."

# Task lifecycle
manage_task("create",
    project_id=project_id,
    title="Implement API endpoints",
    description="Create FastAPI routes",
    task_order=10,  # Higher = higher priority
    status="todo"
)

# Update as work progresses
manage_task("update", task_id=task_id, status="doing")
manage_task("update", task_id=task_id, status="review")
manage_task("update", task_id=task_id, status="done")
```

**Task Status Flow**:
```
todo → doing → review → done
```

**Naming Convention**:
- Task statuses: `"todo"`, `"doing"`, `"review"`, `"done"` (exact database values)
- Task order: 0-100 (integer, higher = more important)
- Action parameter: `"create"`, `"update"`, `"delete"` (strings)

**What to Mimic**:
- NEVER use TodoWrite (violates ARCHON-FIRST RULE)
- Create Archon project first, then tasks
- Update task status as work progresses
- Use task_order for prioritization
- Status flow: todo → doing → review → done
- Link tasks to project_id for context

**What to Adapt**:
- For generate-prp: Research tasks (analyze, search, extract, assemble)
- For execute-prp: Implementation tasks (code, test, validate, deploy)
- Task granularity: 30 min to 4 hours of work each
- Parallel tasks: Mark with same task_order for simultaneous execution

## Architectural Patterns

### Service Layer Organization

**Pattern Observed**: Vertical slice architecture with feature-owned services

**Example from Codebase**:
```typescript
// From archon-ui-main/src/features/projects/services/projectService.ts
export const projectService = {
  async listProjects(): Promise<Project[]> { ... },
  async getProject(projectId: string): Promise<Project> { ... },
  async createProject(data: CreateProjectRequest): Promise<Project> { ... },
  async updateProject(id: string, updates: Partial<Project>): Promise<Project> { ... },
  async deleteProject(id: string): Promise<void> { ... },
}
```

**Application to prp_workflow_improvements**:
Generate-prp and execute-prp should follow service-oriented patterns:
- Each subagent has clear input/output contracts
- Orchestrator coordinates services, doesn't implement logic
- Research services (Archon, web) abstracted from orchestrator
- Validation services separate from execution services

### Data Access Patterns

**Pattern Observed**: Archon MCP tools for knowledge access, local file operations for code

**Example from Codebase**:
```python
# Archon RAG for documentation
results = mcp__archon__rag_search_knowledge_base(
    query="FastAPI patterns",  # SHORT queries
    match_count=5
)

# Local file search for code patterns
files = Grep(
    pattern="async.*def.*api",
    glob="**/*.py",
    output_mode="files_with_matches"
)

# Read specific file
content = Read("/absolute/path/to/file.py")
```

**Recommendations**:
- Use Archon for: Past PRPs, documentation, code examples, lessons learned
- Use Grep for: Local codebase pattern matching
- Use Read for: Extracting specific code sections
- Use Write for: Creating research documents, extracted examples
- Use Bash for: Running validation commands (pytest, ruff, mypy)

### Error Handling Patterns

**Pattern Observed**: Fail-forward with detailed logging, graceful degradation

**Example from Codebase**:
```markdown
# From CLAUDE.md Error Handling section
**When to Fail Fast and Loud**:
- Service startup failures
- Missing configuration
- Invalid data that would corrupt state

**When to Complete but Log Detailed Errors**:
- Batch processing (crawling, document processing)
- Background tasks
- Optional features

**Critical Nuance**: Never accept corrupted data
- Skip failed item entirely rather than storing corrupted data
```

**Best Practices Identified**:
- Subagent failures: Log, continue with partial results, offer regeneration
- Archon unavailable: Fall back to web search, document URLs for later ingestion
- Validation failures: Iterative fixes with detailed error messages
- Quality failures: Regenerate specific phase, not entire workflow
- User cancellation: Save partial progress, allow resume

### Testing Patterns

**Test File Organization**: Mirror source structure in tests/ subdirectory

**Fixture Patterns**:
```python
# From test_rag_simple.py
@pytest.fixture
def mock_supabase():
    """Mock external dependencies"""
    client = MagicMock()
    client.rpc.return_value.execute.return_value.data = []
    return client

@pytest.fixture
def service_under_test(mock_supabase):
    """Create service with mocked dependencies"""
    with patch("module.get_client", return_value=mock_supabase):
        from module import Service
        return Service(client=mock_supabase)
```

**Test Structure**:
- Naming: `test_{feature}_{scenario}.py`
- Organization: Class-based (`Test{Module}{Aspect}`)
- Fixtures: Reusable setup with clear names
- Assertions: Descriptive and specific
- Async: Use `@pytest.mark.asyncio` for async tests

## File Organization

### Typical Structure for Similar Features

```
vibes/
├── .claude/
│   ├── agents/
│   │   ├── prp-gen-feature-analyzer.md         # Phase 1
│   │   ├── prp-gen-codebase-researcher.md      # Phase 2A
│   │   ├── prp-gen-documentation-hunter.md     # Phase 2B
│   │   ├── prp-gen-example-curator.md          # Phase 2C
│   │   ├── prp-gen-gotcha-detective.md         # Phase 3
│   │   ├── prp-gen-assembler.md                # Phase 4
│   │   ├── prp-exec-task-analyzer.md           # Execute Phase 1
│   │   ├── prp-exec-implementer-*.md           # Execute Phase 2 (parallel)
│   │   └── prp-exec-validator.md               # Execute Phase 3
│   └── commands/
│       ├── generate-prp.md                      # Enhanced orchestrator
│       └── execute-prp.md                       # Enhanced orchestrator
├── prps/
│   ├── research/                                # Research artifacts
│   │   ├── feature-analysis.md
│   │   ├── codebase-patterns.md
│   │   ├── documentation-links.md
│   │   ├── examples-to-include.md
│   │   └── gotchas.md
│   ├── templates/
│   │   └── prp_base.md
│   ├── INITIAL_{feature}.md                     # Input to generate-prp
│   └── {feature}.md                             # Output from generate-prp
└── examples/
    └── {feature}/                               # Extracted code
        ├── README.md
        └── {pattern}.{ext}
```

**Rationale**: Mirrors INITIAL.md factory structure proven to work. Separate agents from commands, research from outputs, examples in dedicated directory.

### Module Naming Conventions

- Main module: `{action}-{noun}.md` for commands (e.g., `generate-prp.md`)
- Supporting modules: `prp-{workflow}-{responsibility}.md` for subagents
- Test modules: Not applicable (commands/agents are markdown, not code)
- Configuration: CLAUDE.md for workflow documentation

**Consistency Check**: New subagents follow `prp-{gen|exec|initial}-{role}` pattern. Research docs stay in `prps/research/`. Examples always in `examples/{feature}/`.

## Integration Points

### Archon Integration

**Pattern from Codebase**:
Always check health, create project, track tasks, store results

**Workflow**:
```python
# 1. Health check
health = mcp__archon__health_check()
archon_available = health["status"] == "healthy"

if archon_available:
    # 2. Create project
    project = mcp__archon__manage_project(
        "create",
        title="PRP: {feature_name}",
        description="Generating PRP for {feature}"
    )

    # 3. Create tasks (one per phase)
    for phase in phases:
        mcp__archon__manage_task(
            "create",
            project_id=project.id,
            title=phase.title,
            task_order=phase.priority
        )

    # 4. Update task status as work progresses
    mcp__archon__manage_task("update", task_id=id, status="doing")

    # 5. Store final result
    mcp__archon__manage_document(
        "create",
        title="PRP: {feature}",
        content=prp_content,
        project_id=project.id
    )
```

### Command Integration

**Pattern from Codebase**:
Commands invoke subagents, don't implement logic themselves

**Router Setup**: Commands in `.claude/commands/` are entry points
**Endpoint Naming**: `/{command-name}` (e.g., `/generate-prp`)
**Request/Response**: User provides INITIAL.md path → receives PRP path + summary

### Configuration Management

**Pattern from Codebase**:
CLAUDE.md documents workflows, subagents declare tools in frontmatter

**Environment Variables**: Archon MCP connection handled by Claude Code
**Config Files**: CLAUDE.md is the configuration (no separate config files)
**Secrets**: N/A (commands don't handle secrets directly)

## Code Style & Conventions

### Naming Conventions Summary

| Element | Convention | Example |
|---------|------------|---------|
| Subagent Files | prp-{workflow}-{role}.md | prp-gen-codebase-researcher.md |
| Command Files | {action}-{noun}.md | generate-prp.md |
| Research Docs | {purpose}.md | codebase-patterns.md |
| Feature Names | snake_case | prp_workflow_improvements |
| Example Files | {pattern}.{ext} | async_tool_pattern.py |
| Directories | snake_case or kebab-case | prps/research/, examples/feature/ |
| Archon Tools | mcp__archon__{function} | mcp__archon__rag_search_knowledge_base |
| Task Status | Database values | "todo", "doing", "review", "done" |

### Documentation Patterns

**Docstring Style**: Markdown documentation within agent files

**Example**:
```markdown
---
name: prp-gen-codebase-researcher
description: Searches Archon and local codebase for patterns...
tools: Read, Write, Grep, Glob, mcp__archon__rag_search_code_examples
color: blue
---

# PRP Generation Codebase Researcher

## Primary Objective
Search for patterns...

## Core Responsibilities
1. Read requirements
2. Search Archon
3. Extract patterns
```

### Import Organization

**Pattern Observed**: Tool declaration in YAML frontmatter

```yaml
tools: Read, Write, Grep, Glob, Bash, mcp__archon__rag_search_code_examples
```

Order: File tools (Read, Write) → Search tools (Grep, Glob) → Execution (Bash) → External (mcp__)

## Recommendations for prp_workflow_improvements

### Patterns to Follow

1. **Multi-Subagent Architecture**: Use 6 subagents for generate-prp, 3-5 for execute-prp
   - Source: INITIAL.md factory (proven pattern)
   - Benefit: Separate context windows prevent pollution, enable parallel execution
   - Implementation: Create subagents in `.claude/agents/` with YAML frontmatter

2. **Parallel Execution in Phase 2**: Invoke 3 research agents simultaneously
   - Source: Factory Phase 2 (3x speedup demonstrated)
   - Benefit: Reduces total time from 15-20 min to <10 min
   - Implementation: Single message with multiple agent invocations

3. **Archon-First Research**: Health check → Archon RAG → Web fallback
   - Source: generate-prp.md + factory pattern
   - Benefit: Faster, more accurate, curated knowledge
   - Implementation: Always `health_check()` first, short queries (2-5 keywords)

4. **Code Extraction to Files**: Physical files in examples/, not just references
   - Source: prp-initial-example-curator.md
   - Benefit: Developers get runnable code, not just pointers
   - Implementation: Read → Extract → Write with attribution + README

5. **Quality Gates**: 8+/10 score required before proceeding to next phase
   - Source: Factory quality gates
   - Benefit: Prevents low-quality outputs from cascading
   - Implementation: Checklist-based scoring, offer regeneration if < 8

6. **Archon Task Management**: Use Archon tasks, NEVER TodoWrite
   - Source: ARCHON-FIRST RULE in CLAUDE.md
   - Benefit: Centralized tracking, project context, persistence
   - Implementation: Create project → tasks → update status as work progresses

### Patterns to Avoid

1. **Anti-pattern**: Sequential execution when tasks are independent
   - Seen in: Current execute-prp.md (sequential steps)
   - Issue: Wastes time - many PRP tasks can run in parallel
   - Alternative: Analyze dependencies, group independent tasks, execute in parallel

2. **Anti-pattern**: TodoWrite for task tracking
   - Seen in: execute-prp.md line 19
   - Issue: Violates ARCHON-FIRST RULE, data not persisted
   - Alternative: Use `mcp__archon__manage_task()` for all task management

3. **Anti-pattern**: Reference examples instead of extracting code
   - Seen in: Current generate-prp (implies references)
   - Issue: Developers can't run/study the code easily
   - Alternative: Extract to physical files with README guidance

4. **Anti-pattern**: Long Archon queries
   - Seen in: Potential misuse (natural language queries)
   - Issue: Archon works best with 2-5 keywords, not sentences
   - Alternative: "async patterns" not "how to implement async patterns in Python"

5. **Anti-pattern**: Skipping quality gates
   - Seen in: Current commands lack quality scoring
   - Issue: Low-quality PRPs lead to implementation failures
   - Alternative: Score every output, require 8+/10, offer regeneration

### New Patterns Needed

If no similar codebase patterns exist:

1. **Task Dependency Analysis** (execute-prp)
   - **Gap**: No automated dependency detection in codebase
   - **Recommendation**: Parse PRP task list, identify "after" dependencies, create execution groups
   - **Rationale**: Enables parallel execution of independent tasks
   - **Example**:
   ```python
   # Analyze dependencies
   tasks = parse_prp_tasks(prp_content)
   groups = create_parallel_groups(tasks)  # Group by dependencies

   # Execute groups in parallel
   for group in groups:
       execute_parallel([task for task in group if no_dependencies(task)])
   ```

2. **Automated Test Generation** (execute-prp)
   - **Gap**: No test generation in current workflow
   - **Recommendation**: Extract test patterns from codebase, adapt to new feature
   - **Rationale**: Reduces testing burden, ensures consistency
   - **Example**:
   ```python
   # Find test patterns
   test_patterns = Grep(pattern="@pytest.fixture", glob="**/test_*.py")

   # Adapt to new feature
   new_tests = adapt_test_patterns(test_patterns, feature_code)

   # Write test file
   Write(f"tests/test_{feature}.py", new_tests)
   ```

3. **PRP Quality Scoring Algorithm** (generate-prp)
   - **Gap**: Subjective quality assessment
   - **Recommendation**: Checklist-based scoring with weighted criteria
   - **Rationale**: Objective, consistent, actionable
   - **Example**:
   ```markdown
   Quality Checklist (10 points total):
   - [ ] Feature description comprehensive (1 pt)
   - [ ] Examples extracted with code files (2 pts)
   - [ ] Documentation URLs included (1 pt)
   - [ ] Gotchas documented with solutions (2 pts)
   - [ ] Implementation blueprint clear (2 pts)
   - [ ] Validation gates executable (1 pt)
   - [ ] References existing patterns (1 pt)

   Score: X/10 (8+ required to proceed)
   ```

## Archon Code Examples Referenced

### Example 1: Human-in-the-Loop Workflow
- **Archon ID**: c0e629a894699314
- **Relevance**: 7/10
- **Key Takeaway**: Shows tool approval flow and task step generation patterns
- **Location in Archon**: pydantic-ai documentation, agent workflows

### Example 2: Configure Hook Commands
- **Archon ID**: 9a7d4217c64c9a0a
- **Relevance**: 8/10
- **Key Takeaway**: Command configuration structure for Claude Code
- **Location in Archon**: Claude Code documentation, hooks section

### Example 3: Run Graph with ProcessPoolExecutor
- **Archon ID**: c0e629a894699314
- **Relevance**: 6/10
- **Key Takeaway**: Parallel execution pattern with dependency injection
- **Location in Archon**: pydantic-ai graph examples

## Local Files Referenced

### File 1: /Users/jon/source/vibes/CLAUDE.md
- **Lines**: 105-304
- **Pattern Type**: Complete INITIAL.md factory workflow
- **Relevance**: 10/10 - PRIMARY pattern to follow

### File 2: /Users/jon/source/vibes/.claude/agents/prp-initial-example-curator.md
- **Lines**: 1-150
- **Pattern Type**: Code extraction and curation
- **Relevance**: 10/10 - Code extraction pattern for generate-prp

### File 3: /Users/jon/source/vibes/.claude/agents/prp-initial-assembler.md
- **Lines**: 1-100
- **Pattern Type**: Research synthesis and assembly
- **Relevance**: 9/10 - Final assembly pattern for generate-prp

### File 4: /Users/jon/source/vibes/.claude/commands/generate-prp.md
- **Lines**: 1-110
- **Pattern Type**: Current PRP generation flow
- **Relevance**: 10/10 - Shows what to enhance

### File 5: /Users/jon/source/vibes/.claude/commands/execute-prp.md
- **Lines**: 1-40
- **Pattern Type**: Current PRP execution flow
- **Relevance**: 10/10 - Shows what to enhance

### File 6: /Users/jon/source/vibes/prps/PRP_create_initial_md_workflow.md
- **Lines**: 1-100
- **Pattern Type**: Complete PRP documenting the factory
- **Relevance**: 9/10 - Shows PRP structure and success criteria

### File 7: /Users/jon/source/vibes/infra/archon/python/tests/test_rag_simple.py
- **Lines**: 1-80
- **Pattern Type**: Testing patterns with fixtures
- **Relevance**: 8/10 - Validation gate implementation

---
Generated: 2025-10-04
Archon Examples Referenced: 26
Local Files Referenced: 7
Total Patterns Documented: 12
Feature: prp_workflow_improvements
Archon Project: 398ad324-008c-41e4-92cc-c5df6207553a
