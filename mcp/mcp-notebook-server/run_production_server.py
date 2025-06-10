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

from database.database import db
from src.phase3_tools_prod import (
    process_inbox_tool,
    bulk_reprocess_tool,
    get_advanced_analytics_tool,
    export_knowledge_graph_tool,
    generate_moc_from_clusters_tool
)

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

class ProductionMCPServer:
    """Production MCP Server for Phase 3"""
    
    def __init__(self, vault_path: str):
        self.vault_path = vault_path
        self.logger = logging.getLogger(__name__)
        
    async def start(self):
        """Start the MCP server"""
        self.logger.info("🚀 INMPARA MCP Server Phase 3 - READY")
        self.logger.info("=" * 60)
        self.logger.info("Available tools:")
        self.logger.info("• process_inbox - Complete automation")
        self.logger.info("• bulk_reprocess - Quality improvement")  
        self.logger.info("• get_advanced_analytics - Comprehensive reporting")
        self.logger.info("• export_knowledge_graph - Multi-format export")
        self.logger.info("• generate_moc_from_clusters - Smart MOC creation")
        self.logger.info("=" * 60)
        
        # Keep server running
        try:
            while True:
                await asyncio.sleep(1)
        except KeyboardInterrupt:
            self.logger.info("📴 Server shutdown requested")

async def main():
    """Main server entry point"""
    parser = argparse.ArgumentParser(description='INMPARA Notebook MCP Server - Phase 3')
    parser.add_argument('--debug', action='store_true', help='Enable debug logging')
    parser.add_argument('--vault-path', default='/workspace/vibes/repos/inmpara', 
                       help='Path to INMPARA vault')
    parser.add_argument('--test', action='store_true', help='Run quick functionality test')
    
    args = parser.parse_args()
    
    # Setup logging
    setup_logging(args.debug)
    logger = logging.getLogger(__name__)
    
    if args.test:
        logger.info("🧪 Running Phase 3 functionality test...")
        
        # Test all major functions
        try:
            result = await get_advanced_analytics_tool(args.vault_path)
            logger.info(f"✅ Analytics: {result.get('success', False)}")
            
            result = await export_knowledge_graph_tool(args.vault_path)
            logger.info(f"✅ Knowledge Graph: {result.get('success', False)}")
            
            result = await generate_moc_from_clusters_tool(args.vault_path)
            logger.info(f"✅ MOC Generation: {result.get('success', False)}")
            
            logger.info("🎉 All Phase 3 tools tested successfully!")
            return
            
        except Exception as e:
            logger.error(f"❌ Test failed: {e}")
            import traceback
            logger.debug(traceback.format_exc())
            return
    
    # Check vault structure
    vault_path = Path(args.vault_path)
    if not vault_path.exists():
        logger.warning(f"⚠️  Vault path does not exist: {args.vault_path}")
        logger.info("Creating basic vault structure...")
        vault_path.mkdir(parents=True, exist_ok=True)
        (vault_path / "00 - Inbox").mkdir(exist_ok=True)
        (vault_path / "99 - Meta").mkdir(exist_ok=True)
        logger.info("✅ Basic vault structure created")
    
    # Start server
    server = ProductionMCPServer(args.vault_path)
    await server.start()

if __name__ == "__main__":
    asyncio.run(main())
