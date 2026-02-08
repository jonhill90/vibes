# Administration and Advanced Patterns Reference

Covers service endpoints, teams, users, security, wikis, extensions, packages, and scripting patterns. For core commands, see [SKILL.md](../SKILL.md).

## Service Endpoints

```bash
# List service endpoints
az devops service-endpoint list --project {project} --output table

# Show service endpoint
az devops service-endpoint show --id {endpoint-id} --project {project}

# Create using configuration file
az devops service-endpoint create --service-endpoint-configuration endpoint.json --project {project}

# Delete service endpoint
az devops service-endpoint delete --id {endpoint-id} --project {project} --yes
```

## Teams

```bash
# List teams
az devops team list --project {project}

# Show team
az devops team show --team {team-name} --project {project}

# Create team
az devops team create \
  --name {team-name} \
  --description "Team description" \
  --project {project}

# Update team
az devops team update \
  --team {team-name} \
  --project {project} \
  --name "{new-team-name}" \
  --description "Updated description"

# Delete team
az devops team delete --team {team-name} --project {project} --yes

# Show team members
az devops team list-member --team {team-name} --project {project}
```

## Users

```bash
# List users
az devops user list --org https://dev.azure.com/{org} --output table

# Show user
az devops user show --user {user-id-or-email} --org https://dev.azure.com/{org}

# Add user
az devops user add \
  --email user@example.com \
  --license-type express \
  --org https://dev.azure.com/{org}

# Update user license
az devops user update \
  --user {user-id-or-email} \
  --license-type advanced \
  --org https://dev.azure.com/{org}

# Remove user
az devops user remove --user {user-id-or-email} --org https://dev.azure.com/{org} --yes
```

## Security Groups

### Group Management

```bash
# List groups in project
az devops security group list --project {project}

# List groups in organization
az devops security group list --scope organization

# Show group details
az devops security group show --group-id {group-id}

# Create group
az devops security group create \
  --name {group-name} \
  --description "Group description" \
  --project {project}

# Update group
az devops security group update \
  --group-id {group-id} \
  --name "{new-group-name}" \
  --description "Updated description"

# Delete group
az devops security group delete --group-id {group-id} --yes
```

### Group Memberships

```bash
# List memberships
az devops security group membership list --id {group-id}

# Add member
az devops security group membership add \
  --group-id {group-id} \
  --member-id {member-id}

# Remove member
az devops security group membership remove \
  --group-id {group-id} \
  --member-id {member-id} --yes
```

## Security Permissions

### Namespaces

```bash
# List namespaces
az devops security permission namespace list

# Show namespace details
az devops security permission namespace show --namespace "GitRepositories"
```

### List and Show Permissions

```bash
# List permissions for user/group
az devops security permission list \
  --id {user-or-group-id} \
  --namespace "GitRepositories" \
  --project {project}

# List for specific token (repository)
az devops security permission list \
  --id {user-or-group-id} \
  --namespace "GitRepositories" \
  --project {project} \
  --token "repoV2/{project}/{repository-id}"

# Show permissions
az devops security permission show \
  --id {user-or-group-id} \
  --namespace "GitRepositories" \
  --project {project} \
  --token "repoV2/{project}/{repository-id}"
```

### Update and Reset Permissions

```bash
# Grant permission
az devops security permission update \
  --id {user-or-group-id} \
  --namespace "GitRepositories" \
  --project {project} \
  --token "repoV2/{project}/{repository-id}" \
  --permission-mask "Pull,Contribute"

# Reset specific permission bits
az devops security permission reset \
  --id {user-or-group-id} \
  --namespace "GitRepositories" \
  --project {project} \
  --token "repoV2/{project}/{repository-id}" \
  --permission-mask "Pull,Contribute"

# Reset all permissions
az devops security permission reset-all \
  --id {user-or-group-id} \
  --namespace "GitRepositories" \
  --project {project} \
  --token "repoV2/{project}/{repository-id}" --yes
```

## Wikis

### Wiki Management

