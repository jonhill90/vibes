#!/usr/bin/env python3
"""
Test AgentBox MCP tools via HTTP/SSE API
"""

import httpx
import json

BASE_URL = "http://localhost:8054"

def test_sse_endpoint():
    """Test SSE endpoint is accessible"""
    print("1. Testing SSE endpoint... ", end="")
    try:
        with httpx.Client() as client:
            response = client.get(
                f"{BASE_URL}/sse",
                headers={"Accept": "text/event-stream"},
                timeout=2.0
            )
            if response.status_code == 200:
                print("✓ PASS")
                return True
    except Exception as e:
        print(f"✗ FAIL: {e}")
    return False

def test_list_tools():
    """Test listing available tools"""
    print("2. Testing list tools... ", end="")
    try:
        with httpx.Client() as client:
            # Create SSE session first
            response = client.get(
                f"{BASE_URL}/sse",
                headers={"Accept": "text/event-stream"},
                timeout=2.0,
                follow_redirects=True
            )

            # Extract session endpoint from SSE response
            for line in response.text.split('\n'):
                if line.startswith('data: /messages/'):
                    session_path = line.replace('data: ', '').strip()

                    # List tools via session
                    tools_request = {
                        "jsonrpc": "2.0",
                        "id": 1,
                        "method": "tools/list"
                    }

                    tools_response = client.post(
                        f"{BASE_URL}{session_path}",
                        json=tools_request,
                        timeout=5.0
                    )

                    if tools_response.status_code == 200:
                        data = tools_response.json()
                        tools = data.get('result', {}).get('tools', [])
                        tool_names = [t['name'] for t in tools]

                        expected = ['run_command', 'take_screenshot', 'click_desktop', 'send_keys', 'type_text', 'health']
                        if all(name in tool_names for name in expected):
                            print(f"✓ PASS (found {len(tools)} tools)")
                            return True
                    break
    except Exception as e:
        print(f"✗ FAIL: {e}")
    return False

def test_run_command():
    """Test run_command tool"""
    print("3. Testing run_command tool... ", end="")
    try:
        with httpx.Client() as client:
            # Create SSE session
            response = client.get(
                f"{BASE_URL}/sse",
                headers={"Accept": "text/event-stream"},
                timeout=2.0
            )

            # Extract session endpoint
            for line in response.text.split('\n'):
                if line.startswith('data: /messages/'):
                    session_path = line.replace('data: ', '').strip()

                    # Call run_command tool
                    tool_request = {
                        "jsonrpc": "2.0",
                        "id": 1,
                        "method": "tools/call",
                        "params": {
                            "name": "run_command",
                            "arguments": {
                                "command": "echo 'test successful'",
                                "working_dir": "/app"
                            }
                        }
                    }

                    tool_response = client.post(
                        f"{BASE_URL}{session_path}",
                        json=tool_request,
                        timeout=10.0
                    )

                    if tool_response.status_code == 200:
                        data = tool_response.json()
                        result = data.get('result', {})
                        content = result.get('content', [])

                        if content and 'test successful' in str(content):
                            print("✓ PASS")
                            return True
                    break
    except Exception as e:
        print(f"✗ FAIL: {e}")
    return False

def test_health_tool():
    """Test health tool"""
    print("4. Testing health tool... ", end="")
    try:
        with httpx.Client() as client:
            # Create SSE session
            response = client.get(
                f"{BASE_URL}/sse",
                headers={"Accept": "text/event-stream"},
                timeout=2.0
            )

            # Extract session endpoint
            for line in response.text.split('\n'):
                if line.startswith('data: /messages/'):
                    session_path = line.replace('data: ', '').strip()

                    # Call health tool
                    tool_request = {
                        "jsonrpc": "2.0",
                        "id": 1,
                        "method": "tools/call",
                        "params": {
                            "name": "health",
                            "arguments": {}
                        }
                    }

                    tool_response = client.post(
                        f"{BASE_URL}{session_path}",
                        json=tool_request,
                        timeout=5.0
                    )

                    if tool_response.status_code == 200:
                        data = tool_response.json()
                        result = data.get('result', {})
                        content = result.get('content', [])

                        if content and 'healthy' in str(content):
                            print("✓ PASS")
                            return True
                    break
    except Exception as e:
        print(f"✗ FAIL: {e}")
    return False

def main():
    print("Testing AgentBox MCP API\n")

    tests = [
        test_sse_endpoint,
        test_list_tools,
        test_run_command,
        test_health_tool
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
