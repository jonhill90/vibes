#!/usr/bin/env python3
# Source: .claude/commands/generate-prp.md (lines 20-73) + .claude/patterns/security-validation.md
# Pattern: Feature name extraction with 6-level security validation
# Extracted: 2025-10-07
# Relevance: 10/10

"""
PATTERN: Feature Name Extraction with Security Validation
==========================================================

Use Case: Extract and validate feature names from file paths (PRP files)

What to Mimic:
  - 6-level security validation (path traversal, whitelist, length, injection)
  - removeprefix() instead of replace() (only strips leading prefix)
  - Allowed prefix whitelist (security enhancement)
  - Redundant prp_ prefix check (enforces naming convention)
  - Actionable error messages with fix suggestions

What to Adapt:
  - ALLOWED_PREFIXES set (add/remove prefixes for your use case)
  - MAX_LENGTH constant (50 is recommended)
  - validate_no_redundant flag (strict for new PRPs, permissive for existing)

What to Skip:
  - Complex regex patterns (keep simple whitelist)
  - Encoding detection (assume UTF-8)

CRITICAL GOTCHA: removeprefix() vs replace()
  ❌ WRONG: feature.replace("INITIAL_", "")
            This removes ALL occurrences: "INITIAL_INITIAL_test" → "test"
  ✅ RIGHT: feature.removeprefix("INITIAL_")
            This only removes from start: "INITIAL_INITIAL_test" → "INITIAL_test"

  Why it matters: Edge case where feature name legitimately contains prefix
                  (e.g., "INITIAL_initial_user_setup" should become "initial_user_setup")
"""

import re
from typing import Set


# Configuration
ALLOWED_PREFIXES: Set[str] = {"INITIAL_", "EXAMPLE_"}
MAX_LENGTH: int = 50
DANGEROUS_CHARS: list[str] = ['$', '`', ';', '&', '|', '>', '<', '\n', '\r']


def extract_feature_name(
    filepath: str,
    strip_prefix: str | None = None,
    validate_no_redundant: bool = True
) -> str:
    """Extract and validate feature name from PRP file path.

    6-level security validation prevents:
      1. Path traversal attacks
      2. Invalid characters (only alphanumeric + _ -)
      3. Excessive length (DoS via long filenames)
      4. Directory traversal in extracted name
      5. Command injection via shell metacharacters
      6. Redundant prp_ prefix (naming convention enforcement)

    Args:
        filepath: Path to PRP file (e.g., "prps/INITIAL_feature.md")
        strip_prefix: Optional prefix to strip (must be in ALLOWED_PREFIXES)
        validate_no_redundant: If True, reject prp_ prefix (strict for new PRPs)

    Returns:
        Validated feature name (safe for use in file paths and shell commands)

    Raises:
        ValueError: If validation fails, with actionable error message

    Examples:
        >>> extract_feature_name("prps/INITIAL_user_auth.md", strip_prefix="INITIAL_")
        'user_auth'

        >>> extract_feature_name("prps/user_auth.md")
        'user_auth'

        >>> extract_feature_name("prps/prp_feature.md")  # Redundant prefix
        ValueError: ❌ Redundant 'prp_' prefix detected...

        >>> extract_feature_name("../../etc/passwd")  # Path traversal
        ValueError: Path traversal: ../../etc/passwd
    """

    # Level 1: Path traversal in full path
    if ".." in filepath:
        raise ValueError(f"Path traversal detected: {filepath}")

    # Extract basename, remove extension
    basename = filepath.split("/")[-1]
    feature = basename.replace(".md", "")

    # Validate and apply strip_prefix parameter
    if strip_prefix:
        # Security: Validate strip_prefix itself (prevents path traversal via parameter)
        if strip_prefix not in ALLOWED_PREFIXES:
            raise ValueError(
                f"Invalid strip_prefix: '{strip_prefix}'\n"
                f"Allowed prefixes: {', '.join(ALLOWED_PREFIXES)}\n"
                f"Never use 'prp_' as strip_prefix"
            )

        # CRITICAL: Use removeprefix() instead of replace()
        # removeprefix() only removes from start, replace() removes all occurrences
        # See: PEP 616 (https://peps.python.org/pep-0616/)
        feature = feature.removeprefix(strip_prefix)

        # Check for empty result after stripping
        if not feature:
            raise ValueError(
                f"Empty feature name after stripping prefix '{strip_prefix}'\n"
                f"File: {filepath}\n"
                f"Fix: Rename file with actual feature name after prefix"
            )

    # Level 2: Whitelist validation (alphanumeric + underscore + hyphen only)
    if not re.match(r'^[a-zA-Z0-9_-]+$', feature):
        raise ValueError(
            f"Invalid characters in feature name: '{feature}'\n"
            f"Only alphanumeric, underscore (_), and hyphen (-) allowed\n"
            f"Fix: Rename file to use only valid characters"
        )

    # Level 3: Length check (prevent DoS via long filenames)
    if len(feature) > MAX_LENGTH:
        raise ValueError(
            f"Feature name too long: {len(feature)} chars (max: {MAX_LENGTH})\n"
            f"Feature: '{feature}'\n"
            f"Fix: Shorten feature name"
        )

    # Level 4: Directory traversal in extracted name
    if ".." in feature or "/" in feature or "\\" in feature:
        raise ValueError(
            f"Path traversal characters in feature name: '{feature}'\n"
            f"Fix: Remove directory traversal characters"
        )

    # Level 5: Command injection prevention
    if any(c in feature for c in DANGEROUS_CHARS):
        dangerous_found = [c for c in DANGEROUS_CHARS if c in feature]
        raise ValueError(
            f"Dangerous characters in feature name: '{feature}'\n"
            f"Found: {dangerous_found}\n"
            f"Fix: Remove shell metacharacters"
        )

    # Level 6: Redundant prefix validation (naming convention enforcement)
    # This prevents creating new PRPs with prp_ prefix (e.g., prps/prp_feature.md)
    # Fail immediately - no try/except wrapper to ensure violations are caught early
    if validate_no_redundant and feature.startswith("prp_"):
        raise ValueError(
            f"❌ Redundant 'prp_' prefix detected: '{feature}'\n"
            f"\n"
            f"PROBLEM: Files are in prps/ directory - prefix is redundant\n"
            f"EXPECTED: '{feature.removeprefix('prp_')}'\n"
            f"\n"
            f"RESOLUTION:\n"
            f"Rename: prps/{feature}.md → prps/{feature.removeprefix('prp_')}.md\n"
            f"\n"
            f"See: .claude/conventions/prp-naming.md for naming rules"
        )

    return feature


