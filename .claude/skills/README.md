# Claude Code Skills System

## Overview

This directory contains Claude Code Skills - modular, reusable capabilities that auto-activate based on context. Skills provide targeted knowledge injection without loading entire pattern libraries, enabling efficient, domain-specific assistance.

**Key Concept**: Skills are documentation, not code. Claude reads and follows guidance in SKILL.md files when relevant to your task.

---

## What Are Skills?

Skills are specialized knowledge modules that:
- **Auto-activate** based on description triggers (task keywords, file patterns)
- **Inject context** on-demand (only load when relevant)
- **Provide progressive disclosure** (main file <500 lines, resource files for details)
- **Enable domain expertise** (specific knowledge vs. generic patterns)

**Skills vs. MCP Tools**:
| Skills | MCP Tools |
|--------|-----------|
| Documentation/guidance (markdown) | Executable functions (Python/TypeScript) |
| Claude reads and follows | Claude invokes as function calls |
| Context injection | Code execution |
| Auto-activated by description | Explicitly called by name |

---

## When to Use Skills vs. MCP Tools

### Use Skills When:
- ✅ Providing domain knowledge (Terraform best practices)
- ✅ Establishing coding patterns (API design standards)
- ✅ Documenting workflows (deployment procedures)
- ✅ Teaching methodologies (task decomposition strategies)
- ✅ Reference material (command cheat sheets)

### Use MCP Tools When:
- ✅ Executing operations (search notes, manage tasks)
- ✅ External integrations (database queries, API calls)
- ✅ State management (read/write project data)
- ✅ System interactions (file operations, shell commands)

**Example**:
- Skill: "How to structure Terraform modules" (guidance)
- MCP Tool: `terraform_validate()` (execution)

---

## Progressive Disclosure Pattern

Skills follow Anthropic's best practice: keep main SKILL.md under 500 lines, use resource files for detailed content.

### Structure

```
.claude/skills/{skill-name}/
├── SKILL.md                    # Main file (<500 lines)
│   ├── Purpose
│   ├── Quick Start
│   ├── Core Principles
│   ├── Quick Reference
│   └── Navigation Guide (links to resources)
└── resources/
    ├── detailed-guide-1.md     # 100-300 lines
    ├── detailed-guide-2.md     # 100-300 lines
    └── examples.md             # Code examples
```

### Why Progressive Disclosure?

**Benefits**:
- **Token efficiency**: Load only what's needed
- **Faster responses**: Less context processing
- **Maintainability**: Update specific guides without touching main file
- **Clarity**: Main file shows overview, resources provide depth

**Anti-pattern** (avoid):
```
❌ skills/terraform/SKILL.md  # 2000 lines - loads entire encyclopedia
```

**Best practice**:
```
✅ skills/terraform/SKILL.md           # 400 lines - overview
✅ skills/terraform/resources/
      state-management.md              # 250 lines
      module-patterns.md               # 200 lines
      security-best-practices.md       # 180 lines
```

---

## Auto-Activation Triggers

Skills activate automatically when description matches task context.

### Description Field Anatomy

```yaml
---
name: terraform-basics
description: "Terraform infrastructure-as-code patterns for AWS and Azure.
             Use when creating .tf files, managing state, writing modules,
             or working with terraform commands (init, plan, apply, destroy)."
---
```

**Trigger Keywords**: `.tf files`, `state`, `modules`, `terraform commands`

**Activation Scenarios**:
- User says: "Create Terraform module for Azure VNet"
- User edits: `infrastructure/modules/networking/main.tf`
- User asks: "How do I manage Terraform state remotely?"

### Writing Effective Descriptions

**Do's** ✅:
- Include specific file extensions (`.tf`, `.ts`, `.py`)
- List common tools/commands (`terraform apply`, `az network`)
- Mention key concepts (`state management`, `dependency injection`)
- Provide 2-3 usage examples in description
- Use domain-specific terminology users will say

**Don'ts** ❌:
- Vague triggers: "Use for coding" (activates too broadly)
- Too narrow: "Only for Terraform 1.5.0" (rarely activates)
- Missing keywords: Description doesn't match user vocabulary
- Over-activation: Broad terms like "development" trigger everywhere

### Examples

