# Source: .claude/commands/execute-prp.md + feature-analysis.md gotchas
# Lines: execute-prp.md:18-27, feature-analysis.md:354-356
# Pattern: Feature name extraction with improved strip_prefix logic
# Extracted: 2025-10-07
# Relevance: 10/10 - Shows both current implementation and improved version

"""
Filename Extraction with Strip Prefix

PURPOSE: Extract feature name from PRP filepath, optionally stripping workflow prefix.
KEY INSIGHT: Current implementation has a gotcha with replace() - it replaces ALL occurrences.
IMPROVEMENT: Use removeprefix() (Python 3.9+) or check startswith() for safer stripping.
"""

import re


# =============================================================================
# CURRENT IMPLEMENTATION (used in execute-prp.md and generate-prp.md)
# =============================================================================

def extract_feature_name_current(filepath: str, strip_prefix: str = None) -> str:
    """
    Current implementation of feature name extraction.

    GOTCHA: Uses replace() which replaces ALL occurrences of prefix.

    Example gotcha:
        >>> extract_feature_name_current("prps/INITIAL_INITIAL_test.md", "INITIAL_")
        'test'  # Both INITIAL_ prefixes removed!

    This is usually fine but can cause issues if feature name coincidentally
    contains the prefix string.
    """
    if ".." in filepath:
        raise ValueError(f"Path traversal: {filepath}")

    feature = filepath.split("/")[-1].replace(".md", "")

    # GOTCHA: replace() replaces ALL occurrences, not just prefix
    # FIXED: Use removeprefix() instead - only removes leading prefix
    if strip_prefix:
        feature = feature.removeprefix(strip_prefix)

    if not re.match(r'^[a-zA-Z0-9_-]+$', feature):
        raise ValueError(f"Invalid: {feature}")

    if len(feature) > 50:
        raise ValueError(f"Too long: {len(feature)}")

    if any(c in feature for c in ['$', '`', ';', '&', '|', '>', '<', '\n', '\r']):
        raise ValueError(f"Dangerous: {feature}")

    return feature


# =============================================================================
# IMPROVED IMPLEMENTATION (recommended for new code)
# =============================================================================

def extract_feature_name_improved(filepath: str, strip_prefix: str = None) -> str:
    """
    Improved implementation using removeprefix() (Python 3.9+).

    IMPROVEMENT: Only removes prefix from START of string, not all occurrences.

    Example:
        >>> extract_feature_name_improved("prps/INITIAL_INITIAL_test.md", "INITIAL_")
        'INITIAL_test'  # Only first INITIAL_ removed

    This is more predictable and safer for edge cases.
    """
    if ".." in filepath:
        raise ValueError(f"Path traversal: {filepath}")

    feature = filepath.split("/")[-1].replace(".md", "")

    # IMPROVED: removeprefix() only removes from start (Python 3.9+)
    if strip_prefix:
        feature = feature.removeprefix(strip_prefix)

    if not re.match(r'^[a-zA-Z0-9_-]+$', feature):
        raise ValueError(f"Invalid: {feature}")

    if len(feature) > 50:
        raise ValueError(f"Too long: {len(feature)}")

    if any(c in feature for c in ['$', '`', ';', '&', '|', '>', '<', '\n', '\r']):
        raise ValueError(f"Dangerous: {feature}")

    return feature


# =============================================================================
# ALTERNATIVE: Explicit startswith() check (Python 3.8 compatible)
# =============================================================================

def extract_feature_name_explicit(filepath: str, strip_prefix: str = None) -> str:
    """
    Alternative implementation using explicit startswith() check.

    ADVANTAGE: Works on Python 3.8 (removeprefix() requires 3.9+)
    ADVANTAGE: More explicit about what's happening

    Example:
        >>> extract_feature_name_explicit("prps/INITIAL_user_auth.md", "INITIAL_")
        'user_auth'

        >>> extract_feature_name_explicit("prps/user_auth.md", "INITIAL_")
        'user_auth'  # No prefix to remove, returns as-is
    """
    if ".." in filepath:
        raise ValueError(f"Path traversal: {filepath}")

    feature = filepath.split("/")[-1].replace(".md", "")

    # EXPLICIT: Check if starts with prefix before removing
    if strip_prefix and feature.startswith(strip_prefix):
        feature = feature[len(strip_prefix):]

    if not re.match(r'^[a-zA-Z0-9_-]+$', feature):
        raise ValueError(f"Invalid: {feature}")

    if len(feature) > 50:
        raise ValueError(f"Too long: {len(feature)}")

    if any(c in feature for c in ['$', '`', ';', '&', '|', '>', '<', '\n', '\r']):
        raise ValueError(f"Dangerous: {feature}")

    return feature


# =============================================================================
# AUTO-DETECTION LOGIC (recommended for execute-prp.md)
# =============================================================================

