# Documentation Links: prp_workflow_improvements

## Technology Stack Identified

Based on feature-analysis.md:
- **Primary System**: Claude Code (Anthropic's AI coding assistant)
- **Architecture**: Multi-subagent orchestration system
- **Key Tools**: Task tool, Archon MCP server, Slash commands
- **Languages**: Markdown (configuration), Python (MCP servers)
- **Knowledge Management**: Archon RAG system with PGVector
- **Data Storage**: Supabase PostgreSQL

## Archon Knowledge Base Results

### Technology 1: Claude Code Subagents

**Archon Source**: 9a7d4217c64c9a0a
**Source Title**: Anthropic Documentation
**Relevance Score**: 10/10

**Key Sections Found in Archon**:

#### Section 1: Subagent Fundamentals
**Content Summary**: Core concepts of subagents as specialized AI assistants with separate context windows, custom tools, and system prompts.

**Relevant Excerpt**:
```
Custom subagents in Claude Code are specialized AI assistants that can be invoked to handle specific types of tasks. They enable more efficient problem-solving by providing task-specific configurations with customized system prompts, tools and a separate context window.

Each subagent:
- Has a specific purpose and expertise area
- Uses its own context window separate from the main conversation
- Can be configured with specific tools it's allowed to use
- Includes a custom system prompt that guides its behavior
```

**Why This Matters**: The INITIAL.md factory workflow uses 6 specialized subagents, each with isolated context to prevent pollution during parallel research tasks.

**Code Example** (Configuration Pattern):
```yaml
---
name: prp-initial-feature-clarifier
description: Analyzes feature requests and creates comprehensive requirements analysis
tools: Read, mcp__archon__rag_search_knowledge_base, mcp__archon__rag_get_available_sources
model: inherit
---
You are a requirements analysis specialist...
```

#### Section 2: Model Selection & Tool Configuration
**Content Summary**: Configuration options for specifying which model subagents use and which tools they can access.

**Relevant Excerpt**:
```yaml
Field | Required | Description
------|----------|-------------
name | Yes | Unique identifier using lowercase letters and hyphens
description | Yes | Natural language description of the subagent's purpose
tools | No | Comma-separated list of specific tools. If omitted, inherits all tools from main thread
model | No | Model to use (sonnet, opus, haiku, or 'inherit')
```

**Why This Matters**: Each INITIAL.md factory subagent needs specific tool access (e.g., documentation-hunter needs WebSearch/WebFetch, codebase-researcher needs Grep/Glob).

#### Section 3: SlashCommand Tool Integration
**Content Summary**: How slash commands can invoke subagents and pass metadata through frontmatter.

**Relevant Excerpt**:
```
SlashCommand tool only supports custom slash commands that:
- Are user-defined (built-in commands not supported)
- Have the 'description' frontmatter field populated
- Character budget limit: 15000 (configurable via SLASH_COMMAND_TOOL_CHAR_BUDGET)
```

**Why This Matters**: The generate-prp and execute-prp commands need proper frontmatter to work with Claude's automatic tool discovery.

### Technology 2: Context Engineering & PRP Methodology

**Archon Source**: b8565aff9938938b
**Source Title**: GitHub - coleam00/context-engineering-intro
**Relevance Score**: 10/10

**Key Sections Found in Archon**:

#### Section 1: PRP Framework Structure
**Content Summary**: The three-part PRP framework: PRD + Curated Codebase Intelligence + Agent Runbook.

**Relevant Excerpt**:
```
Context Engineering Template structure:
.claude/
├── commands/
│   ├── generate-prp.md  # Generates comprehensive PRPs
│   └── execute-prp.md   # Executes PRPs to implement features
PRPs/
├── templates/
│   └── prp_base.md    # Base template for PRPs
└── EXAMPLE_multi_agent_prp.md
examples/         # Your code examples (critical!)
CLAUDE.md         # Global rules for AI assistant
INITIAL.md        # Template for feature requests
```

**Why This Matters**: The INITIAL.md factory creates the foundation document that feeds into generate-prp, following this proven structure.

**Code Example**:
```markdown
# PRP Structure

## PRD (Product Requirements Document)
- Goal
- Why
- What
- Success Criteria

## Curated Codebase Intelligence
- Current tree
- Desired tree
- Existing patterns
- Documentation URLs
- Known gotchas

## Agent Runbook
- Implementation blueprint
- Pseudocode
- Task list
- Validation loops
```

#### Section 2: Validation Loops & Quality Gates
**Content Summary**: Progressive validation approach with three levels: syntax/style, unit tests, integration tests.

**Relevant Excerpt**:
```bash
## Validation Loop

### Level 1: Syntax & Style
ruff check --fix && mypy .

### Level 2: Unit Tests
pytest tests/ -v

### Level 3: Integration Tests
# Project-specific commands

## Final Validation Checklist
- [ ] All tests pass
- [ ] No linting errors
- [ ] No type errors
- [ ] Manual test successful
- [ ] Error cases handled gracefully
```

**Why This Matters**: The execute-prp command needs built-in validation loops to ensure generated code meets quality standards.

### Technology 3: Multi-Agent Workflows

**Archon Source**: 464a0ce4d22bf72f
**Source Title**: Microsoft Agents Framework
**Relevance Score**: 7/10

**Key Sections Found in Archon**:

#### Section 1: Workflow Orchestration Patterns
**Content Summary**: Graph-based workflows for orchestrating multiple agents in complex processes with state management.

**Relevant Excerpt**:
```
The framework provides capabilities for:
- Individual AI agents to process user inputs and execute tasks
- Graph-based workflows that orchestrate multiple agents for complex processes
- Robust state management
- Event handling
- Proper history tracking
```

**Why This Matters**: Phase 2 of INITIAL.md factory runs 3 subagents in parallel - needs proper coordination and state tracking.

### Technology 4: Model Context Protocol (MCP)

**Archon Source**: d60a71d62eb201d5
**Source Title**: Model Context Protocol - LLMs
**Relevance Score**: 8/10

**Key Sections Found in Archon**:

#### Section 1: MCP Server Architecture
**Content Summary**: MCP servers provide tools, resources, and prompts to AI assistants through standardized protocol.

**Relevant Excerpt**:
```
MCP consists of two layers:
- Data layer: JSON-RPC based protocol for client-server communication, including lifecycle management, and core primitives (tools, resources, prompts, notifications)
- Transport layer: Communication mechanisms (STDIO for local, HTTP for remote)

MCP servers can execute locally or remotely:
- Local: Filesystem server using STDIO transport
- Remote: Sentry MCP server using HTTP transport
```

**Why This Matters**: Archon MCP server provides RAG search and task management tools that INITIAL.md factory subagents use for research.

## Official Documentation URLs

### Technology 1: Claude Code

**Official Site**: https://docs.claude.com/en/docs/claude-code/
**Version**: Latest (2025)

#### Subagents Documentation
- **URL**: https://docs.claude.com/en/docs/claude-code/sub-agents
- **Relevance**: Critical - defines entire subagent architecture
- **Key Topics**:
  - Creating subagents (file-based and interactive)
  - Configuration frontmatter (name, description, tools, model)
  - Context preservation benefits
  - Delegation patterns
- **Code Examples**: Yes - complete subagent configuration examples
- **Production Ready**: Yes - official Anthropic documentation

**Relevant Configuration Pattern**:
```yaml
---
name: code-reviewer
description: Expert code review specialist
tools: Read, Grep, Glob, Bash
model: inherit
---
You are a senior code reviewer ensuring high standards of code quality and security.

Review checklist:
- Code readability
- No duplicated code
- Proper error handling
- Input validation
- Test coverage
```

#### Slash Commands Documentation
- **URL**: https://docs.claude.com/en/docs/claude-code/slash-commands
- **Relevance**: Critical - defines command structure for generate-prp/execute-prp
- **Key Topics**:
  - Command file structure and frontmatter
  - $ARGUMENTS support for parameters
  - Bash command integration with ! prefix
  - File references with @ prefix
  - SlashCommand tool integration
- **Code Examples**: Yes - complete command examples
- **Production Ready**: Yes

**Command Frontmatter Example**:
```yaml
---
description: Generate comprehensive PRP from INITIAL.md
argument-hint: <feature-name>
model: sonnet
allowed-tools: Read, Write, Grep, Glob, mcp__archon__rag_search_knowledge_base
---
```

#### Common Workflows Documentation
- **URL**: https://docs.claude.com/en/docs/claude-code/common-workflows
- **Relevance**: High - parallel execution patterns and best practices
- **Key Topics**:
  - Using specialized subagents
  - Plan Mode for safe analysis
  - Parallel sessions with Git worktrees
  - Custom slash commands creation
- **Code Examples**: Yes - workflow examples
- **Production Ready**: Yes

**Parallel Execution Pattern**:
```
"Explore the codebase using 4 tasks in parallel"
- Claude Code supports up to 10 parallel tasks concurrently
- Tasks queued intelligently when exceeding limit
- Each task has separate context window
```

### Technology 2: Context Engineering & PRP

**Official Site**: https://github.com/coleam00/context-engineering-intro
**Version**: Latest (2025)

#### PRP Template Repository
- **URL**: https://github.com/coleam00/context-engineering-intro
- **Relevance**: Critical - defines PRP methodology we're implementing
- **Key Topics**:
  - PRP structure (PRD + Codebase Intelligence + Runbook)
  - INITIAL.md → PRP generation workflow
  - Validation loop methodology
  - Examples directory best practices
- **Code Examples**: Yes - complete PRP examples
- **Production Ready**: Yes - 10.2k stars, battle-tested

**PRP Generation Flow**:
```bash
# 1. Create initial feature request
# Edit INITIAL.md with requirements

# 2. Generate comprehensive PRP
/generate-prp INITIAL.md

# 3. Execute the PRP
/execute-prp PRPs/your-feature.md
```

#### Context Engineering Guide
- **URL**: https://www.aifire.co/p/ai-coding-assistants-a-guide-to-context-engineering-prp
- **Relevance**: High - methodology and best practices
- **Key Topics**:
  - Context engineering principles
  - PRP framework components
  - Validation principles
  - Common failure traps
- **Code Examples**: Conceptual examples
- **Production Ready**: Yes - comprehensive guide

**Critical Validation Principles**:
```
1. Thoroughly review AI-generated plans
2. Check for:
   - Logical architecture
   - Security considerations
   - Comprehensive feature implementation
   - Potential over-engineering
3. Context isn't one-time - it's ongoing discipline
```

### Technology 3: Archon MCP Server

**Official Site**: https://github.com/coleam00/Archon
**Version**: Beta (2025)

#### Archon GitHub Repository
- **URL**: https://github.com/coleam00/Archon
- **Relevance**: Critical - the MCP server used for knowledge/task management
- **Key Topics**:
  - RAG knowledge base with vector search
  - Task and project management
  - MCP tool integration
  - Multi-model support (OpenAI, Ollama, Gemini)
- **Code Examples**: Yes - installation and usage
- **Production Ready**: Beta - expect some issues

**Archon Architecture**:
```
Frontend UI: React + Vite (Port 3737)
Server: FastAPI + SocketIO (Port 8181)
MCP Server: HTTP Wrapper (Port 8051)
Agents Service: PydanticAI (Port 8052)
Database: Supabase PostgreSQL + PGVector
```

#### Archon MCP Tools
- **URL**: https://mcpdb.org/mcps/archon
- **Relevance**: Critical - defines available MCP tools
- **Key Tools**:
  - `rag_search_knowledge_base(query, source_id?, match_count)`
  - `rag_get_available_sources()`
  - `manage_project(action, ...)`
  - `manage_task(action, ...)`
  - `find_tasks(query?, filter_by?, filter_value?)`
  - `find_projects(query?, project_id?)`
- **Code Examples**: Yes - tool signatures
- **Production Ready**: Beta

**RAG Search Pattern**:
```python
# 1. Get available sources
sources = rag_get_available_sources()

# 2. Search knowledge base (2-5 keywords!)
results = rag_search_knowledge_base(
    query="FastAPI async",  # SHORT!
    match_count=5
)

# 3. Filtered search by source
filtered = rag_search_knowledge_base(
    query="authentication",
    source_id="src_abc123",  # Use ID, not URL
    match_count=5
)
```

### Technology 4: Model Context Protocol (MCP)

**Official Site**: https://modelcontextprotocol.io
**Version**: Latest (2025)

#### MCP Core Documentation
- **URL**: https://modelcontextprotocol.io/llms-full.txt
- **Relevance**: Medium - understanding MCP architecture
- **Key Topics**:
  - MCP protocol layers (data + transport)
  - Tool definitions and invocation
  - Resource and prompt management
  - Client-server communication
- **Code Examples**: Yes - server implementations
- **Production Ready**: Yes

**MCP Server Pattern**:
```python
from mcp.server import Server
from mcp.types import Tool, TextContent

server = Server("my-server")

@server.list_tools()
async def list_tools() -> list[Tool]:
    return [Tool(name="my-tool", description="...")]

@server.call_tool()
async def call_tool(name: str, arguments: dict):
    return [TextContent(type="text", text="result")]
```

## Implementation Tutorials & Guides

### Tutorial 1: Multi-agent Parallel Coding with Claude Code
- **URL**: https://medium.com/@codecentrevibe/claude-code-multi-agent-parallel-coding-83271c4675fa
- **Source**: Medium (Code Centre)
- **Date**: 2025
- **Relevance**: 9/10 - directly covers parallel subagent execution
- **What It Covers**: Real-world patterns for orchestrating multiple subagents in parallel, queuing systems for >10 agents, context management strategies
- **Code Quality**: High - production examples
- **Key Takeaways**:
  - Explicitly define which steps delegate to subagents
  - Similar to multi-threaded programming - orchestration matters
  - Early subagent usage preserves main context
  - Batch processing when exceeding 10-agent limit
- **Notes**: Covers July 2025 implementations scaling beyond 10-agent limit

### Tutorial 2: Claude Code Subagent Deep Dive
- **URL**: https://cuong.io/blog/2025/06/24-claude-code-subagent-deep-dive
- **Source**: Code Centre Blog
- **Date**: June 2025
- **Relevance**: 9/10 - technical deep dive into subagent internals
- **What It Covers**: Subagent architecture, context window management, tool permission patterns, delegation strategies
- **Code Quality**: High
- **Key Takeaways**:
  - Each subagent's context is isolated
  - Tool restrictions improve security and focus
  - System prompts should be highly specific
  - Project-level vs user-level subagents
- **Notes**: Excellent for understanding context isolation

### Tutorial 3: Claude Code Slash Commands Best Practices
- **URL**: https://alexop.dev/tils/claude-code-slash-commands-boost-productivity/
- **Source**: alexop.dev
- **Date**: 2025
- **Relevance**: 8/10 - slash command patterns and automation
- **What It Covers**: Custom command creation, argument handling, bash integration, team distribution
- **Code Quality**: High - production-ready examples
- **Key Takeaways**:
  - Use $ARGUMENTS for dynamic parameters
  - Bash commands with ! prefix for preprocessing
  - File references with @ to include context
  - Project commands in .claude/commands/ for team sharing
- **Notes**: Practical patterns for command development

### Tutorial 4: Context Engineering for AI Assistants
- **URL**: https://www.aifire.co/p/ai-coding-assistants-a-guide-to-context-engineering-prp
- **Source**: AI Fire
- **Date**: 2025
- **Relevance**: 10/10 - foundational context engineering principles
- **What It Covers**: Shift from "code monkey" to "code architect", PRP methodology, validation principles, common pitfalls
- **Code Quality**: Conceptual - methodology focus
- **Key Takeaways**:
  - Context engineering > prompt engineering
  - Treat AI as junior developer needing comprehensive briefing
  - Validation is non-negotiable
  - Context is ongoing discipline, not one-time setup
- **Notes**: Essential reading for understanding why PRP approach works

### Tutorial 5: How to Use Claude Code Subagents to Parallelize Development
- **URL**: https://zachwills.net/how-to-use-claude-code-subagents-to-parallelize-development/
- **Source**: Zach Wills Blog
- **Date**: 2025
- **Relevance**: 8/10 - practical parallelization patterns
- **What It Covers**: Parallel workflow design, coordinating multiple subagents, managing results, avoiding conflicts
- **Code Quality**: High
- **Key Takeaways**:
  - Design workflows with parallelization in mind
  - Clear separation of concerns between agents
  - Result aggregation strategies
  - Conflict resolution patterns
- **Notes**: Good for Phase 2 parallel research implementation

## Version Considerations

### Claude Code
- **Recommended Version**: Latest stable (>= 1.0.124)
- **Reason**: SlashCommand tool support, improved subagent delegation, Task tool maturity
- **Breaking Changes**: Earlier versions may not support all subagent features
- **Compatibility**: Works with MCP servers via stdio or HTTP transport

### Archon MCP Server
- **Current Version**: Beta
- **Reason**: Active development, some features may not work 100%
- **Migration Path**: Monitor GitHub releases for stable version
- **Compatibility**: Requires MCP-compatible clients (Claude Code, Cursor, Windsurf)

### Context Engineering Methodology
- **Version**: 2025 patterns
- **Evolution**: From prompt engineering → context engineering → PRP methodology
- **Updates**: Active community contributions on GitHub

## Common Pitfalls Documented

### Pitfall 1: Subagent Context Pollution
- **Source**: https://docs.claude.com/en/docs/claude-code/sub-agents
- **Problem**: Main conversation context gets polluted when not using subagents for research tasks
- **Symptom**: Claude loses track of high-level objectives, gets bogged down in details
- **Solution**: Delegate research, analysis, and exploration to specialized subagents with isolated contexts
- **Code Example**:
```yaml
# Wrong: Doing research in main context
"Search the codebase for authentication patterns"

# Right: Delegate to specialized subagent
---
name: auth-researcher
description: Research authentication patterns in codebase
tools: Grep, Glob, Read
---
You are an authentication research specialist.
Search for auth patterns and document findings.
```

### Pitfall 2: Vague Subagent System Prompts
- **Source**: https://cuong.io/blog/2025/06/24-claude-code-subagent-deep-dive
- **Problem**: Generic system prompts lead to unfocused subagent behavior
- **Symptom**: Subagent produces generic or off-target results
- **Solution**: Write highly specific system prompts with clear objectives, checklists, and constraints
- **Code Example**:
```yaml
# Wrong
---
name: code-helper
description: Helps with code
---
You help with code.

# Right
---
name: python-linter
description: Lint Python code for PEP8 compliance and security issues
tools: Read, Bash
---
You are a Python code quality specialist.

Your task:
1. Read the specified Python files
2. Run: ruff check --select=E,F,W,C,N,D,S
3. Report issues by category with file:line references
4. Provide specific fix suggestions

Focus areas:
- PEP8 compliance (E, W)
- Code complexity (C)
- Security issues (S)
- Docstring coverage (D)
```

### Pitfall 3: Incorrect Archon Query Patterns
- **Source**: https://github.com/coleam00/Archon (README)
- **Problem**: Using long, verbose queries instead of 2-5 keywords
- **Symptom**: Poor search results from RAG system
- **Solution**: Use SHORT, focused queries for Archon searches
- **Code Example**:
```python
# Wrong: Verbose query
rag_search_knowledge_base(
    query="How do I implement user authentication with JWT tokens in FastAPI with proper security practices and refresh token rotation",
    match_count=5
)

# Right: Short, focused
rag_search_knowledge_base(
    query="FastAPI JWT auth",
    match_count=5
)

# Even better: Multiple targeted searches
rag_search_knowledge_base(query="JWT authentication", match_count=3)
rag_search_knowledge_base(query="refresh tokens", match_count=3)
rag_search_knowledge_base(query="FastAPI security", match_count=3)
```

### Pitfall 4: Blind Parallel Execution
- **Source**: https://medium.com/@codecentrevibe/claude-code-multi-agent-parallel-coding-83271c4675fa
- **Problem**: Running subagents in parallel without clear orchestration strategy
- **Symptom**: Duplicate work, conflicting outputs, difficult result aggregation
- **Solution**: Design workflow with explicit coordination points and result synthesis
- **Code Example**:
```markdown
# Wrong: Vague parallelization
"Use 3 subagents to research this feature"

# Right: Explicit orchestration
Phase 2: Parallel Research

Run these 3 subagents simultaneously:

1. codebase-researcher
   - Input: feature-analysis.md
   - Output: codebase-patterns.md
   - Focus: Existing code patterns

2. documentation-hunter
   - Input: feature-analysis.md
   - Output: documentation-links.md
   - Focus: Official docs and guides

3. example-curator
   - Input: feature-analysis.md
   - Output: examples-to-include.md + examples/
   - Focus: Extract working code examples

Coordination: All 3 complete before Phase 3 begins
Synthesis: Assembler reads all 3 outputs
```

### Pitfall 5: Missing Validation Loops
- **Source**: https://www.aifire.co/p/ai-coding-assistants-a-guide-to-context-engineering-prp
- **Problem**: Trusting AI output without validation, leading to broken code in production
- **Symptom**: Code that "should work" but fails in testing or production
- **Solution**: Implement progressive validation loops (syntax → unit tests → integration)
- **Code Example**:
```bash
# Wrong: Skip validation
# "The code looks good, ship it!"

# Right: Progressive validation
## Validation Loop

### Level 1: Syntax & Style
ruff check --fix .
mypy .

### Level 2: Unit Tests
pytest tests/ -v

### Level 3: Integration Tests
./scripts/integration-test.sh

### Level 4: Manual Verification
# Test actual feature with real data

## Iterate until ALL levels pass
# If any level fails, fix and restart from that level
```

### Pitfall 6: Hardcoding Source IDs
- **Source**: Archon MCP documentation
- **Problem**: Using URLs instead of source_id parameter, or hardcoding source IDs
- **Symptom**: Searches fail or return wrong sources
- **Solution**: Always call rag_get_available_sources() first, match by title, use returned ID
- **Code Example**:
```python
# Wrong: Hardcoded or using URL
rag_search_knowledge_base(
    query="FastAPI patterns",
    source_id="https://fastapi.tiangolo.com",  # URLs don't work!
    match_count=5
)

# Wrong: Hardcoded ID
rag_search_knowledge_base(
    query="FastAPI patterns",
    source_id="src_abc123",  # May not exist in this Archon instance
    match_count=5
)

# Right: Dynamic source lookup
sources = rag_get_available_sources()
fastapi_source = next(
    (s for s in sources if "FastAPI" in s["title"]),
    None
)

if fastapi_source:
    results = rag_search_knowledge_base(
        query="async patterns",
        source_id=fastapi_source["source_id"],
        match_count=5
    )
```

## Code Examples from Documentation

### Example 1: Complete Subagent Configuration
- **Source**: https://docs.claude.com/en/docs/claude-code/sub-agents
- **Code**:
```yaml
---
name: api-integration-specialist
description: Expert in integrating third-party APIs with proper error handling and rate limiting
tools: Read, Write, Bash, WebFetch
model: sonnet
---
You are an API integration specialist focused on production-ready implementations.

Your responsibilities:
1. Research API documentation thoroughly
2. Implement proper authentication (OAuth, API keys, etc.)
3. Add comprehensive error handling
4. Implement rate limiting and retry logic
5. Write integration tests

Standards:
- Use environment variables for credentials
- Implement exponential backoff for retries
- Log all API calls with request IDs
- Handle all documented error cases
- Write clear docstrings with example usage

Testing:
- Mock API responses in unit tests
- Provide manual testing instructions
- Document rate limits and quotas
```
- **Explanation**: Complete subagent definition with frontmatter configuration and detailed system prompt
- **Applicability**: Use as template for all 6 INITIAL.md factory subagents
- **Modifications Needed**: Adjust name, description, tools, and system prompt for each specialist role

### Example 2: Slash Command with Arguments
- **Source**: https://docs.claude.com/en/docs/claude-code/slash-commands
- **Code**:
```yaml
---
description: Generate comprehensive PRP from INITIAL.md
argument-hint: <feature-name>
model: sonnet
allowed-tools: Read, Write, Grep, Glob, Task, mcp__archon__rag_search_knowledge_base, mcp__archon__rag_get_available_sources
---

# PRP Generation Command

Feature: $ARGUMENTS

## Phase 1: Read INITIAL.md
!cat prps/INITIAL_$ARGUMENTS.md

## Phase 2: Research Codebase
Search for existing patterns related to this feature.

## Phase 3: Gather Documentation
Find official docs and guides.

## Phase 4: Generate PRP
Create comprehensive PRP in prps/$ARGUMENTS.md following template.

## Validation
- [ ] All sections complete
- [ ] Code examples included
- [ ] Validation loops defined
- [ ] Success criteria clear
```
- **Explanation**: Slash command that accepts arguments, runs bash commands, and orchestrates multi-phase workflow
- **Applicability**: Template for improving generate-prp command
- **Modifications Needed**: Add Archon integration, subagent delegation, parallel execution

### Example 3: Parallel Subagent Invocation
- **Source**: Claude Code best practices (community patterns)
- **Code**:
```python
# In slash command or main context:
# Invoke 3 subagents in parallel (single Task tool call)

Task(
    agents=[
        "prp-initial-codebase-researcher",
        "prp-initial-documentation-hunter",
        "prp-initial-example-curator"
    ],
    instructions=[
        "Research codebase patterns → codebase-patterns.md",
        "Find official documentation → documentation-links.md",
        "Extract code examples → examples-to-include.md + examples/"
    ],
    outputs=[
        "prps/research/codebase-patterns.md",
        "prps/research/documentation-links.md",
        "prps/research/examples-to-include.md"
    ]
)

# Wait for all 3 to complete, then proceed to Phase 3
```
- **Explanation**: Parallel invocation pattern for Phase 2 research
- **Applicability**: Critical for INITIAL.md factory Phase 2 parallel execution
- **Modifications Needed**: Verify Task tool supports this syntax (may need 3 separate Task calls in same message)

### Example 4: Archon RAG Integration Pattern
- **Source**: https://github.com/coleam00/Archon
- **Code**:
```python
# Complete Archon workflow for research task

# Step 1: Check what documentation is available
sources = mcp__archon__rag_get_available_sources()
# Returns: [
#   {source_id: "src_123", title: "FastAPI Documentation", ...},
#   {source_id: "src_456", title: "Pydantic AI Docs", ...}
# ]

# Step 2: Find relevant source
target_source = next(
    (s for s in sources if "FastAPI" in s["title"]),
    None
)

# Step 3: General search (no source filter)
general_results = mcp__archon__rag_search_knowledge_base(
    query="async patterns",  # 2-5 keywords!
    match_count=5
)

# Step 4: Filtered search (specific source)
if target_source:
    specific_results = mcp__archon__rag_search_knowledge_base(
        query="dependency injection",
        source_id=target_source["source_id"],
        match_count=5
    )

# Step 5: Extract relevant sections
for result in specific_results["results"]:
    content = result["content"]
    url = result["metadata"]["url"]
    # Use in documentation
```
- **Explanation**: Complete pattern for searching Archon knowledge base
- **Applicability**: Use in all research subagents (documentation-hunter, codebase-researcher, gotcha-detective)
- **Modifications Needed**: None - this is the correct pattern

### Example 5: Validation Loop Implementation
- **Source**: https://github.com/coleam00/context-engineering-intro
- **Code**:
```markdown
## Validation Loop

### Level 1: Syntax & Style
```bash
# Python
ruff check --fix .
mypy src/

# TypeScript
eslint --fix .
tsc --noEmit
```

**Exit Criteria**: Zero errors from all tools

### Level 2: Unit Tests
```bash
# Python
pytest tests/unit/ -v --cov=src --cov-report=term-missing

# TypeScript
npm test -- --coverage
```

**Exit Criteria**: All tests pass, >80% coverage

### Level 3: Integration Tests
```bash
# Start dependencies
docker-compose up -d

# Run integration tests
pytest tests/integration/ -v

# Cleanup
docker-compose down
```

**Exit Criteria**: All integration tests pass

### Level 4: Manual Verification
- [ ] Feature works end-to-end
- [ ] Error cases handled gracefully
- [ ] UI/UX is intuitive
- [ ] Performance is acceptable

## Iterate Until All Levels Pass
If any level fails:
1. Fix the issues
2. Restart validation from that level
3. Do NOT skip to next level
4. Do NOT assume "it should work now"
```
- **Explanation**: Progressive validation with clear exit criteria and iteration instructions
- **Applicability**: Include in all generated PRPs to ensure quality
- **Modifications Needed**: Adjust tools/commands for specific project tech stack

## Security & Authentication Guidance

From official documentation:

### Security Best Practices
- **Source**: https://docs.claude.com/en/docs/claude-code/sub-agents
- **Key Practices**:
  - **Tool Restrictions**: Limit each subagent to minimum required tools - don't grant Write/Bash to read-only researchers
  - **Permissions Management**: Use `/permissions` command to deny tools at global level
  - **Environment Variables**: Never hardcode credentials - always use env vars
  - **MCP Security**: Local MCP servers (stdio) run in same security context as Claude Code
- **Code Examples**: See subagent configuration examples above

### Authentication Patterns
- **Recommended Method**: Environment variables for all credentials
- **Documentation**: https://docs.claude.com/en/docs/claude-code/settings
- **Implementation Guide**:
  1. Add to `.env` file (gitignored)
  2. Reference in code via `os.environ.get("VAR_NAME")`
  3. Document in README with `.env.example`
- **Code Example**:
```bash
# .env.example
ANTHROPIC_API_KEY=your-key-here
ARCHON_URL=http://localhost:8051
OPENAI_API_KEY=your-openai-key

# In code
import os
api_key = os.environ.get("ANTHROPIC_API_KEY")
if not api_key:
    raise ValueError("ANTHROPIC_API_KEY not set")
```

## Deployment & Configuration

### Environment Setup
- **Source**: https://github.com/coleam00/Archon
- **Required Environment Variables**:
  - `ANTHROPIC_API_KEY`: Claude API access
  - `OPENAI_API_KEY`: OpenAI models (optional)
  - `ARCHON_URL`: MCP server endpoint (default: http://localhost:8051)
  - `SUPABASE_URL`: Database URL
  - `SUPABASE_KEY`: Database auth key
- **Configuration Files**:
  - `.claude/settings.local.json` - Claude Code permissions
  - `claude.json` - MCP server configurations
- **Setup Guide**: https://github.com/coleam00/Archon#installation

### Deployment Considerations
- **Documentation**: https://docs.claude.com/en/docs/claude-code/
- **Supported Platforms**:
  - macOS (native)
  - Windows (native)
  - Linux (native)
- **Scaling Guidance**:
  - Archon uses microservices architecture - can scale each service independently
  - PostgreSQL + PGVector for RAG - horizontal scaling possible
  - MCP servers can be local (stdio) or remote (HTTP)

## Testing Guidance from Official Docs

### Testing Approach Recommended
- **Source**: Context Engineering methodology
- **Framework**: Depends on language (pytest for Python, jest for TypeScript)
- **Patterns**:
  - Unit tests for individual functions
  - Integration tests for MCP tool calls
  - End-to-end tests for complete workflows
  - Mock external dependencies (Archon, OpenAI, etc.)
- **Example Tests**: See validation loop examples above

### Mocking External Services
- **Guide**: Standard mocking patterns for each language
- **Tools Recommended**:
  - Python: `pytest-mock`, `responses` for HTTP
  - TypeScript: `jest.mock()`, `msw` for API mocking
- **Examples**:
```python
# Python: Mock Archon MCP calls
def test_rag_search(mocker):
    mock_search = mocker.patch("mcp.archon.rag_search_knowledge_base")
    mock_search.return_value = {
        "success": True,
        "results": [{"content": "test", "similarity_score": 0.9}]
    }

    result = search_documentation("FastAPI")
    assert result["success"]
    mock_search.assert_called_once()
```

## Archon Sources Summary

**Total Archon Sources Used**: 4

| Source ID | Title | Relevance | Sections Used |
|-----------|-------|-----------|---------------|
| 9a7d4217c64c9a0a | Anthropic Documentation | 10/10 | 3 |
| b8565aff9938938b | GitHub - coleam00/context-engineering-intro | 10/10 | 2 |
| 464a0ce4d22bf72f | Microsoft Agents Framework | 7/10 | 1 |
| d60a71d62eb201d5 | Model Context Protocol - LLMs | 8/10 | 1 |

## External URLs Summary

**Total External URLs**: 15

**By Category**:
- Official Documentation: 4 (Claude Code, MCP, Archon, Context Engineering)
- API References: 2 (MCP tools, Archon MCP)
- Tutorials: 5 (Parallel agents, subagent deep dive, slash commands, context engineering, parallelization)
- Best Practices: 4 (Context engineering guide, PRP methodology, Claude Code workflows, validation patterns)

## Research Quality Assessment

- **Documentation Coverage**: Complete
- **Code Examples Available**: Yes - 15+ complete examples
- **Version Information Current**: Yes - all 2025 documentation
- **Security Guidance Found**: Yes - tool restrictions, environment variables
- **Testing Guidance Found**: Yes - validation loops, mocking patterns

**Gaps Identified**:
- Limited documentation on Task tool parallel invocation syntax (community patterns exist but not official docs)
- Archon in beta - some features may not work 100%
- No official migration guides for Claude Code version updates

**Recommendations**:
- Monitor Claude Code changelog for Task tool updates
- Follow Archon GitHub issues for beta stability improvements
- Test parallel Task invocation patterns in development before production use
- Create internal wiki documenting discovered patterns

---
Generated: 2025-10-04
Archon Sources Used: 4
External URLs: 15
Code Examples Found: 15
Feature: prp_workflow_improvements
