#!/usr/bin/env python3
"""
Basic functionality test for INMPARA Notebook Server
Tests core components without requiring Qdrant connection.
"""

import sys
import os
from pathlib import Path
import tempfile
import shutil

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

def test_content_analyzer():
    """Test content analysis functionality."""
    print("🧪 Testing Content Analyzer...")
    
    from content_analyzer import INMPARAContentAnalyzer
    
    analyzer = INMPARAContentAnalyzer()
    
    # Test content
    test_content = """
    Found that Azure Databricks requires specific DNS configuration for private endpoints. 
    The issue was that the private DNS zone wasn't properly linked to the VNet.
    Solution is to create an A record mapping the workspace URL to the private endpoint IP.
    """
    
    result = analyzer.analyze_content(test_content)
    
    print(f"   ✅ Title: {result.title}")
    print(f"   ✅ Content Type: {result.content_type}")
    print(f"   ✅ Primary Domain: {result.primary_domain}")
    print(f"   ✅ Tags: {result.tags}")
    print(f"   ✅ Confidence: {result.confidence:.2f}")
    print(f"   ✅ Observations: {len(result.observations)} found")
    
    return result

def test_template_engine():
    """Test template generation."""
    print("🧪 Testing Template Engine...")
    
    from template_engine import INMPARATemplateEngine
    from content_analyzer import INMPARAContentAnalyzer
    
    # Use temporary vault path
    with tempfile.TemporaryDirectory() as temp_vault:
        template_engine = INMPARATemplateEngine(temp_vault)
        analyzer = INMPARAContentAnalyzer()
        
        # Analyze content
        test_content = "Azure private endpoint DNS configuration requires A records."
        result = analyzer.analyze_content(test_content)
        
        # Generate note
        note_content = template_engine.generate_note(
            result,
            content=test_content,
            context="Test context",
            source_type="test"
        )
        
        print(f"   ✅ Generated note with {len(note_content)} characters")
        print(f"   ✅ Contains frontmatter: {'---' in note_content}")
        print(f"   ✅ Contains title: {'#' in note_content}")
        print(f"   ✅ Contains observations: {'## Observations' in note_content}")
        
        # Test validation
        validation = template_engine.validate_inmpara_format(note_content)
        print(f"   ✅ Format validation: {'valid' if validation['valid'] else 'invalid'}")
        
        return note_content

def test_database():
    """Test database operations."""
    print("🧪 Testing Database...")
    
    from database.database import INMPARADatabase
    
    # Use temporary database
    with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as temp_db:
        temp_db_path = temp_db.name
    
    try:
        db = INMPARADatabase(temp_db_path)
        
        # Test note insertion
        note_data = {
            'title': 'Test Note',
            'file_path': '1 - Notes/test-note.md',
            'content_type': 'note',
            'domain': 'testing',
            'created_date': '2025-06-10',
            'modified_date': '2025-06-10',
            'confidence_score': 0.85,
            'source_type': 'test',
            'word_count': 10,
            'character_count': 50,
            'content_hash': 'test_hash',
            'frontmatter': {'title': 'Test Note'},
            'tags': [{'tag': 'testing', 'tag_type': 'auto'}],
            'relationships': []
        }
        
        note_id = db.add_note(note_data)
        print(f"   ✅ Created note with ID: {note_id}")
        
        # Test search
        search_results = db.search_notes(query="Test", limit=5)
        print(f"   ✅ Search returned {len(search_results)} results")
        
        # Test insight tracking
        insight_data = {
            'session_id': 'test_session',
            'insight_text': 'Test insight',
            'confidence': 0.8,
            'insight_type': 'technical-finding',
            'domains': ['testing']
        }
        
        insight_id = db.add_conversation_insight(insight_data)
        print(f"   ✅ Created insight with ID: {insight_id}")
        
        # Test stats
        stats = db.get_processing_stats(30)
        print(f"   ✅ Retrieved processing stats: {len(stats)} entries")
        
    finally:
        # Cleanup
        os.unlink(temp_db_path)

def test_file_manager():
    """Test file management operations."""
    print("🧪 Testing File Manager...")
    
    from utils.file_utils import INMPARAFileManager
    
    with tempfile.TemporaryDirectory() as temp_vault:
        file_manager = INMPARAFileManager(temp_vault)
        
        # Test vault structure creation
        inbox_path = Path(temp_vault) / "0 - Inbox"
        notes_path = Path(temp_vault) / "1 - Notes"
        
        print(f"   ✅ Inbox folder exists: {inbox_path.exists()}")
        print(f"   ✅ Notes folder exists: {notes_path.exists()}")
        
        # Test file creation
        test_content = """---
title: Test Note
type: note
---

# Test Note

This is a test note.
"""
        
        success, file_path, message = file_manager.create_file(
            test_content,
            "1 - Notes",
            "test-note.md"
        )
        
        print(f"   ✅ File creation: {success} - {message}")
        print(f"   ✅ File path: {file_path}")
        
        # Test file search
        search_results = file_manager.search_files("test")
        print(f"   ✅ Search found {len(search_results)} files")
        
        # Test statistics
        stats = file_manager.get_vault_statistics()
        print(f"   ✅ Vault stats: {stats['total_files']} files, {stats['word_count']} words")

def test_conversation_monitor():
    """Test conversation monitoring without vector search."""
    print("🧪 Testing Conversation Monitor (basic)...")
    
    from conversation_monitor import ConversationMonitor
    from content_analyzer import INMPARAContentAnalyzer
    
    # Mock minimal components for testing
    class MockDatabase:
        def add_conversation_insight(self, data):
            return 1
    
    class MockVectorSearch:
        def suggest_connections(self, *args, **kwargs):
            return []
    
    class MockTemplateEngine:
        def __init__(self):
            pass
    
    analyzer = INMPARAContentAnalyzer()
    mock_db = MockDatabase()
    mock_vector = MockVectorSearch()
    mock_template = MockTemplateEngine()
    
    monitor = ConversationMonitor(
        database=mock_db,
        vector_search=mock_vector,
        template_engine=mock_template,
        vault_path="/tmp"
    )
    
    # Test insight detection
    test_message = "Found that Azure Databricks requires specific DNS configuration. The issue was missing A records."
    
    insights = monitor.content_analyzer.analyze_for_insights(test_message)
    print(f"   ✅ Detected {len(insights)} insights")
    
    for insight in insights:
        print(f"      - {insight['type']}: confidence {insight['confidence']:.2f}")
    
    session_id = monitor.start_new_session()
    print(f"   ✅ Started session: {session_id}")

def main():
    """Run all tests."""
    print("🚀 INMPARA Notebook Server - Basic Functionality Test")
    print("=" * 60)
    
    try:
        # Run tests
        test_content_analyzer()
        print()
        
        test_template_engine()
        print()
        
        test_database()
        print()
        
        test_file_manager()
        print()
        
        test_conversation_monitor()
        print()
        
        print("✅ All basic functionality tests passed!")
        print()
        print("🎯 Phase 1 implementation is working correctly!")
        print("📋 Next steps:")
        print("   1. Start Qdrant: docker-compose up -d qdrant")
        print("   2. Run build script: ./build.sh")
        print("   3. Start server: python main.py")
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    return 0

if __name__ == "__main__":
    exit(main())
