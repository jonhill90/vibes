# Pipelines, Builds, Releases, and Agents Reference

Complete `az pipelines` command reference. For quick-start examples, see [SKILL.md](../SKILL.md).

## Pipelines

### List Pipelines

```bash
az pipelines list --output table
az pipelines list --query "[?name=='myPipeline']"
az pipelines list --folder-path 'folder/subfolder'
```

### Create Pipeline

```bash
# From local repository context (auto-detects settings)
az pipelines create --name 'ContosoBuild' --description 'Pipeline for contoso project'

# With specific branch and YAML path
az pipelines create \
  --name {pipeline-name} \
  --repository {repo} \
  --branch main \
  --yaml-path azure-pipelines.yml \
  --description "My CI/CD pipeline"

# For GitHub repository
az pipelines create \
  --name 'GitHubPipeline' \
  --repository https://github.com/Org/Repo \
  --branch main \
  --repository-type github

# Skip first run
az pipelines create --name 'MyPipeline' --skip-run true
```

### Show Pipeline

```bash
az pipelines show --id {pipeline-id}
az pipelines show --name {pipeline-name}
```

### Update Pipeline

```bash
az pipelines update --id {pipeline-id} --name "New name" --description "Updated description"
```

### Delete Pipeline

```bash
az pipelines delete --id {pipeline-id} --yes
```

### Run Pipeline

```bash
# Run by name
az pipelines run --name {pipeline-name} --branch main

# Run by ID
az pipelines run --id {pipeline-id} --branch refs/heads/main

# With parameters
az pipelines run --name {pipeline-name} --parameters version=1.0.0 environment=prod

# With variables
az pipelines run --name {pipeline-name} --variables buildId=123 configuration=release

# Open results in browser
az pipelines run --name {pipeline-name} --open
```

## Pipeline Runs

### List Runs

```bash
az pipelines runs list --pipeline {pipeline-id}
az pipelines runs list --name {pipeline-name} --top 10
az pipelines runs list --branch main --status completed
```

### Show Run Details

```bash
az pipelines runs show --run-id {run-id}
az pipelines runs show --run-id {run-id} --open
```

### Pipeline Artifacts

```bash
# List artifacts for a run
az pipelines runs artifact list --run-id {run-id}

# Download artifact
az pipelines runs artifact download \
  --artifact-name '{artifact-name}' \
  --path {local-path} \
  --run-id {run-id}

# Upload artifact
az pipelines runs artifact upload \
  --artifact-name '{artifact-name}' \
  --path {local-path} \
  --run-id {run-id}
```

### Pipeline Run Tags

```bash
az pipelines runs tag add --run-id {run-id} --tags production v1.0
az pipelines runs tag list --run-id {run-id} --output table
```

## Builds

### List Builds

```bash
az pipelines build list
az pipelines build list --definition {build-definition-id}
az pipelines build list --status completed --result succeeded
```

### Queue Build

```bash
az pipelines build queue --definition {build-definition-id} --branch main
az pipelines build queue --definition {build-definition-id} --parameters version=1.0.0
```

### Show Build Details

```bash
az pipelines build show --id {build-id}
```

### Cancel Build

```bash
az pipelines build cancel --id {build-id}
```

### Build Tags

```bash
az pipelines build tag add --build-id {build-id} --tags prod release
az pipelines build tag delete --build-id {build-id} --tag prod
```

### Build Definitions

```bash
az pipelines build definition list
az pipelines build definition list --name {definition-name}
az pipelines build definition show --id {definition-id}
```

## Releases

### List Releases

```bash
az pipelines release list
az pipelines release list --definition {release-definition-id}
```

### Create Release

```bash
az pipelines release create --definition {release-definition-id}
az pipelines release create --definition {release-definition-id} --description "Release v1.0"
```

### Show Release

```bash
az pipelines release show --id {release-id}
```

### Release Definitions

```bash
az pipelines release definition list
az pipelines release definition show --id {definition-id}
```

## Pipeline Variables

### List Variables

```bash
az pipelines variable list --pipeline-id {pipeline-id}
```

### Create Variable

```bash
# Non-secret variable
az pipelines variable create \
  --name {var-name} \
  --value {var-value} \
  --pipeline-id {pipeline-id}

# Secret variable
az pipelines variable create \
  --name {var-name} \
  --secret true \
  --pipeline-id {pipeline-id}

# Secret with prompt
az pipelines variable create \
  --name {var-name} \
  --secret true \
  --prompt true \
  --pipeline-id {pipeline-id}
```

### Update Variable

```bash
az pipelines variable update \
  --name {var-name} \
  --value {new-value} \
  --pipeline-id {pipeline-id}

# Update secret variable
az pipelines variable update \
  --name {var-name} \
  --secret true \
  --value "{new-secret-value}" \
  --pipeline-id {pipeline-id}
```

### Delete Variable

```bash
az pipelines variable delete --name {var-name} --pipeline-id {pipeline-id} --yes
```

## Variable Groups

### List Variable Groups

```bash
az pipelines variable-group list
az pipelines variable-group list --output table
```

### Show Variable Group

```bash
az pipelines variable-group show --id {group-id}
```

### Create Variable Group

```bash
az pipelines variable-group create \
  --name {group-name} \
  --variables key1=value1 key2=value2 \
  --authorize true
```

### Update Variable Group

```bash
az pipelines variable-group update \
  --id {group-id} \
  --name {new-name} \
  --description "Updated description"
```

### Delete Variable Group

```bash
az pipelines variable-group delete --id {group-id} --yes
```

### Variable Group Variables

```bash
# List variables in group
az pipelines variable-group variable list --group-id {group-id}

# Create non-secret variable
az pipelines variable-group variable create \
  --group-id {group-id} \
  --name {var-name} \
  --value {var-value}

# Create secret variable
az pipelines variable-group variable create \
  --group-id {group-id} \
  --name {var-name} \
  --secret true

# Secret with environment variable
export AZURE_DEVOPS_EXT_PIPELINE_VAR_MySecret=secretvalue
az pipelines variable-group variable create \
  --group-id {group-id} \
  --name MySecret \
  --secret true

# Update variable
az pipelines variable-group variable update \
  --group-id {group-id} \
  --name {var-name} \
  --value {new-value} \
  --secret false

# Delete variable
az pipelines variable-group variable delete \
  --group-id {group-id} \
  --name {var-name}
```

## Pipeline Folders

```bash
# List folders
az pipelines folder list

# Create folder
az pipelines folder create --path 'folder/subfolder' --description "My folder"

# Delete folder
az pipelines folder delete --path 'folder/subfolder'

# Update folder
az pipelines folder update --path 'old-folder' --new-path 'new-folder'
```

## Agent Pools

```bash
# List agent pools
az pipelines pool list
az pipelines pool list --pool-type automation
az pipelines pool list --pool-type deployment

# Show agent pool
az pipelines pool show --pool-id {pool-id}
```

## Agent Queues

```bash
# List agent queues
az pipelines queue list
az pipelines queue list --pool-name {pool-name}

# Show agent queue
az pipelines queue show --id {queue-id}
```

## Agents

```bash
# List agents in pool
az pipelines agent list --pool-id {pool-id}

# Show agent details
az pipelines agent show --agent-id {agent-id} --pool-id {pool-id}
```
