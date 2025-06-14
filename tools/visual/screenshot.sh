#!/bin/bash
# Screenshot tool for Docker environment
URL="${1:-http://host.docker.internal:8082}"
OUTPUT="${2:-screenshot.png}"

# Since we're in Docker, we need to use a different approach
# Let's use curl to fetch the HTML first to verify connectivity
echo "Testing connection to $URL..."
if curl -s -I "$URL" | grep -q "200 OK"; then
    echo "✓ Successfully connected to $URL"
    
    # For now, let's at least grab the HTML content
    curl -s "$URL" > "${OUTPUT%.png}.html"
    echo "HTML content saved to: ${OUTPUT%.png}.html"
    
    # TODO: Need proper headless browser solution for Docker
    echo "Note: Full screenshot capability requires headless browser in Docker"
else
    echo "✗ Failed to connect to $URL"
    exit 1
fi
