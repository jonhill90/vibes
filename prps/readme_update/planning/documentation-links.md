# Documentation Resources: README.md Update Post-Context Refactor

## Overview

This document curates official documentation, technical resources, and best practices for updating the Vibes README.md to accurately reflect the current system state after successful context optimization (59-70% token reduction). Focus is on MCP server documentation, technical writing patterns, context engineering principles, and progressive disclosure techniques.

---

## Primary MCP Documentation

### Model Context Protocol (Official Specification)
**Official Docs**: https://modelcontextprotocol.io/specification/2025-06-18/index
**Version**: 2025-06-18 (Latest)
**Archon Source**: d60a71d62eb201d5
**Relevance**: 10/10

**Sections to Read**:
1. **Protocol Overview**: https://modelcontextprotocol.io/llms-full.txt#scope
   - **Why**: Explains MCP architecture, layers (data + transport), and client-server model
   - **Key Concepts**: MCP servers can run locally (STDIO) or remotely (HTTP), JSON-RPC protocol, lifecycle management

2. **Core Concepts**: https://modelcontextprotocol.io/llms-full.txt#concepts-of-mcp
   - **Why**: Defines tools, resources, prompts, and notifications—core primitives for server capabilities
   - **Key Concepts**: Data layer protocol, transport layer mechanisms, security considerations

3. **Example Servers**: https://modelcontextprotocol.io/examples
   - **Why**: Reference implementations showing official server patterns (fetch, filesystem, git)
   - **Key Concepts**: Server capability patterns, tool design, resource management

**Code Examples from Docs**:
```json
{
  "mcpServers": {
    "filesystem": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-filesystem", "/path/to/allowed/files"]
    },
    "fetch": {
      "command": "uvx",
      "args": ["mcp-server-fetch"]
    }
  }
}
```

**Gotchas from Documentation**:
- MCP servers can execute locally OR remotely—don't assume all are local processes
- Security considerations: Clients SHOULD implement user approval controls and rate limiting
- Transport types matter: STDIO for local, Streamable HTTP for remote
- Both parties MUST handle sensitive data appropriately

---

## MCP Server Implementations

### 1. Archon MCP Server
**Official Docs**: https://github.com/coleam00/Archon
**Purpose**: Task/knowledge management, RAG search, project tracking
**Archon Source**: b8565aff9938938b (Context Engineering Intro repo includes Archon usage)
**Relevance**: 10/10

**Key Features**:
- Web crawling and document processing
- Advanced semantic search with contextual embeddings
- Multi-LLM support (OpenAI, Ollama, Google Gemini)
- Real-time collaboration and task management
- Microservices architecture (Frontend, Server API, MCP Server, Agents Service)

**Architecture**:
- Frontend UI: React + Vite (Port 3737)
- Server API: FastAPI + SocketIO (Port 8181)
- MCP Server: Lightweight HTTP Wrapper (Port 8051)
- Agents Service: PydanticAI (Port 8052)

**Configuration Example**:
```json
"archon": {
  "command": "npx",
  "args": ["mcp-remote", "http://localhost:8051/mcp"]
}
```

**Key Capabilities**:
- `find_tasks()` - Search and filter tasks by status/project
- `manage_task()` - Create/update/delete tasks
- `find_projects()` - Search projects
- `rag_search_knowledge_base()` - Search documentation (2-5 keywords)
- `rag_get_available_sources()` - List available documentation sources

**Setup Requirements**:
- Docker Desktop
- Node.js 18+
- Supabase account
- OpenAI API key (or alternative LLM provider)

**Usage Pattern** (from CLAUDE.md):
```
1. Get Task → find_tasks(task_id="..." or filter_by="status", filter_value="todo")
2. Start Work → manage_task("update", task_id="...", status="doing")
3. Research → rag_search_knowledge_base(query="...", source_id="...")
4. Complete → manage_task("update", task_id="...", status="done")
```

**Gotchas**:
- Task status flow: `todo` → `doing` → `review` → `done` (follow this order)
- Keep RAG queries SHORT (2-5 keywords) for better results
- Higher `task_order` = higher priority (0-100 scale)
- Source ID must match actual source from `rag_get_available_sources()`

---

