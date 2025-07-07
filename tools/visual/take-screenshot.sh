#!/bin/bash
# Take screenshot using browserless API with REAL viewport control

# Default values
URL="${1:-http://host.docker.internal:8082}"
WIDTH="${WIDTH:-1920}"
HEIGHT="${HEIGHT:-1080}"
FULL_PAGE="${FULL_PAGE:-false}"

# Generate timestamp in YYYYMMDDhhmmss format
TIMESTAMP=$(date +"%Y%m%d%H%M%S")

# Extract domain/identifier from URL for filename (optional)
if [ "$#" -ge 1 ]; then
    # Extract domain and sanitize for filename
    DOMAIN=$(echo "$URL" | sed -E 's|https?://||' | sed -E 's|/.*||' | sed -E 's|[^a-zA-Z0-9.-]|_|g')
    if [ "$FULL_PAGE" = "true" ]; then
        DEFAULT_OUTPUT="/workspace/vibes/screenshots/${TIMESTAMP}_${DOMAIN}_${WIDTH}x${HEIGHT}_fullpage.png"
    else
        DEFAULT_OUTPUT="/workspace/vibes/screenshots/${TIMESTAMP}_${DOMAIN}_${WIDTH}x${HEIGHT}.png"
    fi
else
    DEFAULT_OUTPUT="/workspace/vibes/screenshots/${TIMESTAMP}_screenshot_${WIDTH}x${HEIGHT}.png"
fi

# Use custom output path if provided, otherwise use timestamp-based name
OUTPUT="${2:-$DEFAULT_OUTPUT}"

echo "Taking screenshot of $URL..."
echo "Viewport: ${WIDTH}x${HEIGHT} (full page: ${FULL_PAGE})"

# Ensure screenshots directory exists
mkdir -p /workspace/vibes/screenshots

# Use browserless screenshot API with TRUE viewport control
curl -X POST \
  http://host.docker.internal:9333/screenshot \
  -H 'Content-Type: application/json' \
  -d "{
    \"url\": \"$URL\",
    \"viewport\": {
      \"width\": $WIDTH,
      \"height\": $HEIGHT
    },
    \"options\": {
      \"fullPage\": $FULL_PAGE,
      \"type\": \"png\"
    }
  }" \
  --output "$OUTPUT"

if [ -f "$OUTPUT" ]; then
    echo "✓ Screenshot saved to: $OUTPUT"
    DIMENSIONS=$(identify "$OUTPUT" 2>/dev/null | awk '{print $3}' || echo "unknown")
    echo "  Actual dimensions: $DIMENSIONS"
    ls -lh "$OUTPUT"
else
    echo "✗ Failed to take screenshot"
    exit 1
fi
