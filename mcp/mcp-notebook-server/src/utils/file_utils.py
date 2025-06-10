"""
INMPARA Notebook Server - File Utilities
Handles file system operations for the INMPARA vault.
"""

import os
import shutil
import hashlib
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime
import frontmatter
import logging

logger = logging.getLogger(__name__)


class INMPARAFileManager:
    """Manages file operations for the INMPARA vault."""
    
    def __init__(self, vault_path: str):
        self.vault_path = Path(vault_path)
        self.folder_structure = {
            'inbox': '0 - Inbox',
            'notes': '1 - Notes',
            'mocs': '2 - MOCs',
            'projects': '3 - Projects',
            'areas': '4 - Areas',
            'resources': '5 - Resources',
            'archive': '6 - Archive',
            'meta': '99 - Meta'
        }
        
        # Ensure vault structure exists
        self._ensure_vault_structure()
    
    def _ensure_vault_structure(self):
        """Ensure all INMPARA folders exist."""
        for folder_key, folder_name in self.folder_structure.items():
            folder_path = self.vault_path / folder_name
            folder_path.mkdir(parents=True, exist_ok=True)
        
        logger.info(f"Vault structure verified at {self.vault_path}")
    
    def get_inbox_files(self) -> List[Dict[str, Any]]:
        """Get all files in the inbox folder."""
        inbox_path = self.vault_path / self.folder_structure['inbox']
        files = []
        
        for file_path in inbox_path.glob("*.md"):
            if file_path.name.startswith('README'):
                continue  # Skip README files
            
            file_info = self._get_file_info(file_path)
            files.append(file_info)
        
        # Sort by creation time (newest first)
        files.sort(key=lambda x: x['created_time'], reverse=True)
        return files
    
    def _get_file_info(self, file_path: Path) -> Dict[str, Any]:
        """Get comprehensive information about a file."""
        stat = file_path.stat()
        
        # Read content
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
        except Exception as e:
            logger.error(f"Error reading file {file_path}: {e}")
            content = ""
        
        # Parse frontmatter if present
        frontmatter_data = {}
        content_body = content
        
        if content.startswith('---'):
            try:
                post = frontmatter.loads(content)
                frontmatter_data = post.metadata
                content_body = post.content
            except Exception as e:
                logger.warning(f"Error parsing frontmatter in {file_path}: {e}")
        
        # Calculate content hash
        content_hash = hashlib.md5(content.encode('utf-8')).hexdigest()
        
        return {
            'file_path': str(file_path.relative_to(self.vault_path)),
            'absolute_path': str(file_path),
            'name': file_path.name,
            'title': frontmatter_data.get('title', file_path.stem),
            'size': stat.st_size,
            'created_time': datetime.fromtimestamp(stat.st_ctime),
            'modified_time': datetime.fromtimestamp(stat.st_mtime),
            'content': content,
            'content_body': content_body,
            'frontmatter': frontmatter_data,
            'word_count': len(content_body.split()),
            'character_count': len(content_body),
            'content_hash': content_hash,
            'has_frontmatter': bool(frontmatter_data)
        }
    
    def move_file(self, source_path: str, destination_folder: str, 
                 new_filename: str = None) -> Tuple[bool, str, str]:
        """Move a file to a different INMPARA folder."""
        try:
            source = Path(source_path)
            if not source.is_absolute():
                source = self.vault_path / source_path
            
            # Determine destination folder path
            if destination_folder in self.folder_structure:
                dest_folder = self.vault_path / self.folder_structure[destination_folder]
            else:
                dest_folder = self.vault_path / destination_folder
            
            dest_folder.mkdir(parents=True, exist_ok=True)
            
            # Determine filename
            filename = new_filename if new_filename else source.name
            destination = dest_folder / filename
            
            # Handle naming conflicts
            counter = 1
            original_destination = destination
            while destination.exists():
                stem = original_destination.stem
                suffix = original_destination.suffix
                destination = dest_folder / f"{stem}_{counter}{suffix}"
                counter += 1
            
            # Move the file
            shutil.move(str(source), str(destination))
            
            relative_dest = str(destination.relative_to(self.vault_path))
            logger.info(f"Moved file from {source_path} to {relative_dest}")
            
            return True, relative_dest, "File moved successfully"
            
        except Exception as e:
            error_msg = f"Error moving file: {e}"
            logger.error(error_msg)
            return False, "", error_msg
    
    def create_file(self, content: str, destination_folder: str, 
                   filename: str) -> Tuple[bool, str, str]:
        """Create a new file in the specified folder."""
        try:
            # Determine destination folder path
            if destination_folder in self.folder_structure:
                dest_folder = self.vault_path / self.folder_structure[destination_folder]
            else:
                dest_folder = self.vault_path / destination_folder
            
            dest_folder.mkdir(parents=True, exist_ok=True)
            
            # Ensure filename has .md extension
            if not filename.endswith('.md'):
                filename += '.md'
            
            file_path = dest_folder / filename
            
            # Handle naming conflicts
            counter = 1
            original_path = file_path
            while file_path.exists():
                stem = original_path.stem
                suffix = original_path.suffix
                file_path = dest_folder / f"{stem}_{counter}{suffix}"
                counter += 1
            
            # Write the file
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            
            relative_path = str(file_path.relative_to(self.vault_path))
            logger.info(f"Created file: {relative_path}")
            
            return True, relative_path, "File created successfully"
            
        except Exception as e:
            error_msg = f"Error creating file: {e}"
            logger.error(error_msg)
            return False, "", error_msg
    
    def update_file(self, file_path: str, content: str) -> Tuple[bool, str]:
        """Update an existing file with new content."""
        try:
            file_path = Path(file_path)
            if not file_path.is_absolute():
                file_path = self.vault_path / file_path
            
            # Create backup
            backup_path = file_path.with_suffix(f'.bak.{datetime.now().strftime("%Y%m%d_%H%M%S")}')
            shutil.copy2(file_path, backup_path)
            
            # Update the file
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            
            logger.info(f"Updated file: {file_path}")
            return True, "File updated successfully"
            
        except Exception as e:
            error_msg = f"Error updating file: {e}"
            logger.error(error_msg)
            return False, error_msg
    
    def delete_file(self, file_path: str, create_backup: bool = True) -> Tuple[bool, str]:
        """Delete a file, optionally creating a backup."""
        try:
            file_path = Path(file_path)
            if not file_path.is_absolute():
                file_path = self.vault_path / file_path
            
            if create_backup:
                # Move to archive instead of deleting
                archive_folder = self.vault_path / self.folder_structure['archive']
                archive_folder.mkdir(parents=True, exist_ok=True)
                
                backup_name = f"deleted_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{file_path.name}"
                backup_path = archive_folder / backup_name
                
                shutil.move(str(file_path), str(backup_path))
                logger.info(f"Archived file to: {backup_path}")
                return True, f"File archived to {backup_path.relative_to(self.vault_path)}"
            else:
                file_path.unlink()
                logger.info(f"Deleted file: {file_path}")
                return True, "File deleted successfully"
            
        except Exception as e:
            error_msg = f"Error deleting file: {e}"
            logger.error(error_msg)
            return False, error_msg
    
    def search_files(self, query: str, folders: List[str] = None, 
                    include_content: bool = True) -> List[Dict[str, Any]]:
        """Search for files matching the query."""
        results = []
        
        # Determine folders to search
        search_folders = []
        if folders:
            for folder in folders:
                if folder in self.folder_structure:
                    search_folders.append(self.vault_path / self.folder_structure[folder])
                else:
                    search_folders.append(self.vault_path / folder)
        else:
            # Search all folders except meta
            for key, folder_name in self.folder_structure.items():
                if key != 'meta':
                    search_folders.append(self.vault_path / folder_name)
        
        query_lower = query.lower()
        
        for folder_path in search_folders:
            if not folder_path.exists():
                continue
            
            for file_path in folder_path.glob("*.md"):
                if file_path.name.startswith('README'):
                    continue
                
                file_info = self._get_file_info(file_path)
                
                # Check if file matches query
                matches = []
                
                # Check title/filename
                if query_lower in file_info['title'].lower():
                    matches.append(('title', file_info['title']))
                
                # Check frontmatter tags
                if 'tags' in file_info['frontmatter']:
                    tags = file_info['frontmatter']['tags']
                    if isinstance(tags, list):
                        for tag in tags:
                            if query_lower in str(tag).lower():
                                matches.append(('tag', str(tag)))
                
                # Check content if requested
                if include_content and query_lower in file_info['content_body'].lower():
                    # Find snippet around match
                    content_lower = file_info['content_body'].lower()
                    match_pos = content_lower.find(query_lower)
                    start = max(0, match_pos - 50)
                    end = min(len(file_info['content_body']), match_pos + len(query) + 50)
                    snippet = file_info['content_body'][start:end].strip()
                    matches.append(('content', snippet))
                
                if matches:
                    file_info['matches'] = matches
                    file_info['match_count'] = len(matches)
                    results.append(file_info)
        
        # Sort by relevance (match count and recency)
        results.sort(key=lambda x: (x['match_count'], x['modified_time']), reverse=True)
        return results
    
    def get_vault_statistics(self) -> Dict[str, Any]:
        """Get statistics about the vault."""
        stats = {
            'total_files': 0,
            'total_size': 0,
            'by_folder': {},
            'by_type': {},
            'recent_files': [],
            'word_count': 0
        }
        
        for folder_key, folder_name in self.folder_structure.items():
            folder_path = self.vault_path / folder_name
            if not folder_path.exists():
                continue
            
            folder_stats = {
                'files': 0,
                'size': 0,
                'word_count': 0
            }
            
            for file_path in folder_path.glob("*.md"):
                if file_path.name.startswith('README'):
                    continue
                
                file_info = self._get_file_info(file_path)
                
                folder_stats['files'] += 1
                folder_stats['size'] += file_info['size']
                folder_stats['word_count'] += file_info['word_count']
                
                stats['total_files'] += 1
                stats['total_size'] += file_info['size']
                stats['word_count'] += file_info['word_count']
                
                # Track content types
                content_type = file_info['frontmatter'].get('type', 'unknown')
                if content_type not in stats['by_type']:
                    stats['by_type'][content_type] = 0
                stats['by_type'][content_type] += 1
                
                # Track recent files
                if len(stats['recent_files']) < 10:
                    stats['recent_files'].append({
                        'path': file_info['file_path'],
                        'title': file_info['title'],
                        'modified': file_info['modified_time']
                    })
            
            stats['by_folder'][folder_name] = folder_stats
        
        # Sort recent files by modification time
        stats['recent_files'].sort(key=lambda x: x['modified'], reverse=True)
        
        return stats
    
    def find_broken_links(self) -> List[Dict[str, Any]]:
        """Find broken wiki links in the vault."""
        broken_links = []
        all_files = {}
        
        # First, build a map of all file titles to paths
        for folder_key, folder_name in self.folder_structure.items():
            folder_path = self.vault_path / folder_name
            if not folder_path.exists():
                continue
            
            for file_path in folder_path.glob("*.md"):
                if file_path.name.startswith('README'):
                    continue
                
                file_info = self._get_file_info(file_path)
                title = file_info['title']
                all_files[title] = file_info['file_path']
        
        # Then, check all links in all files
        import re
        
        for folder_key, folder_name in self.folder_structure.items():
            folder_path = self.vault_path / folder_name
            if not folder_path.exists():
                continue
            
            for file_path in folder_path.glob("*.md"):
                if file_path.name.startswith('README'):
                    continue
                
                file_info = self._get_file_info(file_path)
                
                # Find all wiki links
                wiki_links = re.findall(r'\[\[([^\]]+)\]\]', file_info['content'])
                
                for link in wiki_links:
                    link = link.strip()
                    if link not in all_files:
                        broken_links.append({
                            'source_file': file_info['file_path'],
                            'source_title': file_info['title'],
                            'broken_link': link,
                            'link_text': f"[[{link}]]"
                        })
        
        return broken_links
    
    def cleanup_vault(self) -> Dict[str, Any]:
        """Perform vault cleanup operations."""
        cleanup_results = {
            'duplicates_found': 0,
            'empty_files_found': 0,
            'backups_cleaned': 0,
            'errors': []
        }
        
        # Find duplicate files (by content hash)
        content_hashes = {}
        
        for folder_key, folder_name in self.folder_structure.items():
            folder_path = self.vault_path / folder_name
            if not folder_path.exists():
                continue
            
            for file_path in folder_path.glob("*.md"):
                if file_path.name.startswith('README'):
                    continue
                
                try:
                    file_info = self._get_file_info(file_path)
                    content_hash = file_info['content_hash']
                    
                    if content_hash in content_hashes:
                        # Duplicate found
                        cleanup_results['duplicates_found'] += 1
                        logger.warning(f"Duplicate content found: {file_path} matches {content_hashes[content_hash]}")
                    else:
                        content_hashes[content_hash] = file_path
                    
                    # Check for empty files
                    if file_info['word_count'] < 5:
                        cleanup_results['empty_files_found'] += 1
                        logger.warning(f"Empty or very short file: {file_path}")
                    
                except Exception as e:
                    cleanup_results['errors'].append(f"Error processing {file_path}: {e}")
        
        # Clean up backup files older than 30 days
        cutoff_date = datetime.now().timestamp() - (30 * 24 * 60 * 60)  # 30 days
        
        for folder_key, folder_name in self.folder_structure.items():
            folder_path = self.vault_path / folder_name
            if not folder_path.exists():
                continue
            
            for backup_file in folder_path.glob("*.bak.*"):
                try:
                    if backup_file.stat().st_mtime < cutoff_date:
                        backup_file.unlink()
                        cleanup_results['backups_cleaned'] += 1
                except Exception as e:
                    cleanup_results['errors'].append(f"Error cleaning backup {backup_file}: {e}")
        
        return cleanup_results
