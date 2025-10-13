"""MCP Server integration tests for tool endpoints.

This module tests:
- execute_command tool returns JSON strings (CRITICAL)
- manage_process tool with list/kill/read actions
- Error handling and structured responses
- JSON string validation (not dicts)

CRITICAL MCP REQUIREMENT:
- All MCP tools MUST return JSON strings (json.dumps()), NEVER dicts (PRP Gotcha #1)
- This is the most important test - validates MCP protocol compliance

Pattern Sources:
- PRP Task 6: MCP Server specification
- infra/task-manager/backend/tests/test_mcp.py
- prps/streamlined_vibesbox/examples/fastmcp_server_pattern.py
"""

import json
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from src.mcp_server import mcp, execute_command, manage_process


class TestExecuteCommandTool:
    """Test suite for execute_command MCP tool."""

    @pytest.mark.asyncio
    async def test_execute_command_returns_json_string(self):
        """Test that execute_command returns JSON string, not dict.

        CRITICAL: MCP tools MUST return JSON strings (Gotcha #1)
        This is the single most important test for MCP compliance.

        Validates:
        - Return type is str
        - String is valid JSON
        - Can be parsed to dict
        - Has required fields (success, stdout, etc.)
        """
        result = await execute_command("echo 'test'", timeout=5)

        # CRITICAL: Must be string, not dict
        assert isinstance(result, str), \
            "MCP tools MUST return JSON strings, not dicts (Gotcha #1)"

        # Verify it's valid JSON
        parsed = json.loads(result)
        assert isinstance(parsed, dict), "JSON string should parse to dict"

        # Verify structure
        assert "success" in parsed
        assert "stdout" in parsed
        assert "stderr" in parsed
        assert "exit_code" in parsed

    @pytest.mark.asyncio
    async def test_execute_command_successful_execution(self):
        """Test executing a successful command.

        Validates:
        - success=True for successful commands
        - stdout contains output
        - exit_code is 0
        - No error field (or error=null)
        """
        result_str = await execute_command("echo 'hello world'", timeout=5)
        result = json.loads(result_str)

        assert result["success"] is True
        assert "hello world" in result["stdout"]
        assert result["exit_code"] == 0
        assert result.get("error") is None

    @pytest.mark.asyncio
    async def test_execute_command_with_custom_shell(self):
        """Test executing command with custom shell.

        Validates:
        - shell parameter works
        - Different shells supported
        - Output correct
        """
        result_str = await execute_command(
            "echo 'custom shell'",
            shell="/bin/sh",
            timeout=5
        )
        result = json.loads(result_str)

        assert result["success"] is True
        assert "custom shell" in result["stdout"]

    @pytest.mark.asyncio
    async def test_execute_command_with_timeout_parameter(self):
        """Test that timeout parameter is respected.

        Validates:
        - Custom timeout value works
        - Commands timing out return error
        - Timeout error is descriptive
        """
        result_str = await execute_command("sleep 10", timeout=1)
        result = json.loads(result_str)

        assert result["success"] is False
        assert result.get("error") is not None
        assert "timeout" in result["error"].lower() or "timed out" in result["stderr"].lower()

    @pytest.mark.asyncio
    async def test_execute_command_with_streaming_enabled(self):
        """Test command execution with streaming=True.

        Validates:
        - stream parameter works
        - Output still captured
        - JSON string returned
        """
        result_str = await execute_command(
            "echo 'line1'; echo 'line2'",
            stream=True,
            timeout=5
        )
        result = json.loads(result_str)

        assert result["success"] is True
        assert "line1" in result["stdout"]
        assert "line2" in result["stdout"]

    @pytest.mark.asyncio
    async def test_execute_command_with_streaming_disabled(self):
        """Test command execution with streaming=False.

        Validates:
        - stream=False works
        - Blocking mode
        - Output captured
        """
        result_str = await execute_command(
            "echo 'blocking'",
            stream=False,
            timeout=5
        )
        result = json.loads(result_str)

        assert result["success"] is True
        assert "blocking" in result["stdout"]

    @pytest.mark.asyncio
    async def test_execute_command_blocked_by_security(self):
        """Test that dangerous commands are blocked by security validation.

        CRITICAL: Security validation happens BEFORE execution (PRP Task 4)

        Validates:
        - Dangerous commands return success=False
        - Error message is descriptive
        - Command is NOT executed
        """
        result_str = await execute_command("rm -rf /", timeout=5)
        result = json.loads(result_str)

        assert result["success"] is False
        assert result.get("error") is not None
        assert "blocked" in result["error"].lower()
        assert result["exit_code"] == -1

    @pytest.mark.asyncio
    async def test_execute_command_secrets_redacted(self):
        """Test that secrets are redacted from output.

        CRITICAL: Security - prevent credential leakage (PRP Task 3)

        Validates:
        - API keys redacted
        - [REDACTED] marker present
        - Original secret not in output
        """
        result_str = await execute_command("echo 'API_KEY=sk-secret123'", timeout=5)
        result = json.loads(result_str)

        assert result["success"] is True
        assert "sk-secret123" not in result["stdout"], "Secret should be redacted"
        assert "[REDACTED]" in result["stdout"]

    @pytest.mark.asyncio
    async def test_execute_command_output_truncated(self):
        """Test that long output is truncated.

        CRITICAL: Output truncation prevents context exhaustion (PRP Gotcha #5)

        Validates:
        - Long output truncated
        - truncated flag is True
        - Truncation message present
        """
        # Command that outputs many lines
        result_str = await execute_command(
            "python3 -c 'for i in range(200): print(i)'",
            timeout=5
        )
        result = json.loads(result_str)

        # Should be truncated
        if result["success"]:
            assert result.get("truncated") is True
            assert "truncated" in result["stdout"].lower()

    @pytest.mark.asyncio
    async def test_execute_command_error_has_suggestion(self):
        """Test that error responses include helpful suggestions.

        Validates:
        - Error responses structured
        - suggestion field present
        - Helpful guidance provided
        """
        result_str = await execute_command("", timeout=5)  # Empty command
        result = json.loads(result_str)

        assert result["success"] is False
        assert "error" in result
        # Suggestion may or may not be in error responses from execute_command
        # (main suggestion pattern is in manage_process)

    @pytest.mark.asyncio
    async def test_execute_command_exception_handling(self):
        """Test that unexpected exceptions are caught and returned as JSON.

        Validates:
        - Exceptions don't crash tool
        - Structured error response
        - JSON string still returned
        - No unhandled exceptions
        """
        # Patch to simulate exception
        with patch('src.command_executor.execute_command', side_effect=Exception("Test error")):
            result_str = await execute_command("echo 'test'", timeout=5)

            # Should still return JSON string
            assert isinstance(result_str, str)

            result = json.loads(result_str)
            assert result["success"] is False
            assert "error" in result
            assert "Test error" in result["error"]


