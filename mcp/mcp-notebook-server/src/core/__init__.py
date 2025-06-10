"""INMPARA Core Modules Package

This package contains the core business logic modules for the INMPARA system.
Each module is focused on a specific aspect of intelligent note-taking.
"""

# Direct imports without relative references
try:
    from notes import NotesManager
    from search import SearchManager  
    from inbox import InboxManager
    from analytics import AnalyticsManager
    from learning import LearningManager
    from sessions import SessionsManager
except ImportError:
    # If direct imports fail, try with package prefix
    from core.notes import NotesManager
    from core.search import SearchManager  
    from core.inbox import InboxManager
    from core.analytics import AnalyticsManager
    from core.learning import LearningManager
    from core.sessions import SessionsManager

__all__ = [
    'NotesManager',
    'SearchManager', 
    'InboxManager',
    'AnalyticsManager',
    'LearningManager', 
    'SessionsManager'
]
