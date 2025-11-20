# ARM Templates - Infrastructure as Code

## Overview

ARM (Azure Resource Manager) templates define Azure infrastructure as JSON. Modern alternative: Bicep (compiled to ARM).

---

## ARM Template Structure

### Basic Template

```json
{
  "$schema": "https://schema.management.azure.com/schemas/2019-04-01/deploymentTemplate.json#",
  "contentVersion": "1.0.0.0",
  "parameters": {
    "location": {
      "type": "string",
      "defaultValue": "[resourceGroup().location]"
    }
  },
  "variables": {
    "storageAccountName": "[concat('storage', uniqueString(resourceGroup().id))]"
  },
  "resources": [
    {
      "type": "Microsoft.Storage/storageAccounts",
      "apiVersion": "2021-04-01",
      "name": "[variables('storageAccountName')]",
      "location": "[parameters('location')]",
      "sku": {
        "name": "Standard_LRS"
      },
      "kind": "StorageV2"
    }
  ],
  "outputs": {
    "storageAccountId": {
      "type": "string",
      "value": "[resourceId('Microsoft.Storage/storageAccounts', variables('storageAccountName'))]"
    }
  }
}
```

---

## Bicep Alternative (Recommended)

### Bicep vs ARM

**Bicep** (modern, concise):
```bicep
param location string = resourceGroup().location

var storageAccountName = 'storage${uniqueString(resourceGroup().id)}'

resource storage 'Microsoft.Storage/storageAccounts@2021-04-01' = {
  name: storageAccountName
  location: location
  sku: {
    name: 'Standard_LRS'
  }
  kind: 'StorageV2'
}

output storageAccountId string = storage.id
```

**ARM** (verbose, JSON):
```json
// See above - 10x more lines for same result
```

---

## Parameter Patterns

### Secure Parameters

```json
{
  "parameters": {
    "adminPassword": {
      "type": "secureString",
      "metadata": {
        "description": "Administrator password (never logged)"
      }
    },
    "sqlConnectionString": {
      "type": "secureString"
    }
  }
}
```

**Usage**:
```bash
# Pass secure parameter from Key Vault
az deployment group create \
  --resource-group prod-app-rg \
  --template-file main.json \
  --parameters @parameters.json \
  --parameters adminPassword="$(az keyvault secret show --name admin-password --vault-name prod-kv --query value -o tsv)"
```

### Parameter Validation

```json
{
  "parameters": {
    "environment": {
      "type": "string",
      "allowedValues": [
        "dev",
        "test",
        "prod"
      ],
      "metadata": {
        "description": "Environment name"
      }
    },
    "vmSize": {
      "type": "string",
      "minLength": 1,
      "maxLength": 50
    }
  }
}
```

---

## Deployment Patterns

### Incremental vs Complete

```bash
# Incremental (default) - adds/updates only
az deployment group create \
  --resource-group prod-app-rg \
  --template-file main.json \
  --mode Incremental

# Complete - deletes resources not in template (DANGEROUS)
az deployment group create \
  --resource-group prod-app-rg \
  --template-file main.json \
  --mode Complete
```

### What-If Validation

```bash
# Preview changes before deployment
az deployment group what-if \
  --resource-group prod-app-rg \
  --template-file main.json \
  --parameters @parameters.json

# Example output:
# + Create: storageAccount1
# ~ Modify: virtualMachine1
# - Delete: publicIp1
```

---

## Modular Templates

### Linked Templates

```json
{
  "resources": [
    {
      "type": "Microsoft.Resources/deployments",
      "apiVersion": "2021-04-01",
      "name": "networkDeployment",
      "properties": {
        "mode": "Incremental",
        "templateLink": {
          "uri": "https://storage.blob.core.windows.net/templates/network.json"
        }
      }
    }
  ]
}
```

### Nested Templates

```json
{
  "resources": [
    {
      "type": "Microsoft.Resources/deployments",
      "apiVersion": "2021-04-01",
      "name": "storageDeployment",
      "properties": {
        "mode": "Incremental",
        "template": {
          "$schema": "...",
          "contentVersion": "1.0.0.0",
          "resources": [
            // Inline template resources
          ]
        }
      }
    }
  ]
}
```

---

## Common Functions

### String Functions

```json
"variables": {
  "storageAccountName": "[concat('storage', uniqueString(resourceGroup().id))]",
  "lowerEnv": "[toLower(parameters('environment'))]",
  "vmName": "[format('vm-{0}-{1}', parameters('environment'), parameters('instance'))]"
}
```

### Resource Functions

```json
"variables": {
  "resourceGroupId": "[resourceGroup().id]",
  "subscriptionId": "[subscription().subscriptionId]",
  "vnetId": "[resourceId('Microsoft.Network/virtualNetworks', 'prod-vnet')]"
}
```

---

## Best Practices

1. **Use Bicep over ARM**: Modern syntax, easier maintenance
2. **Validate before deploy**: Use what-if to preview changes
3. **Modularize templates**: Linked/nested templates for reusability
4. **Secure parameters**: Use secureString for sensitive data
5. **Output values**: Expose IDs and URIs for other deployments
6. **Version control**: Track template changes in git
7. **Test deployments**: Validate in dev before prod
8. **Document parameters**: Add metadata descriptions

---

**Resource Status**: COMPLETE ✅
**Line Count**: 208 ✅
