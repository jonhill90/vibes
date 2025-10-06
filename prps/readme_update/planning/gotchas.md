# Known Gotchas: README.md Update Post-Context Refactor

## Overview

This document identifies critical pitfalls when updating README.md to reflect the 59-70% context optimization achievement and 4 active MCP servers. The biggest risks are: duplicating content between CLAUDE.md and README.md (violating the hard-won DRY principle), breaking the two-level progressive disclosure pattern, and making accuracy claims that drift from reality.

---

## Critical Gotchas

### 1. CLAUDE.md / README.md Content Duplication

**Severity**: Critical
**Category**: Context Optimization Violation
**Affects**: The entire context refactor achievement (59-70% reduction)
**Source**: prps/prp_context_refactor/execution/validation-report.md

**What it is**:
Adding information to README.md that's already in CLAUDE.md, or vice versa. This defeats the purpose of the context refactor which achieved 59-70% token reduction by eliminating duplication.

**Why it's a problem**:
- Violates DRY principle that enabled context optimization
- Increases token usage unnecessarily
- Creates maintenance burden (update in two places)
- Pattern updates don't propagate
- Defeats the context engineering achievement

**How to detect it**:
- Search for identical paragraphs in both files
- Check if Archon workflow details appear in both
- Look for MCP server configuration in both places
- Verify pattern library content isn't inlined in both

**How to avoid/fix**:

```markdown
# ❌ WRONG - Duplicating Archon workflow in README.md

## README.md
### Archon Workflow
1. Get Task → find_tasks(task_id="...")
2. Start Work → manage_task("update", task_id="...", status="doing")
3. Research → rag_search_knowledge_base(query="...")
4. Complete → manage_task("update", task_id="...", status="done")

# CLAUDE.md also has this exact content - DUPLICATION!

# ✅ RIGHT - Progressive disclosure with references

## README.md
### Current Capabilities
- **Task management** via Archon MCP (find_tasks, manage_task, RAG search)
- **Persistent memory** across sessions via basic-memory MCP
- **Container orchestration** via Docker MCP Gateway
- **Shell + GUI automation** via vibesbox MCP

See [CLAUDE.md](CLAUDE.md) for detailed workflow patterns.

# CLAUDE.md has the detailed workflow, README has high-level summary
```

**Validation Test**:
```bash
# Check for duplication
diff <(grep -o "find_tasks" README.md) <(grep -o "find_tasks" CLAUDE.md)
# Should show README doesn't have implementation details

# Measure token count to verify no increase
wc -w README.md CLAUDE.md
# Combined count should not exceed pre-refactor baseline
```

