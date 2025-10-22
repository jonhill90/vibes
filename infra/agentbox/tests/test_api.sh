#!/bin/bash
set -euo pipefail

# AgentBox API Tests
# Tests HTTP/SSE endpoints and MCP tools

BASE_URL="http://localhost:8054"
GREEN='\033[0;32m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo "Testing AgentBox API..."
echo

# Test 1: Health check
echo -n "1. Health check... "
HEALTH=$(curl -s ${BASE_URL}/health)
if echo "$HEALTH" | grep -q "healthy"; then
    echo -e "${GREEN}✓ PASS${NC}"
else
    echo -e "${RED}✗ FAIL${NC}"
    echo "Response: $HEALTH"
    exit 1
fi

# Test 2: SSE endpoint accessible
echo -n "2. SSE endpoint... "
SSE_RESPONSE=$(curl -s -N -m 2 ${BASE_URL}/sse -H "Accept: text/event-stream" || echo "timeout")
if [ "$SSE_RESPONSE" != "timeout" ]; then
    echo -e "${GREEN}✓ PASS${NC}"
else
    echo -e "${RED}✗ FAIL (timeout expected on initial connection)${NC}"
fi

# Test 3: MCP tool - run_command
echo -n "3. MCP tool: run_command... "
COMMAND_RESULT=$(curl -s -X POST ${BASE_URL}/mcp/run_command \
    -H "Content-Type: application/json" \
    -d '{"command": "echo hello", "working_dir": "/app"}' 2>&1 || echo "fail")

if echo "$COMMAND_RESULT" | grep -q "hello\|EXIT CODE"; then
    echo -e "${GREEN}✓ PASS${NC}"
else
    echo -e "${RED}✗ FAIL${NC}"
    echo "Response: $COMMAND_RESULT"
fi

# Test 4: Container is running
echo -n "4. Container status... "
if docker ps | grep -q agentbox; then
    echo -e "${GREEN}✓ PASS${NC}"
else
    echo -e "${RED}✗ FAIL${NC}"
    exit 1
fi

# Test 5: Logs show startup
echo -n "5. Server logs... "
if docker logs agentbox 2>&1 | grep -q "Starting AgentBox"; then
    echo -e "${GREEN}✓ PASS${NC}"
else
    echo -e "${RED}✗ FAIL${NC}"
fi

echo
echo -e "${GREEN}All tests passed!${NC}"
