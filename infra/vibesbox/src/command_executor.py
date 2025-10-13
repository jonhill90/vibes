"""
Command executor for Vibesbox MCP server.

Async subprocess execution with streaming output, timeout handling,
and graceful process termination.

Patterns from:
- prps/streamlined_vibesbox/examples/subprocess_streaming_pattern.py
- PRP Task 4 specification
- PRP Gotcha #3: Zombie process prevention
- PRP Gotcha #6: Timeout enforcement
"""

import asyncio
from typing import AsyncIterator

from src.models import CommandResult
from src.security import validate_command, sanitize_output


async def stream_command_output(
    command: str,
    shell: str = "/bin/sh",
    timeout: int = 30
) -> AsyncIterator[str]:
    """
    Stream command output line by line as it arrives.

    Pattern from: examples/subprocess_streaming_pattern.py
    Critical: Don't wait for process.communicate() - stream as lines arrive!

    Args:
        command: Shell command to execute
        shell: Shell interpreter path (default: /bin/sh)
        timeout: Maximum execution time in seconds

    Yields:
        Output lines as they arrive from stdout

    Raises:
        asyncio.TimeoutError: If command exceeds timeout
    """
    process = None
    try:
        # PATTERN 1: Create subprocess with PIPE for streaming
        # Gotcha: Use PIPE for streaming, not communicate()
        process = await asyncio.create_subprocess_shell(
            command,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
            shell=True,
            executable=shell
        )

        # PATTERN 2: Stream stdout line by line asynchronously
        # Gotcha: Don't wait for completion - yield lines as they arrive
        async def read_stdout():
            """Read stdout line by line"""
            if process and process.stdout:
                async for line in process.stdout:
                    decoded = line.decode('utf-8', errors='replace')
                    yield decoded

        # Read output with timeout
        lines_read = 0
        async for line in read_stdout():
            yield line
            lines_read += 1

        # Wait for process to complete (with overall timeout)
        await asyncio.wait_for(process.wait(), timeout=timeout)

    except asyncio.TimeoutError:
        # PATTERN 3: Graceful termination on timeout
        # From: PRP Gotcha #6 - Two-stage termination (SIGTERM -> SIGKILL)
        if process:
            await _graceful_terminate(process)
        yield f"\n[TIMEOUT] Command exceeded {timeout}s and was terminated\n"
        raise

    except Exception as e:
        # Handle other errors
        if process:
            await _graceful_terminate(process)
        yield f"\n[ERROR] {str(e)}\n"
        raise

    finally:
        # PATTERN 4: Ensure cleanup to prevent zombie processes
        # From: PRP Gotcha #3 - MUST await process.wait() to reap process
        if process and process.returncode is None:
            process.kill()
            try:
                await process.wait()
            except ProcessLookupError:
                pass  # Process already terminated


async def execute_command(
    command: str,
    shell: str = "/bin/sh",
    timeout: int = 30,
    stream: bool = True
) -> CommandResult:
    """
    Execute command with validation, streaming, and output handling.

    Pattern from: PRP Task 4 specification
    Critical gotchas addressed:
    - Security validation BEFORE execution (PRP Gotcha #2)
    - Output truncation to prevent context exhaustion (PRP Gotcha #5)
    - Timeout enforcement (PRP Gotcha #6)
    - Secrets redaction (PRP Task 3)

    Args:
        command: Shell command to execute
        shell: Shell interpreter path (default: /bin/sh)
        timeout: Maximum execution time in seconds (default: 30)
        stream: Whether to stream output line-by-line (default: True)

    Returns:
        CommandResult with success status, output, and metadata

    Examples:
        >>> result = await execute_command("echo 'test'", timeout=5)
        >>> print(result.stdout)
        test

        >>> result = await execute_command("sleep 100", timeout=1)
        >>> print(result.error)
        Timeout
    """
    # STEP 1: Security validation BEFORE execution
    # Pattern from: PRP Task 4 - validate_command() from security module
    is_valid, error_msg = validate_command(command)
    if not is_valid:
        return CommandResult(
            success=False,
            exit_code=-1,
            stdout="",
            stderr=error_msg,
            truncated=False,
            error=error_msg
        )

    # STEP 2: Execute command based on stream mode
    if stream:
        # Streaming mode: collect output line by line
        return await _execute_streaming(command, shell, timeout)
    else:
        # Non-streaming mode: wait for completion
        return await _execute_blocking(command, shell, timeout)


