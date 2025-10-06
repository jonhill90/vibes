# Source: README.md lines 99-114 (current) + actual .claude/ structure
# Pattern: Directory tree visualization in README
# Extracted: 2025-10-05
# Relevance: 10/10 - Shows exact format to use for .claude/ documentation

## Current Directory Listing (Outdated)

```markdown
### Directory Structure

```
vibes/
├── prps/
│   ├── templates/        # PRP templates for different types
│   │   ├── prp_base.md          # Comprehensive base template
│   │   ├── feature_template.md  # Standard features
│   │   ├── tool_template.md     # API integrations
│   │   └── documentation_template.md  # Documentation
│   ├── active/           # In-progress PRPs
│   ├── completed/        # Finished PRPs
│   └── archived/         # Old reference PRPs
└── examples/             # Reference patterns and examples
    ├── prp-workflow/     # Example PRPs
    ├── tools/            # Code patterns (API, files, etc.)
    └── documentation/    # Doc templates
```
```

## Updated Directory Listing (With .claude/)

```markdown
### Directory Structure

```
vibes/
├── .claude/              # Claude Code project context
│   ├── commands/         # Slash commands (/generate-prp, /execute-prp)
│   ├── patterns/         # Reusable implementation patterns
│   ├── agents/           # Subagent definitions for parallel execution
│   └── templates/        # Report templates (validation, completion)
├── prps/                 # PRP workspace
│   ├── {feature}/        # Per-feature PRP directory
│   │   ├── INITIAL.md    # Feature description
│   │   ├── prp_{feature}.md      # Generated PRP
│   │   ├── planning/     # Research outputs (feature-analysis.md, etc.)
│   │   ├── examples/     # Extracted code examples
│   │   └── execution/    # Implementation artifacts
│   └── templates/        # PRP templates (base, feature, tool, docs)
└── mcp/                  # MCP server implementations
    ├── mcp-vibesbox-server/
    └── basic-memory-mcp/
```
```

## What to Mimic

### 1. **Tree Structure Format**
```
directory/
├── subdirectory/         # Description
│   ├── file.md          # Description
│   └── file2.md         # Description
└── another/             # Description
```

### 2. **Inline Comments Pattern**
- Use `# Description` after directory/file names
- Keep descriptions brief (3-7 words)
- Explain purpose, not contents

### 3. **Placeholder Syntax**
- Use `{variable}` for dynamic names
- Example: `{feature}/` means any feature name
- Helps readers understand pattern

### 4. **Grouping by Purpose**
- `.claude/` = Context/commands (Claude Code specific)
- `prps/` = PRP workflow workspace
- `mcp/` = Server implementations

### 5. **Two-Level Maximum**
- Top level: major directories
- One level down: key subdirectories
- Use `...` if more levels exist but not shown

## What to Adapt

### Add .claude/ Documentation
The current README is missing `.claude/` entirely. Add it as first item:

```markdown
├── .claude/              # Claude Code project context
│   ├── commands/         # Slash commands (/generate-prp, /execute-prp)
│   ├── patterns/         # Reusable implementation patterns
│   ├── agents/           # Subagent definitions for parallel execution
│   └── templates/        # Report templates (validation, completion)
```

### Update prps/ Structure
Current README shows outdated `active/completed/archived` structure. Update to:

```markdown
├── prps/                 # PRP workspace
│   ├── {feature}/        # Per-feature PRP directory
│   │   ├── INITIAL.md    # Feature description (user writes this)
│   │   ├── prp_{feature}.md      # Generated PRP (system creates this)
│   │   ├── planning/     # Research outputs (feature-analysis.md, etc.)
│   │   ├── examples/     # Extracted code examples
│   │   └── execution/    # Implementation artifacts
│   └── templates/        # PRP templates (base, feature, tool, docs)
```

### Keep mcp/ Simple
```markdown
└── mcp/                  # MCP server implementations
    ├── mcp-vibesbox-server/
    └── basic-memory-mcp/
```

## What to Skip

- Don't list every file (just representative samples)
- Don't go deeper than 2-3 levels
- Don't duplicate file purposes already explained in other sections
- Don't show `.git/`, `node_modules/`, etc. (irrelevant)

## Pattern Highlights

### Comment Style Guidelines

```markdown
# Good comments (purpose-focused)
├── commands/         # Slash commands (/generate-prp, /execute-prp)
├── patterns/         # Reusable implementation patterns
├── {feature}/        # Per-feature PRP directory

# Bad comments (too vague)
├── commands/         # Commands
├── patterns/         # Patterns
├── {feature}/        # Feature

# Bad comments (too verbose)
├── commands/         # Directory containing all the slash command definitions for the PRP system
```

### Placeholder Patterns

```markdown
# Dynamic directory names
{feature}/            # Shows this is variable
prp_{feature}.md      # Shows file naming pattern

# Specific examples where helpful
mcp-vibesbox-server/  # Actual directory name
basic-memory-mcp/     # Actual directory name
```

### Description Length
- Aim for 3-7 words
- Use gerund verbs: "Containing...", "Defining..."
- Or noun phrases: "Research outputs", "Code examples"

## Why This Example

The current README has an established tree visualization format that works well. The issue is:
1. Missing `.claude/` directory entirely
2. Showing outdated `prps/` structure (active/completed/archived)
3. Not showing the actual per-feature structure

This example shows how to maintain the existing ASCII tree style while updating to reflect current reality.

## Actual .claude/ Structure

For reference, here's what actually exists:

```
.claude/
├── agents/               # 13 agent definition files
│   ├── prp-gen-*.md     # PRP generation agents (6 files)
│   ├── prp-exec-*.md    # PRP execution agents (5 files)
│   └── validation-gates.md
├── commands/             # 7 command files
│   ├── generate-prp.md
│   ├── execute-prp.md
│   └── [5 other commands]
├── patterns/             # 5 pattern files
│   ├── archon-workflow.md
│   ├── parallel-subagents.md
│   ├── quality-gates.md
│   ├── security-validation.md
│   └── README.md
└── templates/            # 2 template files
    ├── validation-report.md
    └── completion-report.md
```

**For README, simplify to**:
```markdown
├── .claude/              # Claude Code project context
│   ├── commands/         # Slash commands (/generate-prp, /execute-prp)
│   ├── patterns/         # Reusable implementation patterns
│   ├── agents/           # Subagent definitions for parallel execution
│   └── templates/        # Report templates (validation, completion)
```

This gives readers the structure without overwhelming detail.
