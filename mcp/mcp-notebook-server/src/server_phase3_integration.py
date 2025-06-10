"""
Phase 3 Server Integration
Complete integration of Phase 3 tools with MCP server
"""

import logging
from mcp.server import Server
from mcp.types import Resource, Tool

# Import Phase 3 components
from .phase3_tool_registrations import (
    register_phase3_tools,
    get_phase3_tool_definitions
)

logger = logging.getLogger(__name__)

def integrate_phase3_with_server(server: Server) -> None:
    """
    Integrate Phase 3 advanced automation and analytics features with MCP server.
    This adds the complete automation vision where users can dump content in inbox
    and trust AI processing with comprehensive analytics and quality improvement tools.
    """
    try:
        logger.info("Integrating Phase 3 advanced automation features...")
        
        # Register Phase 3 tools
        register_phase3_tools(server)
        
        logger.info("Phase 3 integration complete - Advanced automation features active")
        
    except Exception as e:
        logger.error(f"Error integrating Phase 3: {str(e)}")
        raise

def get_phase3_tools_list() -> list[Tool]:
    """Get list of all Phase 3 tools for server registration"""
    return get_phase3_tool_definitions()

def get_phase3_status() -> dict:
    """Get Phase 3 implementation status"""
    return {
        "phase": "Phase 3",
        "status": "Complete",
        "features": [
            "Complete inbox processing automation",
            "Bulk quality improvement reprocessing", 
            "Advanced analytics and reporting",
            "Knowledge graph visualization export",
            "MOC auto-generation from note clusters"
        ],
        "tools_count": len(get_phase3_tool_definitions()),
        "automation_level": "Full",
        "description": "Complete automation where users can dump content in inbox and trust AI processing with comprehensive analytics"
    }

