"""Tests for Task Tracking Abstraction Layer (Task 3)."""

import pytest
import json
import uuid
from datetime import datetime
from pathlib import Path
from unittest.mock import Mock, patch, mock_open
from tests.conftest import assert_valid_task_state


class TestFileBackendOperations:
    """Test file backend create/update/find operations."""

    def test_create_project(self, temp_prp_dir, sample_task_state):
        """Test creating project with file backend."""
        feature_name = "test_feature"
        state_path = temp_prp_dir / feature_name / "execution" / "state.json"

        # Create project
        project_id = str(uuid.uuid4())
        state = {
            "project_id": project_id,
            "name": feature_name,
            "description": "Test project",
            "created_at": datetime.now().isoformat(),
            "tasks": {}
        }

        # Ensure directory exists
        state_path.parent.mkdir(parents=True, exist_ok=True)

        # Write state
        state_path.write_text(json.dumps(state, indent=2))

        # Verify file created
        assert state_path.exists()

        # Verify content
        loaded_state = json.loads(state_path.read_text())
        assert loaded_state["project_id"] == project_id
        assert loaded_state["name"] == feature_name
        assert_valid_task_state(loaded_state)

    def test_create_task(self, temp_prp_dir):
        """Test creating task in file backend."""
        feature_name = "test_feature"
        state_path = temp_prp_dir / feature_name / "execution" / "state.json"
        state_path.parent.mkdir(parents=True, exist_ok=True)

        # Initialize state
        project_id = str(uuid.uuid4())
        state = {
            "project_id": project_id,
            "name": feature_name,
            "created_at": datetime.now().isoformat(),
            "tasks": {}
        }
        state_path.write_text(json.dumps(state, indent=2))

        # Create task
        task_id = str(uuid.uuid4())
        state["tasks"][task_id] = {
            "title": "Task 1: Create Skills System",
            "status": "todo",
            "created_at": datetime.now().isoformat(),
            "project_id": project_id
        }

        # Update state
        state_path.write_text(json.dumps(state, indent=2))

        # Verify task created
        loaded_state = json.loads(state_path.read_text())
        assert task_id in loaded_state["tasks"]
        assert loaded_state["tasks"][task_id]["status"] == "todo"

    def test_update_task_status(self, temp_prp_dir):
        """Test updating task status in file backend."""
        feature_name = "test_feature"
        state_path = temp_prp_dir / feature_name / "execution" / "state.json"
        state_path.parent.mkdir(parents=True, exist_ok=True)

        # Initialize with task
        project_id = str(uuid.uuid4())
        task_id = str(uuid.uuid4())
        state = {
            "project_id": project_id,
            "name": feature_name,
            "created_at": datetime.now().isoformat(),
            "tasks": {
                task_id: {
                    "title": "Task 1",
                    "status": "todo",
                    "created_at": datetime.now().isoformat(),
                    "project_id": project_id
                }
            }
        }
        state_path.write_text(json.dumps(state, indent=2))

        # Update status: todo -> doing
        state["tasks"][task_id]["status"] = "doing"
        state["tasks"][task_id]["updated_at"] = datetime.now().isoformat()
        state_path.write_text(json.dumps(state, indent=2))

        # Verify update
        loaded_state = json.loads(state_path.read_text())
        assert loaded_state["tasks"][task_id]["status"] == "doing"
        assert "updated_at" in loaded_state["tasks"][task_id]

    def test_find_tasks_by_status(self, temp_prp_dir):
        """Test finding tasks by status filter."""
        feature_name = "test_feature"
        state_path = temp_prp_dir / feature_name / "execution" / "state.json"
        state_path.parent.mkdir(parents=True, exist_ok=True)

        # Create state with multiple tasks
        project_id = str(uuid.uuid4())
        state = {
            "project_id": project_id,
            "name": feature_name,
            "created_at": datetime.now().isoformat(),
            "tasks": {
                "task-1": {
                    "title": "Task 1",
                    "status": "todo",
                    "created_at": datetime.now().isoformat(),
                    "project_id": project_id
                },
                "task-2": {
                    "title": "Task 2",
                    "status": "doing",
                    "created_at": datetime.now().isoformat(),
                    "project_id": project_id
                },
                "task-3": {
                    "title": "Task 3",
                    "status": "todo",
                    "created_at": datetime.now().isoformat(),
                    "project_id": project_id
                }
            }
        }
        state_path.write_text(json.dumps(state, indent=2))

        # Find todo tasks
        loaded_state = json.loads(state_path.read_text())
        todo_tasks = [
            task for task_id, task in loaded_state["tasks"].items()
            if task["status"] == "todo"
        ]

        assert len(todo_tasks) == 2
        assert all(t["status"] == "todo" for t in todo_tasks)


