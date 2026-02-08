# API, Search, and Advanced Patterns

For quick-start examples, see [SKILL.md](../SKILL.md).

## REST API

### GET Requests

```bash
# Get repo info
gh api repos/OWNER/REPO

# Get PR details
gh api repos/OWNER/REPO/pulls/123

# Get PR comments
gh api repos/OWNER/REPO/pulls/123/comments

# Get issue timeline
gh api repos/OWNER/REPO/issues/456/timeline

# Get workflow runs
gh api repos/OWNER/REPO/actions/runs --jq '.workflow_runs[:5] | .[].name'
```

### POST / PATCH / DELETE

```bash
# Create issue comment via API
gh api repos/OWNER/REPO/issues/456/comments \
  -f body="Comment via API"

# Update issue
gh api repos/OWNER/REPO/issues/456 \
  --method PATCH \
  -f state="closed"

# Delete a comment
gh api repos/OWNER/REPO/issues/comments/{comment-id} \
  --method DELETE

# Add labels to issue
gh api repos/OWNER/REPO/issues/456/labels \
  --method POST \
  -f "labels[]=bug" -f "labels[]=priority"
```

### Pagination

```bash
# Auto-paginate through all results
gh api repos/OWNER/REPO/issues --paginate --jq '.[].title'

# Paginate with custom per-page
gh api repos/OWNER/REPO/issues?per_page=100 --paginate

# Get total count with pagination
gh api repos/OWNER/REPO/issues --paginate --jq 'length'
```

### Placeholder Substitution

```bash
# {owner} and {repo} are auto-filled from current repo context
gh api repos/{owner}/{repo}/pulls
gh api repos/{owner}/{repo}/issues/456
gh api repos/{owner}/{repo}/actions/runs
```

## GraphQL API

### Basic Queries

```bash
# Query with GraphQL
gh api graphql -f query='
  query {
    repository(owner: "OWNER", name: "REPO") {
      issues(first: 5, states: OPEN) {
        nodes {
          number
          title
        }
      }
    }
  }
'

# With variables
gh api graphql \
  -f query='query($owner: String!, $repo: String!) {
    repository(owner: $owner, name: $repo) {
      stargazerCount
      forkCount
    }
  }' \
  -f owner="OWNER" \
  -f repo="REPO"
```

### Extract with JQ

```bash
gh api graphql -f query='
  query {
    viewer {
      repositories(first: 10, orderBy: {field: UPDATED_AT, direction: DESC}) {
        nodes { name, updatedAt }
      }
    }
  }
' --jq '.data.viewer.repositories.nodes[].name'
```

## Search Commands

### Search Repositories

```bash
gh search repos "cli tool" --language go --stars ">100" --limit 20
gh search repos "topic:kubernetes" --sort stars --order desc
gh search repos "org:github" --json fullName,description,stargazersCount
```

### Search Issues and PRs

```bash
gh search issues "memory leak" --language rust --state open
gh search issues "label:good-first-issue" --language python --sort created
gh search prs "author:@me" --state merged --merged ">2024-01-01"
gh search prs "review:required" --repo OWNER/REPO
```

### Search Code

```bash
gh search code "func main" --language go --repo OWNER/REPO
gh search code "import React" --filename "*.tsx" --limit 10
```

### Search Commits

```bash
gh search commits "fix typo" --author @me --repo OWNER/REPO
gh search commits "security" --committer-date ">2024-06-01"
```

## Extensions

```bash
# Install an extension
gh extension install owner/gh-extension-name

# List installed extensions
gh extension list

# Upgrade extensions
gh extension upgrade --all
gh extension upgrade owner/gh-extension-name

# Remove an extension
gh extension remove owner/gh-extension-name

# Browse available extensions
gh extension browse
gh extension search "copilot"
```

## Aliases

```bash
# Set an alias
gh alias set pv "pr view"
gh alias set co "pr checkout"
gh alias set myissues "issue list --assignee @me"

# Set with shell commands
gh alias set --shell igrep 'gh issue list --json number,title | jq -r ".[] | \"#\(.number) \(.title)\"" | grep -i "$1"'

# List aliases
gh alias list

# Delete an alias
gh alias delete pv
```

## Configuration

```bash
# Set editor
gh config set editor "code --wait"

# Set default protocol
gh config set git_protocol ssh

# Set browser
gh config set browser "firefox"

# Set pager
gh config set pager "less -R"

# View config
gh config get editor
gh config list
```

## Gists

```bash
# Create a gist
gh gist create file.txt

# Create public gist with description
gh gist create file.txt --public --desc "My snippet"

# Create from multiple files
gh gist create file1.txt file2.py

# Create from stdin
echo "hello" | gh gist create --filename greeting.txt

# List gists
gh gist list --limit 10

# View a gist
gh gist view {gist-id}

# Edit a gist
gh gist edit {gist-id}

# Clone a gist
gh gist clone {gist-id}

# Delete a gist
gh gist delete {gist-id}
```

