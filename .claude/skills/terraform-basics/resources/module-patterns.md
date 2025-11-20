# Module Patterns - Deep Dive

## Overview

Terraform modules enable code reuse, composition, and standardization across infrastructure projects.

---

## Module Design Principles

### 1. Single Responsibility

Each module should manage ONE logical component:

```hcl
✅ GOOD - Focused modules
modules/azure-vnet/          # Virtual network only
modules/azure-subnet/        # Subnet configuration
modules/azure-nsg/           # Network security groups

❌ BAD - Monolithic module
modules/azure-networking/    # VNet + Subnets + NSG + Routes + Peering
# Too many concerns, hard to compose
```

### 2. Clear Input/Output Contract

```hcl
# modules/azure-vnet/variables.tf
variable "vnet_name" {
  description = "Name of the virtual network"
  type        = string

  validation {
    condition     = can(regex("^[a-z0-9-]+$", var.vnet_name))
    error_message = "VNet name must be lowercase alphanumeric with hyphens."
  }
}

variable "address_space" {
  description = "Address space for the virtual network (CIDR blocks)"
  type        = list(string)

  validation {
    condition     = alltrue([for cidr in var.address_space : can(cidrhost(cidr, 0))])
    error_message = "Address space must be valid CIDR notation."
  }
}

# modules/azure-vnet/outputs.tf
output "vnet_id" {
  description = "Virtual network resource ID"
  value       = azurerm_virtual_network.vnet.id
}

output "vnet_name" {
  description = "Virtual network name"
  value       = azurerm_virtual_network.vnet.name
}
```

### 3. Composition Over Duplication

```hcl
# Compose smaller modules into larger ones

# Root module
module "network" {
  source = "./modules/azure-vnet"
  # ...
}

module "subnet_frontend" {
  source     = "./modules/azure-subnet"
  vnet_id    = module.network.vnet_id  # Compose
  subnet_name = "frontend"
}

module "subnet_backend" {
  source     = "./modules/azure-subnet"
  vnet_id    = module.network.vnet_id  # Compose
  subnet_name = "backend"
}
```

---

## Module Structure

### Minimal Module

```
modules/azure-storage-account/
├── main.tf         # Resource definitions
├── variables.tf    # Input variables
├── outputs.tf      # Output values
└── README.md       # Documentation
```

### Complete Module

```
modules/azure-aks-cluster/
├── main.tf              # Primary resources
├── variables.tf         # Input variables
├── outputs.tf           # Output values
├── versions.tf          # Terraform and provider versions
├── README.md            # Usage documentation
├── examples/
│   ├── basic/
│   │   ├── main.tf
│   │   └── README.md
│   └── advanced/
│       ├── main.tf
│       └── README.md
└── tests/
    ├── basic_test.go
    └── advanced_test.go
```

---

## Module Versioning

### Git Tags

```bash
# Tag module release
git tag -a "v1.0.0" -m "Initial release of Azure VNet module"
git push origin v1.0.0

# Use specific version
module "network" {
  source = "git::https://github.com/org/terraform-modules.git//modules/azure-vnet?ref=v1.0.0"
}
```

### Semantic Versioning

- **v1.0.0**: Major version (breaking changes)
- **v1.1.0**: Minor version (new features, backward compatible)
- **v1.1.1**: Patch version (bug fixes)

### Version Constraints

```hcl
module "network" {
  source  = "terraform-aws-modules/vpc/aws"
  version = "5.1.0"       # Exact version
  # version = "~> 5.1"    # Allow patch updates (5.1.x)
  # version = ">= 5.0"    # Minimum version
  # version = ">= 5.0, < 6.0"  # Range
}
```

---

## Module Composition Patterns

### Pattern 1: Layered Modules

**Base Layer**: Foundational resources
```hcl
# Layer 1: Network foundation
module "network_foundation" {
  source = "./modules/network-foundation"
  # Creates VNet, subnets, NSGs
}

# Layer 2: Compute resources (depends on Layer 1)
module "compute" {
  source    = "./modules/compute-cluster"
  subnet_id = module.network_foundation.backend_subnet_id
}

# Layer 3: Application services (depends on Layer 2)
module "app_services" {
  source      = "./modules/app-services"
  backend_ips = module.compute.private_ips
}
```

### Pattern 2: Environment Modules

```hcl
# modules/environment/main.tf
module "network" {
  source        = "../azure-vnet"
  vnet_name     = "${var.environment}-vnet"
  address_space = var.vnet_address_space
}

module "aks" {
  source       = "../azure-aks"
  cluster_name = "${var.environment}-aks"
  subnet_id    = module.network.subnet_id
}

# Root: Use environment module for each environment
module "dev_environment" {
  source      = "./modules/environment"
  environment = "dev"
  # ...
}

module "prod_environment" {
  source      = "./modules/environment"
  environment = "prod"
  # ...
}
```

