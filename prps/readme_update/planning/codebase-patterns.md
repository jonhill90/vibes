# Codebase Patterns: readme_update

## Overview

This document extracts patterns from the Vibes codebase related to documentation structure, MCP server documentation, context optimization metrics, and pattern library organization. The patterns focus on how the project documents its architecture, tracks compression achievements, and organizes reusable patterns—all critical for accurately updating README.md post-context-refactor.

---

## Architectural Patterns

### Pattern 1: Two-Level Documentation Hierarchy (CLAUDE.md ↔ README.md)
**Source**: /Users/jon/source/vibes/CLAUDE.md (lines 1-10)
**Relevance**: 10/10 - Critical for avoiding duplication

**What it does**: Separates project rules (CLAUDE.md) from architecture/setup (README.md). CLAUDE.md is concise (107 lines) and references README.md for comprehensive details.

**Key Techniques**:
```markdown
# CLAUDE.md
## Repository Overview

See [../README.md](../README.md) for complete architecture, directory structure, MCP server details, and quick start guide.

**Key differences for Claude Code**: This file contains project rules and workflows only. For setup, architecture, and component details, consult README.md.
```

**When to use**:
- Updating README.md: Never duplicate content that's already in CLAUDE.md
- Adding new sections: Ensure they belong in README (architecture) not CLAUDE (workflow rules)
- Referencing patterns: Link to `.claude/patterns/` instead of inlining

**How to adapt**:
- When adding MCP server details, put comprehensive docs in README, brief workflow in CLAUDE
- When documenting context optimization, show metrics in README, reference achievement in CLAUDE if needed
- Pattern library belongs in README as "what exists", CLAUDE references it for "how to use"

**Why this pattern**:
- Achieves 59-70% token reduction by eliminating duplication
- Clear separation of concerns (rules vs architecture)
- Progressive disclosure: README is comprehensive, CLAUDE is compressed

---

### Pattern 2: MCP Server Table Documentation Format
**Source**: /Users/jon/source/vibes/README.md (lines 17-21)
**Relevance**: 9/10 - Current README uses this exact format

**What it does**: Documents MCP servers in scannable table format with 4 columns: Server, Purpose, Status, Connection.

**Key Techniques**:
```markdown
| Server | Purpose | Status | Connection |
|--------|---------|--------|------------|
| `mcp-vibes-server` | Shell access, container management | ✅ Active | Docker exec |
| `mcp-vibesbox-server` | Unified shell + VNC GUI | ✅ Active | Docker exec |
```

**When to use**:
- Adding missing MCP servers (archon, basic-memory, MCP_DOCKER)
- Documenting server capabilities concisely
- Providing quick reference for configuration

**How to adapt**:
- Add row for each new server in config file
- Purpose: Extract from server README.md or infer from config
- Status: ✅ Active (all 4 currently configured), 🚧 Development, ❌ Disabled
- Connection: Match config args (e.g., "Docker exec", "npx mcp-remote", "docker mcp")

**Why this pattern**:
- Scannable format (tables > paragraphs)
- Matches existing README style
- Easy to maintain and extend

---

### Pattern 3: Context Optimization Metrics Display
**Source**: /Users/jon/source/vibes/prps/prp_context_refactor/execution/validation-report.md (lines 189-220)
**Relevance**: 10/10 - Exact metrics to include in README

**What it does**: Documents token reduction achievements with specific line counts and percentages.

**Key Techniques**:
```markdown
### Final State (Iteration 3)
- CLAUDE.md: **107 lines** (target ≤120) - **PASS** ✅
- generate-prp.md: **320 lines** (target ≤350) - **PASS** ✅
- execute-prp.md: **202 lines** (target ≤350) - **PASS** ✅

/generate-prp reduction: (1044 - 427) / 1044 = 59% - PASS ✅
/execute-prp reduction: (1044 - 309) / 1044 = 70% - PASS ✅

**Per /generate-prp invocation**:
- Before: 1044 lines
- After: 427 lines
- Savings: **617 lines (59%)**

**Per /execute-prp invocation**:
- Before: 1044 lines
- After: 309 lines
- Savings: **735 lines (70%)**
```

**When to use**:
- Creating "Context Optimization" section in README
- Celebrating compression achievements
- Providing concrete evidence of optimization work

