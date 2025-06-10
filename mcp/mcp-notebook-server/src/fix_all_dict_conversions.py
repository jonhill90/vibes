import re

with open('phase3_tools_prod.py', 'r') as f:
    content = f.read()

# Fix all dict(row) calls in list comprehensions
patterns = [
    (r'activity_data = \[dict\(row\) for row in cursor\.fetchall\(\)\]',
     'activity_data = [dict(zip([desc[0] for desc in cursor.description], row)) for row in cursor.fetchall()]'),
    (r'learning_stats = \[dict\(row\) for row in cursor\.fetchall\(\)\]', 
     'learning_stats = [dict(zip([desc[0] for desc in cursor.description], row)) for row in cursor.fetchall()]'),
    (r'feedback_stats = \[dict\(row\) for row in cursor\.fetchall\(\)\]',
     'feedback_stats = [dict(zip([desc[0] for desc in cursor.description], row)) for row in cursor.fetchall()]')
]

for pattern, replacement in patterns:
    content = re.sub(pattern, replacement, content)

with open('phase3_tools_prod.py', 'w') as f:
    f.write(content)

print("Fixed all dict conversions in production version")
