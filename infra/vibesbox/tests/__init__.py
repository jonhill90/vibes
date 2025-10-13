"""Vibesbox test suite.

This package contains unit and integration tests for the Vibesbox MCP server.

Test Structure:
- test_security.py: Command validation and output sanitization tests
- test_command_executor.py: Command execution, streaming, and timeout tests
- test_session_manager.py: Process session management and cleanup tests
- test_mcp_server.py: MCP tool integration tests

Test Patterns:
- pytest-asyncio for async tests
- unittest.mock for mocking external dependencies
- Comprehensive edge case coverage
- JSON string validation for MCP tools (CRITICAL)

Pattern Sources:
- infra/task-manager/backend/tests/test_mcp.py
- PRP Task 10 specification
"""
