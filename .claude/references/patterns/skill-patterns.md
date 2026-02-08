# Skill Design Patterns

Proven patterns for building effective Claude Code skills.

## Progressive Disclosure

Keep SKILL.md lean, load detailed content on demand.

```
my-skill/
├── SKILL.md              # Core instructions (<500 lines)
├── reference.md          # Detailed API docs
├── examples.md           # Usage examples
└── troubleshooting.md    # Common issues
```

In SKILL.md:
```markdown
## Quick Start
[Core workflow here]

## Advanced
- For API details, see [reference.md](reference.md)
- For examples, see [examples.md](examples.md)
```

## Domain-Specific Organization

Organize by domain to avoid loading irrelevant context:

```
bigquery-skill/
├── SKILL.md (overview and navigation)
└── references/
    ├── finance.md
    ├── sales.md
    ├── product.md
    └── marketing.md
```

When user asks about sales, Claude only reads sales.md.

## Framework Variants

Organize by framework/variant:

```
cloud-deploy/
├── SKILL.md (workflow + provider selection)
└── references/
    ├── aws.md
    ├── gcp.md
    └── azure.md
```

## Subagent Skills

Skills that run in isolated context:

```yaml
---
name: deep-research
description: Thorough codebase research
context: fork
agent: Explore
---

Research $ARGUMENTS:
1. Find relevant files using Glob and Grep
2. Read and analyze code
3. Return summary with file references
```

## Dynamic Context Injection

Pre-fetch data before Claude sees the skill:

```yaml
---
name: pr-review
description: Review pull request
context: fork
agent: Explore
allowed-tools: Bash(gh *)
---

## PR Context
- Diff: !`gh pr diff`
- Comments: !`gh pr view --comments`
- Files: !`gh pr diff --name-only`

## Review the PR
[Instructions...]
```

## Manual-Only Skills

Skills with side effects that only you should trigger:

```yaml
---
name: deploy
description: Deploy to production
disable-model-invocation: true
---

Deploy $ARGUMENTS:
1. Run tests
2. Build
3. Deploy
4. Verify
```

## Background Knowledge Skills

Skills Claude uses but users don't invoke:

```yaml
---
name: codebase-context
description: Architecture and patterns for this codebase
user-invocable: false
---

[Architectural knowledge...]
```

## Restricted Tool Skills

Limit tools for safety:

```yaml
---
name: safe-reader
description: Read-only file exploration
allowed-tools: Read, Grep, Glob
---

Explore the codebase without making changes.
```

## Skills with Hooks

Validate operations during skill execution:

```yaml
---
name: db-operations
description: Database operations with validation
hooks:
  PreToolUse:
    - matcher: "Bash"
      hooks:
        - type: command
          command: "./scripts/validate-sql.sh"
---
```

## Workflow Skills

Multi-step processes:

```yaml
---
name: release
description: Create a new release
disable-model-invocation: true
---

# Release Workflow

## 1. Pre-flight
- Run tests: `npm test`
- Check lint: `npm run lint`

## 2. Version Bump
- Update version in package.json
- Update CHANGELOG.md

## 3. Build & Tag
- `npm run build`
- `git tag v$VERSION`

## 4. Publish
- `npm publish`
- `git push --tags`

STOP if any step fails.
```

## Template Skills

Generate from templates:

```yaml
---
name: new-component
description: Create a new React component
---

Create component $ARGUMENTS using template:

```tsx
// Template in assets/component-template.tsx
import React from 'react';

interface ${Name}Props {
  // Props here
}

export const ${Name}: React.FC<${Name}Props> = (props) => {
  return (
    <div>
      {/* Component content */}
    </div>
  );
};
```

## Positional Arguments

Access multiple arguments:

```yaml
---
name: migrate
description: Migrate component from one framework to another
argument-hint: [component] [from] [to]
---

Migrate $0 from $1 to $2.
Preserve behavior and tests.
```
