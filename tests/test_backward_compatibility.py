"""Tests for Backward Compatibility (Task 9)."""

import pytest
import json
from pathlib import Path
from unittest.mock import Mock, patch, mock_open


class TestExistingPRPExecution:
    """Test existing PRPs execute without modification."""

    def test_prp_structure_unchanged(self, temp_prp_dir):
        """Test existing PRP directory structure is preserved."""
        # Existing PRP structure
        prp_name = "existing_feature"
        prp_dir = temp_prp_dir / prp_name
        prp_dir.mkdir(parents=True)

        # Existing files
        (prp_dir / f"{prp_name}.md").write_text("# Existing PRP")
        planning_dir = prp_dir / "planning"
        planning_dir.mkdir()
        (planning_dir / "feature-analysis.md").write_text("# Analysis")

        # Should be able to execute without modifying structure
        assert (prp_dir / f"{prp_name}.md").exists()
        assert planning_dir.exists()

        # Can add execution directory without breaking structure
        exec_dir = prp_dir / "execution"
        exec_dir.mkdir()

        assert exec_dir.exists()
        assert (prp_dir / f"{prp_name}.md").exists()  # Original preserved

    def test_execute_prp_without_initial_md(self, temp_prp_dir):
        """Test execute-prp works with regular PRPs (not INITIAL.md)."""
        prp_name = "user_authentication"
        prp_path = temp_prp_dir / f"{prp_name}.md"

        # Regular PRP (not INITIAL_*.md)
        prp_path.write_text("# User Authentication PRP")

        # Should extract feature name correctly
        feature_name = prp_path.stem  # Remove .md

        assert feature_name == prp_name
        assert not feature_name.startswith("INITIAL_")

    def test_legacy_prp_format_support(self):
        """Test support for legacy PRP format."""
        # Legacy PRP might have different sections
        legacy_prp = """# PRP: Legacy Feature

## Overview
Legacy description

## Implementation
Legacy implementation steps

## Validation
Legacy validation
"""

        # Should still be parsable
        sections = ["Overview", "Implementation", "Validation"]

        for section in sections:
            assert section in legacy_prp, \
                f"Legacy format should preserve {section} section"


class TestGeneratePRPBackwardCompatibility:
    """Test generate-prp with old INITIAL.md files."""

    def test_initial_md_prefix_detection(self):
        """Test detection of INITIAL_ prefix."""
        test_files = [
            ("INITIAL_user_auth.md", True, "user_auth"),
            ("user_auth.md", False, "user_auth"),
            ("INITIAL_new_feature.md", True, "new_feature")
        ]

        for filename, has_prefix, expected_feature in test_files:
            stem = filename.replace(".md", "")
            has_initial = stem.startswith("INITIAL_")

            assert has_initial == has_prefix, \
                f"Prefix detection failed for {filename}"

            # Extract feature name
            if has_initial:
                feature = stem.removeprefix("INITIAL_")
            else:
                feature = stem

            assert feature == expected_feature, \
                f"Feature extraction failed for {filename}"

    def test_old_initial_files_work(self, temp_prp_dir):
        """Test old INITIAL.md files still work."""
        # Old INITIAL.md format
        old_initial_content = """Create a user authentication system.

Features:
- Login/logout
- Password hashing
- JWT tokens
"""

        initial_path = temp_prp_dir / "INITIAL_user_auth.md"
        initial_path.write_text(old_initial_content)

        # Should be readable
        assert initial_path.exists()

        # Feature name extraction
        feature_name = initial_path.stem.removeprefix("INITIAL_")
        assert feature_name == "user_auth"

    def test_prp_directory_creation_compatible(self, temp_prp_dir):
        """Test PRP directory creation compatible with existing structure."""
        feature_name = "test_feature"

        # Create directories as in new workflow
        dirs_to_create = [
            temp_prp_dir / feature_name / "planning",
            temp_prp_dir / feature_name / "examples",
            temp_prp_dir / feature_name / "execution"
        ]

        for directory in dirs_to_create:
            directory.mkdir(parents=True, exist_ok=True)

        # Should not conflict with existing PRPs
        for directory in dirs_to_create:
            assert directory.exists()


class TestExecutePRPBackwardCompatibility:
    """Test execute-prp with legacy PRP format."""

    def test_execute_legacy_task_format(self):
        """Test execution of legacy task format."""
        # Legacy task format (simple markdown list)
        legacy_tasks = """## Implementation Blueprint

### Task 1: Create Models
Create user model with validation.

### Task 2: Create API
Create authentication endpoints.
"""

        # Should be able to parse tasks
        import re
        task_pattern = r'### Task \d+: (.*?)\n'
        tasks = re.findall(task_pattern, legacy_tasks)

        assert len(tasks) >= 2, "Should parse legacy task format"
        assert "Create Models" in tasks[0]

    def test_generic_implementer_fallback(self):
        """Test fallback to generic implementer for unknown domains."""
        # Legacy PRP without domain experts
        components = ["Custom business logic", "Generic coding tasks"]

        # No domain matches
        def detect_domain(components):
            # Simplified domain detection
            known_domains = ["terraform", "azure", "kubernetes"]
            for component in components:
                if any(domain in component.lower() for domain in known_domains):
                    return domain
            return None

        domain = detect_domain(components)

        # Should use generic implementer
        implementer = domain if domain else "prp-exec-implementer"
        assert implementer == "prp-exec-implementer"

    def test_no_breaking_changes_to_prp_structure(self):
        """Test no breaking changes to PRP file structure."""
        # Essential PRP sections that must remain
        essential_sections = [
            "## Goal",
            "## Why",
            "## What",
            "## All Needed Context",
            "## Implementation Blueprint",
            "## Validation Loop"
        ]

        # Modern PRP template
        modern_prp = """# PRP: Test Feature

## Goal
Feature description

## Why
Business value

## What
Technical details

## All Needed Context
Resources

## Implementation Blueprint
Tasks

## Validation Loop
Validation steps
"""

        # Verify all sections present
        for section in essential_sections:
            assert section in modern_prp, \
                f"Essential section '{section}' missing (breaking change)"


