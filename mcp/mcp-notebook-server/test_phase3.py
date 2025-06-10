approve=False
            )
            
            self.assertTrue(result.get('success', False))
            self.assertGreaterEqual(result.get('processed_count', 0), 1)
            self.assertIn('processed_files', result)
        
        asyncio.run(run_test())
    
    def test_inbox_processing_with_confidence_threshold(self):
        """Test inbox processing respects confidence thresholds"""
        async def run_test():
            # Test with high confidence threshold
            result = await process_inbox_tool(
                vault_path=self.test_vault,
                batch_size=5,
                confidence_threshold=0.9,  # Very high threshold
                auto_approve=False
            )
            
            self.assertTrue(result.get('success', False))
            # With high threshold, should mostly be manual review
            manual_review = result.get('manual_review', 0)
            auto_processed = result.get('auto_processed', 0)
            self.assertGreaterEqual(manual_review, auto_processed)
        
        asyncio.run(run_test())

class TestBulkReprocessing(TestPhase3Features):
    """Test bulk reprocessing functionality"""
    
    def test_bulk_reprocess_notes(self):
        """Test bulk reprocessing of existing notes"""
        async def run_test():
            result = await bulk_reprocess_tool(
                vault_path=self.test_vault,
                target_folder="1 - Notes",
                reprocess_count=10,
                min_confidence_improvement=0.01
            )
            
            self.assertTrue(result.get('success', False))
            self.assertGreaterEqual(result.get('reprocessed_count', 0), 1)
            self.assertIn('recommendations', result)
        
        asyncio.run(run_test())
    
    def test_bulk_reprocess_improvement_threshold(self):
        """Test bulk reprocessing respects improvement threshold"""
        async def run_test():
            # Test with very high improvement threshold
            result = await bulk_reprocess_tool(
                vault_path=self.test_vault,
                target_folder="1 - Notes",
                reprocess_count=10,
                min_confidence_improvement=0.5  # Very high threshold
            )
            
            self.assertTrue(result.get('success', False))
            # Should find few or no improvements with high threshold
            improvements = result.get('improvements_found', 0)
            self.assertLessEqual(improvements, result.get('reprocessed_count', 1))
        
        asyncio.run(run_test())

class TestAdvancedAnalytics(TestPhase3Features):
    """Test advanced analytics functionality"""
    
    def test_get_analytics_basic(self):
        """Test basic analytics generation"""
        async def run_test():
            result = await get_advanced_analytics_tool(
                vault_path=self.test_vault,
                days_back=30
            )
            
            self.assertTrue(result.get('success', False))
            self.assertIn('vault_structure', result)
            self.assertIn('content_distribution', result)
            self.assertIn('knowledge_graph', result)
        
        asyncio.run(run_test())
    
    def test_vault_structure_analysis(self):
        """Test vault structure analysis helper"""
        async def run_test():
            result = await _analyze_vault_structure(self.test_vault)
            
            self.assertIn('total_files', result)
            self.assertIn('folders', result)
            self.assertGreater(result.get('total_files', 0), 0)
        
        asyncio.run(run_test())

class TestKnowledgeGraphExport(TestPhase3Features):
    """Test knowledge graph export functionality"""
    
    def test_export_json_format(self):
        """Test JSON knowledge graph export"""
        async def run_test():
            result = await export_knowledge_graph_tool(
                vault_path=self.test_vault,
                format="json",
                include_content=False
            )
            
            self.assertTrue(result.get('success', False))
            self.assertEqual(result.get('export_format'), 'json')
            self.assertIn('export_path', result)
            self.assertIn('graph_stats', result)
            
            # Check if export file was created
            export_path = result.get('export_path')
            if export_path:
                self.assertTrue(os.path.exists(export_path))
        
        asyncio.run(run_test())
    
    def test_export_graphml_format(self):
        """Test GraphML knowledge graph export"""
        async def run_test():
            result = await export_knowledge_graph_tool(
                vault_path=self.test_vault,
                format="graphml",
                include_content=False
            )
            
            self.assertTrue(result.get('success', False))
            self.assertEqual(result.get('export_format'), 'graphml')
        
        asyncio.run(run_test())
    
    def test_knowledge_graph_metrics(self):
        """Test knowledge graph metrics calculation"""
        async def run_test():
            result = await _calculate_knowledge_graph_metrics(self.test_vault)
            
            self.assertIn('total_nodes', result)
            self.assertIn('total_edges', result)
            self.assertIn('network_density', result)
            self.assertGreaterEqual(result.get('total_nodes', 0), 0)
        
        asyncio.run(run_test())