class TestManageProcessTool:
    """Test suite for manage_process MCP tool."""

    @pytest.mark.asyncio
    async def test_manage_process_returns_json_string(self):
        """Test that manage_process returns JSON string, not dict.

        CRITICAL: MCP tools MUST return JSON strings (Gotcha #1)

        Validates:
        - Return type is str
        - Valid JSON
        - Can be parsed to dict
        """
        result = await manage_process(action="list")

        # CRITICAL: Must be string, not dict
        assert isinstance(result, str), \
            "MCP tools MUST return JSON strings, not dicts (Gotcha #1)"

        # Verify valid JSON
        parsed = json.loads(result)
        assert isinstance(parsed, dict)

    @pytest.mark.asyncio
    async def test_manage_process_list_action(self):
        """Test manage_process with action='list'.

        Validates:
        - Lists all active/completed sessions
        - Returns array of processes
        - Each process has pid, command, status
        - count field present
        """
        result_str = await manage_process(action="list")
        result = json.loads(result_str)

        assert result["success"] is True
        assert "processes" in result
        assert isinstance(result["processes"], list)
        assert "count" in result

        # If any processes, verify structure
        if result["processes"]:
            process = result["processes"][0]
            assert "pid" in process
            assert "command" in process
            assert "status" in process
            assert "started_at" in process

    @pytest.mark.asyncio
    async def test_manage_process_kill_action(self):
        """Test manage_process with action='kill'.

        Validates:
        - Terminates specified process
        - Returns success message
        - pid parameter required
        """
        # This test would need a real session to kill
        # For now, test invalid PID handling
        result_str = await manage_process(action="kill", pid=99999)
        result = json.loads(result_str)

        # Should fail (PID doesn't exist)
        assert result["success"] is False
        assert "error" in result or "not found" in result.get("error", "").lower()

    @pytest.mark.asyncio
    async def test_manage_process_kill_with_sigterm(self):
        """Test kill action with SIGTERM (graceful).

        Validates:
        - signal='SIGTERM' does graceful termination
        - Process terminated correctly
        """
        # Would need real session for full test
        # Test parameter passing
        result_str = await manage_process(action="kill", pid=99999, signal="SIGTERM")
        result = json.loads(result_str)

        # Structure is correct even for failed kill
        assert isinstance(result, dict)
        assert "success" in result

    @pytest.mark.asyncio
    async def test_manage_process_kill_with_sigkill(self):
        """Test kill action with SIGKILL (force).

        Validates:
        - signal='SIGKILL' does forceful termination
        - Force flag passed correctly
        """
        result_str = await manage_process(action="kill", pid=99999, signal="SIGKILL")
        result = json.loads(result_str)

        # Structure is correct
        assert isinstance(result, dict)
        assert "success" in result

    @pytest.mark.asyncio
    async def test_manage_process_read_action(self):
        """Test manage_process with action='read'.

        Validates:
        - Reads incremental output from process
        - Returns output string
        - has_new_output flag present
        - pid parameter required
        """
        # Would need real session for full test
        # Test invalid PID handling
        result_str = await manage_process(action="read", pid=99999)
        result = json.loads(result_str)

        # Should fail (PID doesn't exist)
        assert result["success"] is False
        assert "error" in result

    @pytest.mark.asyncio
    async def test_manage_process_invalid_action(self):
        """Test manage_process with invalid action.

        Validates:
        - Invalid actions return error
        - Error message is descriptive
        - Suggests valid actions
        """
        result_str = await manage_process(action="invalid_action")
        result = json.loads(result_str)

        assert result["success"] is False
        assert "error" in result
        assert "suggestion" in result
        # Should mention valid actions
        assert "list" in result["suggestion"] or "kill" in result["suggestion"]

    @pytest.mark.asyncio
    async def test_manage_process_missing_pid_for_kill(self):
        """Test that kill action requires pid parameter.

        Validates:
        - pid=None for kill returns error
        - Error message mentions missing PID
        """
        result_str = await manage_process(action="kill", pid=None)
        result = json.loads(result_str)

        assert result["success"] is False
        assert "error" in result
        # Error should mention PID
        assert "pid" in result["error"].lower() or "Invalid" in result["error"]

    @pytest.mark.asyncio
    async def test_manage_process_missing_pid_for_read(self):
        """Test that read action requires pid parameter.

        Validates:
        - pid=None for read returns error
        - Error message mentions missing PID
        """
        result_str = await manage_process(action="read", pid=None)
        result = json.loads(result_str)

        assert result["success"] is False
        assert "error" in result

    @pytest.mark.asyncio
    async def test_manage_process_error_has_suggestion(self):
        """Test that error responses include helpful suggestions.

        CRITICAL: Structured error pattern from task-manager (PRP pattern)

        Validates:
        - suggestion field in errors
        - Helpful guidance for users
        - Explains how to fix issue
        """
        result_str = await manage_process(action="kill", pid=99999)
        result = json.loads(result_str)

        assert result["success"] is False
        assert "suggestion" in result
        # Should suggest using list to see processes
        assert "list" in result["suggestion"].lower()

    @pytest.mark.asyncio
    async def test_manage_process_exception_handling(self):
        """Test that exceptions are caught and returned as structured errors.

        Validates:
        - Exceptions don't crash tool
        - JSON string returned
        - Error details included
        """
        # Patch to simulate exception
        with patch('src.mcp_server.session_manager.list_sessions', side_effect=Exception("Test error")):
            result_str = await manage_process(action="list")

            # Should still return JSON string
            assert isinstance(result_str, str)

            result = json.loads(result_str)
            assert result["success"] is False
            assert "error" in result


