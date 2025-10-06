"""API routes module for FastAPI endpoints."""

from .projects import router as projects_router
from .tasks import router as tasks_router

__all__ = ["projects_router", "tasks_router"]
