#!/bin/bash
# Search for Context7 library IDs

if [ $# -lt 1 ]; then
    echo "Usage: search.sh <library-name> [query]" >&2
    exit 1
fi

LIBRARY_NAME="$1"
QUERY="${2:-$1}"

# Load API key from .env file
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ENV_FILE="$SCRIPT_DIR/../../.env"
API_KEY=""
if [ -f "$ENV_FILE" ]; then
    API_KEY=$(grep "^CONTEXT7_API_KEY=" "$ENV_FILE" | cut -d'=' -f2- | tr -d '"' | tr -d "'")
fi
# Fallback to environment variable
if [ -z "$API_KEY" ]; then
    API_KEY="${CONTEXT7_API_KEY:-}"
fi

# URL encode parameters
ENCODED_LIB=$(printf %s "$LIBRARY_NAME" | jq -sRr @uri)
ENCODED_QUERY=$(printf %s "$QUERY" | jq -sRr @uri)
URL="https://context7.com/api/v2/libs/search?libraryName=${ENCODED_LIB}&query=${ENCODED_QUERY}"

# Make request
if [ -n "$API_KEY" ]; then
    RESPONSE=$(curl -s -H "Authorization: Bearer $API_KEY" "$URL")
else
    RESPONSE=$(curl -s "$URL")
fi

# Parse and display results
echo "Available Libraries:"
echo ""
echo "$RESPONSE" | jq -r '.results[] | "- **\(.title // "Unknown")**\n  ID: `\(.id // "N/A")`\n  Description: \(.description // "No description")\n  Snippets: \(.totalSnippets // 0)\n"'
