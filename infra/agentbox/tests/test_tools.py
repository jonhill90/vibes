#!/usr/bin/env python3
"""
Test AgentBox MCP tools via streamable-http API
"""

import httpx
import json
import os

# Use localhost:8000 when running inside container, localhost:8054 when running from host
BASE_URL = os.getenv("AGENTBOX_URL", "http://localhost:8054")

def test_health_endpoint():
    """Test HTTP health endpoint"""
    print("1. Testing HTTP health endpoint... ", end="")
    try:
        with httpx.Client() as client:
            response = client.get(
                f"{BASE_URL}/health",
                timeout=5.0
            )
            if response.status_code == 200:
                data = response.json()
                if data.get("status") == "healthy":
                    print("✓ PASS")
                    return True
    except Exception as e:
        print(f"✗ FAIL: {e}")
    return False

def test_mcp_endpoint():
    """Test MCP endpoint is accessible"""
    print("2. Testing MCP endpoint... ", end="")
    try:
        with httpx.Client() as client:
            # streamable-http requires POST with initialize and proper headers
            init_request = {
                "jsonrpc": "2.0",
                "id": 1,
                "method": "initialize",
                "params": {
                    "protocolVersion": "2024-11-05",
                    "capabilities": {},
                    "clientInfo": {
                        "name": "test-client",
                        "version": "1.0.0"
                    }
                }
            }

            response = client.post(
                f"{BASE_URL}/mcp",
                json=init_request,
                headers={
                    "Accept": "application/json, text/event-stream"
                },
                timeout=5.0
            )

            if response.status_code in [200, 202]:
                print("✓ PASS")
                return True
            else:
                print(f"✗ FAIL: HTTP {response.status_code}")
    except Exception as e:
        print(f"✗ FAIL: {e}")
    return False

def test_list_tools():
    """Test listing available tools"""
    print("3. Testing list tools... ", end="")
    try:
        with httpx.Client() as client:
            # Initialize session
            init_request = {
                "jsonrpc": "2.0",
                "id": 1,
                "method": "initialize",
                "params": {
                    "protocolVersion": "2024-11-05",
                    "capabilities": {},
                    "clientInfo": {
                        "name": "test-client",
                        "version": "1.0.0"
                    }
                }
            }

            init_response = client.post(
                f"{BASE_URL}/mcp",
                json=init_request,
                headers={"Accept": "application/json, text/event-stream"},
                timeout=5.0
            )

            session_id = init_response.headers.get("mcp-session-id")
            if not session_id:
                print(f"✗ FAIL: No session ID")
                return False

            # Send initialized notification
            client.post(
                f"{BASE_URL}/mcp",
                json={"jsonrpc": "2.0", "method": "notifications/initialized"},
                headers={
                    "Accept": "application/json, text/event-stream",
                    "mcp-session-id": session_id
                },
                timeout=5.0
            )

            # List tools
            tools_request = {
                "jsonrpc": "2.0",
                "id": 2,
                "method": "tools/list"
            }

            tools_response = client.post(
                f"{BASE_URL}/mcp",
                json=tools_request,
                headers={
                    "Accept": "application/json, text/event-stream",
                    "mcp-session-id": session_id
                },
                timeout=5.0
            )

            if tools_response.status_code == 200:
                # Parse SSE format
                for line in tools_response.text.split('\n'):
                    if line.startswith('data: '):
                        data = json.loads(line.replace('data: ', ''))
                        if 'result' in data and 'tools' in data['result']:
                            tool_names = [t['name'] for t in data['result']['tools']]
                            expected = ['execute_command', 'manage_process', 'health']
                            if all(name in tool_names for name in expected):
                                print(f"✓ PASS (found {len(tool_names)} tools)")
                                return True
                            else:
                                print(f"✗ FAIL: Expected {expected}, got {tool_names}")
                                return False
            print(f"✗ FAIL: HTTP {tools_response.status_code}")
    except Exception as e:
        print(f"✗ FAIL: {e}")
    return False

def test_execute_command():
    """Test execute_command tool"""
    print("4. Testing execute_command tool... ", end="")
    try:
        with httpx.Client() as client:
            # Initialize session
            init_request = {
                "jsonrpc": "2.0",
                "id": 1,
                "method": "initialize",
                "params": {
                    "protocolVersion": "2024-11-05",
                    "capabilities": {},
                    "clientInfo": {
                        "name": "test-client",
                        "version": "1.0.0"
                    }
                }
            }

            init_response = client.post(
                f"{BASE_URL}/mcp",
                json=init_request,
                headers={"Accept": "application/json, text/event-stream"},
                timeout=5.0
            )

            session_id = init_response.headers.get("mcp-session-id")
            if not session_id:
                print(f"✗ FAIL: No session ID")
                return False

            # Send initialized notification
            client.post(
                f"{BASE_URL}/mcp",
                json={"jsonrpc": "2.0", "method": "notifications/initialized"},
                headers={
                    "Accept": "application/json, text/event-stream",
                    "mcp-session-id": session_id
                },
                timeout=5.0
            )

            # Call execute_command tool
            tool_request = {
                "jsonrpc": "2.0",
                "id": 2,
                "method": "tools/call",
                "params": {
                    "name": "execute_command",
                    "arguments": {
                        "command": "echo 'test successful'",
                        "shell": "/bin/sh",
                        "timeout": 10
                    }
                }
            }

            tool_response = client.post(
                f"{BASE_URL}/mcp",
                json=tool_request,
                headers={
                    "Accept": "application/json, text/event-stream",
                    "mcp-session-id": session_id
                },
                timeout=15.0
            )

            if tool_response.status_code == 200:
                # Parse SSE format
                for line in tool_response.text.split('\n'):
                    if line.startswith('data: '):
                        data = json.loads(line.replace('data: ', ''))
                        if 'result' in data:
                            content = data['result'].get('content', [])
                            if content and 'test successful' in str(content):
                                print("✓ PASS")
                                return True
                print(f"✗ FAIL: Could not find 'test successful' in response")
            else:
                print(f"✗ FAIL: HTTP {tool_response.status_code}")
    except Exception as e:
        print(f"✗ FAIL: {e}")
    return False

def main():
    print("Testing AgentBox MCP API (streamable-http)\n")

    tests = [
        test_health_endpoint,
        test_mcp_endpoint,
        test_list_tools,
        test_execute_command
    ]

    passed = sum(test() for test in tests)
    total = len(tests)

    print(f"\n{passed}/{total} tests passed")

    if passed == total:
        print("✓ All tests passed!")
        return 0
    else:
        print("✗ Some tests failed")
        return 1

if __name__ == "__main__":
    exit(main())
