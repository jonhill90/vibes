#!/usr/bin/env python3
"""Minimal analytics test"""

import sys
import os
import sqlite3
import tempfile

# Add src to path
sys.path.append('src')

def test_analytics_queries():
    """Test the analytics queries directly"""
    # Create a temporary database
    db_path = tempfile.mktemp(suffix='.db')
    conn = sqlite3.connect(db_path)
    
    # Create tables with correct schema
    conn.execute("""
        CREATE TABLE processing_log (
            id INTEGER PRIMARY KEY,
            action TEXT,
            confidence REAL,
            user_approved BOOLEAN,
            timestamp DATE DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    conn.execute("""
        CREATE TABLE learning_patterns (
            id INTEGER PRIMARY KEY,
            pattern_type TEXT,
            confidence REAL,
            last_updated DATE DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    conn.execute("""
        CREATE TABLE user_feedback (
            id INTEGER PRIMARY KEY,
            action_type TEXT,
            confidence_impact REAL,
            feedback_date DATE DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    conn.execute("""
        CREATE TABLE session_summaries (
            id INTEGER PRIMARY KEY,
            session_id TEXT,
            insights_captured INTEGER,
            start_time DATE DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    # Test each query
    queries = [
        # Processing activity
        """
        SELECT 
            DATE(timestamp) as date,
            action,
            COUNT(*) as count,
            AVG(confidence) as avg_confidence,
            SUM(CASE WHEN user_approved = 1 THEN 1 ELSE 0 END) as approved_count,
            SUM(CASE WHEN user_approved = 0 THEN 1 ELSE 0 END) as rejected_count
        FROM processing_log 
        WHERE timestamp >= datetime('now', '-30 days')
        GROUP BY DATE(timestamp), action
        ORDER BY date DESC
        """,
        
        # Learning patterns
        """
        SELECT 
            pattern_type,
            COUNT(*) as pattern_count,
            AVG(confidence) as avg_confidence,
            MAX(last_updated) as last_updated
        FROM learning_patterns
        GROUP BY pattern_type
        ORDER BY pattern_count DESC
        """,
        
        # User feedback
        """
        SELECT 
            action_type,
            COUNT(*) as feedback_count,
            AVG(confidence_impact) as avg_confidence_impact
        FROM user_feedback
        WHERE feedback_date >= datetime('now', '-30 days')
        GROUP BY action_type
        """,
        
        # Session stats
        """
        SELECT 
            COUNT(DISTINCT session_id) as total_sessions,
            COUNT(*) as total_summaries,
            AVG(insights_captured) as avg_insights_per_session
        FROM session_summaries
        WHERE start_time >= datetime('now', '-30 days')
        """
    ]
    
    for i, query in enumerate(queries):
        try:
            cursor = conn.execute(query)
            if i == 3:  # Session stats (single row)
                row = cursor.fetchone()
                if row:
                    columns = [desc[0] for desc in cursor.description]
                    result = dict(zip(columns, row))
                    print(f"✅ Query {i+1}: {result}")
                else:
                    print(f"✅ Query {i+1}: No data")
            else:  # List results
                rows = cursor.fetchall()
                columns = [desc[0] for desc in cursor.description]
                results = [dict(zip(columns, row)) for row in rows]
                print(f"✅ Query {i+1}: {len(results)} rows")
        except Exception as e:
            print(f"❌ Query {i+1} failed: {e}")
    
    conn.close()
    os.unlink(db_path)
    print("🎉 Analytics queries test complete!")

if __name__ == "__main__":
    test_analytics_queries()
