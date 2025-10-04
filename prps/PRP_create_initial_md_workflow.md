name: "INITIAL.md Factory Workflow - Multi-Subagent System for PRP Generation"
description: |

## Purpose
Comprehensive PRP for building a multi-subagent workflow system that creates high-quality INITIAL.md files
through systematic research and analysis. Enables <10 minute INITIAL.md generation with 8+/10 quality score.

## Core Principles
1. **Archon-First Research**: Always check Archon MCP before external searches
2. **Parallel Execution**: Phase 2 runs 3 agents simultaneously
3. **Example Extraction**: Extract actual code, don't just reference
4. **Autonomous Operation**: Subagents work without user interaction after Phase 0
5. **Progressive Success**: Simple, working system first, then enhance

---

## Goal

Build a complete multi-subagent workflow system (the "INITIAL.md factory") that transforms user feature requests
into comprehensive, PRP-ready INITIAL.md files through systematic research, analysis, and synthesis.

**End State**: Users say "Create INITIAL.md for [feature]" → receive production-ready INITIAL.md in <10 minutes

## Why

### Business Value
- **Time Savings**: Reduces INITIAL.md creation from 30+ minutes manual work to <10 minutes automated
- **Quality Improvement**: Systematic research ensures comprehensive coverage and consistency
- **Knowledge Scaling**: Each INITIAL.md improves as Archon knowledge base grows
- **Future-Ready**: Naming convention enables additional workflows (prp-execute-*, prp-validate-*)

### User Impact
- Get high-quality requirements documents with minimal interaction
- Leverage accumulated knowledge automatically
- Consistent format and quality every time
- Immediate transition to PRP generation

### Integration
- Feeds directly into existing `/generate-prp` command
- Uses Archon MCP for knowledge augmentation
- Follows established agent-factory pattern
- Integrates with existing PRP workflow

## What

### User-Visible Behavior

**User Request**: "Help me create INITIAL.md for web scraper with rate limiting"

**System Response**:
1. Asks 2-3 clarifying questions (Phase 0)
2. Creates comprehensive INITIAL.md autonomously
3. Extracts relevant code examples to examples/{feature}/ directory
4. Generates research documents in prps/research/
5. Delivers complete INITIAL.md ready for `/generate-prp`

**Time**: <10 minutes total
**Quality**: 8+/10 PRP-readiness score

### Technical Requirements

**6 Specialized Subagents** (`.claude/agents/`):
1. `prp-initial-feature-clarifier.md` - Deep requirements analysis
2. `prp-initial-codebase-researcher.md` - Pattern extraction from codebase
3. `prp-initial-documentation-hunter.md` - Official docs research
4. `prp-initial-example-curator.md` - Code example extraction & organization
5. `prp-initial-gotcha-detective.md` - Security & pitfall identification
6. `prp-initial-assembler.md` - Final INITIAL.md synthesis

**Orchestrator Command** (`.claude/commands/create-initial.md`):
- Coordinates 5-phase workflow
- Handles Archon project/task creation
- Manages parallel execution in Phase 2
- Delivers final results to user

**CLAUDE.md Updates**:
- Comprehensive workflow documentation
- Trigger pattern recognition
- Phase-by-phase guidance
- Archon integration instructions

### Success Criteria

- [ ] All 6 subagent files created with proper YAML frontmatter
- [ ] Orchestrator command implements 5-phase workflow
- [ ] Phase 2 uses parallel tool invocation (single message, 3 agents)
- [ ] Example curator extracts code to examples/{feature}/ with README
- [ ] CLAUDE.md updated with comprehensive workflow section
- [ ] Research directory auto-created: prps/research/
- [ ] Complete workflow execution in <10 minutes
- [ ] Generated INITIAL.md follows INITIAL_EXAMPLE.md structure
- [ ] Archon integration works (health check, project/task creation, RAG search)
- [ ] Quality score: 8+/10 for generated INITIAL.md files

---

## All Needed Context

### Documentation & References

```yaml
# MUST READ - Include these in your context window

- file: /Users/jon/source/vibes/prps/INITIAL_create_initial_md_workflow.md
  why: Complete feature specification with architecture and requirements
  critical: Contains all components to build, examples, and validation criteria

- file: /Users/jon/source/vibes/repos/context-engineering-intro/use-cases/agent-factory-with-subagents/CLAUDE.md
  why: Primary pattern reference for multi-subagent orchestration
  critical: Shows 5-phase workflow, parallel execution, Archon integration

- file: /Users/jon/source/vibes/repos/context-engineering-intro/use-cases/agent-factory-with-subagents/.claude/agents/pydantic-ai-planner.md
  why: Example subagent structure with YAML frontmatter
  critical: Shows autonomous working protocol, output standards

- file: /Users/jon/source/vibes/.claude/agents/documentation-manager.md
  why: Existing subagent pattern in vibes project
  critical: Shows simple, effective subagent structure

- file: /Users/jon/source/vibes/.claude/agents/validation-gates.md
  why: Testing/validation specialist pattern
  critical: Shows TodoWrite tool usage, validation approach

- file: /Users/jon/source/vibes/infra/archon/.claude/agents/library-researcher.md
  why: Archon-first research strategy pattern
  critical: Shows Archon MCP tool usage, output format

- file: /Users/jon/source/vibes/repos/context-engineering-intro/INITIAL_EXAMPLE.md
  why: Target INITIAL.md structure and format
  critical: Assembler must follow this format exactly

- file: /Users/jon/source/vibes/prps/templates/prp_base.md
  why: PRP template structure
  critical: Shows what INITIAL.md will feed into

- url: https://docs.claude.com/en/docs/claude-code/sub-agents
  why: Official Claude Code subagent documentation
  section: YAML frontmatter format, tool restrictions, context windows
  critical: Proper subagent configuration

- url: https://medium.com/@codecentrevibe/claude-code-multi-agent-parallel-coding-83271c4675fa
  why: Parallel subagent execution patterns
  section: How to invoke multiple agents in single message
  critical: Phase 2 parallel execution implementation

- url: https://zachwills.net/how-to-use-claude-code-subagents-to-parallelize-development/
  why: Practical parallel invocation examples
  section: Task tool batch execution
  critical: Avoiding sequential execution antipattern
```

### Current Codebase Tree

```bash
vibes/
├── .claude/
│   ├── agents/
│   │   ├── documentation-manager.md        # Existing: Proactive docs
│   │   └── validation-gates.md             # Existing: Testing specialist
│   └── commands/
│       ├── generate-prp.md                 # Existing: PRP generation
│       └── execute-prp.md                  # Existing: PRP execution
│
├── prps/
│   └── templates/
│       └── prp_base.md                     # PRP template
│
├── repos/
│   └── context-engineering-intro/
│       ├── INITIAL_EXAMPLE.md              # Target format
│       └── use-cases/agent-factory-with-subagents/
│           ├── CLAUDE.md                   # Pattern reference
│           └── .claude/agents/             # Example subagents
│
├── infra/archon/.claude/agents/
│   ├── codebase-analyst.md                 # Archon pattern
│   └── library-researcher.md               # Archon pattern
│
└── CLAUDE.md                               # Main instructions
```

### Desired Codebase Tree

```bash
vibes/
├── .claude/
│   ├── agents/
│   │   ├── documentation-manager.md                    # Existing
│   │   ├── validation-gates.md                         # Existing
│   │   ├── prp-initial-feature-clarifier.md           # NEW: Phase 1 agent
│   │   ├── prp-initial-codebase-researcher.md         # NEW: Phase 2A agent
│   │   ├── prp-initial-documentation-hunter.md        # NEW: Phase 2B agent
│   │   ├── prp-initial-example-curator.md             # NEW: Phase 2C agent
│   │   ├── prp-initial-gotcha-detective.md            # NEW: Phase 3 agent
│   │   └── prp-initial-assembler.md                   # NEW: Phase 4 agent
│   │
│   └── commands/
│       ├── generate-prp.md                             # Existing
│       ├── execute-prp.md                              # Existing
│       └── create-initial.md                           # NEW: Main orchestrator
│
├── prps/
│   ├── research/                                        # NEW: Auto-created
│   │   ├── feature-analysis.md                         # Phase 1 output
│   │   ├── codebase-patterns.md                        # Phase 2A output
│   │   ├── documentation-links.md                      # Phase 2B output
│   │   ├── examples-to-include.md                      # Phase 2C output
│   │   └── gotchas.md                                  # Phase 3 output
│   │
│   ├── INITIAL_{feature-name}.md                       # Phase 4 output
│   └── templates/prp_base.md                           # Existing
│
├── examples/                                            # NEW: Auto-created
│   └── {feature-name}/                                 # Created per feature
│       ├── README.md                                   # Example guidance
│       ├── pattern_1.py                                # Extracted code
│       ├── pattern_2.py                                # Extracted code
│       └── test_pattern.py                             # Extracted test
│
└── CLAUDE.md                                           # UPDATED: Workflow docs
```

### Known Gotchas & Library Quirks