### 2. Docker MCP Gateway
**Official Docs**: https://docs.docker.com/ai/mcp-gateway/
**GitHub**: https://github.com/docker/mcp-gateway
**Purpose**: Orchestrate and manage MCP servers securely in containers
**Archon Source**: Not in Archon
**Relevance**: 9/10

**Key Features**:
- Container-based servers (MCP servers in isolated Docker containers)
- Unified management (centralized config, credentials, access control)
- Secrets management (secure API keys via Docker Desktop)
- OAuth integration (built-in OAuth flows for service authentication)
- Enterprise observability (monitoring, logging, filtering)

**Security Advantages**:
- MCP servers run with restricted privileges
- Network access and resource usage controlled
- Verify container image provenance before use
- Block-secrets interceptor scans for leaked credentials

**Installation & Commands**:
```bash
# Run MCP gateway (stdio transport)
docker mcp gateway run

# Run MCP gateway (streaming transport)
docker mcp gateway run --port 8080 --transport streaming

# Enable specific servers
docker mcp server enable <server-name>

# Connect a client
docker mcp client connect vscode
```

**Configuration Example**:
```json
"MCP_DOCKER": {
  "command": "docker",
  "args": ["mcp", "gateway", "run"]
}
```

**Use Cases**:
- **Developers**: Deploy MCP servers locally and in production
- **Security Teams**: Achieve enterprise-grade isolation and visibility
- **Operators**: Scale consistently across environments

**Gotchas**:
- Requires Docker Desktop with MCP Toolkit enabled
- Gateway unifies multiple MCP servers into single endpoint
- Container networking must be configured for server communication
- Interceptors (verify-signatures, block-secrets) add security layers

---

### 3. Basic Memory MCP Server
**Official Docs**: https://github.com/basicmachines-co/basic-memory
**Purpose**: Persistent memory across Claude sessions via local Markdown files
**Archon Source**: Not in Archon
**Relevance**: 8/10

**Key Features**:
- Local-first knowledge storage (Markdown files on your computer)
- Bidirectional knowledge interaction (AI can read AND write)
- Integrates with Obsidian and Claude Desktop
- Semantic linking between topics
- Knowledge graph visualization

**Tools Provided**:
- `write_note(title, content, folder, tags)` - Create/update notes
- `read_note(identifier, page, page_size)` - Read existing notes
- `build_context(url, depth, timeframe)` - Web crawling for context
- `search(query, page, page_size)` - Search knowledge base
- `recent_activity(type, depth, timeframe)` - Activity tracking
- `canvas(nodes, edges, title, folder)` - Visualize knowledge graph

**Configuration Examples**:

*Claude Code*:
```bash
claude mcp add-json "basic-memory" '{"command":"uvx","args":["basic-memory","mcp"]}'
```

*VS Code* (User Settings JSON):
```json
{
  "mcp": {
    "servers": {
      "basic-memory": {
        "command": "uvx",
        "args": ["basic-memory", "mcp"]
      }
    }
  }
}
```

*Claude Desktop*:
```json
"basic-memory": {
  "command": "docker",
  "args": ["exec", "-i", "basic-memory-mcp", "/app/start.sh"]
}
```

**Data Format**:
- Frontmatter for metadata (YAML)
- Observations as structured facts
- Relations connecting different topics
- Simple Markdown structure for human + AI readability

**Use Cases**:
- Never re-explain your project to Claude
- Build persistent knowledge through conversations
- Create local knowledge graphs
- Integrate with note-taking workflows (Obsidian)

**Gotchas**:
- Requires `uv` package manager for installation
- Files stored locally—backup strategy needed
- Markdown format must follow specific structure for AI parsing
- Cloud sync optional but not built-in

---

### 4. Vibesbox MCP Server (Local Codebase)
**Local Docs**: `/Users/jon/source/vibes/mcp/mcp-vibesbox-server/README.md`
**Purpose**: Unified shell + VNC GUI automation + Chromium browser for containerized desktop
**Archon Source**: Not in Archon (local implementation)
**Relevance**: 10/10

**Status**: ✅ Production Ready + Chromium Confirmed (July 2025)

