# Issues and Labels

For quick-start examples, see [SKILL.md](../SKILL.md).

## Advanced Issue Operations

### Issue Templates

```bash
# Create issue with body from file
gh issue create --title "Bug report" --body-file .github/ISSUE_TEMPLATE/bug_report.md

# Interactive creation picks up templates automatically
gh issue create
```

### Pin / Unpin Issues

```bash
# Pin an issue to the repo
gh issue pin 456

# Unpin an issue
gh issue unpin 456
```

### Transfer Issues

```bash
# Transfer issue to another repository
gh issue transfer 456 OWNER/OTHER-REPO
```

### Develop (Linked Branches)

```bash
# Create a linked branch for an issue
gh issue develop 456

# Create with specific branch name and base
gh issue develop 456 --name "fix/issue-456" --base main

# Create and check out immediately
gh issue develop 456 --checkout
```

### Lock / Unlock Conversations

```bash
# Lock an issue conversation
gh issue lock 456 --reason "resolved"

# Lock reasons: off-topic, too heated, resolved, spam
gh issue lock 456 --reason "spam"

# Unlock
gh issue unlock 456
```

### Delete Issues

```bash
# Delete an issue (requires admin permissions)
gh issue delete 456 --yes
```

### Close with Reason

```bash
# Close as completed (default)
gh issue close 456

# Close as not planned
gh issue close 456 --reason "not planned"

# Close with comment
gh issue close 456 --comment "Closing — duplicate of #123"
```

### Edit Issue Fields

```bash
# Edit title and body
gh issue edit 456 --title "New title" --body "Updated description"

# Manage labels
gh issue edit 456 --add-label "priority","backend" --remove-label "triage"

# Manage assignees
gh issue edit 456 --add-assignee user1 --remove-assignee user2

# Set milestone and project
gh issue edit 456 --milestone "v3.0" --add-project "Roadmap"
```

## Labels

### Create Labels

```bash
# Create a label
gh label create "priority/high" --description "High priority" --color FF0000

# Color can be hex (with or without #)
gh label create "type/bug" --description "Bug report" --color "#d73a4a"

# Force create (update if exists)
gh label create "status/wip" --description "Work in progress" --color 0E8A16 --force
```

### List Labels

```bash
# List all labels
gh label list

# JSON output
gh label list --json name,description,color

# Filter with jq
gh label list --json name --jq '.[].name' | sort
```

### Edit Labels

```bash
# Rename a label
gh label edit "bug" --name "type/bug"

# Change color and description
gh label edit "type/bug" --color "d73a4a" --description "Something isn't working"
```

### Delete Labels

```bash
# Delete a label
gh label delete "old-label" --yes
```

### Clone Labels

```bash
# Clone all labels from one repo to another
gh label clone SOURCE-OWNER/SOURCE-REPO --force

# Clone into a specific repo
gh label clone SOURCE-OWNER/SOURCE-REPO --repo TARGET-OWNER/TARGET-REPO
```

## Search

### Search Issues

```bash
# Search issues across GitHub
gh search issues "memory leak" --language go --state open --limit 20

# Search within a specific repo
gh search issues "auth error" --repo OWNER/REPO

# Search with qualifiers
gh search issues "label:bug assignee:@me state:open"

# JSON output
gh search issues "type:bug" --json number,title,repository --jq '.[] | "\(.repository.name)#\(.number): \(.title)"'
```

### Search Pull Requests

```bash
# Search PRs
gh search prs "refactor" --state merged --author @me

# Search by review status
gh search prs "review:approved" --repo OWNER/REPO

# Search draft PRs
gh search prs "draft:true" --repo OWNER/REPO
```

## Bulk Operations

### Bulk Close Issues

```bash
# Close all issues with a specific label
gh issue list --label "wontfix" --json number --jq '.[].number' | while read -r num; do
  gh issue close "$num" --reason "not planned"
done
```

### Bulk Label Issues

```bash
# Add label to all open issues assigned to you
gh issue list --assignee @me --json number --jq '.[].number' | while read -r num; do
  gh issue edit "$num" --add-label "in-progress"
done
```

### Bulk Transfer Issues

```bash
# Transfer all issues with a label to another repo
gh issue list --label "moved" --json number --jq '.[].number' | while read -r num; do
  gh issue transfer "$num" OWNER/NEW-REPO
done
```

### Export Issues to CSV

```bash
gh issue list --state all --limit 500 \
  --json number,title,state,labels,assignees,createdAt \
  --jq '(["Number","Title","State","Labels","Assignees","Created"] | @csv),
        (.[] | [
          .number,
          .title,
          .state,
          ([.labels[].name] | join(";")),
          ([.assignees[].login] | join(";")),
          .createdAt
        ] | @csv)' > issues.csv
```
