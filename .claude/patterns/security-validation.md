# Security Validation Pattern

**Purpose**: Input validation - prevents path traversal, command injection
**Security Level**: HIGH

## Feature Name Extraction

```python
import re

def extract_feature_name(filepath: str, strip_prefix: str = None, validate_no_redundant: bool = True) -> str:
    """6-level security validation for feature names from file paths.

    Args:
        filepath: Path to PRP file (e.g., "prps/INITIAL_feature.md")
        strip_prefix: Optional prefix to strip (e.g., "INITIAL_")
        validate_no_redundant: If True, reject prp_ prefix (strict for new PRPs)

    Returns:
        Validated feature name

    Raises:
        ValueError: If validation fails with actionable error message
    """
    # Whitelist of allowed prefixes (security enhancement)
    ALLOWED_PREFIXES = {"INITIAL_", "EXAMPLE_"}

    # 1. Path traversal in full path
    if ".." in filepath: raise ValueError(f"Path traversal: {filepath}")

    # Extract basename, remove extension
    feature = filepath.split("/")[-1].replace(".md", "")

    # Validate strip_prefix parameter itself (prevents path traversal via parameter)
    if strip_prefix:
        if strip_prefix not in ALLOWED_PREFIXES:
            raise ValueError(
                f"Invalid strip_prefix: '{strip_prefix}'\n"
                f"Allowed prefixes: {', '.join(ALLOWED_PREFIXES)}\n"
                f"Never use 'prp_' as strip_prefix"
            )
        # Use removeprefix() instead of replace() - only removes leading prefix, not all occurrences
        feature = feature.removeprefix(strip_prefix)

        # Check for empty result after stripping
        if not feature:
            raise ValueError(
                f"Empty feature name after stripping prefix '{strip_prefix}'\n"
                f"File: {filepath}\n"
                f"Fix: Rename file with actual feature name after prefix"
            )

    # 2. Whitelist (alphanumeric + _ - only)
    if not re.match(r'^[a-zA-Z0-9_-]+$', feature): raise ValueError(f"Invalid: {feature}")

    # 3. Length (max 50 chars)
    if len(feature) > 50: raise ValueError(f"Too long: {len(feature)}")

    # 4. Directory traversal
    if ".." in feature or "/" in feature or "\\" in feature: raise ValueError(f"Path traversal: {feature}")

    # 5. Command injection
    if any(c in feature for c in ['$','`',';','&','|','>','<','\n','\r']): raise ValueError(f"Dangerous: {feature}")

    # 6. Redundant prefix validation
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
```

## Usage

```python
# generate-prp (strict validation for new PRPs):
feature_name = extract_feature_name(initial_md_path, strip_prefix="INITIAL_", validate_no_redundant=True)

# execute-prp (permissive for existing PRPs):
feature_name = extract_feature_name(prp_path, validate_no_redundant=False)
```

## Test Cases

```python
# FAIL cases (should raise ValueError):
# - Path traversal: "../../etc/passwd"
# - Command injection: "test; rm -rf /", "test$(whoami)", "test`id`"
# - Redundant prefix (strict): "prp_context_refactor" (when validate_no_redundant=True)
# - Invalid strip_prefix: extract_feature_name(path, strip_prefix="prp_")
# - Empty after stripping: "INITIAL_.md" with strip_prefix="INITIAL_"

# PASS cases:
# - Valid names: "user_auth", "web-scraper", "apiClient123", "TEST_Feature-v2"
# - Legacy PRP (permissive): "prp_context_refactor" (when validate_no_redundant=False)
# - With prefix: "INITIAL_feature" with strip_prefix="INITIAL_" → "feature"
```
