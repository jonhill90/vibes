# Platform - Identity Domain

## 🎯 Purpose
Centralized identity, access management, and security infrastructure across the Azure landing zone with Azure AD, Key Vaults, and RBAC automation.

## 🏗️ Based on Sandbox Patterns
From your `azure/identity/main.tf` - you've proven this works with:
- Cross-subscription RBAC with service principals
- Key Vault per domain with network ACLs
- Managed identities for service-to-service auth
- Azure DevOps service connection automation

## 📋 Domain Components

### Azure AD Management (`entra-id/`)
- [ ] Service principal automation for each domain
- [ ] Security groups for role-based access
- [ ] Application registrations for apps
- [ ] Conditional access policies
- [ ] Identity protection settings

### Key Vault Infrastructure (`key-vaults/`)
- [ ] Domain-specific Key Vaults:
  - `connectivity-vault` (networking secrets)
  - `management-vault` (DevOps, monitoring)
  - `identity-vault` (security secrets)
  - `platform-vault` (shared platform secrets)
  - `application-vault` (app-specific secrets)
- [ ] Network ACLs restricting to specific subnets
- [ ] Private endpoints for secure access
- [ ] RBAC integration with Azure AD groups

### RBAC Automation (`rbac/`)
- [ ] Cross-subscription role assignments
- [ ] Service principal permissions per domain
- [ ] Managed identity role assignments
- [ ] Custom role definitions where needed
- [ ] Access reviews and lifecycle management

## 🚀 Evolution to AVM
- [ ] Evaluate `avm/res/key-vault/vault` module
- [ ] Implement `avm/res/authorization/role-assignment` patterns
- [ ] Standardize managed identity creation
- [ ] Automate service principal lifecycle

## 🔐 Security Enhancements
- [ ] Key rotation automation
- [ ] Certificate lifecycle management
- [ ] Privileged Identity Management (PIM)
- [ ] Zero-trust authentication patterns
- [ ] Security baseline enforcement

## 🔗 Integration Points
- **DevOps Domain**: Service connections and secrets
- **Connectivity Domain**: Network ACLs and private endpoints
- **All Domains**: RBAC and managed identities

## 🎯 Success Criteria
- [ ] Zero service principal secrets stored in code
- [ ] All secrets managed through Key Vault
- [ ] Least-privilege access implemented
- [ ] Cross-subscription RBAC working
- [ ] Automated identity lifecycle management

## 📝 Notes
Identity is deployed **second** after connectivity - provides security foundation for all other domains.
