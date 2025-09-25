#!/bin/bash

# IT Glue MCP Server Startup Script
echo "Starting IT Glue MCP Server..."

# Check for required environment variables
if [ -z "$ITGLUE_API_KEY" ]; then
    echo "ERROR: ITGLUE_API_KEY environment variable is required"
    exit 1
fi

# Load environment variables from .env file if it exists
if [ -f .env ]; then
    echo "Loading environment from .env file"
    export $(cat .env | xargs)
fi

# Start the MCP server
echo "Connecting to IT Glue at: ${ITGLUE_BASE_URL:-https://api.itglue.com}"
echo "Debug mode: ${DEBUG:-false}"

python3 server.py