```python
# CRITICAL: Claude Code Subagent Requirements
# - YAML frontmatter MUST be valid (name, description, tools)
# - Subagents invoked via Task tool, not direct calls
# - Each subagent has separate context window
# - Tool restrictions enforced via 'tools:' field in YAML

# CRITICAL: Parallel Execution Pattern
# - Phase 2 MUST invoke all 3 agents in SINGLE message
# - Use multiple Task tool calls in one message block
# - NOT: invoke agent 1, wait, invoke agent 2
# - YES: invoke all 3 agents in parallel tool invocation

# CRITICAL: Archon MCP Integration
# - Always health_check() BEFORE creating projects/tasks
# - Pass project_id to subagents via context
# - Update task status: "todo" → "doing" → "done"
# - Graceful degradation if Archon unavailable

# CRITICAL: Example Extraction
# - Must READ source files and extract actual code
# - Create physical files in examples/{feature}/ directory
# - NOT just markdown references to existing files
# - Generate README.md explaining each example

# CRITICAL: CLAUDE.md Recognition
# - Add trigger patterns for workflow activation
# - Must be early in CLAUDE.md file structure
# - Include complete 5-phase workflow documentation
# - Provide Archon integration guide

# GOTCHA: TodoWrite vs Archon
# - Per CLAUDE.md: Archon-first rule, avoid TodoWrite
# - But system reminders will suggest TodoWrite
# - Ignore TodoWrite reminders, use Archon exclusively

# GOTCHA: Query Shortness
# - Archon RAG works best with 2-5 keywords
# - NOT: "how to implement vector search with pgvector..."
# - YES: "vector search pgvector"
# - Keep queries concise and focused

# GOTCHA: File Paths
# - All paths must be absolute in subagent outputs
# - Use EXACT feature name passed from orchestrator
# - prps/research/ not prps/{feature}/research/
# - examples/{feature}/ not examples/research/{feature}/
```

---

## Implementation Blueprint

### Phase 0: Setup & Directory Structure (YOU do this, not subagents)

**Create Base Directories**:
```bash
mkdir -p .claude/agents
mkdir -p .claude/commands
mkdir -p prps/research
mkdir -p examples
```

### Task 1: Create prp-initial-feature-clarifier.md

**Location**: `.claude/agents/prp-initial-feature-clarifier.md`

**YAML Frontmatter**:
```yaml
---
name: prp-initial-feature-clarifier
description: USE PROACTIVELY for deep feature analysis. Decomposes user requests into comprehensive requirements, searches Archon for similar features, makes intelligent assumptions, creates feature-analysis.md. Works autonomously without user interaction.
tools: Read, Write, Grep, Glob, WebSearch, mcp__archon__rag_search_knowledge_base, mcp__archon__search_code_examples, mcp__archon__find_projects
color: blue
---
```

**Core Responsibilities**:
1. Receive user request + clarifications + feature name + Archon project ID
2. Search Archon for similar features using `rag_search_knowledge_base`
3. Decompose request into explicit and implicit requirements
4. Make intelligent assumptions for gaps (document clearly)
5. Identify technical components needed
6. Create `prps/research/feature-analysis.md`

**Output Format** (feature-analysis.md):
```markdown
# Feature Analysis: {feature_name}

## User Request Summary
[Original request and clarifications]

## Core Requirements
1. [Primary feature]
2. [Secondary feature]
3. [Additional features]

## Technical Components
- **Data Models**: [What needs to be stored/validated]
- **External APIs**: [Third-party integrations]
- **Processing Logic**: [Core algorithms/workflows]
- **UI/CLI Requirements**: [User interface needs]

## Similar Features Found (Archon Search)
- **Feature**: [Name]
  - **Source**: [Project/file]
  - **Similarity**: [What's similar]
  - **Lessons**: [What to reuse/avoid]

## Assumptions Made
- [Assumption 1]: [Reasoning]
- [Assumption 2]: [Reasoning]

## Success Criteria
- [ ] [Measurable outcome 1]
- [ ] [Measurable outcome 2]

---
Generated: {date}
Archon Project: {project_id}
```

**Validation**: File exists at `prps/research/feature-analysis.md` with all sections populated

---

### Task 2: Create prp-initial-codebase-researcher.md

**Location**: `.claude/agents/prp-initial-codebase-researcher.md`

**YAML Frontmatter**:
```yaml
---
name: prp-initial-codebase-researcher
description: USE PROACTIVELY for codebase pattern extraction. Searches Archon code examples and local codebase for similar implementations, extracts naming conventions and architectural patterns, creates codebase-patterns.md. Works autonomously.
tools: Read, Grep, Glob, Write, mcp__archon__search_code_examples, mcp__archon__rag_search_knowledge_base
color: green
---
```

**Core Responsibilities**:
1. Read `prps/research/feature-analysis.md` for requirements
2. Search Archon code examples using `search_code_examples` (2-5 keywords)
3. Use Grep to find similar local implementations
4. Extract naming conventions, file structures, patterns
5. Identify testing patterns from existing code
6. Create `prps/research/codebase-patterns.md`

**Search Strategy**:
```python
# Archon-First Pattern
archon_results = search_code_examples(query="async tool implementation")
if archon_results:
    analyze(archon_results)
else:
    # Fallback to local grep
    grep_results = grep("async.*def.*tool", pattern="*.py")
```

**Output Format** (codebase-patterns.md):
```markdown
# Codebase Patterns: {feature_name}

## Similar Implementations Found

### Pattern 1: {Name}
- **Source**: [File path or Archon example ID]
- **Pattern**: [What it demonstrates]
- **Code Structure**:
  ```
  src/
  ├── feature/
  │   ├── models.py
  │   ├── service.py
  │   └── tests/
  ```
- **Naming Convention**: [snake_case, camelCase, etc.]
- **Key Insights**: [What to mimic]

## Architectural Patterns
- **Service Layer**: [How business logic is organized]
- **Data Access**: [ORM, SQL, API patterns]
- **Error Handling**: [Try/except patterns, custom exceptions]
- **Testing**: [Test file locations, fixture patterns]

## File Organization
- **Typical Structure**: [Where similar features live]
- **Module Naming**: [Conventions to follow]
- **Test Placement**: [Test directory structure]

## Integration Points
- **Database**: [Migration patterns, schema design]
- **API Routes**: [Endpoint patterns, router setup]
- **Configuration**: [Settings.py, env vars]

## Recommendations
- **Follow**: [Existing patterns to use]
- **Avoid**: [Anti-patterns seen in codebase]
- **New Patterns Needed**: [If no similar code exists]

---
Generated: {date}
Archon Examples Referenced: [count]
Local Files Referenced: [count]
```

**Validation**: File exists with specific code examples and patterns extracted

---

### Task 3: Create prp-initial-documentation-hunter.md

**Location**: `.claude/agents/prp-initial-documentation-hunter.md`

**YAML Frontmatter**:
```yaml
---
name: prp-initial-documentation-hunter
description: USE PROACTIVELY for official documentation research. Searches Archon knowledge base first, then WebSearch for API references and implementation guides. Creates documentation-links.md with actionable URLs and code examples.
tools: WebSearch, WebFetch, Write, mcp__archon__rag_search_knowledge_base, mcp__archon__rag_get_available_sources
color: purple
---
```

**Core Responsibilities**:
1. Read `prps/research/feature-analysis.md` for tech stack
2. Check Archon available sources with `rag_get_available_sources`
3. Search Archon knowledge base using `rag_search_knowledge_base`
4. If not in Archon, use WebSearch for official docs
5. Find quickstart guides, API references, tutorials
6. Note version-specific considerations
7. Create `prps/research/documentation-links.md`

**Archon-First Strategy**:
```python
# 1. Get available sources
sources = rag_get_available_sources()

# 2. Search Archon for technology docs
results = rag_search_knowledge_base(query="FastAPI async patterns", match_count=5)

# 3. If found in Archon, prioritize those
if results:
    use_archon_docs(results)
else:
    # 4. Fallback to web search
    web_results = WebSearch("FastAPI official documentation 2025")
```

**Output Format** (documentation-links.md):
```markdown
# Documentation Links: {feature_name}

## Technology Stack Identified
- **Primary Language**: Python 3.12
- **Framework**: FastAPI
- **Database**: PostgreSQL + pgvector
- **LLM Library**: Pydantic AI
- **Other**: [Additional libraries]

## Archon Knowledge Base Results

### FastAPI Documentation
- **Source**: Archon (source_id: src_abc123)
- **Relevance**: 9/10
- **Key Sections**:
  - Async endpoints: [Archon excerpt or URL]
  - Dependency injection: [Archon excerpt or URL]
  - Testing: [Archon excerpt or URL]

## Official Documentation URLs

### FastAPI
- **Quickstart**: https://fastapi.tiangolo.com/tutorial/
- **Async Guide**: https://fastapi.tiangolo.com/async/
  - **Why**: Explains async/await patterns critical for agent tools
  - **Key Code Example**: [Include if available]

### Pydantic AI
- **Main Docs**: https://ai.pydantic.dev/
- **Tool Development**: https://ai.pydantic.dev/tools/
  - **Why**: Shows @agent.tool decorator pattern
  - **Critical Gotcha**: RunContext[DepsType] required for context-aware tools

## Implementation Tutorials
- **Article**: [URL]
  - **Relevance**: Shows end-to-end example
  - **Code Quality**: High/Medium/Low
  - **Notes**: [What to use from this]

## Version Considerations
- **FastAPI**: v0.104+ (async dependency injection improved)
- **Pydantic AI**: v0.0.14+ (latest stable)
- **Breaking Changes**: [Any known issues]

## Common Pitfalls Documented
- **Pitfall**: Sync functions in async context
  - **Solution**: Use async def for all agent tools
  - **Source**: [URL or Archon reference]

---
Generated: {date}
Archon Sources Used: [count]
External URLs: [count]
```

