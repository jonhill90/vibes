# Resource Groups - Organization Strategies

## Overview

Resource groups are fundamental Azure organizational units. Proper resource group design simplifies management, cost tracking, and access control.

---

## Resource Group Design Patterns

### Pattern 1: Environment-Based

**Use Case**: Separate dev, test, staging, production

```bash
az group create --name dev-rg --location eastus
az group create --name test-rg --location eastus
az group create --name staging-rg --location eastus
az group create --name prod-rg --location eastus
```

**Pros**:
- Clear environment isolation
- Easy to delete entire environment
- Simple RBAC (dev team = dev-rg)

**Cons**:
- Shared resources duplicated across environments
- Less granular cost tracking

---

### Pattern 2: Workload-Based

**Use Case**: Separate by application or service

```bash
az group create --name webapp-rg --location eastus
az group create --name api-rg --location eastus
az group create --name database-rg --location eastus
az group create --name monitoring-rg --location eastus
```

**Pros**:
- Clear ownership boundaries
- Independent lifecycle management
- Granular RBAC per workload

**Cons**:
- More resource groups to manage
- Potential for cross-RG dependencies

---

### Pattern 3: Lifecycle-Based

**Use Case**: Group by resource lifetime

```bash
az group create --name shared-network-rg --location eastus  # Long-lived
az group create --name app-compute-rg --location eastus     # Medium-lived
az group create --name temp-storage-rg --location eastus    # Short-lived
```

**Pros**:
- Prevents accidental deletion of long-lived resources
- Clear decommissioning boundaries

**Cons**:
- Requires understanding of resource lifetimes upfront

---

### Pattern 4: Hybrid (Recommended)

**Use Case**: Combine environment + workload

```bash
# Pattern: {environment}-{workload}-rg
az group create --name prod-webapp-rg --location eastus
az group create --name prod-api-rg --location eastus
az group create --name prod-data-rg --location eastus
az group create --name shared-network-rg --location eastus  # Cross-environment

az group create --name dev-webapp-rg --location eastus
az group create --name dev-api-rg --location eastus
```

**Pros**:
- Best of both worlds
- Clear environment + workload boundaries
- Flexible RBAC and cost tracking

**Cons**:
- More resource groups (manageable with naming convention)

---

## Naming Conventions

### Recommended Pattern

```
{environment}-{workload}-{resource-type}-rg

environment: dev, test, stage, prod, shared
workload: webapp, api, data, network, monitoring
resource-type: Optional (app, infra, etc.)
```

### Examples

```bash
prod-webapp-rg         # Production web application resources
dev-api-rg             # Development API resources
shared-network-rg      # Shared networking (cross-environment)
prod-data-infra-rg     # Production data infrastructure
test-ml-rg             # Testing machine learning workload
```

---

## Tagging Strategy

### Required Tags

```bash
az group create \
  --name prod-webapp-rg \
  --location eastus \
  --tags \
    Environment=production \
    CostCenter=engineering \
    Owner=team-platform \
    Project=customer-portal \
    ManagedBy=terraform
```

### Tag Inheritance

**Resource groups propagate tags to resources (if configured):**

```bash
# Create resource group with tags
az group create --name prod-webapp-rg --tags Environment=production

# Resources inherit tags (Azure Policy can enforce)
az vm create \
  --name webapp-vm-01 \
  --resource-group prod-webapp-rg
  # Inherits Environment=production
```

---

## RBAC Patterns

### Least Privilege

```bash
# Grant specific roles to resource groups

# Developers: Reader on prod, Contributor on dev
az role assignment create \
  --role "Reader" \
  --assignee dev-team@company.com \
  --resource-group prod-webapp-rg

az role assignment create \
  --role "Contributor" \
  --assignee dev-team@company.com \
  --resource-group dev-webapp-rg

# DevOps: Contributor on all RGs
az role assignment create \
  --role "Contributor" \
  --assignee devops-team@company.com \
  --resource-group prod-webapp-rg
```

### Custom Roles

```bash
# Create custom role for specific resource group
az role definition create --role-definition @custom-role.json

# Assign custom role
az role assignment create \
  --role "Custom VM Operator" \
  --assignee team@company.com \
  --resource-group prod-webapp-rg
```

---

## Cost Management

### Budget Alerts

```bash
# Create budget for resource group
az consumption budget create \
  --budget-name prod-webapp-budget \
  --amount 5000 \
  --time-grain Monthly \
  --start-date 2025-01-01 \
  --end-date 2025-12-31 \
  --resource-group prod-webapp-rg
```

### Cost Analysis by Tag

```bash
# Query costs by Environment tag
az consumption usage list \
  --query "[?tags.Environment=='production']" \
  --output table
```

---

## Lifecycle Management

### Resource Group Deletion

```bash
# Delete resource group (DELETES ALL RESOURCES!)
az group delete --name dev-webapp-rg --yes

# Delete without waiting
az group delete --name dev-webapp-rg --no-wait

# List deletions in progress
az group list --query "[?properties.provisioningState=='Deleting']"
```

### Resource Locks

```bash
# Prevent accidental deletion
az group lock create \
  --name prod-lock \
  --resource-group prod-webapp-rg \
  --lock-type CanNotDelete

# Prevent modifications
az group lock create \
  --name readonly-lock \
  --resource-group prod-data-rg \
  --lock-type ReadOnly
```

---

## Best Practices

1. **Use consistent naming**: Follow naming convention across all RGs
2. **Tag everything**: Enable cost tracking and ownership
3. **Apply locks**: Protect production resource groups
4. **Least privilege RBAC**: Grant minimum required access
5. **Set budgets**: Monitor spending per resource group
6. **Document organization**: Maintain RG design documentation
7. **Review regularly**: Audit resource groups quarterly
8. **Delete unused**: Remove empty or unnecessary RGs

---

**Resource Status**: COMPLETE ✅
**Line Count**: 235 ✅
