#!/bin/bash
# Script to start the MCP consulting agent server

# Get the directory of this script
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"
cd "$SCRIPT_DIR"

# Activate the virtual environment
source mcp_venv/bin/activate

# Set the transport for Claude Code compatibility
export MCP_TRANSPORT=stdio

# Make sure API keys are available from .env file if it exists
if [ -f .env ]; then
    set -o allexport
    source .env
    set +o allexport
fi

# Run the MCP server with stdio transport
python mcp_consul_server.py