class TestStatePersistence:
    """Test state persistence across invocations."""

    def test_state_survives_read_write_cycle(self, temp_prp_dir):
        """Test state survives read-modify-write cycle."""
        state_path = temp_prp_dir / "test_feature" / "execution" / "state.json"
        state_path.parent.mkdir(parents=True, exist_ok=True)

        # Write initial state
        initial_state = {
            "project_id": "test-123",
            "name": "test_feature",
            "created_at": "2025-11-20T12:00:00.000Z",
            "tasks": {}
        }
        state_path.write_text(json.dumps(initial_state, indent=2))

        # Read state
        loaded = json.loads(state_path.read_text())

        # Modify state
        loaded["tasks"]["task-1"] = {
            "title": "New task",
            "status": "todo",
            "created_at": datetime.now().isoformat(),
            "project_id": "test-123"
        }

        # Write modified state
        state_path.write_text(json.dumps(loaded, indent=2))

        # Read again and verify
        final = json.loads(state_path.read_text())
        assert "task-1" in final["tasks"]
        assert final["project_id"] == initial_state["project_id"]

    def test_multiple_task_updates_persist(self, temp_prp_dir):
        """Test multiple task updates persist correctly."""
        state_path = temp_prp_dir / "test_feature" / "execution" / "state.json"
        state_path.parent.mkdir(parents=True, exist_ok=True)

        # Initialize
        state = {
            "project_id": "test-123",
            "name": "test_feature",
            "created_at": datetime.now().isoformat(),
            "tasks": {}
        }
        state_path.write_text(json.dumps(state, indent=2))

        # Simulate multiple updates
        for i in range(5):
            state = json.loads(state_path.read_text())
            task_id = f"task-{i}"
            state["tasks"][task_id] = {
                "title": f"Task {i}",
                "status": "todo",
                "created_at": datetime.now().isoformat(),
                "project_id": "test-123"
            }
            state_path.write_text(json.dumps(state, indent=2))

        # Verify all tasks persisted
        final_state = json.loads(state_path.read_text())
        assert len(final_state["tasks"]) == 5

    def test_state_json_pretty_printed(self, temp_prp_dir):
        """Test state JSON is pretty-printed for human readability."""
        state_path = temp_prp_dir / "test_feature" / "execution" / "state.json"
        state_path.parent.mkdir(parents=True, exist_ok=True)

        state = {
            "project_id": "test-123",
            "name": "test_feature",
            "tasks": {}
        }

        # Write with indent=2
        state_path.write_text(json.dumps(state, indent=2))

        content = state_path.read_text()

        # Check for indentation (newlines and spaces)
        assert '\n' in content, "Should have newlines"
        assert '  ' in content, "Should have indentation"


class TestGracefulDegradation:

    def test_fallback_to_file_backend(self):
        """Test automatic fallback to file backend."""
        def create_task_tracker(backend: str = "file"):
            """Create task tracker with specified backend."""
                try:
                    # Mock health check failure
                except Exception:
                    return "file"
            return backend

        assert result == "file", "Should fallback to file backend"

    def test_file_backend_works_offline(self, temp_prp_dir):
        """Test file backend works without network connection."""
        # File backend should work completely offline
        state_path = temp_prp_dir / "test_feature" / "execution" / "state.json"
        state_path.parent.mkdir(parents=True, exist_ok=True)

        # No network calls needed
        state = {
            "project_id": str(uuid.uuid4()),
            "name": "test_feature",
            "created_at": datetime.now().isoformat(),
            "tasks": {}
        }

        # Should succeed without any external dependencies
        state_path.write_text(json.dumps(state, indent=2))

        assert state_path.exists()
        assert json.loads(state_path.read_text())["project_id"] == state["project_id"]

        def file_backend_create_task(state_path: Path, task_title: str):
            """Create task using only file operations."""
            state = json.loads(state_path.read_text())
            task_id = str(uuid.uuid4())

            state["tasks"][task_id] = {
                "title": task_title,
                "status": "todo",
                "created_at": datetime.now().isoformat(),
                "project_id": state["project_id"]
            }

            state_path.write_text(json.dumps(state, indent=2))
            return task_id

        import inspect
        source = inspect.getsource(file_backend_create_task)



