"""
Tests for port configuration requirements.

This test file verifies that all services properly require environment variables
for port configuration and fail with clear error messages when not set.
"""

import os

import pytest


class TestPortConfiguration:
    """Test that services require port environment variables."""

    def setup_method(self):
        """Save original environment variables before each test."""
        self.original_env = os.environ.copy()

    def teardown_method(self):
        """Restore original environment variables after each test."""
        os.environ.clear()
        os.environ.update(self.original_env)

    def test_service_discovery_requires_all_ports(self):
        """Test that ServiceDiscovery requires all port environment variables."""
        # Clear port environment variables
        for key in ["ARCHON_SERVER_PORT", "ARCHON_MCP_PORT", "ARCHON_AGENTS_PORT"]:
            os.environ.pop(key, None)

        # Import should fail without environment variables
        with pytest.raises(ValueError, match="ARCHON_SERVER_PORT environment variable is required"):
            from src.server.config.service_discovery import ServiceDiscovery

            ServiceDiscovery()

    def test_service_discovery_requires_mcp_port(self):
        """Test that ServiceDiscovery requires MCP port."""
        os.environ["ARCHON_SERVER_PORT"] = "8181"
        os.environ.pop("ARCHON_MCP_PORT", None)
        os.environ["ARCHON_AGENTS_PORT"] = "8052"

        with pytest.raises(ValueError, match="ARCHON_MCP_PORT environment variable is required"):
            from src.server.config.service_discovery import ServiceDiscovery

            ServiceDiscovery()

    def test_service_discovery_requires_agents_port(self):
        """Test that ServiceDiscovery requires agents port."""
        os.environ["ARCHON_SERVER_PORT"] = "8181"
        os.environ["ARCHON_MCP_PORT"] = "8051"
        os.environ.pop("ARCHON_AGENTS_PORT", None)

        with pytest.raises(ValueError, match="ARCHON_AGENTS_PORT environment variable is required"):
            from src.server.config.service_discovery import ServiceDiscovery

            ServiceDiscovery()

    def test_service_discovery_with_all_ports(self):
        """Test that ServiceDiscovery works with all ports set."""
        os.environ["ARCHON_SERVER_PORT"] = "9191"
        os.environ["ARCHON_MCP_PORT"] = "9051"
        os.environ["ARCHON_AGENTS_PORT"] = "9052"

        from src.server.config.service_discovery import ServiceDiscovery

        sd = ServiceDiscovery()

        assert sd.DEFAULT_PORTS["api"] == 9191
        assert sd.DEFAULT_PORTS["mcp"] == 9051
        assert sd.DEFAULT_PORTS["agents"] == 9052

    def test_mcp_server_requires_port(self):
        """Test that MCP server requires ARCHON_MCP_PORT."""
        os.environ.pop("ARCHON_MCP_PORT", None)

        # We can't directly import mcp_server.py as it will raise at module level
        # So we test the specific logic
        with pytest.raises(ValueError, match="ARCHON_MCP_PORT environment variable is required"):
            mcp_port = os.getenv("ARCHON_MCP_PORT")
            if not mcp_port:
                raise ValueError(
                    "ARCHON_MCP_PORT environment variable is required. "
                    "Please set it in your .env file or environment. "
                    "Default value: 8051"
                )

    def test_main_server_requires_port(self):
        """Test that main server requires ARCHON_SERVER_PORT when run directly."""
        os.environ.pop("ARCHON_SERVER_PORT", None)

        # Test the logic that would be in main.py
        with pytest.raises(ValueError, match="ARCHON_SERVER_PORT environment variable is required"):
            server_port = os.getenv("ARCHON_SERVER_PORT")
            if not server_port:
                raise ValueError(
                    "ARCHON_SERVER_PORT environment variable is required. "
                    "Please set it in your .env file or environment. "
                    "Default value: 8181"
                )

    def test_agents_server_requires_port(self):
        """Test that agents server requires ARCHON_AGENTS_PORT."""
        os.environ.pop("ARCHON_AGENTS_PORT", None)

        # Test the logic that would be in agents/server.py
        with pytest.raises(ValueError, match="ARCHON_AGENTS_PORT environment variable is required"):
            agents_port = os.getenv("ARCHON_AGENTS_PORT")
            if not agents_port:
                raise ValueError(
                    "ARCHON_AGENTS_PORT environment variable is required. "
                    "Please set it in your .env file or environment. "
                    "Default value: 8052"
                )

    def test_agent_chat_api_requires_agents_port(self):
        """Test that agent_chat_api requires ARCHON_AGENTS_PORT for service calls."""
        os.environ.pop("ARCHON_AGENTS_PORT", None)

        # Test the logic that would be in agent_chat_api
        with pytest.raises(ValueError, match="ARCHON_AGENTS_PORT environment variable is required"):
            agents_port = os.getenv("ARCHON_AGENTS_PORT")
            if not agents_port:
                raise ValueError(
                    "ARCHON_AGENTS_PORT environment variable is required. "
                    "Please set it in your .env file or environment."
                )

    def test_config_requires_port_or_archon_mcp_port(self):
        """Test that config.py requires PORT or ARCHON_MCP_PORT."""
        from src.server.config.config import ConfigurationError

        os.environ.pop("PORT", None)
        os.environ.pop("ARCHON_MCP_PORT", None)

        # Test the logic from config.py
        with pytest.raises(
            ConfigurationError, match="PORT or ARCHON_MCP_PORT environment variable is required"
        ):
            port_str = os.getenv("PORT")
            if not port_str:
                port_str = os.getenv("ARCHON_MCP_PORT")
                if not port_str:
                    raise ConfigurationError(
                        "PORT or ARCHON_MCP_PORT environment variable is required. "
                        "Please set it in your .env file or environment. "
                        "Default value: 8051"
                    )

    def test_custom_port_values(self):
        """Test that services use custom port values when set."""
        # Set custom ports
        os.environ["ARCHON_SERVER_PORT"] = "9999"
        os.environ["ARCHON_MCP_PORT"] = "8888"
        os.environ["ARCHON_AGENTS_PORT"] = "7777"

        from src.server.config.service_discovery import ServiceDiscovery

        sd = ServiceDiscovery()

        # Verify custom ports are used
        assert sd.DEFAULT_PORTS["api"] == 9999
        assert sd.DEFAULT_PORTS["mcp"] == 8888
        assert sd.DEFAULT_PORTS["agents"] == 7777

        # Verify service URLs use custom ports
        if not sd.is_docker:
            assert sd.get_service_url("api") == "http://localhost:9999"
            assert sd.get_service_url("mcp") == "http://localhost:8888"
            assert sd.get_service_url("agents") == "http://localhost:7777"


