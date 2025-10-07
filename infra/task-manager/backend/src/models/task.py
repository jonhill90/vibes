"""Task Pydantic models for request/response validation."""

from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field, field_validator


# Type aliases for task enums
TaskStatus = Literal["todo", "doing", "review", "done"]
TaskPriority = Literal["low", "medium", "high", "urgent"]


class TaskCreate(BaseModel):
    """Request model for creating a task."""

    project_id: str | None = None
    title: str = Field(..., min_length=1, max_length=500)
    description: str | None = None
    status: TaskStatus = "todo"
    assignee: str = "User"
    priority: TaskPriority = "medium"
    position: int = 0

    @field_validator("title")
    @classmethod
    def title_not_empty(cls, v: str) -> str:
        """Validate that title is not empty or whitespace only."""
        if not v.strip():
            raise ValueError("Title cannot be empty or whitespace")
        return v.strip()


class TaskUpdate(BaseModel):
    """Request model for updating a task."""

    title: str | None = None
    description: str | None = None
    status: TaskStatus | None = None
    assignee: str | None = None
    priority: TaskPriority | None = None
    position: int | None = None

    @field_validator("title")
    @classmethod
    def title_not_empty(cls, v: str | None) -> str | None:
        """Validate that title is not empty or whitespace only if provided."""
        if v is not None and not v.strip():
            raise ValueError("Title cannot be empty or whitespace")
        return v.strip() if v is not None else None


class TaskResponse(BaseModel):
    """Response model for task data."""

    id: str
    project_id: str | None
    parent_task_id: str | None
    title: str
    description: str | None
    status: TaskStatus
    assignee: str
    priority: TaskPriority
    position: int
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}
