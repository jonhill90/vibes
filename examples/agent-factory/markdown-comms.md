# Markdown Communication Protocol

This example demonstrates how agents communicate through structured markdown files - the foundation of the Context Engineering Agent Factory pattern.

## Pattern Overview

**Concept**: Agents communicate by writing and reading structured markdown files

**Why Markdown**:
- ✅ Human-readable and reviewable
- ✅ Version-controllable with git
- ✅ Structured yet flexible
- ✅ No complex serialization
- ✅ Easy to debug and modify
- ✅ LLMs excel at markdown generation

## Basic Communication Flow

```
┌─────────────┐
│   Agent A   │  Produces information
└──────┬──────┘
       │
       ▼
   ┌────────────┐
   │ output.md  │  Structured markdown file
   └──────┬─────┘
          │
          ▼
   ┌─────────────┐
   │   Agent B   │  Consumes information
   └─────────────┘
```

## Message Format Standards

### Producer Agent Responsibilities

**1. Create Structured Documents**

```markdown
# [Document Title]

## [Section 1: Required Information]
[Content that consumers need]

## [Section 2: Additional Context]
[Supporting information]

## [Section 3: Metadata]
[How to use this information]
```

**2. Follow Consistent Naming**

- `INITIAL.md` - First requirements/specifications document
- `[component].md` - Component-specific specs (prompts.md, tools.md, dependencies.md)
- `[COMPONENT]_REPORT.md` - Status and validation reports
- `README.md` - Final user-facing documentation

**3. Include All Necessary Context**

Don't assume consumers know context - include everything they need:

```markdown
# API Specification

## Context
This API supports the product catalog feature with search and filtering.

## Endpoints

### GET /products
**Purpose**: Search and filter products
**Query Params**:
- `q` (string, optional): Search query
- `category` (string, optional): Filter by category
- `min_price` (number, optional): Minimum price
- `max_price` (number, optional): Maximum price

**Response**:
```json
{
  "products": [...],
  "total": 100,
  "page": 1
}
```
```

### Consumer Agent Responsibilities

**1. Read Complete Documents**

```python
# Use Read tool to get full content
content = read_file("projects/catalog/planning/INITIAL.md")

# Parse structure
sections = extract_sections(content)

# Extract needed information
requirements = sections["Functional Requirements"]
```

**2. Validate Information Completeness**

Before processing, check if document has all needed sections:

```markdown
## Validation

Required sections in INITIAL.md:
- [ ] Functional Requirements
- [ ] Technical Requirements
- [ ] Success Criteria

If missing sections, report error and request clarification.
```

**3. Use Exact Paths From Prompts**

```xml
<prompt>
Input: projects/catalog/planning/INITIAL.md
Output: projects/catalog/planning/DESIGN.md

Read the input file and create the output file.
</prompt>
```

Agent must use EXACTLY these paths - no assumptions or modifications.

## Real-World Example: Agent Factory Phase 2

### Scenario: Three Parallel Agents Reading Same Input

**Shared Input** (created by planner in Phase 1):
`agents/web_search_agent/planning/INITIAL.md`

```markdown
# Web Search Agent - Requirements

## Agent Classification
- Type: Tool-based agent
- Primary capability: Web search with Brave API
- Output format: Structured search results

## Functional Requirements

1. **Web Search**
   - Accept search queries as user input
   - Execute search via Brave Search API
   - Return top 10 results with titles, URLs, snippets

2. **Result Processing**
   - Parse search results
   - Format for readability
   - Handle no-results gracefully

## Technical Requirements
- Use pydantic-ai framework
- Async operations for API calls
- Error handling for network failures
- Rate limiting compliance

## External Dependencies
- Brave Search API (requires API key)
- HTTP client (httpx recommended)

## Success Criteria
- [ ] Agent successfully executes searches
- [ ] Results properly formatted
- [ ] Errors handled gracefully
- [ ] API key securely managed
```

### Agent 1: Prompt Engineer

**Reads**: `agents/web_search_agent/planning/INITIAL.md`
**Produces**: `agents/web_search_agent/planning/prompts.md`

```markdown
# Web Search Agent - System Prompts

## Primary System Prompt

You are a web search assistant powered by Brave Search API. Your role is to help users find relevant information on the web.

When a user asks a question or requests information:
1. Formulate an effective search query
2. Execute the search using your web_search tool
3. Present results in a clear, organized format

Always:
- Provide source URLs for verification
- Summarize key findings
- Suggest follow-up searches if appropriate

## Prompt Configuration

- **Length**: 150 words
- **Temperature**: 0.7 (balanced creativity/consistency)
- **Tone**: Helpful and informative

## Usage

```python
system_prompt = \"\"\"
You are a web search assistant powered by Brave Search API...
\"\"\"

agent = Agent(
    model="openai:gpt-4",
    system_prompt=system_prompt,
    ...
)
```
```

### Agent 2: Tool Integrator

**Reads**: `agents/web_search_agent/planning/INITIAL.md`
**Produces**: `agents/web_search_agent/planning/tools.md`

