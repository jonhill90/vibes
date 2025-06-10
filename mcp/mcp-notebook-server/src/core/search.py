"""
INMPARA Search Module

This module handles all search operations including semantic search, exact search,
connection suggestions, and content discovery across the vault.

Target: ~400 lines - Complete search functionality
"""

import os
import re
import json
import logging
from typing import Dict, List, Any, Optional, Tuple
from pathlib import Path

logger = logging.getLogger(__name__)


class SearchManager:
    """
    Manages all search operations for the INMPARA vault.
    
    Handles semantic search via vector embeddings, exact text search,
    connection suggestions, and intelligent content discovery.
    """
    
    def __init__(self, vault_path: str, vector_search_engine=None, database=None):
        """Initialize the SearchManager with required components."""
        self.vault_path = vault_path
        self.vector_search = vector_search_engine
        self.database = database
        
        # Search configuration
        self.default_limit = 10
        self.min_score_threshold = 0.5
        self.connection_threshold = 0.7
        
        logger.info(f"SearchManager initialized for vault: {vault_path}")
    
    async def search_semantic(self, query: str, limit: int = None, min_score: float = None,
                            domain_filter: str = None, content_type_filter: str = None) -> Dict[str, Any]:
        """
        Perform semantic search using vector embeddings.
        
        Args:
            query: Search query text
            limit: Maximum number of results
            min_score: Minimum similarity score threshold
            domain_filter: Filter by specific domain
            content_type_filter: Filter by content type
            
        Returns:
            Dict with search results and metadata
        """
        try:
            if not query or not query.strip():
                return {'success': False, 'error': 'Query cannot be empty'}
            
            limit = limit or self.default_limit
            min_score = min_score or self.min_score_threshold
            
            if not self.vector_search:
                return {'success': False, 'error': 'Vector search engine not available'}
            
            # Perform vector search
            results = await self.vector_search.search_similar(
                query=query,
                limit=limit * 2,  # Get more results for filtering
                score_threshold=min_score
            )
            
            # Filter results by domain/type if specified
            filtered_results = self._filter_search_results(
                results, domain_filter, content_type_filter
            )
            
            # Limit final results
            final_results = filtered_results[:limit]
            
            # Enhance results with additional metadata
            enhanced_results = await self._enhance_search_results(final_results)
            
            return {
                'success': True,
                'query': query,
                'results': enhanced_results,
                'count': len(enhanced_results),
                'total_found': len(filtered_results),
                'search_type': 'semantic'
            }
            
        except Exception as e:
            logger.error(f"Error in semantic search: {e}")
            return {'success': False, 'error': str(e)}
    
    def search_exact(self, query: str, case_sensitive: bool = False,
                    whole_words: bool = False, file_extension: str = '.md') -> Dict[str, Any]:
        """
        Perform exact text search across vault files.
        
        Args:
            query: Search query text
            case_sensitive: Whether search should be case sensitive
            whole_words: Whether to match whole words only
            file_extension: File extension to search in
            
        Returns:
            Dict with search results and metadata
        """
        try:
            if not query or not query.strip():
                return {'success': False, 'error': 'Query cannot be empty'}
            
            results = []
            search_pattern = self._build_search_pattern(query, case_sensitive, whole_words)
            
            # Walk through vault files
            for root, dirs, files in os.walk(self.vault_path):
                # Skip hidden directories and .git
                dirs[:] = [d for d in dirs if not d.startswith('.')]
                
                for file in files:
                    if not file.endswith(file_extension):
                        continue
                        
                    file_path = os.path.join(root, file)
                    matches = self._search_in_file(file_path, search_pattern)
                    
                    if matches:
                        results.append({
                            'file_path': file_path,
                            'file_name': file,
                            'matches': matches,
                            'match_count': len(matches)
                        })
            
            # Sort by relevance (match count)
            results.sort(key=lambda x: x['match_count'], reverse=True)
            
            return {
                'success': True,
                'query': query,
                'results': results,
                'count': len(results),
                'total_matches': sum(r['match_count'] for r in results),
                'search_type': 'exact'
            }
            
        except Exception as e:
            logger.error(f"Error in exact search: {e}")
            return {'success': False, 'error': str(e)}
    
    async def suggest_connections(self, note_path: str, max_suggestions: int = 5) -> Dict[str, Any]:
        """
        Suggest connections between notes based on content similarity.
        
        Args:
            note_path: Path to the note to find connections for
            max_suggestions: Maximum number of suggestions
            
        Returns:
            Dict with connection suggestions
        """
        try:
            if not os.path.exists(note_path):
                return {'success': False, 'error': 'Note file does not exist'}
            
            # Read note content
            with open(note_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Extract main content (skip frontmatter)
            main_content = self._extract_main_content(content)
            
            if not main_content.strip():
                return {'success': False, 'error': 'Note has no content to analyze'}
            
            # Perform semantic search with note content
            search_results = await self.search_semantic(
                query=main_content[:500],  # Use first 500 chars for search
                limit=max_suggestions + 5,  # Get extra to filter out self
                min_score=self.connection_threshold
            )
            
            if not search_results['success']:
                return search_results
            
            # Filter out the source note itself
            base_name = os.path.basename(note_path)
            suggestions = []
            
            for result in search_results['results']:
                result_name = os.path.basename(result.get('file_path', ''))
                if result_name != base_name:
                    # Add connection reason
                    connection_info = self._analyze_connection_reason(
                        main_content, result.get('content', '')
                    )
                    result['connection_reason'] = connection_info
                    suggestions.append(result)
            
            # Limit final suggestions
            final_suggestions = suggestions[:max_suggestions]
            
            return {
                'success': True,
                'source_note': note_path,
                'suggestions': final_suggestions,
                'count': len(final_suggestions)
            }
            
        except Exception as e:
            logger.error(f"Error suggesting connections: {e}")
            return {'success': False, 'error': str(e)}
    
    def search_by_tags(self, tags: List[str], match_all: bool = False) -> Dict[str, Any]:
        """
        Search notes by tags using database queries.
        
        Args:
            tags: List of tags to search for
            match_all: Whether note must have ALL tags (True) or ANY tags (False)
            
        Returns:
            Dict with search results
        """
        try:
            if not tags:
                return {'success': False, 'error': 'No tags provided'}
            
            if not self.database:
                return {'success': False, 'error': 'Database not available'}
            
            # Query database for notes with tags
            results = self.database.search_by_tags(tags, match_all=match_all)
            
            return {
                'success': True,
                'tags': tags,
                'match_all': match_all,
                'results': results,
                'count': len(results),
                'search_type': 'tags'
            }
            
        except Exception as e:
            logger.error(f"Error in tag search: {e}")
            return {'success': False, 'error': str(e)}
    
    def search_by_domain(self, domain: str) -> Dict[str, Any]:
        """
        Search notes by domain using database queries.
        
        Args:
            domain: Domain to search for
            
        Returns:
            Dict with search results
        """
        try:
            if not domain:
                return {'success': False, 'error': 'Domain not provided'}
            
            if not self.database:
                return {'success': False, 'error': 'Database not available'}
            
            # Query database for notes in domain
            results = self.database.search_by_domain(domain)
            
            return {
                'success': True,
                'domain': domain,
                'results': results,
                'count': len(results),
                'search_type': 'domain'
            }
            
        except Exception as e:
            logger.error(f"Error in domain search: {e}")
            return {'success': False, 'error': str(e)}
    
    async def find_similar_notes(self, content: str, limit: int = 5,
                               exclude_paths: List[str] = None) -> Dict[str, Any]:
        """
        Find notes similar to given content.
        
        Args:
            content: Content to find similar notes for
            limit: Maximum number of similar notes
            exclude_paths: Paths to exclude from results
            
        Returns:
            Dict with similar notes
        """
        try:
            if not content or not content.strip():
                return {'success': False, 'error': 'Content cannot be empty'}
            
            exclude_paths = exclude_paths or []
            
            # Perform semantic search
            search_results = await self.search_semantic(
                query=content[:1000],  # Use first 1000 chars
                limit=limit + len(exclude_paths),  # Get extra for exclusions
                min_score=0.6
            )
            
            if not search_results['success']:
                return search_results
            
            # Filter out excluded paths
            filtered_results = []
            for result in search_results['results']:
                if result.get('file_path') not in exclude_paths:
                    filtered_results.append(result)
            
            final_results = filtered_results[:limit]
            
            return {
                'success': True,
                'similar_notes': final_results,
                'count': len(final_results)
            }
            
        except Exception as e:
            logger.error(f"Error finding similar notes: {e}")
            return {'success': False, 'error': str(e)}
    
    def _filter_search_results(self, results: List[Dict], domain_filter: str,
                             content_type_filter: str) -> List[Dict]:
        """Filter search results by domain and content type."""
        if not domain_filter and not content_type_filter:
            return results
        
        filtered = []
        for result in results:
            # Check domain filter
            if domain_filter:
                result_domain = result.get('metadata', {}).get('domain', '').lower()
                if domain_filter.lower() not in result_domain:
                    continue
            
            # Check content type filter
            if content_type_filter:
                result_type = result.get('metadata', {}).get('type', '').lower()
                if content_type_filter.lower() != result_type:
                    continue
            
            filtered.append(result)
        
        return filtered
    
    async def _enhance_search_results(self, results: List[Dict]) -> List[Dict]:
        """Enhance search results with additional metadata."""
        enhanced = []
        
        for result in results:
            enhanced_result = result.copy()
            
            # Add file metadata if available
            file_path = result.get('file_path')
            if file_path and os.path.exists(file_path):
                stat = os.stat(file_path)
                enhanced_result['file_size'] = stat.st_size
                enhanced_result['modified_time'] = stat.st_mtime
            
            # Add snippet if content is available
            content = result.get('content', '')
            if content:
                enhanced_result['snippet'] = self._create_content_snippet(content)
            
            enhanced.append(enhanced_result)
        
        return enhanced
    
    def _build_search_pattern(self, query: str, case_sensitive: bool, whole_words: bool):
        """Build regex pattern for exact search."""
        escaped_query = re.escape(query)
        
        if whole_words:
            pattern = rf'\b{escaped_query}\b'
        else:
            pattern = escaped_query
        
        flags = 0 if case_sensitive else re.IGNORECASE
        return re.compile(pattern, flags)
    
    def _search_in_file(self, file_path: str, pattern) -> List[Dict]:
        """Search for pattern in a specific file."""
        matches = []
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                lines = f.readlines()
            
            for line_num, line in enumerate(lines, 1):
                for match in pattern.finditer(line):
                    matches.append({
                        'line_number': line_num,
                        'line_content': line.strip(),
                        'match_start': match.start(),
                        'match_end': match.end(),
                        'matched_text': match.group()
                    })
        
        except (IOError, UnicodeDecodeError) as e:
            logger.warning(f"Could not search in file {file_path}: {e}")
        
        return matches
    
    def _extract_main_content(self, content: str) -> str:
        """Extract main content, skipping frontmatter."""
        if content.startswith('---'):
            parts = content.split('---', 2)
            if len(parts) >= 3:
                return parts[2].strip()
        return content
    
    def _analyze_connection_reason(self, source_content: str, target_content: str) -> str:
        """Analyze why two pieces of content are connected."""
        # Simple heuristic - find common terms
        source_words = set(re.findall(r'\b\w{4,}\b', source_content.lower()))
        target_words = set(re.findall(r'\b\w{4,}\b', target_content.lower()))
        
        common_words = source_words.intersection(target_words)
        
        if len(common_words) > 5:
            return f"Shares many concepts: {', '.join(list(common_words)[:5])}"
        elif len(common_words) > 2:
            return f"Related topics: {', '.join(list(common_words))}"
        else:
            return "Semantic similarity"
    
    def _create_content_snippet(self, content: str, max_length: int = 200) -> str:
        """Create a snippet from content."""
        main_content = self._extract_main_content(content)
        
        if len(main_content) <= max_length:
            return main_content
        
        # Find a good breaking point near max_length
        snippet = main_content[:max_length]
        last_space = snippet.rfind(' ')
        
        if last_space > max_length * 0.7:  # If we can find a space in the last 30%
            snippet = snippet[:last_space]
        
        return snippet + "..."
