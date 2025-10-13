"""Session Manager for Vibesbox MCP server.

Manages long-running process sessions with proper cleanup and zombie prevention.
Pattern from: prps/streamlined_vibesbox/examples/process_cleanup_pattern.py
"""

import asyncio
import signal
import time
import uuid
from collections import OrderedDict
from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional

from src.models import SessionInfo


@dataclass
class CommandSession:
    """Active command session tracking.

    Attributes:
        session_id: Unique session identifier (UUID)
        command: Original command string that was executed
        process: asyncio subprocess Process object
        started_at: Unix timestamp when process started (time.time())
        output_buffer: List of output lines for incremental reading
    """
    session_id: str
    command: str
    process: asyncio.subprocess.Process
    started_at: float
    output_buffer: list[str] = field(default_factory=list)

    @property
    def pid(self) -> int:
        """Get process ID."""
        if not self.process.pid:
            raise RuntimeError("Process has no PID")
        return self.process.pid

    @property
    def is_running(self) -> bool:
        """Check if process is still running."""
        return self.process.returncode is None


class SessionManager:
    """Manage command execution sessions with proper cleanup.

    PATTERN FROM: examples/process_cleanup_pattern.py
    - Track active sessions by PID
    - Track completed sessions (limited to 100 most recent)
    - Graceful termination (SIGTERM -> SIGKILL)
    - Automatic zombie process reaping
    - Background task to move completed sessions

    CRITICAL GOTCHA: Must await process.wait() to prevent zombies
    """

    def __init__(self, max_completed_sessions: int = 100):
        """Initialize session manager.

        Args:
            max_completed_sessions: Maximum number of completed sessions to keep
                                   in history (prevents memory leaks)
        """
        self.sessions: dict[int, CommandSession] = {}
        # Using OrderedDict to maintain insertion order for cleanup
        self.completed: OrderedDict[int, CommandSession] = OrderedDict()
        self.max_completed_sessions = max_completed_sessions
        self._cleanup_tasks: set[asyncio.Task] = set()

    async def start_session(
        self,
        command: str,
        shell: str = "/bin/sh"
    ) -> int:
        """Start a new command execution session.

        Creates subprocess and tracks it in active sessions.
        Automatically sets up background task to track completion.

        Args:
            command: Shell command to execute
            shell: Shell interpreter to use (default: /bin/sh)

        Returns:
            Process PID

        Raises:
            RuntimeError: If process creation fails or no PID available
        """
        # Create subprocess with pipes for output capture
        process = await asyncio.create_subprocess_shell(
            command,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
            shell=True,
            executable=shell
        )

        if not process.pid:
            raise RuntimeError("Failed to create process with valid PID")

        # Create session tracking object
        session = CommandSession(
            session_id=str(uuid.uuid4()),
            command=command,
            process=process,
            started_at=time.time()
        )

        # Track in active sessions
        self.sessions[process.pid] = session

        # Set up background reaping task
        # PATTERN: Move to completed dict when process finishes
        task = asyncio.create_task(self._track_completion(session))
        self._cleanup_tasks.add(task)
        task.add_done_callback(self._cleanup_tasks.discard)

        return process.pid

    async def _track_completion(self, session: CommandSession):
        """Background task to track process completion and prevent zombies.

        CRITICAL PATTERN FROM: process_cleanup_pattern.py
        - Wait for process to complete
        - Move from active to completed dict
        - Limit completed dict size to prevent memory leaks
        - This prevents zombie processes by calling wait()

        Args:
            session: CommandSession to track
        """
        try:
            # Wait for process completion (prevents zombies)
            await session.process.wait()

            pid = session.pid

            # Move from active to completed
            if pid in self.sessions:
                del self.sessions[pid]

            # Add to completed history
            self.completed[pid] = session

            # PATTERN: Limit completed history size
            # Keep only last max_completed_sessions
            while len(self.completed) > self.max_completed_sessions:
                # Remove oldest entry (first in OrderedDict)
                oldest_pid = next(iter(self.completed))
                del self.completed[oldest_pid]

        except Exception as e:
            # Log error but don't crash background task
            print(f"Error tracking completion for session {session.session_id}: {e}")

    def get_session(self, pid: int) -> Optional[CommandSession]:
        """Get session by PID (active or completed).

        Args:
            pid: Process ID to look up

        Returns:
            CommandSession if found in active or completed, None otherwise
        """
        # Check active sessions first
        if pid in self.sessions:
            return self.sessions[pid]

        # Check completed sessions
        if pid in self.completed:
            return self.completed[pid]

        return None

    async def read_output(self, pid: int) -> str:
        """Read new output from session since last read.

        Returns incremental output - only lines produced since last call.
        Output is consumed from buffer after reading.

        Args:
            pid: Process ID to read from

        Returns:
            New output as string, or empty string if no new output

        Raises:
            ValueError: If session not found
        """
        session = self.get_session(pid)
        if not session:
            raise ValueError(f"Session with PID {pid} not found")

        # If process is still running and has stdout, try to read new lines
        if session.is_running and session.process.stdout:
            try:
                # Non-blocking read of available output
                while True:
                    try:
                        # Try to read line without blocking
                        line = await asyncio.wait_for(
                            session.process.stdout.readline(),
                            timeout=0.1
                        )
                        if not line:
                            break
                        session.output_buffer.append(
                            line.decode('utf-8', errors='replace')
                        )
                    except asyncio.TimeoutError:
                        # No more lines available
                        break
            except Exception as e:
                print(f"Error reading output for PID {pid}: {e}")

        # Return all buffered output and clear buffer
        output = "".join(session.output_buffer)
        session.output_buffer.clear()

        return output

    async def terminate_session(
        self,
        pid: int,
        force: bool = False
    ) -> bool:
        """Terminate a session gracefully or forcefully.

        PATTERN FROM: process_cleanup_pattern.py forceTerminate()
        Two-stage termination:
        1. Send SIGTERM (graceful) or SIGINT
        2. Wait 1 second for process to exit
        3. If still running, send SIGKILL (force)
        4. Always wait() to reap the process (prevent zombies)

        Args:
            pid: Process ID to terminate
            force: If True, immediately use SIGKILL. If False, try graceful first.

        Returns:
            True if session was found and terminated, False if not found
        """
        session = self.sessions.get(pid)
        if not session:
            # Not in active sessions
            return False

        try:
            if force:
                # Immediate SIGKILL
                session.process.kill()
                await session.process.wait()
                return True

            # Stage 1: Try graceful termination
            # SIGINT is better for interactive processes
            try:
                session.process.send_signal(signal.SIGINT)
            except ProcessLookupError:
                # Process already gone
                return False

            # Wait up to 1 second for graceful shutdown
            try:
                await asyncio.wait_for(session.process.wait(), timeout=1.0)
                return True
            except asyncio.TimeoutError:
                # Stage 2: Force kill if still running
                session.process.kill()  # SIGKILL
                await session.process.wait()  # Reap the process
                return True

        except ProcessLookupError:
            # Process already terminated
            return False
        except Exception as e:
            # Log error but don't crash
            print(f"Error terminating session {pid}: {e}")
            return False

    def list_sessions(self) -> list[SessionInfo]:
        """List all active and recently completed sessions.

        Returns:
            List of SessionInfo objects with session details
        """
        sessions_info = []

        # Add active sessions
        for session in self.sessions.values():
            sessions_info.append(SessionInfo(
                pid=session.pid,
                command=session.command,
                started_at=datetime.fromtimestamp(session.started_at),
                status="running"
            ))

        # Add completed sessions
        for session in self.completed.values():
            sessions_info.append(SessionInfo(
                pid=session.pid,
                command=session.command,
                started_at=datetime.fromtimestamp(session.started_at),
                status="completed"
            ))

        return sessions_info

    async def cleanup_all(self) -> None:
        """Clean up all active sessions on shutdown.

        CRITICAL: Call this on server shutdown to prevent orphaned processes.
        Terminates all active sessions gracefully.

        Pattern from: process_cleanup_pattern.py
        """
        # Get list of PIDs to avoid dict modification during iteration
        pids = list(self.sessions.keys())

        for pid in pids:
            await self.terminate_session(pid, force=False)

        # Wait for all cleanup tasks to complete
        if self._cleanup_tasks:
            await asyncio.gather(*self._cleanup_tasks, return_exceptions=True)
