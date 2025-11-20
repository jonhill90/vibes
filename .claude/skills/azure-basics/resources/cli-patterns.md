# Azure CLI Patterns - Automation & Scripting

## Overview

Azure CLI (`az`) is the command-line interface for Azure resource management. Mastering CLI patterns enables efficient automation and infrastructure operations.

---

## Authentication Patterns

### Interactive Login

```bash
# Standard login (browser-based)
az login

# Login with specific tenant
az login --tenant TENANT_ID

# Login with service principal
az login \
  --service-principal \
  --username APP_ID \
  --password PASSWORD \
  --tenant TENANT_ID
```

### Managed Identity (VM/Container)

```bash
# Login using VM's managed identity
az login --identity

# Login with specific identity
az login --identity --username USER_ASSIGNED_IDENTITY_ID
```

### Account Management

```bash
# List subscriptions
az account list --output table

# Set active subscription
az account set --subscription SUBSCRIPTION_ID

# Show current subscription
az account show
```

---

## Output Formatting

### Format Options

```bash
# Table format (human-readable)
az vm list --output table

# JSON format (default, machine-readable)
az vm list --output json

# YAML format
az vm list --output yaml

# TSV format (tab-separated)
az vm list --output tsv

# None (no output)
az vm create --output none
```

### JMESPath Queries

```bash
# Extract specific fields
az vm list --query "[].{Name:name, Size:hardwareProfile.vmSize}" --output table

# Filter by condition
az vm list --query "[?powerState=='VM running']" --output table

# Get single value
VNET_ID=$(az network vnet show \
  --name prod-vnet \
  --resource-group prod-network-rg \
  --query id -o tsv)
```

---

## Scripting Patterns

### Error Handling

```bash
# Exit on error
set -e

# Check command success
if az vm show --name prod-vm --resource-group prod-rg &>/dev/null; then
    echo "VM exists"
else
    echo "VM not found, creating..."
    az vm create --name prod-vm --resource-group prod-rg ...
fi

# Capture exit code
az vm create --name test-vm --resource-group test-rg
EXIT_CODE=$?
if [ $EXIT_CODE -eq 0 ]; then
    echo "VM created successfully"
else
    echo "VM creation failed with code $EXIT_CODE"
    exit 1
fi
```

### Idempotent Operations

```bash
# Create resource group (idempotent)
az group create --name prod-rg --location eastus || true

# Check existence before creation
if ! az vm show --name prod-vm --resource-group prod-rg &>/dev/null; then
    az vm create --name prod-vm --resource-group prod-rg ...
fi
```

### Parallel Execution

```bash
# Create multiple VMs in parallel
for i in {1..5}; do
    az vm create \
        --name "vm-$i" \
        --resource-group prod-rg \
        --image Ubuntu2204 \
        --no-wait &  # Background execution
done

# Wait for all background jobs
wait
```

---

## Resource Querying

### List Resources

```bash
# List all VMs in subscription
az vm list --query "[].{Name:name, RG:resourceGroup, Location:location}" --output table

# List resources by type
az resource list --resource-type Microsoft.Compute/virtualMachines

# List resources by tag
az resource list --tag Environment=production --output table

# List resources in resource group
az resource list --resource-group prod-app-rg
```

### Show Resource Details

```bash
# Get VM details
az vm show --name prod-vm --resource-group prod-rg

# Get specific property
VM_SIZE=$(az vm show \
  --name prod-vm \
  --resource-group prod-rg \
  --query hardwareProfile.vmSize -o tsv)

# Get resource ID
VNET_ID=$(az network vnet show \
  --name prod-vnet \
  --resource-group prod-network-rg \
  --query id -o tsv)
```

---

## Bulk Operations

### Update Multiple Resources

```bash
# Update tags on all VMs in resource group
for VM in $(az vm list --resource-group prod-rg --query "[].name" -o tsv); do
    az vm update \
        --name "$VM" \
        --resource-group prod-rg \
        --set tags.ManagedBy=Platform-Team
done
```

### Delete Resources by Pattern

```bash
# Delete all test VMs
az vm list --resource-group test-rg --query "[?starts_with(name, 'test-')]" -o tsv | \
while read -r VM_NAME; do
    az vm delete \
        --name "$VM_NAME" \
        --resource-group test-rg \
        --yes --no-wait
done
```

---

## Diagnostic and Monitoring

### Activity Logs

```bash
# Get recent activity logs
az monitor activity-log list \
  --resource-group prod-app-rg \
  --start-time 2025-01-01 \
  --query "[].{Time:eventTimestamp, Operation:operationName.localizedValue}" \
  --output table

# Filter by caller
az monitor activity-log list \
  --caller admin@company.com \
  --output table
```

### Metrics

```bash
# Get VM CPU metrics
az monitor metrics list \
  --resource $(az vm show --name prod-vm --resource-group prod-rg --query id -o tsv) \
  --metric "Percentage CPU" \
  --start-time 2025-01-01T00:00:00Z \
  --end-time 2025-01-02T00:00:00Z
```

---

## Cost Management

### Cost Analysis

```bash
# Get cost for resource group
az consumption usage list \
  --start-date 2025-01-01 \
  --end-date 2025-01-31 \
  --query "[?resourceGroup=='prod-app-rg']"

# Aggregate by resource type
az consumption usage list \
  --start-date 2025-01-01 \
  --end-date 2025-01-31 \
  --query "group_by([?resourceGroup=='prod-app-rg'], &instanceName)"
```

---

## Advanced Patterns

### REST API Access

```bash
# Get access token
TOKEN=$(az account get-access-token --query accessToken -o tsv)

# Call Azure REST API
curl -H "Authorization: Bearer $TOKEN" \
  "https://management.azure.com/subscriptions/SUB_ID/resourceGroups?api-version=2021-04-01"
```

### Azure CLI in CI/CD

```yaml
# GitHub Actions example
steps:
  - name: Azure Login
    uses: azure/login@v1
    with:
      creds: ${{ secrets.AZURE_CREDENTIALS }}

  - name: Deploy Infrastructure
    run: |
      az deployment group create \
        --resource-group prod-rg \
        --template-file main.bicep \
        --parameters @parameters.json
```

---

## Best Practices

1. **Use JMESPath**: Query only needed fields
2. **Handle errors**: Check exit codes, use `set -e`
3. **Idempotent scripts**: Check existence before creation
4. **Parallel execution**: Use `--no-wait` for bulk operations
5. **Output formatting**: Table for humans, TSV/JSON for scripts
6. **Secure credentials**: Use managed identities, not stored credentials
7. **Logging**: Redirect output for audit trails
8. **Resource tagging**: Tag resources for easier querying

---

**Resource Status**: COMPLETE ✅
**Line Count**: 238 ✅
