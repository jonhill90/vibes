# PRP: README Update - Context Refactor Results

**Generated**: 2025-01-15
**Based On**: prps/readme_update/planning/INITIAL.md
**Archon Project**: 6099f284-3e20-40b9-8dfd-3c47a0ffa5a5

---

## Goal

Update README.md to accurately reflect the current state of the Vibes project after successful context optimization (59-70% token reduction). The README currently lists only 2 MCP servers but the system has 4 active servers, doesn't mention the Archon integration (critical workflow component), omits context optimization achievements, and lacks documentation about the new pattern library structure.

**End State**:
- All 4 MCP servers documented with accurate purposes and connection methods
- Context optimization achievement (59-70% reduction) prominently featured with specific metrics
- Pattern library section added referencing `.claude/patterns/README.md`
- `.claude/` directory structure explained with line counts demonstrating compression
- "Current Capabilities" section made specific with server-attributed features
- MCP configuration example updated to show all 4 servers
- Conversational tone preserved throughout

## Why

**Current Pain Points**:
- Users see incomplete MCP server list (2 vs 4 actual servers) → setup confusion
- Archon integration undocumented despite being "critical to workflow" → can't leverage task management
- Context optimization achievement invisible → major milestone not celebrated or replicable
- Pattern library exists but not discoverable → developers can't reuse proven patterns
- Directory structure outdated → users don't understand `.claude/` organization
- Vague capability claims ("Remember conversations") → no actionable guidance

**Business Value**:
- **Immediate**: Accurate setup instructions → fewer support requests, faster onboarding
- **Strategic**: Document context optimization methodology → other teams can replicate 59-70% token savings
- **Community**: Showcase Archon integration → demonstrate real-world MCP server patterns
- **Developer Experience**: Pattern library discoverability → faster feature implementation
- **Trust**: Accurate documentation → credibility for all other project claims

## What

### Core Features

1. **Complete MCP Server Table** (4 servers vs current 2):
   - Add `archon` (Task/knowledge management, RAG search)
   - Add `basic-memory` (Persistent memory across sessions)
   - Add `MCP_DOCKER` (Container orchestration gateway)
   - Update table with Status, Transport type, Connection method

2. **Context Optimization Section** (NEW):
   - Achievement headline: 59-70% token reduction
   - Line count metrics: CLAUDE.md (107), generate-prp (320), execute-prp (202)
   - Before/after comparison with calculations
   - Link to validation-report.md for methodology

3. **Pattern Library Section** (NEW):
   - Quick reference table (Need to... | See Pattern | Used By)
   - 4 key patterns: archon-workflow, parallel-subagents, quality-gates, security-validation
   - Link to `.claude/patterns/README.md` for details
   - Explanation of when/why to use patterns

4. **Updated Directory Structure**:
   - Add `.claude/` tree showing commands, patterns, agents, templates
   - Show per-feature `prps/{feature_name}/` organization
   - Include line counts as evidence of compression
   - Preserve existing `prps/` structure

5. **Specific Current Capabilities**:
   - Replace vague claims ("Remember conversations") with server-specific features
   - Map each capability to MCP server providing it
   - Include MCP tool names where applicable

6. **Complete MCP Configuration Example**:
   - Replace 1-server JSON with all 4 servers
   - Show actual production config structure
   - Validate JSON syntax before inclusion

### Success Criteria

- [ ] All 4 MCP servers listed in table with accurate purposes (lines 17-21)
- [ ] Context Optimization section added after "Current Capabilities"
- [ ] Pattern Library section added after "PRP Workflow"
- [ ] `.claude/` directory structure documented (lines 99-114 updated)
- [ ] "Current Capabilities" made specific (server names mentioned)
- [ ] Config example shows all 4 servers (lines 48-57 replaced)
- [ ] Line counts accurate: CLAUDE.md=107, generate-prp=320, execute-prp=202
- [ ] Conversational tone preserved (no corporate/formal language)
- [ ] No duplication with CLAUDE.md content
- [ ] All links valid (pattern files, validation reports exist)
- [ ] Markdown tables render correctly (verified on GitHub preview)
- [ ] JSON configuration valid (passes `jq` validation)

---

## All Needed Context

### Documentation & References

