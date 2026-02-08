# Contribution Workflow

Step-by-step processes for contributing to this repository.

---

## Adding a New Skill

### 1. Start from Template

```bash
cp -r templates/skills/minimal .claude/skills/my-skill
cd .claude/skills/my-skill
```

### 2. Edit SKILL.md

Update frontmatter:
```yaml
---
name: my-skill-name
description: "Clear description of when to use this skill"
---
```

Write instructions (the body content).

### 3. Add Optional Components

- `references/` - For skills >500 lines, move details here
- `scripts/` - Helper scripts (make executable)
- `assets/` - Templates, configs, static files

### 4. Validate

```bash
./tools/validators/skill-validator.sh .claude/skills/my-skill
```

### 5. Test

```bash
# From project root
claude /my-skill
```

---

## Adding a New Agent

### 1. Create Agent File

```bash
touch .claude/agents/my-agent.md
```

### 2. Add Frontmatter and Instructions

```yaml
---
name: my-agent
description: What my agent does
tools: Read, Grep, Glob
model: haiku
---

You are a specialist in...
```

---

## Adding a New Rule

### 1. Create Rule File

```bash
touch .claude/rules/my-rule.md
```

### 2. Add Path Patterns and Instructions

```yaml
---
paths:
  - "**/*.py"
---

Python coding conventions:
- Use type hints
- Follow PEP 8
```

---

## Updating Reference Documentation

Reference documentation lives in `.claude/references/`:

1. Edit the relevant file
2. Keep under 500 lines (link to deeper references if needed)
3. Verify code examples work

---

## Commit and PR Guidelines

### Commit Messages

Use clear, descriptive messages:

```
Add skill: explain-code with diagram support
Fix: skill validator handles multiline descriptions
Update: improve memory-system documentation
```

Format: `<action>: <brief description>`

Actions: Add, Fix, Update, Remove, Refactor

### PR Checklist

Before submitting:

- [ ] All validators pass
- [ ] Skills tested with `claude /skill-name`
- [ ] No sensitive information included
- [ ] Follows naming conventions

### Branch Naming

```
feature/add-explain-code-skill
fix/validator-multiline-bug
docs/improve-memory-guide
```
