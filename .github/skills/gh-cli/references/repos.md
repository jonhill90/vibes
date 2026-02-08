# Repos and Releases

For quick-start examples, see [SKILL.md](../SKILL.md).

## Repository Creation

### Create from Template

```bash
# Create repo from a template
gh repo create my-project --template OWNER/TEMPLATE-REPO --public --clone

# Create from template without cloning
gh repo create my-project --template OWNER/TEMPLATE-REPO --private
```

### Create with Options

```bash
# Create with README, license, and gitignore
gh repo create my-project \
  --public \
  --add-readme \
  --license mit \
  --gitignore Node \
  --description "My new project" \
  --clone

# Create in an organization
gh repo create my-org/my-project --private --team engineering

# Create from local directory
gh repo create --source . --public --push
```

## Repository Settings

### Edit Repository Properties

```bash
# Change description and homepage
gh repo edit --description "A cool project" --homepage "https://example.com"

# Change visibility
gh repo edit --visibility public
gh repo edit --visibility private

# Change default branch
gh repo edit --default-branch develop

# Toggle features
gh repo edit --enable-wiki=false
gh repo edit --enable-issues=true
gh repo edit --enable-projects=false
gh repo edit --enable-discussions=true

# Configure merge options
gh repo edit --enable-merge-commit=true
gh repo edit --enable-squash-merge=true
gh repo edit --enable-rebase-merge=false
gh repo edit --enable-auto-merge=true

# Delete branch on merge
gh repo edit --delete-branch-on-merge=true

# Allow forking (org repos)
gh repo edit --allow-forking=true

# Set topics
gh repo edit --add-topic "cli","golang" --remove-topic "old-topic"
```

### Archive / Unarchive

```bash
# Archive a repository (read-only)
gh repo archive OWNER/REPO --yes

# Unarchive
gh repo unarchive OWNER/REPO --yes
```

### Rename / Delete

```bash
# Rename repository
gh repo rename new-name --yes

# Delete repository (destructive!)
gh repo delete OWNER/REPO --yes
```

## Fork Management

### Fork with Options

```bash
# Fork to your account
gh repo fork OWNER/REPO

# Fork and clone locally
gh repo fork OWNER/REPO --clone

# Fork to an organization
gh repo fork OWNER/REPO --org my-org

# Fork with custom remote name
gh repo fork OWNER/REPO --remote-name upstream
```

### Sync Fork

```bash
# Sync default branch with upstream
gh repo sync OWNER/FORK

# Sync specific branch
gh repo sync OWNER/FORK --branch develop

# Sync and force (overwrite local changes)
gh repo sync OWNER/FORK --force
```

## Deploy Keys

```bash
# Add a deploy key
gh repo deploy-key add key.pub --title "CI Server"

# Add with write access
gh repo deploy-key add key.pub --title "Deploy Bot" --allow-write

# List deploy keys
gh repo deploy-key list

# Delete a deploy key
gh repo deploy-key delete {key-id}
```

## Rulesets

```bash
# List rulesets
gh ruleset list

# List org rulesets
gh ruleset list --org my-org

# View ruleset details
gh ruleset view {ruleset-id}

# View with web
gh ruleset view {ruleset-id} --web

# Check which rules apply to a branch
gh ruleset check --branch main
```

## Release Management

### Create with Assets

```bash
# Create release and upload assets
gh release create v1.0.0 \
  ./dist/app-linux-amd64.tar.gz \
  ./dist/app-darwin-amd64.tar.gz \
  ./dist/app-windows-amd64.zip \
  --title "v1.0.0" \
  --generate-notes

# Upload additional assets after creation
gh release upload v1.0.0 ./dist/checksums.txt
```

### Edit Releases

```bash
# Edit title and notes
gh release edit v1.0.0 --title "v1.0.0 - Stable" --notes "Updated notes"

# Convert to/from draft
gh release edit v1.0.0 --draft=false
gh release edit v1.0.0 --draft=true

# Convert to/from prerelease
gh release edit v1.0.0 --prerelease=false

# Set as latest
gh release edit v1.0.0 --latest
```

### Delete Releases and Assets

```bash
# Delete a release
gh release delete v1.0.0 --yes

# Delete release and its tag
gh release delete v1.0.0 --yes --cleanup-tag

# Delete a specific asset
gh release delete-asset v1.0.0 "old-binary.tar.gz" --yes
```

### Download Assets

```bash
# Download all assets
gh release download v1.0.0

# Download to specific directory
gh release download v1.0.0 --dir ./release-assets

# Download matching pattern
gh release download v1.0.0 --pattern "*.tar.gz"

# Download from latest release
gh release download --pattern "*.zip"

# Skip existing files
gh release download v1.0.0 --skip-existing
```

### Attestation and Verification

```bash
# Verify artifact attestation
gh attestation verify ./dist/app-linux-amd64.tar.gz --repo OWNER/REPO

# List attestations
gh attestation list --repo OWNER/REPO
```

### List Releases with Filters

```bash
# List releases
gh release list --limit 10

# Exclude drafts and prereleases
gh release list --exclude-drafts --exclude-pre-releases

# JSON output
gh release list --json tagName,name,publishedAt,isPrerelease \
  --jq '.[] | "\(.tagName)\t\(.name)\t\(.publishedAt)"'
```

## Repository Listing

```bash
# List your repos
gh repo list --limit 30

# Filter by visibility and language
gh repo list --visibility public --language typescript

# List org repos
gh repo list my-org --limit 50

# Filter archived repos
gh repo list --archived

# JSON output with fields
gh repo list --json name,description,isPrivate,primaryLanguage \
  --jq '.[] | "\(.name)\t\(.primaryLanguage.name // "none")\t\(.description // "")"'

# Sort by various criteria
gh repo list --sort stars --order desc
gh repo list --sort updated
```
