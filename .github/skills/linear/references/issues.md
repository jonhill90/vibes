# Issues

For quick-start examples, see [SKILL.md](../SKILL.md).

## Issue States

Linear issues move through workflow states. Use `--state` / `-s` to filter or set state.

| State | Description |
|-------|-------------|
| `triage` | New, needs review |
| `backlog` | Accepted, not yet planned |
| `unstarted` | Planned, not in progress (default for `issue list`) |
| `started` | Actively being worked on |
| `completed` | Done |
| `canceled` | Won't do |

Use `--all-states` to show issues from all states.

## Priority Levels

| Value | Level | Description |
|-------|-------|-------------|
| `1` | Urgent | Needs immediate attention |
| `2` | High | Important, do soon |
| `3` | Medium | Normal priority |
| `4` | Low | Nice to have |

Note: Priority uses 1-4 (not 0-4 like the Linear API).

## Sort Requirement

`issue list` requires `--sort` to be set via one of:

1. CLI flag: `--sort priority`
2. Config file: in `.linear.toml`
3. Environment variable: `LINEAR_ISSUE_SORT=priority`

Values: `priority`, `manual`

## Issue Create — Full Options

```bash
linear issue create \
  --title "Issue title" \               # Required
  --description "Details here" \        # -d
  --priority 2 \                        # 1-4
  --state "backlog" \                   # -s, by name or type
  --assignee self \                     # -a, 'self', username, or display name
  --label "bug" \                       # -l, can be repeated
  --team "Platform" \                   # If not default team
  --project "Q1 Roadmap" \             # Project name
  --parent "ENG-100" \                 # -p, parent issue
  --estimate 3 \                       # Points estimate
  --due-date 2025-03-01 \             # Due date
  --start \                            # Start immediately (create branch)
  --no-use-default-template \          # Skip default template
  --no-interactive                     # Disable prompts
```

## Issue Update — Full Options

```bash
linear issue update ENG-123 \
  --title "New title" \                 # -t
  --description "Updated details" \     # -d
  --state "in progress" \               # -s
  --priority 1 \                        # 1-4
  --assignee self \                     # -a
  --label "bug" \                       # -l, can be repeated
  --team "Platform" \
  --project "Q1 Roadmap" \
  --parent "ENG-100" \                 # -p
  --estimate 5
```

## Issue Describe

Print the issue title and a `Linear-issue:` trailer — useful for commit messages.

```bash
linear issue describe
# Output:
#   Fix login timeout
#
#   Linear-issue: ENG-123

# Use "References" instead of "Fixes" in the trailer
linear issue describe --references
```

## Issue Comment

```bash
# Manage comments on an issue
linear issue comment
```

## Issue Attach

```bash
# Attach a file to an issue
linear issue attach ENG-123 ./screenshot.png
```

## Branch Detection

The CLI uses regex to detect Linear issue IDs from Git branch names:

- Pattern: `{team-key}-{number}` anywhere in the branch name
- Examples that match: `eng-123-fix-login`, `feature/eng-123`, `eng-123`
- The detected ID is used by `issue view`, `issue id`, `issue title`, `issue url`, `issue describe`, and `issue pr`

```bash
# Works on any branch containing a Linear issue pattern
git checkout eng-123-fix-login
linear issue id     # ENG-123
linear issue title  # Fix login timeout
```

## PR Creation Details

`linear issue pr` (alias: `issue pull-request`) creates a GitHub PR via `gh`:

```bash
linear issue pr \
  --base main \           # Target branch
  --head feature-branch \ # Source branch
  --draft \               # Create as draft
  --title "Custom" \      # Custom title (issue ID still prefixed)
  --web                   # Open in browser after creation
```

- **Title:** Prefixed with issue ID (e.g., `ENG-123 Fix login timeout`)
- **Body:** Contains the Linear issue URL
- **Requires:** `gh` CLI installed and authenticated

## Issue Start — Full Options

```bash
linear issue start ENG-123 \
  --from-ref main \           # -f, git ref to branch from
  --branch my-branch \        # -b, custom branch name
  --all-assignees \           # -A, show all assignees in picker
  --unassigned                # -U, show unassigned in picker
```

When called without an issue ID, starts an interactive picker.