**Key Features**:
- Shell access via `run_command()`
- VNC desktop environment (XFCE4, 1920x1080)
- Screenshot capture for Claude's vision
- Desktop automation (click, drag, type, keyboard)
- ARM64 Chromium browser (Playwright-based)
- Container networking (access to vibes-network)

**MCP Tools** (7 total):
- `run_command(command, working_dir)` - Shell execution
- `take_screenshot(display=":1")` - Visual feedback for Claude
- `click_desktop(x, y, button, double_click)` - Mouse control
- `drag_mouse(start_x, start_y, end_x, end_y, button)` - Text selection
- `type_text(text)` - Keyboard input
- `send_keys(keys)` - Key combinations (Ctrl+C, Alt+Tab)
- `start_vnc_server(display, geometry, password)` - VNC management

**Configuration**:
```json
"vibesbox": {
  "command": "docker",
  "args": ["exec", "-i", "mcp-vibesbox-server", "python3", "/workspace/server.py"]
}
```

**Architecture Stack**:
- Ubuntu 22.04 base
- TigerVNC server + XFCE4 desktop
- Node.js 22.x + Playwright + ARM64 Chromium
- ImageMagick for screenshots
- xdotool for automation
- Python MCP server (stdio transport)

**Performance Metrics**:
- Screenshot Speed: ~0.5s capture + base64 conversion
- Automation Latency: Instant mouse/keyboard response
- Browser Launch: Instant (pre-installed, no download)
- Network: vibes-network for container-to-container communication
- Resolution: 1920x1080 (configurable)

**Use Cases**:
- GUI application testing
- Web browser automation (real Chromium)
- Visual workflows (Claude sees desktop state)
- Text selection & data entry
- Monitor integration (browser access to monitoring interfaces)

**Gotchas**:
- Requires Docker with vibes-network created
- VNC port 5901 (display :1) must be available
- ARM64 architecture required (or Rosetta on macOS)
- Screenshot returns base64—handle large payloads
- Browser requires `--no-sandbox --disable-dev-shm-usage` flags in container

---

## Context Engineering & Optimization

### Anthropic's Context Engineering Guide
**Official Resource**: https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents
**Publication Date**: September 2025
**Archon Source**: Not in Archon
**Relevance**: 10/10

**Core Principles**:

1. **Context is a Finite Resource**
   - **Why**: LLMs have limited "attention budget"—more tokens ≠ better performance
   - **Goal**: "Find the smallest possible set of high-signal tokens that maximize likelihood of desired outcome"
   - **Key Insight**: As context grows, models face "context rot" (harder to retrieve right information)

2. **Context Window Management Strategies**
   - **Compacting**: Summarize conversations near context window limit, restart with compressed summary
   - **Structured Notes**: Save persistent information outside context window (like basic-memory)
   - **Sub-Agent Architectures**: Assign specialized agents to focused tasks, main agent receives condensed summaries

3. **Dynamic Context Retrieval** ("Just-in-time" strategy)
   - Maintain lightweight identifiers (file paths, queries)
   - Dynamically load data using tools when needed
   - Enable "progressive disclosure" through autonomous exploration
   - Avoid pre-loading all possible context

4. **System Prompt Design** (The "Right Altitude")
   - **Too Low**: Overly rigid, prescriptive instructions → brittle behavior
   - **Too High**: Vague, ambiguous guidance → unpredictable outputs
   - **Goldilocks Zone**: Specific enough to guide, flexible enough to adapt
   - Use clear, direct language with distinct, tagged sections

5. **Tool Selection Principles**
   - Minimize tool overlap (reduces confusion)
   - Ensure tools are self-contained and clear
   - Design tools that are "token efficient" (concise I/O)

