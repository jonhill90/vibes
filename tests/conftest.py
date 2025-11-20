"""Test configuration and fixtures for agent architecture modernization tests."""

import pytest
import json
import tempfile
import shutil
from pathlib import Path
from typing import Dict, Any
from unittest.mock import MagicMock, Mock


@pytest.fixture
def temp_prp_dir():
    """Create temporary PRP directory for testing."""
    temp_dir = tempfile.mkdtemp(prefix="test_prp_")
    yield Path(temp_dir)
    shutil.rmtree(temp_dir)


@pytest.fixture
def sample_skill_frontmatter():
    """Sample skill frontmatter for testing."""
    return {
        "name": "test-skill",
        "description": "Test skill for unit testing. Use when testing skill system."
    }


@pytest.fixture
def sample_agent_frontmatter():
    """Sample agent frontmatter for testing."""
    return {
        "name": "test-expert",
        "description": "Test domain expert. USE PROACTIVELY for testing.",
        "tools": ["Read", "Write", "Grep"],
        "skills": ["test-skill"],
        "allowed_commands": ["echo", "ls"],
        "blocked_commands": ["rm", "dd"],
        "color": "blue"
    }


@pytest.fixture
def sample_task_state():
    """Sample task state for testing."""
    return {
        "project_id": "test-project-123",
        "name": "test_feature",
        "description": "Test feature description",
        "created_at": "2025-11-20T12:00:00.000Z",
        "tasks": {
            "task-1": {
                "title": "Task 1: Test task",
                "status": "todo",
                "created_at": "2025-11-20T12:00:00.000Z",
                "project_id": "test-project-123"
            }
        }
    }


@pytest.fixture
def sample_feature_analysis():
    """Sample feature analysis for domain detection."""
    return {
        "technical_components": [
            "Terraform modules for infrastructure",
            "Azure Resource Groups",
            "Python FastAPI backend"
        ],
        "domains_detected": ["terraform", "azure", "python_backend"]
    }


@pytest.fixture
def mock_read_file(monkeypatch):
    """Mock file read operations."""
    def mock_read(file_path: str) -> str:
        if "SKILL.md" in file_path:
            return """---
name: test-skill
description: Test skill description
---

# Test Skill

This is a test skill."""
        elif "task-manager.md" in file_path:
            return """---
name: task-manager
description: Task orchestration specialist
tools: Read, Write, Grep, Glob
---

You are a task manager."""
        elif "state.json" in file_path:
            return json.dumps({
                "project_id": "test-123",
                "tasks": {}
            })
        return ""

    monkeypatch.setattr("builtins.open", lambda path, mode='r': Mock(read=lambda: mock_read(path)))
    return mock_read


@pytest.fixture
def mock_basic_memory():
    """Mock basic-memory MCP responses."""
    return {
        "search_notes": Mock(return_value=[
            {"id": "note-1", "content": "Test knowledge note 1"},
            {"id": "note-2", "content": "Test knowledge note 2"}
        ]),
        "read_note": Mock(return_value={
            "id": "note-1",
            "content": "Detailed note content"
        })
    }


def assert_valid_frontmatter(frontmatter: Dict[str, Any], required_fields: list):
    """Helper to assert frontmatter has required fields."""
    for field in required_fields:
        assert field in frontmatter, f"Missing required field: {field}"


def assert_valid_task_state(state: Dict[str, Any]):
    """Helper to assert task state structure is valid."""
    required_fields = ["project_id", "name", "created_at", "tasks"]
    for field in required_fields:
        assert field in state, f"Missing required field: {field}"

    assert isinstance(state["tasks"], dict), "tasks must be a dictionary"

    for task_id, task in state["tasks"].items():
        task_required = ["title", "status", "created_at", "project_id"]
        for field in task_required:
            assert field in task, f"Task {task_id} missing field: {field}"

        # Validate status flow
        valid_statuses = ["todo", "doing", "review", "done"]
        assert task["status"] in valid_statuses, f"Invalid status: {task['status']}"


def assert_valid_domain_selection(selection: Dict[str, Any]):
    """Helper to assert domain selection structure is valid."""
    required_fields = ["primary", "collaborators", "strategy"]
    for field in required_fields:
        assert field in selection, f"Missing required field: {field}"

    assert isinstance(selection["collaborators"], list), "collaborators must be a list"

    valid_strategies = ["parallel", "sequential"]
    assert selection["strategy"] in valid_strategies, f"Invalid strategy: {selection['strategy']}"
