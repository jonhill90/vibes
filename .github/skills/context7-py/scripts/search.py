#!/usr/bin/env python3
import sys, json, urllib.request, urllib.parse, os
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
params = {'libraryName': sys.argv[1], 'query': sys.argv[2] if len(sys.argv) > 2 else sys.argv[1]}
url = f"https://context7.com/api/v2/libs/search?{urllib.parse.urlencode(params)}"
req = urllib.request.Request(url)
if api_key: req.add_header('Authorization', f'Bearer {api_key}')

try:
    with urllib.request.urlopen(req) as response:
        data = json.loads(response.read().decode())
        print("Available Libraries:\n")
        for lib in data.get('results', []):
            print(f"- **{lib.get('title', 'Unknown')}**")
            print(f"  ID: `{lib.get('id', 'N/A')}`")
            print(f"  Description: {lib.get('description', 'No description')}")
            print(f"  Snippets: {lib.get('totalSnippets', 0)}")
            print()
except Exception as e:
    print(f"Error: {e}", file=sys.stderr)
    sys.exit(1)