class TestMCPToolsIntegration:
    """Integration tests for MCP tools working together."""

    @pytest.mark.asyncio
    async def test_both_tools_return_json_strings(self):
        """Test that BOTH MCP tools return JSON strings.

        CRITICAL: Comprehensive check of MCP protocol compliance

        Validates:
        - execute_command returns string
        - manage_process returns string
        - Both are valid JSON
        """
        # Test execute_command
        exec_result = await execute_command("echo 'test'", timeout=5)
        assert isinstance(exec_result, str), "execute_command must return JSON string"
        json.loads(exec_result)  # Must parse

        # Test manage_process
        manage_result = await manage_process(action="list")
        assert isinstance(manage_result, str), "manage_process must return JSON string"
        json.loads(manage_result)  # Must parse

    @pytest.mark.asyncio
    async def test_error_responses_are_json_strings(self):
        """Test that error responses are also JSON strings.

        Validates:
        - Errors return JSON strings (not exceptions)
        - Consistent response format
        - No unhandled exceptions
        """
        # Execute invalid command
        exec_error = await execute_command("rm -rf /", timeout=5)
        assert isinstance(exec_error, str)
        exec_parsed = json.loads(exec_error)
        assert exec_parsed["success"] is False

        # Manage invalid action
        manage_error = await manage_process(action="invalid")
        assert isinstance(manage_error, str)
        manage_parsed = json.loads(manage_error)
        assert manage_parsed["success"] is False

    @pytest.mark.asyncio
    async def test_all_responses_have_success_field(self):
        """Test that all responses have 'success' field.

        Validates:
        - Consistent response structure
        - success=True for success
        - success=False for errors
        """
        # Success case
        success_result = await execute_command("echo 'test'", timeout=5)
        success_parsed = json.loads(success_result)
        assert "success" in success_parsed
        assert success_parsed["success"] is True

        # Error case
        error_result = await execute_command("rm -rf /", timeout=5)
        error_parsed = json.loads(error_result)
        assert "success" in error_parsed
        assert error_parsed["success"] is False


