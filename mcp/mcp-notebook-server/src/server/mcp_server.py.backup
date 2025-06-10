"""
INMPARA MCP Server Core Implementation

This module contains the main INMPARAServer class that handles MCP protocol
communication and coordinates between different functional modules.

Target: ~300 lines - Core server logic only, no tool implementations
"""

import asyncio
import os
import sys
import logging
from pathlib import Path
from typing import Dict, List, Any, Optional

# MCP imports
from mcp.server import Server
from mcp.server.models import InitializationOptions
from mcp.server.stdio import stdio_server

# Add parent directory to path for imports
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

# Database and core components
from database.database import INMPARADatabase
from database.vector_search import VectorSearchEngine
from utils.file_utils import INMPARAFileManager

# Core business logic modules
from core import NotesManager
from core import SearchManager
from core import InboxManager
from core import AnalyticsManager
from core import SessionsManager, LearningManager

# Tool registration
from server.tools import setup_mcp_tools

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Load environment variables
from dotenv import load_dotenv
load_dotenv()


class INMPARAServer:
    """
    INMPARA Notebook MCP Server
    
    Main server class that handles MCP protocol communication and coordinates
    between different functional modules for intelligent note-taking.
    """
    
    def __init__(self):
        """Initialize the INMPARA MCP Server with configuration and components."""
        # Configuration from environment (updated for new vault structure)
        self.vault_path = os.getenv('INMPARA_VAULT_PATH', '/workspace/vibes/repos/inmpara')
        self.db_path = os.getenv('SQLITE_DB_PATH', 'vault/.notebook/inmpara.db')
        self.qdrant_host = os.getenv('QDRANT_HOST', 'localhost')
        self.qdrant_port = int(os.getenv('QDRANT_PORT', '6334'))
        self.collection_name = os.getenv('QDRANT_COLLECTION', 'inmpara_vault')
        
        # Processing thresholds
        self.confidence_threshold = float(os.getenv('CONFIDENCE_THRESHOLD', '0.85'))
        self.auto_approve_threshold = float(os.getenv('AUTO_APPROVE_THRESHOLD', '0.9'))
        
        # Component placeholders
        self.server = None
        self.database = None
        self.vector_search = None
        
        self.session_manager = None
        self.file_manager = None
        
        # New core modules
        self.notes_manager = None
        self.search_manager = None
        self.inbox_manager = None
        self.analytics_manager = None
        self.learning_manager = None
        self.sessions_manager = None
        
        logger.info(f"INMPARA Server initialized with vault: {self.vault_path}")
        logger.info(f"Database location: {self.db_path}")
    
    async def initialize(self):
        """Initialize all server components and connections."""
        try:
            # Ensure vault and database directories exist
            os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
            os.makedirs(self.vault_path, exist_ok=True)
            
            # Initialize database
            self.database = INMPARADatabase(self.db_path)
            logger.info("Database initialized")
            
            # Initialize vector search
            self.vector_search = VectorSearchEngine(
                host=self.qdrant_host,
                port=self.qdrant_port,
                collection_name=self.collection_name
            )
            await self.vector_search.initialize()
            logger.info("Vector search engine initialized")
            
            # Initialize legacy components for compatibility
            self.file_manager = INMPARAFileManager(self.vault_path)

            # Initialize new core modules
            self.sessions_manager = SessionsManager(
                vault_path=self.vault_path,
                database=self.database
            )
            logger.info("Sessions manager initialized")
            
            self.learning_manager = LearningManager(
                vault_path=self.vault_path,
                database=self.database
            )
            logger.info("Learning manager initialized")
            
            
            
            self.session_manager = SessionManager(
                database=self.database,
                vector_search=self.vector_search
            )
            
            # Initialize new core modules
            self.notes_manager = NotesManager(
                vault_path=self.vault_path,
                
                
                file_manager=self.file_manager
            )
            
            self.search_manager = SearchManager(
                vault_path=self.vault_path,
                vector_search_engine=self.vector_search,
                database=self.database
            )
            
            self.inbox_manager = InboxManager(
                vault_path=self.vault_path,
                notes_manager=self.notes_manager,
                
                
                database=self.database
            )
            
            self.analytics_manager = AnalyticsManager(
                vault_path=self.vault_path,
                database=self.database,
                vector_search=self.vector_search
            )
            
            self.learning_manager = LearningManager(
                database=self.database,
                confidence_threshold=self.confidence_threshold
            )
            
            self.sessions_manager = SessionsManager(
                database=self.database,
                vector_search=self.vector_search
            )
            
            # Create MCP server instance
            self.server = Server("inmpara-notebook-server")
            
            # Setup all tools
            setup_mcp_tools(self.server, self)
            
            logger.info("All components initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize server: {e}")
            raise
    
    def run(self):
        """Start the MCP server and handle stdio communication."""
        async def main():
            try:
                await self.initialize()
                
                # Run server with stdio transport
                async with stdio_server() as (read_stream, write_stream):
                    await self.server.run(
                        read_stream,
                        write_stream,
                        InitializationOptions(
                            server_name="inmpara-notebook-server",
                            server_version="1.0.0",
                            capabilities={}
                        )
                    )
                    
            except Exception as e:
                logger.error(f"Server error: {e}")
                raise
        
        # Run the server
        try:
            asyncio.run(main())
        except KeyboardInterrupt:
            logger.info("Server shutdown requested")
        except Exception as e:
            logger.error(f"Fatal server error: {e}")
            raise
    
    def get_component(self, component_name: str):
        """Get a reference to a specific component."""
        components = {
            'database': self.database,
            'vector_search': self.vector_search,
            'session_manager': self.session_manager,
            'file_manager': self.file_manager,
            # New core modules
            'notes_manager': self.notes_manager,
            'search_manager': self.search_manager,
            'inbox_manager': self.inbox_manager,
            'analytics_manager': self.analytics_manager,
            'learning_manager': self.learning_manager,
            'sessions_manager': self.sessions_manager
        }
        return components.get(component_name)
    
    def get_vault_path(self) -> str:
        """Get the configured vault path."""
        return self.vault_path
    
    def get_confidence_threshold(self) -> float:
        """Get the current confidence threshold."""
        return self.confidence_threshold
    
    def get_auto_approve_threshold(self) -> float:
        """Get the auto-approval threshold."""
        return self.auto_approve_threshold


# Legacy alias for backward compatibility
INMPARANotebookServer = INMPARAServer