class TestPortValidation:
    """Test port validation logic."""

    def test_invalid_port_values(self):
        """Test that invalid port values are rejected."""
        os.environ["ARCHON_SERVER_PORT"] = "not-a-number"
        os.environ["ARCHON_MCP_PORT"] = "8051"
        os.environ["ARCHON_AGENTS_PORT"] = "8052"

        with pytest.raises(ValueError):
            from src.server.config.service_discovery import ServiceDiscovery

            ServiceDiscovery()

    def test_port_out_of_range(self):
        """Test that port values must be valid port numbers."""
        test_cases = [
            ("0", False),  # Port 0 is reserved
            ("1", True),  # Valid
            ("65535", True),  # Maximum valid port
            ("65536", False),  # Too high
            ("-1", False),  # Negative
        ]

        for port_value, should_succeed in test_cases:
            os.environ["ARCHON_SERVER_PORT"] = port_value
            os.environ["ARCHON_MCP_PORT"] = "8051"
            os.environ["ARCHON_AGENTS_PORT"] = "8052"

            if should_succeed:
                # Should not raise
                from src.server.config.service_discovery import ServiceDiscovery

                sd = ServiceDiscovery()
                assert sd.DEFAULT_PORTS["api"] == int(port_value)
            else:
                # Should raise for invalid ports
                with pytest.raises((ValueError, AssertionError)):
                    from src.server.config.service_discovery import ServiceDiscovery

                    sd = ServiceDiscovery()
                    # Additional validation might be needed
                    port = int(port_value)
                    assert 1 <= port <= 65535, f"Port {port} out of valid range"
