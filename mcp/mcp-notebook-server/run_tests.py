#!/usr/bin/env python3
"""Test runner for Phase 3"""

import os
import sys
import subprocess

# Change to script directory
os.chdir(os.path.dirname(os.path.abspath(__file__)))

# Add src to path
sys.path.insert(0, 'src')

# Try to run tests
try:
    result = subprocess.run([
        sys.executable, '-m', 'unittest', 'test_phase3', '-v'
    ], capture_output=True, text=True, cwd='.')
    
    print("Test Results:")
    print("=" * 50)
    print("STDOUT:")
    print(result.stdout)
    if result.stderr:
        print("STDERR:")
        print(result.stderr)
    print("Return code:", result.returncode)
    
except Exception as e:
    print(f"Test execution failed: {e}")
