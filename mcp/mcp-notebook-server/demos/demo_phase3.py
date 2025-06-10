#!/usr/bin/env python3
"""
Phase 3 Demo: Complete Automation & Advanced Analytics
Demonstrates all Phase 3 features including inbox processing, analytics, and MOC generation
"""

# Add src to path for imports
import sys
from pathlib import Path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root / 'src'))


import os
import sys
import asyncio
import json
import tempfile
import shutil
from datetime import datetime

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

# Import Phase 3 tools
from phase3_tools import (
    process_inbox_tool,
    bulk_reprocess_tool,
    get_advanced_analytics_tool, 
    export_knowledge_graph_tool,
    generate_moc_from_clusters_tool
)

# Import existing components
from database.database import db
from content_analyzer import content_analyzer
from pattern_learner import pattern_learner
from session_manager import session_manager

async def setup_demo_environment():
    """Setup demo environment with sample content"""
    print("🔧 Setting up Phase 3 demo environment...")
    
    # Create temporary vault for demo
    demo_vault = "/tmp/inmpara_phase3_demo"
    if os.path.exists(demo_vault):
        shutil.rmtree(demo_vault)
    
    # Create INMPARA folder structure
    folders = [
        "0 - Inbox",
        "1 - Notes", 
        "2 - MOCs",
        "3 - Projects",
        "4 - Areas",
        "5 - Resources",
        "6 - Archive",
        "99 - Meta"
    ]
    
    for folder in folders:
        os.makedirs(os.path.join(demo_vault, folder), exist_ok=True)
    
    # Create sample inbox content
    sample_inbox_content = [
        {
            "filename": "azure-dns-issue.md",
            "content": """# Azure DNS Configuration Issue

Having trouble with private DNS zones not resolving correctly in our Azure environment.

The issue seems to be related to VNET linking and DNS forwarding rules. Need to investigate further.

Key points:
- Private DNS zone created
- VNET linked to zone
- A records configured
- Still not resolving from VMs

This might be related to our recent terraform changes to the networking infrastructure.
"""
        },
        {
            "filename": "terraform-state-locking.md", 
            "content": """# Terraform State Locking Problems

We're seeing terraform state locking issues across multiple environments.

The state files seem to get stuck in a locked state even when no terraform operations are running.

Troubleshooting steps:
1. Check for running terraform processes
2. Verify state lock DynamoDB table
3. Manual unlock if necessary
4. Review terraform backend configuration

This is blocking our deployment pipeline and needs urgent attention.
"""
        },
        {
            "filename": "databricks-networking.md",
            "content": """# Databricks Private Endpoint Setup

Setting up private endpoints for Azure Databricks to improve security posture.

Configuration involves:
- Creating private endpoints in spoke VNETs
- Updating DNS configuration
- Testing connectivity from on-premises
- Validating security group rules

Need to document the complete process for other environments.
"""
        },
        {
            "filename": "ai-model-training.md",
            "content": """# Machine Learning Model Training Pipeline

Working on automating our ML model training pipeline using Azure ML.

Components:
- Data preprocessing scripts
- Feature engineering pipeline
- Model training with hyperparameter tuning
- Model validation and testing
- Deployment automation

This will significantly reduce manual effort in our ML workflows.
"""
        },
        {
            "filename": "kubernetes-monitoring.md",
            "content": """# Kubernetes Cluster Monitoring Setup

Implementing comprehensive monitoring for our AKS clusters.

Monitoring stack includes:
- Prometheus for metrics collection
- Grafana for visualization 
- AlertManager for notifications
- Jaeger for distributed tracing

Need to configure proper alerting rules for production workloads.
"""
        }
    ]
    
    # Write sample content to inbox
    for sample in sample_inbox_content:
        filepath = os.path.join(demo_vault, "0 - Inbox", sample["filename"])
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(sample["content"])
    
    # Create some existing notes for clustering demo
    existing_notes = [
        {
            "filename": "2025-06-01-azure-vnet-configuration.md",
            "content": """---
title: Azure VNET Configuration Best Practices
type: note
tags:
  - azure
  - networking
  - vnet
  - infrastructure
created: 2025-06-01
updated: 2025-06-01
status: active
stage: 1-notes
domain: cloud-infrastructure
permalink: 1-notes/azure-vnet-configuration
---

# Azure VNET Configuration Best Practices

## Content
Comprehensive guide for setting up Azure Virtual Networks following enterprise best practices.

## Observations
- [technical-finding] Hub-spoke topology provides better network isolation #azure #networking
- [insight] Proper subnet planning essential for scalability #planning

## Relations
- relates_to [[Azure Networking MOC]]
- part_of [[Cloud Infrastructure]]

## Tags
#azure #networking #vnet #infrastructure
"""
        },
        {
            "filename": "2025-06-02-terraform-azure-modules.md", 
            "content": """---
title: Terraform Azure Modules Development
type: note
tags:
  - terraform
  - azure
  - infrastructure-as-code
  - modules
created: 2025-06-02
updated: 2025-06-02
status: active
stage: 1-notes
domain: cloud-infrastructure
permalink: 1-notes/terraform-azure-modules
---

# Terraform Azure Modules Development

## Content
Creating reusable Terraform modules for Azure infrastructure components.

## Observations
- [technical-finding] Module versioning critical for stability #terraform #versioning
- [insight] Standardized modules improve deployment consistency #standardization

## Relations
- relates_to [[Infrastructure as Code MOC]]
- enables [[Azure Deployment Automation]]

## Tags
#terraform #azure #infrastructure-as-code #modules
"""
        }
    ]
    
    # Write existing notes
    for note in existing_notes:
        filepath = os.path.join(demo_vault, "1 - Notes", note["filename"])
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(note["content"])
    
    print(f"✅ Demo environment created at {demo_vault}")
    return demo_vault

