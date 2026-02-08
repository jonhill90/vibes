# Actions, Secrets, and Variables

For quick-start examples, see [SKILL.md](../SKILL.md).

## Workflow Management

### Enable / Disable Workflows

```bash
# Disable a workflow
gh workflow disable {workflow-name}

# Enable a workflow
gh workflow enable {workflow-name}

# View workflow YAML
gh workflow view {workflow-name} --yaml
```

### List Workflows with Filters

```bash
# List all workflows (including disabled)
gh workflow list --all

# JSON output with specific fields
gh workflow list --json id,name,state --jq '.[] | select(.state == "active")'
```

## Run Management

### Re-run with Options

```bash
# Re-run all jobs
gh run rerun {run-id}

# Re-run only failed jobs
gh run rerun {run-id} --failed

# Re-run with debug logging enabled
gh run rerun {run-id} --debug

# Re-run failed jobs with debug
gh run rerun {run-id} --failed --debug
```

### View Run Logs

```bash
# Full log output
gh run view {run-id} --log

# Only failed step logs
gh run view {run-id} --log-failed

# View specific job logs
gh run view {run-id} --job {job-id} --log
```

### List Runs with Filters

```bash
# Filter by workflow, branch, status
gh run list --workflow ci.yml --branch main --status completed --limit 20

# Filter by event type
gh run list --event push
gh run list --event pull_request

# Filter by user
gh run list --user octocat

# JSON output
gh run list --json databaseId,status,conclusion,headBranch \
  --jq '.[] | select(.conclusion == "failure")'
```

## Artifacts

### Download Artifacts

```bash
# Download all artifacts from a run
gh run download {run-id}

# Download specific artifact by name
gh run download {run-id} --name "build-output"

# Download to custom directory
gh run download {run-id} --dir ./my-artifacts

# Download matching a pattern
gh run download {run-id} --pattern "build-*"

# List artifacts without downloading
gh run view {run-id} --json jobs --jq '.jobs[].steps'
```

### Scripting: Download Latest Artifact

```bash
# Get latest successful run ID for a workflow
RUN_ID=$(gh run list \
  --workflow ci.yml \
  --status success \
  --limit 1 \
  --json databaseId \
  --jq '.[0].databaseId')

# Download specific artifact
gh run download "$RUN_ID" --name "dist" --dir ./output
```

## Secrets

### Repository Secrets

```bash
# Set a secret
gh secret set SECRET_NAME --body "secret-value"

# Set from file
gh secret set SECRET_NAME < secret.txt

# Set from environment variable
gh secret set SECRET_NAME --body "$MY_SECRET"

# List secrets
gh secret list

# Delete a secret
gh secret delete SECRET_NAME
```

### Organization Secrets

```bash
# Set org secret (visible to all repos)
gh secret set SECRET_NAME --org my-org --body "value"

# Set org secret for specific repos
gh secret set SECRET_NAME --org my-org \
  --repos repo1,repo2 \
  --body "value"

# Set org secret for private repos only
gh secret set SECRET_NAME --org my-org \
  --visibility private \
  --body "value"

# List org secrets
gh secret list --org my-org
```

### Environment Secrets

```bash
# Set environment secret
gh secret set SECRET_NAME --env production --body "value"

# List environment secrets
gh secret list --env production

# Delete environment secret
gh secret delete SECRET_NAME --env production
```

## Variables

### Repository Variables

```bash
# Set a variable
gh variable set VAR_NAME --body "value"

# List variables
gh variable list

# Get a variable value
gh variable get VAR_NAME

# Delete a variable
gh variable delete VAR_NAME
```

### Organization Variables

```bash
# Set org variable
gh variable set VAR_NAME --org my-org --body "value"

# Set for specific repos
gh variable set VAR_NAME --org my-org --repos repo1,repo2 --body "value"

# List org variables
gh variable list --org my-org
```

### Environment Variables

```bash
# Set environment variable
gh variable set VAR_NAME --env staging --body "value"

# List environment variables
gh variable list --env staging

# Delete environment variable
gh variable delete VAR_NAME --env staging
```

## Cache Management

```bash
# List caches
gh cache list

# List with sort and filter
gh cache list --sort size --order desc --limit 10
gh cache list --key "npm-"

# Delete specific cache
gh cache delete {cache-id}

# Delete caches matching a key
gh cache delete --all --key "npm-"
```

## CI Scripting Patterns

### Poll for Run Completion

```bash
# Start workflow and capture run
gh workflow run deploy.yml -f env=staging
sleep 5  # Allow run to register

RUN_ID=$(gh run list \
  --workflow deploy.yml \
  --limit 1 \
  --json databaseId \
  --jq '.[0].databaseId')

# Watch and exit with run's status code
gh run watch "$RUN_ID" --exit-status
echo "Run completed with exit code: $?"
```

### Get Failed Runs for a Branch

```bash
gh run list \
  --branch main \
  --status failure \
  --limit 5 \
  --json databaseId,displayTitle,conclusion,createdAt \
  --jq '.[] | "\(.databaseId)\t\(.displayTitle)\t\(.createdAt)"'
```

### Rerun All Failed Runs

```bash
gh run list --status failure --limit 10 --json databaseId --jq '.[].databaseId' | while read -r id; do
  gh run rerun "$id" --failed
done
```

### Download Artifacts from Multiple Runs

```bash
for run_id in $(gh run list --workflow release.yml --status success --limit 5 --json databaseId --jq '.[].databaseId'); do
  gh run download "$run_id" --dir "./artifacts/$run_id"
done
```