## Codespaces

```bash
# List codespaces
gh codespace list

# Create codespace
gh codespace create --repo OWNER/REPO --branch main --machine basicLinux32gb

# Open in VS Code
gh codespace code --codespace {name}

# SSH into codespace
gh codespace ssh --codespace {name}

# Stop / delete codespace
gh codespace stop --codespace {name}
gh codespace delete --codespace {name} --force

# Port forwarding
gh codespace ports forward 3000:3000 --codespace {name}

# View logs
gh codespace logs --codespace {name}
```

## SSH and GPG Keys

```bash
# List SSH keys
gh ssh-key list

# Add SSH key
gh ssh-key add key.pub --title "My Laptop"

# Delete SSH key
gh ssh-key delete {key-id} --yes

# List GPG keys
gh gpg-key list

# Add GPG key
gh gpg-key add key.pub
```

## Status Dashboard

```bash
# View cross-repo status (assigned issues, PRs, mentions)
gh status

# Exclude specific repos or orgs
gh status --exclude "OWNER/REPO" --org my-org
```

## Environment Variables

| Variable | Purpose |
|----------|---------|
| `GH_TOKEN` / `GITHUB_TOKEN` | Authentication token (skips `gh auth login`) |
| `GH_HOST` | Target GitHub host (for GHES) |
| `GH_REPO` | Default repository in `OWNER/REPO` format |
| `GH_ENTERPRISE_TOKEN` | Token for GitHub Enterprise Server |
| `GH_EDITOR` | Editor for `gh` prompts |
| `GH_BROWSER` | Browser for `--web` commands |
| `GH_PAGER` | Pager for long output |
| `GH_DEBUG` | Set to `1` or `api` for debug output |
| `GH_PROMPT_DISABLED` | Set to `1` to disable interactive prompts |
| `NO_COLOR` | Disable color output |
| `GH_CONFIG_DIR` | Override config directory (default: `~/.config/gh`) |
| `CLICOLOR_FORCE` | Force color output even when piped |

## Go Template Syntax

Used with `--template` flag for custom output formatting.

```bash
# Basic field access
gh pr list --json number,title --template '{{range .}}#{{.number}} {{.title}}{{"\n"}}{{end}}'

# Conditional
gh pr list --json number,title,isDraft --template \
  '{{range .}}{{if .isDraft}}[DRAFT] {{end}}#{{.number}} {{.title}}{{"\n"}}{{end}}'

# Table formatting with tablerow
gh pr list --json number,title,state --template \
  '{{tablerow "Number" "Title" "State"}}{{range .}}{{tablerow .number .title .state}}{{end}}'

# Color and formatting
gh pr list --json number,title --template \
  '{{range .}}{{.number | color "green"}} {{.title}}{{"\n"}}{{end}}'

# Time formatting
gh pr list --json number,createdAt --template \
  '{{range .}}#{{.number}} {{timeago .createdAt}}{{"\n"}}{{end}}'

# Available template functions: color, autocolor, timeago, timefmt, pluck, join, truncate, tablerow, tablerender
```

## Scripting Patterns

### Idempotent Create-or-Update

```bash
# Create label if it doesn't exist, update if it does
gh label create "status/ready" \
  --description "Ready for review" \
  --color 0E8A16 \
  --force
```

### Error Handling

```bash
# Check if command succeeded
if gh pr merge 123 --squash 2>/dev/null; then
  echo "PR merged successfully"
else
  echo "Failed to merge PR"
  exit 1
fi

# Check if PR exists
if gh pr view 123 --json state --jq '.state' 2>/dev/null; then
  echo "PR exists"
fi
```

### Retry Logic

```bash
MAX_RETRIES=3
for i in $(seq 1 $MAX_RETRIES); do
  if gh workflow run deploy.yml -f env=prod 2>/dev/null; then
    echo "Workflow triggered on attempt $i"
    break
  fi
  echo "Attempt $i failed, retrying..."
  sleep $((i * 5))
done
```

### Cross-Repo Operations

```bash
# Run command against a different repo
gh pr list --repo OWNER/OTHER-REPO

# Loop through repos
for repo in $(gh repo list my-org --limit 100 --json nameWithOwner --jq '.[].nameWithOwner'); do
  echo "=== $repo ==="
  gh issue list --repo "$repo" --state open --limit 5
done
```

### Combine with Git

```bash
# Create PR after pushing current branch
git push -u origin "$(git branch --show-current)" && \
  gh pr create --fill

# Check out a PR, review, and merge
gh pr checkout 123 && \
  gh pr review 123 --approve && \
  gh pr merge 123 --squash --delete-branch
```