```markdown
# Web Search Agent - Tool Specifications

## Tool 1: web_search

### Purpose
Execute web searches using Brave Search API and return formatted results.

### Function Signature

```python
async def web_search(
    ctx: RunContext[AgentDependencies],
    query: str,
    max_results: int = 10
) -> str:
    \"\"\"
    Search the web using Brave Search API.

    Args:
        ctx: Agent context with dependencies
        query: Search query string
        max_results: Maximum number of results (default 10)

    Returns:
        Formatted search results with titles, URLs, and snippets
    \"\"\"
```

### Implementation Notes
- Use httpx for async HTTP requests
- API endpoint: https://api.search.brave.com/res/v1/web/search
- Include User-Agent header
- Handle rate limiting (429 responses)
- Timeout after 30 seconds

### Error Handling
- Network errors: Return "Search unavailable, please try again"
- Invalid API key: Log error, return "Configuration error"
- No results: Return "No results found for: {query}"

### Dependencies Required
- API key via ctx.deps.search_api_key
- httpx client via ctx.deps.http_client
```

### Agent 3: Dependency Manager

**Reads**: `agents/web_search_agent/planning/INITIAL.md`
**Produces**: `agents/web_search_agent/planning/dependencies.md`

```markdown
# Web Search Agent - Dependencies

## Environment Variables

### BRAVE_API_KEY (required)
- **Description**: API key for Brave Search API
- **How to obtain**: Register at https://brave.com/search/api/
- **Format**: String, alphanumeric
- **Example**: `.env.example` should contain `BRAVE_API_KEY=your_key_here`

## Python Packages

### Core Dependencies
```txt
pydantic-ai>=0.0.14
pydantic>=2.0.0
httpx>=0.27.0
python-dotenv>=1.0.0
```

### Development Dependencies
```txt
pytest>=8.0.0
pytest-asyncio>=0.23.0
```

## Model Providers

### Primary: OpenAI GPT-4
```python
from pydantic_ai.models.openai import OpenAIModel

model = OpenAIModel("gpt-4")
```

### Configuration
```python
class AgentDependencies(BaseModel):
    search_api_key: str  # From BRAVE_API_KEY env var
    http_client: httpx.AsyncClient
```

## Installation

```bash
pip install -r requirements.txt
cp .env.example .env
# Add BRAVE_API_KEY to .env
```
```

### How Communication Works

**Phase 2 Orchestration**:

```markdown
Phase 2: Parallel Component Design (3 agents work simultaneously)

All agents read the same INITIAL.md and create their specialized outputs...

<tool_use>
  <tool_name>Task</tool_name>
  <parameters>
    <description>Design system prompts</description>
    <prompt>
You are pydantic-ai-prompt-engineer.

Input: agents/web_search_agent/planning/INITIAL.md
Output: agents/web_search_agent/planning/prompts.md
Folder: web_search_agent

[Instructions...]
    </prompt>
    <subagent_type>pydantic-ai-prompt-engineer</subagent_type>
  </parameters>
</tool_use>

<tool_use>
  <tool_name>Task</tool_name>
  <parameters>
    <description>Plan tool implementations</description>
    <prompt>
You are pydantic-ai-tool-integrator.

Input: agents/web_search_agent/planning/INITIAL.md
Output: agents/web_search_agent/planning/tools.md
Folder: web_search_agent

[Instructions...]
    </prompt>
    <subagent_type>pydantic-ai-tool-integrator</subagent_type>
  </parameters>
</tool_use>

<tool_use>
  <tool_name>Task</tool_name>
  <parameters>
    <description>Configure dependencies</description>
    <prompt>
You are pydantic-ai-dependency-manager.

Input: agents/web_search_agent/planning/INITIAL.md
Output: agents/web_search_agent/planning/dependencies.md
Folder: web_search_agent

[Instructions...]
    </prompt>
    <subagent_type>pydantic-ai-dependency-manager</subagent_type>
  </parameters>
</tool_use>
```

**Result**: Three markdown files, each with specialized information, all consistent because they used the same input and folder name.

## Communication Patterns

### Pattern 1: Linear Chain

Sequential processing where each agent builds on the previous:

```
Agent A → doc1.md → Agent B → doc2.md → Agent C → doc3.md
```

**Example**:
```
planner → INITIAL.md → designer → DESIGN.md → implementer → CODE
```

### Pattern 2: Fan-Out (Parallel)

One input, multiple parallel outputs:

```
                   ┌→ Agent A → output1.md
input.md → [split] ├→ Agent B → output2.md
                   └→ Agent C → output3.md
```

**Example**:
```
                     ┌→ prompt-engineer → prompts.md
INITIAL.md → [read] ├→ tool-integrator → tools.md
                     └→ dependency-mgr → dependencies.md
```

### Pattern 3: Fan-In (Merge)

Multiple inputs, one output:

```
input1.md ─┐
input2.md ─┼→ Agent → combined.md
input3.md ─┘
```

**Example**:
```
prompts.md ──┐
tools.md ────┼→ implementer → agent.py
deps.md ─────┘
```

