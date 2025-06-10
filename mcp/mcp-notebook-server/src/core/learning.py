"""
INMPARA Learning Module

This module handles pattern learning from user feedback, confidence adjustments,
and continuous improvement of the AI decision-making process.

Target: ~400 lines - Complete learning and adaptation functionality
"""

import json
import logging
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime, timedelta
from collections import defaultdict

logger = logging.getLogger(__name__)


class LearningManager:
    """
    Manages pattern learning and AI improvement operations.
    
    Handles user feedback processing, confidence threshold adjustments,
    pattern recognition, and decision accuracy tracking.
    """
    
    def __init__(self, database=None, confidence_threshold: float = 0.7):
        """Initialize the LearningManager with required components."""
        self.database = database
        self.base_confidence_threshold = confidence_threshold
        
        # Learning configuration
        self.min_pattern_occurrences = 3
        self.learning_decay_factor = 0.95
        self.confidence_adjustment_rate = 0.1
        
        logger.info(f"LearningManager initialized with threshold: {confidence_threshold}")
    
    async def learn_from_feedback(self, feedback_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process user feedback and update learned patterns.
        
        Args:
            feedback_data: Dict containing feedback information
                - action_id: ID of the action being reviewed
                - decision: 'approve' or 'reject'
                - correction: Optional corrected values
                - context: Additional context information
        
        Returns:
            Dict with learning results
        """
        try:
            action_id = feedback_data.get('action_id')
            decision = feedback_data.get('decision')  # 'approve' or 'reject'
            correction = feedback_data.get('correction', {})
            context = feedback_data.get('context', {})
            
            if not action_id or not decision:
                return {'success': False, 'error': 'Missing required feedback data'}
            
            # Get original action details
            original_action = self._get_action_details(action_id)
            if not original_action:
                return {'success': False, 'error': 'Original action not found'}
            
            # Process feedback
            feedback_result = self._process_feedback(original_action, decision, correction, context)
            
            # Update patterns
            pattern_updates = await self._update_patterns(original_action, feedback_result)
            
            # Adjust confidence thresholds if needed
            threshold_adjustments = self._adjust_confidence_thresholds(feedback_result)
            
            # Log the learning event
            learning_event = {
                'timestamp': datetime.now(),
                'action_id': action_id,
                'feedback': decision,
                'patterns_updated': len(pattern_updates),
                'threshold_adjustments': threshold_adjustments
            }
            
            if self.database:
                self.database.log_learning_event(learning_event)
            
            return {
                'success': True,
                'feedback_processed': True,
                'patterns_updated': pattern_updates,
                'threshold_adjustments': threshold_adjustments,
                'learning_event': learning_event
            }
            
        except Exception as e:
            logger.error(f"Error learning from feedback: {e}")
            return {'success': False, 'error': str(e)}
    
    def get_learned_patterns(self) -> Dict[str, Any]:
        """
        Retrieve all learned patterns and their effectiveness.
        
        Returns:
            Dict with categorized learned patterns
        """
        try:
            patterns = {
                'folder_patterns': [],
                'tag_patterns': [],
                'domain_patterns': [],
                'content_type_patterns': [],
                'confidence_adjustments': {},
                'effectiveness_metrics': {}
            }
            
            if not self.database:
                return patterns
            
            # Get stored patterns from database
            stored_patterns = self.database.get_learned_patterns()
            
            for pattern in stored_patterns:
                pattern_type = pattern.get('type')
                
                if pattern_type == 'folder':
                    patterns['folder_patterns'].append(pattern)
                elif pattern_type == 'tag':
                    patterns['tag_patterns'].append(pattern)
                elif pattern_type == 'domain':
                    patterns['domain_patterns'].append(pattern)
                elif pattern_type == 'content_type':
                    patterns['content_type_patterns'].append(pattern)
            
            # Get confidence adjustments
            patterns['confidence_adjustments'] = self._get_confidence_adjustments()
            
            # Calculate effectiveness metrics
            patterns['effectiveness_metrics'] = self._calculate_pattern_effectiveness(stored_patterns)
            
            return patterns
            
        except Exception as e:
            logger.error(f"Error getting learned patterns: {e}")
            return {}
    
    async def apply_learned_patterns(self, analysis_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Apply learned patterns to new content analysis.
        
        Args:
            analysis_data: Content analysis data to enhance with patterns
            
        Returns:
            Enhanced analysis with pattern-based suggestions
        """
        try:
            patterns = self.get_learned_patterns()
            enhanced_analysis = analysis_data.copy()
            
            # Apply folder patterns
            folder_suggestion = self._apply_folder_patterns(analysis_data, patterns['folder_patterns'])
            if folder_suggestion:
                enhanced_analysis['suggested_folder'] = folder_suggestion
            
            # Apply tag patterns
            tag_suggestions = self._apply_tag_patterns(analysis_data, patterns['tag_patterns'])
            if tag_suggestions:
                enhanced_analysis['suggested_tags'] = tag_suggestions
            
            # Apply domain patterns
            domain_suggestion = self._apply_domain_patterns(analysis_data, patterns['domain_patterns'])
            if domain_suggestion:
                enhanced_analysis['suggested_domain'] = domain_suggestion
            
            # Adjust confidence based on pattern matching
            confidence_adjustment = self._calculate_pattern_confidence(analysis_data, patterns)
            enhanced_analysis['pattern_confidence_boost'] = confidence_adjustment
            
            enhanced_analysis['patterns_applied'] = True
            enhanced_analysis['pattern_count'] = sum(len(p) for p in patterns.values() if isinstance(p, list))
            
            return enhanced_analysis
            
        except Exception as e:
            logger.error(f"Error applying learned patterns: {e}")
            return analysis_data
    
    def calculate_confidence_adjustments(self, base_confidence: float, context: Dict[str, Any]) -> float:
        """
        Calculate confidence adjustments based on learned patterns and context.
        
        Args:
            base_confidence: Base confidence score
            context: Context information for the decision
            
        Returns:
            Adjusted confidence score
        """
        try:
            adjusted_confidence = base_confidence
            
            # Get confidence adjustment factors
            adjustments = self._get_confidence_adjustments()
            
            # Apply contextual adjustments
            content_type = context.get('content_type', 'unknown')
            if content_type in adjustments:
                type_adjustment = adjustments[content_type]
                adjusted_confidence += type_adjustment * self.confidence_adjustment_rate
            
            # Apply domain-specific adjustments
            domain = context.get('domain', 'unknown')
            domain_key = f"domain_{domain}"
            if domain_key in adjustments:
                domain_adjustment = adjustments[domain_key]
                adjusted_confidence += domain_adjustment * self.confidence_adjustment_rate
            
            # Apply recent accuracy adjustments
            recent_accuracy = self._get_recent_accuracy()
            if recent_accuracy < 0.7:  # If recent accuracy is low, be more conservative
                adjusted_confidence *= 0.9
            elif recent_accuracy > 0.9:  # If recent accuracy is high, be more confident
                adjusted_confidence *= 1.1
            
            # Ensure confidence stays within bounds
            return max(0.0, min(1.0, adjusted_confidence))
            
        except Exception as e:
            logger.error(f"Error calculating confidence adjustments: {e}")
            return base_confidence
    
    def track_decision_accuracy(self, decision_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Track accuracy of AI decisions for continuous improvement.
        
        Args:
            decision_data: Information about the decision and its outcome
            
        Returns:
            Tracking results and accuracy metrics
        """
        try:
            # Store decision for later accuracy calculation
            if self.database:
                self.database.store_decision_tracking(decision_data)
            
            # Calculate current accuracy metrics
            accuracy_metrics = self._calculate_current_accuracy()
            
            return {
                'success': True,
                'decision_tracked': True,
                'current_accuracy': accuracy_metrics
            }
            
        except Exception as e:
            logger.error(f"Error tracking decision accuracy: {e}")
            return {'success': False, 'error': str(e)}
    
    def get_learning_insights(self) -> Dict[str, Any]:
        """
        Get insights about the learning process and AI improvement.
        
        Returns:
            Dict with learning insights and recommendations
        """
        try:
            insights = {
                'learning_summary': {},
                'pattern_effectiveness': {},
                'improvement_trends': {},
                'recommendations': []
            }
            
            # Learning summary
            patterns = self.get_learned_patterns()
            insights['learning_summary'] = {
                'total_patterns': sum(len(p) for p in patterns.values() if isinstance(p, list)),
                'folder_patterns': len(patterns.get('folder_patterns', [])),
                'tag_patterns': len(patterns.get('tag_patterns', [])),
                'domain_patterns': len(patterns.get('domain_patterns', [])),
                'confidence_adjustments': len(patterns.get('confidence_adjustments', {}))
            }
            
            # Pattern effectiveness
            insights['pattern_effectiveness'] = patterns.get('effectiveness_metrics', {})
            
            # Improvement trends
            insights['improvement_trends'] = self._analyze_improvement_trends()
            
            # Generate recommendations
            insights['recommendations'] = self._generate_learning_recommendations(insights)
            
            return insights
            
        except Exception as e:
            logger.error(f"Error getting learning insights: {e}")
            return {}
    
    def _get_action_details(self, action_id: str) -> Optional[Dict[str, Any]]:
        """Get details of a specific action."""
        if not self.database:
            return None
        
        try:
            return self.database.get_action_by_id(action_id)
        except Exception as e:
            logger.error(f"Error getting action details: {e}")
            return None
    
    def _process_feedback(self, original_action: Dict, decision: str, 
                         correction: Dict, context: Dict) -> Dict[str, Any]:
        """Process user feedback and extract learning information."""
        feedback_result = {
            'decision': decision,
            'approved': decision == 'approve',
            'original_confidence': original_action.get('confidence', 0.0),
            'action_type': original_action.get('action_type'),
            'context': context
        }
        
        if decision == 'reject' and correction:
            feedback_result['correction'] = correction
            feedback_result['corrected_folder'] = correction.get('folder')
            feedback_result['corrected_tags'] = correction.get('tags', [])
            feedback_result['corrected_domain'] = correction.get('domain')
        
        return feedback_result
    
    async def _update_patterns(self, original_action: Dict, feedback_result: Dict) -> List[Dict]:
        """Update learned patterns based on feedback."""
        pattern_updates = []
        
        try:
            if feedback_result['approved']:
                # Reinforce successful patterns
                pattern_updates.extend(self._reinforce_patterns(original_action))
            else:
                # Learn from corrections
                if 'correction' in feedback_result:
                    pattern_updates.extend(self._learn_from_correction(original_action, feedback_result['correction']))
                # Weaken unsuccessful patterns
                pattern_updates.extend(self._weaken_patterns(original_action))
            
            # Store updated patterns
            if self.database and pattern_updates:
                for pattern in pattern_updates:
                    self.database.update_learned_pattern(pattern)
            
        except Exception as e:
            logger.error(f"Error updating patterns: {e}")
        
        return pattern_updates
    
    def _reinforce_patterns(self, action: Dict) -> List[Dict]:
        """Reinforce patterns that led to successful decisions."""
        patterns = []
        
        # Reinforce folder pattern
        if 'folder' in action and 'content_type' in action:
            patterns.append({
                'type': 'folder',
                'content_type': action['content_type'],
                'folder': action['folder'],
                'reinforced': True,
                'timestamp': datetime.now()
            })
        
        # Reinforce tag patterns
        if 'tags' in action and 'keywords' in action:
            for tag in action['tags']:
                patterns.append({
                    'type': 'tag',
                    'keywords': action['keywords'][:3],  # Top 3 keywords
                    'tag': tag,
                    'reinforced': True,
                    'timestamp': datetime.now()
                })
        
        return patterns
    
    def _learn_from_correction(self, original_action: Dict, correction: Dict) -> List[Dict]:
        """Learn new patterns from user corrections."""
        patterns = []
        
        # Learn corrected folder pattern
        if 'folder' in correction and 'content_type' in original_action:
            patterns.append({
                'type': 'folder',
                'content_type': original_action['content_type'],
                'folder': correction['folder'],
                'learned_from_correction': True,
                'original_folder': original_action.get('folder'),
                'timestamp': datetime.now()
            })
        
        # Learn corrected tag patterns
        if 'tags' in correction and 'keywords' in original_action:
            for tag in correction['tags']:
                patterns.append({
                    'type': 'tag',
                    'keywords': original_action['keywords'][:3],
                    'tag': tag,
                    'learned_from_correction': True,
                    'timestamp': datetime.now()
                })
        
        return patterns
    
    def _weaken_patterns(self, action: Dict) -> List[Dict]:
        """Weaken patterns that led to unsuccessful decisions."""
        patterns = []
        
        # This would involve finding existing patterns that matched this action
        # and reducing their confidence/weight
        # Implementation depends on how patterns are stored
        
        return patterns
    
    def _adjust_confidence_thresholds(self, feedback_result: Dict) -> Dict[str, float]:
        """Adjust confidence thresholds based on feedback."""
        adjustments = {}
        
        try:
            action_type = feedback_result.get('action_type')
            original_confidence = feedback_result.get('original_confidence', 0.0)
            approved = feedback_result.get('approved', False)
            
            if action_type:
                # Adjust threshold for this action type
                current_adjustment = self._get_current_adjustment(action_type)
                
                if approved and original_confidence < 0.8:
                    # Decision was good but confidence was low - lower threshold
                    new_adjustment = current_adjustment - 0.05
                elif not approved and original_confidence > 0.6:
                    # Decision was bad but confidence was high - raise threshold
                    new_adjustment = current_adjustment + 0.05
                else:
                    new_adjustment = current_adjustment
                
                # Store adjustment
                adjustments[action_type] = new_adjustment
                
                if self.database:
                    self.database.update_confidence_adjustment(action_type, new_adjustment)
        
        except Exception as e:
            logger.error(f"Error adjusting confidence thresholds: {e}")
        
        return adjustments
    
    def _apply_folder_patterns(self, analysis: Dict, patterns: List[Dict]) -> Optional[str]:
        """Apply learned folder patterns to analysis."""
        content_type = analysis.get('content_type', 'unknown')
        
        for pattern in patterns:
            if pattern.get('content_type') == content_type:
                if pattern.get('accuracy', 0) > 0.7:  # Only use high-accuracy patterns
                    return pattern.get('folder')
        
        return None
    
    def _apply_tag_patterns(self, analysis: Dict, patterns: List[Dict]) -> List[str]:
        """Apply learned tag patterns to analysis."""
        suggested_tags = []
        keywords = analysis.get('keywords', [])
        
        for pattern in patterns:
            pattern_keywords = pattern.get('keywords', [])
            if any(keyword in keywords for keyword in pattern_keywords):
                if pattern.get('accuracy', 0) > 0.6:
                    suggested_tags.append(pattern.get('tag'))
        
        return list(set(suggested_tags))  # Remove duplicates
    
    def _apply_domain_patterns(self, analysis: Dict, patterns: List[Dict]) -> Optional[str]:
        """Apply learned domain patterns to analysis."""
        keywords = analysis.get('keywords', [])
        
        for pattern in patterns:
            pattern_keywords = pattern.get('keywords', [])
            if any(keyword in keywords for keyword in pattern_keywords):
                if pattern.get('accuracy', 0) > 0.7:
                    return pattern.get('domain')
        
        return None
    
    def _calculate_pattern_confidence(self, analysis: Dict, patterns: Dict) -> float:
        """Calculate confidence boost based on pattern matching."""
        boost = 0.0
        
        # Boost confidence if multiple patterns match
        matching_patterns = 0
        
        if self._apply_folder_patterns(analysis, patterns.get('folder_patterns', [])):
            matching_patterns += 1
        
        if self._apply_tag_patterns(analysis, patterns.get('tag_patterns', [])):
            matching_patterns += 1
        
        if self._apply_domain_patterns(analysis, patterns.get('domain_patterns', [])):
            matching_patterns += 1
        
        # Each matching pattern adds confidence
        boost = matching_patterns * 0.1
        
        return min(boost, 0.3)  # Cap boost at 0.3
    
    def _get_confidence_adjustments(self) -> Dict[str, float]:
        """Get current confidence adjustments."""
        if not self.database:
            return {}
        
        try:
            return self.database.get_confidence_adjustments()
        except Exception as e:
            logger.error(f"Error getting confidence adjustments: {e}")
            return {}
    
    def _get_current_adjustment(self, action_type: str) -> float:
        """Get current adjustment for a specific action type."""
        adjustments = self._get_confidence_adjustments()
        return adjustments.get(action_type, 0.0)
    
    def _get_recent_accuracy(self) -> float:
        """Get recent decision accuracy."""
        if not self.database:
            return 0.5
        
        try:
            recent_decisions = self.database.get_recent_decisions(days=30)
            if not recent_decisions:
                return 0.5
            
            approved = sum(1 for d in recent_decisions if d.get('approved', False))
            return approved / len(recent_decisions)
            
        except Exception as e:
            logger.error(f"Error getting recent accuracy: {e}")
            return 0.5
    
    def _calculate_current_accuracy(self) -> Dict[str, float]:
        """Calculate current accuracy metrics."""
        metrics = {
            'overall_accuracy': 0.0,
            'recent_accuracy': 0.0,
            'accuracy_by_type': {}
        }
        
        if not self.database:
            return metrics
        
        try:
            # Overall accuracy
            all_decisions = self.database.get_all_decisions()
            if all_decisions:
                approved = sum(1 for d in all_decisions if d.get('approved', False))
                metrics['overall_accuracy'] = approved / len(all_decisions)
            
            # Recent accuracy
            metrics['recent_accuracy'] = self._get_recent_accuracy()
            
            # Accuracy by action type
            action_types = set(d.get('action_type') for d in all_decisions if d.get('action_type'))
            for action_type in action_types:
                type_decisions = [d for d in all_decisions if d.get('action_type') == action_type]
                if type_decisions:
                    approved = sum(1 for d in type_decisions if d.get('approved', False))
                    metrics['accuracy_by_type'][action_type] = approved / len(type_decisions)
        
        except Exception as e:
            logger.error(f"Error calculating current accuracy: {e}")
        
        return metrics
    
    def _calculate_pattern_effectiveness(self, patterns: List[Dict]) -> Dict[str, Any]:
        """Calculate effectiveness metrics for learned patterns."""
        effectiveness = {
            'average_accuracy': 0.0,
            'high_accuracy_patterns': 0,
            'low_accuracy_patterns': 0,
            'by_type': {}
        }
        
        if not patterns:
            return effectiveness
        
        accuracies = [p.get('accuracy', 0) for p in patterns if 'accuracy' in p]
        if accuracies:
            effectiveness['average_accuracy'] = sum(accuracies) / len(accuracies)
            effectiveness['high_accuracy_patterns'] = sum(1 for a in accuracies if a > 0.8)
            effectiveness['low_accuracy_patterns'] = sum(1 for a in accuracies if a < 0.5)
        
        # Effectiveness by pattern type
        by_type = defaultdict(list)
        for pattern in patterns:
            pattern_type = pattern.get('type', 'unknown')
            if 'accuracy' in pattern:
                by_type[pattern_type].append(pattern['accuracy'])
        
        for pattern_type, accuracies in by_type.items():
            effectiveness['by_type'][pattern_type] = sum(accuracies) / len(accuracies)
        
        return effectiveness
    
    def _analyze_improvement_trends(self) -> Dict[str, Any]:
        """Analyze trends in AI improvement over time."""
        trends = {
            'accuracy_trend': 'stable',
            'pattern_growth': 0,
            'recent_improvements': []
        }
        
        if not self.database:
            return trends
        
        try:
            # Analyze accuracy trend over time
            monthly_accuracy = self.database.get_monthly_accuracy()
            if len(monthly_accuracy) >= 2:
                recent_avg = sum(monthly_accuracy[-3:]) / len(monthly_accuracy[-3:])
                older_avg = sum(monthly_accuracy[:-3]) / len(monthly_accuracy[:-3]) if len(monthly_accuracy) > 3 else recent_avg
                
                if recent_avg > older_avg + 0.05:
                    trends['accuracy_trend'] = 'improving'
                elif recent_avg < older_avg - 0.05:
                    trends['accuracy_trend'] = 'declining'
            
            # Pattern growth
            pattern_counts = self.database.get_pattern_growth()
            if len(pattern_counts) >= 2:
                trends['pattern_growth'] = pattern_counts[-1] - pattern_counts[0]
        
        except Exception as e:
            logger.error(f"Error analyzing improvement trends: {e}")
        
        return trends
    
    def _generate_learning_recommendations(self, insights: Dict) -> List[str]:
        """Generate recommendations based on learning insights."""
        recommendations = []
        
        # Pattern effectiveness recommendations
        effectiveness = insights.get('pattern_effectiveness', {})
        avg_accuracy = effectiveness.get('average_accuracy', 0)
        
        if avg_accuracy < 0.6:
            recommendations.append("Consider collecting more user feedback to improve pattern accuracy")
        
        low_accuracy = effectiveness.get('low_accuracy_patterns', 0)
        if low_accuracy > 5:
            recommendations.append("Review and clean up low-accuracy patterns")
        
        # Trend-based recommendations
        trends = insights.get('improvement_trends', {})
        if trends.get('accuracy_trend') == 'declining':
            recommendations.append("AI accuracy is declining - investigate recent changes")
        
        pattern_growth = trends.get('pattern_growth', 0)
        if pattern_growth < 0:
            recommendations.append("Pattern learning has slowed - encourage more user feedback")
        
        # Summary recommendations
        total_patterns = insights.get('learning_summary', {}).get('total_patterns', 0)
        if total_patterns < 10:
            recommendations.append("More patterns needed for effective learning")
        
        return recommendations
