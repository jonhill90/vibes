#!/usr/bin/env python3
import sys
import os
sys.path.append('/workspace/vibes/mcp/mcp-vibesbox-server')

# Import the functions directly from server.py
import subprocess
import tempfile
import base64

def run_vnc_command(command: str, display: str = ":1") -> subprocess.CompletedProcess:
    """Execute command in VNC environment with proper DISPLAY setting"""
    env = os.environ.copy()
    env["DISPLAY"] = display
    
    return subprocess.run(
        command,
        shell=True,
        env=env,
        capture_output=True,
        text=True,
        cwd="/workspace"
    )

def take_screenshot_base64(display: str = ":1") -> str:
    """Take screenshot and return as base64 encoded image"""
    with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as tmp_file:
        try:
            # Take screenshot using ImageMagick
            result = run_vnc_command(f"import -window root {tmp_file.name}", display)
            
            if result.returncode != 0:
                return f"Screenshot failed: {result.stderr}"
            
            # Read and encode as base64
            with open(tmp_file.name, "rb") as f:
                image_data = f.read()
                base64_data = base64.b64encode(image_data).decode('utf-8')
                return base64_data
        finally:
            if os.path.exists(tmp_file.name):
                os.unlink(tmp_file.name)

# Test functions
print("Testing screenshot...")
screenshot_result = take_screenshot_base64()
if screenshot_result.startswith("Screenshot failed"):
    print(f"❌ Screenshot test failed: {screenshot_result}")
else:
    print(f"✅ Screenshot test passed: {len(screenshot_result)} bytes of base64 data")

print("\nTesting desktop click...")
click_result = run_vnc_command("xdotool mousemove 200 200 click 1")
if click_result.returncode == 0:
    print("✅ Desktop click test passed")
else:
    print(f"❌ Desktop click test failed: {click_result.stderr}")

print("\nTesting text typing...")
type_result = run_vnc_command("xdotool type 'Hello World'")
if type_result.returncode == 0:
    print("✅ Text typing test passed")
else:
    print(f"❌ Text typing test failed: {type_result.stderr}")

print("\nTesting key combinations...")
key_result = run_vnc_command("xdotool key ctrl+a")
if key_result.returncode == 0:
    print("✅ Key combination test passed")
else:
    print(f"❌ Key combination test failed: {key_result.stderr}")
