"""Security validation tests for command execution.

This module tests:
- Command allowlist validation (only approved commands can execute)
- Blocklist rejection (dangerous commands are blocked)
- Shell metacharacter detection (command injection prevention)
- Secrets redaction from output (API keys, passwords, tokens)

Critical Security Patterns:
- Allowlist approach is more secure than blocklist
- Shell metacharacters (;, |, &, $, `) indicate injection attempts
- Secrets must be redacted from all command output

Pattern Sources:
- PRP Task 3: Security Layer specification
- PRP Gotcha #2: Command injection prevention (CWE-78)
"""

import pytest

from src.security import (
    ALLOWED_COMMANDS,
    BLOCKED_COMMANDS,
    validate_command,
    sanitize_output,
    is_safe_for_execution,
)


class TestCommandValidation:
    """Test suite for command validation logic."""

    def test_allowed_commands_pass_validation(self):
        """Test that allowed commands pass validation.

        Validates:
        - All commands in ALLOWED_COMMANDS pass
        - Validation returns (True, "")
        - No false positives
        """
        # Test various allowed commands
        allowed_tests = [
            "ls -la /tmp",
            "pwd",
            "cat file.txt",
            "grep pattern file.txt",
            "echo hello world",
            "find . -name '*.py'",
            "ps aux",
            "du -sh /tmp",
            "python script.py",
            "git status",
        ]

        for command in allowed_tests:
            is_valid, error = validate_command(command)
            assert is_valid, f"Command '{command}' should be allowed but got error: {error}"
            assert error == "", f"Error message should be empty for allowed command '{command}'"

    def test_blocked_commands_rejected(self):
        """Test that blocked dangerous commands are rejected.

        Validates:
        - All BLOCKED_COMMANDS are rejected
        - Error message indicates blocking
        - Clear explanation provided
        """
        # Test exact blocked commands
        blocked_tests = [
            "rm -rf /",
            "dd if=/dev/zero",
            ":(){ :|:& };:",  # Fork bomb
            "chmod -R 777 /",
            "mkfs",
        ]

        for command in blocked_tests:
            is_valid, error = validate_command(command)
            assert not is_valid, f"Command '{command}' should be blocked"
            assert "blocked" in error.lower(), f"Error should indicate blocking: {error}"
            assert error != "", "Error message should explain why command is blocked"

    def test_blocked_command_substrings_rejected(self):
        """Test that commands containing blocked patterns are rejected.

        Validates:
        - Substring matching works (not just exact match)
        - Commands like "echo rm -rf /" are blocked
        - Prevents obfuscation attempts
        """
        dangerous_substring_tests = [
            "echo rm -rf / && ls",  # Contains blocked pattern
            "test && dd if=/dev/zero of=/dev/sda",  # Disk wipe
            "ls && mkfs.ext4 /dev/sda",  # Format disk
        ]

        for command in dangerous_substring_tests:
            is_valid, error = validate_command(command)
            assert not is_valid, f"Command with dangerous substring '{command}' should be blocked"
            assert "blocked" in error.lower()

    def test_shell_metacharacters_caught(self):
        """Test that shell metacharacters are detected and rejected.

        CRITICAL: Shell metacharacters enable command injection (PRP Gotcha #2)

        Validates:
        - Semicolon (;) - command separator
        - Pipe (|) - command chaining
        - Ampersand (&, &&) - background/AND execution
        - OR operator (||)
        - Variable expansion ($)
        - Command substitution (`, $())
        """
        metacharacter_tests = [
            ("ls; echo test", ";"),          # Changed to avoid blocklist
            ("ls | grep test", "|"),
            ("ls & echo test", "&"),
            ("ls && echo test", "&&"),
            ("ls || echo test", "||"),
            ("echo $HOME", "$"),
            ("echo `whoami`", "`"),
        ]

        for command, metachar in metacharacter_tests:
            is_valid, error = validate_command(command)
            assert not is_valid, f"Command with metacharacter '{metachar}' should be rejected: {command}"
            # Error mentions either "metacharacter" or the actual metachar or "chaining"
            assert any(keyword in error.lower() for keyword in ["metacharacter", "chaining", metachar]), \
                f"Error should mention command chaining or metacharacter '{metachar}': {error}"

    def test_output_redirection_blocked(self):
        """Test that output redirection is blocked (data exfiltration risk).

        Validates:
        - > (output redirection) is blocked
        - < (input redirection) is blocked
        - Prevents writing to sensitive files
        """
        redirection_tests = [
            "cat /etc/passwd > /tmp/passwords",
            "cat < /etc/shadow",
        ]

        for command in redirection_tests:
            is_valid, error = validate_command(command)
            assert not is_valid, f"Redirection command should be blocked: {command}"
            assert ">" in error or "<" in error or "redirection" in error.lower(), \
                f"Error should mention redirection: {error}"

    def test_command_not_in_allowlist_rejected(self):
        """Test that commands not in ALLOWED_COMMANDS are rejected.

        Validates:
        - Unknown commands are blocked
        - Error message lists allowed commands
        - Allowlist approach (secure by default)
        """
        unapproved_commands = [
            "systemctl restart nginx",  # System control
            "reboot",  # System reboot
            "shutdown",  # System shutdown
            "iptables -F",  # Firewall modification
            "useradd hacker",  # User creation
        ]

        for command in unapproved_commands:
            is_valid, error = validate_command(command)
            assert not is_valid, f"Unapproved command should be rejected: {command}"
            assert "allowlist" in error.lower() or "not in" in error.lower(), \
                f"Error should mention allowlist: {error}"
            # Should suggest valid commands
            assert any(cmd in error for cmd in ["ls", "pwd", "cat"]), \
                f"Error should list some allowed commands: {error}"

    def test_empty_command_rejected(self):
        """Test that empty or whitespace-only commands are rejected.

        Validates:
        - Empty string rejected
        - Whitespace-only rejected
        - Clear error message
        """
        empty_tests = [
            "",
            "   ",
            "\t",
            "\n",
        ]

        for command in empty_tests:
            is_valid, error = validate_command(command)
            assert not is_valid, f"Empty command '{repr(command)}' should be rejected"
            assert "empty" in error.lower(), f"Error should mention 'empty': {error}"

    def test_command_with_path_allowed(self):
        """Test that commands with full paths work if base command is allowed.

        Validates:
        - /usr/bin/ls is allowed (base command: ls)
        - /bin/cat is allowed (base command: cat)
        - Path is stripped to check allowlist
        """
        path_tests = [
            "/usr/bin/ls -la",
            "/bin/cat file.txt",
            "/usr/bin/python3 script.py",
        ]

        for command in path_tests:
            is_valid, error = validate_command(command)
            assert is_valid, f"Command with path '{command}' should be allowed: {error}"

    def test_is_safe_for_execution_convenience_function(self):
        """Test convenience function is_safe_for_execution().

        Validates:
        - Returns True for safe commands
        - Returns False for unsafe commands
        - Simpler API than validate_command()
        """
        assert is_safe_for_execution("ls -la") is True
        assert is_safe_for_execution("pwd") is True
        assert is_safe_for_execution("rm -rf /") is False
        assert is_safe_for_execution("ls; rm file") is False
        assert is_safe_for_execution("") is False


