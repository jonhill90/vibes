"""
INMPARA Inbox Module

This module handles batch processing of inbox items, including file analysis,
routing decisions, and automated processing based on learned patterns.

Target: ~400 lines - Complete inbox processing pipeline
"""

import os
import json
import logging
from typing import Dict, List, Any, Optional, Tuple
from pathlib import Path
from datetime import datetime

logger = logging.getLogger(__name__)


class InboxManager:
    """
    Manages inbox processing operations for the INMPARA vault.
    
    Handles batch processing, confidence-based routing, automated decisions,
    and integration with learning patterns for continuous improvement.
    """
    
    def __init__(self, vault_path: str, notes_manager=None, pattern_learner=None,
                 content_analyzer=None, database=None):
        """Initialize the InboxManager with required components."""
        self.vault_path = vault_path
        self.inbox_path = os.path.join(vault_path, "0 - Inbox")
        
        # Component dependencies
        self.notes_manager = notes_manager
        self.pattern_learner = pattern_learner
        self.content_analyzer = content_analyzer
        self.database = database
        
        # Processing configuration
        self.default_batch_size = 10
        self.high_confidence_threshold = 0.85
        self.medium_confidence_threshold = 0.6
        self.auto_approve_threshold = 0.9
        
        logger.info(f"InboxManager initialized for inbox: {self.inbox_path}")
    
    async def process_inbox(self, batch_size: int = None, confidence_threshold: float = None,
                          auto_approve: bool = False) -> Dict[str, Any]:
        """
        Main inbox processing pipeline with learned patterns and automation.
        
        Args:
            batch_size: Number of items to process in one batch
            confidence_threshold: Minimum confidence for auto-processing
            auto_approve: Whether to automatically approve high-confidence decisions
            
        Returns:
            Dict with processing results and statistics
        """
        try:
            batch_size = batch_size or self.default_batch_size
            confidence_threshold = confidence_threshold or self.medium_confidence_threshold
            
            # Get inbox items
            inbox_items = self.get_inbox_items()
            
            if not inbox_items:
                return {
                    'success': True,
                    'processed': 0,
                    'message': 'No items found in inbox'
                }
            
            # Limit to batch size
            items_to_process = inbox_items[:batch_size]
            
            # Process each item
            processing_results = []
            auto_processed = 0
            manual_review = 0
            errors = 0
            
            for item in items_to_process:
                try:
                    result = await self.process_inbox_item(
                        item, confidence_threshold, auto_approve
                    )
                    
                    processing_results.append(result)
                    
                    # Update counters
                    if result.get('auto_processed'):
                        auto_processed += 1
                    elif result.get('needs_review'):
                        manual_review += 1
                    elif not result.get('success'):
                        errors += 1
                        
                except Exception as e:
                    logger.error(f"Error processing item {item['path']}: {e}")
                    errors += 1
                    processing_results.append({
                        'success': False,
                        'item': item,
                        'error': str(e)
                    })
            
            # Generate summary
            summary = {
                'success': True,
                'total_items': len(inbox_items),
                'processed': len(processing_results),
                'auto_processed': auto_processed,
                'manual_review': manual_review,
                'errors': errors,
                'remaining_in_inbox': len(inbox_items) - len(items_to_process),
                'confidence_threshold': confidence_threshold,
                'auto_approve_enabled': auto_approve,
                'results': processing_results
            }
            
            # Log processing action
            if self.database:
                self.database.log_processing_action({
                    'action': 'inbox_batch_process',
                    'timestamp': datetime.now(),
                    'items_processed': len(processing_results),
                    'auto_processed': auto_processed,
                    'manual_review': manual_review,
                    'errors': errors
                })
            
            return summary
            
        except Exception as e:
            logger.error(f"Error in inbox processing: {e}")
            return {'success': False, 'error': str(e)}
    
    async def process_inbox_item(self, item: Dict[str, Any], confidence_threshold: float,
                               auto_approve: bool) -> Dict[str, Any]:
        """
        Process a single inbox item with learned patterns.
        
        Args:
            item: Inbox item information
            confidence_threshold: Confidence threshold for auto-processing
            auto_approve: Whether to auto-approve high confidence decisions
            
        Returns:
            Dict with processing result
        """
        try:
            file_path = item['path']
            
            # Analyze the file
            analysis = await self.analyze_inbox_file(file_path)
            
            if not analysis['success']:
                return {
                    'success': False,
                    'item': item,
                    'error': analysis.get('error', 'Analysis failed')
                }
            
            # Get routing decision with confidence
            routing_decision = await self.get_routing_decision(analysis, file_path)
            
            confidence = routing_decision.get('confidence', 0.0)
            
            # Determine processing action based on confidence
            if confidence >= self.auto_approve_threshold and auto_approve:
                # High confidence - auto process
                result = await self.auto_process_file(item, routing_decision)
                result['auto_processed'] = True
                result['confidence'] = confidence
                
            elif confidence >= confidence_threshold:
                # Medium confidence - suggest with high confidence
                result = {
                    'success': True,
                    'item': item,
                    'analysis': analysis,
                    'routing_decision': routing_decision,
                    'confidence': confidence,
                    'recommendation': 'auto_process',
                    'needs_review': False,
                    'message': f'High confidence recommendation (confidence: {confidence:.2f})'
                }
                
            else:
                # Low confidence - manual review needed
                result = {
                    'success': True,
                    'item': item,
                    'analysis': analysis,
                    'routing_decision': routing_decision,
                    'confidence': confidence,
                    'recommendation': 'manual_review',
                    'needs_review': True,
                    'message': f'Manual review recommended (confidence: {confidence:.2f})'
                }
            
            return result
            
        except Exception as e:
            logger.error(f"Error processing inbox item: {e}")
            return {
                'success': False,
                'item': item,
                'error': str(e)
            }
    
    async def analyze_inbox_file(self, file_path: str) -> Dict[str, Any]:
        """
        Analyze an inbox file for content and metadata.
        
        Args:
            file_path: Path to the file to analyze
            
        Returns:
            Dict with analysis results
        """
        try:
            if not os.path.exists(file_path):
                return {'success': False, 'error': 'File does not exist'}
            
            # Read file content
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            if not content.strip():
                return {'success': False, 'error': 'File is empty'}
            
            # Extract title from filename or content
            filename = os.path.basename(file_path)
            title = self._extract_title(filename, content)
            
            # Use content analyzer if available
            if self.content_analyzer:
                analysis = await self.content_analyzer.analyze_content(content, title)
            else:
                # Basic analysis fallback
                analysis = self._basic_content_analysis(content, title)
            
            # Add file metadata
            stat = os.stat(file_path)
            analysis.update({
                'file_path': file_path,
                'filename': filename,
                'title': title,
                'file_size': stat.st_size,
                'created_time': stat.st_ctime,
                'modified_time': stat.st_mtime
            })
            
            return {
                'success': True,
                'analysis': analysis
            }
            
        except Exception as e:
            logger.error(f"Error analyzing inbox file: {e}")
            return {'success': False, 'error': str(e)}
    
    async def get_routing_decision(self, analysis: Dict[str, Any], file_path: str) -> Dict[str, Any]:
        """
        Get routing decision with confidence based on learned patterns.
        
        Args:
            analysis: File analysis results
            file_path: Path to the file
            
        Returns:
            Dict with routing decision and confidence
        """
        try:
            # Get learned patterns if available
            learned_patterns = {}
            if self.pattern_learner:
                learned_patterns = self.pattern_learner.get_learned_patterns()
            
            # Determine destination folder
            destination = self._determine_destination(analysis, learned_patterns)
            
            # Determine tags
            suggested_tags = self._suggest_tags(analysis, learned_patterns)
            
            # Determine domain
            domain = self._determine_domain(analysis, learned_patterns)
            
            # Calculate confidence based on various factors
            confidence = self._calculate_routing_confidence(
                analysis, destination, suggested_tags, domain, learned_patterns
            )
            
            routing_decision = {
                'destination_folder': destination['folder'],
                'suggested_filename': destination['filename'],
                'tags': suggested_tags,
                'domain': domain,
                'confidence': confidence,
                'reasoning': destination.get('reasoning', ''),
                'learned_patterns_applied': len(learned_patterns) > 0
            }
            
            return routing_decision
            
        except Exception as e:
            logger.error(f"Error getting routing decision: {e}")
            return {
                'destination_folder': '1 - Notes',
                'tags': [],
                'domain': 'General',
                'confidence': 0.1,
                'error': str(e)
            }
    
    async def auto_process_file(self, item: Dict[str, Any], routing_decision: Dict[str, Any]) -> Dict[str, Any]:
        """
        Automatically process a file based on routing decision.
        
        Args:
            item: Inbox item information
            routing_decision: Routing decision with destination and metadata
            
        Returns:
            Dict with processing result
        """
        try:
            file_path = item['path']
            
            # Read file content
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Extract title
            title = routing_decision.get('suggested_filename', os.path.basename(file_path))
            title = title.replace('.md', '').replace('-', ' ').title()
            
            # Create note using NotesManager
            if self.notes_manager:
                note_result = await self.notes_manager.create_note(
                    title=title,
                    content=content,
                    tags=routing_decision.get('tags', []),
                    domain=routing_decision.get('domain', 'General'),
                    source='inbox_auto'
                )
                
                if note_result['success']:
                    # Move original file to processed or delete
                    processed_path = self._move_to_processed(file_path)
                    
                    return {
                        'success': True,
                        'item': item,
                        'note_created': note_result,
                        'original_moved_to': processed_path,
                        'message': 'File auto-processed successfully'
                    }
                else:
                    return {
                        'success': False,
                        'item': item,
                        'error': note_result.get('error', 'Note creation failed')
                    }
            else:
                return {
                    'success': False,
                    'item': item,
                    'error': 'NotesManager not available'
                }
            
        except Exception as e:
            logger.error(f"Error auto-processing file: {e}")
            return {
                'success': False,
                'item': item,
                'error': str(e)
            }
    
    def get_inbox_items(self) -> List[Dict[str, Any]]:
        """Get list of items in the inbox folder."""
        items = []
        
        if not os.path.exists(self.inbox_path):
            logger.warning(f"Inbox path does not exist: {self.inbox_path}")
            return items
        
        try:
            for root, dirs, files in os.walk(self.inbox_path):
                for file in files:
                    if file.endswith('.md'):
                        file_path = os.path.join(root, file)
                        stat = os.stat(file_path)
                        
                        items.append({
                            'name': file,
                            'path': file_path,
                            'size': stat.st_size,
                            'created': stat.st_ctime,
                            'modified': stat.st_mtime
                        })
            
            # Sort by modification time (newest first)
            items.sort(key=lambda x: x['modified'], reverse=True)
            
        except Exception as e:
            logger.error(f"Error getting inbox items: {e}")
        
        return items
    
    def _extract_title(self, filename: str, content: str) -> str:
        """Extract title from filename or content."""
        # Try to get title from content first (if it has frontmatter)
        if content.startswith('---'):
            try:
                import yaml
                parts = content.split('---', 2)
                if len(parts) >= 3:
                    frontmatter = yaml.safe_load(parts[1])
                    if 'title' in frontmatter:
                        return frontmatter['title']
            except:
                pass
        
        # Try to get title from first heading
        lines = content.split('\n')
        for line in lines:
            if line.startswith('# '):
                return line[2:].strip()
        
        # Fall back to filename
        title = filename.replace('.md', '').replace('_', ' ').replace('-', ' ')
        return title.title()
    
    def _basic_content_analysis(self, content: str, title: str) -> Dict[str, Any]:
        """Basic content analysis fallback."""
        import re
        
        word_count = len(content.split())
        
        # Extract keywords
        words = re.findall(r'\b[a-zA-Z]{3,}\b', content.lower())
        keywords = list(set(words))[:10]
        
        # Determine basic content type
        content_lower = content.lower()
        if 'project' in content_lower:
            content_type = 'project'
        elif 'meeting' in content_lower:
            content_type = 'meeting'
        elif any(word in content_lower for word in ['todo', 'task', 'action']):
            content_type = 'tasks'
        else:
            content_type = 'note'
        
        return {
            'word_count': word_count,
            'keywords': keywords,
            'content_type': content_type,
            'complexity': 'high' if word_count > 500 else 'medium' if word_count > 100 else 'low'
        }
    
    def _determine_destination(self, analysis: Dict[str, Any], learned_patterns: Dict) -> Dict[str, Any]:
        """Determine destination folder based on analysis and patterns."""
        content_type = analysis.get('content_type', 'note')
        
        # Default mapping
        folder_mapping = {
            'project': '3 - Projects',
            'meeting': '1 - Notes/Meetings',
            'tasks': '1 - Notes/Tasks',
            'note': '1 - Notes'
        }
        
        folder = folder_mapping.get(content_type, '1 - Notes')
        
        # Apply learned patterns if available
        if learned_patterns and 'folder_patterns' in learned_patterns:
            pattern_match = self._apply_folder_patterns(analysis, learned_patterns['folder_patterns'])
            if pattern_match:
                folder = pattern_match['folder']
        
        # Generate filename
        title = analysis.get('title', 'Untitled')
        safe_title = re.sub(r'[<>:"/\\|?*]', '', title)
        timestamp = datetime.now().strftime("%Y%m%d")
        filename = f"{safe_title} - {timestamp}.md"
        
        return {
            'folder': folder,
            'filename': filename,
            'reasoning': f"Content type: {content_type}"
        }
    
    def _suggest_tags(self, analysis: Dict[str, Any], learned_patterns: Dict) -> List[str]:
        """Suggest tags based on analysis and learned patterns."""
        tags = []
        
        # Add content type tag
        content_type = analysis.get('content_type')
        if content_type and content_type != 'note':
            tags.append(content_type)
        
        # Add keyword-based tags
        keywords = analysis.get('keywords', [])
        for keyword in keywords[:3]:  # Top 3 keywords
            if len(keyword) > 3:
                tags.append(keyword)
        
        # Apply learned tag patterns
        if learned_patterns and 'tag_patterns' in learned_patterns:
            pattern_tags = self._apply_tag_patterns(analysis, learned_patterns['tag_patterns'])
            tags.extend(pattern_tags)
        
        return list(set(tags))[:6]  # Max 6 unique tags
    
    def _determine_domain(self, analysis: Dict[str, Any], learned_patterns: Dict) -> str:
        """Determine domain based on analysis and learned patterns."""
        # Default domain detection
        keywords = analysis.get('keywords', [])
        content = ' '.join(keywords).lower()
        
        if any(word in content for word in ['ai', 'machine', 'learning', 'neural']):
            return 'AI'
        elif any(word in content for word in ['business', 'strategy', 'market']):
            return 'Business'
        elif any(word in content for word in ['code', 'programming', 'software']):
            return 'Technology'
        else:
            return 'General'
    
    def _calculate_routing_confidence(self, analysis: Dict, destination: Dict,
                                    tags: List[str], domain: str, learned_patterns: Dict) -> float:
        """Calculate confidence score for routing decision."""
        confidence = 0.5  # Base confidence
        
        # Boost confidence based on clear indicators
        content_type = analysis.get('content_type')
        if content_type in ['project', 'meeting']:
            confidence += 0.2
        
        # Boost confidence if learned patterns were applied
        if learned_patterns:
            confidence += 0.2
        
        # Boost confidence based on keyword strength
        keywords = analysis.get('keywords', [])
        if len(keywords) > 5:
            confidence += 0.1
        
        # Cap at 1.0
        return min(confidence, 1.0)
    
    def _apply_folder_patterns(self, analysis: Dict, patterns: List[Dict]) -> Optional[Dict]:
        """Apply learned folder patterns to analysis."""
        # Simplified pattern matching
        for pattern in patterns:
            if pattern.get('accuracy', 0) > 0.8:
                return pattern
        return None
    
    def _apply_tag_patterns(self, analysis: Dict, patterns: List[Dict]) -> List[str]:
        """Apply learned tag patterns to analysis."""
        suggested_tags = []
        for pattern in patterns:
            if pattern.get('accuracy', 0) > 0.7:
                suggested_tags.extend(pattern.get('tags', []))
        return suggested_tags[:3]
    
    def _move_to_processed(self, file_path: str) -> str:
        """Move processed file to a processed folder or delete it."""
        try:
            processed_dir = os.path.join(self.vault_path, "_processed")
            os.makedirs(processed_dir, exist_ok=True)
            
            filename = os.path.basename(file_path)
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            new_filename = f"{timestamp}_{filename}"
            new_path = os.path.join(processed_dir, new_filename)
            
            os.rename(file_path, new_path)
            return new_path
            
        except Exception as e:
            logger.error(f"Error moving processed file: {e}")
            # If moving fails, just delete the original
            try:
                os.remove(file_path)
                return "deleted"
            except:
                return "error"
