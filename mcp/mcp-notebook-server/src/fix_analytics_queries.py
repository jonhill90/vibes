import re

with open('phase3_tools_prod.py', 'r') as f:
    content = f.read()

# Fix the learning patterns query to use existing columns
learning_patterns_fix = '''            # Learning patterns statistics
            cursor = conn.execute("""
                SELECT 
                    pattern_type,
                    COUNT(*) as pattern_count,
                    AVG(confidence) as avg_confidence,
                    MAX(last_updated) as last_updated
                FROM learning_patterns
                GROUP BY pattern_type
                ORDER BY pattern_count DESC
            """)'''

# Replace the learning patterns query
content = re.sub(
    r'# Learning patterns statistics.*?ORDER BY pattern_count DESC\s*"""\)',
    learning_patterns_fix,
    content,
    flags=re.DOTALL
)

with open('phase3_tools_prod.py', 'w') as f:
    f.write(content)

print("Fixed analytics queries to match database schema")
