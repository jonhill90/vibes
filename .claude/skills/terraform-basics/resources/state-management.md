# State Management - Deep Dive

## Overview

Terraform state is the single source of truth for infrastructure. Proper state management is critical for team collaboration, disaster recovery, and operational safety.

---

## Remote State Backends

### Azure Storage Backend

**Recommended for Azure-heavy infrastructure**

```hcl
terraform {
  backend "azurerm" {
    resource_group_name  = "terraform-state-rg"
    storage_account_name = "tfstatestorage"
    container_name       = "tfstate"
    key                  = "prod.terraform.tfstate"

    # Optional: Enable versioning
    # Configured at storage account level
  }
}
```

**Setup**:
```bash
# Create resource group
az group create --name terraform-state-rg --location eastus

# Create storage account
az storage account create \
  --name tfstatestorage \
  --resource-group terraform-state-rg \
  --location eastus \
  --sku Standard_LRS

# Create container
az storage container create \
  --name tfstate \
  --account-name tfstatestorage
```

**State Locking**: Automatic via blob lease mechanism

---

### AWS S3 Backend

**Recommended for AWS-heavy infrastructure**

```hcl
terraform {
  backend "s3" {
    bucket         = "my-terraform-state"
    key            = "prod/terraform.tfstate"
    region         = "us-east-1"
    dynamodb_table = "terraform-locks"  # For locking
    encrypt        = true
  }
}
```

**Setup**:
```bash
# Create S3 bucket
aws s3 mb s3://my-terraform-state --region us-east-1

# Enable versioning
aws s3api put-bucket-versioning \
  --bucket my-terraform-state \
  --versioning-configuration Status=Enabled

# Create DynamoDB table for locking
aws dynamodb create-table \
  --table-name terraform-locks \
  --attribute-definitions AttributeName=LockID,AttributeType=S \
  --key-schema AttributeName=LockID,KeyType=HASH \
  --billing-mode PAY_PER_REQUEST
```

**State Locking**: DynamoDB-based (explicit configuration)

---

### Terraform Cloud Backend

**Recommended for multi-cloud or distributed teams**

```hcl
terraform {
  backend "remote" {
    organization = "my-org"

    workspaces {
      name = "prod-infrastructure"
    }
  }
}
```

**Features**:
- Built-in state locking
- State versioning
- Remote execution
- Access controls
- Audit logs

---

## State Locking

### Why Locking Matters

**Without Locking**:
```
User A: terraform apply (starts)
User B: terraform apply (starts simultaneously)
Result: State corruption, race conditions, data loss
```

**With Locking**:
```
User A: terraform apply (acquires lock)
User B: terraform apply (waits for lock)
User A: Completes, releases lock
User B: Acquires lock, proceeds
Result: Sequential, safe execution
```

### Lock Troubleshooting

**Stuck Lock (After Crash)**:
```bash
# Check lock status
terraform plan
# Error: state locked

# Force unlock (use with caution)
terraform force-unlock LOCK_ID

# Verify no other operations running before force-unlock!
```

**Manual Lock Release**:

*Azure Storage*:
```bash
# Break lease on blob
az storage blob lease break \
  --container-name tfstate \
  --blob-name prod.terraform.tfstate \
  --account-name tfstatestorage
```

*AWS S3/DynamoDB*:
```bash
# Delete lock item
aws dynamodb delete-item \
  --table-name terraform-locks \
  --key '{"LockID": {"S": "my-terraform-state/prod/terraform.tfstate"}}'
```

---

## State Migration

### Migrating from Local to Remote

**Step 1: Backup local state**
```bash
cp terraform.tfstate terraform.tfstate.backup
```

**Step 2: Add backend configuration**
```hcl
terraform {
  backend "azurerm" {
    # ... backend config
  }
}
```

**Step 3: Initialize with migration**
```bash
terraform init -migrate-state

# Terraform will prompt:
# "Do you want to copy existing state to the new backend?"
# Answer: yes
```

**Step 4: Verify migration**
```bash
# Check local state deleted
ls terraform.tfstate  # Should not exist

# Verify remote state
terraform state list
```

---

### Migrating Between Remote Backends

**Scenario**: Moving from Azure Storage to Terraform Cloud

**Step 1: Pull current state**
```bash
terraform state pull > terraform.tfstate.backup
```

**Step 2: Update backend configuration**
```hcl
terraform {
  backend "remote" {
    # New backend config
  }
}
```

**Step 3: Re-initialize**
```bash
terraform init -migrate-state
```