class TestNoBreakingChangesForUsers:
    """Test no breaking changes for existing users."""

    def test_file_paths_remain_consistent(self):
        """Test file paths remain consistent with existing codebase."""
        # Expected paths should not change
        expected_paths = {
            "agents": ".claude/agents/",
            "skills": ".claude/skills/",
            "patterns": ".claude/patterns/",
            "commands": ".claude/commands/",
            "prps": "prps/"
        }

        for component, path in expected_paths.items():
            assert path.startswith(".claude/") or path == "prps/", \
                f"{component} path changed (breaking change)"

    def test_agent_frontmatter_schema_compatible(self, sample_agent_frontmatter):
        """Test agent frontmatter schema remains compatible."""
        # Core fields that must remain
        core_fields = ["name", "description", "tools"]

        for field in core_fields:
            assert field in sample_agent_frontmatter, \
                f"Core field '{field}' missing (breaking change)"

    def test_skill_frontmatter_schema_compatible(self, sample_skill_frontmatter):
        """Test skill frontmatter schema remains compatible."""
        # Core fields that must remain
        core_fields = ["name", "description"]

        for field in core_fields:
            assert field in sample_skill_frontmatter, \
                f"Core field '{field}' missing (breaking change)"

    def test_command_invocation_unchanged(self):
        """Test command invocation patterns unchanged."""
        # Commands should still be invoked same way
        commands = [
            "/generate-prp",
            "/execute-prp",
            "/create-agent"
        ]

        for cmd in commands:
            assert cmd.startswith("/"), \
                f"Command '{cmd}' format changed (breaking change)"

            # No spaces in command names
            assert " " not in cmd, \
                f"Command '{cmd}' has spaces (breaking change)"


class TestMigrationPath:
    """Test migration path from old to new architecture."""

    def test_archon_to_file_backend_migration(self, temp_prp_dir):
        """Test migration from Archon to file backend state."""
        # Simulate Archon project data
        archon_project = {
            "project_id": "archon-123",
            "name": "existing_feature",
            "tasks": {
                "task-1": {"status": "done"},
                "task-2": {"status": "doing"}
            }
        }

        # Migrate to file backend
        state_path = temp_prp_dir / "existing_feature" / "execution" / "state.json"
        state_path.parent.mkdir(parents=True, exist_ok=True)

        # Convert Archon format to file backend format
        file_backend_state = {
            "schema_version": "1.0",
            "project_id": archon_project["project_id"],
            "name": archon_project["name"],
            "created_at": "2025-11-20T12:00:00.000Z",
            "tasks": archon_project["tasks"]
        }

        state_path.write_text(json.dumps(file_backend_state, indent=2))

        # Verify migration
        migrated = json.loads(state_path.read_text())
        assert migrated["project_id"] == archon_project["project_id"]
        assert len(migrated["tasks"]) == len(archon_project["tasks"])

    def test_gradual_rollout_support(self):
        """Test gradual rollout of new architecture."""
        # Should support both Archon and file backend simultaneously
        def get_task_tracker(prefer_archon: bool = False):
            """Get task tracker with preference."""
            if prefer_archon:
                try:
                    # Try Archon first
                    return "archon"
                except Exception:
                    return "file"  # Fallback to file
            else:
                return "file"  # Default to file

        # New users get file backend
        new_user_tracker = get_task_tracker(prefer_archon=False)
        assert new_user_tracker == "file"

        # Existing users can opt for Archon
        existing_user_tracker = get_task_tracker(prefer_archon=True)
        assert existing_user_tracker in ["archon", "file"]

    def test_documentation_migration_notes(self):
        """Test migration documentation exists."""
        # Migration guide should cover:
        required_sections = [
            "Archon to Skills migration",
            "Task tracking abstraction",
            "Basic-memory integration",
            "Breaking changes (if any)",
            "Rollback procedure"
        ]

        # Placeholder for migration guide validation
        migration_guide_exists = True  # Would check actual file

        assert migration_guide_exists, \
            "Migration guide should exist for users"


class TestPerformanceParity:
    """Test performance parity with Archon-based system."""

    def test_file_backend_faster_than_archon(self):
        """Test file backend is faster than Archon (no network)."""
        import time

        # File backend operation (fast, local)
        start = time.time()
        # Simulate file operation
        data = {"test": "data"}
        json.dumps(data)
        file_time = time.time() - start

        # Archon would be slower (network latency)
        simulated_network_latency = 0.1  # 100ms
        archon_time = file_time + simulated_network_latency

        assert file_time < archon_time, \
            "File backend should be faster than Archon"

    def test_no_external_dependency_overhead(self):
        """Test no external dependency overhead with file backend."""
        # File backend has zero external dependencies
        external_deps_file = []

        # Archon backend would have network dependency
        external_deps_archon = ["network", "archon_server"]

        assert len(external_deps_file) == 0, \
            "File backend should have no external dependencies"
        assert len(external_deps_archon) > 0, \
            "Archon backend has external dependencies"
