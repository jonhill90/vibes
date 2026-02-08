# Repository Conventions

Naming and structure conventions for this repository.

---

## Naming Conventions

### General Rules

- Use `kebab-case` for all directories and files (except SKILL.md, CLAUDE.md)
- Capitalize special files: `SKILL.md`, `CLAUDE.md`, `README.md`

### By Component Type

| Component | Location | Main File | Example |
|-----------|----------|-----------|---------|
| Skill | `.claude/skills/skill-name/` | `SKILL.md` | `.claude/skills/explain-code/SKILL.md` |
| Agent | `.claude/agents/` | `agent-name.md` | `.claude/agents/researcher.md` |
| Rule | `.claude/rules/` | `rule-name.md` | `.claude/rules/typescript.md` |
| Reference | `.claude/references/` | `topic.md` | `.claude/references/memory-system.md` |
| Template | `templates/` | varies | `templates/skills/minimal/SKILL.md` |

### Skill Names (in YAML frontmatter)

- Lowercase only
- Hyphens for word separation
- Must match directory name
- Examples: `explain-code`, `review-pr`, `commit`

---

## Directory Structure

### Skills

```
.claude/skills/skill-name/
├── SKILL.md           # Required: instructions and frontmatter
├── references/        # Optional: detailed reference files
│   └── advanced.md
├── scripts/           # Optional: helper scripts
│   └── helper.sh
└── assets/            # Optional: templates, configs
    └── template.txt
```

**Rules:**
- SKILL.md is the only required file
- No README.md (use SKILL.md for all documentation)
- scripts/ must be executable (chmod +x)

### Agents

```
.claude/agents/
├── researcher.md
├── code-reviewer.md
└── debugger.md
```

**Rules:**
- Single markdown file per agent
- Filename = agent identifier

### Rules

```
.claude/rules/
├── typescript.md      # Path-specific rules
├── testing.md
└── documentation.md
```

**Rules:**
- Use `paths:` frontmatter for file-specific rules
- Omit `paths:` for global rules

### References

```
.claude/references/
├── memory-system.md   # Core documentation
├── skills-guide.md
├── subagents-guide.md
├── hooks-guide.md
└── patterns/          # Design patterns
    ├── skill-patterns.md
    ├── agent-patterns.md
    └── memory-patterns.md
```

---

## What NOT to Include

### Inside Skill Directories

- README.md (use SKILL.md)
- CHANGELOG.md
- INSTALLATION_GUIDE.md
- Any human-facing auxiliary documentation

### Anywhere in Repository

- Binaries or compiled code
- Large files (>1MB)
- Sensitive information (API keys, credentials)
- Duplicate content