```bash
# List wikis
az devops wiki list --project {project}

# Show wiki
az devops wiki show --wiki {wiki-name} --project {project}

# Create project wiki
az devops wiki create \
  --name {wiki-name} \
  --project {project} \
  --type projectWiki

# Create code wiki from repository
az devops wiki create \
  --name {wiki-name} \
  --project {project} \
  --type codeWiki \
  --repository {repo-name} \
  --mapped-path /wiki

# Delete wiki
az devops wiki delete --wiki {wiki-id} --project {project} --yes
```

### Wiki Pages

```bash
# List pages
az devops wiki page list --wiki {wiki-name} --project {project}

# Show page
az devops wiki page show \
  --wiki {wiki-name} \
  --path "/page-name" \
  --project {project}

# Create page
az devops wiki page create \
  --wiki {wiki-name} \
  --path "/new-page" \
  --content "# New Page\n\nPage content here..." \
  --project {project}

# Update page
az devops wiki page update \
  --wiki {wiki-name} \
  --path "/existing-page" \
  --content "# Updated Page\n\nNew content..." \
  --project {project}

# Delete page
az devops wiki page delete \
  --wiki {wiki-name} \
  --path "/old-page" \
  --project {project} --yes
```

## Administration

### Banner Management

```bash
# List banners
az devops admin banner list

# Add new banner
az devops admin banner add \
  --message "System maintenance scheduled" \
  --level info  # info, warning, error

# Update banner
az devops admin banner update \
  --id {banner-id} \
  --message "Updated message" \
  --level warning \
  --expiration-date "2025-12-31T23:59:59Z"

# Remove banner
az devops admin banner remove --id {banner-id}
```

## DevOps Extensions

Manage extensions installed in the Azure DevOps organization (different from CLI extensions).

```bash
# List installed extensions
az devops extension list --org https://dev.azure.com/{org}

# Search marketplace
az devops extension search --search-query "docker"

# Install extension
az devops extension install \
  --ext-id {extension-id} \
  --org https://dev.azure.com/{org} \
  --publisher {publisher-id}

# Enable / disable extension
az devops extension enable --ext-id {extension-id} --org https://dev.azure.com/{org}
az devops extension disable --ext-id {extension-id} --org https://dev.azure.com/{org}

# Uninstall extension
az devops extension uninstall --ext-id {extension-id} --org https://dev.azure.com/{org} --yes
```

## Universal Packages (Azure Artifacts)

```bash
# Publish package
az artifacts universal publish \
  --feed {feed-name} \
  --name {package-name} \
  --version {version} \
  --path {package-path} \
  --project {project}

# Download package
az artifacts universal download \
  --feed {feed-name} \
  --name {package-name} \
  --version {version} \
  --path {download-path} \
  --project {project}
```

## Git Aliases

```bash
# Enable Git aliases for DevOps operations
az devops configure --use-git-aliases true

# Then use Git commands directly
git pr create --target-branch main
git pr list
git pr checkout 123
```

## Advanced JMESPath Queries

### Filtering and Sorting

```bash
# Filter by multiple conditions
az pipelines list --query "[?name.contains('CI') && enabled==true]"

# Sort by date (descending)
az pipelines runs list --query "sort_by([?status=='completed'], &finishTime | reverse(@))"

# Get top N after filtering
az pipelines runs list --query "[?result=='succeeded'] | [0:5]"
```

### Nested Queries

```bash
# Extract nested properties
az pipelines show --id $PIPELINE_ID --query "{Name:name, Repo:repository.{Name:name, Type:type}}"

# Query build details
az pipelines build show --id $BUILD_ID --query "{ID:id, Number:buildNumber, Status:status, Result:result, Requested:requestedFor.displayName}"
```

### Conditional and Default Values

```bash
# Conditional output
az pipelines list --query "[].{Name:name, Status:(enabled ? 'Enabled' : 'Disabled')}"

# Extract with defaults
az pipelines show --id $PIPELINE_ID --query "{Name:name, Folder:folder || 'Root', Description:description || 'No description'}"
```

## Scripting Patterns

### Retry Logic