**Additional Resources**:
- prps/prp_context_refactor/execution/validation-report.md (lines 189-220)
- .claude/patterns/archon-workflow.md (reference pattern, don't duplicate)

---

### 2. MCP Server Status Misrepresentation

**Severity**: Critical
**Category**: Accuracy / Trust
**Affects**: User setup experience, documentation credibility
**Source**: claude_desktop_config.json validation

**What it is**:
Listing MCP servers as "✅ Active" when they're not actually running, or documenting servers that aren't in the actual configuration file.

**Why it's a problem**:
- Users follow setup instructions and servers don't work
- Erodes trust in documentation accuracy
- Creates confusion about what's actually available
- Setup failures frustrate users immediately

**How to detect it**:
- Compare README server list with actual `claude_desktop_config.json`
- Check Docker container status: `docker ps | grep mcp`
- Verify each server starts: `docker exec -i <container> <command>`
- Test MCP server connection from Claude Desktop logs

**How to avoid/fix**:

```markdown
# ❌ WRONG - Claiming servers are active without verification

| Server | Purpose | Status | Connection |
|--------|---------|--------|------------|
| archon | Task management | ✅ Active | npx mcp-remote |
| super-cool-ai | Magic AI features | ✅ Active | Docker exec |

# "super-cool-ai" doesn't exist in config - misleading users!

# ✅ RIGHT - Validate against actual config

| Server | Purpose | Status | Connection |
|--------|---------|--------|------------|
| archon | Task/knowledge management, RAG search | ✅ Active | npx mcp-remote |
| vibesbox | Shell + VNC GUI automation | ✅ Active | Docker exec |
| basic-memory | Persistent memory across sessions | ✅ Active | Docker exec |
| MCP_DOCKER | Container orchestration gateway | ✅ Active | docker mcp |

# All 4 servers verified in claude_desktop_config.json
```

**Validation Script**:
```bash
# Extract servers from config
jq -r '.mcpServers | keys[]' ~/Library/Application\ Support/Claude/claude_desktop_config.json > /tmp/config_servers.txt

# Extract servers from README table
grep "| \`" README.md | awk -F'|' '{print $2}' | tr -d ' `' > /tmp/readme_servers.txt

# Compare - should be identical
diff /tmp/config_servers.txt /tmp/readme_servers.txt
```

**Testing for this issue**:
```python
import json
import subprocess

# Read actual config
config_path = "~/Library/Application Support/Claude/claude_desktop_config.json"
with open(config_path) as f:
    config = json.load(f)

actual_servers = set(config.get("mcpServers", {}).keys())

# Expected servers from README
readme_servers = {"archon", "vibesbox", "basic-memory", "MCP_DOCKER"}

# Verify match
assert actual_servers == readme_servers, f"Mismatch: {actual_servers} != {readme_servers}"
```

---

### 3. Metrics Drift and Accuracy Claims

**Severity**: Critical
**Category**: Data Integrity
**Affects**: Context optimization achievement documentation
**Source**: Validation report line count verification

**What it is**:
Claiming specific line counts (e.g., "CLAUDE.md: 107 lines") or reduction percentages without verifying they're still accurate. Files change over time and metrics drift.

**Why it's a problem**:
- False claims damage credibility
- Can't reproduce achievements if numbers are wrong
- Metrics used for validation become meaningless
- Other teams citing your work get bad data

**How to detect it**:
- Run `wc -l CLAUDE.md` and compare to claimed count
- Check if files modified since validation report was created
- Verify percentage calculations still match
- Compare current state to validation-report.md baseline

**How to avoid/fix**:

```bash
# ❌ WRONG - Hardcoded metrics without verification

## Context Optimization Achievement
- CLAUDE.md: **107 lines** (originally claimed in validation report)
- generate-prp.md: **320 lines**
- execute-prp.md: **202 lines**

# These might be outdated! Files could have changed.

# ✅ RIGHT - Measure and verify current state

## Context Optimization Achievement

### Verification (2025-01-15)
```bash
# Current line counts
wc -l CLAUDE.md                          # 107 lines ✅
wc -l .claude/commands/generate-prp.md   # 320 lines ✅
wc -l .claude/commands/execute-prp.md    # 202 lines ✅

# Reduction calculations
# /generate-prp: (1044 - 427) / 1044 = 59% ✅
# /execute-prp: (1044 - 309) / 1044 = 70% ✅
```

**Results**: 59-70% token reduction achieved and verified current.

See [validation-report.md](../prp_context_refactor/execution/validation-report.md) for full methodology.
```

**Automated Verification**:
```python
#!/usr/bin/env python3
# verify_metrics.py - Run before committing README updates

import subprocess
from pathlib import Path

def count_lines(filepath):
    result = subprocess.run(['wc', '-l', filepath], capture_output=True, text=True)
    return int(result.stdout.split()[0])

# Expected values from README
expected = {
    'CLAUDE.md': 107,
    '.claude/commands/generate-prp.md': 320,
    '.claude/commands/execute-prp.md': 202
}

# Verify each file
for file, expected_count in expected.items():
    actual_count = count_lines(file)
    if actual_count != expected_count:
        print(f"❌ DRIFT: {file}")
        print(f"   Expected: {expected_count} lines")
        print(f"   Actual: {actual_count} lines")
        print(f"   Update README.md or re-measure!")
    else:
        print(f"✅ {file}: {actual_count} lines (verified)")

# Calculate reductions
before_generate = 1044
after_generate = 427
reduction_generate = (before_generate - after_generate) / before_generate * 100
print(f"\n/generate-prp reduction: {reduction_generate:.0f}%")

before_execute = 1044
after_execute = 309
reduction_execute = (before_execute - after_execute) / before_execute * 100
print(f"/execute-prp reduction: {reduction_execute:.0f}%")
```

---

### 4. Markdown Table Formatting Errors

**Severity**: High
**Category**: Rendering / Display
**Affects**: MCP server table, pattern reference table
**Source**: GitHub Markdown rendering issues

**What it is**:
Common Markdown table syntax errors that break rendering: missing separator rows, insufficient hyphens, uneven column counts, or missing blank lines before tables.

**Why it's a problem**:
- Tables don't render at all (appear as raw text)
- Layout breaks on GitHub/other renderers
- Users can't read critical configuration info
- Professional appearance compromised

**How to detect it**:
- Preview README.md on GitHub before committing
- Check for at least 3 hyphens in separator row (---)
- Count pipe characters | in each row (must be equal)
- Ensure blank line before table starts
- Look for unescaped | characters in cell content

**How to avoid/fix**:

```markdown
# ❌ WRONG - Multiple table formatting errors

| Server | Purpose | Status | Connection |
|---|---:|-----|---|
| archon | Task management | ✅ Active | npx |
| vibesbox | Shell + GUI | ✅ | docker exec |
# Issues:
# 1. Only 1 hyphen in separator (should be 3+)
# 2. Inconsistent alignment (mix of left/right)
# 3. Missing cell content (vibesbox status column)
# 4. No blank line before table

# ✅ RIGHT - Proper table formatting

*Blank line above (required)*

| Server | Purpose | Status | Connection |
|--------|---------|--------|------------|
| `archon` | Task/knowledge management, RAG search | ✅ Active | npx mcp-remote |
| `vibesbox` | Shell + VNC GUI automation | ✅ Active | Docker exec |
| `basic-memory` | Persistent memory across sessions | ✅ Active | Docker exec |
| `MCP_DOCKER` | Container orchestration gateway | ✅ Active | docker mcp |

*Blank line below for safety*

# All columns filled, 3+ hyphens, consistent alignment, server names in backticks
```

**Special characters handling**:
```markdown
# Pipe characters in cell content must be escaped

| Tool | Command | Example |
|------|---------|---------|
| grep | Search files | `grep "pattern" file.txt` |
| awk | Text processing | `awk -F'\|' '{print $1}'` ← Escaped \| |

# Without escape, the | breaks the table column structure
```

**Validation checklist**:
- [ ] Blank line before table
- [ ] Header row with | separators
- [ ] Separator row with minimum 3 hyphens per column (---)
- [ ] All data rows have same number of | characters
- [ ] No unescaped | in cell content
- [ ] Blank line after table
- [ ] Preview on GitHub to confirm rendering

---

## High Priority Gotchas

### 5. Progressive Disclosure Pattern Violation (Three-Level Depth)

**Severity**: High
**Category**: Context Engineering / UX
**Affects**: Pattern library documentation, MCP server details
**Source**: Context refactor two-level disclosure rule

**What it is**:
Creating more than two levels of information disclosure: README → detailed doc → sub-documentation. The context refactor established a strict two-level maximum.

**Why it's a problem**:
- Navigation fatigue (users get lost)
- Defeats progressive disclosure benefits
- More than 2 levels negatively affects UX
- Violates context engineering principles

**How to detect it**:
- Trace link paths: if README links to X, and X links to Y, that's 3 levels
- Check if pattern library section links to patterns that link elsewhere
- Map documentation hierarchy depth
- Look for "See X for details, see Y for implementation, see Z for examples"

**How to avoid/fix**:

```markdown
# ❌ WRONG - Three levels of disclosure

## README.md (Level 1)
See [Pattern Library](.claude/patterns/README.md) for implementation patterns.

## .claude/patterns/README.md (Level 2)
See [archon-workflow.md](archon-workflow.md) for Archon integration details.

## .claude/patterns/archon-workflow.md (Level 3)
See [Archon GitHub repo](https://github.com/coleam00/Archon) for full API docs.

# This is 3+ levels - users have to click 3 times to get to information!

# ✅ RIGHT - Two levels maximum with inline quick reference

## README.md (Level 1 - Quick Reference)

### Pattern Library

See [.claude/patterns/README.md](.claude/patterns/README.md) for reusable patterns.

**Quick Reference**:

| Need to... | See Pattern | Used By |
|------------|-------------|---------|
| Integrate with Archon MCP | [archon-workflow.md](.claude/patterns/archon-workflow.md) | generate-prp, execute-prp |
| Execute parallel subagents | [parallel-subagents.md](.claude/patterns/parallel-subagents.md) | generate-prp Phase 2 |
| Validate PRP quality | [quality-gates.md](.claude/patterns/quality-gates.md) | generate-prp Phase 5 |

External docs: [Archon GitHub](https://github.com/coleam00/Archon) (reference only)

# Level 1: Quick reference table with direct links
# Level 2: Pattern files with implementation details
# External links clearly marked as "reference only" (not part of hierarchy)
```

**Flattening strategy**:
```markdown
# Instead of deep nesting, use horizontal organization

## Pattern Library

| Pattern | Purpose | When to Use | Link |
|---------|---------|-------------|------|
| archon-workflow | Archon MCP integration | Task management, RAG search | [View](.claude/patterns/archon-workflow.md) |
| parallel-subagents | 3x speedup execution | Multi-task research | [View](.claude/patterns/parallel-subagents.md) |
| quality-gates | Validation loops | PRP generation, execution | [View](.claude/patterns/quality-gates.md) |

All external documentation: [Context Engineering Intro](https://github.com/coleam00/context-engineering-intro)

# Single table with everything, one click to details (2 levels total)
```

---

### 6. Vague Capability Claims

**Severity**: High
**Category**: Clarity / Usability
**Affects**: "Current Capabilities" section
**Source**: Current README analysis + research feedback

**What it is**:
Generic statements like "Remember conversations" or "Persistent knowledge" without explaining which MCP server provides the capability or how it works.

**Why it's a problem**:
- Not actionable for users
- Doesn't explain which server enables which feature
- Can't troubleshoot if capability isn't working
- Misses opportunity to showcase specific MCP servers

**How to detect it**:
- Look for capabilities without associated server names
- Check if verbs are vague ("manage", "handle", "support")
- See if capability can be tested/verified
- Ask: "Which server provides this and how?"

**How to avoid/fix**:

```markdown
# ❌ WRONG - Vague, generic capabilities

## Current Capabilities

- **Execute code** in safe environments
- **Remember conversations** and build knowledge
- **Analyze repositories** from GitHub
- **Manage cloud infrastructure** with various tools
- **Persistent knowledge** across sessions
- **Browser automation** and screenshots

# Users don't know: Which server? How does it work? How to use it?

# ✅ RIGHT - Specific, server-attributed capabilities

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

Each capability maps to a specific MCP server with concrete features.
```

**Capability verification template**:
```markdown
### [Capability Name] via `[server-name]` MCP

**What it does**: [1-2 sentence description]

**Key features**:
- [Specific feature 1 with MCP tool name]
- [Specific feature 2 with MCP tool name]
- [Specific feature 3 with MCP tool name]

**Example usage**:
```bash
# [Actual command or MCP tool invocation]
[command example]
```

**Verify it works**:
```bash
# Test the server
docker exec -i [container] [command]
# Expected output: [what success looks like]
```
```

---

### 7. Link Rot and Broken References

**Severity**: High
**Category**: Maintenance / Usability
**Affects**: All documentation links in README
**Source**: Web research on documentation best practices

**What it is**:
Links to files that don't exist, incorrect relative paths, or references to moved/renamed files. Also includes broken section anchors (#heading links).

**Why it's a problem**:
- Users click and get 404 errors
- Documentation appears unmaintained
- Trust in other claims erodes
- Navigation breaks the learning flow

**How to detect it**:
- Click every link in README.md
- Check if referenced files exist: `test -f .claude/patterns/archon-workflow.md`
- Verify section anchors match actual headings
- Use link checker tools

**How to avoid/fix**:

```markdown
# ❌ WRONG - Broken links and incorrect paths

See [Pattern Library](patterns/README.md) for details.
See [Archon Integration](.claude/patterns/archon.md) for workflow.
See [Context Optimization](#context-engineering) for metrics.

# Issues:
# 1. patterns/README.md doesn't exist (missing .claude/ prefix)
# 2. archon.md doesn't exist (actual file: archon-workflow.md)
# 3. Section anchor #context-engineering doesn't exist (no heading matches)

# ✅ RIGHT - Verified links with validation

See [Pattern Library](.claude/patterns/README.md) for details.
See [Archon Integration](.claude/patterns/archon-workflow.md) for workflow.
See [Context Optimization](#context-optimization-achievement) for metrics.

# All paths verified:
# ls .claude/patterns/README.md ✅
# ls .claude/patterns/archon-workflow.md ✅
# grep "## Context Optimization Achievement" README.md ✅
```

**Link validation script**:
```bash
#!/bin/bash
# validate_readme_links.sh

echo "Validating README.md links..."

# Extract relative file links (not URLs)
grep -oP '\[.*?\]\(\K[^)#]+(?=\))' README.md | grep -v '^http' | while read -r link; do
    if [ -f "$link" ]; then
        echo "✅ $link"
    else
        echo "❌ BROKEN: $link (file not found)"
    fi
done

# Extract section anchor links
grep -oP '\[.*?\]\(#\K[^)]+(?=\))' README.md | while read -r anchor; do
    # Convert anchor to heading format (replace - with space, capitalize)
    heading=$(echo "$anchor" | sed 's/-/ /g' | sed 's/\b\w/\u&/g')

    if grep -q "## $heading" README.md || grep -q "### $heading" README.md; then
        echo "✅ #$anchor → found heading"
    else
        echo "❌ BROKEN ANCHOR: #$anchor (no matching heading)"
    fi
done
```

**Section anchor gotcha**:
```markdown
# Section anchors are auto-generated from headings

## Context Optimization Achievement  → #context-optimization-achievement
## Context Engineering & PRPs      → #context-engineering--prps

# Rules:
# - Lowercase all letters
# - Replace spaces with hyphens
# - Keep & as literal &
# - Remove special chars except &

# Link to it correctly:
[See metrics](#context-optimization-achievement) ✅
[See metrics](#Context-Optimization-Achievement) ❌ (case sensitive!)
```

---

### 8. JSON Configuration Syntax Errors

**Severity**: High
**Category**: Configuration / Setup
**Affects**: MCP server configuration example
**Source**: MCP troubleshooting research

**What it is**:
Invalid JSON in the configuration example: trailing commas, missing quotes, incorrect structure, or copy-paste artifacts that break Claude Desktop's config parser.

**Why it's a problem**:
- Users copy broken config and MCP servers don't load
- Claude Desktop fails silently or shows generic errors
- Setup frustration leads to abandonment
- Common issue in MCP troubleshooting

**How to detect it**:
- Run JSON through validator: `jq . config.json`
- Look for trailing commas (last item in object/array)
- Check for unquoted keys or values
- Verify bracket/brace matching
- Test by actually using the config example

**How to avoid/fix**:

```json
// ❌ WRONG - Multiple JSON syntax errors

{
  "mcpServers": {
    "archon": {
      "command": "npx",
      "args": ["mcp-remote", "http://localhost:8051/mcp"],  // ← Trailing comma!
    },
    "vibesbox": {
      command: "docker",  // ← Unquoted key!
      "args": ["exec", "-i", "mcp-vibesbox-server", "python3", "/workspace/server.py"]
    },  // ← Trailing comma!
  }
}

// ✅ RIGHT - Valid JSON, validated and tested

{
  "mcpServers": {
    "archon": {
      "command": "npx",
      "args": ["mcp-remote", "http://localhost:8051/mcp"]
    },
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
    }
  }
}
```

**Validation workflow**:
```bash
# Before adding JSON to README, validate it:

# 1. Create test file
cat > /tmp/mcp_config_test.json << 'EOF'
{
  "mcpServers": {
    "archon": {
      "command": "npx",
      "args": ["mcp-remote", "http://localhost:8051/mcp"]
    }
  }
}
EOF

# 2. Validate JSON syntax
jq . /tmp/mcp_config_test.json
# Should output formatted JSON if valid

# 3. Check for common gotchas
if grep -q ',$' /tmp/mcp_config_test.json; then
    echo "❌ WARNING: Trailing comma detected"
fi

# 4. Actually test the config (optional but recommended)
cp ~/Library/Application\ Support/Claude/claude_desktop_config.json ~/claude_config_backup.json
cp /tmp/mcp_config_test.json ~/Library/Application\ Support/Claude/claude_desktop_config.json
# Restart Claude Desktop and verify servers load
# Restore backup: cp ~/claude_config_backup.json ~/Library/Application\ Support/Claude/claude_desktop_config.json
```

---

## Medium Priority Gotchas

### 9. Directory Structure Outdated After Refactor

**Severity**: Medium
**Category**: Documentation Accuracy
**Affects**: Directory structure tree section
**Source**: Context refactor restructuring

**What it is**:
The README still shows the old `prps/` directory structure, but the context refactor created a new `.claude/` directory structure (commands, patterns, agents, templates) that isn't documented.

**Why it's confusing**:
- Users don't know `.claude/` exists
- Can't find pattern library (it's in `.claude/patterns/`)
- References to "pattern library" point to non-existent location
- Recent achievement (context refactor) is invisible

**How to handle it**:

```markdown
# ❌ OUTDATED - Only shows old structure

### Directory Structure

```
vibes/
├── prps/
│   ├── templates/        # PRP templates
│   ├── active/           # In-progress
│   └── completed/        # Finished
└── examples/             # Reference patterns
```

# Missing: .claude/ directory created during context refactor!

# ✅ UPDATED - Shows current state after refactor

### Directory Structure

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
│   │   ├── prp-gen-codebase-researcher.md
│   │   ├── prp-gen-documentation-hunter.md
│   │   └── prp-gen-gotcha-detective.md
│   └── templates/        # Report templates
│       └── validation-report.md
├── prps/                 # Per-feature PRP artifacts
│   └── {feature_name}/
│       ├── planning/     # Research outputs
│       ├── examples/     # Concrete examples
│       └── execution/    # Implementation artifacts
└── CLAUDE.md             # 107 lines (project rules only)
```

**Key Changes from Context Refactor**:
- Created `.claude/` directory for DRY pattern reuse
- Separated commands, patterns, agents, and templates
- Achieved 59-70% token reduction through this structure
```

**Explanation of why this matters**:
```markdown
The new `.claude/` structure enables the context optimization achievement by:

1. **Pattern extraction**: Common patterns moved to `.claude/patterns/` (used 3+ times → extract to pattern)
2. **DRY principle**: Commands reference patterns instead of duplicating code
3. **Separation of concerns**: Commands, patterns, agents, templates each have dedicated directories
4. **Progressive disclosure**: README → patterns index → individual pattern files (2 levels max)

This structure directly supports the 59-70% token reduction by eliminating duplication across commands.
```

---

### 10. Over-Compression Losing Critical Context

**Severity**: Medium
**Category**: Context Engineering
**Affects**: Documentation clarity, user understanding
**Source**: Context compression research

**What it is**:
Compressing documentation so aggressively that critical details are lost. Pursuing brevity at the cost of usability, removing examples or explanations that users actually need.

**Why it's confusing**:
- Users can't understand how to use features
- Missing "why" context for decisions
- Examples removed that would clarify usage
- Over-optimization defeats documentation purpose

**How to handle it**:

```markdown
# ❌ OVER-COMPRESSED - Lost critical context

## MCP Servers
4 servers. See config.

# Users don't know: What servers? What do they do? How to configure?

# ❌ UNDER-COMPRESSED - Verbose, duplicative

## MCP Servers

The Vibes project utilizes Model Context Protocol servers to extend Claude's capabilities. MCP is a protocol developed by Anthropic that allows Claude to interact with external tools and services. In our implementation, we use four different MCP servers, each serving a specific purpose in the overall architecture.

The first server is called archon, and it provides task management and knowledge search capabilities through a RAG-based system. The second server is vibesbox, which offers shell access and GUI automation. The third server is basic-memory, providing persistent storage. The fourth server is MCP_DOCKER, which orchestrates containers.

[200+ more words of explanation...]

# ✅ RIGHT - Balanced compression with clarity

## Current Architecture

**Production Stack**: Claude Desktop + MCP Servers + Docker Containers

Vibes runs as a distributed system of 4 specialized MCP servers:

| Server | Purpose | Status | Connection |
|--------|---------|--------|------------|
| `archon` | Task/knowledge management, RAG search | ✅ Active | npx mcp-remote |
| `vibesbox` | Shell + VNC GUI automation | ✅ Active | Docker exec |
| `basic-memory` | Persistent memory across sessions | ✅ Active | Docker exec |
| `MCP_DOCKER` | Container orchestration gateway | ✅ Active | docker mcp |

See [CLAUDE.md](CLAUDE.md) for detailed Archon workflow. See individual server READMEs in `mcp/*/README.md` for technical details.

# Compressed but complete: What (table), Why (purpose), How (connection), Where (links for details)
```

**Compression quality checklist**:
- [ ] Core information preserved (what, why, how)
- [ ] Links to detailed docs provided (progressive disclosure)
- [ ] At least one example for complex features
- [ ] No jargon without explanation
- [ ] Can a new user understand and act on this?

---

### 11. Tone Inconsistency Breaking Voice

**Severity**: Medium
**Category**: User Experience / Branding
**Affects**: Overall README readability
**Source**: INITIAL.md constraint "same friendly tone"

**What it is**:
Shifting from conversational, learning-focused voice to corporate/formal language when adding new sections. Mixing tutorial-style explanations with dry technical specifications.

**Why it's confusing**:
- Disrupts reading flow
- Feels like different authors
- Loses the "Ask → Build → Understand → Improve → Create" philosophy
- Makes documentation less approachable

**How to handle it**:

```markdown
# ❌ WRONG - Corporate/formal tone shift

## Context Optimization Achievement

The Vibes project has successfully implemented a comprehensive context engineering initiative that resulted in significant token reduction across multiple system components. Utilizing advanced compression techniques and strategic content reorganization, the development team achieved optimization metrics ranging from 59% to 70% across critical command files. This optimization was accomplished through systematic elimination of redundant content and implementation of DRY principles.

Stakeholders should note that this achievement demonstrates the efficacy of context engineering methodologies...

# This sounds like a corporate press release, not the conversational Vibes voice!

# ✅ RIGHT - Consistent conversational tone

## Context Optimization Achievement

We compressed the context Claude sees by 59-70% without losing functionality. Here's what that means:

**Before refactor**: Every command loaded 1044 lines of duplicated patterns, examples, and instructions.

**After refactor**:
- Commands load 300-400 lines (reference patterns, don't duplicate)
- Patterns live in `.claude/patterns/` (DRY principle)
- Claude gets the same information but with 59-70% fewer tokens

**Why this matters**: Claude has an "attention budget"—more tokens doesn't mean better results. By compressing context, we improved both speed and accuracy.

See [validation-report.md](prps/prp_context_refactor/execution/validation-report.md) for the full methodology.

# Conversational, explains "why it matters," uses "we" and "you," focuses on learning
```

**Tone consistency guidelines**:

| ✅ Vibes Voice | ❌ Avoid |
|---------------|---------|
| "We compressed..." | "The compression initiative was implemented..." |
| "Here's what that means:" | "Stakeholders should note that..." |
| "Why this matters:" | "The implications of this optimization are..." |
| "Claude sees..." | "The AI system processes..." |
| Active voice | Passive voice |
| Short sentences (10-15 words) | Long, complex sentences (25+ words) |
| Second person ("you") | Third person ("users," "stakeholders") |
| Examples and analogies | Abstract concepts only |

---

## Low Priority Gotchas

### 12. Emoji Overuse Undermining Professionalism

**Severity**: Low
**Category**: Style / Professionalism
**Affects**: Overall README presentation
**Source**: Documentation best practices research

**What it is**:
Excessive use of emojis (🎉 🚀 ✨ 🔥) that undermines technical credibility, especially when used for decoration rather than functional status indicators.

**How to handle**:
```markdown
# ❌ Too many decorative emojis
## 🚀 Context Optimization Achievement 🎉

We did it! 🔥 59-70% reduction! ✨ Amazing results! 🙌

# ✅ Strategic emoji use only
## Context Optimization Achievement

**Results**: 59-70% token reduction ✅

# Use emojis only for:
# - Status indicators: ✅ ❌ 🚧 ⚠️
# - Functional markers in lists/tables
# - Sparingly, with purpose
```

---

### 13. Version-Specific Information Without Dates

**Severity**: Low
**Category**: Maintenance
**Affects**: Time-sensitive claims
**Source**: Documentation maintenance research

**What it is**:
Claiming "current" state or "latest" features without timestamps, making it impossible to know when information was last verified.

**How to handle**:
```markdown
# ❌ Undated claims
## Current Architecture
The latest MCP configuration includes 4 servers...

# ✅ Dated verification
## Current Architecture
*(Verified: 2025-01-15)*

MCP configuration includes 4 active servers...

# Or in validation sections:
### Configuration Validation
```bash
# Last verified: 2025-01-15
jq '.mcpServers | keys' ~/Library/Application\ Support/Claude/claude_desktop_config.json
```
```

---

## MCP-Specific Gotchas

### 14. Transport Type Confusion (STDIO vs HTTP)

**Severity**: Medium
**Category**: MCP Configuration
**Affects**: Server connection methods
**Source**: MCP specification research (Archon)

**What it is**:
Not clarifying which transport type each MCP server uses. STDIO servers use `docker exec`, HTTP servers use `npx mcp-remote` or URLs. Mixing them up breaks connections.

**Why it's a problem**:
- Users try wrong connection method
- "Connection closed" errors with code -32000
- Server appears broken when it's actually a config issue

**How to avoid/fix**:

```markdown
# ❌ UNCLEAR - No transport type indicated

| Server | Purpose | Connection |
|--------|---------|------------|
| archon | Task management | Remote |
| vibesbox | Shell + GUI | Container |

# "Remote" and "Container" don't explain the actual transport mechanism

# ✅ CLEAR - Transport type explicit

| Server | Purpose | Status | Transport | Connection |
|--------|---------|--------|-----------|------------|
| `archon` | Task/knowledge management | ✅ | HTTP (SSE) | `npx mcp-remote http://localhost:8051/mcp` |
| `vibesbox` | Shell + GUI automation | ✅ | STDIO | `docker exec -i mcp-vibesbox-server python3 /workspace/server.py` |
| `basic-memory` | Persistent memory | ✅ | STDIO | `docker exec -i basic-memory-mcp /app/start.sh` |
| `MCP_DOCKER` | Container orchestration | ✅ | STDIO | `docker mcp gateway run` |

**Transport Types**:
- **STDIO**: Process communication via stdin/stdout (docker exec, local processes)
- **HTTP (SSE)**: Server-Sent Events over HTTP (npx mcp-remote, remote servers)
```

**Configuration debugging**:
```bash
# Test STDIO transport
docker exec -i mcp-vibesbox-server python3 /workspace/server.py
# Should start MCP server listening on stdin

# Test HTTP transport
curl http://localhost:8051/mcp
# Should return MCP server info or error
```

---

### 15. MCP Server Dependency Documentation Gap

**Severity**: Medium
**Category**: Setup / Troubleshooting
**Affects**: Initial user setup
**Source**: MCP troubleshooting research

**What it is**:
Not documenting which servers depend on each other, or external dependencies (Node.js version, Python packages, Docker versions).

**Why it's a problem**:
- Setup fails with cryptic errors
- Users don't know which server to start first
- Missing dependencies cause silent failures

**How to avoid/fix**:

```markdown
# ❌ MISSING - No dependency information

## Quick Start
Start all MCP servers and configure Claude Desktop.

# ✅ COMPLETE - Dependencies and order documented

## Quick Start

### Prerequisites

**System Requirements**:
- Docker Desktop 4.0+
- Node.js 18+ (for archon server)
- Python 3.9+ (for STDIO servers)
- Claude Desktop (latest version)

**MCP Server Dependencies**:

1. **Infrastructure** (start first):
   ```bash
   # Create shared network
   docker network create vibes-network

   # Start core containers
   docker-compose -f mcp/mcp-vibesbox-server/docker-compose.yml up -d
   docker-compose -f mcp/basic-memory/docker-compose.yml up -d
   ```

2. **Archon** (external service):
   ```bash
   # Requires Supabase account and OpenAI API key
   # See: https://github.com/coleam00/Archon
   # Runs on: http://localhost:8051
   ```

3. **MCP Gateway** (optional, for orchestration):
   ```bash
   docker mcp gateway run
   # Requires: Docker Desktop with MCP Toolkit enabled
   ```

**Startup Order**:
1. vibes-network (shared networking)
2. vibesbox + basic-memory (core services)
3. Archon (external, HTTP-based)
4. MCP_DOCKER gateway (optional)
5. Configure Claude Desktop
6. Restart Claude Desktop

**Dependency Graph**:
```
archon (HTTP:8051) ──┐
                     ├─→ Claude Desktop
vibesbox (STDIO) ────┤
basic-memory (STDIO) ┤
MCP_DOCKER (STDIO) ──┘
```
```

---

## Anti-Patterns to Avoid

### 1. README as Dumping Ground

**What it is**: Adding every new feature, achievement, or configuration detail to README without considering structure or audience.

**Why it's bad**:
- README becomes overwhelming (1000+ lines)
- Can't find critical information
- Violates progressive disclosure

**Better pattern**:
```markdown
# Instead of dumping everything in README:
## New Feature: Advanced Archon Configuration
[500 lines of configuration options...]

# Create separate doc and link:
## Advanced Configuration
For Archon configuration options, see [docs/archon-config.md](docs/archon-config.md).

Quick start (most users):
- Default config works out of the box
- Edit `ARCHON_API_KEY` in `.env`
- Restart Archon service
```

---

### 2. Copy-Paste Configuration Without Testing

**What it is**: Copying configuration examples from other projects without verifying they work in your setup.

**Why it's bad**:
- Paths might be wrong for your structure
- Server names might not match
- Creates setup frustration

**Better pattern**:
```bash
# Before adding config to README:

# 1. Create test config file
# 2. Actually test it works
# 3. Verify paths are relative to user's system
# 4. Include validation command

# Example:
# After copying this config, verify with:
jq . ~/Library/Application\ Support/Claude/claude_desktop_config.json
# Expected: No errors, config parsed successfully
```

---

### 3. Metrics Without Methodology

**What it is**: Claiming "59-70% reduction" without explaining how it was measured or how to reproduce it.

**Why it's bad**:
- Can't verify claims
- Can't reproduce results
- Appears like marketing fluff

**Better pattern**:
```markdown
## Context Optimization: 59-70% Reduction

**Methodology**:
1. Measured baseline: `wc -w .claude/commands/*.md` (before refactor)
2. Applied DRY principle: extracted patterns to `.claude/patterns/`
3. Updated commands to reference patterns instead of duplicating
4. Measured result: `wc -w .claude/commands/*.md` (after refactor)
5. Calculated: (before - after) / before × 100

**Reproduction**:
```bash
# See full calculation in validation report
cat prps/prp_context_refactor/execution/validation-report.md
```

**Results**:
- /generate-prp: 1044 → 427 lines (59% reduction)
- /execute-prp: 1044 → 309 lines (70% reduction)
```

---

### 4. Silent Breaking Changes

**What it is**: Updating README to reflect new state without mentioning what changed or providing migration guidance.

**Why it's bad**:
- Existing users' setups break
- No upgrade path documented
- Creates support burden

**Better pattern**:
```markdown
## Migration Guide (for existing users)

### What Changed
The context refactor introduced `.claude/` directory structure. If you have an older Vibes setup:

**Before** (pre-context refactor):
- Patterns were embedded in command files
- Commands were 1000+ lines each

**After** (post-context refactor):
- Patterns extracted to `.claude/patterns/`
- Commands reference patterns (300-400 lines)

**Action Required**:
1. Pull latest changes: `git pull`
2. New files will appear in `.claude/` directory
3. Old command references updated automatically
4. No configuration changes needed

**Backward Compatibility**: Old PRP format still works, new PRPs use pattern references.
```

---

## Gotcha Checklist for Implementation

Before marking README update complete, verify these gotchas are addressed:

### Content & Accuracy
- [ ] **No CLAUDE.md duplication**: Archon workflow in CLAUDE.md, not README
- [ ] **All 4 MCP servers listed**: archon, vibesbox, basic-memory, MCP_DOCKER
- [ ] **Status indicators accurate**: All ✅ Active verified against actual config
- [ ] **Line counts current**: CLAUDE.md = 107, generate-prp = 320, execute-prp = 202
- [ ] **Metrics verified**: 59-70% reduction calculation shown and validated

### Links & References
- [ ] **All file links valid**: Test each `.claude/patterns/` link exists
- [ ] **Section anchors correct**: #heading links match actual headings
- [ ] **External URLs reachable**: Test GitHub links, Archon docs, etc.
- [ ] **Progressive disclosure ≤2 levels**: README → details (not README → index → details)

### Formatting & Syntax
- [ ] **Tables render correctly**: Blank lines before/after, 3+ hyphens, even columns
- [ ] **JSON valid**: No trailing commas, all quotes, brackets balanced
- [ ] **Markdown valid**: Preview on GitHub before committing
- [ ] **Code blocks have language tags**: ```bash, ```json, ```markdown

### Structure & Organization
- [ ] **Directory structure current**: Shows `.claude/` directory structure
- [ ] **Capabilities specific**: Each capability mentions which MCP server provides it
- [ ] **Tone consistent**: Conversational voice maintained throughout
- [ ] **No over-compression**: Critical context preserved, examples included

### MCP-Specific
- [ ] **Transport types clear**: STDIO vs HTTP indicated for each server
- [ ] **Dependencies documented**: Startup order, system requirements, version needs
- [ ] **Configuration complete**: All 4 servers in JSON example
- [ ] **Connection methods accurate**: Match actual claude_desktop_config.json

---

## Validation Scripts

### Pre-Commit Validation
```bash
#!/bin/bash
# .github/scripts/validate_readme.sh

echo "🔍 Validating README.md before commit..."

# 1. Check line count claims
expected_claude=107
actual_claude=$(wc -l < CLAUDE.md)
if [ "$actual_claude" != "$expected_claude" ]; then
    echo "❌ CLAUDE.md line count mismatch: expected $expected_claude, got $actual_claude"
    exit 1
fi

# 2. Validate JSON syntax
jq empty < README.md | grep -Pzo '(?s)\{[^}]+mcpServers[^}]+\}' > /tmp/readme_json.json 2>/dev/null
if ! jq . /tmp/readme_json.json > /dev/null 2>&1; then
    echo "❌ JSON configuration in README is invalid"
    exit 1
fi

# 3. Check for broken links
while IFS= read -r link; do
    if [[ ! "$link" =~ ^http ]] && [[ ! -f "$link" ]]; then
        echo "❌ Broken link: $link"
        exit 1
    fi
done < <(grep -oP '\[.*?\]\(\K[^)#]+(?=\))' README.md)

# 4. Verify MCP server count
server_count=$(grep -c "| \`.*\` |" README.md)
if [ "$server_count" -lt 4 ]; then
    echo "❌ Expected 4 MCP servers in table, found $server_count"
    exit 1
fi

# 5. Check for CLAUDE.md duplication
if grep -q "find_tasks.*manage_task.*doing" README.md; then
    echo "❌ Archon workflow duplication detected (should be in CLAUDE.md only)"
    exit 1
fi

echo "✅ All validations passed!"
```

### Link Checker
```python
#!/usr/bin/env python3
# scripts/check_readme_links.py

import re
import os
from pathlib import Path

readme = Path("README.md").read_text()

# Extract all links
links = re.findall(r'\[([^\]]+)\]\(([^)]+)\)', readme)

errors = []

for text, link in links:
    # Skip external URLs and anchors
    if link.startswith('http') or link.startswith('#'):
        continue

    # Check file exists
    filepath = Path(link.split('#')[0])  # Remove anchor
    if not filepath.exists():
        errors.append(f"❌ Broken link: [{text}]({link}) - file not found")

# Check section anchors
anchors = re.findall(r'\[([^\]]+)\]\(#([^)]+)\)', readme)
headings = re.findall(r'^#+\s+(.+)$', readme, re.MULTILINE)
heading_anchors = {h.lower().replace(' ', '-').replace('&', '') for h in headings}

for text, anchor in anchors:
    if anchor not in heading_anchors:
        errors.append(f"❌ Broken anchor: [{text}](#{anchor}) - no matching heading")

if errors:
    print("\n".join(errors))
    exit(1)
else:
    print("✅ All links valid")
```

---

## Confidence Assessment

**Gotcha Coverage**: 9/10

### Comprehensive Coverage
- **Documentation**: Common README mistakes, progressive disclosure anti-patterns ✅
- **MCP Servers**: Configuration errors, transport confusion, dependency gaps ✅
- **Context Engineering**: Duplication risks, over-compression, metrics drift ✅
- **Markdown**: Table formatting, JSON syntax, link rot ✅
- **Tone & Style**: Voice consistency, professionalism, audience awareness ✅

### Gaps
- **Platform-specific rendering**: Some Markdown renderers have unique quirks (low risk for GitHub)
- **Accessibility**: Alt text for images, screen reader considerations (README has minimal images)
- **Internationalization**: Non-English documentation challenges (not applicable for this project)

### Research Quality
- **Archon sources**: 3 sources searched (MCP docs, context engineering, PRPs)
- **Web sources**: 5 targeted searches (README best practices, Markdown gotchas, MCP troubleshooting, context compression, progressive disclosure)
- **Local codebase**: Analyzed current README.md, CLAUDE.md, validation reports, pattern library
- **Real examples**: All gotchas include actual code from Vibes project

### Solution Completeness
Every gotcha includes:
- ✅ Clear description of the problem
- ✅ Why it's a problem (impact)
- ✅ How to detect it (symptoms)
- ✅ **How to avoid/fix it** (solution with code)
- ✅ Validation method or test

---

## Recommendations for PRP Assembly

When generating the final PRP:

1. **Reference critical gotchas in "Known Gotchas & Library Quirks"**:
   - Gotcha #1 (CLAUDE.md duplication) → Add to validation gates
   - Gotcha #2 (MCP server status) → Verify against config in assembly
   - Gotcha #3 (Metrics drift) → Run line count validation before delivery
   - Gotcha #4 (Markdown tables) → Include formatting checklist

2. **Add validation gates based on gotchas**:
   - **Gate 1**: No CLAUDE.md duplication (search for specific Archon workflow text)
   - **Gate 2**: JSON config valid (jq validation)
   - **Gate 3**: All links valid (run link checker script)
   - **Gate 4**: Line counts accurate (automated verification)
   - **Gate 5**: MCP servers match config (diff against actual config file)

3. **Include gotcha-prevention checklists in Implementation Blueprint**:
   - Pre-write checklist: Verify line counts, validate config, test links
   - Post-write checklist: Run validation scripts, preview on GitHub, test one config example
   - Pre-commit checklist: All 15 gotchas addressed

4. **Reference gotcha solutions in task steps**:
   - Task: "Add MCP server table" → Reference Gotcha #4 (table formatting)
   - Task: "Update context optimization section" → Reference Gotcha #3 (metrics drift)
   - Task: "Add pattern library reference" → Reference Gotcha #5 (progressive disclosure)

5. **Provide gotcha-aware implementation examples**:
   - Show correct table format (from Gotcha #4)
   - Show correct progressive disclosure (from Gotcha #5)
   - Show correct tone (from Gotcha #11)
   - Show correct JSON (from Gotcha #8)

---

## Sources Referenced

### From Archon
- **d60a71d62eb201d5** (MCP Protocol Specification): Transport types, configuration patterns, MCP server architecture
- **b8565aff9938938b** (Context Engineering Intro): README validation checklists, anti-patterns documentation
- **c0e629a894699314** (Pydantic.ai): Configuration validation patterns (limited relevance)

### From Web
- **README Best Practices** (makeareadme.com, jehna/readme-best-practices, freecodecamp): Common mistakes, quality issues, content organization
- **Markdown Table Formatting** (Stack Overflow, GitHub issues): Separator row errors, column count issues, special character handling
- **MCP Troubleshooting** (mcp.harishgarg.com, dev.to, GitHub issues): Configuration errors, connection issues, dependency problems
- **Context Compression Research** (LangChain, arXiv papers): Information loss, cost trade-offs, optimization pitfalls
- **Progressive Disclosure** (Nielsen Norman Group, GitLab Design): Anti-patterns, layer limits, discoverability issues

### From Local Codebase
- **README.md**: Current structure, tone patterns, existing gotchas
- **CLAUDE.md**: Two-level disclosure pattern, Archon workflow
- **prps/prp_context_refactor/execution/validation-report.md**: Line count methodology, reduction metrics
- **.claude/patterns/README.md**: Pattern library structure, quick reference format
- **claude_desktop_config.json**: Actual MCP server configuration (4 servers)

---

## Final Notes

**Most Critical Gotchas** (address these first):
1. **CLAUDE.md duplication** (#1) - Violates entire context refactor achievement
2. **MCP server status accuracy** (#2) - Breaks user setup immediately
3. **Metrics drift** (#3) - Damages credibility of achievements

**Quick Wins** (easy to fix, high impact):
- Validate JSON syntax before committing (#8)
- Run link checker script (#7)
- Preview tables on GitHub (#4)

**Pattern for Success**:
1. Write README updates
2. Run validation scripts (provided in this doc)
3. Verify against gotcha checklist
4. Test actual user flow (clone repo, follow setup, verify servers load)
5. Commit with confidence

**Remember**: The README is the first impression. Getting it right means users succeed faster, trust the project more, and can focus on building instead of debugging documentation issues.
