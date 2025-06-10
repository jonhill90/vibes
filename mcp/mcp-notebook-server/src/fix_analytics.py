import re

# Read the file
with open('phase3_tools.py', 'r') as f:
    content = f.read()

# Fix the session_stats line - need to use row factory to get dict-like rows
fix_pattern = r'session_stats = dict\(cursor\.fetchone\(\) or \{\}\)'
replacement = '''session_stats_row = cursor.fetchone()
            if session_stats_row:
                columns = [desc[0] for desc in cursor.description]
                session_stats = dict(zip(columns, session_stats_row))
            else:
                session_stats = {
                    "total_sessions": 0,
                    "total_summaries": 0, 
                    "avg_topics_per_session": 0.0
                }'''

content = re.sub(fix_pattern, replacement, content)

# Write back
with open('phase3_tools.py', 'w') as f:
    f.write(content)

print("Fixed analytics session_stats conversion")
