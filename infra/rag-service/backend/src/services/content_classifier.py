"""Content type classification for multi-collection routing.

Pure function-based classifier that detects whether text chunks should be
stored in "code", "documents", or "media" collections based on content patterns.

Pattern: Pure functions, no external dependencies (except settings)
Reference: prps/multi_collection_architecture.md (lines 394-461)
"""

import re
from typing import Literal

from ..config.settings import settings

# Type alias for collection types
CollectionType = Literal["documents", "code", "media"]


class ContentClassifier:
    """Classify text chunks into content types for collection routing.

    Algorithm:
    1. Check for media indicators (images) → "media" (highest priority)
    2. Count code indicators vs total lines → "code" if > threshold
    3. Default to "documents" for general text

    The classifier is intentionally lenient (40% threshold) to avoid
    misclassifying technical documentation as code.
    """

    @staticmethod
    def extract_code_language(text: str) -> str | None:
        """Extract programming language from code fence markers.

        Searches for markdown code fences (```language) and extracts the
        language identifier. Handles various fence formats:
        - ```python → "python"
        - ```javascript → "javascript"
        - ```c++ → "c++"
        - ```objective-c → "objective-c"
        - ```python {highlight} → "python" (ignores attributes)
        - ``` → None (no language specified)

        Args:
            text: Text content to analyze (typically a code chunk)

        Returns:
            str | None: Language identifier if found, None otherwise

        Examples:
            >>> ContentClassifier.extract_code_language("```python\\nprint('hello')")
            "python"

            >>> ContentClassifier.extract_code_language("```c++\\nint main()")
            "c++"

            >>> ContentClassifier.extract_code_language("```\\nsome code")
            None

            >>> ContentClassifier.extract_code_language("def foo(): pass")
            None

        Note:
            - Searches for code fences anywhere in text (not just at start)
            - Returns first language found if multiple fences exist
            - Returns None for unfenced code blocks
            - Language identifiers are lowercased for consistency
            - Pattern matches existing extract_code_blocks.py script (lines 58-61)
        """
        # Match code fence with optional language identifier
        # Pattern: ``` followed by language (alphanumeric + _ + - + +), optional attributes
        # Matches: ```python, ```c++, ```objective-c, ```python {highlight}
        fence_pattern = r'```([a-zA-Z0-9_+-]+)(?:\s+[^\n]*)?'

        # Search for code fence anywhere in text (use re.search, not text.strip())
        # This finds fences embedded in documentation, not just at the start
        match = re.search(fence_pattern, text, re.MULTILINE)

        if match and match.group(1):
            # Found language identifier (e.g., "python" from ```python)
            return match.group(1).lower()

        # No code fence or no language specified
        return None

    @staticmethod
    def detect_content_type(text: str) -> CollectionType:
        """Detect if chunk is code, document, or media based on content.

        CRITICAL RULE: Only classify as "code" if it's an ACTUAL code snippet
        with a code fence AND language tag. Everything else is "documents".

        Args:
            text: Text content to classify (typically a chunk from ingestion)

        Returns:
            CollectionType: "code", "media", or "documents"

        Examples:
            >>> ContentClassifier.detect_content_type("```python\\ndef foo(): pass\\n```")
            "code"

            >>> ContentClassifier.detect_content_type("![image](test.png)")
            "media"

            >>> ContentClassifier.detect_content_type("This is a blog post.")
            "documents"

        Note:
            - Media detection has highest priority
            - Code MUST have code fence with language tag (```python, ```bash, etc.)
            - No language tag = NOT a code snippet = goes to documents
            - API docs, JSON examples without fences = documents
        """
        # Check for media (highest priority - most specific)
        media_indicators = [
            "![" in text,           # Markdown image syntax: ![alt](url)
            "<img" in text,         # HTML image tag
            "data:image/" in text,  # Base64-encoded images
            "<svg" in text,         # SVG vector graphics
        ]

        if any(media_indicators):
            return "media"

        # Check for code snippets (MUST have code fence with language tag)
        # CRITICAL: Only classify as "code" if we can extract a language
        # If there's no language tag, it's not a proper code snippet
        fence_pattern = r'```([a-zA-Z0-9_+-]+)(?:\s+[^\n]*)?'
        if re.search(fence_pattern, text, re.MULTILINE):
            # Found code fence with language tag - this is actual code
            return "code"

        # Everything else is documents
        # This includes: API docs, JSON examples without fences, technical documentation
        return "documents"


# Convenience function for direct import
def classify_content(text: str) -> CollectionType:
    """Convenience wrapper for ContentClassifier.detect_content_type().

    Args:
        text: Text content to classify

    Returns:
        CollectionType: "code", "media", or "documents"

    Example:
        >>> from services.content_classifier import classify_content
        >>> classify_content("def hello(): pass")
        "code"
    """
    return ContentClassifier.detect_content_type(text)
