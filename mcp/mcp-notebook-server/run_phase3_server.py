#!/usr/bin/env python3
"""
Production INMPARA Notebook MCP Server - Phase 3
Complete automation with advanced analytics and learning.
"""

import asyncio
import argparse
import logging
import sys
import os
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from database.database import INMPARADatabase as DatabaseManager
from server import InmparaMCPServer
from session_manager import SessionManager
from conversation_monitor import ConversationMonitor

# Phase 3 imports
from phase3_tool_registrations import register_phase3_tools

def setup_logging(debug=False):
    """Configure logging for production server"""
    level = logging.DEBUG if debug else logging.INFO
    
    logging.basicConfig(
        level=level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(sys.stdout),
            logging.FileHandler('inmpara_mcp_server.log')
        ]
    )
    
    # Reduce noise from some modules
    logging.getLogger('asyncio').setLevel(logging.WARNING)
    logging.getLogger('urllib3').setLevel(logging.WARNING)

async def main():
    """Main server entry point"""
    parser = argparse.ArgumentParser(description='INMPARA Notebook MCP Server - Phase 3')
    parser.add_argument('--debug', action='store_true', help='Enable debug logging')
    parser.add_argument('--vault-path', default='/workspace/vibes/repos/inmpara', 
                       help='Path to INMPARA vault')
    parser.add_argument('--db-path', default='inmpara_mcp.db',
                       help='Path to SQLite database')
    parser.add_argument('--port', type=int, default=8000,
                       help='Server port (for future HTTP transport)')
    
    args = parser.parse_args()
    
    # Setup logging
    setup_logging(args.debug)
    logger = logging.getLogger(__name__)
    
    logger.info("🚀 Starting INMPARA Notebook MCP Server - Phase 3")
    logger.info("=" * 60)
    logger.info("Features: Complete automation, analytics, learning")
    logger.info(f"Vault path: {args.vault_path}")
    logger.info(f"Database: {args.db_path}")
    
    try:
        # Initialize database
        db = INMPARADatabase(args.db_path)
        logger.info("✅ Database initialized")
        
        # Initialize session manager
        session_manager = SessionManager()
        logger.info("✅ Session manager initialized")
        
        # Initialize conversation monitor
        monitor = ConversationMonitor(session_manager)
        logger.info("✅ Conversation monitor initialized")
        
        # Create MCP server
        server = InmparaMCPServer(
            vault_path=args.vault_path,
            session_manager=session_manager,
            conversation_monitor=monitor
        )
        
        # Register Phase 3 tools
        register_phase3_tools(server, args.vault_path)
        logger.info("✅ Phase 3 tools registered")
        
        # Check vault structure
        vault_path = Path(args.vault_path)
        if not vault_path.exists():
            logger.warning(f"⚠️  Vault path does not exist: {args.vault_path}")
            logger.info("Creating basic vault structure...")
            vault_path.mkdir(parents=True, exist_ok=True)
            (vault_path / "00 - Inbox").mkdir(exist_ok=True)
            (vault_path / "99 - Meta").mkdir(exist_ok=True)
            logger.info("✅ Basic vault structure created")
        
        logger.info("🎯 Server ready for MCP connections")
        logger.info("=" * 60)
        logger.info("Phase 3 Features Available:")
        logger.info("• 📥 process_inbox - Complete automation")
        logger.info("• 🔧 bulk_reprocess - Quality improvement")
        logger.info("• 📊 get_advanced_analytics - Comprehensive reporting")
        logger.info("• 🕸️  export_knowledge_graph - Multi-format export")
        logger.info("• 📚 generate_moc_from_clusters - Smart MOC creation")
        logger.info("=" * 60)
        
        # Run server
        await server.run()
        
    except KeyboardInterrupt:
        logger.info("📴 Server shutdown requested")
    except Exception as e:
        logger.error(f"❌ Server error: {e}")
        import traceback
        logger.debug(traceback.format_exc())
        sys.exit(1)
    finally:
        logger.info("🛑 INMPARA MCP Server stopped")

if __name__ == "__main__":
    asyncio.run(main())