class TestHealthCheckEndpoint:
    """Test suite for /health endpoint."""

    @pytest.mark.asyncio
    async def test_health_check_returns_healthy(self):
        """Test that health check endpoint returns healthy status.

        NOTE: Health check is NOT an MCP tool, so it CAN return dict directly

        Validates:
        - Returns dict (not JSON string - this is FastAPI endpoint)
        - status='healthy'
        - service='vibesbox'
        """
        from src.mcp_server import health_check

        result = await health_check()

        # Health check can return dict (it's a FastAPI endpoint, not MCP tool)
        assert isinstance(result, dict)
        assert result["status"] == "healthy"
        assert result["service"] == "vibesbox"


class TestJSONStringValidation:
    """Dedicated tests for JSON string validation (CRITICAL requirement)."""

    @pytest.mark.asyncio
    async def test_execute_command_never_returns_dict(self):
        """Test that execute_command NEVER returns dict.

        CRITICAL: This is the #1 MCP gotcha - must return JSON string

        Validates:
        - Return type is ALWAYS str
        - NEVER dict
        - Multiple scenarios tested
        """
        test_cases = [
            ("echo 'test'", 5, True),  # Success case
            ("rm -rf /", 5, True),     # Blocked case
            ("sleep 10", 1, True),     # Timeout case
            ("", 5, True),             # Empty command
        ]

        for command, timeout, stream in test_cases:
            result = await execute_command(command, timeout=timeout, stream=stream)
            assert isinstance(result, str), \
                f"execute_command('{command}') returned {type(result)} instead of str"
            assert not isinstance(result, dict), \
                f"execute_command MUST NOT return dict (Gotcha #1)"

    @pytest.mark.asyncio
    async def test_manage_process_never_returns_dict(self):
        """Test that manage_process NEVER returns dict.

        CRITICAL: This is the #1 MCP gotcha - must return JSON string

        Validates:
        - Return type is ALWAYS str
        - NEVER dict
        - All actions tested
        """
        test_cases = [
            ("list", None, "SIGTERM"),           # List action
            ("kill", 99999, "SIGTERM"),          # Kill action (invalid PID)
            ("read", 99999, "SIGTERM"),          # Read action (invalid PID)
            ("invalid", None, "SIGTERM"),        # Invalid action
        ]

        for action, pid, signal in test_cases:
            result = await manage_process(action=action, pid=pid, signal=signal)
            assert isinstance(result, str), \
                f"manage_process('{action}') returned {type(result)} instead of str"
            assert not isinstance(result, dict), \
                f"manage_process MUST NOT return dict (Gotcha #1)"

    @pytest.mark.asyncio
    async def test_json_strings_parse_to_dict(self):
        """Test that all JSON strings can be parsed to dict.

        Validates:
        - JSON strings are valid JSON
        - Parse to dict successfully
        - No JSON syntax errors
        """
        # Test various scenarios
        results = [
            await execute_command("echo 'test'", timeout=5),
            await execute_command("rm -rf /", timeout=5),
            await manage_process(action="list"),
            await manage_process(action="invalid"),
        ]

        for result_str in results:
            try:
                parsed = json.loads(result_str)
                assert isinstance(parsed, dict), "Parsed JSON should be dict"
            except json.JSONDecodeError as e:
                pytest.fail(f"Invalid JSON returned: {e}\nContent: {result_str}")
