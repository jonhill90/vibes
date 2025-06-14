#!/bin/bash
# Simple wrapper to take and describe screenshots

TARGET="${1:-http://host.docker.internal:8082}"
SCREENSHOT_PATH="/workspace/vibes/screenshots/$(date +%Y%m%d_%H%M%S).png"

# Create screenshots directory
mkdir -p /workspace/vibes/screenshots

# Take screenshot
echo "📸 Taking screenshot of: $TARGET"
/workspace/vibes/tools/visual/take-screenshot.sh "$TARGET" "$SCREENSHOT_PATH"

# Show file info
if [ -f "$SCREENSHOT_PATH" ]; then
    echo ""
    echo "Screenshot details:"
    file "$SCREENSHOT_PATH"
    echo ""
    echo "To view: Copy $SCREENSHOT_PATH to your local machine"
fi