**Validation**: File contains actionable URLs with specific sections identified

---

### Task 4: Create prp-initial-example-curator.md

**Location**: `.claude/agents/prp-initial-example-curator.md`

**YAML Frontmatter**:
```yaml
---
name: prp-initial-example-curator
description: USE PROACTIVELY for code example extraction and organization. Searches Archon and local codebase, EXTRACTS actual code to examples/{feature}/ directory, creates README with usage guidance. NOT just references - actual code files.
tools: Read, Write, Glob, Grep, Bash, mcp__archon__search_code_examples
color: orange
---
```

**Core Responsibilities**:
1. Read `prps/research/feature-analysis.md` for requirements
2. Search Archon code examples
3. Find relevant local code using Grep/Glob
4. **EXTRACT** code snippets to physical files
5. Create `examples/{feature}/` directory
6. Generate comprehensive README.md
7. Create `prps/research/examples-to-include.md`

**CRITICAL: Code Extraction Pattern**:
```python
# NOT just referencing files - EXTRACT actual code

# 1. Find relevant code
archon_examples = search_code_examples(query="async tool")
local_files = grep("@agent.tool", pattern="*.py", output_mode="files_with_matches")

# 2. Read source files
source_content = Read(file_path="src/agents/example.py")

# 3. Extract specific lines or sections
extracted_code = source_content[45:67]  # Lines 45-67

# 4. Write to examples directory
Write(file_path=f"examples/{feature_name}/tool_pattern.py", content=extracted_code)
```

**Directory Creation**:
```bash
# MUST create this structure
mkdir -p examples/{feature_name}

# Result:
examples/{feature_name}/
├── README.md                    # Usage guidance
├── api_pattern.py               # Extracted code
├── validation_pattern.py        # Extracted code
└── test_pattern.py              # Extracted test
```

**README.md Template**:
```markdown
# {Feature Name} - Code Examples

## Overview
This directory contains extracted code examples to reference during {feature_name} implementation.

## Files in This Directory

| File | Source | Purpose | Relevance |
|------|--------|---------|-----------|
| api_pattern.py | src/api/auth.py:45-67 | Authentication pattern | 9/10 |
| validation_pattern.py | Archon example #123 | Input validation | 8/10 |
| test_pattern.py | tests/test_api.py:20-45 | Testing approach | 7/10 |

## Detailed Example Guidance

### api_pattern.py
**Source**: `src/api/auth.py` (lines 45-67)
**Original Context**: User authentication endpoint

**What to Mimic**:
- Token validation approach
- Error handling with try/except
- Response structure format

**What to Adapt**:
- Replace auth-specific logic with {feature} logic
- Adjust validation rules for your use case
- Keep error handling pattern intact

**What to Skip**:
- Database-specific queries (use your DB pattern)
- UI-specific rendering logic

**Key Pattern Highlights**:
```python
# Pattern: Error collection instead of fail-fast
errors = []
if not valid_x:
    errors.append("X invalid")
if not valid_y:
    errors.append("Y invalid")
if errors:
    return error_response(errors)
```

**Why This Example**:
Shows how to validate multiple fields and return comprehensive error messages,
critical for {specific reason related to feature}.

### validation_pattern.py
[Similar detailed guidance for each file]

## Usage Instructions

1. **Study the patterns** before writing code
2. **Copy patterns**, not specific logic
3. **Adapt** to your feature's needs
4. **Test** that patterns work in your context

## Pattern Summary

**Common Patterns Across Examples**:
- Async/await for all I/O operations
- Pydantic models for validation
- Try/except with specific exception types
- Structured error responses

**Testing Patterns**:
- Use pytest fixtures for setup
- Mock external dependencies
- Test happy path + edge cases + errors

---
Generated: {date}
Total Examples: {count}
Archon Examples: {count}
Local Examples: {count}
```

**Output Format** (examples-to-include.md):
```markdown
# Examples to Include: {feature_name}

## Extraction Summary

✅ Created examples/{feature_name}/ directory
✅ Generated README.md with {count} examples documented
✅ Extracted {count} code files

## Examples Extracted

### Example 1: API Pattern
- **Source**: src/api/auth.py
- **Lines**: 45-67
- **Destination**: examples/{feature_name}/api_pattern.py
- **Relevance**: 9/10 - Shows authentication approach
- **Extraction Status**: ✅ Complete
- **Guidance Added**: What to mimic, adapt, skip

### Example 2: Validation Logic
- **Source**: Archon code example #123
- **Destination**: examples/{feature_name}/validation_pattern.py
- **Relevance**: 8/10 - Error collection pattern
- **Extraction Status**: ✅ Complete
- **Guidance Added**: Pattern highlights, why this example

### Example 3: Test Pattern
- **Source**: tests/test_api.py
- **Lines**: 20-45
- **Destination**: examples/{feature_name}/test_pattern.py
- **Relevance**: 7/10 - Testing approach
- **Extraction Status**: ✅ Complete
- **Guidance Added**: Fixture patterns, mock usage

## Files Created
```
examples/{feature_name}/
├── README.md                    ✅
├── api_pattern.py               ✅
├── validation_pattern.py        ✅
└── test_pattern.py              ✅
```

## Usage in INITIAL.md

Reference examples directory like this:
```markdown
## EXAMPLES:

See `examples/{feature_name}/` for extracted code examples.

- **examples/{feature_name}/README.md** - Overview and detailed guidance
- **examples/{feature_name}/api_pattern.py** - Use for API endpoint structure
- **examples/{feature_name}/validation_pattern.py** - Use for input validation
- **examples/{feature_name}/test_pattern.py** - Use for testing approach

Each example includes:
- Source attribution
- What to mimic vs. what to adapt
- Pattern highlights with code snippets
- Relevance score for your feature
```

---
Generated: {date}
Total Files Extracted: {count}
```

**Validation**:
- [ ] examples/{feature}/ directory exists
- [ ] README.md generated with detailed guidance
- [ ] 2-4 code files extracted
- [ ] Each example has "what to mimic" notes

---

### Task 5: Create prp-initial-gotcha-detective.md

**Location**: `.claude/agents/prp-initial-gotcha-detective.md`

**YAML Frontmatter**:
```yaml
---
name: prp-initial-gotcha-detective
description: USE PROACTIVELY for security and pitfall detection. Searches Archon and web for known issues, common mistakes, performance concerns. Creates gotchas.md with solutions, not just warnings.
tools: WebSearch, WebFetch, Write, mcp__archon__rag_search_knowledge_base
color: red
---
```

**Core Responsibilities**:
1. Read previous research documents
2. Search Archon for known gotchas with technologies identified
3. Research common pitfalls via web (GitHub issues, Stack Overflow)
4. Identify security considerations
5. Document performance concerns
6. Note rate limits and quotas
7. Create `prps/research/gotchas.md` with SOLUTIONS

**Research Strategy**:
```python
# 1. Archon search for known issues
gotchas = rag_search_knowledge_base(query="FastAPI common pitfalls")

# 2. Web search for recent issues
github_issues = WebSearch("FastAPI async issues site:github.com 2024")

# 3. Security considerations
security = WebSearch("FastAPI security best practices OWASP")

# 4. Performance patterns
performance = WebSearch("FastAPI performance optimization async")
```

**Output Format** (gotchas.md):
```markdown
# Gotchas & Pitfalls: {feature_name}

## Security Considerations

### Issue: SQL Injection via Dynamic Queries
**Severity**: HIGH
**Impact**: Database compromise
**Solution**:
```python
# ❌ WRONG - vulnerable to injection
query = f"SELECT * FROM users WHERE name = '{user_input}'"

# ✅ RIGHT - use parameterized queries
query = "SELECT * FROM users WHERE name = %s"
cursor.execute(query, (user_input,))
```
**Source**: [Archon or URL]

### Issue: API Key Exposure in Logs
**Severity**: HIGH
**Impact**: Credential theft
**Solution**:
```python
# ❌ WRONG - logs API keys
logger.info(f"Using API key: {api_key}")

# ✅ RIGHT - mask sensitive data
logger.info(f"Using API key: {api_key[:8]}***")
```
**Source**: [Archon or URL]

## Common Pitfalls

### Pitfall: Async/Sync Mixing
**Problem**: Calling sync functions in async context blocks event loop
**Symptoms**: Slow performance, timeouts
**Solution**:
```python
# ❌ WRONG - blocks event loop
async def process():
    result = slow_sync_function()  # Blocks!

