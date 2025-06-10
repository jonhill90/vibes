import re

with open('phase3_tools_prod.py', 'r') as f:
    content = f.read()

# Fix the user feedback query to use feedback_date instead of timestamp
feedback_fix = '''            # User feedback analysis
            cursor = conn.execute("""
                SELECT 
                    action_type,
                    COUNT(*) as feedback_count,
                    AVG(confidence_impact) as avg_confidence_impact
                FROM user_feedback
                WHERE feedback_date >= datetime('now', '-{} days')
                GROUP BY action_type
            """.format(days_back))'''

# Replace the user feedback query
content = re.sub(
    r'# User feedback analysis.*?GROUP BY action_type\s*"""\)',
    feedback_fix,
    content,
    flags=re.DOTALL
)

with open('phase3_tools_prod.py', 'w') as f:
    f.write(content)

print("Fixed user feedback query")
