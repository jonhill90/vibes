"""MCP tools for RAG service."""

from .document_tools import register_document_tools
from .search_tools import register_search_tools

__all__ = ["register_document_tools", "register_search_tools"]
