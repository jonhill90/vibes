import datetime
"""
INMPARA Notebook Server - Database Layer
Handles SQLite database operations for notes, tags, relationships, and learning patterns.
"""

import sqlite3
import json
import uuid
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any
import logging

logger = logging.getLogger(__name__)


class INMPARADatabase:
    """SQLite database for INMPARA vault metadata and learning patterns."""
    
    def __init__(self, db_path: str):
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._init_database()
    
    def _init_database(self):
        """Initialize database with required tables."""
        with sqlite3.connect(self.db_path) as conn:
            conn.executescript("""
                -- Note metadata and tracking
                CREATE TABLE IF NOT EXISTS notes (
                    id TEXT PRIMARY KEY,
                    title TEXT NOT NULL,
                    file_path TEXT UNIQUE,
                    content_type TEXT,
                    domain TEXT,
                    created_date DATE,
                    modified_date DATE,
                    confidence_score REAL,
                    source_type TEXT,
                    word_count INTEGER,
                    character_count INTEGER,
                    content_hash TEXT,
                    last_processed DATE,
                    frontmatter_json TEXT
                );

                -- Dynamic tagging system
                CREATE TABLE IF NOT EXISTS tags (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    note_id TEXT,
                    tag TEXT,
                    tag_type TEXT,
                    confidence REAL DEFAULT 1.0,
                    source TEXT,
                    created_date DATE DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (note_id) REFERENCES notes(id)
                );

                -- Semantic relationships
                CREATE TABLE IF NOT EXISTS relationships (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    source_note_id TEXT,
                    target_note_id TEXT,
                    relationship_type TEXT,
                    confidence REAL DEFAULT 1.0,
                    context TEXT,
                    source TEXT,
                    created_date DATE DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (source_note_id) REFERENCES notes(id)
                );

                -- Conversation insights tracking
                CREATE TABLE IF NOT EXISTS conversation_insights (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    session_id TEXT,
                    insight_text TEXT,
                    note_id TEXT,
                    confidence REAL,
                    insight_type TEXT,
                    domains TEXT,
                    created_date DATE DEFAULT CURRENT_TIMESTAMP,
                    processed BOOLEAN DEFAULT FALSE,
                    FOREIGN KEY (note_id) REFERENCES notes(id)
                );

                -- Learning and feedback tracking
                CREATE TABLE IF NOT EXISTS learning_patterns (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    pattern_type TEXT,
                    pattern_data TEXT,
                    confidence REAL,
                    usage_count INTEGER DEFAULT 1,
                    success_rate REAL,
                    last_updated DATE DEFAULT CURRENT_TIMESTAMP
                );

                -- User feedback and corrections
                CREATE TABLE IF NOT EXISTS user_feedback (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    action_type TEXT,
                    original_value TEXT,
                    corrected_value TEXT,
                    note_id TEXT,
                    confidence_impact REAL,
                    feedback_date DATE DEFAULT CURRENT_TIMESTAMP,
                    processed BOOLEAN DEFAULT FALSE,
                    FOREIGN KEY (note_id) REFERENCES notes(id)
                );

                -- Processing audit trail
                CREATE TABLE IF NOT EXISTS processing_log (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    action TEXT,
                    source_path TEXT,
                    destination_path TEXT,
                    confidence REAL,
                    reasoning TEXT,
                    user_approved BOOLEAN,
                    timestamp DATE DEFAULT CURRENT_TIMESTAMP
                );

                -- Session tracking tables for Phase 2
                CREATE TABLE IF NOT EXISTS conversation_sessions (
                    session_id TEXT PRIMARY KEY,
                    start_time DATE,
                    last_activity DATE,
                    topics TEXT,
                    domains TEXT,
                    context_summary TEXT
                );

                CREATE TABLE IF NOT EXISTS session_summaries (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    session_id TEXT,
                    start_time DATE,
                    end_time DATE,
                    duration_minutes REAL,
                    topics_covered TEXT,
                    domains_explored TEXT,
                    insights_captured INTEGER,
                    notes_created INTEGER,
                    final_context TEXT
                );

                CREATE TABLE IF NOT EXISTS session_topics (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    session_id TEXT,
                    topic TEXT
                );

                CREATE TABLE IF NOT EXISTS session_domains (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    session_id TEXT,
                    domain TEXT
                );


                -- Indexes for performance
                CREATE INDEX IF NOT EXISTS idx_notes_file_path ON notes(file_path);
                CREATE INDEX IF NOT EXISTS idx_notes_content_type ON notes(content_type);
                CREATE INDEX IF NOT EXISTS idx_notes_domain ON notes(domain);
                CREATE INDEX IF NOT EXISTS idx_tags_note_id ON tags(note_id);
                CREATE INDEX IF NOT EXISTS idx_tags_tag ON tags(tag);
                CREATE INDEX IF NOT EXISTS idx_relationships_source ON relationships(source_note_id);
                CREATE INDEX IF NOT EXISTS idx_relationships_target ON relationships(target_note_id);
                CREATE INDEX IF NOT EXISTS idx_insights_session ON conversation_insights(session_id);
                CREATE INDEX IF NOT EXISTS idx_insights_processed ON conversation_insights(processed);
            """)
            logger.info("Database initialized successfully")

    def add_note(self, note_data: Dict[str, Any]) -> str:
        """Add a new note to the database."""
        note_id = str(uuid.uuid4())
        
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                INSERT INTO notes (
                    id, title, file_path, content_type, domain, created_date,
                    modified_date, confidence_score, source_type, word_count,
                    character_count, content_hash, last_processed, frontmatter_json
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                note_id,
                note_data.get('title'),
                note_data.get('file_path'),
                note_data.get('content_type'),
                note_data.get('domain'),
                note_data.get('created_date'),
                note_data.get('modified_date'),
                note_data.get('confidence_score'),
                note_data.get('source_type'),
                note_data.get('word_count'),
                note_data.get('character_count'),
                note_data.get('content_hash'),
                datetime.now().isoformat(),
                json.dumps(note_data.get('frontmatter', {}))
            ))
            
            # Add tags
            for tag_data in note_data.get('tags', []):
                self.add_tag(note_id, tag_data)
            
            # Add relationships
            for rel_data in note_data.get('relationships', []):
                self.add_relationship(note_id, rel_data)
        
        logger.info(f"Added note {note_id}: {note_data.get('title')}")
        return note_id

    def add_tag(self, note_id: str, tag_data: Dict[str, Any]):
        """Add a tag to a note."""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                INSERT INTO tags (note_id, tag, tag_type, confidence, source)
                VALUES (?, ?, ?, ?, ?)
            """, (
                note_id,
                tag_data.get('tag'),
                tag_data.get('tag_type', 'auto'),
                tag_data.get('confidence', 1.0),
                tag_data.get('source', 'auto')
            ))

    def add_relationship(self, source_note_id: str, rel_data: Dict[str, Any]):
        """Add a relationship between notes."""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                INSERT INTO relationships (
                    source_note_id, target_note_id, relationship_type,
                    confidence, context, source
                ) VALUES (?, ?, ?, ?, ?, ?)
            """, (
                source_note_id,
                rel_data.get('target_note_id'),
                rel_data.get('relationship_type'),
                rel_data.get('confidence', 1.0),
                rel_data.get('context', ''),
                rel_data.get('source', 'auto')
            ))

    def add_conversation_insight(self, insight_data: Dict[str, Any]) -> int:
        """Add a conversation insight to track."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute("""
                INSERT INTO conversation_insights (
                    session_id, insight_text, confidence, insight_type,
                    domains, note_id
                ) VALUES (?, ?, ?, ?, ?, ?)
            """, (
                insight_data.get('session_id'),
                insight_data.get('insight_text'),
                insight_data.get('confidence'),
                insight_data.get('insight_type'),
                json.dumps(insight_data.get('domains', [])),
                insight_data.get('note_id')
            ))
            return cursor.lastrowid

    def get_note_by_path(self, file_path: str) -> Optional[Dict[str, Any]]:
        """Retrieve note by file path."""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.execute("""
                SELECT * FROM notes WHERE file_path = ?
            """, (file_path,))
            row = cursor.fetchone()
            
            if row:
                note = dict(row)
                note['frontmatter'] = json.loads(note['frontmatter_json'] or '{}')
                
                # Get tags
                cursor = conn.execute("""
                    SELECT * FROM tags WHERE note_id = ?
                """, (note['id'],))
                note['tags'] = [dict(r) for r in cursor.fetchall()]
                
                # Get relationships
                cursor = conn.execute("""
                    SELECT * FROM relationships WHERE source_note_id = ?
                """, (note['id'],))
                note['relationships'] = [dict(r) for r in cursor.fetchall()]
                
                return note
        return None

    def search_notes(self, query: str = "", content_type: str = None, 
                    domain: str = None, limit: int = 20) -> List[Dict[str, Any]]:
        """Search notes with filters."""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            
            where_clauses = []
            params = []
            
            if query:
                where_clauses.append("(title LIKE ? OR file_path LIKE ?)")
                params.extend([f"%{query}%", f"%{query}%"])
            
            if content_type:
                where_clauses.append("content_type = ?")
                params.append(content_type)
            
            if domain:
                where_clauses.append("domain = ?")
                params.append(domain)
            
            where_clause = " AND ".join(where_clauses) if where_clauses else "1=1"
            
            cursor = conn.execute(f"""
                SELECT * FROM notes 
                WHERE {where_clause}
                ORDER BY modified_date DESC
                LIMIT ?
            """, params + [limit])
            
            return [dict(row) for row in cursor.fetchall()]

    def get_recent_insights(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get recent conversation insights."""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.execute("""
                SELECT * FROM conversation_insights
                ORDER BY created_date DESC
                LIMIT ?
            """, (limit,))
            
            insights = []
            for row in cursor.fetchall():
                insight = dict(row)
                insight['domains'] = json.loads(insight['domains'])
                insights.append(insight)
            
            return insights

    def update_note_confidence(self, note_id: str, new_confidence: float):
        """Update confidence score for a note."""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                UPDATE notes SET confidence_score = ? WHERE id = ?
            """, (new_confidence, note_id))

    def log_processing_action(self, action_data: Dict[str, Any]):
        """Log a processing action for audit trail."""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                INSERT INTO processing_log (
                    action, source_path, destination_path, confidence,
                    reasoning, user_approved
                ) VALUES (?, ?, ?, ?, ?, ?)
            """, (
                action_data.get('action'),
                action_data.get('source_path'),
                action_data.get('destination_path'),
                action_data.get('confidence'),
                action_data.get('reasoning'),
                action_data.get('user_approved')
            ))

    def add_user_feedback(self, feedback_data: Dict[str, Any]):
        """Record user feedback for learning."""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                INSERT INTO user_feedback (
                    action_type, original_value, corrected_value,
                    note_id, confidence_impact
                ) VALUES (?, ?, ?, ?, ?)
            """, (
                feedback_data.get('action_type'),
                feedback_data.get('original_value'),
                feedback_data.get('corrected_value'),
                feedback_data.get('note_id'),
                feedback_data.get('confidence_impact')
            ))

    def get_learning_patterns(self, pattern_type: str = None) -> List[Dict[str, Any]]:
        """Retrieve learning patterns."""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            
            if pattern_type:
                cursor = conn.execute("""
                    SELECT * FROM learning_patterns WHERE pattern_type = ?
                    ORDER BY success_rate DESC, usage_count DESC
                """, (pattern_type,))
            else:
                cursor = conn.execute("""
                    SELECT * FROM learning_patterns
                    ORDER BY success_rate DESC, usage_count DESC
                """)
            
            patterns = []
            for row in cursor.fetchall():
                pattern = dict(row)
                pattern['pattern_data'] = json.loads(pattern['pattern_data'])
                patterns.append(pattern)
            
            return patterns

    def update_learning_pattern(self, pattern_id: int, success: bool):
        """Update learning pattern based on success/failure."""
        with sqlite3.connect(self.db_path) as conn:
            # Get current pattern
            cursor = conn.execute("""
                SELECT usage_count, success_rate FROM learning_patterns WHERE id = ?
            """, (pattern_id,))
            row = cursor.fetchone()
            
            if row:
                usage_count, success_rate = row
                new_usage_count = usage_count + 1
                
                # Update success rate using exponential moving average
                alpha = 0.1  # Learning rate
                new_success_rate = success_rate * (1 - alpha) + (1.0 if success else 0.0) * alpha
                
                conn.execute("""
                    UPDATE learning_patterns 
                    SET usage_count = ?, success_rate = ?, last_updated = ?
                    WHERE id = ?
                """, (new_usage_count, new_success_rate, datetime.now().isoformat(), pattern_id))

    def get_processing_stats(self, days: int = 30) -> Dict[str, Any]:
        """Get processing statistics for the last N days."""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            
            cutoff_date = (datetime.now() - timedelta(days=days)).isoformat()
            
            # Count by action type
            cursor = conn.execute("""
                SELECT action, COUNT(*) as count, AVG(confidence) as avg_confidence
                FROM processing_log 
                WHERE timestamp >= ?
                GROUP BY action
            """, (cutoff_date,))
            
            action_stats = {row['action']: {
                'count': row['count'],
                'avg_confidence': row['avg_confidence']
            } for row in cursor.fetchall()}
            
            # Overall stats
            cursor = conn.execute("""
                SELECT 
                    COUNT(*) as total_actions,
                    AVG(confidence) as avg_confidence,
                    SUM(CASE WHEN user_approved = 1 THEN 1 ELSE 0 END) as approved_count,
                    SUM(CASE WHEN user_approved = 0 THEN 1 ELSE 0 END) as rejected_count
                FROM processing_log 
                WHERE timestamp >= ?
            """, (cutoff_date,))
            
            overall = dict(cursor.fetchone())
            
            return {
                'period_days': days,
                'overall': overall,
                'by_action': action_stats
            }

    def get_connection(self):
        """Get database connection for complex operations"""
        return sqlite3.connect(self.db_path)


    def close(self):
        """Close database connection."""
        # SQLite connections are closed automatically with context managers
        pass

# Create global database instance
import os
default_db_path = os.getenv('INMPARA_DB_PATH', '/workspace/vibes/mcp/mcp-notebook-server/data/inmpara_notebook.db')
db = INMPARADatabase(default_db_path)
