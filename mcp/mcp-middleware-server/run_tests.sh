#!/bin/bash

# MCP Middleware Test Runner
# This script runs various tests to validate the middleware functionality

set -e

echo "=== MCP Middleware Test Suite ==="
echo

# Check if Python dependencies are available
echo "Checking Python dependencies..."
python3 -c "import mcp, flask, flask_cors" 2>/dev/null || {
    echo "Error: Required Python packages not found. Please install:"
    echo "pip install -r requirements.txt"
    exit 1
}
echo "✓ Dependencies OK"
echo

# Test 1: Syntax validation
echo "Test 1: Syntax Validation"
echo "Checking server.py..."
python3 -m py_compile server.py && echo "✓ server.py syntax OK" || echo "✗ server.py syntax error"

echo "Checking server_enhanced.py..."
python3 -m py_compile server_enhanced.py && echo "✓ server_enhanced.py syntax OK" || echo "✗ server_enhanced.py syntax error"

echo "Checking server_with_sse.py..."
python3 -m py_compile server_with_sse.py && echo "✓ server_with_sse.py syntax OK" || echo "✗ server_with_sse.py syntax error"

echo "Checking test MCP..."
python3 -m py_compile mcps/test_mcp.py && echo "✓ test_mcp.py syntax OK" || echo "✗ test_mcp.py syntax error"
echo

# Test 2: Directory structure
echo "Test 2: Directory Structure"
[ -d "mcps" ] && echo "✓ mcps directory exists" || echo "✗ mcps directory missing"
[ -f "mcps/test_mcp.py" ] && echo "✓ test MCP exists" || echo "✗ test MCP missing"
[ -f "requirements.txt" ] && echo "✓ requirements.txt exists" || echo "✗ requirements.txt missing"
[ -f "README.md" ] && echo "✓ README.md exists" || echo "✗ README.md missing"
echo

# Test 3: Test MCP functionality
echo "Test 3: Test MCP Standalone"
echo "Starting test MCP for 3 seconds..."
timeout 3s python3 mcps/test_mcp.py &
TEST_PID=$!
sleep 1

if kill -0 $TEST_PID 2>/dev/null; then
    echo "✓ Test MCP started successfully"
    kill $TEST_PID 2>/dev/null || true
    wait $TEST_PID 2>/dev/null || true
else
    echo "✗ Test MCP failed to start"
fi
echo

# Test 4: Run comprehensive test harness
echo "Test 4: Comprehensive Test Harness"
if [ -f "test_harness.py" ]; then
    echo "Running test harness..."
    python3 test_harness.py server_enhanced.py
    
    if [ -f "test_results.json" ]; then
        echo "✓ Test harness completed, results saved"
        echo "Summary:"
        python3 -c "
import json
with open('test_results.json', 'r') as f:
    results = json.load(f)
if 'summary' in results:
    s = results['summary']
    print(f\"  Total tests: {s['total']}\")
    print(f\"  Passed: {s['passed']}\")
    print(f\"  Failed: {s['failed']}\")
    print(f\"  Errors: {s['errors']}\")
    print(f\"  Success rate: {s['success_rate']:.1f}%\")
else:
    print(f\"  Error: {results.get('error', 'Unknown error')}\")
"
    else
        echo "✗ Test harness did not produce results"
    fi
else
    echo "✗ Test harness not found"
fi
echo

# Test 5: Configuration validation
echo "Test 5: Configuration Validation"
echo "Checking if middleware can be configured for Claude Desktop..."

cat > claude_config_example.json << EOF
{
  "mcpServers": {
    "middleware": {
      "command": "python",
      "args": ["$(pwd)/server_enhanced.py"]
    }
  }
}
EOF

echo "✓ Example Claude Desktop configuration created: claude_config_example.json"
echo

echo "=== Test Suite Complete ==="
echo
echo "Next steps:"
echo "1. Install the middleware in Claude Desktop using the example configuration"
echo "2. Test dynamic MCP loading with: load_mcp"
echo "3. Monitor real-time feedback with: start_feedback_server"
echo
echo "For detailed documentation, see README.md"