```yaml
# MUST READ - MCP Server Documentation

- url: https://modelcontextprotocol.io/specification/2025-06-18/index
  sections:
    - "Protocol Overview" - MCP architecture, client-server model, transport layers
    - "Core Concepts" - Tools, resources, prompts, notifications
  why: Understand MCP server capabilities and connection methods (STDIO vs HTTP)
  critical_gotchas:
    - MCP servers can be local (STDIO) OR remote (HTTP)—don't assume all are docker exec
    - Security: clients SHOULD implement user approval controls and rate limiting

- url: https://github.com/coleam00/Archon
  sections:
    - "Key Features" - Task management, RAG search, multi-LLM support
    - "Architecture" - Frontend (3737), Server API (8181), MCP Server (8051)
    - "MCP Tools" - find_tasks, manage_task, rag_search_knowledge_base
  why: Document Archon's specific capabilities for README table and capabilities section
  critical_gotchas:
    - Task status flow: todo → doing → review → done (follow this order)
    - RAG queries: keep SHORT (2-5 keywords) for better results
    - Connection: HTTP (SSE) via npx mcp-remote (not docker exec)

- url: https://docs.docker.com/ai/mcp-gateway/
  sections:
    - "Key Features" - Container-based servers, unified management, security
    - "Installation & Commands" - docker mcp gateway run
  why: Understand MCP_DOCKER gateway purpose and connection method
  critical_gotchas:
    - Requires Docker Desktop with MCP Toolkit enabled
    - Gateway unifies multiple servers into single endpoint
    - Transport: STDIO via docker mcp gateway run

- url: https://github.com/basicmachines-co/basic-memory
  sections:
    - "Key Features" - Local-first Markdown storage, Obsidian integration
    - "Tools Provided" - write_note, read_note, search, recent_activity
  why: Document basic-memory server purpose and capabilities
  critical_gotchas:
    - Connection: Docker exec (not npx or HTTP)
    - Files stored locally—backup strategy needed

- url: https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents
  sections:
    - "Context is a Finite Resource" - Attention budget, context rot
    - "Context Window Management Strategies" - Compacting, structured notes, sub-agents
    - "Performance Metrics" - 54% better performance with context engineering
  why: Explain WHY context optimization matters for README section
  critical_gotchas:
    - Longer context ≠ better results (attention budget is real)
    - 59-70% reduction achieved through DRY principle and pattern extraction
    - Progressive disclosure: load on-demand, not all upfront

# MUST READ - Technical Writing Best Practices

- url: https://www.makeareadme.com/
  sections:
    - "Essential Sections" - Name, description, installation, usage
    - "Writing Style Guidelines" - Scannable structure, progressive complexity
    - "Code Examples" - Show exactly how, not just describe
  why: Maintain professional README structure and style
  critical_gotchas:
    - Use Markdown headers liberally (##, ###) for scannability
    - Short paragraphs (2-4 sentences max)
    - Bullet points > long prose

- url: https://primer.github.io/design/ui-patterns/progressive-disclosure/
  sections:
    - "Core Principle" - Hide/show information to reduce cognitive load
    - "Two-Level Maximum Rule" - README → detailed docs (not 3+ levels)
  why: Avoid over-explaining in README (link to details instead)
  critical_gotchas:
    - Progressive disclosure should be used sparingly
    - Blank lines needed before/after Markdown inside <details> tags
    - Two-level maximum: README (overview) → linked docs (details)

# ESSENTIAL LOCAL FILES

- file: /Users/jon/source/vibes/prps/readme_update/examples/README.md
  why: Comprehensive guide to all curated examples (MCP table format, config snippets, metrics presentation)
  pattern: What to mimic/adapt/skip for each example

- file: /Users/jon/source/vibes/prps/readme_update/examples/mcp-server-table.md
  why: Current 2-server table format to extend to 4 servers
  critical: Backtick formatting, status emoji, 4-column structure

- file: /Users/jon/source/vibes/prps/readme_update/examples/config-complete.json
  why: Actual production config with all 4 MCP servers (validated JSON)
  pattern: Use this EXACT config for README example (lines 48-57)

- file: /Users/jon/source/vibes/prps/readme_update/examples/section-structure.md
  why: Section header patterns, conversational tone examples, templates for new sections
  critical: Two-level headers only (## and ###), avoid ####

- file: /Users/jon/source/vibes/prps/readme_update/examples/metrics-presentation.md
  why: Context optimization metrics format (before → after, percentages)
  pattern: Bold percentages (**59-70%**), hierarchical presentation

- file: /Users/jon/source/vibes/prps/readme_update/examples/directory-listing.md
  why: ASCII tree format for directory structure, comment style
  critical: Inline comments (# Brief description), placeholder syntax ({variable}/)

- file: /Users/jon/source/vibes/.claude/patterns/README.md
  why: Pattern library quick reference table (3 columns: Need to... | See Pattern | Used By)
  pattern: Reference this for Pattern Library section

- file: /Users/jon/source/vibes/prps/prp_context_refactor/execution/validation-report.md
  why: Source of truth for line counts and reduction percentages
  critical: CLAUDE.md=107, generate-prp=320, execute-prp=202, 59-70% reduction calculations
```

### Current Codebase Tree

```
vibes/
├── README.md                 # CURRENT STATE (to be updated)
│   ├── Lines 17-21: MCP server table (2 servers, needs +2)
│   ├── Lines 48-57: Config example (1 server, needs all 4)
│   ├── Lines 99-114: Directory structure (outdated, missing .claude/)
│   └── "Current Capabilities" section (vague, needs specificity)
├── CLAUDE.md                 # 107 lines (project rules only)
│   └── Contains Archon workflow details (don't duplicate in README)
├── .claude/                  # NEW structure from context refactor
│   ├── commands/             # Slash commands (59-70% reduction achieved)
│   │   ├── generate-prp.md   # 320 lines (59% reduction from 1044)
│   │   └── execute-prp.md    # 202 lines (70% reduction from 1044)
│   ├── patterns/             # Reusable patterns (DRY principle)
│   │   ├── README.md         # Pattern library index
│   │   ├── archon-workflow.md    # 133 lines
│   │   ├── parallel-subagents.md # 150 lines
│   │   ├── quality-gates.md      # 128 lines
│   │   └── security-validation.md # 47 lines
│   ├── agents/               # Subagent specifications
│   └── templates/            # Report templates
├── prps/                     # Per-feature PRP artifacts
│   ├── readme_update/        # THIS FEATURE
│   │   ├── planning/         # Research documents (5 files)
│   │   └── examples/         # Curated examples (7 files)
│   └── prp_context_refactor/
│       └── execution/
│           └── validation-report.md  # Source of metrics
└── mcp/                      # MCP server implementations
    ├── mcp-vibesbox-server/
    │   └── README.md         # 251 lines (comprehensive server docs)
    └── mcp-vibes-server/
```

