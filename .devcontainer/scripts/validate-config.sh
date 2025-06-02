#!/bin/bash

echo "🔍 Validating devcontainer configuration..."
echo ""

# Check JSON files
echo "📋 Checking JSON files:"
if python3 -c "import json; json.load(open('.devcontainer/devcontainer.json'))" 2>/dev/null; then
    echo "✅ devcontainer.json - valid"
else
    echo "❌ devcontainer.json - invalid JSON"
fi

if python3 -c "import json; json.load(open('.devcontainer/scripts/codex/config.json'))" 2>/dev/null; then
    echo "✅ codex/config.json - valid"
else
    echo "❌ codex/config.json - invalid JSON"
fi

# Check required files
echo ""
echo "📁 Checking required files:"
for file in ".devcontainer/Dockerfile" ".devcontainer/docker-compose.yml" ".devcontainer/devcontainer.json"; do
    if [ -f "$file" ]; then
        echo "✅ $file - exists"
    else
        echo "❌ $file - missing"
    fi
done

# Check scripts
echo ""
echo "📜 Checking scripts:"
for script in ".devcontainer/scripts/postCreate.sh" ".devcontainer/scripts/test-network.sh" ".devcontainer/scripts/test-docker.sh"; do
    if [ -f "$script" ] && [ -x "$script" ]; then
        echo "✅ $script - exists and executable"
    elif [ -f "$script" ]; then
        echo "⚠️  $script - exists but not executable"
    else
        echo "❌ $script - missing"
    fi
done

echo ""
echo "🎯 Configuration validation complete!"
