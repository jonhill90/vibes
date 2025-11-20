---
name: skill-creator
description: Guide for creating effective skills. This skill should be used when users want to create a new skill (or update an existing skill) that extends Claude's capabilities with specialized knowledge, workflows, or tool integrations.
---

# Skill Creator

This skill provides guidance for creating effective skills.

## About Skills

Skills are modular, self-contained packages that extend Claude's capabilities by providing
specialized knowledge, workflows, and tools. Think of them as "onboarding guides" for specific
domains or tasks—they transform Claude from a general-purpose agent into a specialized agent
equipped with procedural knowledge that no model can fully possess.

### What Skills Provide

1. Specialized workflows - Multi-step procedures for specific domains
2. Tool integrations - Instructions for working with specific file formats or APIs
3. Domain expertise - Company-specific knowledge, schemas, business logic
4. Bundled resources - Scripts, references, and assets for complex and repetitive tasks

### Anatomy of a Skill

Every skill consists of a required SKILL.md file and optional bundled resources:

```
skill-name/
├── SKILL.md (required)
│   ├── YAML frontmatter metadata (required)
│   │   ├── name: (required)
│   │   └── description: (required)
│   └── Markdown instructions (required)
└── Supporting files (optional - use any structure)
    ├── scripts/          - Executable code (Python/Bash/etc.)
    ├── resources/        - Additional documentation or reference files
    ├── templates/        - Template files for output
    └── *.md             - Additional markdown files (loaded as needed)
```

#### SKILL.md (required)

**Metadata Quality:** The `name` and `description` in YAML frontmatter determine when Claude will use the skill. Be specific about what the skill does and when to use it. Use the third-person (e.g. "This skill should be used when..." instead of "Use this skill when...").

#### Supporting Files (optional)

Skills can include any additional files alongside SKILL.md. Common patterns:

##### Scripts (`scripts/`)

Executable code (Python/Bash/etc.) for tasks that require deterministic reliability or are repeatedly rewritten.

- **When to include**: When the same code is being rewritten repeatedly or deterministic reliability is needed
- **Example**: `scripts/rotate_pdf.py` for PDF rotation tasks
- **Benefits**: Token efficient, deterministic, may be executed without loading into context
- **Note**: Scripts may still need to be read by Claude for patching or environment-specific adjustments

##### Additional Documentation (`.md` files or `resources/`)

Reference material loaded as needed into context to inform Claude's process and thinking.

- **When to include**: For documentation that Claude should reference while working
- **Examples**: `REFERENCE.md` for detailed API docs, `FORMS.md` for form-filling guides, `resources/schema.md` for database schemas
- **Use cases**: Database schemas, API documentation, domain knowledge, company policies, detailed workflow guides
- **Benefits**: Keeps SKILL.md lean, loaded only when Claude determines it's needed
- **Best practice**: Reference these files from SKILL.md (e.g., "For advanced usage, see [REFERENCE.md](REFERENCE.md)")
- **Avoid duplication**: Information should live in either SKILL.md or supporting files, not both. Keep only essential procedural instructions in SKILL.md; move detailed reference material to supporting files.

##### Templates (`templates/` or any directory)

Files used in output (not loaded to context).

- **When to include**: When the skill needs files that will be copied or modified in output
- **Examples**: `templates/template.txt` for boilerplate, `templates/frontend-template/` for HTML/React boilerplate
- **Use cases**: Templates, boilerplate code, sample documents that get copied or modified
- **Benefits**: Enables Claude to use files without loading them into context

### Progressive Disclosure Design Principle

Skills use a three-level loading system to manage context efficiently:

1. **Metadata (name + description)** - Always in context (~100 words)
2. **SKILL.md body** - When skill triggers (<5k words recommended)
3. **Supporting files** - As needed by Claude (loaded when referenced)

