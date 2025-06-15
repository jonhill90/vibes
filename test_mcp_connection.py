#!/usr/bin/env python3
"""
Test MCP Middleware Connection

Tests the SSE connection and basic MCP functionality.
"""

import asyncio
import json
import aiohttp
import sys
from typing import Dict, Any

async def test_sse_connection(url: str):
    """Test SSE connection to MCP middleware."""
    print(f"Testing SSE connection to {url}")
    
    try:
        async with aiohttp.ClientSession() as session:
            headers = {"Accept": "text/event-stream"}
            async with session.get(url, headers=headers) as response:
                print(f"Response status: {response.status}")
                print(f"Response headers: {dict(response.headers)}")
                
                if response.status == 200:
                    # Read the first few lines
                    count = 0
                    async for line in response.content:
                        line_str = line.decode('utf-8').strip()
                        if line_str:
                            print(f"SSE Line {count}: {line_str}")
                            count += 1
                            if count >= 5:  # Just read first few lines
                                break
                    print("✅ SSE connection successful!")
                    return True
                else:
                    print(f"❌ SSE connection failed with status {response.status}")
                    return False
                    
    except Exception as e:
        print(f"❌ SSE connection error: {e}")
        return False

async def test_health_endpoint(url: str):
    """Test health endpoint."""
    print(f"Testing health endpoint: {url}")
    
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                if response.status == 200:
                    data = await response.json()
                    print(f"✅ Health check successful: {data}")
                    return True
                else:
                    print(f"❌ Health check failed with status {response.status}")
                    return False
    except Exception as e:
        print(f"❌ Health check error: {e}")
        return False

async def test_mcp_post_message(base_url: str):
    """Test posting a message to the MCP endpoint."""
    url = f"{base_url}/messages/"
    print(f"Testing MCP POST message to {url}")
    
    # Basic MCP initialize request
    mcp_request = {
        "jsonrpc": "2.0",
        "id": "1",
        "method": "initialize",
        "params": {
            "protocolVersion": "2024-11-05",
            "capabilities": {},
            "clientInfo": {
                "name": "test-client",
                "version": "1.0.0"
            }
        }
    }
    
    try:
        async with aiohttp.ClientSession() as session:
            headers = {
                "Content-Type": "application/json",
                "Accept": "application/json, text/event-stream"
            }
            async with session.post(url, json=mcp_request, headers=headers) as response:
                print(f"Response status: {response.status}")
                print(f"Response headers: {dict(response.headers)}")
                
                if response.status in [200, 202]:
                    text = await response.text()
                    print(f"✅ MCP POST successful: {text[:200]}...")
                    return True
                else:
                    print(f"❌ MCP POST failed with status {response.status}")
                    text = await response.text()
                    print(f"Response: {text[:200]}...")
                    return False
                    
    except Exception as e:
        print(f"❌ MCP POST error: {e}")
        return False

async def main():
    """Main test function."""
    base_url = "http://host.docker.internal:5001"
    health_url = f"{base_url}/health"
    sse_url = f"{base_url}/sse"
    
    print("🧪 Testing MCP Middleware Server")
    print("=" * 50)
    
    # Test health endpoint
    health_ok = await test_health_endpoint(health_url)
    
    # Test SSE connection
    sse_ok = await test_sse_connection(sse_url)
    
    # Test MCP message posting
    post_ok = await test_mcp_post_message(base_url)
    
    print("\n" + "=" * 50)
    print("📊 Test Results:")
    print(f"  Health endpoint: {'✅' if health_ok else '❌'}")
    print(f"  SSE connection:  {'✅' if sse_ok else '❌'}")  
    print(f"  MCP POST:        {'✅' if post_ok else '❌'}")
    
    all_passed = health_ok and sse_ok and post_ok
    print(f"\n🎯 Overall: {'✅ ALL TESTS PASSED' if all_passed else '❌ SOME TESTS FAILED'}")
    
    return 0 if all_passed else 1

if __name__ == "__main__":
    try:
        result = asyncio.run(main())
        sys.exit(result)
    except KeyboardInterrupt:
        print("\n⚠️ Test interrupted by user")
        sys.exit(1)
