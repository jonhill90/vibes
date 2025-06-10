"""
INMPARA Notes Module

This module handles all note creation, validation, and formatting operations
following the INMPARA methodology and format standards.

Target: ~400 lines - Complete note lifecycle management
"""

import os
import yaml
import re
import logging
from datetime import datetime
from typing import Dict, List, Any, Optional, Tuple
from pathlib import Path

logger = logging.getLogger(__name__)


class NotesManager:
    """
    Manages note creation, validation, and formatting operations.
    
    Handles INMPARA format compliance, content analysis, frontmatter generation,
    auto-tagging, and file placement logic.
    """
    
    def __init__(self, vault_path: str, file_manager=None):
        """Initialize the NotesManager with required components."""
        self.vault_path = vault_path
        self.file_manager = file_manager
        
        # INMPARA folder structure
        self.folder_mapping = {
            'note': '1 - Notes',
            'moc': '2 - MOCs', 
            'project': '3 - Projects',
            'area': '4 - Areas',
            'resource': '5 - Resources',
            'archive': '6 - Archive'
        }
        
        # Domain-specific folder mappings
        self.domain_mappings = {
            'AI': '1 - Notes/AI',
            'Technology': '1 - Notes/Tech',
            'Business': '1 - Notes/Business',
            'Personal': '1 - Notes/Personal',
            'Learning': '1 - Notes/Learning',
            'Research': '1 - Notes/Research'
        }
        
        logger.info(f"NotesManager initialized for vault: {vault_path}")
    
    async def create_note(self, title: str, content: str, tags: List[str] = None,
                         domain: str = None, note_type: str = "note",
                         source: str = "manual") -> Dict[str, Any]:
        """
        Main note creation function with INMPARA formatting.
        
        Args:
            title: Note title
            content: Note content
            tags: List of tags
            domain: Content domain
            note_type: Type of note (note, moc, project, etc.)
            source: Source of note creation
            
        Returns:
            Dict with creation results including file_path, note_id, etc.
        """
        try:
            # Validate inputs
            validation_result = self.validate_note_inputs(title, content)
            if not validation_result['valid']:
                return validation_result
            
            # Analyze content for metadata extraction
            analysis = await self.analyze_content(content, title, domain)
            
            # Generate tags if not provided
            if not tags:
                tags = self.suggest_tags(content, domain, analysis)
            
            # Determine note placement
            folder_path = self.determine_destination(domain, note_type, analysis)
            
            # Generate frontmatter
            frontmatter = self.generate_frontmatter(
                title=title,
                tags=tags,
                domain=domain,
                note_type=note_type,
                source=source,
                analysis=analysis
            )
            
            # Format content with INMPARA structure
            formatted_content = self.format_note_content(content, analysis)
            
            # Combine frontmatter and content
            full_content = f"{frontmatter}\n\n{formatted_content}"
            
            # Generate filename
            filename = self.generate_filename(title, note_type)
            file_path = os.path.join(folder_path, filename)
            
            # Ensure directory exists
            os.makedirs(folder_path, exist_ok=True)
            
            # Save note
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(full_content)
            
            # Validate INMPARA format
            format_validation = self.validate_inmpara_format(file_path)
            
            result = {
                'success': True,
                'file_path': file_path,
                'title': title,
                'tags': tags,
                'domain': domain,
                'folder': folder_path,
                'analysis': analysis,
                'format_valid': format_validation['valid'],
                'message': 'Note created successfully'
            }
            
            logger.info(f"Note created: {file_path}")
            return result
            
        except Exception as e:
            logger.error(f"Error creating note: {e}")
            return {
                'success': False,
                'error': str(e),
                'message': 'Failed to create note'
            }
    
    def validate_note_inputs(self, title: str, content: str) -> Dict[str, Any]:
        """Validate note creation inputs."""
        if not title or not title.strip():
            return {'valid': False, 'error': 'Title is required'}
        
        if not content or not content.strip():
            return {'valid': False, 'error': 'Content is required'}
        
        if len(title) > 200:
            return {'valid': False, 'error': 'Title too long (max 200 characters)'}
        
        return {'valid': True}
    
    async def analyze_content(self, content: str, title: str, domain: str) -> Dict[str, Any]:
        """Analyze content for metadata extraction and classification."""
        
        # Basic content analysis fallback
        word_count = len(content.split())
        
        # Simple keyword extraction
        keywords = self.extract_keywords(content, title)
        
        # Determine content type based on patterns
        content_type = self.classify_content_type(content, title)
        
        return {
            'word_count': word_count,
            'keywords': keywords,
            'content_type': content_type,
            'complexity': 'medium' if word_count > 200 else 'low',
            'domain': domain or 'General',
            'confidence': 0.7  # Medium confidence for basic analysis
        }
    
    def extract_keywords(self, content: str, title: str) -> List[str]:
        """Extract basic keywords from content."""
        # Combine title and content
        text = f"{title} {content}".lower()
        
        # Remove common words and extract meaningful terms
        common_words = {'the', 'is', 'at', 'which', 'on', 'and', 'a', 'to', 'are', 'as', 'was', 'will', 'be'}
        words = re.findall(r'\b[a-zA-Z]{3,}\b', text)
        keywords = [word for word in words if word not in common_words]
        
        # Return most frequent unique keywords
        unique_keywords = list(set(keywords))
        return unique_keywords[:10]  # Top 10 keywords
    
    def classify_content_type(self, content: str, title: str) -> str:
        """Classify content type based on patterns."""
        text = f"{title} {content}".lower()
        
        if any(word in text for word in ['project', 'goals', 'timeline', 'deliverable']):
            return 'project'
        elif any(word in text for word in ['overview', 'index', 'map of content', 'moc']):
            return 'moc'
        elif any(word in text for word in ['area', 'ongoing', 'responsibility']):
            return 'area'
        elif any(word in text for word in ['resource', 'reference', 'link', 'tool']):
            return 'resource'
        else:
            return 'note'
    
    def suggest_tags(self, content: str, domain: str, analysis: Dict[str, Any]) -> List[str]:
        """Auto-suggest tags based on content analysis."""
        suggested_tags = []
        
        # Add domain tag
        if domain:
            suggested_tags.append(domain.lower())
        
        # Add content type tag
        content_type = analysis.get('content_type', 'note')
        if content_type != 'note':
            suggested_tags.append(content_type)
        
        # Add keyword-based tags
        keywords = analysis.get('keywords', [])
        for keyword in keywords[:5]:  # Top 5 keywords as tags
            if len(keyword) > 2 and keyword not in suggested_tags:
                suggested_tags.append(keyword)
        
        # Add automatic tags based on patterns
        content_lower = content.lower()
        if 'todo' in content_lower or 'task' in content_lower:
            suggested_tags.append('tasks')
        if 'meeting' in content_lower:
            suggested_tags.append('meeting')
        if 'idea' in content_lower:
            suggested_tags.append('ideas')
        
        return suggested_tags[:8]  # Max 8 tags
    
    def determine_destination(self, domain: str, note_type: str, analysis: Dict[str, Any]) -> str:
        """Determine the destination folder for the note."""
        # Get base folder for note type
        base_folder = self.folder_mapping.get(note_type, '1 - Notes')
        base_path = os.path.join(self.vault_path, base_folder)
        
        # Add domain subfolder if specified
        if domain and domain in self.domain_mappings:
            domain_path = os.path.join(self.vault_path, self.domain_mappings[domain])
            return domain_path
        elif domain:
            # Create custom domain folder
            domain_folder = f"1 - Notes/{domain}"
            return os.path.join(self.vault_path, domain_folder)
        
        return base_path
    
    def generate_frontmatter(self, title: str, tags: List[str], domain: str,
                           note_type: str, source: str, analysis: Dict[str, Any]) -> str:
        """Generate INMPARA-compliant frontmatter."""
        timestamp = datetime.now().strftime("%Y-%m-%d")
        
        # Create slug for permalink
        slug = re.sub(r'[^a-zA-Z0-9\s-]', '', title.lower())
        slug = re.sub(r'\s+', '-', slug)
        
        frontmatter_data = {
            'title': title,
            'date': timestamp,
            'tags': tags,
            'domain': domain or 'General',
            'type': note_type,
            'status': 'active',
            'source': source,
            'permalink': f"/{slug}",
            'word_count': analysis.get('word_count', 0),
            'complexity': analysis.get('complexity', 'medium')
        }
        
        # Add additional metadata if available
        if 'confidence' in analysis:
            frontmatter_data['ai_confidence'] = analysis['confidence']
        
        # Convert to YAML
        yaml_content = yaml.dump(frontmatter_data, default_flow_style=False, sort_keys=False)
        return f"---\n{yaml_content}---"
    
    def format_note_content(self, content: str, analysis: Dict[str, Any]) -> str:
        """Format content with INMPARA structure."""
        formatted_content = content
        
        # Add automatic structure for certain content types
        content_type = analysis.get('content_type', 'note')
        
        if content_type == 'project':
            # Add project structure if not present
            if '## Overview' not in formatted_content:
                project_template = """## Overview

{content}

## Goals
- [ ] 

## Timeline
- Start: 
- End: 

## Resources
- 

## Notes
- """
                formatted_content = project_template.format(content=content)
        
        elif content_type == 'moc':
            # Add MOC structure if not present
            if '## Index' not in formatted_content:
                moc_template = """## Overview

{content}

## Index
- 

## Related Notes
- 

## Resources
- """
                formatted_content = moc_template.format(content=content)
        
        return formatted_content
    
    def generate_filename(self, title: str, note_type: str) -> str:
        """Generate a safe filename from title."""
        # Clean title for filename
        safe_title = re.sub(r'[<>:"/\\|?*]', '', title)
        safe_title = re.sub(r'\s+', ' ', safe_title).strip()
        
        # Truncate if too long
        if len(safe_title) > 100:
            safe_title = safe_title[:100].strip()
        
        # Add timestamp to ensure uniqueness
        timestamp = datetime.now().strftime("%Y%m%d-%H%M")
        
        return f"{safe_title} - {timestamp}.md"
    
    def validate_inmpara_format(self, file_path: str) -> Dict[str, Any]:
        """Validate that a note follows INMPARA format standards."""
        try:
            if not os.path.exists(file_path):
                return {'valid': False, 'error': 'File does not exist'}
            
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Check for frontmatter
            if not content.startswith('---'):
                return {'valid': False, 'error': 'Missing YAML frontmatter'}
            
            # Extract frontmatter
            parts = content.split('---', 2)
            if len(parts) < 3:
                return {'valid': False, 'error': 'Invalid frontmatter format'}
            
            try:
                frontmatter = yaml.safe_load(parts[1])
            except yaml.YAMLError as e:
                return {'valid': False, 'error': f'Invalid YAML: {e}'}
            
            # Check required fields
            required_fields = ['title', 'date', 'tags', 'domain']
            missing_fields = [field for field in required_fields if field not in frontmatter]
            
            if missing_fields:
                return {
                    'valid': False,
                    'error': f'Missing required fields: {missing_fields}'
                }
            
            return {
                'valid': True,
                'frontmatter': frontmatter,
                'message': 'Note format is valid'
            }
            
        except Exception as e:
            return {'valid': False, 'error': str(e)}