# ✅ RIGHT - use run_in_executor
async def process():
    loop = asyncio.get_event_loop()
    result = await loop.run_in_executor(None, slow_sync_function)
```
**Detection**: Use `asyncio` debug mode
**Source**: [URL]

### Pitfall: Missing Error Handling for External APIs
**Problem**: Unhandled API failures crash application
**Symptoms**: 500 errors, service unavailable
**Solution**:
```python
# ❌ WRONG - no error handling
response = await external_api.call(data)

# ✅ RIGHT - handle timeouts, rate limits, errors
try:
    response = await external_api.call(data)
except TimeoutError:
    # Retry with exponential backoff
except RateLimitError:
    # Queue for later processing
except APIError as e:
    # Log and return error response
```
**Source**: [URL]

## Performance Concerns

### Concern: N+1 Query Problem
**Impact**: Database overload, slow response times
**Scenario**: Loading related data in loops
**Solution**: Use eager loading or batch queries
**Code Example**:
```python
# ❌ WRONG - N+1 queries
for user in users:
    user.posts = db.query(Post).filter(Post.user_id == user.id).all()

# ✅ RIGHT - single query with join
users_with_posts = db.query(User).options(joinedload(User.posts)).all()
```

## Rate Limits & Quotas

### API: OpenAI GPT-4
- **Limit**: 10,000 tokens/minute (tier 1)
- **Quota**: 1M tokens/month
- **Handling**: Implement token counting, queue requests
- **Backoff**: Exponential with jitter

### API: Brave Search
- **Limit**: 1 request/second (free tier)
- **Quota**: 2,000 queries/month
- **Handling**: Rate limiter with Redis
- **Backoff**: Linear delay

## Version-Specific Issues

### FastAPI 0.104+ Breaking Changes
**Change**: Dependency injection order changed
**Impact**: Some dependencies fail to inject
**Migration**: Update dependency order in function signatures
**Source**: https://fastapi.tiangolo.com/release-notes/#0104

## Testing Gotchas

### Issue: TestModel Doesn't Validate Actual API Calls
**Problem**: Tests pass but real API fails
**Solution**: Use integration tests with FunctionModel
```python
# Unit test with TestModel (fast, but limited)
@pytest.fixture
def agent():
    return Agent("test")  # Uses TestModel

# Integration test with real model (slower, comprehensive)
@pytest.fixture
def agent_integration():
    return Agent("openai:gpt-4")  # Real API call
```

## Recommendations

### Do This:
- ✅ Use async def for all I/O operations
- ✅ Implement exponential backoff for retries
- ✅ Validate all external inputs with Pydantic
- ✅ Use environment variables for secrets
- ✅ Log errors with context, not just messages

### Don't Do This:
- ❌ Hardcode API keys or secrets
- ❌ Use sync functions in async context
- ❌ Ignore rate limits and quotas
- ❌ Skip input validation
- ❌ Return generic error messages

---
Generated: {date}
Security Issues: {count}
Performance Concerns: {count}
Rate Limits Documented: {count}
Sources Referenced: {count}
```

**Validation**: File contains solutions, not just warnings; includes code examples

---

### Task 6: Create prp-initial-assembler.md

**Location**: `.claude/agents/prp-initial-assembler.md`

**YAML Frontmatter**:
```yaml
---
name: prp-initial-assembler
description: USE PROACTIVELY for final INITIAL.md synthesis. Reads all 5 research documents, synthesizes into coherent INITIAL.md following INITIAL_EXAMPLE.md format. Ensures PRP-ready quality (8+/10). Works autonomously.
tools: Read, Write, mcp__archon__manage_document
color: yellow
---
```

**Core Responsibilities**:
1. Read ALL 5 research files from prps/research/
2. Read examples/{feature}/README.md for example context
3. Synthesize into INITIAL.md following INITIAL_EXAMPLE.md structure
4. Ensure comprehensive coverage of all requirements
5. Reference examples directory appropriately
6. Store in Archon (if available)
7. Create `prps/INITIAL_{feature_name}.md`

**Synthesis Process**:
```python
# 1. Load all research
feature_analysis = Read("prps/research/feature-analysis.md")
codebase_patterns = Read("prps/research/codebase-patterns.md")
documentation = Read("prps/research/documentation-links.md")
examples = Read("prps/research/examples-to-include.md")
gotchas = Read("prps/research/gotchas.md")
example_readme = Read(f"examples/{feature_name}/README.md")

# 2. Synthesize sections
# - Feature description from feature-analysis
# - Architecture from codebase-patterns
# - Documentation URLs from documentation
# - Examples reference from examples
# - Gotchas integrated throughout

# 3. Follow INITIAL_EXAMPLE.md structure exactly

# 4. Write final INITIAL.md
Write(f"prps/INITIAL_{feature_name}.md", synthesized_content)

# 5. Store in Archon if available
if archon_available:
    manage_document("create", project_id=project_id,
                   title=f"INITIAL: {feature_name}",
                   content=synthesized_content,
                   document_type="spec")
```

**Output Format** (INITIAL_{feature_name}.md):
```markdown
## FEATURE:

[Comprehensive feature description synthesized from feature-analysis]

## EXAMPLES:

See `examples/{feature_name}/` directory for extracted code examples.

### Code Examples Available:
- **examples/{feature_name}/README.md** - Overview and detailed guidance
- **examples/{feature_name}/api_pattern.py** - [From codebase-patterns]
- **examples/{feature_name}/validation_pattern.py** - [From examples research]
- **examples/{feature_name}/test_pattern.py** - [From codebase-patterns]

Each example includes:
- Source attribution
- What to mimic vs. what to adapt
- Pattern highlights with code snippets
- Relevance score for this feature

### Relevant Codebase Patterns:
[From codebase-patterns.md]
- **File**: src/similar/feature.py
  - **Pattern**: [What it shows]
  - **Use**: [When to reference]

## DOCUMENTATION:

### Official Documentation:
[From documentation-links.md with specific URLs]

- **Technology 1**: https://...
  - **Relevant Sections**: [Specific sections]
  - **Why**: [Importance to feature]
  - **Critical Gotchas**: [From gotchas.md]

- **Technology 2**: https://...
  - **API Reference**: [Specific methods]
  - **Code Examples**: [Links to working examples]

### Archon Knowledge Base:
[If used during research]
- **Source**: [source_id from documentation-links]
- **Relevance**: [Why this source is valuable]

## OTHER CONSIDERATIONS:

### Architecture & Patterns:
[From codebase-patterns.md]
- Follow {framework} pattern for {component}
- Use {pattern_name} from src/{example_file}
- Test structure mirrors implementation

### Security Considerations:
[From gotchas.md - security section]
- [ ] Validate all external inputs
- [ ] Use environment variables for secrets
- [ ] Implement rate limiting for API calls
- [ ] [Specific security requirements]

### Performance Considerations:
[From gotchas.md - performance section]
- Use async/await for I/O operations
- Implement caching for {specific_data}
- [Specific performance requirements]

### Known Gotchas:
[From gotchas.md - top 3-5 most critical]
- **Gotcha 1**: [Issue]
  - **Solution**: [How to handle]
  - **Source**: [Where this is documented]

### Rate Limits & Quotas:
[From gotchas.md if APIs involved]
- **API**: [Limits and handling strategy]

### Environment Setup:
- Create .env.example with required variables
- Virtual environment: {tool} (if needed)
- Dependencies: See {codebase}/requirements.txt pattern

### Project Structure:
[From codebase-patterns.md - recommended structure]
```
{feature_name}/
├── {files_to_create}
```

### Validation Commands:
[From codebase-patterns.md - testing patterns]
```bash
# Syntax/Style
ruff check src/{feature}/ --fix

# Type checking
mypy src/{feature}/

# Unit tests
pytest tests/test_{feature}.py -v

# Integration tests
[specific commands]
```

---

## Quality Score Self-Assessment

- [ ] Feature description comprehensive (not vague)
- [ ] All examples extracted (not just referenced)
- [ ] Examples have "what to mimic" guidance
- [ ] Documentation includes working examples
- [ ] Gotchas documented with solutions
- [ ] Follows INITIAL_EXAMPLE.md structure
- [ ] Ready for immediate PRP generation
- [ ] Score: {X}/10

---
Generated: {date}
Research Documents Used: 5
Examples Directory: examples/{feature_name}/ ({count} files)
Archon Project: {project_id}
```

**Validation**:
- [ ] Follows INITIAL_EXAMPLE.md structure
- [ ] References examples/ directory
- [ ] Includes URLs from documentation research
- [ ] Integrates gotchas with solutions
- [ ] Quality score: 8+/10

---

### Task 7: Create Main Orchestrator Command

**Location**: `.claude/commands/create-initial.md`

**Purpose**: Coordinate all 6 subagents through 5-phase workflow with Archon integration

