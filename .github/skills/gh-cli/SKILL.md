---
name: gh-cli
description: Manage GitHub via CLI including pull requests, issues, workflows, actions, releases, and repositories. Use when working with GitHub, gh commands, GitHub Actions CI/CD, PRs, issues, releases, or repository management.
---

# GitHub CLI

Manage GitHub resources using the `gh` command-line tool.

**CLI Version:** 2.65.0+

## Prerequisites

```bash
# Install GitHub CLI
brew install gh          # macOS
sudo apt install gh      # Debian/Ubuntu
winget install GitHub.cli # Windows
conda install -c conda-forge gh  # Conda

# Verify installation
gh --version
```

## Authentication

Two methods: interactive browser login or token-based for CI/CD.

### Interactive Login

```bash
# Browser-based login (default)
gh auth login

# Select GitHub.com or GitHub Enterprise
gh auth login --hostname github.example.com

# Choose protocol (HTTPS or SSH)
gh auth login --git-protocol ssh
```

### Token-Based (CI/CD, automation)

```bash
# Login with token from stdin
echo $MY_TOKEN | gh auth login --with-token

# Or set environment variable (skips login entirely)
export GH_TOKEN=$MY_TOKEN
# Alternative variable name
export GITHUB_TOKEN=$MY_TOKEN
```

### Verify and Manage Auth

```bash
# Check current auth status
gh auth status

# Switch between accounts
gh auth switch

# Refresh token scopes
gh auth refresh --scopes repo,read:org

# Set default repository for current directory
gh repo set-default OWNER/REPO

# Logout
gh auth logout
```

## CLI Structure

```
gh pr          create | list | view | merge | review | checks | checkout | close | reopen | edit | ready | diff | comment
gh issue       create | list | view | close | reopen | edit | comment | delete | pin | transfer | develop | lock
gh workflow    list | view | run | enable | disable
gh run         list | view | watch | download | rerun | cancel
gh release     create | list | view | download | edit | delete | upload
gh repo        create | clone | fork | view | edit | list | sync | archive | rename | delete
gh api         REST and GraphQL API calls
gh label       create | list | edit | delete | clone
gh secret      set | list | delete (repo/org/env scopes)
gh variable    set | list | get | delete (repo/org/env scopes)
gh search      repos | issues | prs | code | commits
gh gist        create | list | view | edit | delete | clone
gh codespace   create | list | code | ssh | stop | delete
gh extension   install | list | upgrade | remove
gh alias       set | list | delete
gh config      set | get | list
gh status      Cross-repo dashboard
```

## Pull Requests

### Create PR

```bash
# Basic PR from current branch
gh pr create --title "Feature: new login flow" --body "Description here"

# Draft PR with reviewers, labels, and assignees
gh pr create \
  --title "Feature: new login flow" \
  --draft \
  --reviewer user1,user2 \
  --assignee @me \
  --label "enhancement" \
  --milestone "v2.0"

# Auto-fill title and body from commits
gh pr create --fill

# Specify base and head branches
gh pr create --base main --head feature/login --title "Login feature"
```

### List and View PRs

```bash
# List open PRs
gh pr list

# Filter by state, author, label
gh pr list --state merged --author @me --limit 10
gh pr list --label "bug" --base main

# View PR details
gh pr view 123
gh pr view 123 --web          # Open in browser
gh pr view 123 --json title,state,reviews

# View PR diff
gh pr diff 123

# Show CI check status
gh pr checks 123
gh pr checks 123 --watch      # Watch until checks complete
```

### Merge PR

```bash
# Merge (default merge commit)
gh pr merge 123

# Squash merge
gh pr merge 123 --squash

# Rebase merge
gh pr merge 123 --rebase

# Merge with options
gh pr merge 123 --squash --delete-branch --body "Squash commit message"

# Enable auto-merge (merges when checks pass)
gh pr merge 123 --auto --squash
```

### Review PR