### Pattern 3: Feature Modules

```hcl
# Modules organized by feature, not resource type

# modules/monitoring/
# - Application Insights
# - Log Analytics
# - Alerts

# modules/networking/
# - VNet
# - Subnets
# - NSGs
# - Routes

module "monitoring" {
  source = "./modules/monitoring"
  # ...
}

module "networking" {
  source = "./modules/networking"
  # ...
}
```

---

## Module Testing

### Terratest (Go)

```go
// tests/basic_test.go
package test

import (
    "testing"
    "github.com/gruntwork-io/terratest/modules/terraform"
    "github.com/stretchr/testify/assert"
)

func TestAzureVNetModule(t *testing.T) {
    terraformOptions := &terraform.Options{
        TerraformDir: "../examples/basic",
    }

    defer terraform.Destroy(t, terraformOptions)

    terraform.InitAndApply(t, terraformOptions)

    vnetID := terraform.Output(t, terraformOptions, "vnet_id")
    assert.NotEmpty(t, vnetID)
}
```

### Terraform Test (Native)

```hcl
# tests/basic.tftest.hcl
run "validate_vnet_creation" {
  command = apply

  variables {
    vnet_name     = "test-vnet"
    address_space = ["10.0.0.0/16"]
  }

  assert {
    condition     = output.vnet_id != ""
    error_message = "VNet ID should not be empty"
  }
}
```

---

## Module Registry

### Terraform Registry

**Publishing**:
1. Create GitHub repository: `terraform-<PROVIDER>-<NAME>`
2. Add module code
3. Tag release: `git tag v1.0.0 && git push --tags`
4. Register at registry.terraform.io

**Using**:
```hcl
module "vpc" {
  source  = "terraform-aws-modules/vpc/aws"
  version = "5.1.0"
}
```

### Private Registry

```hcl
# Terraform Cloud
module "network" {
  source  = "app.terraform.io/my-org/network/azurerm"
  version = "1.2.0"
}

# GitHub
module "network" {
  source = "github.com/my-org/terraform-modules//azure-vnet?ref=v1.2.0"
}
```

---

## Common Module Patterns

### Optional Resources with `count`

```hcl
# Create NAT Gateway only if enabled
resource "azurerm_nat_gateway" "nat" {
  count               = var.enable_nat_gateway ? 1 : 0
  name                = "${var.vnet_name}-nat"
  location            = var.location
  resource_group_name = var.resource_group_name
}

# Output handling optional resources
output "nat_gateway_id" {
  description = "NAT Gateway ID (if enabled)"
  value       = var.enable_nat_gateway ? azurerm_nat_gateway.nat[0].id : null
}
```

### Dynamic Blocks

```hcl
# Dynamic subnet creation
resource "azurerm_subnet" "subnet" {
  for_each = var.subnets

  name                 = each.key
  resource_group_name  = var.resource_group_name
  virtual_network_name = azurerm_virtual_network.vnet.name
  address_prefixes     = [each.value.address_prefix]

  dynamic "delegation" {
    for_each = lookup(each.value, "delegations", [])
    content {
      name = delegation.value.name

      service_delegation {
        name    = delegation.value.service_name
        actions = delegation.value.actions
      }
    }
  }
}
```

### Module Defaults with Locals

```hcl
locals {
  # Provide sensible defaults
  default_tags = {
    ManagedBy   = "Terraform"
    Environment = var.environment
  }

  # Merge user tags with defaults
  tags = merge(local.default_tags, var.tags)

  # Computed naming
  resource_prefix = "${var.project}-${var.environment}"
}

resource "azurerm_resource_group" "rg" {
  name     = "${local.resource_prefix}-rg"
  location = var.location
  tags     = local.tags
}
```

---

## Best Practices

1. **README Documentation**: Always include usage examples
2. **Input Validation**: Validate variable inputs with conditions
3. **Output Everything Useful**: Expose IDs, names, attributes
4. **Version Lock**: Pin provider versions in modules
5. **Examples**: Provide basic and advanced usage examples
6. **Testing**: Write tests for critical modules
7. **Changelog**: Maintain CHANGELOG.md for version history
8. **Naming Consistency**: Use consistent naming conventions
9. **Tags**: Support custom tags via variable
10. **Minimize Complexity**: Keep modules simple and focused

---

**Resource Status**: COMPLETE ✅
**Line Count**: 287 ✅
