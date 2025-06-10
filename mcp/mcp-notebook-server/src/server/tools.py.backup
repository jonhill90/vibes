"""
INMPARA MCP Server Tool Registration

This module handles all MCP tool registrations and provides a clean interface
between the MCP protocol and the core business logic modules.

Target: ~200 lines - Tool registration and simple wrappers only
"""

import json
from typing import Any, Sequence
from mcp.types import Tool, TextContent

# Import core functionality from current locations
# These will be moved to core modules in later phases
from ..phase3_tools import (
    process_inbox_tool,
    bulk_reprocess_tool, 
    get_advanced_analytics_tool,
    export_knowledge_graph_tool,
    generate_moc_from_clusters_tool
)


def setup_mcp_tools(server, server_instance):
    """
    Register all MCP tools with the server instance.
    
    Args:
        server: The MCP server instance to register tools with
        server_instance: The INMPARAServer instance for component access
    """
    
    # ==== CORE MODULE TOOLS ====
    # These use the new core modules
    
    @server.call_tool()
    async def create_note(arguments: dict) -> Sequence[TextContent]:
        """Create a new note using the NotesManager."""
        try:
            notes_manager = server_instance.get_component('notes_manager')
            if not notes_manager:
                return [TextContent(type="text", text="Error: NotesManager not available")]
            
            result = await notes_manager.create_note(
                title=arguments.get("title", ""),
                content=arguments.get("content", ""),
                tags=arguments.get("tags", []),
                domain=arguments.get("domain"),
                note_type=arguments.get("note_type", "note"),
                source="mcp_tool"
            )
            
            return [TextContent(type="text", text=json.dumps(result, indent=2, default=str))]
            
        except Exception as e:
            return [TextContent(type="text", text=f"Error: {str(e)}")]
    
    @server.call_tool()
    async def search_vault(arguments: dict) -> Sequence[TextContent]:
        """Search the vault using the SearchManager."""
        try:
            search_manager = server_instance.get_component('search_manager')
            if not search_manager:
                return [TextContent(type="text", text="Error: SearchManager not available")]
            
            search_type = arguments.get("search_type", "semantic")
            query = arguments.get("query", "")
            
            if search_type == "semantic":
                result = await search_manager.search_semantic(
                    query=query,
                    limit=int(arguments.get("limit", 5)),
                    min_score=float(arguments.get("min_score", 0.5)),
                    domain_filter=arguments.get("domain_filter"),
                    content_type_filter=arguments.get("content_type_filter")
                )
            elif search_type == "exact":
                result = search_manager.search_exact(
                    query=query,
                    case_sensitive=arguments.get("case_sensitive", False),
                    whole_words=arguments.get("whole_words", False)
                )
            else:
                result = {"success": False, "error": f"Unknown search type: {search_type}"}
            
            return [TextContent(type="text", text=json.dumps(result, indent=2, default=str))]
            
        except Exception as e:
            return [TextContent(type="text", text=f"Error: {str(e)}")]
    
    @server.call_tool()
    async def process_inbox_new(arguments: dict) -> Sequence[TextContent]:
        """Process inbox using the new InboxManager."""
        try:
            inbox_manager = server_instance.get_component('inbox_manager')
            if not inbox_manager:
                return [TextContent(type="text", text="Error: InboxManager not available")]
            
            result = await inbox_manager.process_inbox(
                batch_size=int(arguments.get("batch_size", 10)),
                confidence_threshold=float(arguments.get("confidence_threshold", 0.7)),
                auto_approve=arguments.get("auto_approve", "false").lower() == "true"
            )
            
            return [TextContent(type="text", text=json.dumps(result, indent=2, default=str))]
            
        except Exception as e:
            return [TextContent(type="text", text=f"Error: {str(e)}")]
    
    @server.call_tool()
    async def get_analytics(arguments: dict) -> Sequence[TextContent]:
        """Get vault analytics using the AnalyticsManager."""
        try:
            analytics_manager = server_instance.get_component('analytics_manager')
            if not analytics_manager:
                return [TextContent(type="text", text="Error: AnalyticsManager not available")]
            
            result = await analytics_manager.generate_vault_analytics(
                include_patterns=arguments.get("include_patterns", "true").lower() == "true",
                include_trends=arguments.get("include_trends", "true").lower() == "true"
            )
            
            return [TextContent(type="text", text=json.dumps(result, indent=2, default=str))]
            
        except Exception as e:
            return [TextContent(type="text", text=f"Error: {str(e)}")]
    
    @server.call_tool()
    async def start_session(arguments: dict) -> Sequence[TextContent]:
        """Start a new session using the SessionsManager."""
        try:
            sessions_manager = server_instance.get_component('sessions_manager')
            if not sessions_manager:
                return [TextContent(type="text", text="Error: SessionsManager not available")]
            
            result = sessions_manager.start_session(
                session_type=arguments.get("session_type", "conversation"),
                initial_context=arguments.get("initial_context", {})
            )
            
            return [TextContent(type="text", text=json.dumps(result, indent=2, default=str))]
            
        except Exception as e:
            return [TextContent(type="text", text=f"Error: {str(e)}")]
    
    @server.call_tool()
    async def get_session_insights(arguments: dict) -> Sequence[TextContent]:
        """Get session insights using the SessionsManager."""
        try:
            sessions_manager = server_instance.get_component('sessions_manager')
            if not sessions_manager:
                return [TextContent(type="text", text="Error: SessionsManager not available")]
            
            result = sessions_manager.get_session_insights(
                session_id=arguments.get("session_id")
            )
            
            return [TextContent(type="text", text=json.dumps(result, indent=2, default=str))]
            
        except Exception as e:
            return [TextContent(type="text", text=f"Error: {str(e)}")]
    
    # ==== LEGACY COMPATIBILITY TOOLS ====
    # These maintain compatibility with existing functionality
    
    @server.call_tool()
    async def capture_conversation_insight(arguments: dict) -> Sequence[TextContent]:
        """Capture and store insights from conversation context."""
        try:
            insight = arguments.get("insight", "")
            context = arguments.get("context", "")
            
            if not insight.strip():
                return [TextContent(type="text", text="Error: Insight text is required")]
            
            # Use the new NotesManager for creating insight notes
            notes_manager = server_instance.get_component('notes_manager')
            if notes_manager:
                result = await notes_manager.create_note(
                    title=f"Conversation Insight: {insight[:50]}...",
                    content=f"**Insight:** {insight}\n\n**Context:** {context}",
                    tags=['conversation', 'insight'],
                    domain='AI',
                    source='conversation_capture'
                )
            else:
                # Fallback to legacy approach
                note_data = {
                    'title': f"Conversation Insight: {insight[:50]}...",
                    'content': f"**Insight:** {insight}\n\n**Context:** {context}",
                    'tags': ['conversation', 'insight'],
                    'domain': 'AI',
                    'source': 'conversation_capture',
                    'created_at': str(__import__('datetime').datetime.now())
                }
                
                note_id = server_instance.database.add_note(note_data)
                result = {
                    "success": True,
                    "note_id": note_id,
                    "insight": insight,
                    "message": "Insight captured successfully"
                }
            
            return [TextContent(type="text", text=json.dumps(result, indent=2, default=str))]
            
        except Exception as e:
            return [TextContent(type="text", text=f"Error: {str(e)}")]

    # ==== LEGACY PHASE 3 TOOLS ====
    # These use the existing extracted functions for backward compatibility
    
    @server.call_tool()
    async def process_inbox(arguments: dict) -> Sequence[TextContent]:
        """Process inbox items with learned patterns and automation (legacy)."""
        try:
            result = await process_inbox_tool(
                vault_path=arguments.get("vault_path", server_instance.get_vault_path()),
                batch_size=int(arguments.get("batch_size", 10)),
                confidence_threshold=float(arguments.get("confidence_threshold", 0.7)),
                auto_approve=arguments.get("auto_approve", "false").lower() == "true"
            )
            return [TextContent(type="text", text=json.dumps(result, indent=2, default=str))]
        except Exception as e:
            return [TextContent(type="text", text=f"Error: {str(e)}")]

    @server.call_tool()
    async def get_advanced_analytics(arguments: dict) -> Sequence[TextContent]:
        """Get comprehensive vault analytics and insights (legacy)."""
        try:
            result = await get_advanced_analytics_tool(
                vault_path=arguments.get("vault_path", server_instance.get_vault_path()),
                include_patterns=arguments.get("include_patterns", "true").lower() == "true",
                include_trends=arguments.get("include_trends", "true").lower() == "true"
            )
            return [TextContent(type="text", text=json.dumps(result, indent=2, default=str))]
        except Exception as e:
            return [TextContent(type="text", text=f"Error: {str(e)}")]

    @server.call_tool()
    async def export_knowledge_graph(arguments: dict) -> Sequence[TextContent]:
        """Export vault as knowledge graph in various formats (legacy)."""
        try:
            result = await export_knowledge_graph_tool(
                vault_path=arguments.get("vault_path", server_instance.get_vault_path()),
                format=arguments.get("format", "json"),
                include_metadata=arguments.get("include_metadata", "true").lower() == "true",
                output_path=arguments.get("output_path")
            )
            return [TextContent(type="text", text=json.dumps(result, indent=2, default=str))]
        except Exception as e:
            return [TextContent(type="text", text=f"Error: {str(e)}")]
