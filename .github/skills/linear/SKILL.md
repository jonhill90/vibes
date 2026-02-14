---
name: linear
description: Manage Linear issues, teams, and projects via CLI including issue tracking, sprint workflows, branch creation, and PR generation. Use when working with Linear, tracking issues, starting work on tasks, creating PRs from Linear issues, or managing teams and projects.
---

# Linear CLI

Manage Linear issues, teams, and projects using the `linear` command-line tool.

**CLI:** [schpet/linear-cli](https://github.com/schpet/linear-cli) v1.9.1+

## Prerequisites

```bash
# Install (macOS)
brew install schpet/tap/linear

# Install (Deno)
deno install -A -g -n linear jsr:@schpet/linear-cli

# Verify installation
linear --help
```

## Authentication

```bash
# Set API key (required)
export LINEAR_API_KEY=lin_api_xxxxx

# Generate at: Linear > Settings > API > Personal API keys

# Or use interactive auth
linear auth
```

## Configuration

```bash
# Interactive per-repo config — generates .linear.toml
linear config

# Sets default team for the repo
# Stores in .linear.toml (commit or gitignore per preference)
```

### .linear.toml

```toml
team_id = "TEAM-UUID"
```

## CLI Structure

```
linear issue          create | list | view | update | delete | start | id | title | url | describe | pr | comment | attach
linear team           list | id | members | create | delete | autolinks
linear project        list | view | create
linear label          list | create | delete
linear document       Manage Linear documents
linear milestone      Manage project milestones
linear initiative     Manage initiatives
linear auth           Manage authentication
linear config         Interactive repo setup
linear completions    Shell completions (bash/zsh/fish)
linear schema         Print GraphQL schema
```

## Issues

### Create Issue

```bash
# Basic issue
linear issue create --title "Bug: login fails on Safari"

# Issue with metadata
linear issue create \
  --title "Feature: dark mode support" \
  --priority 2 \
  --state "backlog" \
  --label "enhancement"

# Assign to yourself
linear issue create --title "Fix auth timeout" --assignee self

# Full options
linear issue create \
  --title "Fix auth timeout" \
  --description "Users get 504 after 30s" \
  --assignee self \
  --priority 2 \
  --state "backlog" \
  --label "bug" \
  --project "Q1 Roadmap" \
  --estimate 3 \
  --due-date 2025-03-01

# Create and start immediately (creates branch)
linear issue create --title "Fix auth timeout" --start
```

### List Issues

```bash
# List your issues (default: assigned to you, unstarted state)
linear issue list --sort priority

# IMPORTANT: --sort is required (values: priority, manual)
# Set LINEAR_ISSUE_SORT=priority to avoid passing it every time

# Filter by state
linear issue list --sort priority --state started
linear issue list --sort priority --state backlog
linear issue list --sort priority --all-states

# Filter by assignee
linear issue list --sort priority                    # Your issues (default)
linear issue list --sort priority -A                 # All assignees
linear issue list --sort priority -U                 # Unassigned only
linear issue list --sort priority --assignee jsmith  # Specific user

# Filter by project or team
linear issue list --sort priority --project "Q1 Roadmap"
linear issue list --sort priority --team "Platform"

# Limit results
linear issue list --sort priority --limit 20

# Open in browser
linear issue list --sort priority --web
```

### View Issue

```bash
# View issue by identifier
linear issue view ENG-123

# View issue detected from current branch
linear issue view

# Open in browser or app
linear issue view ENG-123 --web
linear issue view ENG-123 --app
```

### Update Issue

```bash
# Update state
linear issue update ENG-123 --state "in progress"

# Update priority
linear issue update ENG-123 --priority 1

# Assign to yourself or someone
linear issue update ENG-123 --assignee self
linear issue update ENG-123 --assignee jsmith

# Update multiple fields
linear issue update ENG-123 \
  --state "in progress" \
  --priority 2 \
  --assignee self \
  --label "bug"
```

### Delete Issue

```bash
linear issue delete ENG-123
```

## Git Workflow

The CLI's headline feature — seamless Git integration with Linear issues.

### Start Work on an Issue

```bash
# Create a branch for an issue and set state to "In Progress"
linear issue start ENG-123

# Branch naming convention: {team-key}-{issue-number}-{slug}
# Example: eng-123-fix-login-timeout

# Start from a specific ref
linear issue start ENG-123 --from-ref main

# Use a custom branch name
linear issue start ENG-123 --branch my-custom-branch

# Interactive — pick from unassigned issues
linear issue start --unassigned
```

### Detect Issue from Branch

The CLI parses the current Git branch name to find the Linear issue.

```bash
# Get issue identifier from current branch
linear issue id
# Output: ENG-123

# Get issue title from current branch
linear issue title
# Output: Fix login timeout

# Get issue URL from current branch
linear issue url
# Output: https://linear.app/team/issue/ENG-123

# Get title + Linear-issue trailer (useful for commits)
linear issue describe
# Output: Fix login timeout
#         Linear-issue: ENG-123
```

### Create PR from Branch

```bash
# Create a GitHub PR linked to the Linear issue
linear issue pr

# Under the hood, calls: gh pr create
# - Title: prefixed with issue ID (e.g., "ENG-123 Fix login timeout")
# - Body: includes Linear issue URL
# NOTE: Requires `gh` CLI to be installed and authenticated

# PR options
linear issue pr --draft                    # Create as draft
linear issue pr --base main                # Specify base branch
linear issue pr --title "Custom title"     # Custom title (ID still prefixed)
linear issue pr --web                      # Open in browser after creation
```

## Teams

```bash
# List all teams
linear team list

# Get configured team ID
linear team id

# List team members
linear team members
linear team members ENG              # Specific team by key

# Create team
linear team create --name "Platform" --key "PLT"

# Delete team
linear team delete ENG

# Configure GitHub autolinks for the team
linear team autolinks
```

## Projects

```bash
# List all projects
linear project list

# View project details
linear project view PROJECT-ID

# Create project
linear project create
```

## Labels

```bash
# List all labels
linear label list

# Create a label
linear label create

# Delete a label
linear label delete "bug"
```

## Common Parameters

| Parameter | Values | Description |
|-----------|--------|-------------|
| `--priority` | `1` Urgent, `2` High, `3` Medium, `4` Low | Issue priority (1-4) |
| `--state` / `-s` | `triage`, `backlog`, `unstarted`, `started`, `completed`, `canceled` | Workflow state |
| `--sort` | `priority`, `manual` | Sort order (**required** for `issue list`) |
| `--assignee` / `-a` | `self`, username, or display name | Assign or filter by user |
| `-A` / `--all-assignees` | flag | Show issues for all assignees |
| `-U` / `--unassigned` | flag | Show only unassigned issues |
| `--limit` | number (default: 50, 0=unlimited) | Max items to return |
| `--web` / `-w` | flag | Open in browser |
| `--app` / `-a` | flag | Open in Linear.app |
| `--workspace` / `-w` | slug | Target a specific workspace |

## Common Workflows

### Start work on a Linear issue

```bash
linear issue start ENG-123
# ... make changes ...
git add -A && git commit -m "Fix login timeout"
linear issue pr
```

### Create issue and start immediately

```bash
linear issue create --title "Fix auth timeout" --assignee self --priority 2 --start
```

### Triage unassigned issues

```bash
linear issue list --sort priority -U --state triage
```

### Review current sprint

```bash
linear issue list --sort priority --state started
linear issue list --sort priority --state unstarted
```

### Create PR from current branch

```bash
# Ensure you're on a branch created by `linear issue start`
linear issue pr
# Verify the PR was created
gh pr view --web
```

### Check what issue you're working on

```bash
linear issue id      # ENG-123
linear issue title   # Fix login timeout
linear issue url     # https://linear.app/...
```

## References

For complete command details beyond the common operations above:

- [Issues](references/issues.md) — Full issue command flags, filtering, and advanced patterns
- [Teams and projects](references/teams-projects.md) — Team management, autolinks, project commands, and configuration