```bash
# Approve
gh pr review 123 --approve

# Request changes
gh pr review 123 --request-changes --body "Please fix the error handling"

# Leave a comment review
gh pr review 123 --comment --body "Looks good overall, minor suggestions"
```

### Checkout and Edit PR

```bash
# Check out PR branch locally
gh pr checkout 123

# Mark draft as ready
gh pr ready 123

# Edit PR metadata
gh pr edit 123 --title "Updated title" --add-label "priority" --add-reviewer user3

# Close / reopen
gh pr close 123
gh pr reopen 123
```

## Issues

### Create Issue

```bash
# Basic issue
gh issue create --title "Bug: login fails on Safari" --body "Steps to reproduce..."

# Issue with metadata
gh issue create \
  --title "Feature request: dark mode" \
  --label "enhancement","ui" \
  --assignee user1,user2 \
  --milestone "v2.0" \
  --project "Roadmap"
```

### List and View Issues

```bash
# List open issues
gh issue list

# Filter by state, label, assignee, milestone
gh issue list --state closed --label "bug" --assignee @me --limit 20
gh issue list --milestone "v2.0" --state all

# View issue details
gh issue view 456
gh issue view 456 --web           # Open in browser
gh issue view 456 --json title,state,labels,comments
```

### Update Issues

```bash
# Close / reopen
gh issue close 456
gh issue close 456 --reason "not planned"
gh issue reopen 456

# Edit issue fields
gh issue edit 456 --title "Updated title" --add-label "priority" --remove-label "triage"
gh issue edit 456 --assignee user1 --milestone "v3.0"

# Add comment
gh issue comment 456 --body "Working on this now"
```

## Workflows & Actions

### List and View Workflows

```bash
# List all workflows
gh workflow list

# View workflow details and recent runs
gh workflow view {workflow-name}
gh workflow view {workflow-name} --web
```

### Run Workflow

```bash
# Trigger workflow on default branch
gh workflow run {workflow-file} --ref main

# With input parameters
gh workflow run deploy.yml -f environment=staging -f version=1.2.3

# From a specific branch
gh workflow run ci.yml --ref feature/new-feature
```

### View and Monitor Runs

```bash
# List recent runs
gh run list --limit 10
gh run list --workflow ci.yml --branch main --status failure

# View run details
gh run view {run-id}
gh run view {run-id} --web
gh run view {run-id} --log          # Full log output
gh run view {run-id} --log-failed   # Only failed step logs

# Watch run in real time
gh run watch {run-id}
gh run watch {run-id} --exit-status  # Exit with run's status code
```

### Manage Runs

```bash
# Download artifacts
gh run download {run-id}
gh run download {run-id} --name "build-output"  # Specific artifact
gh run download {run-id} --dir ./artifacts       # Custom directory

# Re-run
gh run rerun {run-id}
gh run rerun {run-id} --failed      # Only failed jobs
gh run rerun {run-id} --debug       # With debug logging

# Cancel
gh run cancel {run-id}
```

## Releases

### Create Release

```bash
# Create release from tag
gh release create v1.0.0 --title "Release v1.0.0" --notes "Release notes here"

# Auto-generate release notes from commits
gh release create v1.0.0 --generate-notes

# Draft release
gh release create v1.0.0 --draft --generate-notes

# Prerelease
gh release create v1.0.0-beta.1 --prerelease --generate-notes

# Upload assets with release
gh release create v1.0.0 ./dist/*.tar.gz ./dist/*.zip --generate-notes

# Notes from file
gh release create v1.0.0 --notes-file CHANGELOG.md
```

### List, View, and Download

```bash
# List releases
gh release list --limit 10

# View release details
gh release view v1.0.0
gh release view v1.0.0 --web

# Download all assets
gh release download v1.0.0

# Download specific asset
gh release download v1.0.0 --pattern "*.tar.gz" --dir ./downloads
```

## Repositories