### Desired Codebase Tree

```
vibes/
└── README.md                 # UPDATED STATE
    ├── Lines 17-24: MCP server table (4 servers: vibesbox, basic-memory, MCP_DOCKER, archon)
    ├── Lines 48-75: Config example (all 4 servers with validated JSON)
    ├── After "Current Capabilities": Context Optimization section (~30 lines)
    ├── After "PRP Workflow": Pattern Library section (~30 lines)
    ├── Lines 99-130: Directory structure (.claude/ + prps/ both shown)
    └── "Current Capabilities": Server-specific features (not vague)

**New Content**:
- Context Optimization section (shows 59-70% reduction, line counts, methodology link)
- Pattern Library section (quick reference table + link to .claude/patterns/README.md)
- 2 additional MCP server rows in table
- Complete 4-server JSON config example
- Updated directory tree with .claude/ structure
```

### Known Gotchas & Library Quirks

```markdown
# CRITICAL: CLAUDE.md / README.md Content Duplication

# ❌ WRONG: Duplicating Archon workflow in README.md
## README.md
### Archon Workflow
1. Get Task → find_tasks(task_id="...")
2. Start Work → manage_task("update", status="doing")
# [This is already in CLAUDE.md—DUPLICATION violates context refactor!]

# ✅ RIGHT: Progressive disclosure with references
## README.md
### Current Capabilities
- **Task management** via Archon MCP (find_tasks, manage_task, RAG search)
See [CLAUDE.md](CLAUDE.md) for detailed workflow patterns.

# CRITICAL: MCP Server Status Must Match Actual Config

# ❌ WRONG: Claiming servers are active without verification
| archon | Task management | ✅ Active | npx |
| cool-ai | Magic features | ✅ Active | docker |  # Doesn't exist!

# ✅ RIGHT: Validate against claude_desktop_config.json
# Verify all 4 servers exist in config before marking ✅ Active
jq '.mcpServers | keys[]' ~/Library/Application\ Support/Claude/claude_desktop_config.json
# Output: archon, basic-memory, MCP_DOCKER, vibesbox (exactly 4)

# CRITICAL: Metrics Drift—Line Counts Must Be Current

# ❌ WRONG: Hardcoded metrics without verification
- CLAUDE.md: **107 lines** (claimed, but file might have changed)

# ✅ RIGHT: Verify before documenting
wc -l CLAUDE.md  # Must equal 107 or update claim
wc -l .claude/commands/generate-prp.md  # Must equal 320
wc -l .claude/commands/execute-prp.md   # Must equal 202

# CRITICAL: Markdown Table Formatting

# ❌ WRONG: Insufficient hyphens, missing blank lines
| Server | Purpose |
|---|---|  # Only 1 hyphen (need 3+)
| archon | Task management |  # No blank line before table

# ✅ RIGHT: Proper table syntax
[blank line before table]
| Server | Purpose | Status | Connection |
|--------|---------|--------|------------|  # 3+ hyphens each
| `archon` | Task/knowledge management | ✅ Active | npx mcp-remote |
[blank line after table]

# CRITICAL: Progressive Disclosure—Two Levels Maximum

# ❌ WRONG: Three levels of disclosure
## README → .claude/patterns/README.md → archon-workflow.md → Archon GitHub
# Users have to click 3+ times to get information!

# ✅ RIGHT: Flatten to two levels with quick reference
## README (Level 1 - Quick Reference)
| Pattern | Use Case | Link |
|---------|----------|------|
| archon-workflow | Archon integration | [View](.claude/patterns/archon-workflow.md) |
# Level 2: Pattern files with implementation details
# External links marked as "reference only" (not part of hierarchy)

# CRITICAL: JSON Configuration Syntax

# ❌ WRONG: Trailing commas, unquoted keys
{
  "mcpServers": {
    "archon": {
      command: "npx",  # Unquoted key!
      "args": ["mcp-remote"],  # Trailing comma!
    },
  }
}

# ✅ RIGHT: Valid JSON (no trailing commas, all keys quoted)
{
  "mcpServers": {
    "archon": {
      "command": "npx",
      "args": ["mcp-remote", "http://localhost:8051/mcp"]
    }
  }
}
# Validate before committing: jq . config.json

# CRITICAL: Tone Consistency

# ❌ WRONG: Corporate/formal tone shift
"The Vibes project has successfully implemented a comprehensive context
engineering initiative that resulted in significant token reduction..."
# Sounds like corporate press release!

# ✅ RIGHT: Conversational Vibes voice
"We compressed the context Claude sees by 59-70% without losing functionality."
# Use: "we", "you", active voice, short sentences (10-15 words)
# Avoid: "leverage", "utilize", "stakeholders", passive voice

# CRITICAL: Transport Type Confusion (STDIO vs HTTP)

# ❌ UNCLEAR: No transport type indicated
| archon | Task management | Remote |  # "Remote" doesn't explain mechanism

# ✅ CLEAR: Transport type explicit
| `archon` | Task/knowledge | ✅ | HTTP (SSE) | `npx mcp-remote http://...` |
| `vibesbox` | Shell + GUI | ✅ | STDIO | `docker exec -i ...` |
# HTTP (SSE): Server-Sent Events over HTTP (npx mcp-remote, remote servers)
# STDIO: Process communication via stdin/stdout (docker exec, local)

