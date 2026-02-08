---
name: validate-skill
description: Validate a SKILL.md file against the Agent Skills specification. Use when checking if a skill is correctly formatted.
argument-hint: [path/to/skill]
---

# Skill Validator

Validate a skill file against the Agent Skills specification.

## Validation Checklist

### Required Structure
- [ ] File is named `SKILL.md`
- [ ] Starts with YAML frontmatter between `---` markers
- [ ] Has markdown content after frontmatter

### Frontmatter Fields
- [ ] `name` - lowercase letters, numbers, hyphens only (max 64 chars)
- [ ] `name` matches the directory name
- [ ] `description` - present and meaningful (1-1024 chars)

### Optional Frontmatter (validate if present)
- [ ] `argument-hint` - string like `[issue-number]`
- [ ] `disable-model-invocation` - boolean
- [ ] `user-invocable` - boolean
- [ ] `allowed-tools` - comma-separated tool names
- [ ] `model` - valid model name
- [ ] `context` - only valid value is `fork`
- [ ] `agent` - agent name (requires `context: fork`)
- [ ] `hooks` - valid hook configuration

### Content Quality
- [ ] Instructions are clear and actionable
- [ ] Under 500 lines (use reference files for more)
- [ ] No README.md in the skill directory

### Supporting Files (if present)
- [ ] Scripts in `scripts/` are executable
- [ ] Reference files are linked from SKILL.md

## How to Validate

1. Read the SKILL.md file at `$ARGUMENTS`
2. Check each item in the checklist
3. Report results as:

**Valid** - All checks pass

**Warnings** - Non-critical issues:
- Missing optional fields
- Long descriptions

**Errors** - Must fix:
- Missing required fields
- Invalid name format
- Name doesn't match directory

## Output Format

```
## Skill Validation: [skill-name]

**Status**: Valid / Has Warnings / Invalid

### Errors (if any)
- [error description]

### Warnings (if any)
- [warning description]

### Checklist
- [x] Item passed
- [ ] Item failed: reason
```
