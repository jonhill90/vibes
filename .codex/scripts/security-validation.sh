#!/bin/bash
# .codex/scripts/security-validation.sh
# Purpose: Security validation for feature names - prevents path traversal and command injection
# Pattern: 6-level validation based on .claude/patterns/security-validation.md
# Source: Adapted from prps/codex_commands/examples/security_validation.py

set -euo pipefail

# =============================================================================
# Configuration
# =============================================================================

# Allowed prefixes for feature names (security whitelist)
# Using space-separated list for Bash 3.x compatibility
ALLOWED_PREFIXES="INITIAL_ EXAMPLE_"

# Maximum feature name length (prevents DoS via long filenames)
MAX_LENGTH=50

# Dangerous characters for command injection detection
DANGEROUS_CHARS='$`;&|><'

# Reserved names (Windows reserved names + Unix special names)
# Using space-separated list for Bash 3.x compatibility
RESERVED_NAMES=". .. CON PRN AUX NUL COM1 COM2 LPT1 LPT2"

# =============================================================================
# Core Validation Functions
# =============================================================================

# Validate feature name with 6-level security checks
validate_feature_name() {
    local feature="$1"
    local validate_no_redundant="${2:-true}"  # Default: strict validation

    # Level 1: Path traversal check (.., /, \)
    if [[ "$feature" == *".."* || "$feature" == *"/"* || "$feature" == *"\\"* ]]; then
        echo "❌ ERROR: Path traversal detected in feature name: '$feature'" >&2
        echo "   Found: Directory traversal characters (.., /, or \\)" >&2
        echo "   Fix: Remove directory traversal characters from feature name" >&2
        return 1
    fi

    # Level 2: Whitelist (alphanumeric + underscore + hyphen only)
    if [[ ! "$feature" =~ ^[a-zA-Z0-9_-]+$ ]]; then
        echo "❌ ERROR: Invalid characters in feature name: '$feature'" >&2
        echo "   Allowed: Letters (a-z, A-Z), digits (0-9), underscore (_), hyphen (-)" >&2
        echo "   Fix: Use only alphanumeric characters, underscores, and hyphens" >&2
        return 1
    fi

    # Level 3: Length check (max 50 chars)
    if [ ${#feature} -gt $MAX_LENGTH ]; then
        echo "❌ ERROR: Feature name too long: ${#feature} chars (max: ${MAX_LENGTH})" >&2
        echo "   Feature: '$feature'" >&2
        echo "   Fix: Shorten feature name to ${MAX_LENGTH} characters or less" >&2
        return 1
    fi

    # Level 4: Dangerous characters ($, `, ;, &, |, etc.)
    local char
    for (( i=0; i<${#DANGEROUS_CHARS}; i++ )); do
        char="${DANGEROUS_CHARS:$i:1}"
        if [[ "$feature" == *"$char"* ]]; then
            echo "❌ ERROR: Dangerous character in feature name: '$feature'" >&2
            echo "   Found: '$char' (shell metacharacter)" >&2
            echo "   Blocked: \$ \` ; & | > <" >&2
            echo "   Fix: Remove shell metacharacters from feature name" >&2
            return 1
        fi
    done

    # Level 5: Redundant prp_ prefix check
    if [[ "$validate_no_redundant" == "true" ]] && [[ "$feature" == prp_* ]]; then
        echo "❌ ERROR: Redundant 'prp_' prefix detected: '$feature'" >&2
        echo "" >&2
        echo "   PROBLEM: Files are in prps/ directory - prefix is redundant" >&2
        echo "   EXPECTED: '${feature#prp_}'" >&2
        echo "" >&2
        echo "   RESOLUTION:" >&2
        echo "   Rename: prps/${feature}.md → prps/${feature#prp_}.md" >&2
        echo "" >&2
        echo "   See: .claude/conventions/prp-naming.md for naming rules" >&2
        return 1
    fi

    # Level 6: Reserved names (., .., CON, NUL, etc.)
    local feature_upper
    feature_upper=$(echo "$feature" | tr '[:lower:]' '[:upper:]')  # Convert to uppercase
    local reserved
    for reserved in $RESERVED_NAMES; do
        if [[ "$feature_upper" == "$reserved" ]]; then
            echo "❌ ERROR: Reserved name detected: '$feature'" >&2
            echo "   This name is reserved and cannot be used" >&2
            echo "   Fix: Choose a different feature name" >&2
            return 1
        fi
    done

    return 0
}

# Extract feature name from file path with security validation
extract_feature_name() {
    local filepath="$1"
    local strip_prefix="${2:-}"  # Optional prefix to strip
    local validate_no_redundant="${3:-true}"  # Default: strict validation

    # Check for path traversal in full path
    if [[ "$filepath" == *".."* ]]; then
        echo "❌ ERROR: Path traversal detected in file path: '$filepath'" >&2
        echo "   Found: Directory traversal sequence (..)" >&2
        echo "   Fix: Use absolute paths or paths without directory traversal" >&2
        return 1
    fi

    # Extract basename
    local basename="${filepath##*/}"

    # Remove .md extension
    local feature="${basename%.md}"

    # Validate and apply strip_prefix parameter
    if [[ -n "$strip_prefix" ]]; then
        # Security: Validate strip_prefix itself (prevents path traversal via parameter)
        local prefix_found=false
        local allowed_prefix
        for allowed_prefix in $ALLOWED_PREFIXES; do
            if [[ "$strip_prefix" == "$allowed_prefix" ]]; then
                prefix_found=true
                break
            fi
        done

        if [[ "$prefix_found" == "false" ]]; then
            echo "❌ ERROR: Invalid strip_prefix: '$strip_prefix'" >&2
            echo "   Allowed prefixes: $ALLOWED_PREFIXES" >&2
            echo "   Never use 'prp_' as strip_prefix" >&2
            return 1
        fi

        # CRITICAL: Use ${var#prefix} instead of ${var//pattern/}
        # ${var#prefix} only removes from start (like Python's removeprefix())
        # ${var//pattern/} removes ALL occurrences (like Python's replace())
        # See PRP gotcha #13 for details
        feature="${feature#"$strip_prefix"}"

        # Check for empty result after stripping
        if [[ -z "$feature" ]]; then
            echo "❌ ERROR: Empty feature name after stripping prefix '$strip_prefix'" >&2
            echo "   File: $filepath" >&2
            echo "   Fix: Rename file with actual feature name after prefix" >&2
            return 1
        fi
    fi

    # Validate feature name with 6-level checks
    if ! validate_feature_name "$feature" "$validate_no_redundant"; then
        return 1
    fi

    # Success - output the validated feature name
    echo "$feature"
    return 0
}

# Validate that feature name is safe for bash variables
# (Used when feature names will be used as bash variable names)
validate_bash_variable_safe() {
    local feature="$1"

    # Bash variable names must:
    # 1. Start with letter or underscore
    # 2. Contain only alphanumeric and underscore
    # Note: Hyphens are NOT allowed in bash variable names
    if [[ ! "$feature" =~ ^[a-zA-Z_][a-zA-Z0-9_]*$ ]]; then
        echo "❌ WARNING: Feature name not safe for bash variables: '$feature'" >&2
        echo "   Bash variables must start with letter/underscore" >&2
        echo "   Bash variables cannot contain hyphens" >&2
        echo "   Note: This is a warning - feature name is still valid for file paths" >&2
        return 1
    fi

    return 0
}

# =============================================================================
# Helper Functions
# =============================================================================

# Show usage information
show_usage() {
    cat <<'EOF'
Usage: source .codex/scripts/security-validation.sh

Security validation for feature names - prevents path traversal and command injection.

Functions available when sourced:
  - extract_feature_name <filepath> [strip_prefix] [validate_no_redundant]
      Extract and validate feature name from file path

  - validate_feature_name <feature> [validate_no_redundant]
      Validate feature name with 6-level security checks

  - validate_bash_variable_safe <feature>
      Check if feature name is safe for bash variables

Arguments:
  filepath               Path to PRP file (e.g., "prps/INITIAL_feature.md")
  strip_prefix          Optional prefix to strip (must be INITIAL_ or EXAMPLE_)
  validate_no_redundant true (default) = reject prp_ prefix, false = allow
  feature               Feature name to validate

6-Level Security Validation:
  1. Path traversal (.., /, \)
  2. Whitelist (alphanumeric + underscore + hyphen only)
  3. Length check (max 50 chars)
  4. Dangerous characters ($, `, ;, &, |, etc.)
  5. Redundant prp_ prefix check (optional)
  6. Reserved names (., .., CON, NUL, etc.)

Examples:
  # Extract from INITIAL.md (strip prefix)
  feature=$(extract_feature_name "prps/INITIAL_user_auth.md" "INITIAL_" "true")

  # Extract from regular PRP (no prefix)
  feature=$(extract_feature_name "prps/user_auth.md" "" "true")

  # Validate existing feature name
  if validate_feature_name "user_auth" "true"; then
      echo "Valid feature name"
  fi

  # Check bash variable safety
  if validate_bash_variable_safe "user_auth"; then
      export FEATURE_NAME="$feature"
  fi

Valid Feature Names:
  ✅ user_auth
  ✅ web-scraper
  ✅ apiClient123
  ✅ TEST_Feature-v2

Invalid Feature Names:
  ❌ ../../etc/passwd (path traversal)
  ❌ test;rm -rf / (command injection)
  ❌ test$(whoami) (command injection)
  ❌ prp_feature (redundant prefix, when validate_no_redundant=true)
  ❌ very_long_feature_name_that_exceeds_the_maximum_length_limit (too long)
  ❌ . (reserved name)
  ❌ CON (reserved Windows name)

Critical Gotcha: removeprefix() vs replace()
  WRONG: feature="${basename//INITIAL_/}"  # Removes ALL occurrences
         "INITIAL_INITIAL_test" → "test" (wrong!)

  RIGHT: feature="${basename#INITIAL_}"  # Only removes from start
         "INITIAL_INITIAL_test" → "INITIAL_test" (correct!)

See Also:
  - .claude/patterns/security-validation.md (detailed pattern documentation)
  - .claude/conventions/prp-naming.md (naming conventions)
  - prps/codex_commands.md (gotcha #2, lines 266-307)

EOF
}

# =============================================================================
# Main Script Logic
# =============================================================================

# Show usage if called directly (not sourced)
if [ "${BASH_SOURCE[0]:-}" = "${0}" ]; then
    echo "⚠️  This script is meant to be sourced, not executed directly." >&2
    echo "" >&2
    show_usage
    exit 1
fi

# If sourced, confirm loading
echo "📦 Security validation script loaded" >&2
echo "   Available functions: extract_feature_name, validate_feature_name, validate_bash_variable_safe" >&2
echo "   Security: 6-level validation (path traversal, whitelist, length, injection, redundant prefix, reserved names)" >&2