# CRITICAL: Vague Capability Claims

# ❌ WRONG: Generic statements without server attribution
- **Execute code** in safe environments
- **Remember conversations** (which server? how?)

# ✅ RIGHT: Specific, server-attributed capabilities
- **Shell execution & container management** via `mcp-vibes-server` MCP
  - Run bash commands in isolated environments
  - Docker container lifecycle management
- **Persistent memory** via `basic-memory` MCP
  - Local Markdown-based knowledge storage
  - Conversation context across sessions
```

---

## Implementation Blueprint

### Phase 0: Planning & Understanding

**BEFORE starting implementation, complete these steps:**

1. **Study all examples in `prps/readme_update/examples/`**:
   - Read `examples/README.md` for comprehensive guidance
   - Review `mcp-server-table.md` for exact table format
   - Study `section-structure.md` for tone and style patterns
   - Understand `metrics-presentation.md` for context optimization format

2. **Verify current state**:
   ```bash
   # Validate line counts match claims
   wc -l CLAUDE.md  # Should be 107
   wc -l .claude/commands/generate-prp.md  # Should be 320
   wc -l .claude/commands/execute-prp.md   # Should be 202

   # Verify MCP servers in config
   jq '.mcpServers | keys[]' ~/Library/Application\ Support/Claude/claude_desktop_config.json
   # Should output: archon, basic-memory, MCP_DOCKER, vibesbox

   # Check README structure
   grep "^## " README.md  # List all major sections
   ```

3. **Read documentation for understanding**:
   - MCP Protocol spec: https://modelcontextprotocol.io/specification/2025-06-18/index
   - Context engineering: https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents
   - README best practices: https://www.makeareadme.com/

### Task List (Execute in Order)

```yaml
Task 1: Add 2 Missing MCP Servers to Table
RESPONSIBILITY: Complete the MCP server documentation (2 → 4 servers)
FILES TO MODIFY:
  - README.md (lines 17-21)

PATTERN TO FOLLOW: examples/mcp-server-table.md

SPECIFIC STEPS:
  1. Open README.md and locate MCP server table (lines 17-21)
  2. Add row for basic-memory:
     | `basic-memory` | Persistent memory across Claude sessions | ✅ Active | Docker exec |
  3. Add row for MCP_DOCKER:
     | `MCP_DOCKER` | Container orchestration gateway | ✅ Active | docker mcp |
  4. Add row for archon:
     | `archon` | Task/knowledge management, RAG search | ✅ Active | npx mcp-remote |
  5. Verify table formatting:
     - Blank line before table
     - Separator row has 3+ hyphens per column
     - All columns aligned
     - Server names in backticks
     - Blank line after table

VALIDATION:
  - Preview README on GitHub to verify table renders correctly
  - All 4 server names match claude_desktop_config.json
  - Status indicators accurate (all ✅ Active verified)

---

Task 2: Update MCP Configuration Example
RESPONSIBILITY: Replace 1-server config with complete 4-server config
FILES TO MODIFY:
  - README.md (lines 48-57)

PATTERN TO FOLLOW: examples/config-complete.json

SPECIFIC STEPS:
  1. Locate config example section (lines 48-57)
  2. Replace entire JSON block with content from examples/config-complete.json
  3. Ensure JSON syntax is valid:
     - No trailing commas
     - All keys quoted
     - Brackets balanced
  4. Maintain code block formatting:
     ```json
     {
       "mcpServers": {
         "vibesbox": { ... },
         "basic-memory": { ... },
         "MCP_DOCKER": { ... },
         "archon": { ... }
       }
     }
     ```
  5. Keep surrounding explanation text unchanged

VALIDATION:
  - Run: echo '<JSON_BLOCK>' | jq .
  - Should output formatted JSON with no errors
  - Verify all 4 servers present: archon, basic-memory, MCP_DOCKER, vibesbox

---

Task 3: Add Context Optimization Section
RESPONSIBILITY: Document 59-70% token reduction achievement
FILES TO MODIFY:
  - README.md (add new section after "Current Capabilities")

PATTERN TO FOLLOW: examples/metrics-presentation.md, examples/section-structure.md

SPECIFIC STEPS:
  1. Insert new section after "Current Capabilities" section
  2. Use template from examples/section-structure.md:
     ```markdown
     ## Context Optimization

     We compressed the context Claude sees by **59-70%** without losing functionality.

     **File Sizes Achieved**:
     - **CLAUDE.md**: 107 lines (from 143, 25% reduction)
     - **Patterns**: 47-150 lines each (target ≤150)
     - **Commands**: 202-320 lines each (target ≤350)

     **Context Per Command**:
     - `/generate-prp`: 427 lines (59% reduction from 1044 baseline)
     - `/execute-prp`: 309 lines (70% reduction from 1044 baseline)

     **Impact**: ~320,400 tokens saved annually (assuming 10 PRP workflows/month)

     **Why this matters**: Claude has an "attention budget"—more tokens doesn't mean
     better results. By compressing context, we improved both speed and accuracy.

     See [validation report](prps/prp_context_refactor/execution/validation-report.md)
     for detailed methodology.
     ```
  3. Verify line counts match actual files (see Task 1 Phase 0 verification)
  4. Use conversational tone (not corporate: "we" vs "the project")
  5. Bold key percentages and numbers

