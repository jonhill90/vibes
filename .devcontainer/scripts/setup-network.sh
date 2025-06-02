#!/bin/bash

echo "🌐 Setting up vibes-network connectivity..."

# Check if vibes-network exists
if docker network ls | grep -q "vibes-network"; then
    echo "✅ vibes-network already exists"
else
    echo "⚠️  vibes-network not found, creating it..."
    if docker network create vibes-network 2>/dev/null; then
        echo "✅ Created vibes-network"
    else
        echo "❌ Failed to create vibes-network (might already exist)"
    fi
fi

# Try to connect current container to the network
CONTAINER_ID=$(hostname)
if docker network connect vibes-network "$CONTAINER_ID" 2>/dev/null; then
    echo "✅ Connected to vibes-network"
else
    echo "⚠️  Could not connect to vibes-network (might already be connected)"
fi

echo "🎯 Network setup complete!"
