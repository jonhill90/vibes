---
name: create-skill
description: Guide for creating effective Claude Code skills. Use when designing, structuring, or building new skills with scripts, references, and assets.
---

# Skill Creator

Guide for creating effective skills for Claude Code.

## What Skills Provide

1. **Specialized workflows** - Multi-step procedures for specific domains
2. **Tool integrations** - Instructions for working with file formats or APIs
3. **Domain expertise** - Company-specific knowledge, schemas, business logic
4. **Bundled resources** - Scripts, references, and assets for complex tasks

## Core Principles

### Concise is Key

The context window is a public good. Challenge each piece of information: "Does Claude really need this?" Prefer concise examples over verbose explanations.

### Degrees of Freedom

Match specificity to task fragility:

- **High freedom** (text instructions): Multiple valid approaches, context-dependent
- **Medium freedom** (pseudocode/scripts with params): Preferred pattern with variation
- **Low freedom** (specific scripts): Fragile operations, consistency critical

## Skill Structure

```
skill-name/
├── SKILL.md (required)
│   ├── YAML frontmatter (name, description)
│   └── Markdown instructions
└── Optional Resources
    ├── scripts/      - Executable code (Python/Bash)
    ├── references/   - Docs loaded on demand
    └── assets/       - Templates, images for output
```

### SKILL.md

- **Frontmatter**: `name` and `description` are the PRIMARY trigger mechanism
- **Body**: Instructions loaded AFTER skill triggers

### Supporting Files

**scripts/** - For deterministic, repeatable code:
```
scripts/rotate_pdf.py
```

**references/** - Documentation loaded as needed:
```
references/api-docs.md
references/schemas.md
```

**assets/** - Files used in output (not loaded into context):
```
assets/template.docx
assets/logo.png
```

### What NOT to Include

- README.md
- CHANGELOG.md
- INSTALLATION_GUIDE.md
- Any human-facing auxiliary documentation

## Progressive Disclosure

Three-level loading:
1. **Metadata** (name + description) - Always in context (~100 words)
2. **SKILL.md body** - When skill triggers (<500 lines)
3. **Bundled resources** - As needed (unlimited)

### Pattern 1: High-level guide with references

```markdown
# PDF Processing

## Quick start
[core example]

## Advanced features
- **Form filling**: See [forms.md](references/forms.md)
- **API reference**: See [api.md](references/api.md)
```

### Pattern 2: Domain organization

```
bigquery-skill/
├── SKILL.md
└── references/
    ├── finance.md
    ├── sales.md
    └── product.md
```

User asks about sales → only load sales.md

### Pattern 3: Conditional details

```markdown
## Basic usage
[simple instructions]

**For advanced config**: See [advanced.md](references/advanced.md)
```

## Creation Process

### 1. Understand with Examples

Ask:
- "What functionality should this skill support?"
- "What would a user say to trigger this?"
- "What are common use cases?"

### 2. Plan Reusable Contents

For each example, identify:
- What scripts would be rewritten repeatedly?
- What references would Claude need?
- What assets would be used in output?

### 3. Create the Skill

```bash
mkdir -p .github/skills/my-skill
```

### 4. Write SKILL.md

**Frontmatter:**
```yaml
---
name: my-skill
description: [What it does AND when to use it. This is the trigger.]
---
```

**Body:**
- Use imperative form ("Create...", "Run...")
- Keep under 500 lines
- Reference supporting files with clear "when to read" guidance

### 5. Validate

```
/validate-skill .github/skills/my-skill
```

### 6. Iterate

1. Use the skill on real tasks
2. Notice struggles or inefficiencies
3. Update SKILL.md or resources
4. Test again

## Frontmatter Options

See `.claude/references/skills-guide.md` for all options:

| Field | Purpose |
|-------|---------|
| `name` | Identifier (lowercase, hyphens) |
| `description` | **Primary trigger** - when to use |
| `argument-hint` | Autocomplete hint `[arg]` |
| `disable-model-invocation` | Manual-only (`true`) |
| `user-invocable` | Hide from menu (`false`) |
| `allowed-tools` | Restrict tools |
| `context: fork` | Run in subagent |
| `agent` | Which subagent type |

## Naming Conventions

- Lowercase letters, digits, hyphens only
- Under 64 characters
- Prefer verb-led phrases: `create-report`, `review-pr`
- Directory name must match `name` field