**Command Content**:
```markdown
# Create INITIAL.md Command

## Trigger Patterns

When user says ANY of these, activate this workflow:
- "Help me create INITIAL.md for [feature]"
- "I need to build INITIAL.md for [feature]"
- "Create INITIAL.md for [feature]"
- "Generate INITIAL requirements for [feature]"
- "Write INITIAL.md for [feature]"
- "I want to make an INITIAL.md for [feature]"

## The 5-Phase Workflow

### Phase 0: Recognition & Basic Clarification (YOU handle this)

**Immediate Actions**:
1. ✅ **STOP** any other work
2. ✅ **ACKNOWLEDGE**: "I'll help create a comprehensive INITIAL.md using the factory workflow"
3. ✅ **ASK** 2-3 clarifying questions:
   - Primary use case: What problem does this solve?
   - Technical preferences: Specific technologies or should I recommend?
   - Integration needs: Any existing systems to integrate with?
4. ✅ **WAIT** for user response (DO NOT PROCEED until user answers)

**After User Responds**:
1. Determine feature name (snake_case: e.g., web_scraper, auth_system)
2. Create directories:
   ```bash
   mkdir -p prps/research
   mkdir -p examples/{feature_name}
   ```
3. Check Archon availability:
   ```python
   health = mcp__archon__health_check()
   archon_available = health["status"] == "healthy"
   ```

4. If Archon available, create project and tasks:
   ```python
   # Create project
   project = mcp__archon__manage_project("create",
       title=f"INITIAL.md: {feature_display_name}",
       description=f"Creating comprehensive INITIAL.md for {feature_description}"
   )
   project_id = project["project"]["id"]

   # Create 6 tasks
   tasks = [
       {"title": "Phase 1: Requirements Analysis", "assignee": "prp-initial-feature-clarifier"},
       {"title": "Phase 2A: Codebase Research", "assignee": "prp-initial-codebase-researcher"},
       {"title": "Phase 2B: Documentation Hunt", "assignee": "prp-initial-documentation-hunter"},
       {"title": "Phase 2C: Example Curation", "assignee": "prp-initial-example-curator"},
       {"title": "Phase 3: Gotcha Analysis", "assignee": "prp-initial-gotcha-detective"},
       {"title": "Phase 4: Assembly", "assignee": "prp-initial-assembler"}
   ]

   task_ids = []
   for task_def in tasks:
       task = mcp__archon__manage_task("create",
           project_id=project_id,
           title=task_def["title"],
           description=f"{task_def['assignee']} - Autonomous execution",
           status="todo",
           assignee=task_def["assignee"]
       )
       task_ids.append(task["task"]["id"])
   ```

5. Proceed to Phase 1

---

### Phase 1: Deep Feature Analysis

**Subagent**: `prp-initial-feature-clarifier`

**Your Actions**:
```python
# Update Archon task
if archon_available:
    mcp__archon__manage_task("update", task_id=task_ids[0], status="doing")

# Invoke clarifier with context
invoke_subagent("prp-initial-feature-clarifier", {
    "user_request": original_user_request,
    "clarifications": user_responses_from_phase_0,
    "feature_name": feature_name,
    "archon_project_id": project_id if archon_available else None
})

# Wait for completion
# Expected output: prps/research/feature-analysis.md

# Mark complete
if archon_available:
    mcp__archon__manage_task("update", task_id=task_ids[0], status="done")
```

---

### Phase 2: Parallel Research (CRITICAL: Use Parallel Invocation)

**CRITICAL**: Invoke ALL THREE agents in a SINGLE message with multiple Task tool calls

**Your Actions**:
```python
# Update Archon tasks to "doing"
if archon_available:
    for i in [1, 2, 3]:  # Tasks 2A, 2B, 2C
        mcp__archon__manage_task("update", task_id=task_ids[i], status="doing")

# ⚠️ CRITICAL: Parallel invocation - single message, multiple Task calls
# Call all three agents at once
parallel_invoke([
    Task(agent="prp-initial-codebase-researcher", context={
        "feature_analysis": "prps/research/feature-analysis.md",
        "feature_name": feature_name,
        "archon_project_id": project_id if archon_available else None
    }),
    Task(agent="prp-initial-documentation-hunter", context={
        "feature_analysis": "prps/research/feature-analysis.md",
        "feature_name": feature_name,
        "archon_project_id": project_id if archon_available else None
    }),
    Task(agent="prp-initial-example-curator", context={
        "feature_analysis": "prps/research/feature-analysis.md",
        "feature_name": feature_name,
        "examples_dir": f"examples/{feature_name}/",
        "archon_project_id": project_id if archon_available else None
    })
])

# Expected outputs:
# - prps/research/codebase-patterns.md
# - prps/research/documentation-links.md
# - prps/research/examples-to-include.md
# - examples/{feature_name}/ directory with code files

# Mark all three complete
if archon_available:
    for i in [1, 2, 3]:
        mcp__archon__manage_task("update", task_id=task_ids[i], status="done")
```

---

### Phase 3: Gotcha Analysis

**Subagent**: `prp-initial-gotcha-detective`

**Your Actions**:
```python
# Update Archon task
if archon_available:
    mcp__archon__manage_task("update", task_id=task_ids[4], status="doing")

# Invoke detective
invoke_subagent("prp-initial-gotcha-detective", {
    "feature_analysis": "prps/research/feature-analysis.md",
    "codebase_patterns": "prps/research/codebase-patterns.md",
    "documentation": "prps/research/documentation-links.md",
    "archon_project_id": project_id if archon_available else None
})

# Expected output: prps/research/gotchas.md

# Mark complete
if archon_available:
    mcp__archon__manage_task("update", task_id=task_ids[4], status="done")
```

---

### Phase 4: Final Assembly

**Subagent**: `prp-initial-assembler`

**Your Actions**:
```python
# Update Archon task
if archon_available:
    mcp__archon__manage_task("update", task_id=task_ids[5], status="doing")

# Invoke assembler
invoke_subagent("prp-initial-assembler", {
    "feature_name": feature_name,
    "research_dir": "prps/research/",
    "examples_dir": f"examples/{feature_name}/",
    "archon_project_id": project_id if archon_available else None
})

# Expected output: prps/INITIAL_{feature_name}.md

# Mark complete
if archon_available:
    mcp__archon__manage_task("update", task_id=task_ids[5], status="done")
```

---

### Phase 5: Delivery & Next Steps (YOU handle this)

**Your Actions**:
```markdown
✅ **INITIAL.md Created Successfully!**

**Generated Files**:
- 📄 `prps/INITIAL_{feature_name}.md` - Comprehensive requirements document
- 📁 `examples/{feature_name}/` - Extracted code examples ({count} files)
- 📋 `prps/research/` - Supporting research (5 documents)

**Quality Check**:
- Feature description: ✅ Comprehensive
- Examples: ✅ {count} relevant examples extracted
- Documentation: ✅ {count} official sources referenced
- Gotchas: ✅ {count} important considerations documented
- PRP-Ready Score: {X}/10

**Next Steps**:

1. **Review the INITIAL.md** (recommended):
   ```bash
   cat prps/INITIAL_{feature_name}.md
   ```

2. **Review extracted examples** (optional but helpful):
   ```bash
   cat examples/{feature_name}/README.md
   ```

3. **Generate the PRP** (when ready):
   ```bash
   /generate-prp prps/INITIAL_{feature_name}.md
   ```

4. **Execute the feature** (after PRP generation):
   ```bash
   /execute-prp PRPs/{feature_name}.md
   ```

Would you like me to review any specific section, or shall we proceed to PRP generation?
```

**Update Archon** (if available):
```python
# Add final notes to project
mcp__archon__manage_project("update",
    project_id=project_id,
    description=f"COMPLETED: Generated INITIAL.md with {example_count} examples"
)

# Store INITIAL.md as document
initial_content = Read(f"prps/INITIAL_{feature_name}.md")
mcp__archon__manage_document("create",
    project_id=project_id,
    title=f"INITIAL: {feature_name}",
    content=initial_content,
    document_type="spec",
    tags=["initial", "requirements", feature_name]
)
```

---

## Error Handling

### If Subagent Fails:
```python
try:
    invoke_subagent("agent-name", context)
except SubagentError as e:
    # Log error
    logger.error(f"Phase X failed: {e}")

    # Update Archon if available
    if archon_available:
        mcp__archon__manage_task("update", task_id=task_id,
            description=f"ERROR: {e}")

    # Continue with partial results
    # Document missing section in final INITIAL.md
    # Offer user option to regenerate specific phase
```

### If Archon Unavailable:
```python
# Proceed without tracking
# Skip all manage_project, manage_task, manage_document calls
# Workflow continues normally
```

---

## Quality Gates

Before delivering INITIAL.md, verify:
- [ ] Feature description comprehensive
- [ ] Examples extracted (not just referenced)
- [ ] Examples have "what to mimic" guidance
- [ ] Documentation includes working examples
- [ ] Gotchas documented with solutions
- [ ] INITIAL.md follows INITIAL_EXAMPLE.md structure
- [ ] Ready for immediate PRP generation
- [ ] Quality score: 8+/10

If any fail:
1. Regenerate failing phase
2. Document gap in INITIAL.md
3. Offer user option to iterate

---
```

