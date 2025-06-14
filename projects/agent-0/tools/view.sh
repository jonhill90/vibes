#!/bin/bash
# Simple wrapper to take and describe screenshots

TARGET="${1:-http://host.docker.internal:8082}"
SCREENSHOT_PATH="/workspace/vibes/projects/Agent-0/screenshots/$(date +%Y%m%d_%H%M%S).png"

# Create screenshots directory
mkdir -p /workspace/vibes/projects/Agent-0/screenshots

# Take screenshot
echo "📸 Taking screenshot of: $TARGET"
/workspace/vibes/projects/Agent-0/tools/take-screenshot.sh "$TARGET" "$SCREENSHOT_PATH"

# Show file info
if [ -f "$SCREENSHOT_PATH" ]; then
    echo ""
    echo "Screenshot details:"
    file "$SCREENSHOT_PATH"
    echo ""
    echo "To view: Copy $SCREENSHOT_PATH to your local machine"
fi
