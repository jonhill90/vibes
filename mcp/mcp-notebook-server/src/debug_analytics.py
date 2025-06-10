import sqlite3
import tempfile
import os

# Create test database
db_path = tempfile.mktemp(suffix='.db')
conn = sqlite3.connect(db_path)

# Create minimal table structure
conn.execute("""
CREATE TABLE session_summaries (
    session_id TEXT,
    topic_count INTEGER,
    created_at TEXT
)
""")

# Test the query
cursor = conn.execute("""
    SELECT 
        COUNT(DISTINCT session_id) as total_sessions,
        COUNT(*) as total_summaries,
        AVG(topic_count) as avg_topics_per_session
    FROM session_summaries
    WHERE created_at >= datetime('now', '-30 days')
""")

row = cursor.fetchone()
print("Row type:", type(row))
print("Row content:", row)
print("Row length:", len(row) if row else "None")

try:
    result = dict(row) if row else {}
    print("Dict conversion successful:", result)
except Exception as e:
    print("Dict conversion error:", e)

# Clean up
conn.close()
os.unlink(db_path)
