"""
Security module for command validation and output sanitization.

This module implements command blocklists, allowlists, and output sanitization
to prevent dangerous command execution and information leakage.

Patterns from:
- PRP: Command injection prevention (CWE-78)
- PRP: Allowlist validation approach
- PRP: Secrets redaction for API keys, passwords, tokens
"""

import re
import shlex
from typing import Tuple

# Blocked commands that are dangerous and should never be executed
# Pattern: Explicit list of destructive commands from PRP Task 3
BLOCKED_COMMANDS = [
    "rm -rf /",
    "dd if=/dev/zero",
    ":(){ :|:& };:",  # Fork bomb
    "chmod -R 777 /",
    "mkfs",
    # Additional dangerous patterns
    "rm -rf /*",
    "mkfs.ext4",
    "mkfs.ext3",
    "mkfs.xfs",
    "mkfs.btrfs",
    "> /dev/sda",  # Overwrite disk
    "dd if=/dev/zero of=/dev/sda",  # Wipe disk
]

# Allowed commands (allowlist approach is more secure than blocklist)
# Pattern: Read-only, write, and system commands from PRP Task 3
ALLOWED_COMMANDS = {
    # Read-only commands
    "ls",
    "pwd",
    "cat",
    "grep",
    "echo",
    "find",
    "head",
    "tail",
    "wc",
    "sort",
    "uniq",
    "cut",
    "awk",
    "sed",
    "less",
    "more",
    "file",
    "stat",
    "du",
    "df",
    # Write commands (limited)
    "touch",
    "mkdir",
    "cp",
    "mv",
    "ln",
    # System commands
    "ps",
    "top",
    "uptime",
    "whoami",
    "hostname",
    "uname",
    "date",
    "env",
    "printenv",
    "which",
    "whereis",
    "type",
    # Development/debugging
    "python",
    "python3",
    "node",
    "npm",
    "git",
    "curl",
    "wget",
    "tar",
    "gzip",
    "gunzip",
    "unzip",
    "zip",
}

# Shell metacharacters that indicate command chaining/injection
# Pattern: From PRP Gotcha #2 - shell metacharacters are dangerous with shell=True
SHELL_METACHARACTERS = {
    ";",   # Command separator
    "|",   # Pipe
    "&",   # Background execution
    "&&",  # AND operator
    "||",  # OR operator
    "$",   # Variable expansion
    "`",   # Command substitution (backtick)
    "$()",  # Command substitution
    ">",   # Output redirection (checked separately)
    "<",   # Input redirection
}

# Regex patterns for secret detection
# Pattern: Redact common secret formats from output
SECRET_PATTERNS = [
    # API Keys
    (re.compile(r'(API_KEY\s*=\s*)[^\s]+', re.IGNORECASE), r'\1[REDACTED]'),
    (re.compile(r'(APIKEY\s*=\s*)[^\s]+', re.IGNORECASE), r'\1[REDACTED]'),
    (re.compile(r'(api[-_]?key\s*[:=]\s*)[^\s\'"]+', re.IGNORECASE), r'\1[REDACTED]'),

    # Passwords
    (re.compile(r'(PASSWORD\s*=\s*)[^\s]+', re.IGNORECASE), r'\1[REDACTED]'),
    (re.compile(r'(PASS\s*=\s*)[^\s]+', re.IGNORECASE), r'\1[REDACTED]'),
    (re.compile(r'(password\s*[:=]\s*)[^\s\'"]+', re.IGNORECASE), r'\1[REDACTED]'),

    # Tokens
    (re.compile(r'(TOKEN\s*=\s*)[^\s]+', re.IGNORECASE), r'\1[REDACTED]'),
    (re.compile(r'(ACCESS_TOKEN\s*=\s*)[^\s]+', re.IGNORECASE), r'\1[REDACTED]'),
    (re.compile(r'(REFRESH_TOKEN\s*=\s*)[^\s]+', re.IGNORECASE), r'\1[REDACTED]'),
    (re.compile(r'(token\s*[:=]\s*)[^\s\'"]+', re.IGNORECASE), r'\1[REDACTED]'),

    # Secrets
    (re.compile(r'(SECRET\s*=\s*)[^\s]+', re.IGNORECASE), r'\1[REDACTED]'),
    (re.compile(r'(SECRET_KEY\s*=\s*)[^\s]+', re.IGNORECASE), r'\1[REDACTED]'),
    (re.compile(r'(secret\s*[:=]\s*)[^\s\'"]+', re.IGNORECASE), r'\1[REDACTED]'),

    # AWS/Cloud credentials
    (re.compile(r'(AWS_SECRET_ACCESS_KEY\s*=\s*)[^\s]+', re.IGNORECASE), r'\1[REDACTED]'),
    (re.compile(r'(AWS_ACCESS_KEY_ID\s*=\s*)[^\s]+', re.IGNORECASE), r'\1[REDACTED]'),

    # Database credentials
    (re.compile(r'(DB_PASSWORD\s*=\s*)[^\s]+', re.IGNORECASE), r'\1[REDACTED]'),
    (re.compile(r'(DATABASE_URL\s*=\s*)[^\s]+', re.IGNORECASE), r'\1[REDACTED]'),

    # Private keys (PEM format)
    (re.compile(r'-----BEGIN [A-Z\s]+ PRIVATE KEY-----[\s\S]+?-----END [A-Z\s]+ PRIVATE KEY-----', re.IGNORECASE),
     '[REDACTED PRIVATE KEY]'),
]


