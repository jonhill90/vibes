#!/bin/bash

echo "🐳 Testing Docker functionality in devcontainer..."
echo ""

# Test Docker CLI access
echo "📋 Testing Docker CLI:"
if command -v docker &>/dev/null; then
    echo "✅ Docker CLI found: $(which docker)"
    
    # Test Docker version
    if docker --version &>/dev/null; then
        echo "✅ Docker version: $(docker --version)"
    else
        echo "❌ Docker version command failed"
    fi
    
    # Test Docker info (daemon connectivity)
    echo ""
    echo "🔗 Testing Docker daemon connectivity:"
    if docker info &>/dev/null; then
        echo "✅ Docker daemon accessible"
        echo "  Container runtime: $(docker info --format '{{.ServerVersion}}')"
        echo "  Total containers: $(docker info --format '{{.Containers}}')"
    else
        echo "❌ Docker daemon not accessible"
        echo "  This might be expected in some devcontainer setups"
    fi
    
    # Test Docker socket permissions
    echo ""
    echo "🔐 Testing Docker socket permissions:"
    if ls -la /var/run/docker.sock &>/dev/null; then
        echo "✅ Docker socket found: $(ls -la /var/run/docker.sock)"
        
        if [ -w /var/run/docker.sock ]; then
            echo "✅ Docker socket is writable"
        else
            echo "⚠️  Docker socket is not writable - check group membership"
        fi
    else
        echo "❌ Docker socket not found"
    fi
    
    # Test group membership
    echo ""
    echo "👥 Testing group membership:"
    if groups | grep -q docker; then
        echo "✅ User is in docker group: $(groups | grep docker)"
    else
        echo "⚠️  User not in docker group: $(groups)"
    fi
    
else
    echo "❌ Docker CLI not found"
fi

# Test Docker Compose
echo ""
echo "🐙 Testing Docker Compose:"
if docker compose version &>/dev/null; then
    echo "✅ Docker Compose available: $(docker compose version)"
else
    echo "❌ Docker Compose not available"
fi

echo ""
echo "🎯 Docker test complete!"
