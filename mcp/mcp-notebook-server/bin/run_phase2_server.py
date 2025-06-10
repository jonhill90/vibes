#!/usr/bin/env python3
"""
INMPARA Notebook MCP Server - Phase 2 Production Runner
Handles import issues and provides clean startup
"""

import os
import sys
import asyncio
import logging
from pathlib import Path

# Setup paths and environment
script_dir = Path(__file__).parent
src_dir = script_dir / "src"
sys.path.insert(0, str(src_dir))

# Set default environment variables
os.environ.setdefault('INMPARA_VAULT_PATH', '/workspace/vibes/repos/inmpara')
os.environ.setdefault('SQLITE_DB_PATH', './data/inmpara_vault.db')
os.environ.setdefault('QDRANT_HOST', 'localhost')
os.environ.setdefault('QDRANT_PORT', '6334')

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def fix_imports():
    """Fix relative import issues"""
    import importlib.util
    
    # Load modules with absolute paths to avoid relative import issues
    modules_to_load = {
        'database.database': src_dir / 'database' / 'database.py',
        'database.vector_search': src_dir / 'database' / 'vector_search.py',
        'content_analyzer': src_dir / 'content_analyzer.py',
        'template_engine': src_dir / 'template_engine.py',
        'conversation_monitor': src_dir / 'conversation_monitor.py',
        'pattern_learner': src_dir / 'pattern_learner.py',
        'session_manager': src_dir / 'session_manager.py',
        'utils.file_utils': src_dir / 'utils' / 'file_utils.py',
    }
    
    for module_name, module_path in modules_to_load.items():
        if module_name not in sys.modules:
            spec = importlib.util.spec_from_file_location(module_name, module_path)
            module = importlib.util.module_from_spec(spec)
            sys.modules[module_name] = module
            spec.loader.exec_module(module)

