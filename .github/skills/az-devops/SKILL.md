---
name: az-devops
description: Manage Azure DevOps via CLI including repos, pull requests, pipelines, builds, work items, and boards. Use when working with Azure DevOps, az devops commands, CI/CD pipelines, PRs, or Azure Boards work items.
---

# Azure DevOps CLI

Manage Azure DevOps resources using the Azure CLI with the Azure DevOps extension.

**CLI Version:** 2.81.0+

## Prerequisites

```bash
# Install Azure CLI
brew install azure-cli  # macOS
curl -sL https://aka.ms/InstallAzureCLIDeb | sudo bash  # Linux

# Verify installation
az --version

# Install Azure DevOps extension
az extension add --name azure-devops

# Verify extension
az extension show --name azure-devops
```

## Authentication

Two methods: Azure CLI credentials (`az login`) or a Personal Access Token (PAT).

### Azure CLI credentials (interactive / service principal)

If you're already signed in via `az login`, the DevOps extension uses those credentials automatically — no extra login step needed.

```bash
# Interactive login (browser-based)
az login

# Service principal (CI/CD, automation)
az login --service-principal -u $APP_ID -p $CLIENT_SECRET --tenant $TENANT_ID

# Managed identity (Azure-hosted environments)
az login --identity
```

### Personal Access Token (PAT)

```bash
# Set PAT via environment variable (recommended for scripts)
export AZURE_DEVOPS_EXT_PAT=$MY_PAT

# Or login explicitly with PAT
echo $MY_PAT | az devops login --organization https://dev.azure.com/{org}

# Logout
az devops logout --organization https://dev.azure.com/{org}
```

### Configure Defaults

```bash
# Set default org and project (avoids repeating on every command)
az devops configure --defaults organization=https://dev.azure.com/{org} project={project}

# List current configuration
az devops configure --list
```

## CLI Structure

```
az devops          # Main DevOps commands
├── admin          # Administration (banner)
├── extension      # Extension management
├── project        # Team projects
├── security       # Security operations
│   ├── group      # Security groups
│   └── permission # Security permissions
├── service-endpoint # Service connections
├── team           # Teams
├── user           # Users
├── wiki           # Wikis
├── configure      # Set defaults
├── invoke         # Invoke REST API
├── login          # Authenticate
└── logout         # Clear credentials

az pipelines       # Azure Pipelines
├── agent          # Agents
├── build          # Builds
├── folder         # Pipeline folders
├── pool           # Agent pools
├── queue          # Agent queues
├── release        # Releases
├── runs           # Pipeline runs
├── variable       # Pipeline variables
└── variable-group # Variable groups

az boards          # Azure Boards
├── area           # Area paths
├── iteration      # Iterations
└── work-item      # Work items

az repos           # Azure Repos
├── import         # Git imports
├── policy         # Branch policies
├── pr             # Pull requests
└── ref            # Git references

az artifacts       # Azure Artifacts
└── universal      # Universal Packages
```

## Pull Requests

### Create PR

```bash
# Basic PR
az repos pr create \
  --repository {repo} \
  --source-branch {source} \
  --target-branch {target} \
  --title "PR Title" \
  --description "PR description"

# Draft PR with reviewers and work items
az repos pr create \
  --repository {repo} \
  --source-branch feature/new-feature \
  --target-branch main \
  --title "Feature: New functionality" \
  --draft true \
  --reviewers user1@example.com user2@example.com \
  --work-items 63 64 \
  --labels "enhancement" \
  --open
```

### List and Show PRs

```bash
az repos pr list --repository {repo} --status active --output table
az repos pr show --id {pr-id}
az repos pr show --id {pr-id} --open  # Open in browser
```

### Update PR

```bash
# Complete PR
az repos pr update --id {pr-id} --status completed

# Abandon PR
az repos pr update --id {pr-id} --status abandoned

# Set auto-complete
az repos pr update --id {pr-id} --auto-complete true

# Toggle draft
az repos pr update --id {pr-id} --draft true
az repos pr update --id {pr-id} --draft false
```

### Vote on PR

```bash
az repos pr set-vote --id {pr-id} --vote approve
az repos pr set-vote --id {pr-id} --vote approve-with-suggestions
az repos pr set-vote --id {pr-id} --vote reject
az repos pr set-vote --id {pr-id} --vote wait-for-author
az repos pr set-vote --id {pr-id} --vote reset
```

### Checkout PR Locally

```bash
az repos pr checkout --id {pr-id}
```

## Pipelines

### List and Show

```bash
az pipelines list --output table
az pipelines show --name {pipeline-name}
```

### Create Pipeline

```bash
az pipelines create \
  --name {pipeline-name} \
  --repository {repo} \
  --branch main \
  --yaml-path azure-pipelines.yml \
  --skip-run true
```

### Run Pipeline

```bash
# Run by name
az pipelines run --name {pipeline-name} --branch main

# With parameters and variables
az pipelines run --name {pipeline-name} \
  --parameters version=1.0.0 environment=prod \
  --variables buildId=123 configuration=release \
  --open
```

### Pipeline Runs