### Pattern 4: Tree (Hierarchical)

Complex workflows with multiple levels:

```
root.md → Agent A → branch1.md ─┬→ Agent B → leaf1.md
                                 └→ Agent C → leaf2.md
```

## Document Structure Standards

### Requirements Documents (INITIAL.md)

```markdown
# [Feature Name] - Requirements

## Overview
[Brief summary]

## Functional Requirements
1. [Requirement 1]
2. [Requirement 2]
...

## Technical Requirements
- [Technical requirement 1]
- [Technical requirement 2]
...

## External Dependencies
- [Dependency 1]: [Purpose]
- [Dependency 2]: [Purpose]

## Success Criteria
- [ ] [Criterion 1]
- [ ] [Criterion 2]
...
```

### Specification Documents ([component].md)

```markdown
# [Component Name] - Specification

## Purpose
[What this component does]

## [Main Section]
[Detailed specification]

## Configuration
[How to configure]

## Usage
```[language]
[Code example]
```

## Notes
[Important considerations]
```

### Report Documents ([COMPONENT]_REPORT.md)

```markdown
# [Component] - Report

## Summary
- **Status**: [Complete/Incomplete/Failed]
- **Issues Found**: [Number]
- **Recommendations**: [Number]

## Details
[Detailed findings]

## Issues
1. [Issue 1]
2. [Issue 2]

## Recommendations
1. [Recommendation 1]
2. [Recommendation 2]
```

## Best Practices

### 1. Use Consistent Headings

Consumers rely on section names to extract information:

```markdown
✅ Good:
## Functional Requirements
[Content]

❌ Bad:
## Requirements (Functional)  # Different format
## What it should do          # Informal
```

### 2. Include Context in Every Document

Don't assume readers have background:

```markdown
✅ Good:
# Database Schema for Product Catalog

This schema supports search, filtering, and cart integration
for the product catalog feature.

❌ Bad:
# Database Schema

[Just schema without context]
```

### 3. Provide Examples

Help consumers understand your intent:

```markdown
## API Endpoint

GET /products?q=laptop&category=electronics&max_price=1000

Returns products matching search query "laptop" in electronics
category under $1000.
```

### 4. Specify Exact Requirements

Be precise about what's needed:

```markdown
✅ Good:
## Environment Variables

BRAVE_API_KEY (required): Brave Search API key
- Format: Alphanumeric string
- How to get: Register at https://brave.com/search/api/

❌ Bad:
## Environment Variables

BRAVE_API_KEY: API key (required)
```

## Error Handling in Communication

### Producer Errors

**Problem**: Can't create output file

```markdown
## Error Handling

If output path is inaccessible:
1. Report error with exact path attempted
2. Suggest alternative path
3. Do not create partial files
```

**Problem**: Input file missing required information

```markdown
## Validation

Before processing:
1. Check for all required sections in input
2. If missing, list specific gaps
3. Request clarification rather than guessing
```

### Consumer Errors

**Problem**: Can't find input file

```markdown
## Input Validation

Before reading:
1. Verify file exists at specified path
2. If not found, report exact path checked
3. Do not proceed with assumptions
```

**Problem**: Input file has unexpected format

```markdown
## Format Validation

After reading:
1. Verify all required sections present
2. If format unexpected, report discrepancies
3. Attempt best-effort parsing, document issues
```

## Debugging Communication Issues

### Issue: Agent can't find file

**Check**:
1. Exact path in prompt: `agents/web_search_agent/planning/INITIAL.md`
2. Exact path agent is trying: `agents/websearch/planning/INITIAL.md` ❌
3. **Solution**: Use EXACT folder name provided: `web_search_agent`

### Issue: Missing information in output

**Check**:
1. Does input have the information? (Read input file)
2. Did agent extract correctly? (Check agent's parsing logic)
3. **Solution**: Update input or fix extraction logic

### Issue: Inconsistent structure

**Check**:
1. Are all producers following same template?
2. Are section names consistent?
3. **Solution**: Define strict templates, validate outputs

## Summary

**Markdown Communication Protocol**:
- ✅ Structured markdown files as message format
- ✅ Producers create complete, contextualized documents
- ✅ Consumers validate and extract information
- ✅ Exact paths and folder names across all agents
- ✅ Consistent section naming for reliable parsing
- ✅ Human-readable and version-controllable

**Patterns**:
- Linear chains for sequential processing
- Fan-out for parallel work from one source
- Fan-in for combining multiple sources
- Trees for hierarchical workflows

**Best Practices**:
- Use consistent document structures
- Include complete context in every file
- Provide examples and precise specifications
- Validate inputs and outputs
- Use exact paths from prompts

---

This communication protocol enables the entire Agent Factory pattern. See:
- [simple-subagent.md](./simple-subagent.md) - Basic agent pattern
- [parallel-workflow.md](./parallel-workflow.md) - Parallel execution
- [.claude/orchestrators/agent-factory.md](../../.claude/orchestrators/agent-factory.md) - Full implementation
