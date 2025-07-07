#!/usr/bin/env python3
"""
Test script for the MCP Time Server with .env configuration and timezone support
"""

from server import TimeServer
import time

def test_time_server():
    print("🕐 Testing MCP Time Server with .env configuration")
    print("=" * 60)
    
    # Initialize server
    server = TimeServer()
    print(f"✅ Server initialized with default timezone: {server.default_timezone}")
    print(f"✅ Server name: {server.server_name}")
    print()
    
    # Test timezone resolution
    print("🌍 Testing timezone resolution:")
    test_timezones = ['EST', 'PST', 'UTC', 'GMT', 'JST', 'America/Chicago']
    for tz in test_timezones:
        resolved = server.resolve_timezone(tz)
        print(f"   {tz:<15} -> {resolved}")
    print()
    
    # Test current time with different timezones
    print("🕒 Testing current time in different timezones:")
    for tz in ['EST', 'PST', 'UTC', 'JST']:
        result = server.get_current_time(tz)
        print(f"   {tz:<3}: {result['formatted']}")
    print()
    
    # Test default timezone (using .env configuration)
    print("⚙️  Testing default timezone from .env:")
    result = server.get_current_time()
    print(f"   Default ({result['requested_timezone']}): {result['formatted']}")
    print()
    
    # Test timestamp functions
    print("📅 Testing timestamp functions:")
    ts_result = server.get_timestamp()
    print(f"   Current timestamp: {ts_result['timestamp']}")
    
    # Test formatting timestamp
    format_result = server.format_time(ts_result['timestamp'], 'PST')
    print(f"   Formatted in PST: {format_result['formatted']}")
    print()
    
    # Test supported timezones
    print("🗺️  Testing supported timezones list:")
    tz_list = server.list_supported_timezones()
    print(f"   Default: {tz_list['default_timezone']}")
    print(f"   Supported abbreviations: {len(tz_list['supported_abbreviations'])} timezones")
    print("   Examples:")
    for abbr in ['EST', 'PST', 'UTC', 'JST']:
        info = tz_list['supported_abbreviations'][abbr]
        print(f"     {abbr} -> {info['iana_name']} ({info['description']})")
    
    print("\n✅ All tests completed successfully!")

if __name__ == "__main__":
    test_time_server()
