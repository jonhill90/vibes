"""
Session Manager for Cross-Conversation Context Tracking
Implements Phase 2 advanced conversation context features
"""

import json
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Set
from dataclasses import dataclass
import hashlib

logger = logging.getLogger(__name__)

@dataclass
class ConversationContext:
    """Represents context from a conversation session"""
    session_id: str
    topics: Set[str]
    domains: Set[str]
    insights_count: int
    notes_created: List[str]
    start_time: datetime
    last_activity: datetime
    context_summary: str

@dataclass
class CrossSessionConnection:
    """Represents a connection between different conversation sessions"""
    session1_id: str
    session2_id: str
    connection_type: str  # topic_overlap, domain_similarity, note_relation
    strength: float
    shared_elements: List[str]
    created_at: datetime

class SessionManager:
    """
    Manages conversation sessions and tracks context across conversations
    to enable intelligent cross-session connections and insights.
    """
    
    def __init__(self, database):
        self.db = database
        self.active_sessions = {}  # session_id -> ConversationContext
        self.session_timeout = timedelta(hours=2)  # Sessions expire after 2 hours
        
    def start_session(self, session_id: str = None) -> str:
        """Start a new conversation session"""
        if not session_id:
            session_id = self._generate_session_id()
        
        # Clean up expired sessions
        self._cleanup_expired_sessions()
        
        context = ConversationContext(
            session_id=session_id,
            topics=set(),
            domains=set(),
            insights_count=0,
            notes_created=[],
            start_time=datetime.now(),
            last_activity=datetime.now(),
            context_summary=""
        )
        
        self.active_sessions[session_id] = context
        
        # Store session in database
        self._store_session_start(context)
        
        logger.info(f"Started new session: {session_id}")
        return session_id
    
    def update_session_context(self, session_id: str, 
                             conversation_text: str,
                             insights: List[Dict[str, Any]] = None,
                             notes_created: List[str] = None) -> Dict[str, Any]:
        """Update session context with new conversation data"""
        if session_id not in self.active_sessions:
            # Auto-create session if it doesn't exist
            self.start_session(session_id)
        
        context = self.active_sessions[session_id]
        context.last_activity = datetime.now()
        
        # Extract topics and domains from conversation
        new_topics = self._extract_topics(conversation_text)
        new_domains = self._extract_domains(conversation_text)
        
        context.topics.update(new_topics)
        context.domains.update(new_domains)
        
        if insights:
            context.insights_count += len(insights)
        
        if notes_created:
            context.notes_created.extend(notes_created)
        
        # Update context summary
        context.context_summary = self._generate_context_summary(context)
        
        # Look for cross-session connections
        connections = self._find_cross_session_connections(session_id)
        
        # Update database
        self._update_session_in_db(context)
        
        return {
            'session_id': session_id,
            'current_topics': list(context.topics),
            'current_domains': list(context.domains),
            'insights_count': context.insights_count,
            'notes_created': context.notes_created,
            'cross_session_connections': connections,
            'context_summary': context.context_summary
        }
    
    def get_session_context(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Get current context for a session"""
        if session_id in self.active_sessions:
            context = self.active_sessions[session_id]
            return {
                'session_id': session_id,
                'topics': list(context.topics),
                'domains': list(context.domains),
                'insights_count': context.insights_count,
                'notes_created': context.notes_created,
                'start_time': context.start_time.isoformat(),
                'last_activity': context.last_activity.isoformat(),
                'context_summary': context.context_summary,
                'active': True
            }
        
        # Check database for historical session
        return self._get_session_from_db(session_id)
    
    def find_related_sessions(self, session_id: str, 
                            limit: int = 5) -> List[Dict[str, Any]]:
        """Find sessions related to the current session"""
        if session_id not in self.active_sessions:
            return []
        
        current_context = self.active_sessions[session_id]
        related_sessions = []
        
        # Check against other active sessions
        for other_id, other_context in self.active_sessions.items():
            if other_id == session_id:
                continue
            
            similarity = self._calculate_session_similarity(current_context, other_context)
            if similarity > 0.3:  # Threshold for relatedness
                related_sessions.append({
                    'session_id': other_id,
                    'similarity': similarity,
                    'shared_topics': list(current_context.topics.intersection(other_context.topics)),
                    'shared_domains': list(current_context.domains.intersection(other_context.domains)),
                    'context_summary': other_context.context_summary,
                    'active': True
                })
        
        # Check database for historical sessions
        historical_related = self._find_historical_related_sessions(
            current_context, limit - len(related_sessions)
        )
        related_sessions.extend(historical_related)
        
        # Sort by similarity
        related_sessions.sort(key=lambda x: x['similarity'], reverse=True)
        
        return related_sessions[:limit]
    
    def get_context_based_suggestions(self, session_id: str,
                                    current_conversation: str) -> List[Dict[str, Any]]:
        """Get suggestions based on cross-session context"""
        suggestions = []
        
        # Get current session context
        if session_id not in self.active_sessions:
            return suggestions
        
        current_context = self.active_sessions[session_id]
        current_topics = self._extract_topics(current_conversation)
        current_domains = self._extract_domains(current_conversation)
        
        # Find related content from other sessions
        related_sessions = self.find_related_sessions(session_id)
        
        for related_session in related_sessions:
            if related_session['similarity'] > 0.5:
                suggestions.append({
                    'type': 'related_session',
                    'title': f"Similar discussion in previous session",
                    'description': related_session['context_summary'],
                    'confidence': related_session['similarity'],
                    'details': {
                        'session_id': related_session['session_id'],
                        'shared_topics': related_session['shared_topics'],
                        'shared_domains': related_session['shared_domains']
                    }
                })
        
        # Find related notes that might be relevant
        related_notes = self._find_related_notes_from_context(current_domains, current_topics)
        
        for note in related_notes[:3]:  # Top 3 related notes
            suggestions.append({
                'type': 'related_note',
                'title': f"Existing note: {note['title']}",
                'description': f"Related to {', '.join(note['tags'][:3])}",
                'confidence': note['relevance_score'],
                'details': {
                    'note_id': note['id'],
                    'file_path': note['file_path'],
                    'created': note['created_date']
                }
            })
        
        return suggestions
    
    def end_session(self, session_id: str) -> Dict[str, Any]:
        """End a conversation session and store final context"""
        if session_id not in self.active_sessions:
            return {'error': 'Session not found'}
        
        context = self.active_sessions[session_id]
        
        # Generate final session summary
        session_summary = {
            'session_id': session_id,
            'duration_minutes': (datetime.now() - context.start_time).total_seconds() / 60,
            'topics_covered': list(context.topics),
            'domains_explored': list(context.domains),
            'insights_captured': context.insights_count,
            'notes_created': len(context.notes_created),
            'final_context': context.context_summary
        }
        
        # Store final session data
        self._store_session_end(context, session_summary)
        
        # Remove from active sessions
        del self.active_sessions[session_id]
        
        logger.info(f"Ended session {session_id}: {session_summary}")
        return session_summary
    
    def get_session_statistics(self, days: int = 30) -> Dict[str, Any]:
        """Get statistics about recent sessions"""
        cutoff_date = (datetime.now() - timedelta(days=days)).isoformat()
        
        with self.db.get_connection() as conn:
            # Session counts and durations
            cursor = conn.execute("""
                SELECT 
                    COUNT(*) as total_sessions,
                    AVG(duration_minutes) as avg_duration,
                    SUM(insights_captured) as total_insights,
                    SUM(notes_created) as total_notes
                FROM session_summaries 
                WHERE start_time >= ?
            """, (cutoff_date,))
            
            stats = dict(cursor.fetchone()) if cursor.rowcount > 0 else {}
            
            # Top topics
            cursor = conn.execute("""
                SELECT topic, COUNT(*) as frequency
                FROM session_topics st
                JOIN session_summaries ss ON st.session_id = ss.session_id
                WHERE ss.start_time >= ?
                GROUP BY topic
                ORDER BY frequency DESC
                LIMIT 10
            """, (cutoff_date,))
            
            stats['top_topics'] = [{'topic': row[0], 'frequency': row[1]} 
                                 for row in cursor.fetchall()]
            
            # Top domains
            cursor = conn.execute("""
                SELECT domain, COUNT(*) as frequency
                FROM session_domains sd
                JOIN session_summaries ss ON sd.session_id = ss.session_id
                WHERE ss.start_time >= ?
                GROUP BY domain
                ORDER BY frequency DESC
                LIMIT 10
            """, (cutoff_date,))
            
            stats['top_domains'] = [{'domain': row[0], 'frequency': row[1]} 
                                  for row in cursor.fetchall()]
            
            return stats
    
    def _generate_session_id(self) -> str:
        """Generate a unique session ID"""
        timestamp = datetime.now().isoformat()
        return hashlib.md5(timestamp.encode()).hexdigest()[:12]
    
    def _cleanup_expired_sessions(self):
        """Remove expired sessions from active sessions"""
        current_time = datetime.now()
        expired_sessions = []
        
        for session_id, context in self.active_sessions.items():
            if current_time - context.last_activity > self.session_timeout:
                expired_sessions.append(session_id)
        
        for session_id in expired_sessions:
            self.end_session(session_id)
    
    def _extract_topics(self, text: str) -> Set[str]:
        """Extract topics from conversation text"""
        topics = set()
        
        # Technical topics patterns
        topic_patterns = {
            'private_endpoints': r'private\s+endpoint',
            'dns_configuration': r'dns\s+config',
            'azure_networking': r'azure\s+network',
            'terraform_state': r'terraform\s+state',
            'api_integration': r'api\s+integration',
            'security_groups': r'security\s+group',
            'load_balancing': r'load\s+balanc',
            'database_connection': r'database\s+connect',
            'monitoring_setup': r'monitoring\s+setup',
            'ci_cd_pipeline': r'ci.?cd\s+pipeline'
        }
        
        import re
        for topic, pattern in topic_patterns.items():
            if re.search(pattern, text, re.IGNORECASE):
                topics.add(topic)
        
        return topics
    
    def _extract_domains(self, text: str) -> Set[str]:
        """Extract technical domains from conversation text"""
        domains = set()
        
        domain_keywords = {
            'azure': ['azure', 'az ', 'microsoft cloud'],
            'terraform': ['terraform', 'tf ', 'hcl'],
            'dns': ['dns', 'domain name', 'name resolution'],
            'networking': ['network', 'subnet', 'vnet', 'vpc'],
            'devops': ['devops', 'ci/cd', 'pipeline', 'deployment'],
            'security': ['security', 'authentication', 'authorization', 'ssl', 'tls'],
            'database': ['database', 'sql', 'nosql', 'db'],
            'monitoring': ['monitoring', 'logging', 'metrics', 'observability']
        }
        
        text_lower = text.lower()
        for domain, keywords in domain_keywords.items():
            if any(keyword in text_lower for keyword in keywords):
                domains.add(domain)
        
        return domains
    
    def _generate_context_summary(self, context: ConversationContext) -> str:
        """Generate a summary of the session context"""
        topics_str = ', '.join(list(context.topics)[:3])
        domains_str = ', '.join(list(context.domains)[:3])
        
        summary = f"Session exploring {domains_str}"
        if topics_str:
            summary += f" with focus on {topics_str}"
        
        if context.insights_count > 0:
            summary += f". Captured {context.insights_count} insights"
        
        if context.notes_created:
            summary += f". Created {len(context.notes_created)} notes"
        
        return summary
    
    def _calculate_session_similarity(self, context1: ConversationContext,
                                    context2: ConversationContext) -> float:
        """Calculate similarity between two session contexts"""
        # Topic overlap
        topic_overlap = len(context1.topics.intersection(context2.topics))
        topic_union = len(context1.topics.union(context2.topics))
        topic_similarity = topic_overlap / topic_union if topic_union > 0 else 0.0
        
        # Domain overlap
        domain_overlap = len(context1.domains.intersection(context2.domains))
        domain_union = len(context1.domains.union(context2.domains))
        domain_similarity = domain_overlap / domain_union if domain_union > 0 else 0.0
        
        # Time proximity (more recent sessions are more relevant)
        time_diff = abs((context1.start_time - context2.start_time).days)
        time_similarity = max(0.0, 1.0 - (time_diff / 30.0))  # Decay over 30 days
        
        # Weighted combination
        similarity = (
            topic_similarity * 0.4 +
            domain_similarity * 0.4 +
            time_similarity * 0.2
        )
        
        return similarity
    
    def _find_cross_session_connections(self, session_id: str) -> List[Dict[str, Any]]:
        """Find connections between current session and others"""
        connections = []
        
        if session_id not in self.active_sessions:
            return connections
        
        current_context = self.active_sessions[session_id]
        
        # Check other active sessions
        for other_id, other_context in self.active_sessions.items():
            if other_id == session_id:
                continue
            
            similarity = self._calculate_session_similarity(current_context, other_context)
            
            if similarity > 0.4:  # Significant connection threshold
                connections.append({
                    'session_id': other_id,
                    'connection_type': 'active_session',
                    'strength': similarity,
                    'shared_topics': list(current_context.topics.intersection(other_context.topics)),
                    'shared_domains': list(current_context.domains.intersection(other_context.domains))
                })
        
        return connections
    
    def _find_related_notes_from_context(self, domains: Set[str], 
                                       topics: Set[str]) -> List[Dict[str, Any]]:
        """Find notes related to current session context"""
        # Search for notes in the same domains
        related_notes = []
        
        for domain in domains:
            notes = self.db.search_notes({'domain': domain})
            for note in notes[:5]:  # Limit per domain
                # Calculate relevance score
                relevance = 0.5  # Base relevance for domain match
                
                # Boost if tags match topics
                note_tags = set(note.get('tags', []))
                topic_overlap = len(note_tags.intersection(topics))
                if topic_overlap > 0:
                    relevance += topic_overlap * 0.2
                
                note['relevance_score'] = min(1.0, relevance)
                related_notes.append(note)
        
        # Sort by relevance
        related_notes.sort(key=lambda x: x['relevance_score'], reverse=True)
        
        return related_notes
    
    def _store_session_start(self, context: ConversationContext):
        """Store session start in database"""
        with self.db.get_connection() as conn:
            conn.execute("""
                INSERT OR REPLACE INTO conversation_sessions
                (session_id, start_time, last_activity, topics, domains, context_summary)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (
                context.session_id,
                context.start_time.isoformat(),
                context.last_activity.isoformat(),
                json.dumps(list(context.topics)),
                json.dumps(list(context.domains)),
                context.context_summary
            ))
    
    def _update_session_in_db(self, context: ConversationContext):
        """Update session data in database"""
        with self.db.get_connection() as conn:
            conn.execute("""
                UPDATE conversation_sessions
                SET last_activity = ?, topics = ?, domains = ?, context_summary = ?
                WHERE session_id = ?
            """, (
                context.last_activity.isoformat(),
                json.dumps(list(context.topics)),
                json.dumps(list(context.domains)),
                context.context_summary,
                context.session_id
            ))
    
    def _store_session_end(self, context: ConversationContext, summary: Dict[str, Any]):
        """Store session end summary"""
        with self.db.get_connection() as conn:
            # Store session summary
            conn.execute("""
                INSERT INTO session_summaries
                (session_id, start_time, end_time, duration_minutes, topics_covered,
                 domains_explored, insights_captured, notes_created, final_context)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                context.session_id,
                context.start_time.isoformat(),
                datetime.now().isoformat(),
                summary['duration_minutes'],
                json.dumps(summary['topics_covered']),
                json.dumps(summary['domains_explored']),
                summary['insights_captured'],
                summary['notes_created'],
                summary['final_context']
            ))
            
            # Store individual topics
            for topic in context.topics:
                conn.execute("""
                    INSERT INTO session_topics (session_id, topic)
                    VALUES (?, ?)
                """, (context.session_id, topic))
            
            # Store individual domains
            for domain in context.domains:
                conn.execute("""
                    INSERT INTO session_domains (session_id, domain)
                    VALUES (?, ?)
                """, (context.session_id, domain))
    
    def _get_session_from_db(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Get session data from database"""
        with self.db.get_connection() as conn:
            cursor = conn.execute("""
                SELECT * FROM conversation_sessions WHERE session_id = ?
            """, (session_id,))
            
            row = cursor.fetchone()
            if row:
                return {
                    'session_id': row['session_id'],
                    'topics': json.loads(row['topics']),
                    'domains': json.loads(row['domains']),
                    'start_time': row['start_time'],
                    'last_activity': row['last_activity'],
                    'context_summary': row['context_summary'],
                    'active': False
                }
            
            return None
    
    def _find_historical_related_sessions(self, current_context: ConversationContext,
                                        limit: int) -> List[Dict[str, Any]]:
        """Find related sessions from database"""
        related_sessions = []
        
        # Simple approach: find sessions with overlapping domains
        for domain in current_context.domains:
            with self.db.get_connection() as conn:
                cursor = conn.execute("""
                    SELECT DISTINCT cs.session_id, cs.context_summary, cs.start_time
                    FROM conversation_sessions cs
                    JOIN session_domains sd ON cs.session_id = sd.session_id
                    WHERE sd.domain = ? AND cs.session_id != ?
                    ORDER BY cs.start_time DESC
                    LIMIT ?
                """, (domain, current_context.session_id, limit))
                
                for row in cursor.fetchall():
                    related_sessions.append({
                        'session_id': row['session_id'],
                        'similarity': 0.6,  # Approximate similarity for domain match
                        'shared_domains': [domain],
                        'shared_topics': [],
                        'context_summary': row['context_summary'],
                        'active': False
                    })
        
        return related_sessions[:limit]
