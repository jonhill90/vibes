#!/usr/bin/env python3
"""
Monitoring patch for MCP Vibesbox Server
Adds operation logging capabilities to send data to the monitor app
"""

import json
import requests
import asyncio
from datetime import datetime
from typing import Dict, Any, Optional
import logging

logger = logging.getLogger(__name__)

class VibesboxMonitor:
    def __init__(self, monitor_host="mcp-vibesbox-monitor", monitor_port=8000):
        self.monitor_url = f"http://{monitor_host}:{monitor_port}"
        self.enabled = True
        
    async def log_operation(self, 
                          operation: str, 
                          details: Dict[str, Any],
                          screenshot_before: Optional[str] = None,
                          screenshot_after: Optional[str] = None):
        """Log an operation to the monitoring system"""
        if not self.enabled:
            return
            
        try:
            operation_data = {
                "timestamp": datetime.now().isoformat(),
                "operation": operation,
                "details": details,
                "screenshot_before": screenshot_before,
                "screenshot_after": screenshot_after
            }
            
            # Send to monitor API (non-blocking)
            requests.post(
                f"{self.monitor_url}/api/operations",
                json=operation_data,
                timeout=1.0  # Quick timeout to not block operations
            )
            logger.info(f"Logged operation: {operation}")
            
        except Exception as e:
            logger.warning(f"Failed to log operation to monitor: {e}")
            # Don't fail the actual operation if monitoring fails

    def disable(self):
        """Disable monitoring"""
        self.enabled = False
        
    def enable(self):
        """Enable monitoring"""
        self.enabled = True

# Global monitor instance
monitor = VibesboxMonitor()

# Helper function to capture screenshot for monitoring
async def capture_screenshot_for_monitoring(display=":1"):
    """Capture screenshot and return base64 string for monitoring"""
    try:
        import subprocess
        import base64
        
        # Capture screenshot
        result = subprocess.run([
            "import", "-window", "root", "-display", display, "png:-"
        ], capture_output=True, check=True)
        
        # Convert to base64
        screenshot_b64 = base64.b64encode(result.stdout).decode('utf-8')
        return screenshot_b64
        
    except Exception as e:
        logger.warning(f"Failed to capture screenshot for monitoring: {e}")
        return None
