#!/usr/bin/env python3
"""
INMPARA Notebook MCP Server - Phase 3 Complete
Production-ready server with all Phase 1, 2, and 3 features
Complete automation where users can dump content in inbox and trust AI processing
"""

import asyncio
import os
import sys
import logging
from pathlib import Path

# Add src to Python path
src_path = Path(__file__).parent / "src"
sys.path.insert(0, str(src_path))

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# MCP imports
from mcp.server import Server
from mcp.server.stdio import stdio_server

# Import all components
from src.database.database import db
from src.content_analyzer import content_analyzer
from src.pattern_learner import pattern_learner
from src.session_manager import session_manager

# Import Phase 1 components
from src.server import (
    capture_conversation_insight,
    auto_create_note,
    search_notes,
    suggest_connections,
    analyze_content,
    get_note_content,
    list_notes,
    create_moc,
    archive_note,
    get_vault_status
)

# Import Phase 2 components
from src.phase2_tool_registrations import (
    register_phase2_tools,
    get_phase2_tool_definitions
)

# Import Phase 3 components
from src.phase3_tool_registrations import (
    register_phase3_tools,
    get_phase3_tool_definitions
)

# Create server instance
server = Server("inmpara-notebook-server")

def setup_environment():
    """Setup the server environment"""
    try:
        # Initialize database
        logger.info("Initializing database...")
        db.initialize_database()
        
        # Initialize components
        logger.info("Initializing AI components...")
        # Components are initialized when imported
        
        # Verify vault path exists
        vault_path = os.getenv('INMPARA_VAULT_PATH', '/workspace/vibes/repos/inmpara')
        if not os.path.exists(vault_path):
            logger.warning(f"Vault path does not exist: {vault_path}")
            logger.info("Server will continue but vault operations may fail")
        else:
            logger.info(f"Vault path verified: {vault_path}")
        
        logger.info("Environment setup complete")
        return True
        
    except Exception as e:
        logger.error(f"Environment setup failed: {str(e)}")
        return False

def register_all_tools():
    """Register all Phase 1, 2, and 3 tools"""
    try:
        logger.info("Registering all MCP tools...")
        
        # Phase 1 tools (basic functionality) - already defined in server.py
        # These are registered when the server module is imported
        
        # Phase 2 tools (advanced intelligence)
        register_phase2_tools(server)
        logger.info("Phase 2 tools registered")
        
        # Phase 3 tools (complete automation)
        register_phase3_tools(server)
        logger.info("Phase 3 tools registered")
        
        # Get tool counts
        phase1_tools = 10  # From original implementation
        phase2_tools = len(get_phase2_tool_definitions())
        phase3_tools = len(get_phase3_tool_definitions())
        total_tools = phase1_tools + phase2_tools + phase3_tools
        
        logger.info(f"All tools registered successfully:")
        logger.info(f"  Phase 1: {phase1_tools} tools (basic functionality)")
        logger.info(f"  Phase 2: {phase2_tools} tools (advanced intelligence)")
        logger.info(f"  Phase 3: {phase3_tools} tools (complete automation)")
        logger.info(f"  Total: {total_tools} tools available")
        
        return True
        
    except Exception as e:
        logger.error(f"Tool registration failed: {str(e)}")
        return False

@server.list_tools()
async def list_tools():
    """List all available tools across all phases"""
    tools = []
    
    # Phase 1 tools
    phase1_tools = [
        {
            "name": "capture_conversation_insight",
            "description": "Capture insights from conversations and create notes automatically"
        },
        {
            "name": "auto_create_note", 
            "description": "Create properly formatted INMPARA notes with AI assistance"
        },
        {
            "name": "search_notes",
            "description": "Search through existing notes using content and metadata"
        },
        {
            "name": "suggest_connections",
            "description": "Find related notes and suggest connections"
        },
        {
            "name": "analyze_content",
            "description": "Analyze content for INMPARA classification and tagging"
        },
        {
            "name": "get_note_content",
            "description": "Retrieve the full content of a specific note"
        },
        {
            "name": "list_notes",
            "description": "List notes with filtering and sorting options"
        },
        {
            "name": "create_moc",
            "description": "Create Maps of Content (MOCs) to organize related notes"
        },
        {
            "name": "archive_note",
            "description": "Archive notes that are no longer active"
        },
        {
            "name": "get_vault_status",
            "description": "Get overview of vault structure and statistics"
        }
    ]
    
    # Add Phase 1 tools
    for tool_def in phase1_tools:
        tools.append({
            "name": tool_def["name"],
            "description": f"[Phase 1] {tool_def['description']}"
        })
    
    # Add Phase 2 tools
    for tool_def in get_phase2_tool_definitions():
        tools.append({
            "name": tool_def.name,
            "description": f"[Phase 2] {tool_def.description}"
        })
    
    # Add Phase 3 tools
    for tool_def in get_phase3_tool_definitions():
        tools.append({
            "name": tool_def.name,
            "description": f"[Phase 3] {tool_def.description}"
        })
    
    return tools

async def main():
    """Main server entry point"""
    print("🚀 INMPARA Notebook MCP Server - Phase 3 Complete")
    print("=" * 60)
    print("Complete automation where users can dump content in inbox")
    print("and trust AI processing with comprehensive analytics")
    print("=" * 60)
    
    # Setup environment
    if not setup_environment():
        print("❌ Environment setup failed")
        sys.exit(1)
    
    # Register tools
    if not register_all_tools():
        print("❌ Tool registration failed")
        sys.exit(1)
    
    print("✅ Server initialization complete")
    print("\nFeatures available:")
    print("📋 Phase 1: Basic conversation monitoring and note creation")
    print("🧠 Phase 2: Advanced intelligence with learning and cross-session context")
    print("🤖 Phase 3: Complete automation with analytics and quality improvement")
    print()
    print("🔗 Ready for Claude Desktop integration")
    print("Add this server to your Claude Desktop MCP configuration")
    print()
    
    try:
        # Run the server
        async with stdio_server() as (read_stream, write_stream):
            await server.run(
                read_stream,
                write_stream,
                server.create_initialization_options()
            )
    except KeyboardInterrupt:
        print("\n👋 Server shutting down...")
    except Exception as e:
        logger.error(f"Server error: {str(e)}")
        print(f"❌ Server error: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())

