"""
INMPARA Sessions Module

This module handles conversation session management, context tracking,
cross-session analysis, and real-time insight detection.

Target: ~400 lines - Complete session and context management
"""

import json
import logging
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime, timedelta
from uuid import uuid4

logger = logging.getLogger(__name__)


class SessionsManager:
    """
    Manages conversation sessions and context tracking.
    
    Handles session lifecycle, context accumulation, cross-session analysis,
    and real-time insight detection during conversations.
    """
    
    def __init__(self, database=None, vector_search=None):
        """Initialize the SessionsManager with required components."""
        self.database = database
        self.vector_search = vector_search
        
        # Current session state
        self.current_session = None
        self.session_context = {}
        
        # Session configuration
        self.max_session_duration = timedelta(hours=4)
        self.context_window_size = 50  # Number of messages to keep in context
        self.insight_detection_threshold = 0.7
        
        logger.info("SessionsManager initialized")
    
    def start_session(self, session_type: str = 'conversation',
                     initial_context: Dict[str, Any] = None) -> Dict[str, Any]:
        """Start a new conversation session."""
        try:
            session_id = str(uuid4())
            timestamp = datetime.now()
            
            session_data = {
                'session_id': session_id,
                'type': session_type,
                'started_at': timestamp,
                'status': 'active',
                'context': initial_context or {},
                'message_count': 0,
                'insights_detected': 0,
                'notes_created': 0
            }
            
            # Store session in database
            if self.database:
                self.database.create_session(session_data)
            
            # Set as current session
            self.current_session = session_data
            self.session_context = {
                'messages': [],
                'detected_insights': [],
                'created_notes': [],
                'topics': set(),
                'entities': set()
            }
            
            logger.info(f"Started new session: {session_id}")
            
            return {
                'success': True,
                'session_id': session_id,
                'session_data': session_data,
                'message': 'Session started successfully'
            }
            
        except Exception as e:
            logger.error(f"Error starting session: {e}")
            return {'success': False, 'error': str(e)}
    
    def update_session_context(self, message: str, message_type: str = 'user',
                             metadata: Dict[str, Any] = None) -> Dict[str, Any]:
        """Update session context with new message and extract insights."""
        try:
            if not self.current_session:
                return {'success': False, 'error': 'No active session'}
            
            timestamp = datetime.now()
            message_data = {
                'timestamp': timestamp,
                'type': message_type,
                'content': message,
                'metadata': metadata or {}
            }
            
            # Add to session context
            self.session_context['messages'].append(message_data)
            
            # Trim context if too large
            if len(self.session_context['messages']) > self.context_window_size:
                self.session_context['messages'] = self.session_context['messages'][-self.context_window_size:]
            
            # Update session statistics
            self.current_session['message_count'] += 1
            self.current_session['last_activity'] = timestamp
            
            # Extract entities and topics
            self._extract_entities_and_topics(message)
            
            # Detect insights in real-time
            insights = self._detect_real_time_insights(message, message_type)
            
            # Update database
            if self.database:
                self.database.update_session_context(self.current_session['session_id'], {
                    'message_count': self.current_session['message_count'],
                    'last_activity': timestamp,
                    'insights_detected': len(self.session_context['detected_insights']),
                    'topics': list(self.session_context['topics']),
                    'entities': list(self.session_context['entities'])
                })
            
            return {
                'success': True,
                'session_id': self.current_session['session_id'],
                'message_added': True,
                'insights_detected': insights,
                'context_size': len(self.session_context['messages']),
                'total_insights': len(self.session_context['detected_insights'])
            }
            
        except Exception as e:
            logger.error(f"Error updating session context: {e}")
            return {'success': False, 'error': str(e)}
    
    def get_session_insights(self, session_id: str = None) -> Dict[str, Any]:
        """Get insights and analysis for a session."""
        try:
            target_session_id = session_id or (self.current_session['session_id'] if self.current_session else None)
            
            if not target_session_id:
                return {'success': False, 'error': 'No session specified or active'}
            
            # Get session data
            if session_id and session_id != (self.current_session['session_id'] if self.current_session else None):
                # Historical session - get from database
                session_data = self._get_historical_session(session_id)
                if not session_data:
                    return {'success': False, 'error': 'Session not found'}
            else:
                # Current session
                session_data = self.current_session
            
            # Analyze session content
            insights = {
                'session_summary': self._generate_session_summary(session_data),
                'key_topics': self._extract_key_topics(session_data),
                'detected_insights': self._get_session_detected_insights(session_data),
                'conversation_flow': self._analyze_conversation_flow(session_data),
                'cross_session_connections': self._find_cross_session_connections(session_data),
                'suggested_actions': self._suggest_session_actions(session_data)
            }
            
            return {
                'success': True,
                'session_id': target_session_id,
                'insights': insights
            }
            
        except Exception as e:
            logger.error(f"Error getting session insights: {e}")
            return {'success': False, 'error': str(e)}
    
    def end_session(self, session_summary: str = None) -> Dict[str, Any]:
        """End the current session and save summary."""
        try:
            if not self.current_session:
                return {'success': False, 'error': 'No active session to end'}
            
            # Update session with end information
            end_time = datetime.now()
            duration = end_time - self.current_session['started_at']
            
            session_end_data = {
                'ended_at': end_time,
                'duration_minutes': duration.total_seconds() / 60,
                'status': 'completed',
                'summary': session_summary or self._generate_auto_summary(),
                'final_stats': {
                    'messages': len(self.session_context['messages']),
                    'insights': len(self.session_context['detected_insights']),
                    'notes_created': len(self.session_context['created_notes']),
                    'topics': len(self.session_context['topics']),
                    'entities': len(self.session_context['entities'])
                }
            }
            
            # Update database
            if self.database:
                self.database.end_session(self.current_session['session_id'], session_end_data)
            
            # Store session data for analysis
            completed_session = self.current_session.copy()
            completed_session.update(session_end_data)
            
            # Clear current session
            session_id = self.current_session['session_id']
            self.current_session = None
            self.session_context = {}
            
            logger.info(f"Ended session: {session_id}")
            
            return {
                'success': True,
                'session_id': session_id,
                'duration_minutes': session_end_data['duration_minutes'],
                'final_stats': session_end_data['final_stats'],
                'summary': session_end_data['summary']
            }
            
        except Exception as e:
            logger.error(f"Error ending session: {e}")
            return {'success': False, 'error': str(e)}
    
    def _extract_entities_and_topics(self, message: str):
        """Extract entities and topics from message."""
        import re
        
        # Extract potential entities (capitalized words)
        entities = re.findall(r'\b[A-Z][a-zA-Z]+\b', message)
        self.session_context['entities'].update(entities)
        
        # Extract potential topics (longer meaningful words)
        topics = re.findall(r'\b[a-zA-Z]{4,}\b', message.lower())
        meaningful_topics = [topic for topic in topics if topic not in 
                           ['that', 'this', 'with', 'have', 'will', 'from', 'they', 'been', 'were']]
        self.session_context['topics'].update(meaningful_topics[:5])  # Top 5 per message
    
    def _detect_real_time_insights(self, message: str, message_type: str) -> List[Dict]:
        """Detect insights in real-time from messages."""
        insights = []
        
        # Detect questions that might need notes
        if '?' in message and message_type == 'user':
            insights.append({
                'type': 'question',
                'content': message,
                'suggestion': 'Consider creating a note to track this question',
                'confidence': 0.6
            })
        
        # Detect action items
        action_words = ['todo', 'task', 'action', 'need to', 'should', 'must', 'remember']
        if any(word in message.lower() for word in action_words):
            insights.append({
                'type': 'action_item',
                'content': message,
                'suggestion': 'This might be an action item worth capturing',
                'confidence': 0.7
            })
        
        # Detect insights or discoveries
        insight_words = ['realize', 'discover', 'understand', 'insight', 'learned', 'found out']
        if any(word in message.lower() for word in insight_words):
            insights.append({
                'type': 'insight',
                'content': message,
                'suggestion': 'This looks like a valuable insight to capture',
                'confidence': 0.8
            })
        
        # Store detected insights
        self.session_context['detected_insights'].extend(insights)
        
        return insights
    
    def _generate_session_summary(self, session_data: Dict) -> str:
        """Generate a summary of the session."""
        duration = session_data.get('duration_minutes', 0)
        message_count = session_data.get('message_count', 0)
        insights_count = session_data.get('insights_detected', 0)
        
        summary = f"Session lasted {duration:.1f} minutes with {message_count} messages. "
        summary += f"Detected {insights_count} insights during conversation."
        
        if self.session_context:
            topics = list(self.session_context.get('topics', []))[:5]
            if topics:
                summary += f" Main topics: {', '.join(topics)}."
        
        return summary
    
    def _generate_auto_summary(self) -> str:
        """Generate automatic summary from current session."""
        if not self.current_session:
            return "No session data available"
        
        return self._generate_session_summary(self.current_session)
    
    def _extract_key_topics(self, session_data: Dict) -> List[str]:
        """Extract key topics from session."""
        if self.current_session and session_data['session_id'] == self.current_session['session_id']:
            return list(self.session_context.get('topics', []))[:10]
        return []
    
    def _get_session_detected_insights(self, session_data: Dict) -> List[Dict]:
        """Get insights detected during session."""
        if self.current_session and session_data['session_id'] == self.current_session['session_id']:
            return self.session_context.get('detected_insights', [])
        return []
    
    def _analyze_conversation_flow(self, session_data: Dict) -> Dict[str, Any]:
        """Analyze the flow and patterns in conversation."""
        flow_analysis = {
            'message_distribution': {'user': 0, 'assistant': 0, 'system': 0},
            'conversation_pace': 'steady',
            'engagement_level': 'medium'
        }
        
        if self.current_session and session_data['session_id'] == self.current_session['session_id']:
            messages = self.session_context.get('messages', [])
            
            # Count message types
            for msg in messages:
                msg_type = msg.get('type', 'unknown')
                if msg_type in flow_analysis['message_distribution']:
                    flow_analysis['message_distribution'][msg_type] += 1
            
            # Analyze pace (very simple)
            if len(messages) > 20:
                flow_analysis['conversation_pace'] = 'fast'
            elif len(messages) < 5:
                flow_analysis['conversation_pace'] = 'slow'
        
        return flow_analysis
    
    def _find_cross_session_connections(self, session_data: Dict) -> List[Dict]:
        """Find connections to other sessions."""
        connections = []
        
        if not self.database:
            return connections
        
        try:
            # Get recent sessions
            recent_sessions = self.database.get_recent_sessions(limit=10)
            
            # Simple connection detection based on shared topics
            current_topics = set(self._extract_key_topics(session_data))
            
            for session in recent_sessions:
                if session['session_id'] == session_data['session_id']:
                    continue
                
                session_topics = set(session.get('topics', []))
                shared_topics = current_topics.intersection(session_topics)
                
                if len(shared_topics) >= 2:  # At least 2 shared topics
                    connections.append({
                        'session_id': session['session_id'],
                        'shared_topics': list(shared_topics),
                        'connection_strength': len(shared_topics) / len(current_topics.union(session_topics))
                    })
        
        except Exception as e:
            logger.error(f"Error finding cross-session connections: {e}")
        
        return connections[:5]  # Top 5 connections
    
    def _suggest_session_actions(self, session_data: Dict) -> List[str]:
        """Suggest actions based on session content."""
        suggestions = []
        
        insights_count = len(self._get_session_detected_insights(session_data))
        
        if insights_count > 3:
            suggestions.append("Consider creating notes from the insights detected in this session")
        
        topics = self._extract_key_topics(session_data)
        if len(topics) > 5:
            suggestions.append("Multiple topics discussed - might be worth creating a MOC")
        
        message_count = session_data.get('message_count', 0)
        if message_count > 50:
            suggestions.append("Long conversation - consider summarizing key points")
        
        return suggestions
    
    def _get_historical_session(self, session_id: str) -> Optional[Dict]:
        """Get historical session data from database."""
        if not self.database:
            return None
        
        try:
            return self.database.get_session(session_id)
        except Exception as e:
            logger.error(f"Error getting historical session: {e}")
            return None
