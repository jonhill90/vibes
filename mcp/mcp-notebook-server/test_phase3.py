#!/usr/bin/env python3
"""
Phase 3 Test Suite for INMPARA Notebook MCP Server
Tests all advanced automation and analytics features.
"""

import unittest
import asyncio
import tempfile
import os
import shutil
import json
from pathlib import Path

# Add src to path
import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from phase3_tools import (
    process_inbox_tool,
    bulk_reprocess_tool,
    get_advanced_analytics_tool,
    export_knowledge_graph_tool,
    generate_moc_from_clusters_tool
)

class TestPhase3Features(unittest.TestCase):
    """Test suite for Phase 3 advanced automation features"""
    
    def setUp(self):
        """Set up test environment"""
        self.test_dir = tempfile.mkdtemp(prefix="inmpara_test_")
        self.inbox_dir = os.path.join(self.test_dir, "00 - Inbox")
        self.meta_dir = os.path.join(self.test_dir, "99 - Meta")
        os.makedirs(self.inbox_dir, exist_ok=True)
        os.makedirs(self.meta_dir, exist_ok=True)
        
        # Create sample inbox files
        self.create_sample_inbox_files()
    
    def tearDown(self):
        """Clean up test environment"""
        if os.path.exists(self.test_dir):
            shutil.rmtree(self.test_dir)
    
    def create_sample_inbox_files(self):
        """Create sample files for testing"""
        files = [
            ("test1.md", "# Kubernetes Testing\nSome content about k8s monitoring"),
            ("test2.md", "# Database Performance\nContent about database optimization"),
            ("test3.md", "# AI Model Training\nMachine learning pipeline notes")
        ]
        
        for filename, content in files:
            with open(os.path.join(self.inbox_dir, filename), 'w') as f:
                f.write(content)
    
    def test_inbox_processing(self):
        """Test inbox processing functionality"""
        async def run_test():
            result = await process_inbox_tool(
                vault_path=self.test_dir,
                confidence_threshold=0.8,
                auto_approve=True
            )
            
            self.assertTrue(result.get('success', False))
            self.assertGreaterEqual(result.get('processed_count', 0), 1)
            self.assertIn('processed_files', result)
        
        asyncio.run(run_test())
    
    def test_inbox_processing_with_confidence_threshold(self):
        """Test inbox processing with different confidence thresholds"""
        async def run_test():
            result = await process_inbox_tool(
                vault_path=self.test_dir,
                confidence_threshold=0.95,
                auto_approve=False
            )
            
            self.assertTrue(result.get('success', False))
            self.assertIn('processed_files', result)
        
        asyncio.run(run_test())
    
    def test_bulk_reprocessing(self):
        """Test bulk reprocessing functionality"""
        async def run_test():
            result = await bulk_reprocess_tool(
                vault_path=self.test_dir,
                confidence_threshold=0.7
            )
            
            self.assertTrue(result.get('success', False))
            self.assertIn('analyzed_count', result)
        
        asyncio.run(run_test())
    
    def test_advanced_analytics(self):
        """Test advanced analytics generation"""
        async def run_test():
            result = await get_advanced_analytics_tool(
                vault_path=self.test_dir,
                days_back=30
            )
            
            self.assertTrue(result.get('success', False))
            self.assertIn('analysis_period', result)
            self.assertIn('processing_activity', result)
        
        asyncio.run(run_test())
    
    def test_knowledge_graph_export(self):
        """Test knowledge graph export"""
        async def run_test():
            result = await export_knowledge_graph_tool(
                vault_path=self.test_dir,
                format="json",
                include_content=False
            )
            
            self.assertTrue(result.get('success', False))
            self.assertIn('export_path', result)
            self.assertGreaterEqual(result.get('node_count', 0), 0)
        
        asyncio.run(run_test())
    
    def test_knowledge_graph_graphml_export(self):
        """Test GraphML export format"""
        async def run_test():
            result = await export_knowledge_graph_tool(
                vault_path=self.test_dir,
                format="graphml",
                include_content=True
            )
            
            self.assertTrue(result.get('success', False))
            self.assertIn('export_path', result)
        
        asyncio.run(run_test())
    
    def test_moc_generation(self):
        """Test MOC auto-generation"""
        async def run_test():
            result = await generate_moc_from_clusters_tool(
                vault_path=self.test_dir,
                min_notes_per_cluster=1,
                confidence_threshold=0.6
            )
            
            self.assertTrue(result.get('success', False))
            self.assertIn('generated_mocs', result)
        
        asyncio.run(run_test())
    
    def test_error_handling(self):
        """Test error handling with invalid paths"""
        async def run_test():
            result = await process_inbox_tool(
                vault_path="/nonexistent/path",
                confidence_threshold=0.8,
                auto_approve=True
            )
            
            # Should handle error gracefully
            self.assertFalse(result.get('success', True))
            self.assertIn('error', result)
        
        asyncio.run(run_test())

class TestIntegration(unittest.TestCase):
    """Integration tests for complete workflows"""
    
    def setUp(self):
        """Set up integration test environment"""
        self.test_dir = tempfile.mkdtemp(prefix="inmpara_integration_")
        self.setup_vault_structure()
    
    def tearDown(self):
        """Clean up test environment"""
        if os.path.exists(self.test_dir):
            shutil.rmtree(self.test_dir)
    
    def setup_vault_structure(self):
        """Create a complete vault structure"""
        dirs = [
            "00 - Inbox",
            "10 - Projects", 
            "20 - Areas",
            "30 - Resources",
            "40 - Archive",
            "99 - Meta"
        ]
        
        for dir_name in dirs:
            os.makedirs(os.path.join(self.test_dir, dir_name), exist_ok=True)
        
        # Add some sample content
        sample_content = [
            ("00 - Inbox/cloud-architecture.md", "# Cloud Architecture\nNotes on AWS patterns"),
            ("30 - Resources/kubernetes-guide.md", "# Kubernetes Guide\nContainer orchestration"),
            ("20 - Areas/DevOps.md", "# DevOps Practices\nCI/CD and automation")
        ]
        
        for path, content in sample_content:
            full_path = os.path.join(self.test_dir, path)
            os.makedirs(os.path.dirname(full_path), exist_ok=True)
            with open(full_path, 'w') as f:
                f.write(content)
    
    def test_full_workflow(self):
        """Test complete workflow from inbox to MOC generation"""
        async def run_workflow():
            # Step 1: Process inbox
            inbox_result = await process_inbox_tool(
                vault_path=self.test_dir,
                confidence_threshold=0.7,
                auto_approve=True
            )
            self.assertTrue(inbox_result.get('success', False))
            
            # Step 2: Generate analytics
            analytics_result = await get_advanced_analytics_tool(
                vault_path=self.test_dir,
                days_back=7
            )
            self.assertTrue(analytics_result.get('success', False))
            
            # Step 3: Export knowledge graph
            export_result = await export_knowledge_graph_tool(
                vault_path=self.test_dir,
                format="json",
                include_content=False
            )
            self.assertTrue(export_result.get('success', False))
            
            # Step 4: Generate MOCs
            moc_result = await generate_moc_from_clusters_tool(
                vault_path=self.test_dir,
                min_notes_per_cluster=1,
                confidence_threshold=0.5
            )
            self.assertTrue(moc_result.get('success', False))
            
            return True
        
        result = asyncio.run(run_workflow())
        self.assertTrue(result)

if __name__ == '__main__':
    print("🧪 Running Phase 3 Test Suite...")
    print("=" * 50)
    
    # Run tests
    unittest.main(verbosity=2)
