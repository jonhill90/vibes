#!/usr/bin/env python3

import asyncio
import json
import os
from datetime import datetime
from zoneinfo import ZoneInfo
from dotenv import load_dotenv
from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import Tool, TextContent


class TimeServer:
    def __init__(self):
        # Load environment variables from .env file
        load_dotenv()
        
        self.default_timezone = os.getenv('DEFAULT_TIMEZONE', 'UTC')
        self.server_name = os.getenv('SERVER_NAME', 'mcp-time-server')
        self.debug = os.getenv('DEBUG', 'false').lower() == 'true'
        
        self.server = Server(self.server_name)
        
        # Timezone abbreviation mappings
        self.timezone_mappings = {
            'EST': 'America/New_York',    # Eastern Standard Time
            'EDT': 'America/New_York',    # Eastern Daylight Time
            'CST': 'America/Chicago',     # Central Standard Time
            'CDT': 'America/Chicago',     # Central Daylight Time
            'MST': 'America/Denver',      # Mountain Standard Time
            'MDT': 'America/Denver',      # Mountain Daylight Time
            'PST': 'America/Los_Angeles', # Pacific Standard Time
            'PDT': 'America/Los_Angeles', # Pacific Daylight Time
            'GMT': 'GMT',                 # Greenwich Mean Time
            'UTC': 'UTC',                 # Coordinated Universal Time
            'BST': 'Europe/London',       # British Summer Time
            'CET': 'Europe/Paris',        # Central European Time
            'JST': 'Asia/Tokyo',          # Japan Standard Time
            'AEST': 'Australia/Sydney',   # Australian Eastern Standard Time
            'IST': 'Asia/Kolkata',        # India Standard Time
        }
        
        self.setup_handlers()
        
        if self.debug:
            print(f"Time Server initialized with default timezone: {self.default_timezone}")

    def resolve_timezone(self, timezone_input: str = None) -> str:
        """Resolve timezone input to IANA timezone name"""
        if timezone_input is None:
            timezone_input = self.default_timezone
            
        timezone_upper = timezone_input.upper()
        
        # Check if it's a known abbreviation
        if timezone_upper in self.timezone_mappings:
            return self.timezone_mappings[timezone_upper]
        
        # Otherwise, assume it's already an IANA timezone name
        return timezone_input

    def setup_handlers(self):
        @self.server.list_tools()
        async def list_tools() -> list[Tool]:
            return [
                Tool(
                    name="get_current_time",
                    description=f"Get current time in a specific timezone (default: {self.default_timezone}). Supports timezone abbreviations like EST, PST, GMT, UTC, etc., or IANA names like America/New_York",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "timezone": {
                                "type": "string",
                                "description": f"Timezone name (IANA format like 'America/New_York') or abbreviation (EST, PST, GMT, UTC, etc.). Defaults to {self.default_timezone}",
                                "default": self.default_timezone
                            }
                        }
                    }
                ),
                Tool(
                    name="get_timestamp",
                    description="Get current Unix timestamp",
                    inputSchema={
                        "type": "object",
                        "properties": {}
                    }
                ),
                Tool(
                    name="format_time",
                    description=f"Format a timestamp to a readable date/time in specified timezone (default: {self.default_timezone})",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "timestamp": {
                                "type": "number",
                                "description": "Unix timestamp to format"
                            },
                            "timezone": {
                                "type": "string",
                                "description": f"Timezone name (IANA format like 'America/New_York') or abbreviation (EST, PST, GMT, UTC, etc.). Defaults to {self.default_timezone}",
                                "default": self.default_timezone
                            }
                        },
                        "required": ["timestamp"]
                    }
                ),
                Tool(
                    name="list_supported_timezones",
                    description="List all supported timezone abbreviations and their IANA equivalents",
                    inputSchema={
                        "type": "object",
                        "properties": {}
                    }
                )
            ]

        @self.server.call_tool()
        async def call_tool(name: str, arguments: dict) -> list[TextContent]:
            try:
                if name == "get_current_time":
                    timezone = arguments.get("timezone")
                    result = self.get_current_time(timezone)
                elif name == "get_timestamp":
                    result = self.get_timestamp()
                elif name == "format_time":
                    timestamp = arguments.get("timestamp")
                    timezone = arguments.get("timezone")
                    result = self.format_time(timestamp, timezone)
                elif name == "list_supported_timezones":
                    result = self.list_supported_timezones()
                else:
                    raise ValueError(f"Unknown tool: {name}")
                
                return [TextContent(
                    type="text",
                    text=json.dumps(result, indent=2)
                )]
            except Exception as e:
                return [TextContent(
                    type="text", 
                    text=f"Error: {str(e)}"
                )]

    def get_current_time(self, timezone_input: str = None) -> dict:
        """Get current time in specified timezone"""
        try:
            original_input = timezone_input or self.default_timezone
            iana_timezone = self.resolve_timezone(timezone_input)
            
            if iana_timezone.upper() == "UTC":
                tz = ZoneInfo("UTC")
            else:
                tz = ZoneInfo(iana_timezone)
            
            now = datetime.now(tz)
            
            return {
                "requested_timezone": original_input,
                "iana_timezone": iana_timezone,
                "datetime": now.isoformat(),
                "formatted": now.strftime("%Y-%m-%d %H:%M:%S %Z"),
                "timestamp": int(now.timestamp()),
                "day_of_week": now.strftime("%A"),
                "date": now.strftime("%Y-%m-%d"),
                "time": now.strftime("%H:%M:%S"),
                "timezone_offset": now.strftime("%z")
            }
        except Exception as e:
            raise ValueError(f"Invalid timezone '{original_input}': {str(e)}")

    def get_timestamp(self) -> dict:
        """Get current Unix timestamp"""
        now = datetime.now()
        return {
            "timestamp": int(now.timestamp()),
            "iso": now.isoformat(),
            "utc_iso": datetime.utcnow().isoformat() + "Z"
        }

    def format_time(self, timestamp: float, timezone_input: str = None) -> dict:
        """Format timestamp to readable date/time"""
        try:
            original_input = timezone_input or self.default_timezone
            iana_timezone = self.resolve_timezone(timezone_input)
            
            if iana_timezone.upper() == "UTC":
                tz = ZoneInfo("UTC")
            else:
                tz = ZoneInfo(iana_timezone)
            
            dt = datetime.fromtimestamp(timestamp, tz)
            
            return {
                "timestamp": timestamp,
                "requested_timezone": original_input,
                "iana_timezone": iana_timezone,
                "datetime": dt.isoformat(),
                "formatted": dt.strftime("%Y-%m-%d %H:%M:%S %Z"),
                "day_of_week": dt.strftime("%A"),
                "day_of_year": dt.timetuple().tm_yday,
                "date": dt.strftime("%Y-%m-%d"),
                "time": dt.strftime("%H:%M:%S"),
                "timezone_offset": dt.strftime("%z")
            }
        except Exception as e:
            raise ValueError(f"Error formatting timestamp: {str(e)}")

    def list_supported_timezones(self) -> dict:
        """List all supported timezone abbreviations"""
        return {
            "default_timezone": self.default_timezone,
            "supported_abbreviations": {
                abbr: {
                    "iana_name": iana,
                    "description": self._get_timezone_description(abbr)
                }
                for abbr, iana in self.timezone_mappings.items()
            },
            "note": "You can also use any valid IANA timezone name directly (e.g., America/New_York, Europe/London, Asia/Tokyo)"
        }

    def _get_timezone_description(self, abbr: str) -> str:
        """Get description for timezone abbreviation"""
        descriptions = {
            'EST': 'Eastern Standard Time (US)',
            'EDT': 'Eastern Daylight Time (US)',
            'CST': 'Central Standard Time (US)',
            'CDT': 'Central Daylight Time (US)',
            'MST': 'Mountain Standard Time (US)',
            'MDT': 'Mountain Daylight Time (US)',
            'PST': 'Pacific Standard Time (US)',
            'PDT': 'Pacific Daylight Time (US)',
            'GMT': 'Greenwich Mean Time',
            'UTC': 'Coordinated Universal Time',
            'BST': 'British Summer Time',
            'CET': 'Central European Time',
            'JST': 'Japan Standard Time',
            'AEST': 'Australian Eastern Standard Time',
            'IST': 'India Standard Time',
        }
        return descriptions.get(abbr, f"{abbr} timezone")

    async def run(self):
        options = self.server.create_initialization_options()
        async with stdio_server() as (read_stream, write_stream):
            await self.server.run(read_stream, write_stream, options)


async def main():
    server = TimeServer()
    await server.run()


if __name__ == "__main__":
    asyncio.run(main())