def extract_feature_name_auto_detect(filepath: str) -> str:
    """
    Auto-detect INITIAL_ prefix and strip it automatically.

    DEVELOPER EXPERIENCE IMPROVEMENT: No need to remember strip_prefix parameter.

    This is the recommended approach for execute-prp.md Phase 0.

    Example:
        >>> extract_feature_name_auto_detect("prps/INITIAL_user_auth.md")
        'user_auth'  # INITIAL_ detected and stripped

        >>> extract_feature_name_auto_detect("prps/user_auth.md")
        'user_auth'  # No prefix, returns as-is
    """
    if ".." in filepath:
        raise ValueError(f"Path traversal: {filepath}")

    feature = filepath.split("/")[-1].replace(".md", "")

    # AUTO-DETECT: Check for INITIAL_ prefix and strip if present
    if feature.startswith("INITIAL_"):
        feature = feature.removeprefix("INITIAL_")  # Python 3.9+
        # Or for Python 3.8: feature = feature[8:]  # len("INITIAL_") = 8

    if not re.match(r'^[a-zA-Z0-9_-]+$', feature):
        raise ValueError(f"Invalid: {feature}")

    if len(feature) > 50:
        raise ValueError(f"Too long: {len(feature)}")

    if any(c in feature for c in ['$', '`', ';', '&', '|', '>', '<', '\n', '\r']):
        raise ValueError(f"Dangerous: {feature}")

    return feature


# =============================================================================
# VALIDATION FOR REDUNDANT PREFIX (new requirement)
# =============================================================================

def extract_feature_name_with_redundant_check(
    filepath: str,
    strip_prefix: str = None,
    validate_no_redundant: bool = True
) -> str:
    """
    Extract feature name with validation for redundant 'prp_' prefix.

    NEW REQUIREMENT: Detect and reject redundant 'prp_' prefix in feature names.

    Args:
        filepath: PRP file path
        strip_prefix: Workflow prefix to strip (e.g., "INITIAL_")
        validate_no_redundant: If True, raise error on 'prp_' prefix

    Example:
        >>> extract_feature_name_with_redundant_check("prps/prp_bad_name.md")
        ValueError: Redundant 'prp_' prefix detected in feature name: prp_bad_name

        >>> extract_feature_name_with_redundant_check("prps/INITIAL_user_auth.md", "INITIAL_")
        'user_auth'
    """
    if ".." in filepath:
        raise ValueError(f"Path traversal: {filepath}")

    feature = filepath.split("/")[-1].replace(".md", "")

    # Strip workflow prefix FIRST (INITIAL_)
    if strip_prefix and feature.startswith(strip_prefix):
        feature = feature[len(strip_prefix):]

    # NEW: Validate no redundant 'prp_' prefix
    if validate_no_redundant and feature.startswith("prp_"):
        raise ValueError(
            f"Redundant 'prp_' prefix detected in feature name: {feature}\n\n"
            f"EXPECTED: Feature names should NOT start with 'prp_' (redundant with 'prps/' directory)\n"
            f"WRONG: prps/prp_context_refactor.md\n"
            f"RIGHT: prps/context_refactor.md\n\n"
            f"See .claude/conventions/prp-naming.md for naming conventions."
        )

    if not re.match(r'^[a-zA-Z0-9_-]+$', feature):
        raise ValueError(f"Invalid: {feature}")

    if len(feature) > 50:
        raise ValueError(f"Too long: {len(feature)}")

    if any(c in feature for c in ['$', '`', ';', '&', '|', '>', '<', '\n', '\r']):
        raise ValueError(f"Dangerous: {feature}")

    return feature


# =============================================================================
# TEST CASES
# =============================================================================

if __name__ == "__main__":
    print("=== TEST: Current vs Improved Implementation ===\n")

    # Edge case: prefix appears multiple times
    test_path = "prps/INITIAL_INITIAL_test.md"
    print(f"Input: {test_path}")
    print(f"Current (replace):   '{extract_feature_name_current(test_path, 'INITIAL_')}'")
    print(f"Improved (removeprefix): '{extract_feature_name_improved(test_path, 'INITIAL_')}'")
    print(f"Explicit (startswith): '{extract_feature_name_explicit(test_path, 'INITIAL_')}'")
    print()

    print("=== TEST: Auto-detection ===\n")
    test_cases = [
        "prps/INITIAL_user_auth.md",
        "prps/user_auth.md",
    ]
    for test in test_cases:
        result = extract_feature_name_auto_detect(test)
        print(f"{test} → {result}")
    print()

    print("=== TEST: Redundant prefix validation ===\n")
    test_redundant = [
        ("prps/prp_bad_name.md", True),  # Should fail
        ("prps/context_refactor.md", False),  # Should pass
        ("prps/INITIAL_user_auth.md", False),  # Should pass (INITIAL_ is workflow prefix)
    ]

    for filepath, should_fail in test_redundant:
        try:
            # Auto-detect INITIAL_ for stripping
            strip = "INITIAL_" if "INITIAL_" in filepath else None
            result = extract_feature_name_with_redundant_check(filepath, strip)
            if should_fail:
                print(f"❌ {filepath} → SHOULD HAVE FAILED")
            else:
                print(f"✅ {filepath} → {result}")
        except ValueError as e:
            if should_fail:
                print(f"✅ {filepath} → Correctly rejected (redundant prp_)")
            else:
                print(f"❌ {filepath} → SHOULD HAVE PASSED: {e}")