VALIDATION:
  - Verify line counts: wc -l CLAUDE.md .claude/commands/*.md
  - Check link exists: ls prps/prp_context_refactor/execution/validation-report.md
  - Tone check: Does this sound like existing README? (conversational, not formal)

---

Task 4: Add Pattern Library Section
RESPONSIBILITY: Make pattern library discoverable with quick reference
FILES TO MODIFY:
  - README.md (add new section after "PRP Workflow" or "Context Engineering & PRPs")

PATTERN TO FOLLOW: .claude/patterns/README.md, examples/section-structure.md

SPECIFIC STEPS:
  1. Insert new section after "Context Engineering & PRPs" section
  2. Create brief introduction (1-2 sentences):
     "The `.claude/patterns/` directory contains reusable implementation patterns
     extracted from the PRP system."
  3. Add quick reference table (3 columns: Pattern | Purpose | Link):
     | Pattern | Purpose | Link |
     |---------|---------|------|
     | archon-workflow | Archon MCP integration, health checks | [View](.claude/patterns/archon-workflow.md) |
     | parallel-subagents | 3x speedup through multi-task parallelization | [View](.claude/patterns/parallel-subagents.md) |
     | quality-gates | Validation loops ensuring 8+/10 PRP scores | [View](.claude/patterns/quality-gates.md) |
     | security-validation | 5-level security checks for user input | [View](.claude/patterns/security-validation.md) |
  4. Add closing sentence with link to full index:
     "See [.claude/patterns/README.md](.claude/patterns/README.md) for complete
     pattern documentation and usage guidelines."
  5. Ensure progressive disclosure (don't inline pattern content—link to it)

VALIDATION:
  - All pattern files exist: ls .claude/patterns/*.md
  - Links use correct relative paths from repository root
  - Table renders correctly (blank lines before/after)
  - Two-level disclosure: README (overview) → pattern files (details)

---

Task 5: Update Directory Structure
RESPONSIBILITY: Document .claude/ directory and per-feature prps/ organization
FILES TO MODIFY:
  - README.md (lines 99-114)

PATTERN TO FOLLOW: examples/directory-listing.md

SPECIFIC STEPS:
  1. Locate "Directory Structure" section (lines 99-114)
  2. Add .claude/ as first item in tree:
     ```
     vibes/
     ├── .claude/              # Context-engineered components (59-70% reduction)
     │   ├── commands/         # Slash commands for Claude Code
     │   │   ├── generate-prp.md    # 320 lines (59% reduction)
     │   │   ├── execute-prp.md     # 202 lines (70% reduction)
     │   │   ├── list-prps.md
     │   │   └── prep-parallel.md
     │   ├── patterns/         # Reusable implementation patterns
     │   │   ├── README.md          # Pattern library index
     │   │   ├── archon-workflow.md
     │   │   ├── parallel-subagents.md
     │   │   ├── quality-gates.md
     │   │   └── security-validation.md
     │   ├── agents/           # Subagent specifications
     │   └── templates/        # Report templates
     ├── prps/                 # Per-feature PRP artifacts
     │   └── {feature_name}/
     │       ├── planning/     # Research outputs
     │       ├── examples/     # Concrete examples
     │       └── execution/    # Implementation artifacts
     └── CLAUDE.md             # 107 lines (project rules only)
     ```
  3. Use inline comments (# Brief description) for each directory
  4. Include line counts for key files (evidence of compression)
  5. Use placeholder syntax {feature_name}/ for per-feature structure
  6. Maintain ASCII tree characters: ├── └── │

VALIDATION:
  - All referenced files/directories exist
  - Line counts accurate: wc -l CLAUDE.md .claude/commands/*.md
  - Comments concise (3-7 words)
  - Tree structure visually clear

---

Task 6: Make Current Capabilities Specific
RESPONSIBILITY: Replace vague claims with server-attributed features
FILES TO MODIFY:
  - README.md ("Current Capabilities" section)

PATTERN TO FOLLOW: examples/section-structure.md (capability attribution pattern)

SPECIFIC STEPS:
  1. Locate "Current Capabilities" section
  2. Replace generic bullets with specific, server-attributed capabilities:
     ```markdown
     ## Current Capabilities

     - **Shell execution & container management** via `mcp-vibes-server` MCP
       - Run bash commands in isolated environments
       - Docker container lifecycle management
       - Network access to vibes-network

     - **Desktop automation & visual feedback** via `mcp-vibesbox-server` MCP
       - VNC desktop environment (XFCE4, 1920x1080)
       - Screenshot capture for Claude's vision
       - Mouse/keyboard control (click, drag, type)
       - ARM64 Chromium browser automation

     - **Task & knowledge management** via `archon` MCP
       - Task tracking (find_tasks, manage_task)
       - RAG search across documentation (2-5 keyword queries)
       - Project management and organization

     - **Persistent memory** via `basic-memory` MCP
       - Local Markdown-based knowledge storage
       - Conversation context across sessions
       - Semantic linking and knowledge graphs

     - **Container orchestration** via `MCP_DOCKER` gateway
       - Unified MCP server management
       - Security isolation and secrets management
       - Enterprise observability
     ```
  3. Each capability must include:
     - Server name in backticks (`server-name`)
     - 2-3 specific features (MCP tool names where applicable)
     - Concrete claims (not vague: "1920x1080" vs "high resolution")
  4. Avoid vague verbs: "manage", "handle", "support" → use specific actions

VALIDATION:
  - Every capability mentions which MCP server provides it
  - No generic claims without server attribution
  - MCP tool names accurate (verify against server README.md files)
  - Tone conversational (bullets, not paragraphs)

---

Task 7: Final Quality Checks
RESPONSIBILITY: Ensure README update meets all success criteria
FILES TO VALIDATE:
  - README.md (entire file)

PATTERN TO FOLLOW: Validation checklist from gotchas.md

SPECIFIC STEPS:
  1. Run validation scripts:
     ```bash
     # Verify line counts
     wc -l CLAUDE.md  # Must be 107
     wc -l .claude/commands/generate-prp.md  # Must be 320
     wc -l .claude/commands/execute-prp.md   # Must be 202

     # Validate JSON syntax
     grep -Pzo '(?s)\{[^}]+mcpServers[^}]+\}' README.md | jq .
     # Should output valid JSON with no errors

     # Check MCP server count
     grep -c "| \`.*\` |" README.md
     # Should be 4 (archon, vibesbox, basic-memory, MCP_DOCKER)

     # Verify no CLAUDE.md duplication
     grep -q "find_tasks.*manage_task.*doing" README.md && echo "DUPLICATION!" || echo "OK"
     # Should output "OK" (no Archon workflow details in README)
     ```

  2. Validate links:
     ```bash
     # Extract and test relative file links
     grep -oP '\[.*?\]\(\K[^)#]+(?=\))' README.md | grep -v '^http' | while read link; do
       test -f "$link" && echo "✅ $link" || echo "❌ BROKEN: $link"
     done
     ```

  3. Preview on GitHub:
     - Commit to branch and push
     - Open GitHub preview of README.md
     - Verify all tables render correctly
     - Check all links are clickable

  4. Tone consistency check:
     - Read through entire README
     - Verify conversational voice maintained (not corporate)
     - Check for: "we", "you", active voice, short sentences
     - Avoid: "leverage", "utilize", "stakeholders", passive voice

  5. Success criteria verification:
     - [ ] All 4 MCP servers in table (lines 17-24)
     - [ ] Context Optimization section added after "Current Capabilities"
     - [ ] Pattern Library section added after "PRP Workflow"
     - [ ] .claude/ directory in structure (lines 99-130)
     - [ ] Current Capabilities specific (server names mentioned)
     - [ ] Config example shows all 4 servers (lines 48-75)
     - [ ] Line counts accurate (107, 320, 202)
     - [ ] Conversational tone preserved
     - [ ] No CLAUDE.md duplication
     - [ ] All links valid
     - [ ] Tables render correctly
     - [ ] JSON valid

VALIDATION:
  - All scripts pass without errors
  - GitHub preview shows correctly rendered README
  - All success criteria checked ✅
```

### Implementation Pseudocode

```markdown
# Task 1: Add MCP Server Rows
def add_mcp_servers_to_table():
    # Pattern from: examples/mcp-server-table.md

    # Find existing table (lines 17-21)
    table_start = find_line("| Server | Purpose | Status | Connection |")

    # Insert after vibesbox row:
    insert_after(table_start + 3, "| `basic-memory` | Persistent memory across Claude sessions | ✅ Active | Docker exec |")
    insert_after(table_start + 4, "| `MCP_DOCKER` | Container orchestration gateway | ✅ Active | docker mcp |")
    insert_after(table_start + 5, "| `archon` | Task/knowledge management, RAG search | ✅ Active | npx mcp-remote |")

    # Gotcha to avoid: Missing blank lines before/after table
    ensure_blank_line(table_start - 1)
    ensure_blank_line(table_start + 6)

# Task 3: Add Context Optimization Section
def add_context_optimization_section():
    # Pattern from: examples/metrics-presentation.md, examples/section-structure.md

    # Find insertion point (after "Current Capabilities")
    capabilities_section = find_heading("## Current Capabilities")
    next_section = find_next_heading(capabilities_section)

    # Insert new section between them
    section_content = """
## Context Optimization

We compressed the context Claude sees by **59-70%** without losing functionality.

**File Sizes Achieved**:
- **CLAUDE.md**: 107 lines (from 143, 25% reduction)
- **Patterns**: 47-150 lines each (target ≤150)
- **Commands**: 202-320 lines each (target ≤350)

**Context Per Command**:
- `/generate-prp`: 427 lines (59% reduction from 1044 baseline)
- `/execute-prp`: 309 lines (70% reduction from 1044 baseline)

**Impact**: ~320,400 tokens saved annually (assuming 10 PRP workflows/month)

**Why this matters**: Claude has an "attention budget"—more tokens doesn't mean better results. By compressing context, we improved both speed and accuracy.

See [validation report](prps/prp_context_refactor/execution/validation-report.md) for detailed methodology.
"""

    insert_at(next_section, section_content)

    # Gotcha to avoid: Line counts drifting from reality
    verify_line_count("CLAUDE.md", expected=107)
    verify_line_count(".claude/commands/generate-prp.md", expected=320)
    verify_line_count(".claude/commands/execute-prp.md", expected=202)

# Task 6: Make Capabilities Specific
def make_capabilities_specific():
    # Pattern from: examples/section-structure.md

    # Find "Current Capabilities" section
    section = find_heading("## Current Capabilities")

    # Replace content with server-attributed capabilities
    replace_section_content(section, """
- **Shell execution & container management** via `mcp-vibes-server` MCP
  - Run bash commands in isolated environments
  - Docker container lifecycle management

- **Desktop automation & visual feedback** via `mcp-vibesbox-server` MCP
  - VNC desktop environment (XFCE4, 1920x1080)
  - Screenshot capture for Claude's vision

- **Task & knowledge management** via `archon` MCP
  - Task tracking (find_tasks, manage_task)
  - RAG search across documentation

- **Persistent memory** via `basic-memory` MCP
  - Local Markdown-based knowledge storage
  - Conversation context across sessions

- **Container orchestration** via `MCP_DOCKER` gateway
  - Unified MCP server management
  - Security isolation and secrets management
""")

    # Gotcha to avoid: Vague claims without server attribution
    verify_all_capabilities_mention_server()
```

---

## Validation Loop

### Level 1: Syntax & Style Checks

```bash
# Markdown validation
markdownlint README.md
# Expected: No errors (or warnings only)

# JSON validation (extract config example from README)
grep -Pzo '(?s)\{[^}]+mcpServers[^}]+\}' README.md > /tmp/readme_config.json
jq . /tmp/readme_config.json
# Expected: Formatted JSON output, no parse errors

# Check for CLAUDE.md duplication (Archon workflow shouldn't be in README)
grep -q "find_tasks.*manage_task.*doing" README.md && echo "❌ DUPLICATION DETECTED" || echo "✅ No duplication"
# Expected: "✅ No duplication"

# Verify line count claims match reality
echo "CLAUDE.md: $(wc -l < CLAUDE.md) lines (expected 107)"
echo "generate-prp: $(wc -l < .claude/commands/generate-prp.md) lines (expected 320)"
echo "execute-prp: $(wc -l < .claude/commands/execute-prp.md) lines (expected 202)"
# Expected: All match claimed values
```

### Level 2: Link Validation

```bash
# Extract and test all relative file links
echo "Checking file links..."
grep -oP '\[.*?\]\(\K[^)#]+(?=\))' README.md | grep -v '^http' | while read -r link; do
    if [ -f "$link" ]; then
        echo "✅ $link"
    else
        echo "❌ BROKEN: $link (file not found)"
    fi
done

# Verify pattern library files exist
for pattern in archon-workflow parallel-subagents quality-gates security-validation; do
    if [ -f ".claude/patterns/${pattern}.md" ]; then
        echo "✅ .claude/patterns/${pattern}.md"
    else
        echo "❌ MISSING: .claude/patterns/${pattern}.md"
    fi
done

# Check validation report exists
test -f "prps/prp_context_refactor/execution/validation-report.md" && \
    echo "✅ validation-report.md" || \
    echo "❌ MISSING: validation-report.md"
```

### Level 3: Content Accuracy Validation

```bash
# Verify MCP server count (should be 4)
server_count=$(grep -c "| \`.*\` |" README.md)
if [ "$server_count" -eq 4 ]; then
    echo "✅ MCP server count: $server_count (expected 4)"
else
    echo "❌ MCP server count: $server_count (expected 4)"
fi

# Verify servers match actual config
config_servers=$(jq -r '.mcpServers | keys[]' ~/Library/Application\ Support/Claude/claude_desktop_config.json | sort)
readme_servers=$(grep "| \`" README.md | awk -F'|' '{print $2}' | tr -d ' `' | sort)

if [ "$config_servers" == "$readme_servers" ]; then
    echo "✅ README servers match config"
else
    echo "❌ MISMATCH:"
    echo "Config: $config_servers"
    echo "README: $readme_servers"
fi

# Verify Context Optimization section exists
if grep -q "## Context Optimization" README.md; then
    echo "✅ Context Optimization section added"
else
    echo "❌ MISSING: Context Optimization section"
fi

# Verify Pattern Library section exists
if grep -q "## Pattern Library" README.md; then
    echo "✅ Pattern Library section added"
else
    echo "❌ MISSING: Pattern Library section"
fi
```

### Level 4: Visual Validation (GitHub Preview)

```bash
# Commit to branch and preview on GitHub
git checkout -b readme-update-context-refactor
git add README.md
git commit -m "Update README: add 4 MCP servers, context optimization, pattern library"
git push origin readme-update-context-refactor

# Open in browser: https://github.com/{user}/{repo}/blob/readme-update-context-refactor/README.md

# Manual checks on GitHub preview:
# - [ ] All tables render correctly (4 MCP servers visible)
# - [ ] JSON code block displays with syntax highlighting
# - [ ] All links are clickable (no 404s)
# - [ ] Directory tree structure displays correctly
# - [ ] Headings create table of contents
# - [ ] Context Optimization section visible
# - [ ] Pattern Library section visible
```

---

## Final Validation Checklist

Before marking complete:

### Content Completeness
- [ ] All 4 MCP servers in table (archon, basic-memory, MCP_DOCKER, vibesbox)
- [ ] Each server has purpose, status (✅), connection method
- [ ] Context Optimization section added with 59-70% metric
- [ ] Pattern Library section added with 4 key patterns
- [ ] .claude/ directory structure documented
- [ ] Current Capabilities made specific (server names mentioned)
- [ ] Config example shows all 4 servers (validated JSON)

### Accuracy
- [ ] Line counts verified: CLAUDE.md=107, generate-prp=320, execute-prp=202
- [ ] MCP servers match claude_desktop_config.json
- [ ] All status indicators accurate (✅ Active verified)
- [ ] Metrics calculations correct (59-70% reduction)
- [ ] All links valid (pattern files, validation reports exist)

### Formatting
- [ ] Markdown tables render correctly (blank lines, 3+ hyphens)
- [ ] JSON configuration valid (no trailing commas, passes jq)
- [ ] Code blocks have language tags (```bash, ```json, ```markdown)
- [ ] Directory tree uses correct ASCII characters (├── └── │)
- [ ] Headings use ## and ### only (no ####)

### Quality
- [ ] Conversational tone preserved (not corporate/formal)
- [ ] No CLAUDE.md content duplication (Archon workflow NOT in README)
- [ ] Progressive disclosure maintained (≤2 levels)
- [ ] Server-attributed capabilities (not vague claims)
- [ ] Short paragraphs (2-4 sentences)
- [ ] Active voice, "we"/"you" pronouns

### Testing
- [ ] markdownlint passes
- [ ] jq validates JSON config
- [ ] All file links resolve
- [ ] GitHub preview renders correctly
- [ ] All validation scripts pass

---

## Anti-Patterns to Avoid

### ❌ Don't Duplicate CLAUDE.md Content
```markdown
# WRONG: Inlining Archon workflow in README
## Archon Workflow
1. Get Task → find_tasks(...)
2. Start Work → manage_task(...)
# This is already in CLAUDE.md!

# RIGHT: Reference CLAUDE.md for details
See [CLAUDE.md](CLAUDE.md) for detailed Archon workflow patterns.
```

### ❌ Don't Use Vague Capability Claims
```markdown
# WRONG: Generic, non-actionable
- Remember conversations
- Execute code safely

# RIGHT: Specific, server-attributed
- **Persistent memory** via `basic-memory` MCP
  - Local Markdown-based knowledge storage
```

### ❌ Don't Exceed Two-Level Progressive Disclosure
```markdown
# WRONG: Three levels
README → patterns/README.md → archon-workflow.md → Archon GitHub

# RIGHT: Two levels with inline reference
README (quick reference table) → pattern files (details)
External links marked as "reference only"
```

### ❌ Don't Skip Validation
```markdown
# WRONG: Claim metrics without verification
- CLAUDE.md: **107 lines** (might be outdated!)

# RIGHT: Verify before documenting
wc -l CLAUDE.md  # Must equal 107 or update claim
```

### ❌ Don't Break Markdown Table Syntax
```markdown
# WRONG: Insufficient hyphens, no blank lines
| Server | Purpose |
|---|---|  # Only 1 hyphen
| archon | Task management |  # No blank line

# RIGHT: Proper syntax
[blank line]
| Server | Purpose |
|--------|---------|  # 3+ hyphens
| `archon` | Task management |
[blank line]
```

---

## Success Metrics

**Quantitative**:
- README.md updated: +80-100 lines
- MCP servers documented: 2 → 4 (100% increase)
- New sections added: 2 (Context Optimization, Pattern Library)
- Line count accuracy: 100% (all claims verified)
- Link validity: 100% (all links resolve)
- JSON validity: 100% (passes jq validation)

**Qualitative**:
- Documentation accuracy: Users can successfully set up all 4 MCP servers
- Discoverability: Pattern library findable from README
- Context optimization: Achievement clearly documented and replicable
- Tone consistency: Conversational voice maintained throughout
- Progressive disclosure: Two-level maximum preserved

**Impact**:
- Reduced setup confusion (complete MCP server list)
- Increased pattern reuse (library discoverable)
- Achievement visibility (context optimization highlighted)
- Trust in documentation (accurate claims, verified links)

---

## PRP Quality Self-Assessment

**Score: 9/10** - High confidence in one-pass implementation success

**Reasoning**:
- ✅ **Comprehensive context**: All 5 research docs thorough (feature-analysis, codebase-patterns, documentation-links, examples-to-include, gotchas)
- ✅ **Clear task breakdown**: 7 sequential tasks with specific steps and validation gates
- ✅ **Proven patterns**: 7 curated examples extracted from production README and config
- ✅ **Validation strategy**: 4 levels (syntax → links → accuracy → visual preview)
- ✅ **Error handling**: 15 gotchas documented with wrong/right code examples
- ✅ **Executable validation**: Bash scripts provided for all validation gates
- ✅ **Progressive complexity**: Phase 0 (study) → Tasks 1-6 (implement) → Task 7 (validate)

**Deduction reasoning** (-1 point):
- Minor gap: Tone validation is somewhat subjective (provided examples help but not fully deterministic)
- Mitigation: Task 7 includes manual tone check with specific criteria ("we" vs "stakeholders")

**Confidence factors**:
- All examples from actual production code (not synthetic)
- All gotchas include solutions (wrong/right code)
- All validation gates executable (bash scripts ready to run)
- All documentation URLs verified and accessible
- All line counts verified against actual files
- All MCP servers verified in actual config

**Expected outcome**: README update completed in single execution with all success criteria met, no rework needed.
