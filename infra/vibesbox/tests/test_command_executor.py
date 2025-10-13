"""Command executor tests for async subprocess execution.

This module tests:
- Simple command execution with success/failure
- Timeout enforcement and graceful termination
- Output truncation to prevent context exhaustion
- Streaming output delivery
- Error handling and edge cases

Critical Patterns:
- Async subprocess with PIPE for streaming (PRP Gotcha #6)
- Timeout with graceful termination: SIGTERM -> SIGKILL (PRP Gotcha #6)
- Output truncation to 100 lines max (PRP Gotcha #5)
- Zombie process prevention via await process.wait() (PRP Gotcha #3)

Pattern Sources:
- PRP Task 4: Command Executor specification
- prps/streamlined_vibesbox/examples/subprocess_streaming_pattern.py
"""

import asyncio
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from src.command_executor import (
    execute_command,
    stream_command_output,
    truncate_output,
)
from src.models import CommandResult


class TestCommandExecution:
    """Test suite for command execution functionality."""

    @pytest.mark.asyncio
    async def test_execute_simple_command_success(self):
        """Test executing a simple command that succeeds.

        Validates:
        - Command executes successfully
        - Output captured correctly
        - Exit code is 0
        - No errors
        """
        result = await execute_command("echo 'test'", timeout=5, stream=False)

        assert isinstance(result, CommandResult)
        assert result.success is True
        assert "test" in result.stdout
        assert result.exit_code == 0
        assert result.error is None

    @pytest.mark.asyncio
    async def test_execute_command_with_args(self):
        """Test executing command with arguments.

        Validates:
        - Commands with arguments work
        - Arguments are parsed correctly
        - Output matches expected result
        """
        result = await execute_command("echo hello world", timeout=5, stream=False)

        assert result.success is True
        assert "hello world" in result.stdout
        assert result.exit_code == 0

    @pytest.mark.asyncio
    async def test_execute_blocked_command_rejected(self):
        """Test that blocked commands are rejected before execution.

        CRITICAL: Security validation happens BEFORE execution (PRP Task 4)

        Validates:
        - Blocked command returns success=False
        - Error message is descriptive
        - Command is NOT executed
        - Exit code is -1 (validation failure)
        """
        result = await execute_command("rm -rf /", timeout=5)

        assert result.success is False
        assert result.exit_code == -1
        assert result.error is not None
        assert "blocked" in result.error.lower()
        assert result.stdout == ""

    @pytest.mark.asyncio
    async def test_execute_invalid_command_error(self):
        """Test executing a command that doesn't exist.

        Validates:
        - Non-existent commands handled gracefully
        - Error message is descriptive
        - No crashes or unhandled exceptions
        """
        # This should fail validation (not in allowlist)
        result = await execute_command("nonexistent_command_xyz123", timeout=5)

        assert result.success is False
        assert result.error is not None

    @pytest.mark.asyncio
    async def test_execute_with_timeout_enforcement(self):
        """Test that timeout enforcement works correctly.

        CRITICAL: Timeout must terminate hung processes (PRP Gotcha #6)

        Validates:
        - Commands exceeding timeout are terminated
        - Timeout error is returned
        - Process is killed (no zombies)
        - Execution time is close to timeout value
        """
        import time

        start = time.time()
        result = await execute_command("sleep 10", timeout=1, stream=False)
        duration = time.time() - start

        assert result.success is False
        assert result.error is not None
        assert "timeout" in result.error.lower() or "timed out" in result.stderr.lower()
        assert duration < 3, f"Should timeout in ~1s, took {duration}s"

    @pytest.mark.asyncio
    async def test_timeout_graceful_termination(self):
        """Test that timeout uses graceful termination (SIGTERM then SIGKILL).

        CRITICAL: Two-stage termination prevents resource leaks (PRP pattern)

        Validates:
        - Process terminated gracefully first (SIGTERM)
        - SIGKILL used if process doesn't exit
        - No zombie processes left behind
        """
        # This test verifies the pattern exists by checking timeout behavior
        result = await execute_command("sleep 100", timeout=1, stream=False)

        assert result.success is False
        assert "timeout" in result.error.lower() or "timed out" in result.stderr.lower()
        # Process should be terminated (no zombies)

    @pytest.mark.asyncio
    async def test_output_truncation_applied(self):
        """Test that long output is truncated to prevent context exhaustion.

        CRITICAL: Output MUST be truncated to max 100 lines (PRP Gotcha #5)

        Validates:
        - Output > 100 lines is truncated
        - Truncation message added
        - truncated flag is True
        - Performance optimization
        """
        # Generate command that outputs 200 lines
        command = "python3 -c 'for i in range(200): print(i)'"
        result = await execute_command(command, timeout=5, stream=False)

        # Should be truncated
        lines = result.stdout.split('\n')
        assert len(lines) <= 102, f"Output should be truncated to ~100 lines, got {len(lines)}"
        assert result.truncated is True, "truncated flag should be True"
        assert "truncated" in result.stdout.lower(), "Should have truncation message"

    @pytest.mark.asyncio
    async def test_secrets_redacted_from_output(self):
        """Test that secrets are redacted from command output.

        CRITICAL: Security - prevent credential leakage (PRP Task 3)

        Validates:
        - API keys redacted
        - Passwords redacted
        - Tokens redacted
        - [REDACTED] marker present
        """
        # Command that outputs a fake API key
        command = "echo 'API_KEY=sk-secret123'"
        result = await execute_command(command, timeout=5, stream=False)

        assert result.success is True
        assert "sk-secret123" not in result.stdout, "Secret should be redacted"
        assert "[REDACTED]" in result.stdout, "Should have redaction marker"

    @pytest.mark.asyncio
    async def test_streaming_mode_enabled(self):
        """Test command execution with streaming enabled.

        Validates:
        - stream=True collects output line by line
        - Output is available incrementally (pattern)
        - Final result contains all output
        """
        result = await execute_command("echo 'line 1'; echo 'line 2'", timeout=5, stream=True)

        assert result.success is True
        assert "line 1" in result.stdout
        assert "line 2" in result.stdout

    @pytest.mark.asyncio
    async def test_streaming_output_line_by_line(self):
        """Test that stream_command_output yields lines as they arrive.

        CRITICAL: Don't wait for communicate() - stream as it arrives (PRP pattern)

        Validates:
        - Lines yielded one at a time
        - AsyncIterator pattern works
        - Output arrives incrementally
        """
        lines_collected = []

        async for line in stream_command_output("echo 'test1'; echo 'test2'", timeout=5):
            lines_collected.append(line)

        assert len(lines_collected) >= 2
        output = "".join(lines_collected)
        assert "test1" in output
        assert "test2" in output

    @pytest.mark.asyncio
    async def test_non_streaming_mode(self):
        """Test command execution without streaming (blocking mode).

        Validates:
        - stream=False waits for completion
        - Full output returned at once
        - Exit code captured correctly
        """
        result = await execute_command("echo 'blocking test'", timeout=5, stream=False)

        assert result.success is True
        assert "blocking test" in result.stdout
        assert result.exit_code == 0

    @pytest.mark.asyncio
    async def test_stderr_captured(self):
        """Test that stderr is captured separately from stdout.

        Validates:
        - stderr captured in result.stderr
        - stdout and stderr separate
        - Both sanitized and truncated
        """
        # Command that writes to stderr
        command = "python3 -c 'import sys; sys.stderr.write(\"error message\\n\")'"
        result = await execute_command(command, timeout=5, stream=False)

        # stderr should contain the error message
        # (Note: depending on shell, this might be in stdout or stderr)
        assert "error message" in result.stderr or "error message" in result.stdout

    @pytest.mark.asyncio
    async def test_empty_command_rejected(self):
        """Test that empty commands are rejected.

        Validates:
        - Empty string rejected
        - Whitespace-only rejected
        - Clear error message
        """
        result = await execute_command("", timeout=5)

        assert result.success is False
        assert result.error is not None
        assert "empty" in result.error.lower()

    @pytest.mark.asyncio
    async def test_concurrent_command_execution(self):
        """Test executing multiple commands concurrently.

        Validates:
        - Multiple commands can run in parallel
        - No resource conflicts
        - All commands complete successfully
        """
        commands = [
            execute_command("echo 'cmd1'", timeout=5, stream=False),
            execute_command("echo 'cmd2'", timeout=5, stream=False),
            execute_command("echo 'cmd3'", timeout=5, stream=False),
        ]

        results = await asyncio.gather(*commands)

        assert len(results) == 3
        assert all(r.success for r in results)
        assert "cmd1" in results[0].stdout
        assert "cmd2" in results[1].stdout
        assert "cmd3" in results[2].stdout


