#!/usr/bin/env python3
import sys, urllib.request, urllib.parse, os
from pathlib import Path

# Load API key from .env file
api_key = ''
env_file = Path(__file__).parent.parent.parent / '.env'
if env_file.exists():
    with open(env_file) as f:
        for line in f:
            line = line.strip()
            if line.startswith('CONTEXT7_API_KEY='):
                api_key = line.split('=', 1)[1].strip().strip('"').strip("'")
                break
# Fallback to environment variable
if not api_key:
    api_key = os.getenv('CONTEXT7_API_KEY', '')
params = {'libraryId': sys.argv[1], 'query': sys.argv[2]}
url = f"https://context7.com/api/v2/context?{urllib.parse.urlencode(params)}"
req = urllib.request.Request(url)
if api_key: req.add_header('Authorization', f'Bearer {api_key}')

try:
    with urllib.request.urlopen(req) as response:
        print(response.read().decode())
except Exception as e:
    print(f"Error: {e}", file=sys.stderr)
    sys.exit(1)
