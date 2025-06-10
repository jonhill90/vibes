"""
INMPARA Core Business Logic Modules

This package contains the core business logic modules for the INMPARA system,
separated from MCP protocol concerns for better maintainability and testing.
"""

# Export main classes for easy importing
from .notes import NotesManager
from .search import SearchManager  
from .inbox import InboxManager
from .analytics import AnalyticsManager
from .learning import LearningManager
from .sessions import SessionsManager

__all__ = [
    'NotesManager',
    'SearchManager', 
    'InboxManager',
    'AnalyticsManager',
    'LearningManager',
    'SessionsManager'
]