**Validation**:
- [ ] Command file created
- [ ] All 5 phases documented
- [ ] Archon integration included
- [ ] Parallel execution in Phase 2
- [ ] Error handling implemented

---

### Task 8: Update CLAUDE.md with Workflow Documentation

**Location**: `/Users/jon/source/vibes/CLAUDE.md`

**Insert After**: "## Common Development Workflows" section
**Before**: "## Development Patterns" section

**Content to Add**:
```markdown
---

# 📋 INITIAL.md Factory Workflow

## Overview

Multi-subagent system for creating comprehensive INITIAL.md files that feed into the PRP generation process.
This workflow automates requirements gathering through systematic research, reducing creation time from 30+ minutes to <10 minutes.

**Key Innovation**: 6 specialized subagents with separate context windows running in parallel conduct comprehensive
research without context pollution, then synthesize into a single production-ready INITIAL.md.

## When to Use This Workflow

✅ **Trigger this workflow when user says ANY of these**:
- "Help me create INITIAL.md for [feature]"
- "I need to build INITIAL.md for [feature]"
- "Create INITIAL.md for [feature]"
- "Generate INITIAL requirements for [feature]"
- "Write INITIAL.md for [feature]"
- "I want to make an INITIAL.md for [feature]"

❌ **Don't use this workflow for**:
- Executing/implementing existing INITIAL.md (use `/execute-prp` instead)
- Generating PRP from existing INITIAL.md (use `/generate-prp` instead)

## Immediate Recognition Actions

When you detect an INITIAL.md creation request:

1. ✅ **STOP** any other work immediately
2. ✅ **ACKNOWLEDGE**: "I'll help create a comprehensive INITIAL.md using the factory workflow"
3. ✅ **PROCEED** to Phase 0 (don't ask for permission)
4. ✅ **NEVER** skip Phase 0 clarifications
5. ✅ **NEVER** try to write INITIAL.md directly

## The 5-Phase Workflow

### Phase 0: Recognition & Basic Clarification

**Who handles this**: YOU (main Claude Code)
**Time**: 2-3 minutes (includes user response wait)

**Your Actions**:
1. Ask 2-3 clarifying questions:
   - Primary use case: What problem does this solve?
   - Technical preferences: Specific technologies or recommend?
   - Integration needs: Any existing systems to integrate?

2. ⚠️ **CRITICAL**: WAIT for user response - DO NOT PROCEED

3. After user responds:
   - Determine feature name (snake_case)
   - Create directories: `prps/research/`, `examples/{feature}/`
   - Check Archon: `health_check()`
   - Create Archon project and 6 tasks if available
   - Proceed to Phase 1

### Phase 1: Deep Feature Analysis

**Subagent**: `prp-initial-feature-clarifier`
**Time**: 2-3 minutes
**Mode**: AUTONOMOUS

**What it does**:
- Searches Archon for similar features
- Decomposes request into requirements
- Makes intelligent assumptions
- Documents assumptions clearly
- Creates `prps/research/feature-analysis.md`

**Your Actions**:
```python
# Update Archon
if archon_available:
    manage_task("update", task_id=task_ids[0], status="doing")

# Invoke
invoke_subagent("prp-initial-feature-clarifier", context)

# Mark complete
manage_task("update", task_id=task_ids[0], status="done")
```

### Phase 2: Parallel Research (CRITICAL PHASE)

**Subagents**: THREE simultaneously
- `prp-initial-codebase-researcher`
- `prp-initial-documentation-hunter`
- `prp-initial-example-curator`

**Time**: 3-5 minutes (all run in parallel)

⚠️ **CRITICAL**: Invoke all three in SINGLE message using parallel tool invocation

**What each does**:
- **Codebase**: Searches Archon + local code for patterns
- **Documentation**: Checks Archon, then WebSearch for official docs
- **Examples**: EXTRACTS code to `examples/{feature}/` directory

**Your Actions**:
```python
# Update tasks
for i in [1,2,3]:
    manage_task("update", task_id=task_ids[i], status="doing")

# Parallel invocation - SINGLE message, multiple Task calls
parallel_invoke([
    Task("prp-initial-codebase-researcher", {...}),
    Task("prp-initial-documentation-hunter", {...}),
    Task("prp-initial-example-curator", {...})
])

# Mark complete
for i in [1,2,3]:
    manage_task("update", task_id=task_ids[i], status="done")
```

**Expected Outputs**:
- `prps/research/codebase-patterns.md`
- `prps/research/documentation-links.md`
- `prps/research/examples-to-include.md`
- `examples/{feature}/` directory with code files + README

### Phase 3: Gotcha Analysis

**Subagent**: `prp-initial-gotcha-detective`
**Time**: 2 minutes

**What it does**:
- Searches Archon for known issues
- Researches pitfalls via web
- Identifies security concerns
- Documents performance issues
- Creates `prps/research/gotchas.md` with SOLUTIONS

### Phase 4: Final Assembly

**Subagent**: `prp-initial-assembler`
**Time**: 1-2 minutes

**What it does**:
- Reads ALL 5 research documents
- Synthesizes into INITIAL.md structure
- Follows INITIAL_EXAMPLE.md format
- Ensures 8+/10 quality
- Creates `prps/INITIAL_{feature}.md`

### Phase 5: Delivery & Next Steps

**Who handles this**: YOU
**Time**: 1 minute

**Your Actions**:
1. Present summary to user
2. Show file locations
3. Quality check summary
4. Provide next steps (/generate-prp, /execute-prp)
5. Update Archon with completion notes
6. Store INITIAL.md as Archon document

## Subagent Reference

All subagents in `.claude/agents/`:

| Agent | Purpose | Output |
|-------|---------|--------|
| prp-initial-feature-clarifier | Requirements analysis | feature-analysis.md |
| prp-initial-codebase-researcher | Pattern extraction | codebase-patterns.md |
| prp-initial-documentation-hunter | Doc research | documentation-links.md |
| prp-initial-example-curator | Code extraction | examples-to-include.md + examples/ |
| prp-initial-gotcha-detective | Pitfall identification | gotchas.md |
| prp-initial-assembler | Final synthesis | INITIAL_{feature}.md |

## Archon Integration

### Always Check Health First
```python
health = health_check()
archon_available = health["status"] == "healthy"
```

### If Archon Available
- Create project for tracking
- Create 6 tasks (one per phase)
- Update task status: "todo" → "doing" → "done"
- Store final INITIAL.md as document
- Pass project_id to all subagents

### If Unavailable
- Proceed without tracking
- Workflow continues normally

## Key Principles

1. **Autonomous After Phase 0**: Subagents work without user input
2. **Parallel Execution**: Phase 2 runs three agents simultaneously
3. **Archon-First**: Always search Archon before external sources
4. **Example Extraction**: Extract actual code, not just references
5. **Quality Over Speed**: Target 8+/10, take extra time if needed

## Error Handling

If subagent fails:
1. Log error with context
2. Continue with partial results
3. Document what's missing
4. Offer regeneration option

## Quality Gates

Before delivery, verify:
- [ ] Feature description comprehensive
- [ ] Examples extracted with guidance
- [ ] Documentation includes working examples
- [ ] Gotchas documented with solutions
- [ ] Follows INITIAL_EXAMPLE.md structure
- [ ] Quality score: 8+/10

## Success Metrics

- ✅ Total time: <10 minutes
- ✅ Quality: 8+/10
- ✅ Examples: 2-4 extracted
- ✅ Documentation: 3-5 sources
- ✅ Gotchas: 2-5 documented
- ✅ PRP generation works first attempt

---
```

**Insertion Point**:
Find line with "## Common Development Workflows" and insert AFTER the existing workflows,
BEFORE "## Development Patterns" section.

**Validation**:
```bash
# Check section added
grep -A 10 "INITIAL.md Factory Workflow" CLAUDE.md

# Check trigger patterns
grep "Help me create INITIAL.md" CLAUDE.md

# Check phase documentation
grep "Phase [0-5]:" CLAUDE.md
```

---

### Task 9: End-to-End Testing

**Test Feature**: "web scraper with rate limiting"

**Test Script**:
```bash
# 1. Verify all agents exist
ls -la .claude/agents/prp-initial-*.md
# Expected: 6 files

# 2. Verify orchestrator exists
cat .claude/commands/create-initial.md
# Expected: Complete workflow documentation

# 3. Start Claude Code session
# In Claude Code, say: "Help me create INITIAL.md for web scraper with rate limiting"

# 4. Verify Phase 0 questions asked
# Expected: 2-3 clarifying questions
# Expected: Waits for user response

# 5. After responding, verify directories created
ls -la prps/research/
ls -la examples/web_scraper/

# 6. Verify research files created
ls prps/research/
# Expected:
# - feature-analysis.md
# - codebase-patterns.md
# - documentation-links.md
# - examples-to-include.md
# - gotchas.md

# 7. Verify examples extracted
ls examples/web_scraper/
# Expected:
# - README.md
# - 2-4 code files (.py)

# 8. Verify INITIAL.md created
cat prps/INITIAL_web_scraper.md
# Check structure matches INITIAL_EXAMPLE.md

# 9. Quality check
# - Feature description comprehensive? ✅
# - Examples have "what to mimic"? ✅
# - Documentation URLs included? ✅
# - Gotchas have solutions? ✅
# - Follows INITIAL_EXAMPLE format? ✅
# - Ready for /generate-prp? ✅

# 10. Measure time
# Should complete in <10 minutes

# 11. Test PRP generation
# /generate-prp prps/INITIAL_web_scraper.md
# Should succeed without clarifications
```

