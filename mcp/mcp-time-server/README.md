# MCP Time Server

A Model Context Protocol (MCP) server that provides time and timezone functionality with environment variable configuration support.

## Features

- 🕐 **Current time retrieval** in any timezone
- 🌍 **Timezone abbreviation support** (EST, PST, GMT, UTC, etc.)
- ⚙️ **Environment configuration** via `.env` file
- 📅 **Timestamp formatting** and conversion
- 🗺️ **Comprehensive timezone support** (IANA timezone names + common abbreviations)

## Quick Start

1. **Configure your timezone** in the `.env` file:
   ```bash
   cp .env.example .env
   # Edit .env to set your preferred timezone
   ```

2. **Run the server**:
   ```bash
   python3 server.py
   ```

## Configuration

### Environment Variables (.env file)

```bash
# Default timezone for the server
# Can be IANA timezone name (e.g., America/New_York, Europe/London)
# Or common abbreviations (EST, PST, GMT, UTC, etc.)
DEFAULT_TIMEZONE=EST

# Optional: Server name for identification
SERVER_NAME=mcp-time-server

# Optional: Enable debug logging
DEBUG=false
```

### Supported Timezone Abbreviations

The server supports common timezone abbreviations that are automatically converted to IANA timezone names:

| Abbreviation | IANA Timezone | Description |
|--------------|---------------|-------------|
| EST/EDT | America/New_York | Eastern Standard/Daylight Time |
| CST/CDT | America/Chicago | Central Standard/Daylight Time |
| MST/MDT | America/Denver | Mountain Standard/Daylight Time |
| PST/PDT | America/Los_Angeles | Pacific Standard/Daylight Time |
| GMT | GMT | Greenwich Mean Time |
| UTC | UTC | Coordinated Universal Time |
| BST | Europe/London | British Summer Time |
| CET | Europe/Paris | Central European Time |
| JST | Asia/Tokyo | Japan Standard Time |
| AEST | Australia/Sydney | Australian Eastern Standard Time |
| IST | Asia/Kolkata | India Standard Time |

You can also use any valid IANA timezone name directly (e.g., `America/New_York`, `Europe/London`, `Asia/Tokyo`).

## Available Tools

### 1. get_current_time
Get the current time in a specified timezone (or default timezone from .env).

**Parameters:**
- `timezone` (optional): Timezone name or abbreviation

**Example:**
```json
{
  "timezone": "EST"
}
```

**Response:**
```json
{
  "requested_timezone": "EST",
  "iana_timezone": "America/New_York",
  "datetime": "2025-07-06T22:56:44-04:00",
  "formatted": "2025-07-06 22:56:44 EDT",
  "timestamp": 1751857004,
  "day_of_week": "Sunday",
  "date": "2025-07-06",
  "time": "22:56:44",
  "timezone_offset": "-0400"
}
```

### 2. get_timestamp
Get the current Unix timestamp.

**Response:**
```json
{
  "timestamp": 1751857004,
  "iso": "2025-07-07T02:56:44.123456",
  "utc_iso": "2025-07-07T02:56:44.123456Z"
}
```

### 3. format_time
Format a Unix timestamp to a readable date/time in a specified timezone.

**Parameters:**
- `timestamp` (required): Unix timestamp to format
- `timezone` (optional): Timezone name or abbreviation

**Example:**
```json
{
  "timestamp": 1751857004,
  "timezone": "PST"
}
```

### 4. list_supported_timezones
List all supported timezone abbreviations and their IANA equivalents.

**Response:**
```json
{
  "default_timezone": "EST",
  "supported_abbreviations": {
    "EST": {
      "iana_name": "America/New_York",
      "description": "Eastern Standard Time (US)"
    }
  },
  "note": "You can also use any valid IANA timezone name directly"
}
```

## Docker Support

### Build and run with Docker:

```bash
# Build the image
docker build -t mcp-time-server .

# Run with docker-compose
docker-compose up -d
```

### Using in MCP client:

Add to your MCP client configuration:

```json
{
  "mcpServers": {
    "time": {
      "command": "python3",
      "args": ["/path/to/mcp-time-server/server.py"]
    }
  }
}
```

## Testing

Run the test script to verify functionality:

```bash
python3 test_time_server.py
```

## Examples

### Get current time in your default timezone (EST):
```bash
# Uses DEFAULT_TIMEZONE from .env
get_current_time()
```

### Get time in different timezones:
```bash
get_current_time({"timezone": "PST"})
get_current_time({"timezone": "UTC"})
get_current_time({"timezone": "Asia/Tokyo"})
```

### Format a timestamp:
```bash
format_time({
  "timestamp": 1751857004,
  "timezone": "EST"
})
```

## Notes

- The server automatically handles daylight saving time transitions
- EST/EDT, PST/PDT, etc. are treated as the same timezone (America/New_York, America/Los_Angeles) with automatic DST handling
- Invalid timezone names will return an error with suggestions
- All times are returned in both ISO format and human-readable format

## Dependencies

- Python 3.8+
- `mcp` package
- `python-dotenv` package
- `tzdata` (timezone database)

Install dependencies:
```bash
pip install mcp python-dotenv
# On Ubuntu/Debian: apt-get install tzdata
```