Claude loads supporting files (like REFERENCE.md or resources/*.md) only when needed, keeping the context window efficient.

## Skill Creation Process

To create a skill, follow the "Skill Creation Process" in order, skipping steps only if there is a clear reason why they are not applicable.

### Step 1: Understanding the Skill with Concrete Examples

Skip this step only when the skill's usage patterns are already clearly understood. It remains valuable even when working with an existing skill.

To create an effective skill, clearly understand concrete examples of how the skill will be used. This understanding can come from either direct user examples or generated examples that are validated with user feedback.

For example, when building an image-editor skill, relevant questions include:

- "What functionality should the image-editor skill support? Editing, rotating, anything else?"
- "Can you give some examples of how this skill would be used?"
- "I can imagine users asking for things like 'Remove the red-eye from this image' or 'Rotate this image'. Are there other ways you imagine this skill being used?"
- "What would a user say that should trigger this skill?"

To avoid overwhelming users, avoid asking too many questions in a single message. Start with the most important questions and follow up as needed for better effectiveness.

Conclude this step when there is a clear sense of the functionality the skill should support.

### Step 2: Planning the Reusable Skill Contents

To turn concrete examples into an effective skill, analyze each example by:

1. Considering how to execute on the example from scratch
2. Identifying what scripts, references, and assets would be helpful when executing these workflows repeatedly

Example: When building a `pdf-editor` skill to handle queries like "Help me rotate this PDF," the analysis shows:

1. Rotating a PDF requires re-writing the same code each time
2. A `scripts/rotate_pdf.py` script would be helpful to store in the skill

Example: When designing a `frontend-webapp-builder` skill for queries like "Build me a todo app" or "Build me a dashboard to track my steps," the analysis shows:

1. Writing a frontend webapp requires the same boilerplate HTML/React each time
2. An `assets/hello-world/` template containing the boilerplate HTML/React project files would be helpful to store in the skill

Example: When building a `big-query` skill to handle queries like "How many users have logged in today?" the analysis shows:

1. Querying BigQuery requires re-discovering the table schemas and relationships each time
2. A `references/schema.md` file documenting the table schemas would be helpful to store in the skill

To establish the skill's contents, analyze each concrete example to create a list of the reusable resources to include: scripts, references, and assets.

### Step 3: Initializing the Skill

At this point, it is time to actually create the skill.

Skip this step only if the skill being developed already exists, and iteration or packaging is needed. In this case, continue to the next step.

When creating a new skill from scratch, create the skill directory structure:

```bash
# Basic structure (required)
mkdir -p .claude/skills/{skill-name}

# Add supporting directories as needed (optional)
mkdir -p .claude/skills/{skill-name}/scripts      # For executable code
mkdir -p .claude/skills/{skill-name}/resources    # For reference docs
mkdir -p .claude/skills/{skill-name}/templates    # For output templates
```

Create the SKILL.md template with proper frontmatter:

```yaml
---
name: {skill-name}
description: {Specific description. Third-person: "This skill should be used when..."}
---

# {Skill Name}

{Purpose and usage instructions}
```

The directory structure includes:
- SKILL.md file with YAML frontmatter and markdown instructions
- Example resource directories: `scripts/`, `references/`, and `assets/`

After initialization, customize or remove the generated SKILL.md and example directories as needed.

### Step 4: Edit the Skill

When editing the (newly-generated or existing) skill, remember that the skill is being created for another instance of Claude to use. Focus on including information that would be beneficial and non-obvious to Claude. Consider what procedural knowledge, domain-specific details, or reusable assets would help another Claude instance execute these tasks more effectively.

#### Start with Supporting Files

To begin implementation, start with the supporting files identified above: scripts, reference documentation, templates, etc. Note that this step may require user input. For example, when implementing a `brand-guidelines` skill, the user may need to provide brand assets or templates, or documentation to store in `resources/`.

Create only the directories you need - not every skill needs scripts, resources, and templates.

#### Update SKILL.md

**Writing Style:** Write the entire skill using **imperative/infinitive form** (verb-first instructions), not second person. Use objective, instructional language (e.g., "To accomplish X, do Y" rather than "You should do X" or "If you need to do X"). This maintains consistency and clarity for AI consumption.

To complete SKILL.md, answer the following questions:

1. What is the purpose of the skill, in a few sentences?
2. When should the skill be used?
3. In practice, how should Claude use the skill? All reusable skill contents developed above should be referenced so that Claude knows how to use them.

### Step 5: Validation

Once the skill is ready, validate it to ensure it meets all requirements:

**Validation checks**:

1. **YAML frontmatter format and required fields**:
   ```bash
   python3 -c "import yaml; yaml.safe_load(open('.claude/skills/{skill-name}/SKILL.md').read().split('---')[1])"
   ```
   - Verify `name` and `description` fields exist
   - Verify frontmatter is valid YAML

2. **Skill naming conventions and directory structure**:
   - Directory name matches frontmatter `name` field
   - Kebab-case naming (lowercase, hyphens, no spaces/underscores)
   - SKILL.md file exists in skill directory

3. **Description completeness and quality**:
   - Description is specific with trigger conditions
   - Uses third-person voice ("This skill should be used when...")
   - Not vague (avoid "helps with tasks", "assists with coding")

4. **File organization and resource references**:
   - Resources in correct directories (scripts/, references/, assets/)
   - All bundled resources mentioned in SKILL.md
   - Usage instructions provided for each resource
   - No duplicate information between SKILL.md and references

If validation fails, report the errors clearly and suggest fixes. Re-run validation after corrections.

### Step 6: Iterate

After testing the skill, users may request improvements. Often this happens right after using the skill, with fresh context of how the skill performed.

**Iteration workflow:**
1. Use the skill on real tasks
2. Notice struggles or inefficiencies
3. Identify how SKILL.md or bundled resources should be updated
4. Implement changes and test again

## Best Practices

### Frontmatter Guidelines
- **Specific descriptions**: Include concrete trigger conditions
- **Third-person voice**: "This skill should be used when..." (not "Use this when...")
- **Avoid vagueness**: Not "helps with coding" but "helps with rotating PDFs using PyPDF2"

### Writing Style Guidelines
- **Imperative/infinitive form**: "To rotate a PDF, use the script" (not "You should use")
- **Objective language**: Instructional, not conversational
- **Verb-first instructions**: Start with action verbs

### Resource Organization
- **Keep SKILL.md lean**: Move detailed info to references/
- **Avoid duplication**: Information in SKILL.md OR references, not both
- **Reference all resources**: Explain how to use each bundled resource
- **Grep patterns**: Include for large references (>10k words)

### Common Pitfalls to Avoid
- ❌ Vague descriptions without trigger conditions
- ❌ Second-person voice in frontmatter or instructions
- ❌ Large SKILL.md files (>5k words) without using references/
- ❌ Missing resource references in SKILL.md
- ❌ Duplicate information in SKILL.md and references/

## Summary

To create an effective skill:

1. **Understand** with concrete examples
2. **Plan** reusable contents (scripts, references, assets)
3. **Initialize** directory structure and SKILL.md template
4. **Edit** SKILL.md and implement bundled resources
5. **Validate** frontmatter, naming, and organization
6. **Iterate** based on real usage

Skills transform Claude into a specialized agent with domain-specific procedural knowledge. Focus on creating clear, specific, reusable resources that help Claude execute tasks effectively.