**Expected Results**:
- ✅ All files created
- ✅ Parallel Phase 2 execution
- ✅ Examples extracted (not just referenced)
- ✅ INITIAL.md follows correct format
- ✅ Quality score: 8+/10
- ✅ Total time: <10 minutes

**Validation**:
```bash
# Count files
find .claude/agents -name "prp-initial-*.md" | wc -l  # Should be 6
find prps/research -name "*.md" | wc -l               # Should be 5
find examples/web_scraper -name "*.py" | wc -l        # Should be 2-4

# Check YAML frontmatter
for f in .claude/agents/prp-initial-*.md; do
    echo "Checking $f"
    head -10 "$f" | grep -E "^name:|^description:|^tools:|^color:"
done

# Verify INITIAL.md structure
grep -E "^## FEATURE:|^## EXAMPLES:|^## DOCUMENTATION:|^## OTHER CONSIDERATIONS:" \
    prps/INITIAL_web_scraper.md
```

---

### Task 10: Documentation & README

**Create**: `prps/workflows/INITIAL_FACTORY_README.md`

**Content**:
```markdown
# INITIAL.md Factory Workflow

## Overview

Multi-subagent system for creating comprehensive INITIAL.md files through systematic research.

**Purpose**: Transform user feature requests into PRP-ready INITIAL.md files in <10 minutes

**Components**:
- 6 specialized subagents (.claude/agents/)
- 1 orchestrator command (.claude/commands/create-initial.md)
- Archon MCP integration for knowledge augmentation

## Quick Start

### User Invocation

Say to Claude Code:
```
Help me create INITIAL.md for [your feature]
```

### What Happens

1. **Phase 0**: Claude asks 2-3 clarifying questions
2. **Phase 1**: Requirements analysis (autonomous)
3. **Phase 2**: Parallel research - 3 agents simultaneously
4. **Phase 3**: Gotcha detection (autonomous)
5. **Phase 4**: Final synthesis (autonomous)
6. **Delivery**: Complete INITIAL.md + examples

**Total Time**: <10 minutes
**Quality**: 8+/10 PRP-ready

## Output Structure

```
prps/
├── INITIAL_{feature}.md           # Final output
└── research/                       # Intermediate research
    ├── feature-analysis.md
    ├── codebase-patterns.md
    ├── documentation-links.md
    ├── examples-to-include.md
    └── gotchas.md

examples/{feature}/
├── README.md                       # Usage guidance
└── *.py                            # Extracted code (2-4 files)
```

## Next Steps After Generation

1. **Review**: `cat prps/INITIAL_{feature}.md`
2. **Generate PRP**: `/generate-prp prps/INITIAL_{feature}.md`
3. **Execute**: `/execute-prp PRPs/{feature}.md`

## Subagent Roles

- **feature-clarifier**: Deep requirements analysis
- **codebase-researcher**: Pattern extraction from code
- **documentation-hunter**: Official docs research
- **example-curator**: Code extraction & organization
- **gotcha-detective**: Security & pitfall identification
- **assembler**: Final INITIAL.md synthesis

## Key Features

✅ **Archon-First**: Uses knowledge base before external searches
✅ **Parallel Execution**: Phase 2 runs 3 agents simultaneously
✅ **Example Extraction**: Creates actual code files, not just references
✅ **Quality Gates**: Ensures 8+/10 PRP-readiness
✅ **Autonomous**: No user interaction after initial questions

## Archon Integration

If Archon MCP is available:
- Creates project for tracking
- Creates 6 tasks (one per phase)
- Updates task status as workflow progresses
- Stores final INITIAL.md as document
- Uses RAG for knowledge-augmented research

If unavailable: Workflow proceeds without tracking

## Troubleshooting

### "No examples found"
**Cause**: Feature is novel, no similar patterns exist
**Solution**: Curator explains this, suggests manual collection

### "Research incomplete"
**Cause**: Subagent failed mid-execution
**Solution**: Check error logs, regenerate specific phase

### "INITIAL.md too vague"
**Cause**: Phase 0 clarifications insufficient
**Solution**: Ask follow-up questions, re-run Phase 1

### "Examples don't match"
**Cause**: Curator misunderstood requirements
**Solution**: Review feature-analysis.md, re-run curator

## Manual Phase Regeneration

Regenerate specific phase:
```
Regenerate codebase research for [feature]
Update documentation links for [feature]
Add more examples for [feature]
```

## Quality Checklist

Before accepting INITIAL.md:
- [ ] Feature description comprehensive
- [ ] Examples extracted to examples/{feature}/
- [ ] Examples have "what to mimic" guidance
- [ ] Documentation includes working examples
- [ ] Gotchas documented with solutions
- [ ] INITIAL.md follows INITIAL_EXAMPLE.md structure
- [ ] Ready for immediate /generate-prp
- [ ] Quality score: 8+/10

## Files Reference

**Subagents**: `.claude/agents/prp-initial-*.md` (6 files)
**Orchestrator**: `.claude/commands/create-initial.md`
**Workflow Docs**: `CLAUDE.md` (INITIAL.md Factory Workflow section)
**Example Target**: `repos/context-engineering-intro/INITIAL_EXAMPLE.md`
**Template**: `prps/templates/prp_base.md`

---

Created: {date}
Version: 1.0
Maintainer: Vibes Project
```

**Validation**: README covers all key aspects and provides troubleshooting

---

## Validation Loop

### Level 1: File Existence & YAML Validity

```bash
# Check all subagents exist
test -f .claude/agents/prp-initial-feature-clarifier.md && echo "✅ clarifier"
test -f .claude/agents/prp-initial-codebase-researcher.md && echo "✅ researcher"
test -f .claude/agents/prp-initial-documentation-hunter.md && echo "✅ hunter"
test -f .claude/agents/prp-initial-example-curator.md && echo "✅ curator"
test -f .claude/agents/prp-initial-gotcha-detective.md && echo "✅ detective"
test -f .claude/agents/prp-initial-assembler.md && echo "✅ assembler"

# Check orchestrator
test -f .claude/commands/create-initial.md && echo "✅ orchestrator"

# Verify YAML frontmatter for each agent
for f in .claude/agents/prp-initial-*.md; do
    echo "Validating YAML in $f"
    head -10 "$f" | grep -q "^name:" || echo "❌ Missing name field"
    head -10 "$f" | grep -q "^description:" || echo "❌ Missing description field"
    head -10 "$f" | grep -q "^tools:" || echo "❌ Missing tools field"
    head -10 "$f" | grep -q "^color:" || echo "❌ Missing color field"
    head -10 "$f" | grep -q "^---$" || echo "❌ Missing frontmatter close"
done

# Expected: All ✅, no ❌
```

### Level 2: Orchestrator Workflow Validation

```bash
# Check Phase 0 documented
grep -q "Phase 0: Recognition" .claude/commands/create-initial.md && echo "✅ Phase 0"

# Check Phase 2 parallel invocation
grep -q "parallel_invoke" .claude/commands/create-initial.md && echo "✅ Parallel"
grep -q "SINGLE message" .claude/commands/create-initial.md && echo "✅ Single message"

# Check Archon integration
grep -q "health_check" .claude/commands/create-initial.md && echo "✅ Health check"
grep -q "manage_project" .claude/commands/create-initial.md && echo "✅ Project creation"
grep -q "manage_task" .claude/commands/create-initial.md && echo "✅ Task management"

# Check error handling
grep -q "except.*Error" .claude/commands/create-initial.md && echo "✅ Error handling"

# Expected: All ✅
```

### Level 3: End-to-End Quality Test

**Test Feature**: web_scraper
**Command**: "Help me create INITIAL.md for web scraper with rate limiting"