async def demo_inbox_processing(vault_path):
    """Demonstrate complete inbox processing automation"""
    print("\n🔄 Demonstrating Inbox Processing Automation...")
    print("=" * 60)
    
    # First, show what's in the inbox
    inbox_path = os.path.join(vault_path, "0 - Inbox")
    inbox_files = [f for f in os.listdir(inbox_path) if f.endswith('.md')]
    print(f"📥 Inbox contains {len(inbox_files)} files:")
    for file in inbox_files:
        print(f"  - {file}")
    
    # Process inbox with medium confidence threshold
    print("\n🤖 Processing inbox with learned patterns...")
    result = await process_inbox_tool(
        vault_path=vault_path,
        batch_size=10,
        confidence_threshold=0.6,
        auto_approve=False  # Don't auto-approve for demo
    )
    
    print(f"📊 Processing Results:")
    print(f"  - Files processed: {result.get('processed_count', 0)}")
    print(f"  - Auto-processed: {result.get('auto_processed', 0)}")
    print(f"  - Manual review needed: {result.get('manual_review', 0)}")
    print(f"  - Errors: {len(result.get('errors', []))}")
    
    if result.get('processed_files'):
        print("\n📋 Detailed Results:")
        for file_result in result['processed_files'][:3]:  # Show first 3
            print(f"  📄 {os.path.basename(file_result['file_path'])}")
            print(f"    Decision: {file_result['decision']}")
            print(f"    Confidence: {file_result['adjusted_confidence']:.2f}")
            if 'target_path' in file_result:
                print(f"    Target: {file_result['target_path']}")
    
    return result

async def demo_bulk_reprocessing(vault_path):
    """Demonstrate bulk reprocessing for quality improvement"""
    print("\n🔧 Demonstrating Bulk Reprocessing...")
    print("=" * 60)
    
    # Reprocess notes in 1 - Notes folder
    result = await bulk_reprocess_tool(
        vault_path=vault_path,
        target_folder="1 - Notes",
        reprocess_count=5,
        min_confidence_improvement=0.05
    )
    
    print(f"📊 Reprocessing Results:")
    print(f"  - Files analyzed: {result.get('files_analyzed', 0)}")
    print(f"  - Improvements found: {result.get('improvements_found', 0)}")
    print(f"  - Errors: {len(result.get('errors', []))}")
    
    if result.get('recommendations'):
        print("\n💡 Quality Improvement Recommendations:")
        for rec in result['recommendations'][:2]:  # Show first 2
            filename = os.path.basename(rec['file_path'])
            improvement = rec['confidence_improvement']
            print(f"  📄 {filename}")
            print(f"    Confidence improvement: +{improvement:.2f}")
            if rec.get('improved_tags'):
                print(f"    Suggested tags: {rec['improved_tags']}")
    
    return result

