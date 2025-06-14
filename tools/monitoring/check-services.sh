#!/bin/bash
# Check what services are available for Agent-0 to see

echo "🔍 Checking available services..."
echo ""
echo "Docker containers running:"
docker ps --format "table {{.Names}}\t{{.Ports}}\t{{.Status}}"
echo ""

# Test common ports
echo "Testing service availability:"
for port in 3000 3333 8082 8765; do
    if curl -s -I "http://host.docker.internal:$port" >/dev/null 2>&1; then
        echo "✓ Port $port is accessible"
    else
        echo "✗ Port $port is not accessible"
    fi
done
