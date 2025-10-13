# Source: /Users/jon/source/vibes/repos/DesktopCommanderMCP/src/terminal-manager.ts
# Lines: 225-245 (forceTerminate function)
# Pattern: Graceful process cleanup and session management
# Extracted: 2025-10-13
# Relevance: 9/10 - Critical for preventing resource leaks

"""Process Cleanup Pattern

This demonstrates proper process cleanup and session management patterns
from DesktopCommanderMCP, adapted to Python/asyncio.

CRITICAL PATTERNS:
1. Two-stage termination (SIGTERM -> wait -> SIGKILL)
2. Session tracking with completion history
3. Cleanup of orphaned processes
4. Limit completed session history (prevent memory leaks)
"""

import asyncio
import signal
import os
from typing import Dict, Optional
from datetime import datetime
from dataclasses import dataclass


@dataclass
class ProcessSession:
    """Active process session"""
    pid: int
    command: str
    process: asyncio.subprocess.Process
    started_at: datetime
    output_buffer: str = ""


@dataclass
class CompletedSession:
    """Completed process session"""
    pid: int
    command: str
    exit_code: int
    started_at: datetime
    ended_at: datetime
    output: str


class ProcessCleanupManager:
    """Manage process lifecycle with proper cleanup.

    PATTERN FROM: DesktopCommanderMCP terminal-manager.ts
    - Track active sessions
    - Track completed sessions (limited history)
    - Graceful termination with fallback to force kill
    - Automatic cleanup on exit
    """

    def __init__(self, max_completed_sessions: int = 100):
        self.active_sessions: Dict[int, ProcessSession] = {}
        self.completed_sessions: Dict[int, CompletedSession] = {}
        self.max_completed_sessions = max_completed_sessions

    async def start_process(
        self,
        command: str,
        shell: str = "/bin/sh"
    ) -> int:
        """Start a process and track it.

        Returns:
            Process PID
        """
        process = await asyncio.create_subprocess_shell(
            command,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
            shell=True,
            executable=shell
        )

        if not process.pid:
            raise RuntimeError("Failed to get process ID")

        session = ProcessSession(
            pid=process.pid,
            command=command,
            process=process,
            started_at=datetime.now()
        )

        self.active_sessions[process.pid] = session

        # Track completion in background
        asyncio.create_task(self._track_completion(session))

        return process.pid

    async def _track_completion(self, session: ProcessSession):
        """Background task to track process completion.

        PATTERN: Move completed sessions from active to completed dict
        Keep limited history to prevent memory leaks.
        """
        # Wait for process to complete
        await session.process.wait()

        # Create completed session record
        completed = CompletedSession(
            pid=session.pid,
            command=session.command,
            exit_code=session.process.returncode or 0,
            started_at=session.started_at,
            ended_at=datetime.now(),
            output=session.output_buffer
        )

        # Move from active to completed
        if session.pid in self.active_sessions:
            del self.active_sessions[session.pid]

        self.completed_sessions[session.pid] = completed

        # PATTERN: Keep only last N completed sessions (from DesktopCommanderMCP)
        if len(self.completed_sessions) > self.max_completed_sessions:
            oldest_pid = next(iter(self.completed_sessions))
            del self.completed_sessions[oldest_pid]

    async def terminate_process(self, pid: int) -> bool:
        """Terminate a process gracefully with force-kill fallback.

        PATTERN FROM: DesktopCommanderMCP terminal-manager.ts forceTerminate()
        Two-stage termination:
        1. Send SIGTERM (graceful shutdown)
        2. Wait 1 second
        3. Send SIGKILL if still running (forceful)

        Args:
            pid: Process ID to terminate

        Returns:
            True if terminated, False if not found
        """
        session = self.active_sessions.get(pid)
        if not session:
            return False

        try:
            # Stage 1: Try graceful termination (SIGINT/SIGTERM)
            # SIGINT is better for interactive processes
            session.process.send_signal(signal.SIGINT)

            # Wait up to 1 second for graceful shutdown
            try:
                await asyncio.wait_for(session.process.wait(), timeout=1.0)
                return True
            except asyncio.TimeoutError:
                # Stage 2: Force kill if still running
                session.process.kill()  # SIGKILL
                await session.process.wait()
                return True

        except ProcessLookupError:
            # Process already terminated
            return False
        except Exception as e:
            # Log error but don't crash
            print(f"Error terminating process {pid}: {e}")
            return False

    def list_active(self) -> list[dict]:
        """List all active processes with runtime info"""
        now = datetime.now()
        return [
            {
                "pid": session.pid,
                "command": session.command,
                "started_at": session.started_at.isoformat(),
                "runtime_seconds": (now - session.started_at).total_seconds()
            }
            for session in self.active_sessions.values()
        ]

    def list_completed(self) -> list[dict]:
        """List recently completed processes"""
        return [
            {
                "pid": session.pid,
                "command": session.command,
                "exit_code": session.exit_code,
                "started_at": session.started_at.isoformat(),
                "ended_at": session.ended_at.isoformat(),
                "duration_seconds": (session.ended_at - session.started_at).total_seconds()
            }
            for session in self.completed_sessions.values()
        ]

    def get_session_output(self, pid: int) -> Optional[str]:
        """Get output for active or completed session"""
        # Check active first
        if pid in self.active_sessions:
            return self.active_sessions[pid].output_buffer

        # Then check completed
        if pid in self.completed_sessions:
            return self.completed_sessions[pid].output

        return None

    async def cleanup_all(self):
        """Clean up all active processes on shutdown.

        CRITICAL: Call this on server shutdown to prevent orphaned processes.
        """
        pids = list(self.active_sessions.keys())
        for pid in pids:
            await self.terminate_process(pid)


# ============================================================================
# INTEGRATION WITH MCP SERVER
# ============================================================================
# How to integrate this with FastMCP tools:

"""
# In mcp_server.py:

from process_cleanup_pattern import ProcessCleanupManager

# Global process manager
process_manager = ProcessCleanupManager()

@mcp.tool()
async def execute_command(command: str, shell: str = "/bin/sh") -> str:
    try:
        pid = await process_manager.start_process(command, shell)
        return json.dumps({
            "success": True,
            "pid": pid,
            "message": "Command started"
        })
    except Exception as e:
        return json.dumps({
            "success": False,
            "error": str(e)
        })

@mcp.tool()
async def list_processes() -> str:
    active = process_manager.list_active()
    completed = process_manager.list_completed()
    return json.dumps({
        "success": True,
        "active": active,
        "completed": completed
    })

@mcp.tool()
async def kill_process(pid: int) -> str:
    success = await process_manager.terminate_process(pid)
    if success:
        return json.dumps({
            "success": True,
            "message": f"Process {pid} terminated"
        })
    else:
        return json.dumps({
            "success": False,
            "error": f"Process {pid} not found"
        })

# CRITICAL: Cleanup on shutdown
@mcp.on_shutdown()
async def cleanup():
    await process_manager.cleanup_all()
"""


# ============================================================================
# EXAMPLE USAGE
# ============================================================================
if __name__ == "__main__":
    async def main():
        manager = ProcessCleanupManager()

        # Start a long-running process
        pid = await manager.start_process("sleep 10")
        print(f"Started process {pid}")

        # List active processes
        print("Active processes:", manager.list_active())

        # Wait a bit
        await asyncio.sleep(2)

        # Terminate it
        success = await manager.terminate_process(pid)
        print(f"Terminated: {success}")

        # List completed
        print("Completed processes:", manager.list_completed())

        # Cleanup all
        await manager.cleanup_all()

    asyncio.run(main())
