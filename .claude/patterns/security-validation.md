# Security Validation Pattern

**Purpose**: Input validation - prevents path traversal, command injection
**Security Level**: HIGH

## Feature Name Extraction

```python
import re

def extract_feature_name(filepath: str, strip_prefix: str = None) -> str:
    """5-level security validation for feature names from file paths."""
    # 1. Path traversal in full path
    if ".." in filepath: raise ValueError(f"Path traversal: {filepath}")

    # Extract basename, remove extension
    feature = filepath.split("/")[-1].replace(".md", "")
    if strip_prefix: feature = feature.replace(strip_prefix, "")

    # 2. Whitelist (alphanumeric + _ - only)
    if not re.match(r'^[a-zA-Z0-9_-]+$', feature): raise ValueError(f"Invalid: {feature}")

    # 3. Length (max 50 chars)
    if len(feature) > 50: raise ValueError(f"Too long: {len(feature)}")

    # 4. Directory traversal
    if ".." in feature or "/" in feature or "\\" in feature: raise ValueError(f"Path traversal: {feature}")

    # 5. Command injection
    if any(c in feature for c in ['$','`',';','&','|','>','<','\n','\r']): raise ValueError(f"Dangerous: {feature}")

    return feature
```

## Usage

```python
# generate-prp: feature_name = extract_feature_name(initial_md_path, strip_prefix="INITIAL_")
# execute-prp: feature_name = extract_feature_name(prp_path)
```

## Test Cases

```python
# Fail: ["../../etc/passwd", "test; rm -rf /", "test$(whoami)", "test`id`"]
# Pass: ["user_auth", "web-scraper", "apiClient123", "TEST_Feature-v2"]
```