**Step 4: Verify**
```bash
terraform plan
# Should show "No changes" if migration successful
```

---

## State Versioning and Backup

### Azure Storage Versioning

```bash
# Enable blob versioning (one-time setup)
az storage account blob-service-properties update \
  --account-name tfstatestorage \
  --enable-versioning true

# List versions
az storage blob list \
  --container-name tfstate \
  --account-name tfstatestorage \
  --include v

# Restore previous version
az storage blob copy start \
  --source-container tfstate \
  --source-blob prod.terraform.tfstate \
  --destination-container tfstate \
  --destination-blob prod.terraform.tfstate \
  --account-name tfstatestorage \
  --source-version-id VERSION_ID
```

### Manual Backups

```bash
# Pull and backup state
terraform state pull > state-backup-$(date +%Y%m%d-%H%M%S).tfstate

# Scheduled backup (cron)
0 2 * * * cd /path/to/terraform && terraform state pull > backups/state-$(date +\%Y\%m\%d).tfstate
```

---

## Disaster Recovery

### Scenario 1: Corrupted State

**Symptoms**:
- `terraform plan` shows unexpected changes
- Resources exist but Terraform wants to recreate
- State file size is 0 bytes

**Recovery**:
```bash
# 1. Restore from backup
terraform state push terraform.tfstate.backup

# 2. Or restore from remote backend version
# (Azure Storage versioning, S3 versioning, Terraform Cloud)

# 3. Verify recovery
terraform plan
```

---

### Scenario 2: Lost State File

**Symptoms**:
- State file deleted or inaccessible
- `terraform plan` shows all resources to be created
- Resources exist in cloud

**Recovery Option 1: Import All Resources**
```bash
# For each resource, import
terraform import azurerm_resource_group.rg /subscriptions/SUB_ID/resourceGroups/RG_NAME
terraform import azurerm_storage_account.storage /subscriptions/SUB_ID/resourceGroups/RG/providers/Microsoft.Storage/storageAccounts/ACCOUNT

# Tedious for large infrastructures
```

**Recovery Option 2: Restore from Backup**
```bash
# Pull latest backup
terraform state push state-backup-latest.tfstate
```

---

### Scenario 3: State Drift (Manual Changes)

**Symptoms**:
- Resources modified outside Terraform
- `terraform plan` shows changes to revert

**Detection**:
```bash
# Refresh state from real infrastructure
terraform refresh

# Compare plan
terraform plan
# Shows drift as updates
```

**Resolution Options**:

*Option 1: Accept drift, update Terraform*
```bash
# Refresh state
terraform refresh

# Update .tf files to match reality
# Next apply will be no-op
```

*Option 2: Revert drift, enforce Terraform*
```bash
# Apply Terraform configuration
terraform apply
# Reverts manual changes
```

---

## State Security

### Sensitive Data in State

**Problem**: State files contain sensitive data (passwords, keys, connection strings)

**Mitigation Strategies**:

1. **Encrypt at Rest**:
   ```hcl
   # Azure Storage: Encryption enabled by default
   # S3: Enable encryption
   terraform {
     backend "s3" {
       encrypt = true
     }
   }
   ```

2. **Restrict Access**:
   ```bash
   # Azure: RBAC on storage account
   az role assignment create \
     --role "Storage Blob Data Contributor" \
     --assignee USER_PRINCIPAL \
     --scope /subscriptions/SUB_ID/resourceGroups/RG/providers/Microsoft.Storage/storageAccounts/STORAGE

   # AWS: IAM policies on S3 bucket and DynamoDB table
   ```

3. **Use Secrets Management**:
   ```hcl
   # Reference secrets from vault, not state
   data "azurerm_key_vault_secret" "db_password" {
     name         = "db-password"
     key_vault_id = data.azurerm_key_vault.vault.id
   }

   resource "azurerm_sql_server" "sql" {
     administrator_login_password = data.azurerm_key_vault_secret.db_password.value
   }
   ```

---

## Multi-Workspace State Management

### Workspace Isolation

Each workspace has separate state file:
```
terraform.tfstate.d/
├── dev/
│   └── terraform.tfstate
├── staging/
│   └── terraform.tfstate
└── prod/
    └── terraform.tfstate
```

### Workspace Naming Strategy

```bash
# Environment-based
terraform workspace new dev
terraform workspace new prod

# Customer-based
terraform workspace new customer-a
terraform workspace new customer-b

# Feature-based
terraform workspace new feature-x
```

---

**Resource Status**: COMPLETE ✅
**Line Count**: 285 ✅