**Quality Validation**:
```bash
# After workflow completes, check outputs

# 1. Research files created
test -f prps/research/feature-analysis.md && echo "✅ Analysis"
test -f prps/research/codebase-patterns.md && echo "✅ Patterns"
test -f prps/research/documentation-links.md && echo "✅ Docs"
test -f prps/research/examples-to-include.md && echo "✅ Examples list"
test -f prps/research/gotchas.md && echo "✅ Gotchas"

# 2. Examples directory created with code
test -d examples/web_scraper && echo "✅ Examples dir"
test -f examples/web_scraper/README.md && echo "✅ Examples README"
find examples/web_scraper -name "*.py" | wc -l  # Should be 2-4

# 3. INITIAL.md created with proper structure
test -f prps/INITIAL_web_scraper.md && echo "✅ INITIAL.md exists"
grep -q "## FEATURE:" prps/INITIAL_web_scraper.md && echo "✅ Feature section"
grep -q "## EXAMPLES:" prps/INITIAL_web_scraper.md && echo "✅ Examples section"
grep -q "## DOCUMENTATION:" prps/INITIAL_web_scraper.md && echo "✅ Docs section"
grep -q "## OTHER CONSIDERATIONS:" prps/INITIAL_web_scraper.md && echo "✅ Considerations"

# 4. Examples referenced correctly
grep -q "examples/web_scraper/" prps/INITIAL_web_scraper.md && echo "✅ Examples ref"

# 5. Documentation URLs included
grep -qE "https?://" prps/INITIAL_web_scraper.md && echo "✅ URLs included"

# 6. Gotchas have solutions
grep -A 5 "Gotcha\|Pitfall\|Security" prps/INITIAL_web_scraper.md | \
    grep -q "Solution" && echo "✅ Solutions provided"

# 7. Time measurement
# Should complete in <10 minutes (manual check)

# 8. Quality score check
grep -q "Score:" prps/INITIAL_web_scraper.md && echo "✅ Self-scored"
```

**Manual Quality Review**:
- [ ] Feature description is comprehensive and specific
- [ ] Examples directory has 2-4 extracted code files
- [ ] Each example in README has "what to mimic" guidance
- [ ] Documentation includes specific URLs with sections
- [ ] Gotchas include solutions, not just warnings
- [ ] INITIAL.md ready for immediate /generate-prp
- [ ] Quality score: 8+/10

**If any checks fail**:
1. Review specific subagent output
2. Check error logs
3. Regenerate failed phase
4. Update agent instructions if needed

---

## Final Validation Checklist

Before considering implementation complete:

### Infrastructure
- [ ] `.claude/agents/` directory contains 6 prp-initial-*.md files
- [ ] `.claude/commands/create-initial.md` exists
- [ ] All YAML frontmatter valid (name, description, tools, color)
- [ ] `prps/research/` directory created
- [ ] `examples/` directory exists

### Agent Implementation
- [ ] feature-clarifier: Makes assumptions, searches Archon, creates feature-analysis.md
- [ ] codebase-researcher: Searches Archon + Grep, creates codebase-patterns.md
- [ ] documentation-hunter: Archon-first, then WebSearch, creates documentation-links.md
- [ ] example-curator: EXTRACTS code, creates examples/{feature}/ + README.md
- [ ] gotcha-detective: Searches issues, creates gotchas.md with solutions
- [ ] assembler: Synthesizes all 5 docs, follows INITIAL_EXAMPLE format

### Orchestrator
- [ ] Phase 0: Asks clarifying questions, WAITS for user
- [ ] Phase 1: Invokes feature-clarifier
- [ ] Phase 2: Parallel invocation (single message, 3 Task calls)
- [ ] Phase 3: Invokes gotcha-detective
- [ ] Phase 4: Invokes assembler
- [ ] Phase 5: Delivers results with next steps
- [ ] Archon integration: health check, project/task creation, status updates
- [ ] Error handling implemented
- [ ] Graceful degradation if Archon unavailable

### Documentation
- [ ] CLAUDE.md updated with comprehensive workflow section
- [ ] Trigger patterns documented
- [ ] 5-phase workflow explained
- [ ] Archon integration guide included
- [ ] Quality gates documented
- [ ] Troubleshooting section added

### Quality
- [ ] Example curator extracts actual code files
- [ ] examples/{feature}/ has README with detailed guidance
- [ ] INITIAL.md follows INITIAL_EXAMPLE structure
- [ ] All research documents properly formatted
- [ ] Complete workflow runs in <10 minutes
- [ ] Generated INITIAL.md scores 8+/10
- [ ] Ready for immediate /generate-prp

### Testing
- [ ] End-to-end test completed
- [ ] All files created in correct locations
- [ ] Parallel execution verified
- [ ] Examples extraction verified
- [ ] Quality score: 8+/10

---

## Anti-Patterns to Avoid

### ❌ Sequential Execution in Phase 2
```python
# WRONG - Sequential execution (slow, defeats purpose)
invoke_subagent("prp-initial-codebase-researcher", {...})
# wait for completion
invoke_subagent("prp-initial-documentation-hunter", {...})
# wait for completion
invoke_subagent("prp-initial-example-curator", {...})
```

### ✅ Correct: Parallel Execution
```python
# RIGHT - Parallel execution (fast, uses separate contexts)
parallel_invoke([
    Task("prp-initial-codebase-researcher", {...}),
    Task("prp-initial-documentation-hunter", {...}),
    Task("prp-initial-example-curator", {...})
])
```

### ❌ Example References Only
```markdown
# WRONG - Just referencing files
See src/api/auth.py for authentication pattern
See tests/test_api.py for testing approach
```

### ✅ Correct: Example Extraction
```python
# RIGHT - Extract actual code
Read(source_file)
extract_relevant_lines()
Write(f"examples/{feature}/pattern.py", extracted_code)
# Plus README with "what to mimic" guidance
```

### ❌ Skipping Phase 0 Clarifications
```python
# WRONG - Immediately invoking subagents
invoke_subagent("prp-initial-feature-clarifier", {...})
```

### ✅ Correct: Phase 0 First
```python
# RIGHT - Ask questions, WAIT for user
ask_clarifying_questions()
# WAIT for user response
# Then proceed to Phase 1
```

### ❌ Generic Archon Queries
```python
# WRONG - Too long, unfocused
rag_search_knowledge_base(
    query="how to implement vector search with pgvector in PostgreSQL..."
)
```

### ✅ Correct: Concise Queries
```python
# RIGHT - 2-5 keywords
rag_search_knowledge_base(query="vector search pgvector")
```

### ❌ Hardcoded Feature Names
```python
# WRONG - Hardcoded
Write("examples/my_feature/pattern.py", code)
```

### ✅ Correct: Use Passed Feature Name
```python
# RIGHT - Use exact feature name from orchestrator
feature_name = context["feature_name"]  # From orchestrator
Write(f"examples/{feature_name}/pattern.py", code)
```

### ❌ Missing Archon Health Check
```python
# WRONG - Assume Archon available
project = manage_project("create", ...)  # May fail
```

### ✅ Correct: Health Check First
```python
# RIGHT - Check availability
health = health_check()
if health["status"] == "healthy":
    project = manage_project("create", ...)
```

### ❌ Assembler Creating New Content
```markdown
# WRONG - Assembler inventing new information
Based on my analysis, you should use FastAPI...
```

### ✅ Correct: Assembler Synthesizing Research
```markdown
# RIGHT - Synthesizing from research docs
[From feature-analysis.md: Use FastAPI for async support]
[From documentation-links.md: Official FastAPI docs at...]
[From codebase-patterns.md: Follow src/api/example.py pattern]
```

---

## Success Metrics

### Time Performance
- **Target**: <10 minutes total
- **Measured**: From Phase 0 start to INITIAL.md delivery
- **Acceptable**: 12 minutes if comprehensive research needed

### Quality Metrics
- **Target**: 8+/10 PRP-readiness
- **Factors**:
  - Feature description comprehensive
  - Examples extracted with guidance
  - Documentation actionable
  - Gotchas have solutions
  - Structure follows INITIAL_EXAMPLE

### Example Extraction
- **Target**: 2-4 relevant code files
- **Quality**: Each has "what to mimic" notes
- **Coverage**: Different aspects (API, validation, testing)

### Documentation Coverage
- **Target**: 3-5 authoritative sources
- **Quality**: Specific URLs with section anchors
- **Relevance**: Implementation-critical sections

### Gotcha Detection
- **Target**: 2-5 important considerations
- **Quality**: Include solutions, not just warnings
- **Coverage**: Security, performance, common pitfalls

### User Satisfaction
- **Target**: User proceeds to /generate-prp without asking questions
- **Quality**: PRP generation succeeds first attempt
- **Confidence**: User feels ready for implementation

---

## PRP Quality Self-Assessment

**Confidence Level**: 9/10

**Reasoning**:
- ✅ **Comprehensive Context**: All reference files, patterns, and documentation included
- ✅ **Clear Implementation Path**: 10 detailed tasks with specific outputs
- ✅ **Example-Driven**: Multiple reference implementations from codebase
- ✅ **Validation Gates**: 3 levels of validation with specific commands
- ✅ **Error Handling**: Documented gotchas and anti-patterns
- ✅ **Archon Integration**: Complete workflow with health checks and task tracking
- ✅ **Quality Gates**: Specific criteria for 8+/10 INITIAL.md

**Potential Gaps** (minor):
- Example curator implementation details could be more prescriptive
- CLAUDE.md placement exact line numbers not specified
- End-to-end test could include timing measurements

**Mitigation**: Implementation agent can reference existing subagent patterns
(pydantic-ai-planner, library-researcher) for additional guidance.

**Overall**: This PRP provides sufficient context and structure for one-pass implementation
with high probability of success. The 6 subagents + orchestrator pattern is proven in the
agent-factory reference, and this PRP adapts it appropriately for INITIAL.md generation.

---

**Score: 9/10** - Ready for immediate implementation with /execute-prp