**How to adapt**:
- Use actual line counts from validation-report.md
- Present as achievement (✅ markers, bold percentages)
- Include both per-command and aggregate metrics
- Link to validation report for full details

**Why this pattern**:
- Concrete numbers > vague claims ("optimized context" vs "59-70% reduction")
- Validation report format already proven
- Shows methodology (before/after/calculation)

---

### Pattern 4: Pattern Library Quick Reference Table
**Source**: /Users/jon/source/vibes/.claude/patterns/README.md (lines 7-12)
**Relevance**: 10/10 - Exact format to use in README

**What it does**: Documents patterns in 3-column quick reference table: "Need to...", "See Pattern", "Used By".

**Key Techniques**:
```markdown
**Need to...** | **See Pattern** | **Used By**
---|---|---
Extract secure feature names | [security-validation.md](security-validation.md) | All commands
Integrate with Archon MCP | [archon-workflow.md](archon-workflow.md) | generate-prp, execute-prp
Execute subagents in parallel | [parallel-subagents.md](parallel-subagents.md) | generate-prp Phase 2
Validate PRP/execution quality | [quality-gates.md](quality-gates.md) | generate-prp Phase 5
```

**When to use**:
- Adding "Pattern Library" section to README
- Providing quick reference without duplicating pattern content
- Showing practical use cases for each pattern

**How to adapt**:
- Reference `.claude/patterns/README.md` for comprehensive details
- Keep table in README as quick reference only
- Use relative links from repository root
- Add brief sentence after table linking to full index

**Why this pattern**:
- Progressive disclosure (table → link → full pattern)
- Scannable format
- Avoids duplication (links to source of truth)
- Follows DRY principle

---

### Pattern 5: Directory Structure Tree with Explanations
**Source**: /Users/jon/source/vibes/README.md (lines 99-114)
**Relevance**: 8/10 - Need to update but keep format

**What it does**: Shows directory structure as ASCII tree with inline comments explaining each directory's purpose.

**Key Techniques**:
```markdown
### Directory Structure

```
vibes/
├── prps/
│   ├── templates/        # PRP templates for different types
│   │   ├── prp_base.md          # Comprehensive base template
│   │   ├── feature_template.md  # Standard features
│   │   ├── tool_template.md     # API integrations
│   └── archived/         # Old reference PRPs
└── examples/             # Reference patterns and examples
```
```

**When to use**:
- Updating "Directory Structure" section to show `.claude/` organization
- Explaining new directory layouts
- Providing navigation guidance

