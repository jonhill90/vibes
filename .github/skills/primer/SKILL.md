---
name: primer
description: Orient in any codebase by analyzing structure, documentation, key files, and current state. Use when starting work on an unfamiliar project, switching codebases, or needing a quick overview.
argument-hint: "subdirectory or focus area (optional)"
---

# Codebase Primer

Analyze the current codebase and produce a structured orientation report.

## Injected Context

### Current Branch

!`git branch --show-current 2>/dev/null || echo "(not a git repo)"`

### Working Tree Status

!`git status --short 2>/dev/null || echo "(not a git repo)"`

### Recent Commits

!`git log --oneline -20 2>/dev/null || echo "(no git history)"`

### Project Structure

!`tree -L 3 -a --dirsfirst -I '.git|node_modules|__pycache__|.venv|venv|dist|build|.next|.nuxt|coverage|.pytest_cache|.mypy_cache|target|vendor|Pods|.gradle|.idea|.vs' $ARGUMENTS 2>/dev/null`

## Workflow

Follow these four phases in order. Be selective — read only what matters.

### Phase 1: Interpret Structure

Analyze the injected project structure above. Identify:

- Project type (application, library, monorepo, framework, CLI tool)
- Primary language(s) based on file extensions and config files
- Directory layout patterns (src/, lib/, app/, packages/)
- Build system (package.json, Cargo.toml, go.mod, pyproject.toml, Makefile)
- Test location (tests/, __tests__/, spec/, *_test.go)
- CI/CD presence (.github/workflows/, .gitlab-ci.yml, Jenkinsfile)

If `$ARGUMENTS` specifies a subdirectory, focus on that subtree while noting its relationship to the broader project.

### Phase 2: Read Documentation

Read the most important documentation files in priority order, stopping when you have enough context:

1. **Agent instructions** (highest priority):
   CLAUDE.md, AGENTS.md, .cursorrules, .github/copilot-instructions.md

2. **Project documentation**:
   README.md, CONTRIBUTING.md, DEVELOPMENT.md, docs/architecture.md

3. **Dependency manifest** (scan only — do not read exhaustively):
   package.json, requirements.txt, pyproject.toml, Cargo.toml, go.mod, Gemfile

Read agent instructions fully. For README, read the first 100 lines. For dependency manifests, scan the dependency list only.

Skip files absent from the project structure. Do not waste tool calls checking for files you can see are missing.

### Phase 3: Identify Key Files

Based on structure and documentation, identify and optionally read:

- **Entry points**: main.*, index.*, app.*, server.*, cli.*
- **Configuration**: tsconfig.json, webpack.config.*, docker-compose.yml
- **Schemas/types**: Core data models, database schemas, API types
- **Core implementations**: The 3-5 most important source files

Read key files only if short (under 200 lines) or scan the first 50 lines for essential context. Note the existence and purpose of large files without reading them in full.

### Phase 4: Assess Current State

The injected git context provides branch, status, and recent commits. If there are uncommitted changes, run `git diff --stat` to identify active work areas.

## Output Format

Produce the primer report using this structure. Be concise — bullet points over paragraphs.

```markdown
## Primer Report: {project-name}

### Project Overview
- **Type**: {app/library/CLI/monorepo/framework}
- **Purpose**: {one-line description}
- **Primary language(s)**: {languages}
- **Framework(s)**: {if applicable}

### Architecture
- {what each major directory does}
- {key architectural patterns}
- {entry point(s)}

### Tech Stack
- **Runtime**: {language version, runtime}
- **Dependencies**: {key dependencies, not exhaustive}
- **Build**: {build tools, bundlers}
- **Test**: {test framework(s)}
- **CI/CD**: {if present}

### Core Principles
{From agent instructions or contributing docs. "No agent instructions found." if none.}

### Key Files
| File | Purpose |
|------|---------|
| {path} | {brief purpose} |

### Current State
- **Branch**: {current branch}
- **Status**: {clean / N uncommitted changes}
- **Recent focus**: {what recent commits suggest}
```

## Guidelines

- **Be selective**: Use the tree output to make targeted read choices.
- **Be fast**: Target under 10 tool calls total.
- **Be portable**: Do not assume any specific language, framework, or toolchain.
- **Handle missing tree**: If tree output is empty or errored, run `git ls-files` or use Glob to discover the project structure.
- **Subdirectory focus**: When `$ARGUMENTS` is provided, scope the report to that area. Still note broader project context briefly.