**Bad (vague)**:
```yaml
description: "Backend development guidelines. Use for coding."
# Problem: Triggers on any "coding" mention, wastes tokens
```

**Good (specific)**:
```yaml
description: "Backend API development with Express.js and TypeScript.
             Use when creating routes, controllers, or API endpoints in src/api/."
# Benefit: Triggers only on relevant backend work
```

---

## Available Skills

### task-management
**Purpose**: Task decomposition, dependency analysis, parallel execution patterns
**Activate on**: Task planning, dependency detection, workflow orchestration
**Resources**: 2 detailed guides (dependency analysis, parallel execution)

### terraform-basics
**Purpose**: Infrastructure-as-code with Terraform for AWS/Azure
**Activate on**: `.tf` files, Terraform commands, module creation, state management
**Resources**: 3 detailed guides (commands, state, modules)

### azure-basics
**Purpose**: Azure cloud services, CLI patterns, resource management
**Activate on**: Azure resources, `az` commands, ARM templates
**Resources**: 3 detailed guides (resource groups, ARM templates, CLI patterns)

---

## Creating New Skills

### Quick Start

1. **Create directory structure**:
   ```bash
   mkdir -p .claude/skills/{skill-name}/resources
   ```

2. **Create SKILL.md** with frontmatter:
   ```yaml
   ---
   name: skill-name
   description: "Clear purpose with specific activation triggers.
                Use when working with X, Y, Z."
   ---

   # Skill Name

   ## Purpose
   [1-2 sentences]

   ## Quick Start
   [Checklists, common tasks]

   ## Core Principles
   [3-7 key rules]

   ## Quick Reference
   [Tables, cheat sheets]

   ## Navigation Guide
   [Links to resource files]
   ```

3. **Keep main file under 500 lines**:
   - Overview content in SKILL.md
   - Detailed guides in resources/

4. **Test activation**:
   - Use relevant keywords in task descriptions
   - Verify skill loads (check Claude context)
   - Refine description if not activating

### Best Practices

**Structure**:
- ✅ Name: kebab-case (`terraform-basics`, not `TerraformBasics`)
- ✅ Frontmatter: Always include `name` and `description` fields
- ✅ Navigation: Link to resource files from main SKILL.md
- ✅ Examples: Include code snippets with ✅/❌ comparisons

**Content**:
- ✅ Specific: "Use when creating .tf files" not "Use for infrastructure"
- ✅ Actionable: Provide commands, templates, workflows
- ✅ Opinionated: Recommend best practices, warn against anti-patterns
- ✅ Contextual: Explain *why* patterns exist, not just *what* they are

**Size**:
- ✅ Main SKILL.md: 200-500 lines
- ✅ Resource files: 100-300 lines each
- ✅ Total skill: Unlimited (progressive disclosure handles size)

---

## Tool Scoping (Security)

Skills can specify required tools via agent definitions that use them:

```yaml
# Agent using skill
---
name: terraform-expert
skills: [terraform-basics]
tools: Read, Write, Edit, Bash  # Minimal tools for domain
allowed_commands: [terraform, tflint, tfsec]
blocked_commands: [terraform destroy, rm, dd]
---
```

**Security Principle**: Skills provide knowledge, agents enforce tool access.

---

## Troubleshooting

### Skill Not Activating

**Check**:
1. Description has specific triggers (not vague)
2. User task matches description keywords
3. SKILL.md has valid YAML frontmatter
4. Name matches directory name

**Fix**: Add more specific keywords to description field

### Skill Loads Too Often

**Check**: Description too broad ("Use for coding")

**Fix**: Narrow description to specific file types, commands, or domains

### Context Limit Errors

**Check**: Main SKILL.md exceeds 500 lines

**Fix**: Move detailed content to resource files, link from main file

---

## Related Documentation

- **Claude Code Skills Docs**: https://code.claude.com/docs/en/skills
- **Sub-agents Integration**: `.claude/agents/` (agents can use skills)
- **Patterns Library**: `.claude/patterns/` (complementary to skills)
- **Domain Experts**: `.claude/agents/{domain}-expert.md` (use skills for knowledge)

---

## Meta

**Skill System Status**: Operational ✅
**Total Skills**: 3
**Last Updated**: 2025-11-20
**Maintained By**: Vibes architecture team
