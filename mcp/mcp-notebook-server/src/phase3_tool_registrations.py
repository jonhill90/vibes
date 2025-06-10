"""
Phase 3 Tool Registrations
MCP tool registrations for Phase 3 advanced automation and analytics features
"""

import json
from typing import Any, Sequence
from mcp.types import Tool, TextContent

# Import Phase 3 tools
from .phase3_tools import (
    process_inbox_tool,
    bulk_reprocess_tool, 
    get_advanced_analytics_tool,
    export_knowledge_graph_tool,
    generate_moc_from_clusters_tool
)

def register_phase3_tools(server) -> None:
    """Register all Phase 3 MCP tools with the server"""
    
    @server.call_tool()
    async def process_inbox(arguments: dict) -> Sequence[TextContent]:
        """
        Complete batch processing pipeline for 0 - Inbox folder.
        Processes all inbox items with learned patterns and high-confidence automation.
        
        Args:
            vault_path (str): Path to INMPARA vault (default: /workspace/vibes/repos/inmpara)
            batch_size (int): Number of items to process in one batch (default: 10)
            confidence_threshold (float): Minimum confidence for auto-processing (default: 0.7)
            auto_approve (bool): Whether to automatically approve high-confidence decisions (default: false)
        """
        try:
            vault_path = arguments.get("vault_path", "/workspace/vibes/repos/inmpara")
            batch_size = int(arguments.get("batch_size", 10))
            confidence_threshold = float(arguments.get("confidence_threshold", 0.7))
            auto_approve = arguments.get("auto_approve", "false").lower() == "true"
            
            result = await process_inbox_tool(
                vault_path=vault_path,
                batch_size=batch_size,
                confidence_threshold=confidence_threshold,
                auto_approve=auto_approve
            )
            
            return [TextContent(
                type="text",
                text=json.dumps(result, indent=2, default=str)
            )]
            
        except Exception as e:
            return [TextContent(
                type="text", 
                text=json.dumps({
                    "success": False,
                    "error": str(e),
                    "message": "Failed to process inbox"
                }, indent=2)
            )]
    
    @server.call_tool()
    async def bulk_reprocess(arguments: dict) -> Sequence[TextContent]:
        """
        Quality improvement tools using learned patterns to reprocess existing notes.
        Uses learned patterns to improve confidence scores and suggestions for existing content.
        
        Args:
            vault_path (str): Path to INMPARA vault (default: /workspace/vibes/repos/inmpara)
            target_folder (str): Folder to reprocess (default: "1 - Notes")
            reprocess_count (int): Maximum number of notes to reprocess (default: 20)
            min_confidence_improvement (float): Minimum improvement needed to suggest changes (default: 0.1)
        """
        try:
            vault_path = arguments.get("vault_path", "/workspace/vibes/repos/inmpara")
            target_folder = arguments.get("target_folder", "1 - Notes")
            reprocess_count = int(arguments.get("reprocess_count", 20))
            min_confidence_improvement = float(arguments.get("min_confidence_improvement", 0.1))
            
            result = await bulk_reprocess_tool(
                vault_path=vault_path,
                target_folder=target_folder,
                reprocess_count=reprocess_count,
                min_confidence_improvement=min_confidence_improvement
            )
            
            return [TextContent(
                type="text",
                text=json.dumps(result, indent=2, default=str)
            )]
            
        except Exception as e:
            return [TextContent(
                type="text",
                text=json.dumps({
                    "success": False,
                    "error": str(e),
                    "message": "Failed to bulk reprocess files"
                }, indent=2)
            )]
    
    @server.call_tool()
    async def get_advanced_analytics(arguments: dict) -> Sequence[TextContent]:
        """
        Advanced analytics and reporting on vault usage, AI decisions, and learning patterns.
        
        Args:
            vault_path (str): Path to INMPARA vault (default: /workspace/vibes/repos/inmpara)
            days_back (int): Number of days to analyze (default: 30)
        """
        try:
            vault_path = arguments.get("vault_path", "/workspace/vibes/repos/inmpara")
            days_back = int(arguments.get("days_back", 30))
            
            result = await get_advanced_analytics_tool(
                vault_path=vault_path,
                days_back=days_back
            )
            
            return [TextContent(
                type="text",
                text=json.dumps(result, indent=2, default=str)
            )]
            
        except Exception as e:
            return [TextContent(
                type="text",
                text=json.dumps({
                    "success": False,
                    "error": str(e),
                    "message": "Failed to generate advanced analytics"
                }, indent=2)
            )]
    
    @server.call_tool()
    async def export_knowledge_graph(arguments: dict) -> Sequence[TextContent]:
        """
        Knowledge graph visualization export capabilities.
        
        Args:
            vault_path (str): Path to INMPARA vault (default: /workspace/vibes/repos/inmpara)
            format (str): Export format - json, graphml, or cypher (default: json)
            include_content (bool): Whether to include full content or just metadata (default: false)
        """
        try:
            vault_path = arguments.get("vault_path", "/workspace/vibes/repos/inmpara")
            format = arguments.get("format", "json")
            include_content = arguments.get("include_content", "false").lower() == "true"
            
            result = await export_knowledge_graph_tool(
                vault_path=vault_path,
                format=format,
                include_content=include_content
            )
            
            return [TextContent(
                type="text",
                text=json.dumps(result, indent=2, default=str)
            )]
            
        except Exception as e:
            return [TextContent(
                type="text",
                text=json.dumps({
                    "success": False,
                    "error": str(e),
                    "message": "Failed to export knowledge graph"
                }, indent=2)
            )]
    
    @server.call_tool()
    async def generate_moc_from_clusters(arguments: dict) -> Sequence[TextContent]:
        """
        MOC auto-generation from note clusters using content similarity and learned patterns.
        
        Args:
            vault_path (str): Path to INMPARA vault (default: /workspace/vibes/repos/inmpara)
            min_cluster_size (int): Minimum notes required to create a MOC (default: 3)
            similarity_threshold (float): Minimum similarity for clustering (default: 0.7)
            target_clusters (int): Target number of clusters to generate (default: 5)
        """
        try:
            vault_path = arguments.get("vault_path", "/workspace/vibes/repos/inmpara")
            min_cluster_size = int(arguments.get("min_cluster_size", 3))
            similarity_threshold = float(arguments.get("similarity_threshold", 0.7))
            target_clusters = int(arguments.get("target_clusters", 5))
            
            result = await generate_moc_from_clusters_tool(
                vault_path=vault_path,
                min_cluster_size=min_cluster_size,
                similarity_threshold=similarity_threshold,
                target_clusters=target_clusters
            )
            
            return [TextContent(
                type="text",
                text=json.dumps(result, indent=2, default=str)
            )]
            
        except Exception as e:
            return [TextContent(
                type="text",
                text=json.dumps({
                    "success": False,
                    "error": str(e),
                    "message": "Failed to generate MOCs from clusters"
                }, indent=2)
            )]

