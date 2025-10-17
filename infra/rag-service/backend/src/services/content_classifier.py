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
    def detect_content_type(text: str) -> CollectionType:
        """Detect if chunk is code, document, or media based on content.

        This is the primary classification method that routes text chunks
        to appropriate embedding collections. The algorithm prioritizes
        specificity: media indicators are checked first (most specific),
        then code patterns, then defaults to documents.

        Args:
            text: Text content to classify (typically a chunk from ingestion)

        Returns:
            CollectionType: "code", "media", or "documents"

        Examples:
            >>> ContentClassifier.detect_content_type("def foo(): pass")
            "code"

            >>> ContentClassifier.detect_content_type("![image](test.png)")
            "media"

            >>> ContentClassifier.detect_content_type("This is a blog post.")
            "documents"

        Note:
            - Media detection has highest priority (most specific)
            - Code detection uses CODE_DETECTION_THRESHOLD from settings (default 0.4)
            - When in doubt, defaults to "documents" collection
        """
        # Check for media (highest priority - most specific)
        # These are explicit visual content indicators
        media_indicators = [
            "![" in text,           # Markdown image syntax: ![alt](url)
            "<img" in text,         # HTML image tag
            "data:image/" in text,  # Base64-encoded images
            "<svg" in text,         # SVG vector graphics
        ]

        if any(media_indicators):
            return "media"

        # Check for code patterns
        # We use multiple indicators to avoid false positives on technical docs
        code_indicators = [
            text.strip().startswith("```"),                     # Code fence start
            text.strip().startswith("    "),                   # Indented code block (4+ spaces)
            bool(re.search(r'\bdef\s+\w+\s*\(', text)),        # Python function definition
            bool(re.search(r'\bfunction\s+\w+\s*\(', text)),   # JavaScript function
            bool(re.search(r'\bclass\s+\w+', text)),           # Class definition (Python/JS/Java)
            "import " in text or "from " in text,              # Python imports
            "{" in text and "}" in text and ";" in text,       # C-style syntax (JS/Java/C++)
            bool(re.search(r'\bconst\s+\w+\s*=', text)),       # Modern JavaScript const
            bool(re.search(r'\blet\s+\w+\s*=', text)),         # Modern JavaScript let
            bool(re.search(r'\basync\s+\w+\s*\(', text)),      # Async function
            bool(re.search(r'=>', text)),                       # Arrow function (JS/TS)
        ]

        # Calculate code density
        code_indicator_count = sum(code_indicators)
        total_lines = max(text.count("\n") + 1, 1)  # +1 for single-line text

        # Absolute minimum: if 3+ code indicators present, classify as code
        # This catches obvious code blocks regardless of length
        if code_indicator_count >= 3:
            return "code"

        # Check code fence density for markdown documents with code examples
        # Count pairs of code fences (opening and closing)
        code_fence_count = text.count("```") // 2
        if code_fence_count > 0 and (code_fence_count / total_lines) > settings.CODE_DETECTION_THRESHOLD:
            return "code"

        # Check for code-heavy content based on threshold
        # This catches files with high code indicator density
        threshold = settings.CODE_DETECTION_THRESHOLD
        if total_lines > 0 and (code_indicator_count / total_lines) > threshold:
            return "code"

        # Default to documents for general text
        # This includes: articles, documentation, blog posts, plain text, etc.
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