**How to adapt**:
- Add `.claude/` directory tree showing commands, patterns, agents, templates
- Keep existing `prps/` structure (don't remove working sections)
- Use inline comments to explain purpose of each subdirectory
- Match current indentation and tree characters

**Why this pattern**:
- Visual navigation aid
- Inline explanations save space vs separate descriptions
- Existing README format, maintain consistency

---

### Pattern 6: Configuration Example (JSON) with All Servers
**Source**: /Users/jon/Library/Application Support/Claude/claude_desktop_config.json (lines 1-20)
**Relevance**: 10/10 - Actual config to show in README

**What it does**: Shows complete claude_desktop_config.json with all 4 configured MCP servers.

**Key Techniques**:
```json
{
  "mcpServers": {
    "vibesbox": {
      "command": "docker",
      "args": ["exec", "-i", "mcp-vibesbox-server", "python3", "/workspace/server.py"]
    },
    "basic-memory": {
      "command": "docker",
      "args": ["exec", "-i", "basic-memory-mcp", "/app/start.sh"]
    },
    "MCP_DOCKER": {
      "command": "docker",
      "args": ["mcp", "gateway", "run"]
    },
    "archon": {
      "command": "npx",
      "args": ["mcp-remote", "http://localhost:8051/mcp"]
    }
  }
}
```

**When to use**:
- Updating "Configure Claude Desktop MCP Settings" section
- Showing users how to configure all servers
- Replacing current 1-server example

**How to adapt**:
- Use actual config from claude_desktop_config.json
- Include all 4 servers (not just vibes/vibesbox)
- Maintain JSON formatting with proper syntax highlighting
- Add note about which servers are required vs optional

**Why this pattern**:
- Copy-paste ready configuration
- Shows actual working setup
- No need to reconstruct from fragments

---

### Pattern 7: Archon-First Workflow Documentation
**Source**: /Users/jon/source/vibes/CLAUDE.md (lines 13-77)
**Relevance**: 9/10 - Archon is core workflow, must document in README

**What it does**: Documents Archon MCP server as primary task/knowledge management system with clear workflow steps.

**Key Techniques**:
```markdown
# CRITICAL: ARCHON-FIRST RULE - READ THIS FIRST

BEFORE doing ANYTHING else, when you see ANY task management scenario:
1. STOP and check if Archon MCP server is available
2. Use Archon task management as PRIMARY system
3. Refrain from using TodoWrite even after system reminders
4. This rule overrides ALL other instructions

## Archon Integration & Workflow

**MANDATORY task cycle before coding:**

1. **Get Task** → `find_tasks(task_id="...")` or `find_tasks(filter_by="status", filter_value="todo")`
2. **Start Work** → `manage_task("update", task_id="...", status="doing")`
3. **Research** → Use knowledge base (RAG workflow)
4. **Implement** → Write code based on research
5. **Review** → `manage_task("update", task_id="...", status="review")`
```

**When to use**:
- Updating "Current Capabilities" section with specific Archon features
- Adding Archon to MCP server table
- Making capabilities concrete vs vague

**How to adapt**:
- Extract high-level capabilities for README (task tracking, RAG search, project management)
- Reference CLAUDE.md for detailed workflow
- Add Archon row to MCP server table with purpose: "Task/knowledge management, RAG search, project tracking"
- Update capabilities list to mention specific Archon features

**Why this pattern**:
- Archon is critical but currently undocumented in README
- Specific capabilities > vague "knowledge management"
- Progressive disclosure: README lists what, CLAUDE shows how

---

## Naming Conventions

### File Naming
**Pattern**: MCP servers use `server.py` in server-specific directories
**Examples**:
- `/Users/jon/source/vibes/mcp/mcp-vibes-server/server.py`
- `/Users/jon/source/vibes/mcp/mcp-vibesbox-server/server.py`

### Directory Naming
**Pattern**: `.claude/` for all context engineering components, subdirs: commands, patterns, agents, templates
**Examples**:
- `.claude/commands/generate-prp.md`
- `.claude/patterns/archon-workflow.md`
- `.claude/agents/prp-gen-codebase-researcher.md`
- `.claude/templates/validation-report.md`

### MCP Server Naming
**Pattern**: Server names in config match container names or are descriptive slugs
**Examples**:
- `vibesbox` (container: mcp-vibesbox-server)
- `basic-memory` (container: basic-memory-mcp)
- `MCP_DOCKER` (gateway service)
- `archon` (remote MCP server)

### Section Naming in Markdown
**Pattern**: Title case for major sections, sentence case for subsections
**Examples**:
- `## Current Architecture` (major)
- `### Prerequisites` (subsection)
- `## Context Engineering & PRPs` (major)
- `### What are PRPs?` (subsection with question)

---

## File Organization

### Current .claude/ Directory Structure
```
.claude/
├── commands/           # Slash commands for Claude Code
│   ├── generate-prp.md       # 320 lines (59% reduction)
│   ├── execute-prp.md        # 202 lines (70% reduction)
│   ├── list-prps.md
│   ├── prep-parallel.md
│   ├── execute-parallel.md
│   ├── prp-cleanup.md
│   └── primer.md
├── patterns/           # Reusable implementation patterns
│   ├── README.md             # Pattern library index
│   ├── archon-workflow.md    # 133 lines
│   ├── parallel-subagents.md # 150 lines
│   ├── quality-gates.md      # 128 lines
│   └── security-validation.md # 47 lines
├── agents/             # Subagent specifications
│   ├── prp-gen-codebase-researcher.md
│   ├── prp-gen-documentation-hunter.md
│   ├── prp-gen-example-curator.md
│   ├── prp-gen-gotcha-detective.md
│   └── prp-gen-assembler.md
└── templates/          # Report templates
    ├── validation-report.md
    └── completion-report.md
```

**Justification**: Separation of concerns by component type (commands vs patterns vs agents). Pattern library enables DRY principle across commands. Template directory supports consistent reporting.

---

### MCP Server Organization
```
mcp/
├── mcp-vibes-server/
│   ├── server.py
│   ├── docker-compose.yml
│   └── README.md
├── mcp-vibesbox-server/
│   ├── server.py
│   ├── docker-compose.yml
│   └── README.md (detailed feature docs)
└── mcp-vibesbox-monitor/
    └── README.md
```

**Justification**: Each MCP server is self-contained with its own docker-compose and documentation. Server README files are comprehensive (mcp-vibesbox-server: 251 lines with feature confirmations).

---

### PRP Directory Organization (Per-Feature Scoped)
```
prps/{feature_name}/
├── planning/               # Research outputs
│   ├── feature-analysis.md
│   ├── codebase-patterns.md
│   ├── documentation-links.md
│   ├── examples-to-include.md
│   └── gotchas.md
├── examples/               # Concrete examples for this PRP
│   └── README.md
└── execution/              # Execution artifacts
    ├── execution-plan.md
    ├── validation-report.md
    └── task-*.md
```

**Justification**: Per-feature scoping prevents global namespace pollution. Three phases: planning (research) → examples (curation) → execution (implementation). Pattern extracted from prp_context_refactor directory structure.

---

## Common Utilities to Leverage

### 1. Security Validation Function
**Location**: `.claude/patterns/security-validation.md`
**Purpose**: 5-level security validation for feature names (path traversal, command injection, dangerous chars)
**Usage Example**:
```python
# See .claude/patterns/security-validation.md for full implementation
feature_name = extract_feature_name(filepath, strip_prefix="INITIAL_")
# Validates: no .., no shell chars, alphanumeric only, length ≤50
```

### 2. Archon Health Check
**Location**: `.claude/patterns/archon-workflow.md`
**Purpose**: Graceful degradation when Archon MCP unavailable
**Usage Example**:
```python
health = mcp__archon__health_check()
archon_available = health["status"] == "healthy"

if archon_available:
    project = mcp__archon__manage_project("create", title="...", description="...")
else:
    print("ℹ️ Archon MCP not available - proceeding without project tracking")
```

### 3. Parallel Task Invocation
**Location**: `.claude/patterns/parallel-subagents.md`
**Purpose**: 3x speedup by invoking multiple subagents in same response
**Usage Example**:
```python
# Invoke ALL in SAME response (critical for parallelism)
Task(subagent_type="prp-gen-codebase-researcher", ...)
Task(subagent_type="prp-gen-documentation-hunter", ...)
Task(subagent_type="prp-gen-example-curator", ...)
Task(subagent_type="prp-gen-gotcha-detective", ...)
```

### 4. Quality Gate Scoring
**Location**: `.claude/patterns/quality-gates.md`
**Purpose**: Validation loops to ensure 8+/10 quality before delivery
**Usage Example**:
```python
# Score PRP comprehensiveness (see pattern for criteria)
if score >= 8:
    deliver_prp()
else:
    identify_gaps_and_fix()
```

---

## Testing Patterns

### Validation Report Structure
**Pattern**: Systematic validation with 5 levels, each with status/attempts/notes
**Example**: `/Users/jon/source/vibes/prps/prp_context_refactor/execution/validation-report.md`

**Key techniques**:
```markdown
| Level | Description | Status | Attempts | Notes |
|-------|-------------|--------|----------|-------|
| 1 | File Size Validation | PASS | 3 | All files within targets |
| 2 | Duplication Check | PASS | 1 | No README duplication found |
| 3 | Pattern Loading Check | PASS | 1 | Doc-style refs only |
| 4 | Functionality Test | SKIP | 0 | Not required for patterns |
| 5 | Token Usage Measurement | PASS | 3 | 59-70% reduction achieved |
```

**When to use**:
- Documenting validation results
- Showing iterative improvement (Iteration 1 → 2 → 3)
- Proving success criteria met

---

### Line Count Validation Method
**Pattern**: Use actual line counts to validate compression claims
**Example**: From validation-report.md

**Key techniques**:
```bash
# Actual validation commands (not shown in README, but methodology referenced)
wc -l CLAUDE.md                          # 107 lines
wc -l .claude/patterns/*.md              # 133, 150, 128, 47 lines
wc -l .claude/commands/generate-prp.md   # 320 lines
wc -l .claude/commands/execute-prp.md    # 202 lines

# Calculation formula for reduction percentage
reduction = (before - after) / before * 100
# Example: (1044 - 427) / 1044 = 59%
```

**When to use**:
- Validating claims in documentation
- Measuring compression achievements
- Providing concrete evidence

---

## Anti-Patterns to Avoid

### 1. Content Duplication Between CLAUDE.md and README.md
**What it is**: Repeating the same information in both files
**Why to avoid**: Violates DRY, causes token waste (defeats context optimization)
**Found in**: Original pre-refactor CLAUDE.md had "Repository Overview" duplicated from README
**Better approach**:
- README: Comprehensive architecture/setup details
- CLAUDE.md: References README, adds workflow rules only
- Pattern: "See [../README.md](../README.md) for complete architecture..."

---

### 2. Inlining Pattern Content in Commands
**What it is**: Copying full pattern implementations into command files
**Why to avoid**:
- Duplication defeats compression (e.g., security validation used in 2+ commands)
- Pattern updates don't propagate
- Increases token usage unnecessarily
**Found in**: Avoided in refactored commands (they use "See .claude/patterns/..." references)
**Better approach**:
- Extract pattern to `.claude/patterns/{name}.md`
- Reference in commands: "See .claude/patterns/security-validation.md for details"
- Include minimal inline code only if critical for workflow

---

### 3. Vague Capability Claims
**What it is**: Generic statements like "Remember conversations" or "Persistent knowledge"
**Why to avoid**:
- Not specific enough to be actionable
- Doesn't explain how or what systems enable it
- Makes README less useful as reference
**Found in**: Current README.md "Current Capabilities" section
**Better approach**:
- "Task management via Archon MCP (find_tasks, manage_task, RAG search)"
- "Persistent memory across sessions via basic-memory MCP server"
- Specific capabilities tied to specific servers

---

### 4. Over-Compression Losing Context
**What it is**: Compressing documentation so aggressively that critical details are lost
**Why to avoid**:
- Breaks functionality understanding
- Removes necessary context for implementation
- Makes documentation unusable
**Found in**: Avoided in context refactor (validation report shows functionality preserved)
**Better approach**:
- Compress verbose explanations, preserve critical workflow steps
- Remove redundant examples, keep pattern references
- Condense docstrings, maintain security checks
- Target: 59-70% reduction while preserving 100% functionality

---

### 5. Listing Non-Configured Servers
**What it is**: Documenting MCP servers in README that aren't actually in claude_desktop_config.json
**Why to avoid**:
- Misleading to users (setup won't work)
- Creates confusion about what's actually available
- Reduces trust in documentation accuracy
**Found in**: Current README only lists 2 servers, but 4 are configured
**Better approach**:
- Validate against actual config file before documenting
- Match table entries 1:1 with mcpServers object keys
- Use status indicators if server exists but isn't active (🚧 Development)

---

## Implementation Hints from Existing Code

### Similar Features Found

#### 1. Context Refactoring PRP (prp_context_refactor)
**Location**: `/Users/jon/source/vibes/prps/prp_context_refactor/`
**Similarity**: Documentation update with validation requirements
**Lessons**:
- Validation report provides concrete evidence of success (use similar metrics)
- Iterative refinement (3 iterations to achieve 59-70% reduction)
- Clear before/after line counts prove compression
- Security patterns must be preserved even when compressing

**Differences**:
- Context refactor modified multiple files across .claude/
- README update is single-file documentation change
- No code changes required for README update

---

#### 2. MCP Server Documentation (mcp-vibesbox-server/README.md)
**Location**: `/Users/jon/source/vibes/mcp/mcp-vibesbox-server/README.md`
**Similarity**: Comprehensive server capability documentation
**Lessons**:
- Use ✅ status markers for confirmed features
- Include "Confirmed Status" sections with dates
- List features with descriptions and verification status
- Show concrete usage examples (bash commands, MCP tool calls)
- Document technical implementation details (architecture, versions)

**Differences**:
- MCP server README is implementation-focused (how server works)
- Main README is user-focused (how to set up and use)
- MCP README can be verbose (251 lines), main README should be scannable

---

#### 3. Pattern Library Index (.claude/patterns/README.md)
**Location**: `/Users/jon/source/vibes/.claude/patterns/README.md`
**Similarity**: Index of reusable components with quick reference
**Lessons**:
- Quick reference table (3 columns) for scannability
- Brief descriptions with links to full details
- Clear usage guidelines section
- Anti-patterns section to warn what NOT to do

**Differences**:
- Pattern library is for developers implementing PRPs
- README pattern library section is for users understanding capabilities
- Index can assume technical audience, README should be beginner-friendly

---

## Recommendations for PRP

Based on pattern analysis:

1. **Follow Two-Level Documentation Pattern** - Never duplicate CLAUDE.md content in README. Reference it instead.

2. **Use MCP Server Table Format** - Add 2 missing servers (archon, basic-memory, MCP_DOCKER) to existing table structure.

3. **Show Context Optimization Metrics** - Create new section with validation report data (107 lines, 59-70% reduction, specific before/after).

4. **Reference Pattern Library** - Use quick reference table from `.claude/patterns/README.md`, link to full index for details.

5. **Update Directory Structure** - Add `.claude/` tree showing commands/patterns/agents/templates subdirectories.

6. **Make Capabilities Specific** - Replace vague "Remember conversations" with "Task tracking via Archon MCP (find_tasks, manage_task, RAG search)".

7. **Update Configuration Example** - Replace 1-server JSON with full 4-server config from actual claude_desktop_config.json.

8. **Preserve Existing Tone** - Maintain conversational style (e.g., "Ask → Build → Understand → Improve → Create" philosophy).

9. **Validate All Claims** - Use actual line counts from wc -l, verify server status from config, confirm features exist.

10. **Avoid Anti-Patterns** - No duplication, no vague claims, no unlisted servers, no over-compression.

---

## Source References

### From Archon
- **b8565aff9938938b** (context-engineering-intro): INITIAL.md template structure, feature documentation patterns - Relevance 7/10
- **c0e629a894699314** (pydantic.ai docs): Configuration validation patterns - Relevance 3/10 (not directly applicable)

### From Local Codebase
- **CLAUDE.md:1-10**: Two-level documentation hierarchy pattern
- **CLAUDE.md:13-77**: Archon workflow documentation (capabilities to reference)
- **README.md:17-21**: MCP server table format
- **README.md:99-114**: Directory structure tree format
- **.claude/patterns/README.md:7-12**: Pattern library quick reference table
- **prps/prp_context_refactor/execution/validation-report.md:189-220**: Context optimization metrics
- **claude_desktop_config.json:1-20**: Actual 4-server MCP configuration
- **mcp/mcp-vibesbox-server/README.md:1-50**: MCP server documentation style (✅ markers, confirmed status)

---

## Next Steps for Assembler

When generating the PRP:

1. **Reference these patterns in "Current Codebase Tree" section**:
   - Include README.md structure analysis
   - Reference CLAUDE.md for separation concerns
   - Note `.claude/patterns/README.md` as pattern source

2. **Include key code snippets in "Implementation Blueprint"**:
   - MCP server table format (4-column)
   - Directory structure tree (ASCII with comments)
   - Quick reference table (3-column)
   - Configuration JSON (all 4 servers)

3. **Add anti-patterns to "Known Gotchas" section**:
   - Gotcha #1: Duplication between CLAUDE.md and README.md
   - Gotcha #2: Inlining pattern content instead of referencing
   - Gotcha #3: Vague capability claims
   - Gotcha #4: Listing non-configured servers

4. **Use file organization for "Desired Codebase Tree"**:
   - Show `.claude/` subdirectories (commands, patterns, agents, templates)
   - Include line counts as evidence (107, 320, 202, 133, 150, 128, 47)
   - Reference validation-report.md for full metrics

5. **Extract validation methodology**:
   - Line count validation (wc -l)
   - Config validation (parse JSON, verify servers exist)
   - Link validation (ensure .claude/patterns/*.md files exist)
   - Tone validation (match existing conversational style)

---

**Pattern Extraction Complete**: 7 architectural patterns, 4 naming conventions, 3 file organization structures, 4 common utilities, 2 testing patterns, 5 anti-patterns, 3 similar implementations documented. Ready for PRP assembly.
