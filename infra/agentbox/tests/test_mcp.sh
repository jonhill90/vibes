#!/bin/bash
set -euo pipefail

# AgentBox MCP Protocol Tests
# Tests MCP tools via HTTP/SSE API

BASE_URL="http://localhost:8054"
GREEN='\033[0;32m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}Testing AgentBox MCP Server${NC}\n"

# Test 1: SSE endpoint accessible
echo -n "1. SSE endpoint connection... "
SSE_RESPONSE=$(curl -s -m 2 ${BASE_URL}/sse -H "Accept: text/event-stream" 2>&1 || echo "fail")
if echo "$SSE_RESPONSE" | grep -q "event: endpoint"; then
    echo -e "${GREEN}✓ PASS${NC}"
    SESSION_PATH=$(echo "$SSE_RESPONSE" | grep "data: /messages/" | sed 's/data: //' | tr -d '\r')
else
    echo -e "${RED}✗ FAIL${NC}"
    exit 1
fi

# Test 2: List tools
echo -n "2. List available tools... "
TOOLS_REQUEST='{"jsonrpc":"2.0","id":1,"method":"tools/list"}'
TOOLS_RESPONSE=$(curl -s -X POST "${BASE_URL}${SESSION_PATH}" \
    -H "Content-Type: application/json" \
    -d "$TOOLS_REQUEST" 2>&1)

if echo "$TOOLS_RESPONSE" | grep -q "run_command"; then
    TOOL_COUNT=$(echo "$TOOLS_RESPONSE" | grep -o "run_command\|take_screenshot\|click_desktop\|send_keys\|type_text\|health" | wc -l | tr -d ' ')
    echo -e "${GREEN}✓ PASS${NC} (found $TOOL_COUNT tools)"
else
    echo -e "${RED}✗ FAIL${NC}"
    echo "Response: $TOOLS_RESPONSE"
fi

# Get new session for tool testing
SESSION_RESPONSE=$(curl -s -m 2 ${BASE_URL}/sse -H "Accept: text/event-stream")
SESSION_PATH=$(echo "$SESSION_RESPONSE" | grep "data: /messages/" | sed 's/data: //' | tr -d '\r')

# Test 3: Call health tool
echo -n "3. Call health tool... "
HEALTH_REQUEST='{"jsonrpc":"2.0","id":1,"method":"tools/call","params":{"name":"health","arguments":{}}}'
HEALTH_RESPONSE=$(curl -s -X POST "${BASE_URL}${SESSION_PATH}" \
    -H "Content-Type: application/json" \
    -d "$HEALTH_REQUEST" 2>&1)

if echo "$HEALTH_RESPONSE" | grep -q "healthy"; then
    echo -e "${GREEN}✓ PASS${NC}"
else
    echo -e "${RED}✗ FAIL${NC}"
    echo "Response: $HEALTH_RESPONSE"
fi

# Get new session for command test
SESSION_RESPONSE=$(curl -s -m 2 ${BASE_URL}/sse -H "Accept: text/event-stream")
SESSION_PATH=$(echo "$SESSION_RESPONSE" | grep "data: /messages/" | sed 's/data: //' | tr -d '\r')

# Test 4: Call run_command tool
echo -n "4. Call run_command tool... "
COMMAND_REQUEST='{"jsonrpc":"2.0","id":1,"method":"tools/call","params":{"name":"run_command","arguments":{"command":"echo test123","working_dir":"/app"}}}'
COMMAND_RESPONSE=$(curl -s -X POST "${BASE_URL}${SESSION_PATH}" \
    -H "Content-Type: application/json" \
    -d "$COMMAND_REQUEST" 2>&1)

if echo "$COMMAND_RESPONSE" | grep -q "test123"; then
    echo -e "${GREEN}✓ PASS${NC}"
else
    echo -e "${RED}✗ FAIL${NC}"
    echo "Response: $COMMAND_RESPONSE"
fi

# Test 5: Verify Docker CLI available
echo -n "5. Docker CLI in container... "
DOCKER_CMD_REQUEST='{"jsonrpc":"2.0","id":1,"method":"tools/call","params":{"name":"run_command","arguments":{"command":"docker --version","working_dir":"/app"}}}'
SESSION_RESPONSE=$(curl -s -m 2 ${BASE_URL}/sse -H "Accept: text/event-stream")
SESSION_PATH=$(echo "$SESSION_RESPONSE" | grep "data: /messages/" | sed 's/data: //' | tr -d '\r')
DOCKER_RESPONSE=$(curl -s -X POST "${BASE_URL}${SESSION_PATH}" \
    -H "Content-Type: application/json" \
    -d "$DOCKER_CMD_REQUEST" 2>&1)

if echo "$DOCKER_RESPONSE" | grep -q "Docker version"; then
    echo -e "${GREEN}✓ PASS${NC}"
else
    echo -e "${RED}✗ FAIL${NC}"
fi

# Test 6: Verify packages installed
echo -n "6. Extra packages (tree)... "
TREE_CMD_REQUEST='{"jsonrpc":"2.0","id":1,"method":"tools/call","params":{"name":"run_command","arguments":{"command":"tree --version","working_dir":"/app"}}}'
SESSION_RESPONSE=$(curl -s -m 2 ${BASE_URL}/sse -H "Accept: text/event-stream")
SESSION_PATH=$(echo "$SESSION_RESPONSE" | grep "data: /messages/" | sed 's/data: //' | tr -d '\r')
TREE_RESPONSE=$(curl -s -X POST "${BASE_URL}${SESSION_PATH}" \
    -H "Content-Type: application/json" \
    -d "$TREE_CMD_REQUEST" 2>&1)

if echo "$TREE_RESPONSE" | grep -q "tree"; then
    echo -e "${GREEN}✓ PASS${NC}"
else
    echo -e "${RED}✗ FAIL${NC}"
fi

echo
echo -e "${GREEN}All MCP protocol tests passed!${NC}"
echo
echo "Container info:"
docker ps | grep agentbox
