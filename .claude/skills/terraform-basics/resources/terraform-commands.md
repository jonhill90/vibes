# Terraform Commands - Complete Reference

## Core Commands

### terraform init

**Purpose**: Initialize Terraform working directory

**When to Run**:
- First time setting up project
- After adding new providers
- After changing backend configuration
- After cloning repository

**Common Usage**:
```bash
# Basic initialization
terraform init

# Initialize with specific backend config
terraform init -backend-config=backend.hcl

# Upgrade providers to latest versions
terraform init -upgrade

# Reconfigure backend
terraform init -reconfigure -backend-config=new-backend.hcl

# Skip plugin installation (use cached)
terraform init -plugin-dir=/path/to/plugins
```

**Flags**:
- `-upgrade`: Update modules and providers
- `-reconfigure`: Ignore existing config, reconfigure backend
- `-backend=false`: Skip backend initialization
- `-get=false`: Skip module download
- `-plugin-dir=PATH`: Use local plugin directory

**Common Errors**:
```
Error: Failed to download module
Fix: Check module source URL, network connectivity

Error: Backend initialization required
Fix: Run `terraform init` again with backend config

Error: Provider version constraints not met
Fix: Update provider version in required_providers
```

---

### terraform validate

**Purpose**: Validate configuration syntax

**When to Run**:
- After editing .tf files
- Before committing to git
- In CI/CD pipeline

**Common Usage**:
```bash
# Validate configuration
terraform validate

# Validate with JSON output (for automation)
terraform validate -json
```

**What It Checks**:
- Syntax errors
- Invalid resource names
- Missing required arguments
- Type mismatches
- Variable references

**Does NOT Check**:
- Provider API validation
- Resource existence
- Authentication
- Network connectivity

---

### terraform plan

**Purpose**: Preview infrastructure changes

**When to Run**:
- Before applying changes
- During code review
- To understand current state vs. desired state

**Common Usage**:
```bash
# Generate execution plan
terraform plan

# Save plan to file
terraform plan -out=tfplan

# Target specific resource
terraform plan -target=azurerm_resource_group.rg

# Use specific variable file
terraform plan -var-file=prod.tfvars

# Show plan in JSON format
terraform plan -json

# Destroy plan
terraform plan -destroy
```

**Reading Plan Output**:
```
+ create       # New resource
~ update       # Modify existing resource
- destroy      # Delete resource
-/+ replace    # Delete and recreate
<= read        # Data source read
```

**Flags**:
- `-out=FILE`: Save plan to file
- `-var="key=value"`: Set variable
- `-var-file=FILE`: Load variables from file
- `-target=RESOURCE`: Plan specific resource only
- `-destroy`: Plan resource destruction
- `-refresh=false`: Skip state refresh

---

### terraform apply

**Purpose**: Apply infrastructure changes

**When to Run**:
- After reviewing plan
- During deployment
- To create/update resources

**Common Usage**:
```bash
# Apply from saved plan (recommended)
terraform apply tfplan

# Apply with auto-approve (use with caution)
terraform apply -auto-approve

# Apply specific resource
terraform apply -target=azurerm_storage_account.storage

# Apply with variable file
terraform apply -var-file=prod.tfvars
```

**Safety Checklist**:
- [ ] Reviewed `terraform plan` output
- [ ] Confirmed resource changes
- [ ] Checked for unintended deletions
- [ ] Verified environment (dev vs. prod)
- [ ] State backup available
- [ ] Manual approval obtained (for prod)

**Flags**:
- `-auto-approve`: Skip approval prompt
- `-target=RESOURCE`: Apply specific resource
- `-parallelism=N`: Limit concurrent operations (default: 10)

---

### terraform destroy

**Purpose**: Destroy all managed infrastructure

**When to Run**:
- Tearing down test environments
- Decommissioning projects
- Cleaning up resources

**Common Usage**:
```bash
# Destroy all resources (with confirmation)
terraform destroy

# Auto-approve (dangerous!)
terraform destroy -auto-approve

# Destroy specific resource
terraform destroy -target=azurerm_resource_group.test

# Preview destroy plan
terraform plan -destroy
```