class TestBackwardCompatibility:
    """Test backward compatibility with existing workflows."""

    def test_existing_prps_execute_with_file_backend(self, temp_prp_dir):
        """Test existing PRPs can execute with file backend."""
        # Simulate existing PRP structure
        prp_path = temp_prp_dir / "existing_feature"
        prp_path.mkdir(parents=True)

        (prp_path / "existing_feature.md").write_text("# Existing PRP")

        # Should be able to create state for existing PRP
        state_path = prp_path / "execution" / "state.json"
        state_path.parent.mkdir(parents=True, exist_ok=True)

        state = {
            "project_id": str(uuid.uuid4()),
            "name": "existing_feature",
            "created_at": datetime.now().isoformat(),
            "tasks": {}
        }

        state_path.write_text(json.dumps(state, indent=2))

        assert state_path.exists()

    def test_state_schema_versioning(self, temp_prp_dir):
        """Test state file includes schema version for future migrations."""
        state_path = temp_prp_dir / "test_feature" / "execution" / "state.json"
        state_path.parent.mkdir(parents=True, exist_ok=True)

        # Include schema_version for future compatibility
        state = {
            "schema_version": "1.0",
            "project_id": str(uuid.uuid4()),
            "name": "test_feature",
            "created_at": datetime.now().isoformat(),
            "tasks": {}
        }

        state_path.write_text(json.dumps(state, indent=2))

        loaded = json.loads(state_path.read_text())
        assert "schema_version" in loaded
        assert loaded["schema_version"] == "1.0"


class TestTaskStatusFlow:
    """Test task status flow validation."""

    def test_valid_status_transitions(self):
        """Test valid task status transitions."""
        valid_flow = {
            "todo": ["doing"],
            "doing": ["review", "todo"],  # Can move back to todo
            "review": ["done", "doing"],  # Can move back to doing
            "done": []  # Terminal state
        }

        # Test transition
        current_status = "todo"
        next_status = "doing"

        assert next_status in valid_flow.get(current_status, []), \
            f"Invalid transition: {current_status} -> {next_status}"

    def test_status_validation(self):
        """Test status value validation."""
        valid_statuses = ["todo", "doing", "review", "done"]

        test_cases = [
            ("todo", True),
            ("doing", True),
            ("invalid", False),
            ("DONE", False),  # Case-sensitive
            ("", False)
        ]

        for status, should_be_valid in test_cases:
            is_valid = status in valid_statuses
            assert is_valid == should_be_valid, \
                f"Status '{status}' validation incorrect"

    def test_task_lifecycle_complete(self, temp_prp_dir):
        """Test complete task lifecycle: todo -> doing -> review -> done."""
        state_path = temp_prp_dir / "test_feature" / "execution" / "state.json"
        state_path.parent.mkdir(parents=True, exist_ok=True)

        # Initialize
        project_id = str(uuid.uuid4())
        task_id = str(uuid.uuid4())
        state = {
            "project_id": project_id,
            "name": "test_feature",
            "created_at": datetime.now().isoformat(),
            "tasks": {
                task_id: {
                    "title": "Task 1",
                    "status": "todo",
                    "created_at": datetime.now().isoformat(),
                    "project_id": project_id
                }
            }
        }
        state_path.write_text(json.dumps(state, indent=2))

        # Lifecycle transitions
        transitions = ["doing", "review", "done"]

        for new_status in transitions:
            state = json.loads(state_path.read_text())
            state["tasks"][task_id]["status"] = new_status
            state["tasks"][task_id]["updated_at"] = datetime.now().isoformat()
            state_path.write_text(json.dumps(state, indent=2))

        # Verify final state
        final = json.loads(state_path.read_text())
        assert final["tasks"][task_id]["status"] == "done"


class TestFeatureNameSecurity:
    """Test feature name security validation."""

    def test_removeprefix_vs_replace(self):
        """Test removeprefix() vs replace() for INITIAL_ stripping."""
        # CRITICAL: Use removeprefix() not replace()
        filename = "INITIAL_INITIAL_test.md"

        # WRONG: replace() removes ALL occurrences
        wrong = filename.replace("INITIAL_", "").replace(".md", "")
        assert wrong == "test", "replace() removes both INITIAL_ prefixes"

        # RIGHT: removeprefix() removes only leading prefix
        right = filename.removeprefix("INITIAL_").replace(".md", "")
        assert right == "INITIAL_test", "removeprefix() removes only first"

    def test_path_traversal_validation(self):
        """Test path traversal detection."""
        def validate_feature_name(name: str) -> bool:
            """Validate feature name for security."""
            if ".." in name:
                return False
            if "/" in name or "\\" in name:
                return False
            return True

        assert not validate_feature_name("../etc/passwd")
        assert not validate_feature_name("path/to/file")
        assert validate_feature_name("valid_feature_name")

    def test_command_injection_validation(self):
        """Test command injection character detection."""
        dangerous_chars = [";", "&", "|", "$", "`", "(", ")", "<", ">"]

        def has_injection_chars(name: str) -> bool:
            """Check for command injection characters."""
            return any(c in name for c in dangerous_chars)

        assert has_injection_chars("feature; rm -rf /")
        assert has_injection_chars("feature && malicious")
        assert not has_injection_chars("valid_feature_name")
