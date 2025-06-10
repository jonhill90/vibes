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
                 database=None):
        """Initialize the InboxManager with required components."""
        self.vault_path = vault_path
        self.inbox_path = os.path.join(vault_path, "0 - Inbox")
        
        # Component dependencies
        self.notes_manager = notes_manager
        self.pattern_learner = pattern_learner
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
            
            # Basic analysis fallback
            analysis = self._analyze_content_basic(content, title)
            
            return {
                'success': True,
                'analysis': analysis,
                'file_path': file_path,
                'title': title,
                'content_length': len(content)
            }
            
        except Exception as e:
            logger.error(f"Failed to analyze file {file_path}: {e}")
            return {'success': False, 'error': str(e)}
    
    def _analyze_content_basic(self, content: str, title: str) -> Dict[str, Any]:
        """Basic content analysis as fallback."""
        lines = content.split('\n')
        word_count = len(content.split())
        
        # Simple domain classification
        domain = 'general'
        if any(word in content.lower() for word in ['code', 'programming', 'function', 'class']):
            domain = 'technical'
        elif any(word in content.lower() for word in ['meeting', 'agenda', 'todo', 'task']):
            domain = 'productivity'
        elif any(word in content.lower() for word in ['idea', 'concept', 'thought', 'inspiration']):
            domain = 'ideas'
        
        return {
            'domain': domain,
            'confidence': 0.7,  # Basic analysis confidence
            'word_count': word_count,
            'line_count': len(lines),
            'suggested_tags': [domain],
            'processing_recommendation': 'review' if word_count > 500 else 'auto'
        }
    
    def _extract_title(self, filename: str, content: str) -> str:
        """Extract title from filename or content."""
        # Try to get title from first line if it looks like a title
        lines = content.split('\n')
        if lines and len(lines[0]) < 100 and not lines[0].startswith('#'):
            return lines[0].strip()
        
        # Fall back to filename without extension
        return os.path.splitext(filename)[0]