```bash
# Clone repository
gh repo clone OWNER/REPO
gh repo clone OWNER/REPO -- --depth 1   # Shallow clone

# Fork repository
gh repo fork OWNER/REPO
gh repo fork OWNER/REPO --clone         # Fork and clone locally

# Create repository
gh repo create my-project --public --clone
gh repo create my-project --private --add-readme --license mit --gitignore Node

# View repository
gh repo view OWNER/REPO
gh repo view OWNER/REPO --web
gh repo view --json name,description,defaultBranchRef

# Edit repository settings
gh repo edit --description "New description"
gh repo edit --visibility private
gh repo edit --enable-wiki=false --enable-issues=true

# Sync fork with upstream
gh repo sync OWNER/REPO

# List repositories
gh repo list OWNER --limit 20 --language go --visibility public
```

## Output Formats & JSON Queries

### JSON Field Selection

```bash
# Select specific fields with --json
gh pr list --json number,title,state,author
gh issue view 456 --json title,labels,assignees

# Available fields vary by command — use --json without value to see options
gh pr list --json
```

### JQ Filtering

```bash
# Filter with --jq (uses jq syntax)
gh pr list --json number,title,author --jq '.[].title'
gh pr list --json number,title,labels --jq '.[] | select(.labels[].name == "bug")'
gh issue list --json number,title --jq '.[] | "\(.number): \(.title)"'
```

### Go Templates

```bash
# Format with --template
gh pr list --json number,title --template '{{range .}}#{{.number}} {{.title}}{{"\n"}}{{end}}'
```

## Common Parameters

| Parameter | Description |
|-----------|-------------|
| `--repo` / `-R` | Target repo as `OWNER/REPO` (overrides current directory) |
| `--json` | Select output fields (comma-separated) |
| `--jq` | Filter JSON output with jq expression |
| `--template` | Format output with Go template |
| `--web` / `-w` | Open in web browser |
| `--limit` / `-L` | Maximum number of items to return |
| `--state` | Filter by state (open, closed, merged, all) |
| `--label` | Filter by label |
| `--assignee` | Filter by assignee |
| `--milestone` | Filter by milestone |
| `--author` | Filter by author |

## Common Workflows

### Create PR from current branch

```bash
BRANCH=$(git branch --show-current)
gh pr create \
  --title "$(git log -1 --pretty=%s)" \
  --body "$(git log -1 --pretty=%b)" \
  --head "$BRANCH" \
  --base main
```

### Review and merge PR

```bash
gh pr review 123 --approve
gh pr merge 123 --squash --delete-branch
```

### Trigger workflow and wait for result

```bash
gh workflow run deploy.yml -f environment=staging
RUN_ID=$(gh run list --workflow deploy.yml --limit 1 --json databaseId --jq '.[0].databaseId')
gh run watch "$RUN_ID" --exit-status
```

### Create release from latest tag

```bash
TAG=$(git describe --tags --abbrev=0)
gh release create "$TAG" --generate-notes
```

### Download latest CI artifacts

```bash
RUN_ID=$(gh run list --workflow ci.yml --status success --limit 1 --json databaseId --jq '.[0].databaseId')
gh run download "$RUN_ID" --name "build-output" --dir ./artifacts
```

### Triage issues by label

```bash
# List untriaged issues and add label
gh issue list --label "" --limit 50 --json number,title --jq '.[].number' | while read -r num; do
  gh issue edit "$num" --add-label "needs-triage"
done
```

## References

For complete command details beyond the common operations above:

- [Actions, secrets, and variables](references/actions.md) — Workflow management, secrets, variables, cache, artifact patterns, CI scripting
- [Issues and labels](references/issues-labels.md) — Issue templates, pin/transfer/develop, label CRUD, search, bulk operations
- [Repos and releases](references/repos.md) — Repo creation/settings, deploy keys, rulesets, release asset management
- [API, search, and advanced patterns](references/advanced.md) — REST/GraphQL API, search commands, extensions, aliases, gists, codespaces, scripting patterns
