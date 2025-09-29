"""
Configuration module for Archon

This module provides configuration management and service discovery
for the Archon microservices architecture.
"""

from .service_discovery import (
    Environment,
    ServiceDiscovery,
    discovery,
    get_agents_url,
    get_api_url,
    get_mcp_url,
    is_service_healthy,
)

__all__ = [
    "ServiceDiscovery",
    "Environment",
    "discovery",
    "get_api_url",
    "get_mcp_url",
    "get_agents_url",
    "is_service_healthy",
]