class TestMOCGeneration(TestPhase3Features):
    """Test MOC auto-generation functionality"""
    
    def test_generate_moc_from_clusters(self):
        """Test MOC generation from note clusters"""
        async def run_test():
            # Create additional notes for better clustering
            self.create_additional_test_notes()
            
            result = await generate_moc_from_clusters_tool(
                vault_path=self.test_vault,
                min_cluster_size=2,
                similarity_threshold=0.3,  # Lower threshold for test
                target_clusters=3
            )
            
            self.assertTrue(result.get('success', False))
            self.assertGreaterEqual(result.get('notes_analyzed', 0), 1)
            self.assertIn('generated_mocs', result)
        
        asyncio.run(run_test())
    
    def test_note_clustering(self):
        """Test note clustering functionality"""
        async def run_test():
            # Create sample note features for clustering
            note_features = [
                {
                    "title": "Azure DNS Configuration",
                    "tags": ["azure", "dns", "networking"],
                    "domain": "cloud-infrastructure",
                    "content_preview": "DNS configuration for Azure resources"
                },
                {
                    "title": "Azure VNET Setup", 
                    "tags": ["azure", "networking", "vnet"],
                    "domain": "cloud-infrastructure",
                    "content_preview": "Virtual network configuration"
                }
            ]
            
            clusters = await _cluster_notes_for_moc(
                note_features, 
                min_cluster_size=2,
                similarity_threshold=0.5,
                target_clusters=2
            )
            
            self.assertIsInstance(clusters, list)
            # Should create at least one cluster if notes are similar enough
        
        asyncio.run(run_test())
    
    def create_additional_test_notes(self):
        """Create additional test notes for clustering"""
        notes = [
            {
                "filename": "azure-networking.md",
                "content": """---
title: Azure Networking Overview
type: note
tags:
  - azure
  - networking
  - cloud
created: 2025-06-10
updated: 2025-06-10
status: active
stage: 1-notes
domain: cloud-infrastructure
permalink: 1-notes/azure-networking
---

# Azure Networking Overview

## Content
Comprehensive overview of Azure networking components.

## Observations
- [technical-finding] Hub-spoke topology preferred #azure #networking

## Tags
#azure #networking #cloud
"""
            },
            {
                "filename": "terraform-modules.md",
                "content": """---
title: Terraform Module Development
type: note
tags:
  - terraform
  - modules
  - infrastructure
created: 2025-06-10
updated: 2025-06-10
status: active
stage: 1-notes
domain: cloud-infrastructure
permalink: 1-notes/terraform-modules
---

# Terraform Module Development

## Content
Best practices for developing reusable Terraform modules.

## Observations
- [insight] Versioning critical for module stability #terraform

## Tags
#terraform #modules #infrastructure
"""
            }
        ]
        
        for note in notes:
            note_path = os.path.join(self.test_vault, "1 - Notes", note["filename"])
            with open(note_path, 'w', encoding='utf-8') as f:
                f.write(note["content"])

class TestPhase3Integration(TestPhase3Features):
    """Test Phase 3 integration and comprehensive scenarios"""
    
    def test_end_to_end_workflow(self):
        """Test complete end-to-end Phase 3 workflow"""
        async def run_test():
            # 1. Process inbox
            inbox_result = await process_inbox_tool(
                vault_path=self.test_vault,
                batch_size=5,
                confidence_threshold=0.5,
                auto_approve=False
            )
            self.assertTrue(inbox_result.get('success', False))
            
            # 2. Generate analytics
            analytics_result = await get_advanced_analytics_tool(
                vault_path=self.test_vault,
                days_back=7
            )
            self.assertTrue(analytics_result.get('success', False))
            
            # 3. Export knowledge graph
            export_result = await export_knowledge_graph_tool(
                vault_path=self.test_vault,
                format="json",
                include_content=False
            )
            self.assertTrue(export_result.get('success', False))
            
            # 4. Generate MOCs (with additional notes)
            self.create_additional_test_notes()
            moc_result = await generate_moc_from_clusters_tool(
                vault_path=self.test_vault,
                min_cluster_size=2,
                similarity_threshold=0.3,
                target_clusters=2
            )
            self.assertTrue(moc_result.get('success', False))
            
            # 5. Bulk reprocess
            reprocess_result = await bulk_reprocess_tool(
                vault_path=self.test_vault,
                target_folder="1 - Notes",
                reprocess_count=5,
                min_confidence_improvement=0.01
            )
            self.assertTrue(reprocess_result.get('success', False))
        
        asyncio.run(run_test())

def run_comprehensive_tests():
    """Run all Phase 3 tests"""
    print("🧪 Running Phase 3 Comprehensive Test Suite")
    print("=" * 50)
    
    # Create test suite
    test_suite = unittest.TestSuite()
    
    # Add test cases
    test_classes = [
        TestInboxProcessing,
        TestBulkReprocessing,
        TestAdvancedAnalytics,
        TestKnowledgeGraphExport,
        TestMOCGeneration,
        TestPhase3Integration
    ]
    
    for test_class in test_classes:
        tests = unittest.TestLoader().loadTestsFromTestCase(test_class)
        test_suite.addTests(tests)
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(test_suite)
    
    # Report results
    print("\n" + "=" * 50)
    print("🧪 Phase 3 Test Results")
    print("=" * 50)
    print(f"Tests run: {result.testsRun}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    
    if result.failures:
        print("\n❌ Failures:")
        for test, failure in result.failures:
            print(f"  - {test}: {failure}")
    
    if result.errors:
        print("\n🚨 Errors:")
        for test, error in result.errors:
            print(f"  - {test}: {error}")
    
    success = len(result.failures) == 0 and len(result.errors) == 0
    
    if success:
        print("\n✅ All Phase 3 tests passed!")
        print("🎉 Phase 3 implementation is working correctly")
    else:
        print("\n❌ Some tests failed")
        print("🔧 Phase 3 implementation needs debugging")
    
    return success

if __name__ == "__main__":
    success = run_comprehensive_tests()
    sys.exit(0 if success else 1)