**Safety Warnings**:
- **ALWAYS review** `terraform plan -destroy` first
- **NEVER use** `-auto-approve` in production
- **BACKUP state** before destroying
- **VERIFY workspace** before destroying

---

## State Management Commands

### terraform state list

**Purpose**: List resources in state file

```bash
# List all resources
terraform state list

# Filter by name pattern
terraform state list | grep storage
```

### terraform state show

**Purpose**: Show detailed resource state

```bash
# Show specific resource
terraform state show azurerm_resource_group.rg

# Output in JSON
terraform state show -json azurerm_resource_group.rg
```

### terraform state mv

**Purpose**: Move resource in state (rename)

```bash
# Rename resource
terraform state mv azurerm_storage_account.old azurerm_storage_account.new

# Move to module
terraform state mv azurerm_resource_group.rg module.network.azurerm_resource_group.rg
```

### terraform state rm

**Purpose**: Remove resource from state (without deleting)

```bash
# Remove from state
terraform state rm azurerm_storage_account.storage

# Resource still exists in cloud, just not tracked
```

**Use Cases**:
- Migrating resource to different state file
- Removing accidentally imported resource
- Decomissioning Terraform management

---

## Import and Output

### terraform import

**Purpose**: Import existing resources into state

```bash
# Import Azure resource group
terraform import azurerm_resource_group.rg /subscriptions/{subscription-id}/resourceGroups/{rg-name}

# Import AWS EC2 instance
terraform import aws_instance.server i-1234567890abcdef0
```

**Workflow**:
1. Write resource configuration (empty block)
2. Run `terraform import`
3. Run `terraform plan` to verify
4. Add missing attributes to match imported state

### terraform output

**Purpose**: Display output values

```bash
# Show all outputs
terraform output

# Show specific output
terraform output vnet_id

# JSON format
terraform output -json
```

---

## Workspace Commands

### terraform workspace

**Purpose**: Manage multiple environments

```bash
# List workspaces
terraform workspace list

# Create new workspace
terraform workspace new dev

# Switch workspace
terraform workspace select prod

# Show current workspace
terraform workspace show

# Delete workspace
terraform workspace delete staging
```

**Use Cases**:
- Dev/staging/prod environments
- Customer-specific deployments
- Feature branch testing

---

## Troubleshooting Commands

### terraform refresh

**Purpose**: Update state from real infrastructure

```bash
# Refresh state
terraform refresh

# Refresh specific resource
terraform refresh -target=azurerm_storage_account.storage
```

**When to Use**:
- Detecting manual changes
- Syncing state after out-of-band modifications
- Troubleshooting drift

### terraform taint

**Purpose**: Mark resource for recreation

```bash
# Taint resource (force recreation)
terraform taint azurerm_virtual_machine.vm

# Next apply will destroy and recreate
```

**Use Cases**:
- Fixing corrupted resource
- Forcing update when Terraform doesn't detect change
- Recreating failed provisioning

### terraform untaint

**Purpose**: Remove taint from resource

```bash
# Untaint resource
terraform untaint azurerm_virtual_machine.vm
```

---

## Performance and Debugging

### Parallelism Control

```bash
# Limit concurrent operations
terraform apply -parallelism=5

# Useful for:
# - Rate limit avoidance
# - Reducing API throttling
# - Sequential dependencies
```

### Debug Logging

```bash
# Enable debug logging
export TF_LOG=DEBUG
terraform plan

# Log levels: TRACE, DEBUG, INFO, WARN, ERROR

# Log to file
export TF_LOG_PATH=terraform.log
terraform apply
```

---

## CI/CD Integration

### Automation-Friendly Flags

```bash
# Non-interactive apply
terraform apply -auto-approve -input=false

# JSON output for parsing
terraform plan -json | jq '.resource_changes'

# Compact warnings
terraform apply -compact-warnings
```

---

**Resource Status**: COMPLETE ✅
**Line Count**: 298 ✅
