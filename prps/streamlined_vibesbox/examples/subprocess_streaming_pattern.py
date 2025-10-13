# Source: Python asyncio subprocess best practices + DesktopCommanderMCP patterns
# Pattern: Async subprocess execution with streaming output
# Extracted: 2025-10-13
# Relevance: 9/10 - Core pattern needed for command execution

"""Async Subprocess Streaming Pattern

This demonstrates how to execute commands asynchronously with streaming
output handling. Adapted from Python asyncio best practices and
DesktopCommanderMCP's approach.

KEY PATTERNS:
1. Use asyncio.create_subprocess_shell for async execution
2. Stream stdout/stderr as they arrive (don't wait for completion)
3. Handle timeouts gracefully
4. Track process state and cleanup
5. Graceful termination (SIGTERM -> SIGKILL)
"""

import asyncio
import signal
from typing import AsyncIterator
from datetime import datetime


class ProcessSession:
    """Track running process state"""
    def __init__(self, pid: int, command: str):
        self.pid = pid
        self.command = command
        self.started_at = datetime.now()
        self.output_buffer = ""
        self.exit_code: int | None = None


async def stream_command_output(
    command: str,
    shell: str = "/bin/sh",
    timeout: int = 30,
    env: dict | None = None
) -> AsyncIterator[str]:
    """Stream command output line by line as it arrives.

    CRITICAL PATTERN: Don't wait for process.communicate()!
    Read stdout/stderr incrementally to show progress.

    Args:
        command: Shell command to execute
        shell: Shell interpreter (e.g., /bin/sh, /bin/bash)
        timeout: Maximum execution time in seconds
        env: Environment variables

    Yields:
        Output lines as they arrive

    Example:
        async for line in stream_command_output("long_running_script.sh"):
            print(line, end='')
    """
    # PATTERN 1: Create subprocess with pipes for streaming
    process = await asyncio.create_subprocess_shell(
        command,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
        shell=True,
        executable=shell,
        env=env or {}
    )

    # PATTERN 2: Stream stdout as lines arrive
    try:
        # Read stdout line by line asynchronously
        if process.stdout:
            async for line in process.stdout:
                decoded = line.decode('utf-8', errors='replace')
                yield decoded

        # Wait for process to complete (with timeout)
        await asyncio.wait_for(process.wait(), timeout=timeout)

    except asyncio.TimeoutError:
        # PATTERN 3: Graceful termination on timeout
        yield "\n[TIMEOUT] Process exceeded timeout, terminating...\n"
        await graceful_terminate(process)
        raise

    except Exception as e:
        yield f"\n[ERROR] {str(e)}\n"
        await graceful_terminate(process)
        raise


async def execute_command_with_streaming(
    command: str,
    shell: str = "/bin/sh",
    timeout: int = 30
) -> dict:
    """Execute command and collect output with streaming support.

    This version collects all output while still streaming it.
    Use this when you need both streaming AND final result.

    Returns:
        Dict with exit_code, stdout, stderr, duration
    """
    started_at = datetime.now()
    stdout_lines = []
    stderr_lines = []

    # PATTERN 4: Create subprocess with both stdout and stderr pipes
    process = await asyncio.create_subprocess_shell(
        command,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
        shell=True,
        executable=shell
    )

    # PATTERN 5: Read stdout and stderr concurrently
    async def read_stream(stream, output_list):
        """Helper to read a stream into a list"""
        if stream:
            async for line in stream:
                decoded = line.decode('utf-8', errors='replace')
                output_list.append(decoded)

    try:
        # Gather both streams concurrently
        await asyncio.wait_for(
            asyncio.gather(
                read_stream(process.stdout, stdout_lines),
                read_stream(process.stderr, stderr_lines),
                process.wait()
            ),
            timeout=timeout
        )

    except asyncio.TimeoutError:
        await graceful_terminate(process)
        raise

    duration = (datetime.now() - started_at).total_seconds()

    return {
        "exit_code": process.returncode or 0,
        "stdout": "".join(stdout_lines),
        "stderr": "".join(stderr_lines),
        "duration": duration,
        "command": command
    }


async def graceful_terminate(process: asyncio.subprocess.Process):
    """Gracefully terminate a process (SIGTERM -> wait -> SIGKILL).

    PATTERN 6: Two-stage termination
    1. Send SIGTERM (graceful shutdown)
    2. Wait 1 second
    3. Send SIGKILL if still running (forceful)

    This is the pattern from DesktopCommanderMCP terminal-manager.ts
    """
    try:
        # Try graceful termination first
        process.send_signal(signal.SIGTERM)

        # Wait up to 1 second for graceful shutdown
        try:
            await asyncio.wait_for(process.wait(), timeout=1.0)
        except asyncio.TimeoutError:
            # Force kill if still running
            process.kill()
            await process.wait()

    except ProcessLookupError:
        # Process already terminated
        pass


# PATTERN 7: Process tracking for session management
class ProcessManager:
    """Manage multiple running processes (like DesktopCommanderMCP)"""

    def __init__(self):
        self.sessions: dict[int, ProcessSession] = {}
        self.completed: dict[int, ProcessSession] = {}

    async def start_process(self, command: str, shell: str = "/bin/sh") -> int:
        """Start a process and return its PID"""
        process = await asyncio.create_subprocess_shell(
            command,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
            shell=True,
            executable=shell
        )

        if not process.pid:
            raise RuntimeError("Failed to get process ID")

        session = ProcessSession(process.pid, command)
        self.sessions[process.pid] = session

        # Track process completion in background
        asyncio.create_task(self._track_completion(process, session))

        return process.pid

    async def _track_completion(self, process, session: ProcessSession):
        """Background task to track process completion"""
        await process.wait()
        session.exit_code = process.returncode

        # Move from active to completed
        if session.pid in self.sessions:
            del self.sessions[session.pid]
            self.completed[session.pid] = session

            # Keep only last 100 completed sessions
            if len(self.completed) > 100:
                oldest_pid = next(iter(self.completed))
                del self.completed[oldest_pid]

    def list_active(self) -> list[dict]:
        """List all active processes"""
        now = datetime.now()
        return [
            {
                "pid": session.pid,
                "command": session.command,
                "runtime": (now - session.started_at).total_seconds()
            }
            for session in self.sessions.values()
        ]

    async def terminate(self, pid: int) -> bool:
        """Terminate a specific process"""
        session = self.sessions.get(pid)
        if not session:
            return False

        try:
            # Send SIGTERM
            import os
            os.kill(pid, signal.SIGTERM)

            # Wait and force kill if needed
            await asyncio.sleep(1)
            if pid in self.sessions:
                os.kill(pid, signal.SIGKILL)

            return True
        except ProcessLookupError:
            return False


# Example usage
if __name__ == "__main__":
    async def main():
        # Example 1: Streaming output
        print("=== Streaming Example ===")
        async for line in stream_command_output("ls -la", shell="/bin/sh"):
            print(line, end='')

        # Example 2: Execute and collect
        print("\n=== Execute and Collect Example ===")
        result = await execute_command_with_streaming("echo 'Hello World'")
        print(f"Exit code: {result['exit_code']}")
        print(f"Output: {result['stdout']}")

        # Example 3: Process manager
        print("\n=== Process Manager Example ===")
        manager = ProcessManager()
        pid = await manager.start_process("sleep 5")
        print(f"Started process {pid}")
        print(f"Active processes: {manager.list_active()}")

    asyncio.run(main())
