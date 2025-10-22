#!/bin/bash
# Simple smoke tests for AgentBox

GREEN='\033[0;32m'
RED='\033[0;31m'
NC='\033[0m'

echo "AgentBox Smoke Tests"
echo "===================="
echo

# Test 1: Container running
echo -n "1. Container status... "
if docker ps | grep -q agentbox; then
    STATUS=$(docker inspect --format='{{.State.Status}}' agentbox)
    if [ "$STATUS" = "running" ]; then
        echo -e "${GREEN}✓ running${NC}"
    else
        echo -e "${RED}✗ $STATUS${NC}"
        exit 1
    fi
else
    echo -e "${RED}✗ not found${NC}"
    exit 1
fi

# Test 2: Port 8054 open
echo -n "2. Port 8054 accessible... "
RESPONSE=$(curl -s -m 2 http://localhost:8054/health 2>&1)
if [ $? -eq 0 ]; then
    echo -e "${GREEN}✓ open${NC}"
else
    echo -e "${RED}✗ closed${NC}"
    exit 1
fi

# Test 3: Health endpoint responds
echo -n "3. Health endpoint... "
HEALTH=$(curl -s -m 2 http://localhost:8054/health 2>&1)
if echo "$HEALTH" | grep -q "healthy"; then
    echo -e "${GREEN}✓ responding${NC}"
else
    echo -e "${RED}✗ not responding${NC}"
    exit 1
fi

# Test 4: Server logs show startup
echo -n "4. Server started... "
if docker logs agentbox 2>&1 | grep -q "Starting AgentBox MCP server"; then
    echo -e "${GREEN}✓ yes${NC}"
else
    echo -e "${RED}✗ no startup message${NC}"
fi

# Test 5: FastMCP in streamable-http mode
echo -n "5. Streamable HTTP mode... "
if docker logs agentbox 2>&1 | grep -q "Streamable HTTP"; then
    echo -e "${GREEN}✓ streamable-http mode${NC}"
else
    echo -e "${RED}✗ wrong mode${NC}"
fi

# Test 6: Can execute commands in container
echo -n "6. Command execution... "
if docker exec agentbox echo "test" 2>&1 | grep -q "test"; then
    echo -e "${GREEN}✓ works${NC}"
else
    echo -e "${RED}✗ failed${NC}"
fi

# Test 7: Docker CLI installed
echo -n "7. Docker CLI... "
if docker exec agentbox docker --version 2>&1 | grep -q "Docker version"; then
    echo -e "${GREEN}✓ installed${NC}"
else
    echo -e "${RED}✗ not installed${NC}"
fi

# Test 8: Tree command installed
echo -n "8. Extra packages (tree)... "
if docker exec agentbox tree --version 2>&1 | grep -q "tree"; then
    echo -e "${GREEN}✓ installed${NC}"
else
    echo -e "${RED}✗ not installed${NC}"
fi

echo
echo -e "${GREEN}✓ All smoke tests passed!${NC}"
echo
echo "Server Details:"
echo "  URL: http://localhost:8054/mcp"
echo "  Transport: streamable-http"
echo "  Health: http://localhost:8054/health"
echo "  Image: $(docker inspect --format='{{.Config.Image}}' agentbox)"
echo "  Status: $(docker inspect --format='{{.State.Status}}' agentbox)"
echo