async def run_server():
    """Run the INMPARA Notebook MCP Server with Phase 2 features"""
    
    try:
        # Ensure data directory exists
        data_dir = script_dir / "data"
        data_dir.mkdir(exist_ok=True)
        
        logger.info("🚀 Starting INMPARA Notebook MCP Server - Phase 2")
        logger.info("=" * 60)
        
        # Fix import issues
        fix_imports()
        logger.info("✅ Import paths resolved")
        
        # Import server components
        from database.database import INMPARADatabase
        from pattern_learner import PatternLearner
        from session_manager import SessionManager
        from content_analyzer import INMPARAContentAnalyzer
        from template_engine import INMPARATemplateEngine
        from conversation_monitor import ConversationMonitor
        from utils.file_utils import INMPARAFileManager
        
        # Import MCP components
        from mcp.server import Server
        from mcp.server.stdio import stdio_server
        from mcp.types import TextContent, Tool
        
        logger.info("✅ All components imported successfully")
        
        # Initialize core components
        vault_path = os.getenv('INMPARA_VAULT_PATH')
        db_path = os.getenv('SQLITE_DB_PATH')
        
        logger.info(f"📁 Vault path: {vault_path}")
        logger.info(f"🗄️  Database path: {db_path}")
        
        db = INMPARADatabase(db_path)
        content_analyzer = INMPARAContentAnalyzer()
        template_engine = INMPARATemplateEngine(vault_path)
        file_manager = INMPARAFileManager(vault_path)
        conversation_monitor = ConversationMonitor()
        
        # Phase 2 components
        pattern_learner = PatternLearner(db)
        session_manager = SessionManager(db)
        
        logger.info("✅ Core components initialized")
        logger.info("🧠 Phase 2 intelligence components loaded")
        
        # Create MCP server
        server = Server("inmpara-notebook-server")
        
        @server.list_tools()
        async def handle_list_tools():
            """List all available tools including Phase 2 features"""
            return [
                # Phase 1 Core Tools
                Tool(
                    name="capture_conversation_insight",
                    description="Intelligently capture and create INMPARA notes from conversation insights",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "conversation_text": {"type": "string"},
                            "session_id": {"type": "string", "default": ""}
                        },
                        "required": ["conversation_text"]
                    }
                ),
                Tool(
                    name="auto_create_note",
                    description="Create INMPARA-formatted note with automatic analysis and filing",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "content": {"type": "string"},
                            "title": {"type": "string", "default": ""},
                            "force_create": {"type": "boolean", "default": False}
                        },
                        "required": ["content"]
                    }
                ),
                
                # Phase 2 Advanced Intelligence Tools
                Tool(
                    name="learn_from_feedback",
                    description="Learn from user corrections to improve AI decision making",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "action_type": {"type": "string"},
                            "original_value": {"type": "string"},
                            "corrected_value": {"type": "string"},
                            "note_id": {"type": "string"},
                            "context": {"type": "string", "default": "{}"}
                        },
                        "required": ["action_type", "original_value", "corrected_value", "note_id"]
                    }
                ),
                Tool(
                    name="get_session_context",
                    description="Get or create conversation session for cross-session tracking",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "session_id": {"type": "string", "default": ""}
                        },
                        "required": []
                    }
                ),
                Tool(
                    name="update_session_context",
                    description="Update session context with new conversation data",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "session_id": {"type": "string"},
                            "conversation_text": {"type": "string"},
                            "insights": {"type": "string", "default": "[]"},
                            "notes_created": {"type": "string", "default": "[]"}
                        },
                        "required": ["session_id", "conversation_text"]
                    }
                ),
                Tool(
                    name="get_learning_insights",
                    description="Get insights about learned patterns and AI improvements",
                    inputSchema={
                        "type": "object",
                        "properties": {},
                        "required": []
                    }
                )
            ]
        
        @server.call_tool()
        async def handle_call_tool(name: str, arguments: dict):
            """Handle all tool calls including Phase 2 features"""
            
            try:
                if name == "capture_conversation_insight":
                    conversation_text = arguments.get("conversation_text", "")
                    session_id = arguments.get("session_id", "")
                    
                    # Use conversation monitor to detect insights
                    insights = conversation_monitor.detect_insights(conversation_text)
                    
                    results = []
                    for insight in insights:
                        if insight.get('confidence', 0) > 0.7:
                            # Analyze content
                            analysis = content_analyzer.analyze_content(insight['text'])
                            
                            # Apply learned patterns for improved confidence
                            content_features = {
                                'content_type': getattr(analysis, 'content_type', ''),
                                'domain': getattr(analysis, 'primary_domain', ''),
                                'keywords': getattr(analysis, 'tags', [])[:3],
                                'has_technical_terms': True
                            }
                            
                            adjustments = pattern_learner.get_confidence_adjustments(content_features)
                            adjusted_confidence = min(1.0, analysis.confidence + adjustments.get('overall_adjustment', 0.0))
                            
                            if adjusted_confidence > pattern_learner.get_current_thresholds()['auto_create']:
                                # Auto-create note
                                note_content = template_engine.generate_note(analysis)
                                file_path = file_manager.save_note(note_content, analysis.destination_folder)
                                
                                # Store in database
                                note_id = db.add_note({
                                    'title': analysis.title,
                                    'file_path': file_path,
                                    'content_type': analysis.content_type,
                                    'domain': analysis.primary_domain,
                                    'confidence_score': adjusted_confidence,
                                    'source_type': 'conversation'
                                })
                                
                                results.append({
                                    'action': 'auto_created',
                                    'note_id': note_id,
                                    'title': analysis.title,
                                    'confidence': adjusted_confidence,
                                    'file_path': file_path
                                })
                    
                    # Update session context if provided
                    if session_id:
                        session_manager.update_session_context(
                            session_id, conversation_text, insights, [r.get('note_id') for r in results]
                        )
                    
                    response = {
                        'success': True,
                        'insights_detected': len(insights),
                        'notes_created': len(results),
                        'results': results,
                        'message': f"📝 Captured {len(results)} insights from conversation"
                    }
                    
                elif name == "auto_create_note":
                    content = arguments.get("content", "")
                    
                    # Analyze content with enhanced intelligence
                    analysis = content_analyzer.analyze_content(content)
                    
                    # Apply pattern learning
                    content_features = {
                        'content_type': getattr(analysis, 'content_type', ''),
                        'domain': getattr(analysis, 'primary_domain', ''),
                        'keywords': getattr(analysis, 'tags', [])[:3]
                    }
                    
                    adjustments = pattern_learner.get_confidence_adjustments(content_features)
                    suggestions = pattern_learner.get_suggested_improvements(content_features)
                    
                    # Generate and save note
                    note_content = template_engine.generate_note(analysis)
                    file_path = file_manager.save_note(note_content, analysis.destination_folder)
                    
                    response = {
                        'success': True,
                        'note_created': True,
                        'title': analysis.title,
                        'file_path': file_path,
                        'confidence': analysis.confidence,
                        'confidence_adjustments': adjustments,
                        'suggestions': suggestions,
                        'message': f"📄 Created note: {analysis.title}"
                    }
                    
                elif name == "learn_from_feedback":
                    from pattern_learner import UserFeedback
                    import json
                    
                    feedback = UserFeedback(
                        action_type=arguments.get("action_type"),
                        original_value=arguments.get("original_value"),
                        corrected_value=arguments.get("corrected_value"),
                        note_id=arguments.get("note_id"),
                        confidence_impact=0.0,
                        context=json.loads(arguments.get("context", "{}"))
                    )
                    
                    results = pattern_learner.learn_from_feedback(feedback)
                    stats = pattern_learner.get_learning_stats()
                    
                    response = {
                        'success': True,
                        'feedback_processed': True,
                        'patterns_updated': results.get('patterns_updated', []),
                        'learning_stats': stats,
                        'message': f"🧠 Learned from {feedback.action_type}: {len(results.get('patterns_updated', []))} patterns updated"
                    }
                    
                elif name == "get_session_context":
                    session_id = arguments.get("session_id", "")
                    
                    if not session_id:
                        session_id = session_manager.start_session()
                        context = session_manager.get_session_context(session_id)
                        response = {
                            'success': True,
                            'session_created': True,
                            'session_id': session_id,
                            'context': context,
                            'message': f"🚀 Started new session: {session_id}"
                        }
                    else:
                        context = session_manager.get_session_context(session_id)
                        response = {
                            'success': True,
                            'session_found': context is not None,
                            'session_id': session_id,
                            'context': context,
                            'message': f"📋 Retrieved session: {session_id}"
                        }
                        
                elif name == "update_session_context":
                    import json
                    
                    session_id = arguments.get("session_id")
                    conversation_text = arguments.get("conversation_text")
                    insights = json.loads(arguments.get("insights", "[]"))
                    notes_created = json.loads(arguments.get("notes_created", "[]"))
                    
                    updated_context = session_manager.update_session_context(
                        session_id, conversation_text, insights, notes_created
                    )
                    
                    suggestions = session_manager.get_context_based_suggestions(
                        session_id, conversation_text
                    )
                    
                    response = {
                        'success': True,
                        'session_updated': True,
                        'context': updated_context,
                        'suggestions': suggestions,
                        'message': f"🔄 Updated session {session_id}"
                    }
                    
                elif name == "get_learning_insights":
                    stats = pattern_learner.get_learning_stats()
                    thresholds = pattern_learner.get_current_thresholds()
                    
                    response = {
                        'success': True,
                        'learning_statistics': stats,
                        'confidence_thresholds': thresholds,
                        'message': f"📊 AI has learned {stats['total_patterns']} patterns"
                    }
                    
                else:
                    response = {
                        'success': False,
                        'error': f"Unknown tool: {name}"
                    }
                
                return [TextContent(type="text", text=f"{response.get('message', '')}\n\n{json.dumps(response, indent=2)}")]
                
            except Exception as e:
                logger.error(f"Error in tool {name}: {str(e)}")
                error_response = {
                    'success': False,
                    'error': str(e),
                    'tool': name
                }
                return [TextContent(type="text", text=f"❌ Error: {json.dumps(error_response, indent=2)}")]
        
        logger.info("✅ MCP tools registered")
        logger.info("🎯 Phase 2 server ready!")
        logger.info("=" * 60)
        
        # Run the server
        async with stdio_server() as (read_stream, write_stream):
            await server.run(read_stream, write_stream, InitializationOptions())
            
    except Exception as e:
        logger.error(f"Server startup failed: {e}")
        raise

if __name__ == "__main__":
    import json
    from mcp.server.models import InitializationOptions
    
    try:
        asyncio.run(run_server())
    except KeyboardInterrupt:
        logger.info("Server stopped by user")
    except Exception as e:
        logger.error(f"Server failed: {e}")
        sys.exit(1)