```bash
# List runs
az pipelines runs list --pipeline {pipeline-id} --top 10
az pipelines runs list --branch main --status completed

# Show run details
az pipelines runs show --run-id {run-id}

# Download artifacts
az pipelines runs artifact download \
  --artifact-name '{artifact-name}' \
  --path {local-path} \
  --run-id {run-id}
```

## Work Items

### Query Work Items (WIQL)

```bash
az boards query \
  --wiql "SELECT [System.Id], [System.Title], [System.State] FROM WorkItems WHERE [System.AssignedTo] = @Me AND [System.State] = 'Active'"

az boards query --wiql "SELECT * FROM WorkItems" --output table
```

### Create Work Item

```bash
# Basic work item
az boards work-item create \
  --title "Fix login bug" \
  --type Bug \
  --assigned-to user@example.com \
  --description "Users cannot login with SSO"

# With area, iteration, and custom fields
az boards work-item create \
  --title "New feature" \
  --type "User Story" \
  --area "Project\\Area1" \
  --iteration "Project\\Sprint 1" \
  --fields "Priority=1" "Severity=2"
```

### Update Work Item

```bash
az boards work-item update \
  --id {work-item-id} \
  --state "Active" \
  --title "Updated title" \
  --assigned-to user@example.com \
  --discussion "Work in progress"

# Update custom fields
az boards work-item update \
  --id {work-item-id} \
  --fields "Priority=1" "StoryPoints=5"
```

### Delete Work Item

```bash
az boards work-item delete --id {work-item-id} --yes           # Soft delete
az boards work-item delete --id {work-item-id} --destroy --yes # Permanent
```

### Show Work Item

```bash
az boards work-item show --id {work-item-id}
az boards work-item show --id {work-item-id} --open
```

## Repositories

```bash
# List repositories
az repos list --output table

# Show repository details
az repos show --repository {repo-name}

# Create repository
az repos create --name {repo-name} --project {project}

# Delete repository
az repos delete --id {repo-id} --yes
```

## Output Formats

All commands support multiple output formats:

```bash
az pipelines list --output table    # Human-readable
az pipelines list --output json     # Default, machine-readable
az pipelines list --output tsv      # Tab-separated, script-friendly
az pipelines list --output yaml     # YAML format
az pipelines list --output jsonc    # Colored JSON
az pipelines list --output none     # No output
```

## JMESPath Queries

Filter and transform output with `--query`:

```bash
# Filter by name
az pipelines list --query "[?name=='myPipeline']"

# Get specific fields
az pipelines list --query "[].{Name:name, ID:id}" --output table

# Chain queries
az pipelines list --query "[?name.contains('CI')].{Name:name, ID:id}"

# Get first result
az pipelines list --query "[0]"
```

## Common Parameters

| Parameter | Description |
|-----------|-------------|
| `--org` / `--organization` | Azure DevOps org URL (`https://dev.azure.com/{org}`) |
| `--project` / `-p` | Project name or ID |
| `--detect` | Auto-detect org from git config |
| `--yes` / `-y` | Skip confirmation prompts |
| `--open` | Open in web browser |
| `--output` / `-o` | Output format (json, table, tsv, yaml, jsonc, yamlc, none) |
| `--query` | JMESPath query string |

## Common Workflows

### Create PR from current branch

```bash
CURRENT_BRANCH=$(git branch --show-current)
az repos pr create \
  --source-branch $CURRENT_BRANCH \
  --target-branch main \
  --title "Feature: $(git log -1 --pretty=%B)" \
  --open
```

### Approve and complete PR

```bash
az repos pr set-vote --id {pr-id} --vote approve
az repos pr update --id {pr-id} --status completed
```

### Download latest pipeline artifact

```bash
RUN_ID=$(az pipelines runs list --pipeline {pipeline-id} --top 1 --query "[0].id" -o tsv)
az pipelines runs artifact download \
  --artifact-name 'webapp' \
  --path ./output \
  --run-id $RUN_ID
```

### Bulk update work items

```bash
for id in $(az boards query --wiql "SELECT ID FROM WorkItems WHERE State='New'" -o tsv); do
  az boards work-item update --id $id --state "Active"
done
```

### Run pipeline and wait for result

```bash
RUN_ID=$(az pipelines run --name "$PIPELINE_NAME" --query "id" -o tsv)
while true; do
  STATUS=$(az pipelines runs show --run-id $RUN_ID --query "status" -o tsv)
  if [[ "$STATUS" != "inProgress" && "$STATUS" != "notStarted" ]]; then break; fi
  sleep 10
done
RESULT=$(az pipelines runs show --run-id $RUN_ID --query "result" -o tsv)
echo "Pipeline result: $RESULT"
```

## References

For complete command details beyond the common operations above:

- [Pipelines, builds, releases, and agents](references/pipelines.md) - Variables, variable groups, builds, releases, agent pools, folders
- [Boards and work items](references/boards.md) - Area paths, iterations, work item relations, advanced WIQL
- [Repos, PRs, and policies](references/repos.md) - Git refs, branch policies, PR reviewers, repository import
- [Administration and advanced patterns](references/advanced.md) - Security, permissions, wikis, service endpoints, teams, users, scripting patterns, JMESPath
