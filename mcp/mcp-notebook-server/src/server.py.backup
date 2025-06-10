"""
Intelligent automatic knowledge capture with INMPARA methodology.
Phase 1: Core conversation monitoring and note creation.
"""

import asyncio
import os
import logging
from datetime import datetime
from typing import Dict, List, Any, Optional
from pathlib import Path

# MCP imports
from mcp.server import Server
from mcp.server.models import InitializationOptions
from mcp.server.stdio import stdio_server
from mcp.types import (
    Resource, Tool, TextContent, ImageContent, EmbeddedResource
)

# Local imports
from .database.database import INMPARADatabase
from .database.vector_search import VectorSearchEngine
from .content_analyzer import INMPARAContentAnalyzer
from .template_engine import INMPARATemplateEngine
from .conversation_monitor import ConversationMonitor
from .utils.file_utils import INMPARAFileManager

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Load environment variables
from dotenv import load_dotenv
load_dotenv()


class INMPARANotebookServer:
    """INMPARA Notebook MCP Server - Phase 1 Implementation."""
    
    def __init__(self):
        # Configuration from environment
        self.vault_path = os.getenv('INMPARA_VAULT_PATH', '/workspace/vibes/repos/inmpara')
        self.db_path = os.getenv('SQLITE_DB_PATH', './data/inmpara_vault.db')
        self.qdrant_host = os.getenv('QDRANT_HOST', 'localhost')
        self.qdrant_port = int(os.getenv('QDRANT_PORT', '6334'))
        self.collection_name = os.getenv('QDRANT_COLLECTION', 'inmpara_vault')
        
        # Thresholds
        self.auto_file_threshold = float(os.getenv('AUTO_FILE_THRESHOLD', '0.85'))
        self.insight_threshold = float(os.getenv('INSIGHT_DETECTION_THRESHOLD', '0.8'))
        self.suggestion_threshold = float(os.getenv('SUGGESTION_THRESHOLD', '0.6'))
        
        # Initialize components
        self.database = None
        self.vector_search = None
        self.content_analyzer = None
        self.template_engine = None
        self.conversation_monitor = None
        self.file_manager = None
        
        # MCP Server
        self.server = Server("inmpara-notebook-server")
        self._setup_tools()
        
        logger.info("INMPARA Notebook Server initialized")
    
    async def initialize(self):
        """Initialize all components."""
        try:
            # Create data directory
            os.makedirs('./data', exist_ok=True)
            
            # Initialize database
            self.database = INMPARADatabase(self.db_path)
            logger.info("Database initialized")
            
            # Initialize vector search
            self.vector_search = VectorSearchEngine(
                host=self.qdrant_host,
                port=self.qdrant_port,
                collection_name=self.collection_name
            )
            logger.info("Vector search initialized")
            
            # Initialize content analyzer
            self.content_analyzer = INMPARAContentAnalyzer()
            logger.info("Content analyzer initialized")
            
            # Initialize template engine
            self.template_engine = INMPARATemplateEngine(self.vault_path)
            logger.info("Template engine initialized")
            
            # Initialize file manager
            self.file_manager = INMPARAFileManager(self.vault_path)
            logger.info("File manager initialized")
            
            # Initialize conversation monitor
            self.conversation_monitor = ConversationMonitor(
                database=self.database,
                vector_search=self.vector_search,
                template_engine=self.template_engine,
                vault_path=self.vault_path
            )
            
            # Set conversation monitor thresholds
            self.conversation_monitor.update_thresholds(
                auto_create_threshold=self.insight_threshold,
                suggestion_threshold=self.suggestion_threshold
            )
            
            logger.info("Conversation monitor initialized")
            
            # Set up callbacks
            self.conversation_monitor.on_note_created = self._on_note_created
            self.conversation_monitor.on_suggestion_generated = self._on_suggestion_generated
            
            logger.info("INMPARA Notebook Server fully initialized")
            
        except Exception as e:
            logger.error(f"Failed to initialize server: {e}")
            raise
    
    def _setup_tools(self):
        """Set up MCP tools."""
        
        @self.server.tool("capture_conversation_insight")
        async def capture_conversation_insight(
            conversation_text: str,
            user_id: str = "user",
            session_id: Optional[str] = None
        ) -> List[Dict[str, Any]]:
            """
             automatic insight detection during chat.
            Monitors conversation for technical findings, insights, patterns, requirements.
            Auto-creates INMPARA-formatted notes when confidence >80%.
            """
            try:
                if session_id:
                    self.conversation_monitor.current_session_id = session_id
                
                results = await self.conversation_monitor.process_message(
                    conversation_text, user_id
                )
                
                logger.info(f"Processed conversation message, found {len(results)} insights")
                return results
                
            except Exception as e:
                logger.error(f"Error capturing conversation insight: {e}")
                return [{
                    'type': 'error',
                    'message': f"Failed to process conversation: {str(e)}"
                }]
        
        @self.server.tool("auto_create_note")
        async def auto_create_note(
            content: str,
            title: Optional[str] = None,
            content_type: Optional[str] = None,
            domain: Optional[str] = None,
            context: str = "",
            source_type: str = "manual"
        ) -> Dict[str, Any]:
            """
            Background note creation with perfect INMPARA formatting.
            Generates proper frontmatter, semantic markup, auto-assigns tags,
            creates relations, and files in correct INMPARA folder.
            """
            try:
                # Analyze content
                analysis_result = self.content_analyzer.analyze_content(
                    content,
                    context={'source_type': source_type}
                )
                
                # Override with provided parameters
                if title:
                    analysis_result.title = title
                    analysis_result.slug = self.template_engine._generate_slug(title)
                
                if content_type:
                    analysis_result.content_type = content_type
                    analysis_result.destination_folder = self.template_engine._determine_destination(analysis_result)
                
                if domain:
                    analysis_result.primary_domain = domain
                    if domain not in analysis_result.domains:
                        analysis_result.domains.insert(0, domain)
                
                # Generate the note
                note_content = self.template_engine.generate_note(
                    analysis_result,
                    content=content,
                    context=context,
                    source_type=source_type
                )
                
                # Determine file path
                file_path = self.template_engine.get_file_path(analysis_result)
                
                # Create the file
                success, relative_path, message = self.file_manager.create_file(
                    note_content,
                    analysis_result.destination_folder,
                    self.template_engine.generate_filename(analysis_result)
                )
                
                if not success:
                    return {
                        'success': False,
                        'error': message
                    }
                
                # Add to database
                note_data = {
                    'title': analysis_result.title,
                    'file_path': relative_path,
                    'content_type': analysis_result.content_type,
                    'domain': analysis_result.primary_domain,
                    'created_date': datetime.now().isoformat(),
                    'modified_date': datetime.now().isoformat(),
                    'confidence_score': analysis_result.confidence,
                    'source_type': source_type,
                    'word_count': analysis_result.word_count,
                    'character_count': analysis_result.character_count,
                    'content_hash': analysis_result.content_hash,
                    'frontmatter': {
                        'title': analysis_result.title,
                        'type': analysis_result.content_type,
                        'tags': analysis_result.tags
                    },
                    'tags': [{'tag': tag, 'tag_type': 'auto'} for tag in analysis_result.tags],
                    'relationships': []
                }
                
                note_id = self.database.add_note(note_data)
                
                # Add to vector search
                vector_data = note_data.copy()
                vector_data['id'] = note_id
                vector_data['content'] = content
                self.vector_search.add_note(vector_data)
                
                # Log the action
                self.database.log_processing_action({
                    'action': 'auto_create_note',
                    'source_path': 'manual_creation',
                    'destination_path': relative_path,
                    'confidence': analysis_result.confidence,
                    'reasoning': analysis_result.reasoning
                })
                
                logger.info(f"Created note: {analysis_result.title} at {relative_path}")
                
                return {
                    'success': True,
                    'note_id': note_id,
                    'title': analysis_result.title,
                    'file_path': relative_path,
                    'content_type': analysis_result.content_type,
                    'domain': analysis_result.primary_domain,
                    'confidence': analysis_result.confidence,
                    'tags': analysis_result.tags,
                    'destination_folder': analysis_result.destination_folder,
                    'reasoning': analysis_result.reasoning
                }
                
            except Exception as e:
                logger.error(f"Error creating note: {e}")
                return {
                    'success': False,
                    'error': str(e)
                }
        
        @self.server.tool("search_semantic")
        async def search_semantic(
            query: str,
            similarity_threshold: float = 0.7,
            content_types: Optional[List[str]] = None,
            domains: Optional[List[str]] = None,
            limit: int = 15
        ) -> List[Dict[str, Any]]:
            """
            Vector similarity search for concept exploration.
            Finds semantically similar content across vault.
            """
            try:
                filters = {}
                if content_types:
                    filters['content_types'] = content_types
                if domains:
                    filters['domains'] = domains
                
                results = self.vector_search.search_semantic(
                    query=query,
                    filters=filters,
                    limit=limit,
                    similarity_threshold=similarity_threshold
                )
                
                logger.info(f"Semantic search for '{query}' returned {len(results)} results")
                return results
                
            except Exception as e:
                logger.error(f"Error in semantic search: {e}")
                return []
        
        @self.server.tool("suggest_connections")
        async def suggest_connections(
            content: str,
            existing_domains: Optional[List[str]] = None,
            limit: int = 5
        ) -> List[Dict[str, Any]]:
            """
            Real-time connection discovery during conversation.
            Shows connections when creating/discussing content.
            """
            try:
                suggestions = self.vector_search.suggest_connections(
                    text_content=content,
                    existing_note_domains=existing_domains,
                    limit=limit,
                    similarity_threshold=0.7
                )
                
                logger.info(f"Generated {len(suggestions)} connection suggestions")
                return suggestions
                
            except Exception as e:
                logger.error(f"Error suggesting connections: {e}")
                return []
        
        @self.server.tool("get_inbox_items")
        async def get_inbox_items() -> List[Dict[str, Any]]:
            """
            Preview pending items in inbox with analysis preview.
            Shows preliminary analysis and confidence scores.
            """
            try:
                inbox_files = self.file_manager.get_inbox_files()
                
                # Add preliminary analysis to each file
                for file_info in inbox_files:
                    if file_info['content_body']:
                        analysis = self.content_analyzer.analyze_content(file_info['content_body'])
                        file_info['analysis_preview'] = {
                            'content_type': analysis.content_type,
                            'primary_domain': analysis.primary_domain,
                            'confidence': analysis.confidence,
                            'suggested_destination': analysis.destination_folder,
                            'tags': analysis.tags,
                            'reasoning': analysis.reasoning
                        }
                
                logger.info(f"Retrieved {len(inbox_files)} inbox items")
                return inbox_files
                
            except Exception as e:
                logger.error(f"Error getting inbox items: {e}")
                return []
        
        @self.server.tool("get_recent_insights")
        async def get_recent_insights(limit: int = 10) -> List[Dict[str, Any]]:
            """
            Get recent conversation insights with processing status.
            Shows what the AI has been detecting and processing.
            """
            try:
                insights = self.database.get_recent_insights(limit)
                logger.info(f"Retrieved {len(insights)} recent insights")
                return insights
                
            except Exception as e:
                logger.error(f"Error getting recent insights: {e}")
                return []
        
        @self.server.tool("search_exact")
        async def search_exact(
            query: str,
            folders: Optional[List[str]] = None,
            include_content: bool = True,
            limit: int = 20
        ) -> List[Dict[str, Any]]:
            """
            Traditional text search for specific terms.
            Supports exact phrase matching across vault content.
            """
            try:
                results = self.file_manager.search_files(
                    query=query,
                    folders=folders,
                    include_content=include_content
                )
                
                # Limit results
                results = results[:limit]
                
                logger.info(f"Exact search for '{query}' returned {len(results)} results")
                return results
                
            except Exception as e:
                logger.error(f"Error in exact search: {e}")
                return []
        
        @self.server.tool("get_vault_analytics")
        async def get_vault_analytics() -> Dict[str, Any]:
            """
            Provide insights about knowledge base growth and health.
            Shows content distribution, growth trends, and statistics.
            """
            try:
                stats = self.file_manager.get_vault_statistics()
                processing_stats = self.database.get_processing_stats(30)
                
                analytics = {
                    'vault_stats': stats,
                    'processing_stats': processing_stats,
                    'collection_info': self.vector_search.get_collection_info(),
                    'generated_at': datetime.now().isoformat()
                }
                
                logger.info("Generated vault analytics")
                return analytics
                
            except Exception as e:
                logger.error(f"Error generating analytics: {e}")
                return {}
        
        @self.server.tool("validate_inmpara_format")
        async def validate_inmpara_format(file_path: str) -> Dict[str, Any]:
            """
            Ensure notes follow INMPARA standards.
            Validates frontmatter, structure, and semantic markup.
            """
            try:
                # Get file content
                full_path = Path(self.vault_path) / file_path
                if not full_path.exists():
                    return {
                        'valid': False,
                        'errors': [f"File not found: {file_path}"]
                    }
                
                with open(full_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Validate format
                validation_result = self.template_engine.validate_inmpara_format(content)
                
                logger.info(f"Validated format for {file_path}: {'valid' if validation_result['valid'] else 'invalid'}")
                return validation_result
                
            except Exception as e:
                logger.error(f"Error validating format: {e}")
                return {
                    'valid': False,
                    'errors': [str(e)]
                }
        
        @self.server.tool("start_conversation_session")
        async def start_conversation_session() -> Dict[str, Any]:
            """
            Start a new conversation session for insight tracking.
            Returns session ID for context tracking across messages.
            """
            try:
                session_id = self.conversation_monitor.start_new_session()
                logger.info(f"Started new conversation session: {session_id}")
                
                return {
                    'session_id': session_id,
                    'started_at': datetime.now().isoformat(),
                    'auto_create_threshold': self.conversation_monitor.auto_create_threshold,
                    'suggestion_threshold': self.conversation_monitor.suggestion_threshold
                }
                
            except Exception as e:
                logger.error(f"Error starting session: {e}")
                return {
                    'error': str(e)
                }
    
    def _on_note_created(self, note_id: str, title: str, file_path: str):
        """Callback when a note is automatically created."""
        logger.info(f"Note created callback: {title} ({note_id})")
    
    def _on_suggestion_generated(self, suggestion: Dict[str, Any]):
        """Callback when a note creation suggestion is generated."""
        logger.info(f"Suggestion generated: {suggestion['title']}")
    
    async def run(self):
        """Run the MCP server."""
        await self.initialize()
        
        async with stdio_server() as (read_stream, write_stream):
            logger.info("INMPARA Notebook Server running via stdio")
            await self.server.run(
                read_stream=read_stream,
                write_stream=write_stream,
                initialization_options=InitializationOptions(
                    server_name="inmpara-notebook-server",
                    server_version="1.0.0"
                )
            )


async def main():
    """Main entry point."""
    server = INMPARANotebookServer()
    await server.run()


if __name__ == "__main__":
    asyncio.run(main())
