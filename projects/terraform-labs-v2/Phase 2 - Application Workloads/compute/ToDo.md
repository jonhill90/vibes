# Application - Compute Domain

## 🎯 Purpose
Virtual machine infrastructure, container platforms, and custom image management for traditional and modern workload hosting with automated deployment and management.

## 🏗️ Based on Sandbox Patterns
From your `azure/compute/` and image bakery - you've proven this works with:
- **Custom VM images**: Windows Server 2022/2025 with PowerShell DSC
- **Image bakery**: Packer-based automated image building
- **VM workloads**: Domain controllers, jumpboxes, application servers
- **Container integration**: Preparation for modern workloads

## 📋 Domain Components

### Virtual Machine Workloads (`vm-workloads/`)
- [ ] Windows Server virtual machines
- [ ] Linux virtual machines
- [ ] Domain controllers and AD infrastructure
- [ ] Jumpbox/bastion hosts for management
- [ ] Application servers and web servers
- [ ] Database servers (non-PaaS scenarios)

### Container Platform (`containers/`)
- [ ] Azure Kubernetes Service (AKS) evaluation
- [ ] Azure Container Instances (ACI) for simple workloads
- [ ] Container registry integration
- [ ] Helm charts and application deployment
- [ ] Pod security and network policies
- [ ] Monitoring and logging for containers

### Image Management (`image-bakery/`)
- [ ] **Windows Server 2022**: Base and Core images
- [ ] **Windows Server 2025**: Base and Core images (future)
- [ ] **Custom application images**: Pre-configured with applications
- [ ] **Security hardening**: CIS benchmarks and security baselines
- [ ] **Automated building**: Packer with Azure DevOps pipelines
- [ ] **Versioning and lifecycle**: Image management and retirement

## 🚀 Evolution to AVM
- [ ] Evaluate `avm/res/compute/virtual-machine` module
- [ ] Implement `avm/res/container-service/managed-cluster` for AKS
- [ ] Use `avm/res/compute/gallery` for image management
- [ ] Standardize VM configurations with AVM

## 🏗️ Infrastructure Patterns
- [ ] **Availability sets and zones**: High availability design
- [ ] **Load balancers**: Traffic distribution and redundancy
- [ ] **Auto-scaling**: VM Scale Sets for dynamic workloads
- [ ] **Backup and recovery**: Azure Backup integration
- [ ] **Monitoring**: VM insights and performance monitoring
- [ ] **Update management**: Automated patching and maintenance

## 🔐 Security and Compliance
- [ ] **Just-in-time access**: Azure Security Center JIT
- [ ] **Disk encryption**: Azure Disk Encryption
- [ ] **Network security**: NSGs and application security groups
- [ ] **Antimalware**: Microsoft Antimalware extension
- [ ] **Configuration management**: PowerShell DSC and Azure Policy
- [ ] **Vulnerability management**: Qualys/Rapid7 integration

## 🐳 Modern Workload Patterns
- [ ] **Microservices architecture**: Container-based applications
- [ ] **Serverless functions**: Azure Functions integration
- [ ] **API management**: Integration with API Management domain
- [ ] **Event-driven architecture**: Service Bus and Event Grid
- [ ] **DevOps integration**: Container CI/CD pipelines

## 🎯 Image Bakery Automation
- [ ] **Packer templates**: Infrastructure as code for images
- [ ] **PowerShell DSC**: Configuration management automation
- [ ] **Security scanning**: Image vulnerability assessment
- [ ] **Testing automation**: Image validation and compliance
- [ ] **Distribution**: Multi-region image replication
- [ ] **Lifecycle management**: Automated image cleanup

## 🔗 Integration Points
- **Platform Connectivity**: VM networking and NSGs
- **Platform Identity**: VM managed identities and domain join
- **Platform Management**: VM monitoring and backup
- **DevOps Platform**: Image building and deployment pipelines

## 🎯 Success Criteria
- [ ] Automated VM deployment with custom images
- [ ] Container platform ready for modern workloads
- [ ] Security hardened and compliant infrastructure
- [ ] Monitoring and backup operational
- [ ] CI/CD integration for all compute resources

## 🏢 Enterprise Showcase Value
- **Cost optimization**: Auto-scaling and right-sizing
- **Security baseline**: Hardened images and configurations
- **Operational excellence**: Automated patching and monitoring
- **Modern platform**: Hybrid VM and container capabilities

## 📝 Notes
Compute domain demonstrates **infrastructure modernization** - showing evolution from traditional VMs to modern container platforms.
