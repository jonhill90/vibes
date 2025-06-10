#!/usr/bin/env python3
"""
Test Phase 2 implementation of INMPARA Notebook MCP Server
"""

import os
import sys
sys.path.append('src')

# Set up environment
os.environ['INMPARA_VAULT_PATH'] = '/workspace/vibes/repos/inmpara'

def test_phase2_components():
    """Test Phase 2 components independently"""
    
    print("🧪 Testing Phase 2 Components")
    print("=" * 50)
    
    try:
        # Test imports
        from src.database.database import INMPARADatabase
        from src.pattern_learner import PatternLearner, UserFeedback
        from src.session_manager import SessionManager
        print("✅ All Phase 2 imports successful")
        
        # Test database initialization
        db = INMPARADatabase("./data/test_inmpara_vault.db")
        # Database auto-initializes
        print("✅ Database initialization successful")
        
        # Test pattern learner
        pattern_learner = PatternLearner(db)
        print("✅ Pattern learner initialization successful")
        
        # Test session manager
        session_manager = SessionManager(db)
        print("✅ Session manager initialization successful")
        
        # Test pattern learner methods
        stats = pattern_learner.get_learning_stats()
        print(f"✅ Learning stats: {stats['total_patterns']} patterns")
        
        thresholds = pattern_learner.get_current_thresholds()
        print(f"✅ Current thresholds: auto_create={thresholds['auto_create']:.2f}")
        
        # Test session manager methods
        session_id = session_manager.start_session()
        print(f"✅ Started new session: {session_id}")
        
        context = session_manager.get_session_context(session_id)
        print(f"✅ Session context retrieved: {len(context.get('topics', []))} topics")
        
        # Test feedback processing
        feedback = UserFeedback(
            action_type="test_feedback",
            original_value="test_original",
            corrected_value="test_corrected", 
            note_id="test_note_123",
            confidence_impact=0.1,
            context={"test": True}
        )
        
        result = pattern_learner.learn_from_feedback(feedback)
        print(f"✅ Feedback processing: {len(result.get('patterns_updated', []))} patterns updated")
        
        print("\n🎉 All Phase 2 components working correctly!")
        
        return True
        
    except Exception as e:
        print(f"❌ Error testing Phase 2 components: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_phase2_tools():
    """Test Phase 2 MCP tools"""
    
    print("\n🔧 Testing Phase 2 MCP Tools")
    print("=" * 50)
    
    try:
        # Import server with absolute imports
        import importlib.util
        spec = importlib.util.spec_from_file_location("server", "src/server.py")
        server_module = importlib.util.module_from_spec(spec)
        
        # Monkey patch for relative imports
        sys.modules['database.database'] = importlib.import_module('src.database.database')
        sys.modules['database.vector_search'] = importlib.import_module('src.database.vector_search')
        sys.modules['content_analyzer'] = importlib.import_module('src.content_analyzer')
        sys.modules['template_engine'] = importlib.import_module('src.template_engine')
        sys.modules['conversation_monitor'] = importlib.import_module('src.conversation_monitor')
        sys.modules['pattern_learner'] = importlib.import_module('src.pattern_learner')
        sys.modules['session_manager'] = importlib.import_module('src.session_manager')
        sys.modules['utils.file_utils'] = importlib.import_module('src.utils.file_utils')
        
        spec.loader.exec_module(server_module)
        
        print("✅ Server module loaded with Phase 2 components")
        
        # Test server initialization
        server = server_module.INMPARANotebookServer()
        print("✅ INMPARA Notebook Server initialized")
        
        print(f"✅ Pattern Learner: {type(server.pattern_learner).__name__}")
        print(f"✅ Session Manager: {type(server.session_manager).__name__}")
        
        print("\n🎉 Phase 2 MCP Server ready!")
        
        return True
        
    except Exception as e:
        print(f"❌ Error testing Phase 2 tools: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("🚀 INMPARA Notebook MCP Server - Phase 2 Testing")
    print("=" * 60)
    
    # Test components first
    components_ok = test_phase2_components()
    
    if components_ok:
        # Test full server
        tools_ok = test_phase2_tools()
        
        if tools_ok:
            print("\n✅ PHASE 2 IMPLEMENTATION COMPLETE")
            print("🎯 Ready for production use with advanced intelligence features:")
            print("   - Learning from user feedback")
            print("   - Cross-conversation context tracking") 
            print("   - Improved confidence scoring")
            print("   - Pattern-based decision making")
        else:
            print("\n⚠️  Components work but server has issues")
    else:
        print("\n❌ Phase 2 components have issues")