def get_phase3_tool_definitions() -> list[Tool]:
    """Get tool definitions for Phase 3 tools"""
    return [
        Tool(
            name="process_inbox",
            description="Complete batch processing pipeline for 0 - Inbox folder with learned patterns and high-confidence automation",
            inputSchema={
                "type": "object",
                "properties": {
                    "vault_path": {
                        "type": "string",
                        "description": "Path to INMPARA vault",
                        "default": "/workspace/vibes/repos/inmpara"
                    },
                    "batch_size": {
                        "type": "integer", 
                        "description": "Number of items to process in one batch",
                        "default": 10,
                        "minimum": 1,
                        "maximum": 50
                    },
                    "confidence_threshold": {
                        "type": "number",
                        "description": "Minimum confidence for auto-processing",
                        "default": 0.7,
                        "minimum": 0.0,
                        "maximum": 1.0
                    },
                    "auto_approve": {
                        "type": "boolean",
                        "description": "Whether to automatically approve high-confidence decisions",
                        "default": False
                    }
                }
            }
        ),
        Tool(
            name="bulk_reprocess", 
            description="Quality improvement tools using learned patterns to reprocess existing notes",
            inputSchema={
                "type": "object",
                "properties": {
                    "vault_path": {
                        "type": "string",
                        "description": "Path to INMPARA vault",
                        "default": "/workspace/vibes/repos/inmpara"
                    },
                    "target_folder": {
                        "type": "string",
                        "description": "Folder to reprocess",
                        "default": "1 - Notes",
                        "enum": ["1 - Notes", "2 - MOCs", "3 - Projects", "4 - Areas", "5 - Resources"]
                    },
                    "reprocess_count": {
                        "type": "integer",
                        "description": "Maximum number of notes to reprocess", 
                        "default": 20,
                        "minimum": 1,
                        "maximum": 100
                    },
                    "min_confidence_improvement": {
                        "type": "number",
                        "description": "Minimum improvement needed to suggest changes",
                        "default": 0.1,
                        "minimum": 0.01,
                        "maximum": 0.5
                    }
                }
            }
        ),
        Tool(
            name="get_advanced_analytics",
            description="Advanced analytics and reporting on vault usage, AI decisions, and learning patterns",
            inputSchema={
                "type": "object", 
                "properties": {
                    "vault_path": {
                        "type": "string",
                        "description": "Path to INMPARA vault",
                        "default": "/workspace/vibes/repos/inmpara"
                    },
                    "days_back": {
                        "type": "integer",
                        "description": "Number of days to analyze",
                        "default": 30,
                        "minimum": 1,
                        "maximum": 365
                    }
                }
            }
        ),
        Tool(
            name="export_knowledge_graph",
            description="Knowledge graph visualization export capabilities",
            inputSchema={
                "type": "object",
                "properties": {
                    "vault_path": {
                        "type": "string", 
                        "description": "Path to INMPARA vault",
                        "default": "/workspace/vibes/repos/inmpara"
                    },
                    "format": {
                        "type": "string",
                        "description": "Export format",
                        "enum": ["json", "graphml", "cypher"],
                        "default": "json"
                    },
                    "include_content": {
                        "type": "boolean",
                        "description": "Whether to include full content or just metadata",
                        "default": False
                    }
                }
            }
        ),
        Tool(
            name="generate_moc_from_clusters",
            description="MOC auto-generation from note clusters using content similarity and learned patterns",
            inputSchema={
                "type": "object",
                "properties": {
                    "vault_path": {
                        "type": "string",
                        "description": "Path to INMPARA vault", 
                        "default": "/workspace/vibes/repos/inmpara"
                    },
                    "min_cluster_size": {
                        "type": "integer",
                        "description": "Minimum notes required to create a MOC",
                        "default": 3,
                        "minimum": 2,
                        "maximum": 20
                    },
                    "similarity_threshold": {
                        "type": "number",
                        "description": "Minimum similarity for clustering",
                        "default": 0.7,
                        "minimum": 0.1,
                        "maximum": 1.0
                    },
                    "target_clusters": {
                        "type": "integer",
                        "description": "Target number of clusters to generate",
                        "default": 5,
                        "minimum": 1,
                        "maximum": 20
                    }
                }
            }
        )
    ]

