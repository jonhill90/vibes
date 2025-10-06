# Source: README.md and .claude/patterns/README.md
# Pattern: Section headers and content structure
# Extracted: 2025-10-05
# Relevance: 9/10 - Shows how to maintain consistent README style

## Existing Section Pattern (from README.md)

```markdown
## Quick Start

### Prerequisites
- Docker Desktop
- Claude Desktop
- Git

### 1. Clone Repository
[bash code block]

### 2. Start MCP Servers
[bash code block]

### 3. Configure Claude Desktop MCP Settings
[explanation + code block]

### 4. Restart Claude Desktop
[brief instruction]
```

## Pattern Library Section Pattern (from .claude/patterns/README.md)

```markdown
# PRP System Patterns - Index

This directory contains reusable implementation patterns extracted from the PRP generation and execution system. Each pattern is self-contained with code examples, gotchas, and usage guidance.

## Quick Reference

**Need to...** | **See Pattern** | **Used By**
---|---|---
Extract secure feature names | [security-validation.md](security-validation.md) | All commands
Integrate with Archon MCP | [archon-workflow.md](archon-workflow.md) | generate-prp, execute-prp

## Pattern Categories

### Security Patterns
- **[security-validation.md](security-validation.md)**: Feature name extraction with 5-level security validation
  - Use when: Accepting user input for file paths or feature names
  - Key benefit: Prevents path traversal, command injection, and directory traversal
```

## What to Mimic

### 1. **Section Header Hierarchy**
- `##` for main sections (Quick Start, Context Engineering & PRPs)
- `###` for subsections (Prerequisites, 1. Clone Repository)
- `####` for sub-subsections (rarely used, only when needed)

### 2. **Brief Introductory Paragraph**
- 1-2 sentences explaining the section
- Example: "This directory contains reusable implementation patterns..."
- Keep it conversational, not corporate

### 3. **Table for Quick Reference**
- Use when listing 3+ items with properties
- Pattern: | What | Where | Why | format
- Example: Quick Reference table in patterns/README.md

### 4. **List Format for Features**
- Use `-` bullets for simple lists
- Use `###` numbered subsections for sequential steps
- Use `**bold**` for emphasis on key terms

### 5. **Progressive Disclosure**
- Overview → Details → Link to more
- Example: "Learn More" section at bottom
- Don't duplicate content, link to it

## What to Adapt

### For New "Context Optimization" Section
```markdown
## Context Optimization

Vibes achieved 59-70% token reduction through aggressive context engineering. The refactoring compressed all context files while preserving functionality:

**Results**:
- CLAUDE.md: 107 lines (from 143, 25% reduction)
- Patterns: 47-150 lines each (avg 120 lines)
- Commands: 202-320 lines each (avg 261 lines)
- Total reduction: 59-70% per command invocation

[Learn more](prps/prp_context_refactor.md) about the context engineering process.
```

### For New "Pattern Library" Section
```markdown
## Pattern Library

The `.claude/patterns/` directory contains reusable implementation patterns extracted from the PRP system. These patterns enable consistent, high-quality implementations.

**Key Patterns**:
- **[archon-workflow.md](claude/patterns/archon-workflow.md)**: Archon MCP integration, health checks, graceful degradation
- **[parallel-subagents.md](.claude/patterns/parallel-subagents.md)**: 3x speedup through multi-task parallelization
- **[quality-gates.md](.claude/patterns/quality-gates.md)**: Validation loops ensuring 8+/10 PRP scores
- **[security-validation.md](.claude/patterns/security-validation.md)**: 5-level security checks for user input

See [.claude/patterns/README.md](.claude/patterns/README.md) for complete pattern documentation.
```

## What to Skip

- Don't use `####` unless absolutely necessary (2 levels max)
- Don't create walls of text (break up with headers/lists)
- Don't duplicate content from linked files
- Don't use corporate language ("leverage", "utilize", "synergy")

## Pattern Highlights

### Conversational Tone Examples
```markdown
# Good (conversational, friendly)
"Vibes transforms Claude Desktop into a conversational development environment"
"Instead of learning command-line tools, you describe what you want to build"
"Ask → Build → Understand → Improve → Create"

# Bad (corporate, formal)
"Vibes leverages the Claude Desktop platform to facilitate development workflows"
"The system provides a methodology for implementing features through natural language"
"Strategic Planning → Technical Implementation → Knowledge Acquisition → Optimization → Production"
```

### Progressive Disclosure Pattern
```markdown
## Topic

Brief overview (1-2 sentences).

**Key Points**: (3-5 bullets)
- Point 1
- Point 2

[Learn more](link/to/detailed/docs.md) about this topic.
```

## Why This Example

The README has an established voice and structure. New sections must match this style to maintain consistency. The pattern library README demonstrates the "quick reference table + categorized list" pattern that works well for documentation sections.

### Directory Structure Example Pattern
The current README shows outdated `prps/` structure. Here's the pattern to follow when documenting `.claude/`:

```markdown
### Directory Structure

```
vibes/
├── .claude/              # Claude Code project context
│   ├── commands/         # Slash commands (generate-prp, execute-prp)
│   ├── patterns/         # Reusable implementation patterns
│   ├── agents/           # Subagent definitions for parallel execution
│   └── templates/        # Report templates (validation, completion)
├── prps/                 # PRP workspace
│   ├── {feature}/        # Per-feature PRP directory
│   │   ├── INITIAL.md    # Feature description
│   │   ├── prp_{feature}.md  # Generated PRP
│   │   ├── planning/     # Research outputs
│   │   ├── examples/     # Code examples
│   │   └── execution/    # Implementation artifacts
│   └── templates/        # PRP templates
└── mcp/                  # MCP server implementations
    ├── mcp-vibesbox-server/
    └── basic-memory-mcp/
```
```

**Key Directories**:
- `.claude/`: Context engineering and command definitions
- `prps/`: PRP generation and execution workspace
- `mcp/`: MCP server containers
