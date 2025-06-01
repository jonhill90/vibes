# Platform - Connectivity Domain

## 🎯 Purpose
Foundation networking infrastructure implementing hub-spoke architecture across multiple Azure subscriptions with private DNS and secure connectivity patterns.

## 🏗️ Based on Sandbox Patterns
From your `azure/network/main.tf` - you've proven this works with:
- Multi-subscription hub-spoke with proper peering
- Private DNS zones for all Azure services
- Cross-subscription RBAC and service connections
- Network ACLs and private endpoints

## 📋 Domain Components

### Hub Infrastructure (`hub/`)
- [ ] Central hub VNet in connectivity subscription
- [ ] Gateway subnet for VPN/ExpressRoute (future)
- [ ] Azure Firewall subnet (optional)
- [ ] Bastion subnet for secure admin access
- [ ] Network Watcher for monitoring

### Spoke Networks (`spokes/`)
- [ ] Management spoke (DevOps, monitoring, governance)
- [ ] Identity spoke (domain controllers, AD services)
- [ ] Platform spoke (shared services, data platform)
- [ ] Application spoke (workloads, apps)

### DNS Infrastructure (`dns/`)
- [ ] Private DNS zones for Azure services:
  - `privatelink.blob.core.windows.net`
  - `privatelink.vaultcore.azure.net`
  - `privatelink.adf.azure.com`
  - `privatelink.dev.azuresynapse.net`
  - `privatelink.sql.azuresynapse.net`
  - `privatelink.documents.azure.com`
  - `privatelink.azuredatabricks.net`
  - `privatelink.azureai.net`
- [ ] Internal domain DNS zone
- [ ] DNS zone links to appropriate VNets

### VNet Peering (`peering/`)
- [ ] Hub-to-spoke peering for all spokes
- [ ] Spoke-to-spoke peering where needed
- [ ] Cross-subscription peering with proper RBAC
- [ ] Route table management

## 🚀 Evolution to AVM
- [ ] Evaluate `avm/ptn/network/hub-spoke` pattern module
- [ ] Migrate from custom VNet resources to AVM modules
- [ ] Implement standardized subnet configurations
- [ ] Add network security group automation

## 🔐 Security Enhancements
- [ ] Network security groups with application rules
- [ ] Azure Firewall or NVA integration
- [ ] DDoS protection standard
- [ ] Network flow logs and analytics

## 🎯 Success Criteria
- [ ] Multi-subscription connectivity working
- [ ] Private DNS resolution for all services
- [ ] Secure network segmentation
- [ ] Monitoring and alerting in place
- [ ] Ready for workload deployment

## 📝 Notes
This domain is the **foundation** - all other domains depend on connectivity being deployed first.