async def _execute_streaming(
    command: str,
    shell: str,
    timeout: int
) -> CommandResult:
    """
    Execute command in streaming mode (collect output as it arrives).

    Pattern from: PRP Task 4 - stream_command_output()
    """
    output_lines = []
    exit_code = 0
    error = None

    try:
        # Collect output from stream
        async for line in stream_command_output(command, shell, timeout):
            output_lines.append(line)

            # PATTERN: Truncate to prevent context window exhaustion
            # From: PRP Gotcha #5 - max 100 lines
            if len(output_lines) > 100:
                output_lines.append(f"... [truncated {len(output_lines) - 100} more lines]\n")
                break

        success = True

    except asyncio.TimeoutError:
        # Timeout occurred
        success = False
        exit_code = -1
        error = f"Command timed out after {timeout}s"

    except Exception as e:
        # Other error
        success = False
        exit_code = -1
        error = str(e)
        output_lines.append(f"\n[ERROR] {error}\n")

    # Combine output and sanitize
    raw_output = "".join(output_lines)
    safe_output = sanitize_output(raw_output)

    # Truncate and return result
    truncated_output, was_truncated = truncate_output(safe_output, max_lines=100)

    return CommandResult(
        success=success,
        exit_code=exit_code,
        stdout=truncated_output,
        stderr="",
        truncated=was_truncated or len(output_lines) > 100,
        error=error
    )


async def _execute_blocking(
    command: str,
    shell: str,
    timeout: int
) -> CommandResult:
    """
    Execute command in blocking mode (wait for completion).

    Pattern from: PRP Task 4 - communicate() with timeout
    """
    process = None
    try:
        # Create subprocess
        process = await asyncio.create_subprocess_shell(
            command,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
            shell=True,
            executable=shell
        )

        # PATTERN: Use wait_for() to enforce timeout
        # From: PRP Gotcha #6 - timeout enforcement
        stdout, stderr = await asyncio.wait_for(
            process.communicate(),
            timeout=timeout
        )

        # Decode output
        stdout_text = stdout.decode('utf-8', errors='replace')
        stderr_text = stderr.decode('utf-8', errors='replace')

        # Truncate output
        stdout_truncated, stdout_was_truncated = truncate_output(stdout_text, max_lines=100)
        stderr_truncated, stderr_was_truncated = truncate_output(stderr_text, max_lines=100)

        # Sanitize to redact secrets
        safe_stdout = sanitize_output(stdout_truncated)
        safe_stderr = sanitize_output(stderr_truncated)

        return CommandResult(
            success=True,
            exit_code=process.returncode or 0,
            stdout=safe_stdout,
            stderr=safe_stderr,
            truncated=stdout_was_truncated or stderr_was_truncated,
            error=None
        )

    except asyncio.TimeoutError:
        # PATTERN: Graceful termination on timeout
        # From: PRP Gotcha #6 - SIGTERM -> SIGKILL
        if process:
            await _graceful_terminate(process)

        return CommandResult(
            success=False,
            exit_code=-1,
            stdout="",
            stderr=f"Command timed out after {timeout}s",
            truncated=False,
            error="Timeout"
        )

    except Exception as e:
        # Handle other errors
        if process:
            await _graceful_terminate(process)

        return CommandResult(
            success=False,
            exit_code=-1,
            stdout="",
            stderr=str(e),
            truncated=False,
            error=str(e)
        )

    finally:
        # Ensure cleanup
        if process and process.returncode is None:
            process.kill()
            try:
                await process.wait()
            except ProcessLookupError:
                pass


def truncate_output(output: str, max_lines: int = 100) -> tuple[str, bool]:
    """
    Truncate output to prevent massive payloads.

    Pattern from: PRP Gotcha #5 - Output truncation required
    Reference: task-manager/mcp_server.py (lines 38-79)

    Args:
        output: Raw output string
        max_lines: Maximum number of lines to keep (default: 100)

    Returns:
        Tuple of (truncated_output, was_truncated)
        - truncated_output: Output limited to max_lines
        - was_truncated: True if output was truncated

    Examples:
        >>> text = "\\n".join([f"line {i}" for i in range(200)])
        >>> truncated, was_truncated = truncate_output(text, max_lines=100)
        >>> print(was_truncated)
        True
        >>> print("truncated" in truncated.lower())
        True
    """
    if not output:
        return output, False

    lines = output.split('\n')
    was_truncated = len(lines) > max_lines

    if was_truncated:
        # Keep first max_lines and add truncation message
        truncated_lines = lines[:max_lines]
        num_truncated = len(lines) - max_lines
        truncated_lines.append(f"\n... [truncated {num_truncated} more lines]")
        return '\n'.join(truncated_lines), True

    return output, False


async def _graceful_terminate(process: asyncio.subprocess.Process) -> None:
    """
    Gracefully terminate a process (SIGTERM -> wait -> SIGKILL).

    Pattern from: examples/subprocess_streaming_pattern.py
    Critical: Two-stage termination prevents resource leaks

    Implementation:
    1. Send SIGTERM (graceful shutdown signal)
    2. Wait 1 second for process to exit
    3. Send SIGKILL if still running (forceful termination)
    4. Always wait() to reap the process (prevent zombies)

    Args:
        process: The subprocess to terminate
    """
    try:
        # Stage 1: Try graceful termination (SIGTERM)
        process.terminate()

        # Wait up to 1 second for graceful shutdown
        try:
            await asyncio.wait_for(process.wait(), timeout=1.0)
        except asyncio.TimeoutError:
            # Stage 2: Force kill if still running (SIGKILL)
            process.kill()
            await process.wait()

    except ProcessLookupError:
        # Process already terminated
        pass
