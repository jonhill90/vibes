# Visual Tools

Tools for capturing screenshots, generating images, and visual inspection of web pages and applications.

## Available Tools

### `take-screenshot.sh`
Core screenshot functionality using the browserless MCP server.

**Usage:**
```bash
./take-screenshot.sh [URL] [OUTPUT_PATH]
```

**Examples:**
```bash
# Screenshot with default output
./take-screenshot.sh https://google.com

# Screenshot with custom path
./take-screenshot.sh https://example.com /workspace/vibes/screenshots/example.png
```

### `view.sh`
Screenshot wrapper that adds timestamps and file information.

**Usage:**
```bash
./view.sh [URL]
```

**Features:**
- Automatic timestamped filenames
- File size and type information
- Creates screenshots directory if needed

### `screenshot.sh`
Legacy tool that captures HTML content when full browser automation isn't available.

**Usage:**
```bash
./screenshot.sh [URL] [OUTPUT]
```

## Dependencies

- **Browserless MCP Server** running on port 9333
- **curl** for HTTP requests
- **Docker network access** to `host.docker.internal`

## Output

All screenshots are saved to `/workspace/vibes/screenshots/` by default.

## Future Tools

Potential additions to this category:
- PDF generation tools
- Image processing/manipulation
- Video capture tools
- OCR and text extraction
- Image comparison and diffing