```bash
retry_command() {
  local max_attempts=3
  local attempt=1
  local delay=5
  while [[ $attempt -le $max_attempts ]]; do
    if "$@"; then return 0; fi
    echo "Attempt $attempt failed. Retrying in ${delay}s..."
    sleep $delay
    ((attempt++))
    delay=$((delay * 2))
  done
  echo "All $max_attempts attempts failed"
  return 1
}

retry_command az pipelines run --name "$PIPELINE_NAME"
```

### Idempotent Create-or-Update

```bash
# Ensure pipeline exists
PIPELINE_ID=$(az pipelines list --query "[?name=='$PIPELINE_NAME'].id" -o tsv)
if [[ -z "$PIPELINE_ID" ]]; then
  az pipelines create --name "$PIPELINE_NAME" --yaml-path azure-pipelines.yml
fi

# Ensure variable group exists
VG_ID=$(az pipelines variable-group list --query "[?name=='$VG_NAME'].id" -o tsv)
if [[ -z "$VG_ID" ]]; then
  VG_ID=$(az pipelines variable-group create \
    --name "$VG_NAME" \
    --variables API_URL=$API_URL API_KEY=$API_KEY \
    --authorize true \
    --query "id" -o tsv)
fi
```

### Input Validation

```bash
if [[ -z "$PROJECT" || -z "$REPO" ]]; then
  echo "Error: PROJECT and REPO must be set"
  exit 1
fi

# Check if branch exists
if ! az repos ref list --repository "$REPO" --query "[?name=='refs/heads/$BRANCH']" -o tsv | grep -q .; then
  echo "Error: Branch $BRANCH does not exist"
  exit 1
fi
```

### Pipeline Orchestration

```bash
# Run pipeline and wait for completion
RUN_ID=$(az pipelines run --name "$PIPELINE_NAME" --query "id" -o tsv)
while true; do
  STATUS=$(az pipelines runs show --run-id $RUN_ID --query "status" -o tsv)
  if [[ "$STATUS" != "inProgress" && "$STATUS" != "notStarted" ]]; then break; fi
  sleep 10
done
RESULT=$(az pipelines runs show --run-id $RUN_ID --query "result" -o tsv)

# Create work item on failure
if [[ "$RESULT" != "succeeded" ]]; then
  az boards work-item create \
    --title "Build failed: Run $RUN_ID" \
    --type Bug \
    --description "Pipeline $PIPELINE_NAME failed with result: $RESULT"
fi
```

### Automated PR Creation

```bash
CURRENT_BRANCH=$(git branch --show-current)
LAST_COMMIT=$(git log -1 --pretty=%B)

PR_ID=$(az repos pr create \
  --source-branch "$CURRENT_BRANCH" \
  --target-branch main \
  --title "$LAST_COMMIT" \
  --auto-complete true \
  --query "pullRequestId" -o tsv)

az repos pr reviewer add --id $PR_ID --reviewers "$REVIEWER_EMAIL"
```

### Branch Policy Automation

```bash
# Apply policies to all repositories
REPOS=$(az repos list --project "$PROJECT" --query "[].id" -o tsv)
for repo_id in $REPOS; do
  az repos policy approver-count create \
    --blocking true --enabled true --branch main \
    --repository-id "$repo_id" --minimum-approver-count 2

  az repos policy work-item-linking create \
    --blocking true --enabled true --branch main \
    --repository-id "$repo_id"
done
```

### Service Connection Configuration

```bash
cat > service-connection.json <<'EOF'
{
  "data": {
    "subscriptionId": "$SUBSCRIPTION_ID",
    "subscriptionName": "My Subscription",
    "creationMode": "Manual"
  },
  "url": "https://management.azure.com/",
  "authorization": {
    "parameters": {
      "tenantid": "$TENANT_ID",
      "serviceprincipalid": "$SP_ID",
      "authenticationType": "spnKey",
      "serviceprincipalkey": "$SP_KEY"
    },
    "scheme": "ServicePrincipal"
  },
  "type": "azurerm",
  "isShared": false,
  "isReady": true
}
EOF

az devops service-endpoint create \
  --service-endpoint-configuration service-connection.json \
  --project "$PROJECT"
```
