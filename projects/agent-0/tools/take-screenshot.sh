#!/bin/bash
# Take screenshot using browserless API
URL="${1:-http://host.docker.internal:8082}"
OUTPUT="${2:-/workspace/vibes/projects/Agent-0/screenshot.png}"

echo "Taking screenshot of $URL..."

# Use browserless screenshot API
curl -X POST \
  http://host.docker.internal:3333/screenshot \
  -H 'Content-Type: application/json' \
  -d "{
    \"url\": \"$URL\",
    \"options\": {
      \"fullPage\": false,
      \"type\": \"png\"
    }
  }" \
  --output "$OUTPUT"

if [ -f "$OUTPUT" ]; then
    echo "✓ Screenshot saved to: $OUTPUT"
    ls -lh "$OUTPUT"
else
    echo "✗ Failed to take screenshot"
    exit 1
fi
