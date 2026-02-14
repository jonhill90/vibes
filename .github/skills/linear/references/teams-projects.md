# Teams and Projects

For quick-start examples, see [SKILL.md](../SKILL.md).

## Teams

### List Teams

```bash
# List all teams in the workspace
linear team list
```

### Team Identifier

```bash
# Get the configured team ID (from .linear.toml)
linear team id
```

### Team Members

```bash
# List members of the configured team
linear team members

# List members of a specific team by key
linear team members ENG
```

### Create Team

```bash
# Create a new team with name and key
linear team create --name "Platform" --key "PLT"

# Key is the prefix for issue IDs (e.g., PLT-123)
# Keep keys short (2-5 uppercase letters)
```

### Delete Team

```bash
# Delete a team by key
linear team delete ENG
```

### Autolinks

```bash
# Configure GitHub repository autolinks for Linear issues
linear team autolinks

# Autolinks automatically convert patterns like ENG-123
# into clickable links in GitHub PRs and commits
```

## Projects

### List Projects

```bash
linear project list
```

### View Project

```bash
linear project view PROJECT-ID
```

### Create Project

```bash
linear project create
```

## Project Updates

```bash
# Manage project status updates
linear project-update
```

## Milestones

```bash
# Manage project milestones
linear milestone
```

## Initiatives

```bash
# Manage Linear initiatives
linear initiative

# Manage initiative status updates (timeline posts)
linear initiative-update
```

## Labels

```bash
# List all labels
linear label list

# Create a label
linear label create

# Delete a label by name or ID
linear label delete "bug"
```

## Documents

```bash
# Manage Linear documents
linear document
```

## Configuration

### Per-Repository Config

```bash
# Run interactive setup
linear config

# Generates .linear.toml in the repo root
# Sets the default team for issue commands
```

### .linear.toml

```toml
team_id = "TEAM-UUID"
```

Place in the repo root. Commit it for shared team defaults, or add to `.gitignore` for personal config.

### Shell Completions

```bash
# Generate completions for your shell
linear completions bash >> ~/.bashrc
linear completions zsh >> ~/.zshrc
linear completions fish > ~/.config/fish/completions/linear.fish
```

### GraphQL Schema

```bash
# Print the Linear GraphQL schema to stdout
linear schema
```

## Environment Variables

| Variable | Purpose |
|----------|---------|
| `LINEAR_API_KEY` | API key for authentication (required) |
| `LINEAR_ISSUE_SORT` | Default sort for `issue list` (`priority` or `manual`) |

Generate API keys at: **Linear > Settings > API > Personal API keys**

## Workspace Flag

All commands accept `--workspace <slug>` / `-w <slug>` to target a specific workspace when you have multiple workspaces configured.
