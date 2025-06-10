#!/usr/bin/env python3
"""
INMPARA MCP Server Start Script

Simple wrapper that ensures the server starts correctly for MCP connections.
"""
import sys
import os
import signal

# Add src to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

def signal_handler(signum, frame):
    """Handle shutdown signals gracefully."""
    print("Received shutdown signal, exiting gracefully...", file=sys.stderr)
    sys.exit(0)

def main():
    """Main entry point for the INMPARA MCP Server."""
    # Register signal handlers
    signal.signal(signal.SIGTERM, signal_handler)
    signal.signal(signal.SIGINT, signal_handler)
    
    try:
        # Change to src directory for proper imports
        os.chdir(os.path.join(os.path.dirname(__file__), 'src'))
        
        from server.mcp_server import INMPARAServer
        server = INMPARAServer()
        server.run()
        
    except ImportError as e:
        print(f"Failed to import server components: {e}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Failed to start server: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()