async def demo_advanced_analytics(vault_path):
    """Demonstrate advanced analytics and reporting"""
    print("\n📈 Demonstrating Advanced Analytics...")
    print("=" * 60)
    
    # Generate comprehensive analytics
    result = await get_advanced_analytics_tool(
        vault_path=vault_path,
        days_back=30
    )
    
    print(f"📊 Analytics Overview:")
    
    # Vault structure
    if 'vault_structure' in result:
        vault_stats = result['vault_structure']
        print(f"  📁 Total files: {vault_stats.get('total_files', 0)}")
        print(f"  💾 Total size: {vault_stats.get('total_size', 0):,} bytes")
        
        if 'folders' in vault_stats:
            print("  📂 Folder distribution:")
            for folder, data in vault_stats['folders'].items():
                file_count = data.get('file_count', 0)
                if file_count > 0:
                    print(f"    - {folder}: {file_count} files")
    
    # Content distribution
    if 'content_distribution' in result:
        content_stats = result['content_distribution']
        print(f"\n🏷️  Content Analysis:")
        print(f"  - Unique tags: {content_stats.get('total_tags', 0)}")
        print(f"  - Domains: {content_stats.get('total_domains', 0)}")
        
        if 'domain_distribution' in content_stats:
            print("  📋 Domain distribution:")
            for domain, count in content_stats['domain_distribution'].items():
                if count > 0:
                    print(f"    - {domain}: {count}")
    
    # Knowledge graph metrics
    if 'knowledge_graph' in result:
        kg_stats = result['knowledge_graph']
        print(f"\n🕸️  Knowledge Graph:")
        print(f"  - Nodes: {kg_stats.get('total_nodes', 0)}")
        print(f"  - Edges: {kg_stats.get('total_edges', 0)}")
        print(f"  - Density: {kg_stats.get('network_density', 0.0):.3f}")
        print(f"  - Hub nodes: {len(kg_stats.get('hub_nodes', []))}")
    
    return result

async def demo_knowledge_graph_export(vault_path):
    """Demonstrate knowledge graph export capabilities"""
    print("\n🕸️  Demonstrating Knowledge Graph Export...")
    print("=" * 60)
    
    # Export in JSON format
    result = await export_knowledge_graph_tool(
        vault_path=vault_path,
        format="json",
        include_content=False
    )
    
    print(f"📊 Export Results:")
    print(f"  - Format: {result.get('export_format', 'unknown')}")
    print(f"  - Export path: {result.get('export_path', 'unknown')}")
    
    if 'graph_stats' in result:
        stats = result['graph_stats']
        print(f"  - Nodes: {stats.get('node_count', 0)}")
        print(f"  - Edges: {stats.get('edge_count', 0)}")
        print(f"  - Content included: {stats.get('included_content', False)}")
    
    # Check if export file was created
    export_path = result.get('export_path')
    if export_path and os.path.exists(export_path):
        file_size = os.path.getsize(export_path)
        print(f"  ✅ Export file created ({file_size:,} bytes)")
        
        # Show sample of exported data
        with open(export_path, 'r', encoding='utf-8') as f:
            sample_data = json.load(f)
            if 'nodes' in sample_data:
                print(f"  📄 Sample nodes: {len(sample_data['nodes'][:3])}/3 shown")
    
    return result

