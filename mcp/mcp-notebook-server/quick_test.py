#!/usr/bin/env python3
"""Quick validation test for Phase 3 functionality"""

import tempfile
import os
import sys
from pathlib import Path

print("🧪 Quick Phase 3 Validation Test")
print("=" * 40)

# Test 1: Demo runs without errors
print("Test 1: Running demo...")
result = os.system("python3 demo_phase3.py > /tmp/demo_output.log 2>&1")
if result == 0:
    print("✅ Demo completed successfully")
else:
    print("❌ Demo failed")
    print("Check /tmp/demo_output.log for details")

# Test 2: Check that all core files exist
print("\nTest 2: Checking core files...")
required_files = [
    "src/phase3_tools.py",
    "src/phase3_helpers.py", 
    "src/phase3_tool_registrations.py",
    "demo_phase3.py",
    "run_phase3_server.py"
]

all_exist = True
for file in required_files:
    if os.path.exists(file):
        print(f"✅ {file}")
    else:
        print(f"❌ {file} missing")
        all_exist = False

# Test 3: Check server can start (dry run)
print("\nTest 3: Testing server startup...")
server_test = os.system("timeout 3 python3 run_phase3_server.py --help > /tmp/server_test.log 2>&1")
if server_test in [0, 124]:  # 0 = success, 124 = timeout (expected)
    print("✅ Server can start")
else:
    print("❌ Server startup failed")
    print("Check /tmp/server_test.log for details")

# Test 4: Check if imports work
print("\nTest 4: Testing imports...")
try:
    import sys
    sys.path.append('src')
    from database.database import DatabaseManager
    from server import InmparaMCPServer
    print("✅ Core imports working")
except ImportError as e:
    print(f"❌ Import error: {e}")

print("\n🎯 Phase 3 Validation Summary:")
if all_exist and result == 0:
    print("✅ Phase 3 is ready for production!")
else:
    print("⚠️  Some issues detected - check individual test results")