def validate_feature_name_bash_safe(feature: str) -> bool:
    """Additional validation: Check if feature name is safe for bash variables.

    This is used when feature names will be used as bash variable names
    (e.g., in script generation, environment variables).

    Args:
        feature: Feature name to validate

    Returns:
        True if safe for bash, False otherwise

    Examples:
        >>> validate_feature_name_bash_safe("user_auth")
        True

        >>> validate_feature_name_bash_safe("2fast2furious")  # Can't start with digit
        False
    """
    # Bash variable names must:
    # 1. Start with letter or underscore
    # 2. Contain only alphanumeric and underscore
    # Note: Hyphens are NOT allowed in bash variable names
    return bool(re.match(r'^[a-zA-Z_][a-zA-Z0-9_]*$', feature))


# Usage Examples
if __name__ == "__main__":
    print("=== Security Validation Examples ===\n")

    # Example 1: INITIAL.md file (strip prefix)
    try:
        feature = extract_feature_name(
            "prps/INITIAL_user_auth.md",
            strip_prefix="INITIAL_",
            validate_no_redundant=True
        )
        print(f"✅ Example 1: '{feature}' (from INITIAL.md)")
    except ValueError as e:
        print(f"❌ Example 1 failed: {e}")

    # Example 2: Regular PRP file (no prefix)
    try:
        feature = extract_feature_name(
            "prps/user_auth.md",
            validate_no_redundant=True
        )
        print(f"✅ Example 2: '{feature}' (regular PRP)")
    except ValueError as e:
        print(f"❌ Example 2 failed: {e}")

    # Example 3: Path traversal attempt (SHOULD FAIL)
    try:
        feature = extract_feature_name(
            "../../etc/passwd",
            validate_no_redundant=True
        )
        print(f"❌ Example 3: SECURITY BREACH - '{feature}' should have failed!")
    except ValueError as e:
        print(f"✅ Example 3: Blocked path traversal correctly")

    # Example 4: Redundant prp_ prefix (SHOULD FAIL with strict validation)
    try:
        feature = extract_feature_name(
            "prps/prp_context_refactor.md",
            validate_no_redundant=True
        )
        print(f"❌ Example 4: '{feature}' should have failed (redundant prefix)!")
    except ValueError as e:
        print(f"✅ Example 4: Blocked redundant prefix correctly")

    # Example 5: Legacy PRP with prp_ prefix (permissive mode)
    try:
        feature = extract_feature_name(
            "prps/prp_context_refactor.md",
            validate_no_redundant=False  # Permissive for existing PRPs
        )
        print(f"✅ Example 5: '{feature}' (legacy PRP, permissive mode)")
    except ValueError as e:
        print(f"❌ Example 5 failed: {e}")

    # Example 6: Command injection attempt (SHOULD FAIL)
    try:
        feature = extract_feature_name(
            "prps/test;rm -rf /.md",
            validate_no_redundant=True
        )
        print(f"❌ Example 6: SECURITY BREACH - '{feature}' should have failed!")
    except ValueError as e:
        print(f"✅ Example 6: Blocked command injection correctly")

    # Example 7: Bash variable safety check
    print("\n=== Bash Variable Safety ===")
    test_cases = [
        ("user_auth", True),
        ("web-scraper", False),  # Hyphen not allowed
        ("2fast2furious", False),  # Can't start with digit
        ("_internal_feature", True),
    ]
    for name, expected in test_cases:
        result = validate_feature_name_bash_safe(name)
        status = "✅" if result == expected else "❌"
        print(f"{status} '{name}': {'safe' if result else 'unsafe'} for bash")
