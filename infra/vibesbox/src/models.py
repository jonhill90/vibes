"""
Data models for Vibesbox MCP server.

Pydantic models for type-safe request/response handling.
Pattern from: Pydantic v2 BaseModel with field validators.
"""

from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field, field_validator


class CommandRequest(BaseModel):
    """Request model for command execution.

    Attributes:
        command: Shell command to execute (required)
        shell: Shell interpreter to use (default: /bin/sh)
        timeout: Maximum execution time in seconds (range: 1-300)
        stream: Whether to stream output line-by-line (default: True)
    """

    command: str = Field(
        ...,
        min_length=1,
        max_length=10000,
        description="Shell command to execute"
    )
    shell: str = Field(
        default="/bin/sh",
        description="Shell interpreter path"
    )
    timeout: int = Field(
        default=30,
        ge=1,
        le=300,
        description="Command timeout in seconds (1-300)"
    )
    stream: bool = Field(
        default=True,
        description="Stream output line-by-line"
    )

    @field_validator('command')
    @classmethod
    def validate_command_not_empty(cls, v: str) -> str:
        """Validate command is not empty or whitespace-only."""
        if not v or not v.strip():
            raise ValueError("Command cannot be empty or whitespace-only")
        return v.strip()

    @field_validator('shell')
    @classmethod
    def validate_shell_path(cls, v: str) -> str:
        """Validate shell path is reasonable."""
        if not v or not v.strip():
            raise ValueError("Shell path cannot be empty")
        return v.strip()


class CommandResult(BaseModel):
    """Result model for command execution.

    Attributes:
        success: Whether the command completed successfully
        exit_code: Process exit code (None if terminated or error)
        stdout: Standard output from command
        stderr: Standard error from command
        truncated: Whether output was truncated
        error: Error message if command failed (None on success)
    """

    success: bool = Field(
        ...,
        description="Whether command completed successfully"
    )
    exit_code: int | None = Field(
        default=None,
        description="Process exit code (None if error/timeout)"
    )
    stdout: str = Field(
        default="",
        description="Standard output from command"
    )
    stderr: str = Field(
        default="",
        description="Standard error from command"
    )
    truncated: bool = Field(
        default=False,
        description="Whether output was truncated (>100 lines)"
    )
    error: str | None = Field(
        default=None,
        description="Error message if command failed"
    )


class SessionInfo(BaseModel):
    """Information about a command execution session.

    Attributes:
        pid: Process ID of the running command
        command: Original command that was executed
        started_at: Timestamp when the process started
        status: Current status of the process
    """

    pid: int = Field(
        ...,
        gt=0,
        description="Process ID (PID)"
    )
    command: str = Field(
        ...,
        min_length=1,
        description="Command being executed"
    )
    started_at: datetime = Field(
        ...,
        description="Process start timestamp"
    )
    status: Literal["running", "completed", "terminated"] = Field(
        ...,
        description="Current process status"
    )

    @field_validator('command')
    @classmethod
    def validate_command_not_empty(cls, v: str) -> str:
        """Validate command is not empty."""
        if not v or not v.strip():
            raise ValueError("Command cannot be empty")
        return v.strip()
