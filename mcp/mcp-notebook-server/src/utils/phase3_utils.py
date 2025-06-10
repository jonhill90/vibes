"""
Phase 3 Utilities
Helper utilities for Phase 3 operations
"""

import re
from typing import Dict, Tuple, Any

class FileUtils:
    """Utility class for file operations used in Phase 3"""
    
    @staticmethod
    def extract_frontmatter(content: str) -> Tuple[Dict[str, Any], str]:
        """Extract YAML frontmatter from markdown content"""
        try:
            if not content.startswith('---'):
                return {}, content
            
            # Find the closing ---
            parts = content.split('---', 2)
            if len(parts) < 3:
                return {}, content
            
            frontmatter_text = parts[1].strip()
            main_content = parts[2].strip()
            
            # Simple YAML parsing (basic implementation)
            frontmatter = {}
            current_key = None
            
            for line in frontmatter_text.split('\n'):
                line = line.strip()
                if not line:
                    continue
                
                if line.startswith('- '):
                    # List item
                    if current_key and isinstance(frontmatter.get(current_key), list):
                        frontmatter[current_key].append(line[2:].strip())
                elif ':' in line:
                    # Key-value pair
                    key, value = line.split(':', 1)
                    key = key.strip()
                    value = value.strip()
                    
                    if not value:
                        # This might be a list
                        frontmatter[key] = []
                        current_key = key
                    else:
                        frontmatter[key] = value
                        current_key = None
            
            return frontmatter, main_content
            
        except Exception:
            return {}, content
    
    @staticmethod
    def create_frontmatter_text(frontmatter: Dict[str, Any]) -> str:
        """Create YAML frontmatter text from dictionary"""
        lines = ['---']
        
        for key, value in frontmatter.items():
            if isinstance(value, list):
                lines.append(f'{key}:')
                for item in value:
                    lines.append(f'  - {item}')
            else:
                lines.append(f'{key}: {value}')
        
        lines.append('---')
        return '\n'.join(lines)

