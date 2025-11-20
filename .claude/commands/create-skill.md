# Create Skill

Interactive command for creating new Claude Code Skills.

## Skill name: $ARGUMENTS

**Purpose**: Guide users through creating effective skills with proper structure, frontmatter, and bundled resources.

**Usage**:
```bash
/create-skill                    # Interactive mode (guided prompts)
/create-skill pdf-editor         # Create skill with specified name
```

---

## Interactive Skill Creation Workflow

This command invokes the **skill-creator** skill to guide the user through a 6-step process:

### Phase 0: Skill Name and Purpose

**Questions to ask**:
1. What should this skill be called? (kebab-case, e.g., "pdf-editor", "brand-guidelines")
2. What is the primary purpose of this skill in 1-2 sentences?
3. What specific tasks or workflows will this skill help with?

**Validate**:
- Skill name follows conventions (lowercase, hyphens, no spaces)
- Purpose is specific (not vague like "helps with coding")
- Check if skill already exists in `.claude/skills/{skill-name}/`

### Phase 1: Understanding with Concrete Examples

**Questions to ask**:
1. Can you provide 2-3 concrete examples of how this skill would be used?
   - Example format: "User says: 'Rotate this PDF 90 degrees'"
   - Example format: "User says: 'Create a todo app with dark mode'"
2. What would a user say that should trigger this skill?
3. Are there edge cases or variations we should consider?

**Output**: Document examples for next phase

### Phase 2: Planning Reusable Contents

**Analyze each example**:
1. What steps would Claude need to take from scratch?
2. What gets rewritten repeatedly?
3. What resources would help?

**Categorize resources**:

**Scripts** (`scripts/`) - When to include:
- Code is rewritten repeatedly (e.g., `rotate_pdf.py`)
- Deterministic reliability needed
- Token efficiency important

**References** (`references/`) - When to include:
- Documentation Claude should reference (e.g., `schema.md`, `api_docs.md`)
- Database schemas, API specs, company policies
- Domain knowledge that informs Claude's thinking
- Keep SKILL.md lean by moving detailed info here

**Assets** (`assets/`) - When to include:
- Files used in output (not loaded to context)
- Templates, boilerplate code (e.g., `frontend-template/`)
- Images, logos, fonts (e.g., `logo.png`, `font.ttf`)

**Output**: List of resources to create with rationale

### Phase 3: Generate Skill Structure

**Create directory structure**:
```
.claude/skills/{skill-name}/
├── SKILL.md (required)
│   ├── YAML frontmatter (name, description)
│   └── Markdown instructions
├── scripts/ (optional)
│   └── example_script.py
├── references/ (optional)
│   └── example_reference.md
└── assets/ (optional)
    └── example_asset.png
```

**Generate SKILL.md template**:
```yaml
---
name: {skill-name}
description: {Specific description with trigger conditions. Third-person voice: "This skill should be used when..."}
---

# {Skill Name}

{1-2 sentence purpose}

## About This Skill

{When to use this skill}

## How to Use

{Step-by-step instructions referencing bundled resources}

## Bundled Resources

### Scripts
{If applicable: List scripts with usage}

### References
{If applicable: List references with grep patterns if large}

### Assets
{If applicable: List assets with purpose}
```

**Key frontmatter rules**:
- `name` must match directory name
- `description` must be specific with trigger conditions
- Use third-person voice ("This skill should be used when...")
- NOT second-person ("Use this skill when...")

### Phase 4: Edit and Implement

**For each resource type**:

1. **Scripts** - Create executable code:
   ```python
   #!/usr/bin/env python3
   """
   Brief description of what this script does.
   """
   # Implementation
   ```

2. **References** - Create markdown documentation:
   ```markdown
   # Reference Title

   {Domain knowledge, schemas, API docs, policies}

   ## Grep Patterns (if >10k words)
   - Pattern 1: `grep -r "pattern" references/`
   ```

3. **Assets** - Copy or create output resources:
   - Templates: Boilerplate code directories
   - Images: Logo files, icons
   - Fonts: Typography assets

**Update SKILL.md**:
- Write in **imperative/infinitive form** (verb-first)
- Use objective, instructional language
- "To accomplish X, do Y" (NOT "You should do X")
- Reference all bundled resources with usage instructions

### Phase 5: Validation

**Run validation checks**:

1. **Frontmatter validation**:
   ```bash
   python3 -c "import yaml; yaml.safe_load(open('.claude/skills/{skill-name}/SKILL.md').read().split('---')[1])"
   ```

2. **Naming conventions**:
   - Directory name matches frontmatter `name`
   - Kebab-case (no underscores, spaces, capitals)
   - Descriptive and specific

3. **Description quality**:
   - Specific trigger conditions ("when users want to X")
   - Third-person voice
   - Not vague ("helps with tasks")

4. **File organization**:
   - SKILL.md exists and has frontmatter
   - Resources in correct directories
   - No duplicate information (SKILL.md vs references)

5. **Resource references**:
   - All bundled resources mentioned in SKILL.md
   - Usage instructions provided
   - Grep patterns for large references (>10k words)

**If validation fails**:
- Report errors clearly
- Suggest fixes
- Re-run validation after fixes

### Phase 6: Testing and Iteration

**Generate test invocation**:
```bash
# Test with example from Phase 1
# Example: "Rotate this PDF 90 degrees"
```

**Provide iteration guidance**:
1. Use the skill on real tasks
2. Notice struggles or inefficiencies
3. Update SKILL.md or bundled resources
4. Test again

**Output summary**:
```
✅ Skill Created: {skill-name}

Location: .claude/skills/{skill-name}/
Structure:
  - SKILL.md ({X} lines)
  - scripts/ ({Y} files)
  - references/ ({Z} files)
  - assets/ ({W} files)

Validation: All checks passed

Next Steps:
1. Test skill: [example usage from Phase 1]
2. Iterate based on real usage
3. Consider adding to README.md skill catalog
```

---

## Progressive Disclosure Design

Skills use three-level loading:

1. **Metadata (name + description)** - Always in context (~100 words)
2. **SKILL.md body** - When skill triggers (<5k words)
3. **Bundled resources** - As needed by Claude (unlimited for scripts)

**Keep SKILL.md lean**:
- Move detailed information to `references/`
- Keep only essential procedural instructions
- Avoid duplication between SKILL.md and references

---

## Best Practices

### Frontmatter Quality
- Be specific about when to use the skill
- Include concrete examples in description
- Use third-person voice consistently

### Writing Style
- Imperative/infinitive form (verb-first)
- Objective, instructional language
- "To accomplish X, do Y" (not "You should do X")

### Resource Organization
- **Scripts**: Deterministic, reusable code
- **References**: Documentation for Claude to reference
- **Assets**: Files used in output (not loaded to context)

### Avoid Common Pitfalls
- ❌ Vague descriptions ("helps with coding")
- ❌ Second-person voice ("You should use this when...")
- ❌ Duplicate information across SKILL.md and references
- ❌ Missing resource references in SKILL.md
- ❌ Large SKILL.md files (>5k words) - use references instead

---

## Implementation Note

This command should invoke the `skill-creator` skill with the following prompt:

```
Create a new skill following the 6-phase process:
1. Skill name and purpose
2. Concrete examples
3. Resource planning
4. Structure generation
5. Implementation
6. Validation

Skill name: {skill-name from arguments or prompt user}

Follow the skill-creator skill instructions to guide the user through
each phase interactively, asking clarifying questions and validating
at each step.
```

The skill-creator skill handles the detailed workflow, this command is just the entry point.
