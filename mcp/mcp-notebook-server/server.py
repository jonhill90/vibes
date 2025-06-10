#!/usr/bin/env python3
"""
INMPARA Notebook MCP Server Entry Point

Simple entry point for the INMPARA (Intelligent Note-taking, Management, 
Processing, Analysis, Retrieval, and Automation) MCP Server.

This entry point loads the main server class and starts the MCP protocol handler.
"""
import sys
import os

# Add src to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))
os.chdir(os.path.join(os.path.dirname(__file__), 'src'))

def main():
    """Main entry point for the INMPARA MCP Server."""
    try:
        from server.mcp_server import INMPARAServer
        server = INMPARAServer()
        server.run()
    except ImportError as e:
        print(f"Failed to import server components: {e}")
        print("Make sure you're running from the correct directory and all dependencies are installed.")
        sys.exit(1)
    except Exception as e:
        print(f"Failed to start server: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