**Performance Metrics** (from Anthropic's research):
- **54% better performance** with context engineering vs prompt engineering alone
- **39% performance boost** + **84% token reduction** using memory tool + context editing
- Sub-agent architectures reduce main agent context by 60-80%

**Progressive Disclosure Implementation**:
```python
# Bad: Pre-load all context
context = load_all_files() + load_all_docs() + load_all_examples()

# Good: Load identifiers, fetch on-demand
file_index = ["src/main.py", "src/utils.py", "docs/api.md"]
# Agent uses tools to fetch specific files when needed
```

**System Prompt Structure** (from guide):
```markdown
# System Prompt Organization

## Role & Capabilities
[Clear role definition at appropriate altitude]

## Task-Specific Guidelines
[Concrete guidance for current task]

## Tool Usage Patterns
[When to use each tool, with examples]

## Output Format
[Expected structure and format]
```

**Gotchas**:
- Don't stuff entire codebase into context—use RAG/search instead
- Longer context ≠ better results (attention budget is real)
- Compaction loses nuance—balance compression vs information loss
- Sub-agents need clear handoff protocols (avoid information gaps)
- "Right altitude" is task-dependent—adjust per use case

---

### Context Engineering vs Prompt Engineering
**Resource**: https://voice.lapaas.com/anthropic-context-engineering-2025/
**Archon Source**: Not in Archon
**Relevance**: 9/10

**Key Distinctions**:

**Prompt Engineering**:
- Methods for writing and organizing LLM instructions
- Focus on instruction quality and structure
- Static optimization of prompts

**Context Engineering**:
- Strategies for curating and maintaining optimal token set during inference
- Includes ALL information in context (beyond just prompts)
- Dynamic management of context throughout execution
- Treats context as precious, finite resource

**Evolution Path**:
> "Context engineering is the natural progression of prompt engineering"

**Benefits of Context Engineering** (validated by Anthropic):
- 54% better agent performance
- Reduces "tunnel vision" and reasoning lock-in
- Prevents over-engineering by maintaining focused context
- Enables complex, long-horizon agent workflows

**Application to Vibes**:
- CLAUDE.md = Context engineering (rules + patterns in finite space)
- Pattern library = Reusable context chunks (DRY principle applied to context)
- Progressive disclosure = Load patterns on-demand, not all upfront
- 59-70% token reduction = Proof of context optimization success

---

## Technical Writing & Documentation Best Practices

### README Best Practices (Official Guidelines)
**Primary Resource**: https://www.makeareadme.com/
**Additional**: https://github.com/jehna/readme-best-practices
**Archon Source**: Not in Archon
**Relevance**: 10/10

**Essential Sections** (in order):
1. **Project Name + Subtitle** - Self-explaining, clear purpose
2. **Description** - 1-3 sentences, non-technical audience
3. **Badges** - Build status, version, coverage (if applicable)
4. **Installation** - Step-by-step, commands ready to copy
5. **Usage** - Code examples, screenshots, common workflows
6. **Contributing** - How others can help
7. **License** - Legal clarity
8. **Project Status** - Active? Maintenance mode? Archived?

**Writing Style Guidelines**:

1. **Scannable Structure**
   - Use Markdown headers (##, ###) liberally
   - Short paragraphs (2-4 sentences max)
   - Bullet points > long prose
   - Code blocks with language tags
   - Tables for comparisons

2. **Progressive Complexity**
   - **Inverted pyramid**: Most important info first
   - Quick start → detailed usage → advanced topics
   - Link to deeper docs instead of inlining everything

3. **Audience Awareness** (write for 3 audiences):
   - **End-users**: Can I use this? How do I install it?
   - **Technical users**: How does it work? What are the APIs?
   - **Contributors**: How do I build/test/contribute?

4. **Code Examples** (critical for developer docs):
   ```markdown
   # Bad: Describe what to do
   You need to configure the server by editing the config file.

   # Good: Show exactly how
   ```bash
   # Edit config file
   nano config.json

   # Add your API key
   {
     "apiKey": "your-key-here"
   }
   ```
   ```

5. **Visual Aids**
   - Screenshots for UI-heavy projects
   - GIFs for workflows (installation, usage)
   - Diagrams for architecture
   - Emojis sparingly (✅ ❌ 🚧 for status)

**Length Guidance**:
> "While READMEs can be too long and detailed, too long is better than too short"

- **Minimum**: Name, description, installation, usage (~50 lines)
- **Sweet Spot**: Add contributing, testing, troubleshooting (~150-300 lines)
- **Comprehensive**: Architecture, API reference, examples (~500+ lines)

**Tone & Voice** (2025 best practices):
- **Conversational** > Formal/corporate
- **Active voice** > Passive voice
- **Direct** > Vague ("Click here" vs "See documentation")
- **Inclusive** (avoid "just", "simply", "obviously")

**Common Mistakes to Avoid**:
- ❌ No installation instructions
- ❌ No usage examples
- ❌ Assuming prior knowledge (unexplained jargon)
- ❌ Outdated information (sync with code)
- ❌ Broken links or missing referenced files

**README Update Checklist**:
- [ ] Does title clearly state what this is?
- [ ] Can a new user install it in <5 minutes?
- [ ] Are there copy-paste ready code examples?
- [ ] Is it updated when features change?
- [ ] Are all links valid?
- [ ] Is tone consistent with project voice?

---

### Progressive Disclosure in Documentation
**Official Resource**: https://primer.github.io/design/ui-patterns/progressive-disclosure/
**Archon Source**: Not in Archon
**Relevance**: 9/10

**Core Principle**:
> "Progressive disclosure is an interaction design pattern that hides/shows information"

**When to Use**:
- Information must be truncated for layout/design
- Content is lengthy but only portions are relevant at a time
- Reducing cognitive load while maintaining information access

**Implementation Guidelines**:

1. **Maintain User Context**
   - Don't disorient users when revealing content
   - Keep initial focus point visible
   - Smooth transitions (not jarring jumps)

2. **Use Sparingly**
   - "Progressive disclosure should be used sparingly"
   - Only when necessary for design/layout
   - Avoid hiding critical information

3. **Icon Patterns** (visual cues):
   - **Chevron** (▼/▲): Toggle collapsed content
   - **Fold/Unfold**: Expand text content
   - **Ellipsis** (...): Show truncated inline text

4. **GitHub Markdown Implementation**:
   ```markdown
   <details>
   <summary>Click to expand: Advanced Configuration</summary>

   ```json
   {
     "advanced": {
       "option1": "value1",
       "option2": "value2"
     }
   }
   ```

   Additional details here...
   </details>
   ```

   **Gotchas**:
   - Blank lines needed before/after Markdown inside `<details>`
   - Otherwise Markdown won't render properly

5. **Two-Level Maximum Rule** (from context refactor):
   - **Level 1**: Main README (overview + quick reference)
   - **Level 2**: Detailed docs (linked from README)
   - **Never**: Three or more levels (causes navigation fatigue)

**Application to Vibes README**:
- **Don't inline**: Full MCP server setup guides → Link to server READMEs
- **Don't inline**: Complete pattern library → Link to `.claude/patterns/README.md`
- **Do inline**: Quick reference table of servers (name, purpose, status)
- **Do inline**: Configuration example (copy-paste ready JSON)

**Good Example** (from Vibes current README):
```markdown
## Pattern Library

See [.claude/patterns/README.md](.claude/patterns/README.md) for reusable implementation patterns.

**Quick Reference**:
| Pattern | Use Case | Benefit |
|---------|----------|---------|
| archon-workflow | Archon integration | Works with/without Archon |
| parallel-subagents | Multi-task execution | 3x speedup |

[Link to detailed pattern docs...]
```

**Bad Example** (anti-pattern):
```markdown
## Pattern Library

### Archon Workflow Pattern

[Inline entire archon-workflow.md content here - 150 lines]

### Parallel Subagents Pattern

[Inline entire parallel-subagents.md content here - 140 lines]

[This violates two-level disclosure and DRY principle]
```

---

## Pattern Library Documentation Structure

### Software Design Pattern Documentation
**Resource**: https://refactoring.guru/design-patterns
**Additional**: https://sourcemaking.com/design_patterns
**Archon Source**: Not in Archon
**Relevance**: 7/10

**Standard Pattern Documentation Format**:

1. **Pattern Name** - Clear, memorable identifier
2. **Intent** - What problem does this solve?
3. **Also Known As** - Alternative names
4. **Motivation** - Example scenario requiring the pattern
5. **Applicability** - When to use this pattern
6. **Structure** - Diagram or code structure
7. **Participants** - Classes/components involved
8. **Collaborations** - How participants work together
9. **Consequences** - Trade-offs and results
10. **Implementation** - Techniques and pitfalls
11. **Sample Code** - Working example
12. **Known Uses** - Real-world applications
13. **Related Patterns** - Similar or complementary patterns

**Vibes Pattern Library Adaptation** (from `.claude/patterns/README.md`):

**Quick Reference Table** (Level 1):
```markdown
**Need to...** | **See Pattern** | **Used By**
---|---|---
Extract secure feature names | security-validation.md | All commands
Integrate with Archon MCP | archon-workflow.md | generate-prp, execute-prp
```

**Pattern Structure** (Level 2 - in individual files):
- **Use when**: Applicability conditions
- **Key benefit**: Primary value proposition
- **Code examples**: Copy-paste ready
- **Gotchas**: Edge cases and pitfalls
- **Anti-patterns**: What NOT to do

**Organization Principles** (from Vibes patterns/README.md):
- ✅ Create pattern after 3+ occurrences (Rule of Three)
- ✅ Include complete code examples
- ✅ Document gotchas and edge cases
- ✅ Update index when adding patterns
- ❌ Don't create sub-patterns (violates two-level rule)
- ❌ Don't cross-reference patterns (circular dependencies)
- ❌ Don't duplicate pattern code in commands (defeats DRY)

---

## Anthropic Prompt Engineering (Context for PRP System)

### Prompt Engineering Overview
**Official Docs**: https://docs.claude.com/en/docs/build-with-claude/prompt-engineering/overview
**Archon Source**: 9a7d4217c64c9a0a
**Relevance**: 8/10

**Claude 4 Best Practices** (latest guidance):
1. **Be specific and direct** - Clear instructions > vague hints
2. **Use examples** - Show desired output format
3. **Structure with XML tags** - Organize complex prompts
4. **Think step-by-step** - Break complex tasks into steps
5. **Provide context** - Give Claude relevant background

**System Prompt Design** (from Anthropic engineering blog):
- Organize into distinct, tagged sections
- Use Markdown headers for structure
- Clear role definition at "right altitude"
- Task-specific guidelines (concrete, not abstract)

**Application to Vibes**:
- CLAUDE.md = System prompt for all interactions
- Commands = Structured prompts with clear tasks
- Patterns = Reusable prompt components
- PRPs = Context-engineered prompts for implementation

---

## GitHub Markdown & Formatting

### GitHub Flavored Markdown Spec
**Official Spec**: https://github.github.com/gfm/
**Cheatsheet**: https://github.com/adam-p/markdown-here/wiki/markdown-cheatsheet
**Archon Source**: Not in Archon
**Relevance**: 7/10

**Key Formatting for READMEs**:

**Tables** (for MCP server listing):
```markdown
| Server | Purpose | Status | Connection |
|--------|---------|--------|------------|
| archon | Task/knowledge management | ✅ Active | npx mcp-remote |
| vibesbox | Shell + GUI automation | ✅ Active | docker exec |
```

**Code Blocks** (with language tags):
```markdown
```json
{
  "mcpServers": {
    "archon": {
      "command": "npx",
      "args": ["mcp-remote", "http://localhost:8051/mcp"]
    }
  }
}
```​
```

**Badges** (status indicators):
```markdown
[![Ask DeepWiki](https://deepwiki.com/badge.svg)](https://deepwiki.com/jonhill90/vibes)
```

**Relative Links** (for internal docs):
```markdown
[Pattern Library](.claude/patterns/README.md)
[Archon Workflow](.claude/patterns/archon-workflow.md)
```

**Collapsible Sections** (progressive disclosure):
```markdown
<details>
<summary>Advanced Configuration</summary>

Content here (needs blank lines before/after Markdown)

</details>
```

---

## Additional Resources

### Tutorials with Code

1. **Context Engineering Intro (coleam00)**
   - **URL**: https://github.com/coleam00/context-engineering-intro
   - **Format**: GitHub repo with examples
   - **Quality**: 10/10
   - **What makes it useful**: Origin of PRP methodology, comprehensive examples, CLAUDE.md patterns, validation loops
   - **Archon Source**: b8565aff9938938b

2. **Anthropic Claude Code Best Practices**
   - **URL**: https://www.anthropic.com/engineering/claude-code-best-practices
   - **Format**: Engineering blog post
   - **Quality**: 10/10
   - **What makes it useful**: Official guidance from Anthropic on context engineering, tool design, agent workflows

3. **Docker MCP Gateway Tutorial**
   - **URL**: https://github.com/theNetworkChuck/docker-mcp-tutorial
   - **Format**: GitHub tutorial repo
   - **Quality**: 8/10
   - **What makes it useful**: Step-by-step MCP server building with Docker, practical examples

### API References

1. **Model Context Protocol Specification**
   - **URL**: https://modelcontextprotocol.io/specification/latest
   - **Coverage**: Complete protocol specification, JSON-RPC methods, transport layer, security
   - **Examples**: Yes, extensive examples for clients and servers

2. **Anthropic Prompt Engineering Interactive Tutorial**
   - **URL**: https://github.com/anthropics/prompt-eng-interactive-tutorial
   - **Coverage**: Hands-on prompt engineering techniques, Claude-specific optimizations
   - **Examples**: Yes, interactive exercises with solutions

### Community Resources

1. **MCP Directory (mcpdb.org)**
   - **URL**: https://mcpdb.org/
   - **Type**: Community-curated MCP server directory
   - **Why included**: Discover existing MCP servers, avoid reinventing the wheel

2. **MCP Market**
   - **URL**: https://mcpmarket.com/
   - **Type**: MCP server marketplace
   - **Why included**: Browse 200+ MCP servers, find integrations for common tools

3. **Awesome MCP Servers**
   - **URL**: https://mcpservers.org/
   - **Type**: Curated list of MCP servers
   - **Why included**: Quality-filtered server recommendations, categorized by use case

---

## Documentation Gaps

### Not Found in Archon or Web

**Vibesbox Comprehensive Documentation**:
- **Gap**: Public documentation for vibesbox MCP server
- **Current State**: Only local README exists (`/mcp/mcp-vibesbox-server/README.md`)
- **Recommendation**: Extract key features from local README, consider publishing to GitHub

**Pattern Library Theory**:
- **Gap**: Academic/formal documentation on "pattern libraries for AI context"
- **Current State**: Emerging practice, mostly undocumented
- **Recommendation**: Reference existing patterns, cite Vibes as implementation example

### Outdated or Incomplete

**MCP Protocol Evolution**:
- **Issue**: Specification updated to 2025-06-18, some community docs reference older versions
- **Impact**: Configuration examples may use deprecated transport methods
- **Suggested Alternative**: Always reference official spec at modelcontextprotocol.io

**Basic Memory Setup Variations**:
- **Issue**: Multiple installation methods (uv, npx, docker) with varying documentation quality
- **Impact**: Configuration can be confusing across different AI assistants
- **Suggested Alternative**: Use Docker approach for consistency (matches Vibes pattern)

---

## Quick Reference URLs

For easy copy-paste into PRP:

```yaml
MCP Documentation:
  - MCP Protocol Spec: https://modelcontextprotocol.io/specification/2025-06-18/index
  - MCP Examples: https://modelcontextprotocol.io/examples
  - MCP SDK Docs: https://modelcontextprotocol.io/docs/sdk

MCP Server Implementations:
  - Archon MCP: https://github.com/coleam00/Archon
  - Docker MCP Gateway: https://docs.docker.com/ai/mcp-gateway/
  - Basic Memory: https://github.com/basicmachines-co/basic-memory
  - Vibesbox: /mcp/mcp-vibesbox-server/README.md (local)

Context Engineering:
  - Anthropic Context Engineering: https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents
  - Context Engineering Intro: https://github.com/coleam00/context-engineering-intro
  - Prompt Engineering Overview: https://docs.claude.com/en/docs/build-with-claude/prompt-engineering/overview

Technical Writing:
  - Make a README: https://www.makeareadme.com/
  - README Best Practices: https://github.com/jehna/readme-best-practices
  - Progressive Disclosure: https://primer.github.io/design/ui-patterns/progressive-disclosure/

Markdown & Formatting:
  - GitHub Flavored Markdown: https://github.github.com/gfm/
  - Markdown Cheatsheet: https://github.com/adam-p/markdown-here/wiki/markdown-cheatsheet
  - Details/Summary in Markdown: https://gist.github.com/scmx/eca72d44afee0113ceb0349dd54a84a2

Pattern Libraries:
  - Design Patterns: https://refactoring.guru/design-patterns
  - Software Patterns: https://sourcemaking.com/design_patterns
  - Local Patterns: .claude/patterns/README.md
```

---

## Recommendations for PRP Assembly

When generating the PRP, the Assembler should:

1. **Include URLs in "Documentation & References" Section**
   - All MCP server docs (4 servers)
   - Context engineering resources (Anthropic + coleam00)
   - Technical writing guides (makeareadme + GitHub primer)
   - Local pattern library reference

2. **Extract Code Examples into PRP Context**
   - MCP configuration JSON (all 4 servers)
   - Server capability patterns (tools, resources)
   - Progressive disclosure implementation (`<details>` tags)
   - Table formatting for server listing

3. **Highlight Gotchas in "Known Gotchas" Section**
   - MCP server transport types (STDIO vs HTTP)
   - Security considerations (user approval, rate limiting)
   - Context window management (attention budget, context rot)
   - Progressive disclosure blank line requirement
   - Two-level documentation depth limit

4. **Reference Specific Sections in Implementation Tasks**
   - "See MCP Protocol Spec §2.1 for transport layer details: [URL]"
   - "Follow Anthropic context engineering guide on 'right altitude': [URL]"
   - "Use progressive disclosure pattern from GitHub Primer: [URL]"
   - "Apply README structure from makeareadme.com: [URL]"

5. **Note Gaps for Implementation Compensation**
   - Vibesbox: Extract from local README (no public docs)
   - MCP_DOCKER: Infer gateway orchestration purpose
   - Pattern library: Use Vibes implementation as reference
   - Basic-memory: Verify Docker config matches actual setup

---

## Archon Ingestion Candidates

**Documentation NOT in Archon but should be**:

1. **Anthropic Context Engineering Guide** (https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents)
   - **Why valuable**: Core principles for AI agent development, token optimization strategies, 54% performance improvement metrics
   - **Use case**: Future PRPs involving context optimization, agent architecture

2. **Docker MCP Gateway Docs** (https://docs.docker.com/ai/mcp-gateway/)
   - **Why valuable**: Official Docker MCP integration, security patterns, enterprise deployment
   - **Use case**: PRPs involving containerized MCP servers, production deployments

3. **Make a README Guide** (https://www.makeareadme.com/)
   - **Why valuable**: Technical writing best practices, README structure patterns
   - **Use case**: Documentation PRPs, project setup guides

4. **GitHub Progressive Disclosure Primer** (https://primer.github.io/design/ui-patterns/progressive-disclosure/)
   - **Why valuable**: UX patterns for documentation, information hierarchy
   - **Use case**: UI documentation, pattern library organization

5. **Basic Memory MCP Docs** (https://github.com/basicmachines-co/basic-memory)
   - **Why valuable**: Persistent memory patterns for AI agents, knowledge graph implementation
   - **Use case**: Memory management PRPs, knowledge base features

**Benefits of Ingestion**:
- Faster PRP research (no web search needed)
- Consistent documentation versions
- Offline access to critical resources
- Semantic search across all documentation sources

---

## Summary Statistics

**Documentation Sources Reviewed**: 15+
**Official MCP Documentation**: 3 sources (Protocol, Gateway, Examples)
**MCP Server Implementations**: 4 (Archon, Docker Gateway, Basic Memory, Vibesbox)
**Technical Writing Resources**: 4 (makeareadme, GitHub best practices, progressive disclosure, GFM spec)
**Context Engineering Resources**: 3 (Anthropic guide, coleam00 intro, prompt engineering)
**Archon Sources Used**: 3 (d60a71d62eb201d5, b8565aff9938938b, 9a7d4217c64c9a0a)
**Web Sources**: 12 (official docs, best practices, specifications)

**Quality Assessment**:
- ✅ All 4 MCP servers documented with official sources
- ✅ Context engineering principles from Anthropic (authoritative)
- ✅ Technical writing best practices from multiple sources
- ✅ Progressive disclosure patterns with implementation examples
- ✅ Local codebase references validated (vibesbox README exists)
- ✅ Quick reference URLs ready for PRP integration
- ✅ Gotchas extracted from official documentation
- ✅ Code examples validated and ready to use

**Confidence Level**: 9/10 (comprehensive coverage, authoritative sources, actionable examples)
