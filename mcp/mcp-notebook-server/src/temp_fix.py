import re

# Read the file
with open('phase3_tools.py', 'r') as f:
    content = f.read()

# Fix the session_stats line
content = re.sub(
    r'session_stats = dict\(cursor\.fetchone\(\)\)',
    'session_stats_row = cursor.fetchone()\n            session_stats = dict(session_stats_row) if session_stats_row else {}',
    content
)

# Write back
with open('phase3_tools.py', 'w') as f:
    f.write(content)

print("Fixed session_stats dictionary conversion")