def validate_command(command: str) -> Tuple[bool, str]:
    """
    Validate command for security before execution.

    Implements:
    - Blocklist checking (dangerous commands)
    - Allowlist checking (only permitted commands)
    - Shell metacharacter detection
    - Command injection prevention

    Pattern from: PRP Task 3 - Security Layer validation
    Critical Gotcha: Uses shlex.split() for safe parsing (PRP Gotcha #2)

    Args:
        command: Command string to validate

    Returns:
        Tuple of (is_valid: bool, error_message: str)
        - (True, "") if command is valid
        - (False, "reason") if command is blocked

    Examples:
        >>> validate_command("ls -la")
        (True, "")

        >>> validate_command("rm -rf /")
        (False, "Command blocked: matches dangerous pattern 'rm -rf /'")

        >>> validate_command("ls; rm -rf /")
        (False, "Command contains shell metacharacter: ;")
    """
    # Empty command check
    if not command or not command.strip():
        return False, "Command cannot be empty"

    command = command.strip()

    # Check against blocklist (exact and substring matches)
    for blocked in BLOCKED_COMMANDS:
        if blocked in command:
            return False, f"Command blocked: matches dangerous pattern '{blocked}'"

    # Check for shell metacharacters (command chaining/injection indicators)
    # Pattern: Detect command chaining attempts from PRP security requirements
    for metachar in SHELL_METACHARACTERS:
        if metachar in command:
            # Allow > and < in specific safe contexts (e.g., "find . -type f")
            if metachar in (">", "<"):
                # Check if it's comparison operator (safe) vs redirection (potentially unsafe)
                # For now, block all redirections as they can be used for data exfiltration
                if " > " in command or " < " in command or command.endswith(">") or command.endswith("<"):
                    return False, f"Command contains shell metacharacter: {metachar} (redirection blocked)"
                # Allow comparison operators in test expressions
                continue
            else:
                return False, f"Command contains shell metacharacter: {metachar} (command chaining blocked)"

    # Parse command to extract base command (first argument)
    # Pattern: Use shlex.split() for safe parsing (PRP Gotcha #2)
    try:
        args = shlex.split(command)
    except ValueError as e:
        return False, f"Invalid command syntax: {e}"

    if not args:
        return False, "Command cannot be empty after parsing"

    # Extract base command (handle paths like /usr/bin/ls)
    base_command = args[0].split("/")[-1]

    # Check against allowlist
    # Pattern: Allowlist approach from PRP Task 3
    if base_command not in ALLOWED_COMMANDS:
        return False, f"Command '{base_command}' not in allowlist. Allowed commands: {', '.join(sorted(ALLOWED_COMMANDS))}"

    # All checks passed
    return True, ""


def sanitize_output(output: str) -> str:
    """
    Redact secrets from command output.

    Scans output for common secret patterns (API keys, passwords, tokens)
    and replaces them with [REDACTED] to prevent information leakage.

    Pattern from: PRP Task 3 - Security Layer output sanitization

    Args:
        output: Raw command output

    Returns:
        Sanitized output with secrets redacted

    Examples:
        >>> sanitize_output("API_KEY=sk-secret123\\nother output")
        'API_KEY=[REDACTED]\\nother output'

        >>> sanitize_output("PASSWORD=mysecret123 TOKEN=abc456")
        'PASSWORD=[REDACTED] TOKEN=[REDACTED]'
    """
    if not output:
        return output

    sanitized = output

    # Apply each regex pattern to redact secrets
    # Pattern: Multiple regex patterns for different secret formats
    for pattern, replacement in SECRET_PATTERNS:
        sanitized = pattern.sub(replacement, sanitized)

    return sanitized


def is_safe_for_execution(command: str) -> bool:
    """
    Quick check if command is safe for execution.

    Convenience function that returns boolean only.
    For detailed error messages, use validate_command().

    Args:
        command: Command to validate

    Returns:
        True if command is safe, False otherwise
    """
    is_valid, _ = validate_command(command)
    return is_valid