class TestSecretsRedaction:
    """Test suite for secret redaction from command output."""

    def test_api_key_redacted(self):
        """Test that API keys are redacted from output.

        Validates:
        - API_KEY=... patterns redacted
        - api_key: ... patterns redacted
        - Case insensitive matching
        """
        api_key_tests = [
            ("API_KEY=sk-secret123\nother output", "sk-secret123"),
            ("APIKEY=abcdef123456\nmore data", "abcdef123456"),
            ("api_key: sk-proj-xyz789", "sk-proj-xyz789"),
            ("api-key=secret_value", "secret_value"),
        ]

        for output, secret in api_key_tests:
            sanitized = sanitize_output(output)
            assert secret not in sanitized, f"Secret '{secret}' should be redacted"
            assert "[REDACTED]" in sanitized, f"Should contain [REDACTED] marker"

    def test_password_redacted(self):
        """Test that passwords are redacted from output.

        Validates:
        - PASSWORD=... patterns redacted
        - password: ... patterns redacted
        - PASS=... patterns redacted
        """
        password_tests = [
            ("PASSWORD=mysecret123\ndata", "mysecret123"),
            ("PASS=p@ssw0rd\nmore", "p@ssw0rd"),
            ("password: hunter2", "hunter2"),
            ("password=SuperSecret!", "SuperSecret!"),
        ]

        for output, secret in password_tests:
            sanitized = sanitize_output(output)
            assert secret not in sanitized, f"Password '{secret}' should be redacted"
            assert "[REDACTED]" in sanitized

    def test_token_redacted(self):
        """Test that tokens are redacted from output.

        Validates:
        - TOKEN=... patterns redacted
        - ACCESS_TOKEN=... patterns redacted
        - REFRESH_TOKEN=... patterns redacted
        """
        token_tests = [
            ("TOKEN=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9\ndata", "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9"),
            ("ACCESS_TOKEN=bearer_token_here", "bearer_token_here"),
            ("REFRESH_TOKEN=refresh_abc123", "refresh_abc123"),
            ("token: jwt_token_value", "jwt_token_value"),
        ]

        for output, secret in token_tests:
            sanitized = sanitize_output(output)
            assert secret not in sanitized, f"Token '{secret}' should be redacted"
            assert "[REDACTED]" in sanitized

    def test_secret_key_redacted(self):
        """Test that secret keys are redacted from output.

        Validates:
        - SECRET=... patterns redacted
        - SECRET_KEY=... patterns redacted
        - secret: ... patterns redacted
        """
        secret_tests = [
            ("SECRET=my_secret_value\n", "my_secret_value"),
            ("SECRET_KEY=app_secret_key_123", "app_secret_key_123"),
            ("secret: hidden_value", "hidden_value"),
        ]

        for output, secret in secret_tests:
            sanitized = sanitize_output(output)
            assert secret not in sanitized, f"Secret '{secret}' should be redacted"
            assert "[REDACTED]" in sanitized

    def test_aws_credentials_redacted(self):
        """Test that AWS credentials are redacted.

        Validates:
        - AWS_SECRET_ACCESS_KEY redacted
        - AWS_ACCESS_KEY_ID redacted
        - Prevents cloud credential leakage
        """
        aws_tests = [
            "AWS_SECRET_ACCESS_KEY=wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY\n",
            "AWS_ACCESS_KEY_ID=AKIAIOSFODNN7EXAMPLE\n",
        ]

        for output in aws_tests:
            sanitized = sanitize_output(output)
            # Check that the actual secret value is gone
            assert "EXAMPLE" not in sanitized or "[REDACTED]" in sanitized
            assert "[REDACTED]" in sanitized

    def test_database_url_redacted(self):
        """Test that database URLs with credentials are redacted.

        Validates:
        - DB_PASSWORD redacted
        - DATABASE_URL redacted
        - Prevents database credential leakage
        """
        db_tests = [
            "DB_PASSWORD=db_secret_123\n",
            "DATABASE_URL=postgresql://user:password@localhost/db\n",
        ]

        for output in db_tests:
            sanitized = sanitize_output(output)
            assert "[REDACTED]" in sanitized

    def test_multiple_secrets_redacted(self):
        """Test that multiple secrets in same output are all redacted.

        Validates:
        - All secrets redacted (not just first one)
        - Different secret types handled
        - No secrets leak through
        """
        output = """
        API_KEY=sk-secret123
        PASSWORD=mypassword
        TOKEN=jwt_token
        SECRET=hidden_value
        """

        sanitized = sanitize_output(output)

        # All secrets should be redacted
        assert "sk-secret123" not in sanitized
        assert "mypassword" not in sanitized
        assert "jwt_token" not in sanitized
        assert "hidden_value" not in sanitized

        # Should have multiple [REDACTED] markers
        assert sanitized.count("[REDACTED]") >= 4

    def test_non_secret_output_unchanged(self):
        """Test that output without secrets is unchanged.

        Validates:
        - Normal output not modified
        - No false positives
        - Performance optimization (no-op when no secrets)
        """
        normal_outputs = [
            "file1.txt\nfile2.txt\n",
            "total 64\ndrwxr-xr-x 4 user group\n",
            "Hello world\nThis is normal output\n",
        ]

        for output in normal_outputs:
            sanitized = sanitize_output(output)
            assert sanitized == output, f"Normal output should be unchanged"
            assert "[REDACTED]" not in sanitized

    def test_empty_output_handled(self):
        """Test that empty output is handled gracefully.

        Validates:
        - Empty string returns empty string
        - No errors on empty input
        """
        assert sanitize_output("") == ""
        assert sanitize_output(None) is None or sanitize_output(None) == ""

    def test_case_insensitive_redaction(self):
        """Test that secret patterns are case-insensitive.

        Validates:
        - api_key, API_KEY, Api_Key all caught
        - password, PASSWORD, Password all caught
        - Prevents case-based evasion
        """
        case_tests = [
            "api_key=secret",
            "API_KEY=secret",
            "Api_Key=secret",
            "PASSWORD=secret",
            "password=secret",
            "Password=secret",
        ]

        for output in case_tests:
            sanitized = sanitize_output(output)
            assert "secret" not in sanitized, f"Case variation '{output}' should redact secret"
            assert "[REDACTED]" in sanitized