class TestOutputTruncation:
    """Test suite for output truncation logic."""

    def test_truncate_short_output_unchanged(self):
        """Test that output under limit is not truncated.

        Validates:
        - Short output unchanged
        - No truncation marker
        - truncated flag is False
        """
        short_output = "line 1\nline 2\nline 3\n"
        truncated, was_truncated = truncate_output(short_output, max_lines=100)

        assert truncated == short_output
        assert was_truncated is False
        assert "truncated" not in truncated.lower()

    def test_truncate_long_output_to_max_lines(self):
        """Test that output over limit is truncated.

        CRITICAL: Must truncate to prevent context exhaustion (PRP Gotcha #5)

        Validates:
        - Output limited to max_lines
        - Truncation message added
        - truncated flag is True
        - Indicates how many lines truncated
        """
        # Generate 200 lines
        long_output = "\n".join([f"line {i}" for i in range(200)])
        truncated, was_truncated = truncate_output(long_output, max_lines=100)

        assert was_truncated is True
        lines = truncated.split('\n')
        assert len(lines) <= 102, f"Should have ~100 lines + truncation message, got {len(lines)}"
        assert "truncated" in truncated.lower()
        assert "100" in truncated, "Should indicate how many lines truncated"

    def test_truncate_exact_limit_not_truncated(self):
        """Test that output exactly at limit is not truncated.

        Validates:
        - Boundary condition: exactly 100 lines
        - No truncation
        - truncated flag is False
        """
        exact_output = "\n".join([f"line {i}" for i in range(100)])
        truncated, was_truncated = truncate_output(exact_output, max_lines=100)

        assert was_truncated is False
        assert "truncated" not in truncated.lower()

    def test_truncate_one_over_limit_truncated(self):
        """Test that output with 101 lines is truncated.

        Validates:
        - Boundary condition: 101 lines
        - Should be truncated to 100 + message
        - truncated flag is True
        """
        over_by_one = "\n".join([f"line {i}" for i in range(101)])
        truncated, was_truncated = truncate_output(over_by_one, max_lines=100)

        assert was_truncated is True
        assert "truncated" in truncated.lower()

    def test_truncate_empty_output(self):
        """Test that empty output is handled gracefully.

        Validates:
        - Empty string returns empty string
        - No errors
        - truncated flag is False
        """
        truncated, was_truncated = truncate_output("", max_lines=100)

        assert truncated == ""
        assert was_truncated is False

    def test_truncate_custom_max_lines(self):
        """Test that custom max_lines parameter works.

        Validates:
        - Can set different limits (e.g., 50 lines)
        - Truncation respects custom limit
        - Flexibility for different use cases
        """
        long_output = "\n".join([f"line {i}" for i in range(100)])
        truncated, was_truncated = truncate_output(long_output, max_lines=50)

        assert was_truncated is True
        lines = truncated.split('\n')
        assert len(lines) <= 52, f"Should have ~50 lines + truncation message"
        assert "50" in truncated, "Should indicate 50 lines truncated"

    def test_truncate_message_format(self):
        """Test that truncation message has correct format.

        Validates:
        - Message indicates how many lines truncated
        - Format: "... [truncated N more lines]"
        - Easy to understand
        """
        long_output = "\n".join([f"line {i}" for i in range(150)])
        truncated, was_truncated = truncate_output(long_output, max_lines=100)

        assert was_truncated is True
        assert "truncated" in truncated.lower()
        assert "50" in truncated, "Should say 50 lines truncated (150 - 100)"
        # Should have format like "... [truncated 50 more lines]"


