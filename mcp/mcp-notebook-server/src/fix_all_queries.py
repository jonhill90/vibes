import re

with open('phase3_tools_prod.py', 'r') as f:
    content = f.read()

# Fix session_summaries query to use start_time and proper column names
session_fix = '''            # Session insights
            cursor = conn.execute("""
                SELECT 
                    COUNT(DISTINCT session_id) as total_sessions,
                    COUNT(*) as total_summaries,
                    AVG(insights_captured) as avg_insights_per_session
                FROM session_summaries
                WHERE start_time >= datetime('now', '-{} days')
            """.format(days_back))'''

# Replace the session query
content = re.sub(
    r'# Session insights.*?WHERE created_at >= datetime.*?"""\)',
    session_fix,
    content,
    flags=re.DOTALL
)

with open('phase3_tools_prod.py', 'w') as f:
    f.write(content)

print("Fixed session summaries query")