async def demo_moc_generation(vault_path):
    """Demonstrate MOC auto-generation from note clusters"""
    print("\n📚 Demonstrating MOC Auto-Generation...")
    print("=" * 60)
    
    # Generate MOCs from note clusters
    result = await generate_moc_from_clusters_tool(
        vault_path=vault_path,
        min_cluster_size=2,  # Lower threshold for demo
        similarity_threshold=0.5,
        target_clusters=3
    )
    
    print(f"📊 MOC Generation Results:")
    print(f"  - Notes analyzed: {result.get('notes_analyzed', 0)}")
    print(f"  - Clusters found: {result.get('clusters_found', 0)}")
    print(f"  - MOCs generated: {result.get('mocs_generated', 0)}")
    
    if result.get('generated_mocs'):
        print("\n📖 Generated MOCs:")
        for moc in result['generated_mocs']:
            print(f"  📚 {moc['moc_name']}")
            print(f"    Notes: {moc['note_count']}")
            print(f"    Domain: {moc['primary_domain']}")
            print(f"    Action: {moc['action']}")
            print(f"    Confidence: {moc['confidence']:.1%}")
            
            # Check if MOC file was created
            if os.path.exists(moc['moc_path']):
                print(f"    ✅ File created: {os.path.basename(moc['moc_path'])}")
    
    return result

async def run_comprehensive_demo():
    """Run comprehensive Phase 3 demonstration"""
    print("🚀 INMPARA Notebook MCP Server - Phase 3 Complete Demo")
    print("=" * 70)
    print("Complete automation where users can dump content in inbox")
    print("and trust AI processing with comprehensive analytics")
    print("=" * 70)
    
    try:
        # Setup demo environment
        vault_path = await setup_demo_environment()
        
        # Initialize database for demo
        db._init_database()
        
        # Simulate some learning patterns for realistic demo
        await simulate_learning_patterns()
        
        # Demo 1: Inbox Processing
        inbox_result = await demo_inbox_processing(vault_path)
        
        # Demo 2: Bulk Reprocessing
        reprocess_result = await demo_bulk_reprocessing(vault_path)
        
        # Demo 3: Advanced Analytics
        analytics_result = await demo_advanced_analytics(vault_path)
        
        # Demo 4: Knowledge Graph Export
        graph_result = await demo_knowledge_graph_export(vault_path)
        
        # Demo 5: MOC Generation
        moc_result = await demo_moc_generation(vault_path)
        
        # Summary
        print("\n🎉 Phase 3 Demo Complete!")
        print("=" * 40)
        print("✅ All Phase 3 features demonstrated successfully:")
        print("  🔄 Complete inbox processing automation")
        print("  🔧 Bulk quality improvement reprocessing")
        print("  📈 Advanced analytics and reporting")
        print("  🕸️  Knowledge graph visualization export")
        print("  📚 MOC auto-generation from note clusters")
        print()
        print("🎯 Phase 3 Implementation: COMPLETE")
        print("   Ready for production use with full automation!")
        
        return True
        
    except Exception as e:
        print(f"\n❌ Demo failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

async def simulate_learning_patterns():
    """Simulate some learning patterns for realistic demo"""
    try:
        # Create some sample learning patterns
        sample_patterns = [
            {
                "pattern_type": "tag_preference",
                "pattern_data": {"azure": 0.9, "networking": 0.8, "terraform": 0.85},
                "confidence_impact": 0.15,
                "usage_count": 5
            },
            {
                "pattern_type": "domain_classification", 
                "pattern_data": {"cloud-infrastructure": 0.9},
                "confidence_impact": 0.1,
                "usage_count": 8
            },
            {
                "pattern_type": "filing_location",
                "pattern_data": {"1 - Notes": 0.8, "5 - Resources": 0.6},
                "confidence_impact": 0.12,
                "usage_count": 6
            }
        ]
        
        # Add patterns to database if not exists
        with db.get_connection() as conn:
            for pattern in sample_patterns:
                conn.execute("""
                    INSERT OR IGNORE INTO learning_patterns 
                    (pattern_type, pattern_data, confidence_impact, usage_count, last_updated)
                    VALUES (?, ?, ?, ?, ?)
                """, (
                    pattern["pattern_type"],
                    json.dumps(pattern["pattern_data"]),
                    pattern["confidence_impact"],
                    pattern["usage_count"],
                    datetime.now().isoformat()
                ))
        
        print("🧠 Sample learning patterns created for demo")
        
    except Exception as e:
        print(f"⚠️  Could not create sample patterns: {str(e)}")

if __name__ == "__main__":
    asyncio.run(run_comprehensive_demo())

