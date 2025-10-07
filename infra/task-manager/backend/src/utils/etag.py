"""ETag generation utilities for HTTP caching.

This module provides helpers for generating ETags to support
HTTP caching with If-None-Match headers.

PATTERN: Use MD5 hash of JSON-serialized data for consistent ETags
"""

import hashlib
import json
from typing import Any


def generate_etag(data: Any) -> str:
    """Generate an ETag from arbitrary data.

    Uses MD5 hash of JSON-serialized data to create a consistent,
    short identifier for caching purposes.

    Args:
        data: Any JSON-serializable data (dict, list, etc.)

    Returns:
        ETag string (MD5 hash in quotes, e.g., '"abc123..."')

    Example:
        etag = generate_etag({"tasks": [...], "total": 5})
        # Returns: '"d41d8cd98f00b204e9800998ecf8427e"'
    """
    # Serialize to JSON with sorted keys for consistency
    json_str = json.dumps(data, sort_keys=True, default=str)

    # Generate MD5 hash
    hash_obj = hashlib.md5(json_str.encode("utf-8"))
    etag_value = hash_obj.hexdigest()

    # Return ETag wrapped in quotes (HTTP standard)
    return f'"{etag_value}"'
