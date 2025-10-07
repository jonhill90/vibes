# Source: .claude/patterns/security-validation.md
# Lines: 8-33
# Pattern: 5-level security validation for feature names
# Extracted: 2025-10-07
# Relevance: 10/10 - Core security pattern that MUST be preserved

"""
5-Level Security Validation Pattern

PURPOSE: Prevent path traversal and command injection in feature names.
WHEN TO USE: Before ANY file operations with user-provided paths.
SECURITY LEVEL: HIGH - This is critical security validation.
"""

import re


def extract_feature_name(filepath: str, strip_prefix: str = None) -> str:
    """
    Extract and validate feature name from filepath with 5-level security checks.

    This function is used in BOTH generate-prp and execute-prp to ensure
    that user-provided file paths are safe to use in file operations.

    CRITICAL: All 5 levels MUST be preserved. DO NOT skip any checks.

    Args:
        filepath: User-provided file path (e.g., "prps/INITIAL_feature_name.md")
        strip_prefix: Optional prefix to remove (e.g., "INITIAL_")

    Returns:
        Validated feature name (e.g., "feature_name")

    Raises:
        ValueError: If any security check fails

    Example:
        >>> extract_feature_name("prps/INITIAL_user_auth.md", "INITIAL_")
        'user_auth'

        >>> extract_feature_name("prps/../etc/passwd.md")
        ValueError: Path traversal: prps/../etc/passwd.md
    """

    # LEVEL 1: Path traversal in full path
    # Prevents: "prps/../../../etc/passwd.md"
    if ".." in filepath:
        raise ValueError(f"Path traversal: {filepath}")

    # Extract basename, remove .md extension
    feature = filepath.split("/")[-1].replace(".md", "")

    # Strip optional prefix (e.g., "INITIAL_")
    # NOTE: Current implementation uses replace() which replaces ALL occurrences
    # GOTCHA: If feature name contains prefix multiple times, all are removed
    # SOLUTION: See filename_extraction_logic.py for improved version
    if strip_prefix:
        feature = feature.replace(strip_prefix, "")

    # LEVEL 2: Whitelist validation (alphanumeric + underscore + hyphen only)
    # Prevents: Special characters, spaces, unicode, etc.
    # Allows: user_auth, web-scraper, apiClient123, TEST_Feature-v2
    if not re.match(r'^[a-zA-Z0-9_-]+$', feature):
        raise ValueError(f"Invalid: {feature}")

    # LEVEL 3: Length validation (max 50 characters)
    # Prevents: DoS attacks with extremely long filenames
    # Prevents: Filesystem issues on some operating systems
    if len(feature) > 50:
        raise ValueError(f"Too long: {len(feature)}")

    # LEVEL 4: Directory traversal in feature name (redundant with level 1, but defense in depth)
    # Prevents: "test..test", "test/subdir", "test\subdir"
    if ".." in feature or "/" in feature or "\\" in feature:
        raise ValueError(f"Path traversal: {feature}")

    # LEVEL 5: Command injection prevention
    # Prevents: Shell metacharacters that could execute commands
    # Dangerous chars: $ ` ; & | > < newline carriage-return
    if any(c in feature for c in ['$', '`', ';', '&', '|', '>', '<', '\n', '\r']):
        raise ValueError(f"Dangerous: {feature}")

    return feature


# =============================================================================
# TEST CASES
# =============================================================================

if __name__ == "__main__":
    # PASS cases
    print("PASS Cases:")
    test_pass = [
        ("prps/user_auth.md", None, "user_auth"),
        ("prps/INITIAL_web_scraper.md", "INITIAL_", "web_scraper"),
        ("prps/apiClient123.md", None, "apiClient123"),
        ("prps/TEST_Feature-v2.md", None, "TEST_Feature-v2"),
    ]

    for filepath, prefix, expected in test_pass:
        try:
            result = extract_feature_name(filepath, prefix)
            assert result == expected, f"Expected {expected}, got {result}"
            print(f"  ✅ {filepath} → {result}")
        except Exception as e:
            print(f"  ❌ {filepath} FAILED: {e}")

    # FAIL cases
    print("\nFAIL Cases (should raise ValueError):")
    test_fail = [
        ("prps/../../etc/passwd.md", None, "Path traversal"),
        ("prps/test; rm -rf /.md", None, "Command injection"),
        ("prps/test$(whoami).md", None, "Command injection"),
        ("prps/test`id`.md", None, "Command injection"),
        ("prps/test space.md", None, "Invalid characters"),
        ("prps/" + "a" * 60 + ".md", None, "Too long"),
    ]

    for filepath, prefix, reason in test_fail:
        try:
            result = extract_feature_name(filepath, prefix)
            print(f"  ❌ {filepath} SHOULD HAVE FAILED ({reason})")
        except ValueError as e:
            print(f"  ✅ {filepath} → Correctly rejected ({reason})")
