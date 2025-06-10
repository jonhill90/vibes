"""
Pattern Learning Engine for INMPARA Notebook MCP Server
Implements Phase 2 advanced intelligence features
"""

import json
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
import re

logger = logging.getLogger(__name__)

@dataclass
class UserFeedback:
    """Represents user feedback on AI decisions"""
    action_type: str  # moved_file, changed_tags, edited_content, etc.
    original_value: str
    corrected_value: str
    note_id: str
    confidence_impact: float
    context: Dict[str, Any]

@dataclass
class LearningPattern:
    """Represents a learned pattern for decision making"""
    pattern_type: str  # filing, tagging, content_type, confidence
    pattern_data: Dict[str, Any]
    confidence: float
    usage_count: int
    success_rate: float
    last_updated: datetime

class PatternLearner:
    """
    Advanced pattern learning engine that learns from user corrections
    and feedback to improve AI decision making over time.
    """
    
    def __init__(self, database):
        self.db = database
        self._confidence_thresholds = {
            'auto_create': 0.8,
            'auto_file': 0.85,
            'suggest': 0.6,
            'min_confidence': 0.3
        }
        self._learning_rate = 0.1
        
    def learn_from_feedback(self, feedback: UserFeedback) -> Dict[str, Any]:
        """
        Main learning function that processes user feedback and updates patterns.
        """
        logger.info(f"Learning from feedback: {feedback.action_type}")
        
        results = {
            'patterns_updated': [],
            'confidence_adjustments': {},
            'new_patterns_created': []
        }
        
        if feedback.action_type == "moved_file":
            results.update(self._learn_filing_pattern(feedback))
        elif feedback.action_type == "changed_tags":
            results.update(self._learn_tagging_pattern(feedback))
        elif feedback.action_type == "edited_content":
            results.update(self._learn_content_preferences(feedback))
        elif feedback.action_type == "added_relation":
            results.update(self._learn_relation_pattern(feedback))
        elif feedback.action_type == "removed_relation":
            results.update(self._learn_anti_relation_pattern(feedback))
        
        # Store feedback in database
        self._store_feedback(feedback)
        
        # Update confidence thresholds based on recent success rates
        self._update_confidence_thresholds()
        
        return results
    
    def _learn_filing_pattern(self, feedback: UserFeedback) -> Dict[str, Any]:
        """Learn from file movement corrections"""
        original_folder = feedback.original_value
        correct_folder = feedback.corrected_value
        
        # Extract features from the note
        note_features = self._extract_note_features(feedback.note_id)
        
        # Update or create filing pattern
        pattern_key = f"filing_{note_features.get('content_type', 'unknown')}"
        pattern_data = {
            'content_type': note_features.get('content_type'),
            'domain': note_features.get('domain'),
            'keywords': note_features.get('keywords', []),
            'correct_folder': correct_folder,
            'wrong_folder': original_folder,
            'confidence_features': note_features.get('confidence_features', {})
        }
        
        pattern_id = self._update_or_create_pattern(
            pattern_type='filing',
            pattern_key=pattern_key,
            pattern_data=pattern_data,
            success=True  # User correction means our original decision was wrong
        )
        
        return {
            'patterns_updated': [{'id': pattern_id, 'type': 'filing'}],
            'filing_correction': {
                'from': original_folder,
                'to': correct_folder,
                'features': note_features
            }
        }
    
    def _learn_tagging_pattern(self, feedback: UserFeedback) -> Dict[str, Any]:
        """Learn from tag changes"""
        original_tags = json.loads(feedback.original_value) if feedback.original_value else []
        correct_tags = json.loads(feedback.corrected_value) if feedback.corrected_value else []
        
        # Find added and removed tags
        added_tags = set(correct_tags) - set(original_tags)
        removed_tags = set(original_tags) - set(correct_tags)
        
        note_features = self._extract_note_features(feedback.note_id)
        
        results = {'patterns_updated': [], 'tagging_corrections': []}
        
        # Learn from added tags
        for tag in added_tags:
            pattern_data = {
                'tag': tag,
                'content_features': note_features,
                'tag_type': self._classify_tag_type(tag),
                'context': feedback.context
            }
            
            pattern_id = self._update_or_create_pattern(
                pattern_type='tagging_positive',
                pattern_key=f"add_{tag}_{note_features.get('domain', 'unknown')}",
                pattern_data=pattern_data,
                success=True
            )
            
            results['patterns_updated'].append({'id': pattern_id, 'type': 'tagging_positive'})
            results['tagging_corrections'].append({'action': 'added', 'tag': tag})
        
        # Learn from removed tags
        for tag in removed_tags:
            pattern_data = {
                'tag': tag,
                'content_features': note_features,
                'tag_type': self._classify_tag_type(tag),
                'context': feedback.context
            }
            
            pattern_id = self._update_or_create_pattern(
                pattern_type='tagging_negative',
                pattern_key=f"remove_{tag}_{note_features.get('domain', 'unknown')}",
                pattern_data=pattern_data,
                success=True
            )
            
            results['patterns_updated'].append({'id': pattern_id, 'type': 'tagging_negative'})
            results['tagging_corrections'].append({'action': 'removed', 'tag': tag})
        
        return results
    
    def _learn_content_preferences(self, feedback: UserFeedback) -> Dict[str, Any]:
        """Learn from content editing patterns"""
        # Analyze what was changed in content
        changes = self._analyze_content_changes(
            feedback.original_value,
            feedback.corrected_value
        )
        
        note_features = self._extract_note_features(feedback.note_id)
        
        pattern_data = {
            'content_changes': changes,
            'note_features': note_features,
            'edit_type': changes.get('edit_type', 'unknown')
        }
        
        pattern_id = self._update_or_create_pattern(
            pattern_type='content_preference',
            pattern_key=f"content_{changes.get('edit_type', 'unknown')}",
            pattern_data=pattern_data,
            success=True
        )
        
        return {
            'patterns_updated': [{'id': pattern_id, 'type': 'content_preference'}],
            'content_changes': changes
        }
    
    def _learn_relation_pattern(self, feedback: UserFeedback) -> Dict[str, Any]:
        """Learn from manually added relations"""
        relation_data = json.loads(feedback.corrected_value)
        note_features = self._extract_note_features(feedback.note_id)
        
        pattern_data = {
            'source_features': note_features,
            'relation_type': relation_data.get('type'),
            'target_note': relation_data.get('target'),
            'context': feedback.context
        }
        
        pattern_id = self._update_or_create_pattern(
            pattern_type='relation_positive',
            pattern_key=f"relation_{relation_data.get('type')}_{note_features.get('domain')}",
            pattern_data=pattern_data,
            success=True
        )
        
        return {
            'patterns_updated': [{'id': pattern_id, 'type': 'relation_positive'}],
            'relation_added': relation_data
        }
    
    def _learn_anti_relation_pattern(self, feedback: UserFeedback) -> Dict[str, Any]:
        """Learn from manually removed relations"""
        relation_data = json.loads(feedback.original_value)
        note_features = self._extract_note_features(feedback.note_id)
        
        pattern_data = {
            'source_features': note_features,
            'relation_type': relation_data.get('type'),
            'target_note': relation_data.get('target'),
            'context': feedback.context
        }
        
        pattern_id = self._update_or_create_pattern(
            pattern_type='relation_negative',
            pattern_key=f"anti_relation_{relation_data.get('type')}_{note_features.get('domain')}",
            pattern_data=pattern_data,
            success=True
        )
        
        return {
            'patterns_updated': [{'id': pattern_id, 'type': 'relation_negative'}],
            'relation_removed': relation_data
        }
    
    def get_confidence_adjustments(self, content_features: Dict[str, Any]) -> Dict[str, float]:
        """
        Get confidence adjustments based on learned patterns.
        """
        adjustments = {
            'filing_confidence': 0.0,
            'tagging_confidence': 0.0,
            'content_type_confidence': 0.0,
            'overall_adjustment': 0.0
        }
        
        # Get relevant patterns
        filing_patterns = self.db.get_learning_patterns('filing')
        tagging_patterns = self.db.get_learning_patterns('tagging_positive')
        
        # Calculate filing confidence adjustment
        for pattern in filing_patterns:
            if self._pattern_matches_features(pattern['pattern_data'], content_features):
                weight = pattern['success_rate'] * (pattern['usage_count'] / 100.0)
                adjustments['filing_confidence'] += weight * 0.1
        
        # Calculate tagging confidence adjustment
        for pattern in tagging_patterns:
            if self._pattern_matches_features(pattern['pattern_data'], content_features):
                weight = pattern['success_rate'] * (pattern['usage_count'] / 100.0)
                adjustments['tagging_confidence'] += weight * 0.05
        
        # Overall adjustment is average of individual adjustments
        adjustments['overall_adjustment'] = (
            adjustments['filing_confidence'] + 
            adjustments['tagging_confidence']
        ) / 2.0
        
        return adjustments
    
    def get_suggested_improvements(self, content_analysis: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Get suggestions for improving content analysis based on learned patterns.
        """
        suggestions = []
        
        # Get patterns that match current content
        filing_patterns = self.db.get_learning_patterns('filing')
        tagging_patterns = self.db.get_learning_patterns('tagging_positive')
        
        # Filing suggestions
        for pattern in filing_patterns[:3]:  # Top 3 patterns
            if (pattern['success_rate'] > 0.8 and 
                self._pattern_matches_features(pattern['pattern_data'], content_analysis)):
                
                suggestions.append({
                    'type': 'filing',
                    'suggestion': f"Consider filing in {pattern['pattern_data'].get('correct_folder')}",
                    'confidence': pattern['success_rate'],
                    'reasoning': f"Similar content was previously moved to this folder"
                })
        
        # Tagging suggestions
        tag_recommendations = {}
        for pattern in tagging_patterns:
            if (pattern['success_rate'] > 0.7 and
                self._pattern_matches_features(pattern['pattern_data'], content_analysis)):
                
                tag = pattern['pattern_data'].get('tag')
                if tag:
                    tag_recommendations[tag] = max(
                        tag_recommendations.get(tag, 0.0),
                        pattern['success_rate']
                    )
        
        for tag, confidence in sorted(tag_recommendations.items(), 
                                    key=lambda x: x[1], reverse=True)[:5]:
            suggestions.append({
                'type': 'tagging',
                'suggestion': f"Consider adding tag '{tag}'",
                'confidence': confidence,
                'reasoning': "Similar content was previously tagged with this"
            })
        
        return suggestions
    
    def _extract_note_features(self, note_id: str) -> Dict[str, Any]:
        """Extract features from a note for pattern matching"""
        # Get note from database
        notes = self.db.search_notes({'id': note_id})
        if not notes:
            return {}
        
        note = notes[0]
        
        # Extract key features
        features = {
            'content_type': note.get('content_type'),
            'domain': note.get('domain'),
            'word_count': note.get('word_count', 0),
            'tags': note.get('tags', []),
            'confidence_score': note.get('confidence_score', 0.0)
        }
        
        # Add computed features
        features['has_technical_terms'] = any(
            term in note.get('title', '').lower() 
            for term in ['azure', 'terraform', 'dns', 'api', 'config']
        )
        
        features['keywords'] = self._extract_keywords(note.get('title', ''))
        
        return features
    
    def _extract_keywords(self, text: str) -> List[str]:
        """Extract key terms from text"""
        # Simple keyword extraction
        technical_terms = re.findall(
            r'\b(?:azure|terraform|dns|api|config|endpoint|network|security)\b',
            text.lower()
        )
        return list(set(technical_terms))
    
    def _classify_tag_type(self, tag: str) -> str:
        """Classify the type of a tag"""
        domain_tags = ['azure', 'terraform', 'dns', 'networking', 'devops', 'security']
        content_type_tags = ['note', 'moc', 'project', 'area', 'resource']
        
        if tag.lower() in domain_tags:
            return 'domain'
        elif tag.lower() in content_type_tags:
            return 'content_type'
        else:
            return 'specific'
    
    def _analyze_content_changes(self, original: str, corrected: str) -> Dict[str, Any]:
        """Analyze what changed in content"""
        changes = {
            'edit_type': 'unknown',
            'changes_count': 0,
            'sections_modified': []
        }
        
        # Simple diff analysis
        if len(corrected) > len(original) * 1.2:
            changes['edit_type'] = 'expansion'
        elif len(corrected) < len(original) * 0.8:
            changes['edit_type'] = 'reduction'
        else:
            changes['edit_type'] = 'modification'
        
        # Count approximate number of changes
        original_words = set(original.split())
        corrected_words = set(corrected.split())
        changes['changes_count'] = len(original_words.symmetric_difference(corrected_words))
        
        return changes
    
    def _pattern_matches_features(self, pattern_data: Dict[str, Any], 
                                content_features: Dict[str, Any]) -> bool:
        """Check if a pattern matches given content features"""
        # Check domain match
        if (pattern_data.get('domain') and 
            pattern_data['domain'] != content_features.get('domain')):
            return False
        
        # Check content type match
        if (pattern_data.get('content_type') and 
            pattern_data['content_type'] != content_features.get('content_type')):
            return False
        
        # Check keyword overlap
        pattern_keywords = set(pattern_data.get('keywords', []))
        content_keywords = set(content_features.get('keywords', []))
        
        if pattern_keywords and not pattern_keywords.intersection(content_keywords):
            return False
        
        return True
    
    def _update_or_create_pattern(self, pattern_type: str, pattern_key: str,
                                pattern_data: Dict[str, Any], success: bool) -> int:
        """Update existing pattern or create new one"""
        # Check if pattern exists
        existing_patterns = self.db.get_learning_patterns(pattern_type)
        
        pattern_id = None
        for pattern in existing_patterns:
            if pattern.get('pattern_key') == pattern_key:
                pattern_id = pattern['id']
                break
        
        if pattern_id:
            # Update existing pattern
            self.db.update_learning_pattern(pattern_id, success)
            return pattern_id
        else:
            # Create new pattern
            return self._create_new_pattern(pattern_type, pattern_key, pattern_data)
    
    def _create_new_pattern(self, pattern_type: str, pattern_key: str,
                          pattern_data: Dict[str, Any]) -> int:
        """Create a new learning pattern"""
        with self.db.get_connection() as conn:
            cursor = conn.execute("""
                INSERT INTO learning_patterns 
                (pattern_type, pattern_data, confidence, usage_count, success_rate, last_updated)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (
                pattern_type,
                json.dumps({**pattern_data, 'pattern_key': pattern_key}),
                0.8,  # Initial confidence
                1,    # Initial usage count
                1.0,  # Initial success rate
                datetime.now().isoformat()
            ))
            return cursor.lastrowid
    
    def _store_feedback(self, feedback: UserFeedback):
        """Store feedback in database"""
        with self.db.get_connection() as conn:
            conn.execute("""
                INSERT INTO user_feedback
                (action_type, original_value, corrected_value, note_id, 
                 confidence_impact, feedback_date)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (
                feedback.action_type,
                feedback.original_value,
                feedback.corrected_value,
                feedback.note_id,
                feedback.confidence_impact,
                datetime.now().isoformat()
            ))
    
    def _update_confidence_thresholds(self):
        """Update confidence thresholds based on recent success rates"""
        # Get recent processing statistics
        stats = self.db.get_processing_stats(days=30)
        
        if stats['overall']['total_actions'] > 10:  # Need enough data
            overall_success_rate = (
                stats['overall'].get('approved_count', 0) / 
                stats['overall']['total_actions']
            )
            
            # Adjust thresholds based on success rate
            if overall_success_rate > 0.9:
                # High success rate - can be more aggressive
                self._confidence_thresholds['auto_create'] *= 0.95
                self._confidence_thresholds['auto_file'] *= 0.95
            elif overall_success_rate < 0.7:
                # Low success rate - be more conservative
                self._confidence_thresholds['auto_create'] *= 1.05
                self._confidence_thresholds['auto_file'] *= 1.05
            
            # Keep thresholds in reasonable bounds
            self._confidence_thresholds['auto_create'] = max(0.6, min(0.9, 
                self._confidence_thresholds['auto_create']))
            self._confidence_thresholds['auto_file'] = max(0.7, min(0.95, 
                self._confidence_thresholds['auto_file']))
    
    def get_current_thresholds(self) -> Dict[str, float]:
        """Get current confidence thresholds"""
        return self._confidence_thresholds.copy()
    
    def get_learning_stats(self) -> Dict[str, Any]:
        """Get learning statistics"""
        patterns = self.db.get_learning_patterns()
        
        stats = {
            'total_patterns': len(patterns),
            'by_type': {},
            'avg_success_rate': 0.0,
            'recent_feedback_count': 0
        }
        
        # Group by type
        for pattern in patterns:
            pattern_type = pattern['pattern_type']
            if pattern_type not in stats['by_type']:
                stats['by_type'][pattern_type] = {
                    'count': 0,
                    'avg_success_rate': 0.0,
                    'total_usage': 0
                }
            
            stats['by_type'][pattern_type]['count'] += 1
            stats['by_type'][pattern_type]['avg_success_rate'] += pattern['success_rate']
            stats['by_type'][pattern_type]['total_usage'] += pattern['usage_count']
        
        # Calculate averages
        for pattern_type in stats['by_type']:
            count = stats['by_type'][pattern_type]['count']
            stats['by_type'][pattern_type]['avg_success_rate'] /= count
        
        # Overall average
        if patterns:
            stats['avg_success_rate'] = sum(p['success_rate'] for p in patterns) / len(patterns)
        
        # Recent feedback count
        cutoff_date = (datetime.now() - timedelta(days=7)).isoformat()
        with self.db.get_connection() as conn:
            cursor = conn.execute("""
                SELECT COUNT(*) FROM user_feedback WHERE feedback_date >= ?
            """, (cutoff_date,))
            stats['recent_feedback_count'] = cursor.fetchone()[0]
        
        return stats
