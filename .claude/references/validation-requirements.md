# Validation Requirements

How to validate skills, agents, and rules.

---

## Validating Skills

Use the `/validate-skill` skill to check SKILL.md files:

```
/validate-skill .claude/skills/my-skill
```

### What Gets Checked

**Required:**
- SKILL.md exists and is readable
- YAML frontmatter is valid
- Required fields: `name`, `description`
- Name format (lowercase, hyphens only, max 64 chars)
- Name matches directory name
- Content exists after frontmatter

**Warnings:**
- Description length (should be 1-1024 chars)
- No README.md in skill directory
- Scripts in `scripts/` should be executable
- SKILL.md over 500 lines

### Common Issues

| Issue | Cause | Fix |
|-------|-------|-----|
| Missing required field | No `name:` or `description:` | Add to frontmatter |
| Invalid name format | Uppercase or special chars | Use lowercase with hyphens |
| Name mismatch | `name:` differs from directory | Make them match |
| README.md found | Extra file in skill dir | Remove it, use SKILL.md |

---

## Validating Agents

Agents are simpler - just check:

1. File is in `.claude/agents/`
2. Has YAML frontmatter with `name` and `description`
3. Filename matches the `name` field
4. Body contains system prompt

---

## Validating Rules

Rules in `.claude/rules/` should:

1. Be markdown files (`.md`)
2. If path-specific, have valid `paths:` frontmatter with glob patterns
3. Contain clear instructions

---

## Testing Components

### Test a Skill

```
/my-skill [test arguments]
```

### Test an Agent

Ask Claude to use it:
```
Use the code-reviewer agent to review this file
```

### Test a Rule

Edit a file matching the rule's path pattern and verify Claude follows the instructions.