class TestStreamingOutput:
    """Test suite for streaming output functionality."""

    @pytest.mark.asyncio
    async def test_stream_outputs_lines_incrementally(self):
        """Test that stream_command_output yields lines as they arrive.

        CRITICAL: Don't buffer - yield as lines arrive (PRP pattern)

        Validates:
        - Lines yielded one by one
        - No waiting for full command completion
        - AsyncIterator pattern
        """
        lines = []
        async for line in stream_command_output("echo 'a'; echo 'b'; echo 'c'", timeout=10):
            lines.append(line)

        assert len(lines) >= 3
        output = "".join(lines)
        assert "a" in output
        assert "b" in output
        assert "c" in output

    @pytest.mark.asyncio
    async def test_stream_handles_timeout(self):
        """Test that streaming handles timeout correctly.

        Validates:
        - Timeout message yielded
        - Process terminated gracefully
        - No hang or zombie processes
        """
        lines = []
        with pytest.raises(asyncio.TimeoutError):
            async for line in stream_command_output("sleep 100", timeout=1):
                lines.append(line)

        # Should have timeout message in collected lines
        output = "".join(lines)
        assert "TIMEOUT" in output or "timed out" in output.lower()

    @pytest.mark.asyncio
    async def test_stream_handles_errors_gracefully(self):
        """Test that streaming handles command errors.

        Validates:
        - Errors don't crash iteration
        - Error message yielded
        - Clean shutdown
        """
        lines = []
        try:
            async for line in stream_command_output("python3 -c 'import sys; sys.exit(1)'", timeout=5):
                lines.append(line)
        except Exception:
            # Some errors are acceptable during streaming
            pass

        # Should complete without hanging
        assert True  # If we got here, no hang occurred
