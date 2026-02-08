#!/bin/bash
# Fetch documentation from Context7

if [ $# -lt 2 ]; then
    echo "Usage: fetch-docs.sh <library-id> <query>" >&2
    exit 1
fi

LIBRARY_ID="$1"
QUERY="$2"

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
ENCODED_LIB=$(printf %s "$LIBRARY_ID" | jq -sRr @uri)
ENCODED_QUERY=$(printf %s "$QUERY" | jq -sRr @uri)
URL="https://context7.com/api/v2/context?libraryId=${ENCODED_LIB}&query=${ENCODED_QUERY}"

# Make request and display
if [ -n "$API_KEY" ]; then
    curl -s -H "Authorization: Bearer $API_KEY" "$URL"
else
    curl -s "$URL"
fi
