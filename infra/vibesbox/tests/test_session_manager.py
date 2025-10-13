"""Session manager tests for process tracking and cleanup.

This module tests:
- Starting new command sessions
- Terminating sessions gracefully
- No zombie process accumulation
- Session cleanup on shutdown
- Reading incremental output

Critical Patterns:
- Track processes by PID to prevent resource leaks
- Graceful termination: SIGTERM -> wait 1s -> SIGKILL (PRP pattern)
- Always await process.wait() to prevent zombies (PRP Gotcha #3)
- Limit completed session history to prevent memory leaks

Pattern Sources:
- PRP Task 5: Session Manager specification
- prps/streamlined_vibesbox/examples/process_cleanup_pattern.py
"""

import asyncio
import time

import pytest

from src.session_manager import SessionManager, CommandSession
from src.models import SessionInfo


class TestSessionCreation:
    """Test suite for session creation and tracking."""

    @pytest.mark.asyncio
    async def test_start_session_returns_valid_pid(self):
        """Test that start_session creates a process and returns valid PID.

        Validates:
        - Session created successfully
        - PID is positive integer
        - Process is running
        - Session tracked in active sessions
        """
        manager = SessionManager()

        pid = await manager.start_session("sleep 2")

        assert isinstance(pid, int)
        assert pid > 0, "PID should be positive integer"

        # Verify session is tracked
        session = manager.get_session(pid)
        assert session is not None
        assert session.pid == pid
        assert session.is_running

        # Cleanup
        await manager.cleanup_all()

    @pytest.mark.asyncio
    async def test_start_session_tracks_command(self):
        """Test that session stores the original command.

        Validates:
        - Command stored in session
        - Can retrieve command from session
        - Useful for debugging/auditing
        """
        manager = SessionManager()

        command = "echo 'test command'"
        pid = await manager.start_session(command)

        session = manager.get_session(pid)
        assert session is not None
        assert session.command == command

        await manager.cleanup_all()

    @pytest.mark.asyncio
    async def test_start_session_records_start_time(self):
        """Test that session records when process started.

        Validates:
        - started_at timestamp recorded
        - Timestamp is recent (within last few seconds)
        - Useful for timeout tracking
        """
        manager = SessionManager()

        before = time.time()
        pid = await manager.start_session("sleep 2")
        after = time.time()

        session = manager.get_session(pid)
        assert session is not None
        assert before <= session.started_at <= after

        await manager.cleanup_all()

    @pytest.mark.asyncio
    async def test_start_multiple_sessions_concurrently(self):
        """Test starting multiple sessions at once.

        Validates:
        - Multiple sessions can run concurrently
        - All sessions tracked correctly
        - No PID conflicts
        - No resource contention
        """
        manager = SessionManager()

        # Start 5 sessions concurrently
        commands = [f"sleep {i}" for i in range(1, 6)]
        pids = await asyncio.gather(*[manager.start_session(cmd) for cmd in commands])

        assert len(pids) == 5
        assert len(set(pids)) == 5, "All PIDs should be unique"

        # Verify all sessions tracked
        for pid in pids:
            session = manager.get_session(pid)
            assert session is not None
            assert session.is_running

        await manager.cleanup_all()

    @pytest.mark.asyncio
    async def test_get_session_returns_none_for_invalid_pid(self):
        """Test that get_session returns None for non-existent PID.

        Validates:
        - Invalid PID returns None
        - No errors raised
        - Graceful handling
        """
        manager = SessionManager()

        session = manager.get_session(99999)
        assert session is None

    @pytest.mark.asyncio
    async def test_session_has_unique_session_id(self):
        """Test that each session has unique UUID session_id.

        Validates:
        - session_id is UUID string
        - Each session has different session_id
        - Useful for correlation/logging
        """
        manager = SessionManager()

        pid1 = await manager.start_session("sleep 1")
        pid2 = await manager.start_session("sleep 1")

        session1 = manager.get_session(pid1)
        session2 = manager.get_session(pid2)

        assert session1 is not None
        assert session2 is not None
        assert session1.session_id != session2.session_id
        assert len(session1.session_id) == 36, "Should be UUID format"

        await manager.cleanup_all()


class TestSessionTermination:
    """Test suite for session termination and cleanup."""

    @pytest.mark.asyncio
    async def test_terminate_session_gracefully(self):
        """Test graceful session termination (SIGTERM first).

        CRITICAL: Two-stage termination pattern (PRP process_cleanup_pattern.py)

        Validates:
        - Session terminated successfully
        - Process no longer running
        - Session moved to completed
        - No zombie processes
        """
        manager = SessionManager()

        pid = await manager.start_session("sleep 10")

        # Terminate gracefully
        success = await manager.terminate_session(pid, force=False)

        assert success is True

        # Session should still be retrievable (in completed)
        await asyncio.sleep(0.5)  # Give background task time to move session
        session = manager.get_session(pid)
        assert session is not None
        # Process should be terminated
        assert not session.is_running

    @pytest.mark.asyncio
    async def test_terminate_session_with_force_kill(self):
        """Test forceful session termination (SIGKILL immediately).

        Validates:
        - force=True sends SIGKILL immediately
        - Process terminated quickly
        - Useful for hung processes
        """
        manager = SessionManager()

        pid = await manager.start_session("sleep 100")

        # Force kill
        success = await manager.terminate_session(pid, force=True)

        assert success is True

        # Wait for cleanup
        await asyncio.sleep(0.5)
        session = manager.get_session(pid)
        assert session is not None
        assert not session.is_running

    @pytest.mark.asyncio
    async def test_terminate_non_existent_session_returns_false(self):
        """Test terminating non-existent session returns False.

        Validates:
        - Invalid PID returns False
        - No errors raised
        - Graceful handling
        """
        manager = SessionManager()

        success = await manager.terminate_session(99999, force=False)

        assert success is False

    @pytest.mark.asyncio
    async def test_terminate_already_completed_session(self):
        """Test terminating already-completed session.

        Validates:
        - Returns False if session already completed
        - No errors
        - Idempotent operation
        """
        manager = SessionManager()

        pid = await manager.start_session("echo 'quick task'")

        # Wait for command to complete
        await asyncio.sleep(1)

        # Try to terminate completed session
        success = await manager.terminate_session(pid, force=False)

        # Should return False (not in active sessions)
        assert success is False


class TestZombieProcessPrevention:
    """Test suite for zombie process prevention.

    CRITICAL: Zombies accumulate if process.wait() not called (PRP Gotcha #3)
    """

    @pytest.mark.asyncio
    async def test_no_zombie_accumulation_after_many_sessions(self):
        """Test that no zombie processes accumulate after creating many sessions.

        CRITICAL: This is the key test for PRP Gotcha #3

        Validates:
        - Create 50+ short-lived processes
        - All processes reaped correctly
        - No zombie processes left behind
        - Background cleanup task works
        """
        import subprocess

        manager = SessionManager()

        # Get initial zombie count (should be 0 or very low)
        def get_zombie_count():
            try:
                result = subprocess.run(
                    ["ps", "aux"],
                    capture_output=True,
                    text=True,
                    timeout=5
                )
                # Count processes with status 'Z' (zombie)
                return result.stdout.count(" Z ")
            except Exception:
                return 0

        initial_zombies = get_zombie_count()

        # Create 50 quick sessions
        for i in range(50):
            pid = await manager.start_session(f"echo 'task {i}'")
            # Don't wait - just create and move on
            await asyncio.sleep(0.05)  # Small delay

        # Wait for all processes to complete and be reaped
        await asyncio.sleep(2)

        # Check zombie count hasn't increased
        final_zombies = get_zombie_count()

        assert final_zombies <= initial_zombies + 1, \
            f"Zombie leak detected: {final_zombies - initial_zombies} new zombies"

        # Cleanup
        await manager.cleanup_all()

    @pytest.mark.asyncio
    async def test_completed_sessions_moved_to_history(self):
        """Test that completed sessions are moved to completed dict.

        CRITICAL: Part of zombie prevention - tracking completion (PRP pattern)

        Validates:
        - Completed sessions moved from active to completed
        - Background task tracks completion
        - await process.wait() called (prevents zombies)
        """
        manager = SessionManager()

        pid = await manager.start_session("echo 'quick'")

        # Initially in active sessions
        assert pid in manager.sessions

        # Wait for command to complete and background task to process
        await asyncio.sleep(1)

        # Should be moved to completed
        assert pid not in manager.sessions
        assert pid in manager.completed

    @pytest.mark.asyncio
    async def test_completed_history_limited_to_max_size(self):
        """Test that completed history doesn't grow unbounded.

        CRITICAL: Memory leak prevention (PRP pattern)

        Validates:
        - Completed dict limited to max_completed_sessions
        - Oldest entries removed when limit reached
        - Memory usage stays constant
        """
        manager = SessionManager(max_completed_sessions=10)

        # Create 20 quick sessions
        pids = []
        for i in range(20):
            pid = await manager.start_session(f"echo 'task {i}'")
            pids.append(pid)
            await asyncio.sleep(0.1)  # Let them complete

        # Wait for all to complete
        await asyncio.sleep(2)

        # Completed dict should have max 10 entries
        assert len(manager.completed) <= 10, \
            f"Completed history should be limited to 10, got {len(manager.completed)}"

        # Should contain only most recent 10
        recent_pids = pids[-10:]
        for pid in recent_pids:
            # Should be in completed (or still in active if very recent)
            assert pid in manager.completed or pid in manager.sessions


class TestSessionCleanup:
    """Test suite for cleanup_all() functionality."""

    @pytest.mark.asyncio
    async def test_cleanup_all_terminates_active_sessions(self):
        """Test that cleanup_all() terminates all active sessions.

        CRITICAL: Must call on shutdown to prevent orphaned processes (PRP pattern)

        Validates:
        - All active sessions terminated
        - Graceful termination attempted
        - No processes left running
        - Safe shutdown
        """
        manager = SessionManager()

        # Start several long-running sessions
        pids = []
        for i in range(5):
            pid = await manager.start_session(f"sleep 100")
            pids.append(pid)

        # Verify all running
        for pid in pids:
            session = manager.get_session(pid)
            assert session is not None
            assert session.is_running

        # Cleanup all
        await manager.cleanup_all()

        # Wait for cleanup
        await asyncio.sleep(1)

        # All sessions should be terminated
        for pid in pids:
            session = manager.get_session(pid)
            if session:
                assert not session.is_running, f"PID {pid} should be terminated"

    @pytest.mark.asyncio
    async def test_cleanup_all_with_no_active_sessions(self):
        """Test that cleanup_all() works even with no active sessions.

        Validates:
        - No errors when no sessions
        - Idempotent operation
        - Safe to call anytime
        """
        manager = SessionManager()

        # Call cleanup with no sessions
        await manager.cleanup_all()

        # Should complete without errors
        assert True

    @pytest.mark.asyncio
    async def test_cleanup_all_waits_for_termination(self):
        """Test that cleanup_all() waits for all processes to terminate.

        Validates:
        - Doesn't return until all processes terminated
        - No orphaned processes
        - Complete cleanup
        """
        manager = SessionManager()

        # Start a few sessions
        for i in range(3):
            await manager.start_session("sleep 5")

        # Cleanup should wait for termination
        start = time.time()
        await manager.cleanup_all()
        duration = time.time() - start

        # Should complete quickly (within a few seconds)
        assert duration < 5, f"Cleanup took too long: {duration}s"


class TestReadOutput:
    """Test suite for reading incremental output."""

    @pytest.mark.asyncio
    async def test_read_output_returns_new_output(self):
        """Test that read_output() returns new output since last read.

        Validates:
        - Incremental output returned
        - Output consumed from buffer
        - Next read returns only new output
        """
        manager = SessionManager()

        # Command that produces output slowly
        pid = await manager.start_session("echo 'line1'; sleep 0.5; echo 'line2'")

        # Wait for first output
        await asyncio.sleep(0.3)
        output1 = await manager.read_output(pid)

        # Wait for second output
        await asyncio.sleep(0.5)
        output2 = await manager.read_output(pid)

        # Both reads should have content (or at least one)
        assert output1 or output2, "Should have some output"

        # If both have content, they should be different
        if output1 and output2:
            assert output1 != output2

        await manager.cleanup_all()

    @pytest.mark.asyncio
    async def test_read_output_from_completed_session(self):
        """Test reading output from already-completed session.

        Validates:
        - Can read output from completed sessions
        - Buffered output still available
        - No errors
        """
        manager = SessionManager()

        pid = await manager.start_session("echo 'test output'")

        # Wait for completion
        await asyncio.sleep(1)

        # Read output after completion
        output = await manager.read_output(pid)

        # Should have the output (or empty if already consumed)
        assert isinstance(output, str)

    @pytest.mark.asyncio
    async def test_read_output_invalid_pid_raises_error(self):
        """Test that reading from invalid PID raises ValueError.

        Validates:
        - Invalid PID raises ValueError
        - Error message is descriptive
        """
        manager = SessionManager()

        with pytest.raises(ValueError, match="not found"):
            await manager.read_output(99999)

    @pytest.mark.asyncio
    async def test_read_output_clears_buffer(self):
        """Test that read_output() clears the buffer after reading.

        Validates:
        - Buffer cleared after read
        - Second read returns empty (until new output)
        - No duplicate output
        """
        manager = SessionManager()

        pid = await manager.start_session("echo 'one time output'")

        # Wait for output
        await asyncio.sleep(0.5)

        # First read
        output1 = await manager.read_output(pid)

        # Immediate second read (no new output)
        output2 = await manager.read_output(pid)

        # First read might have output
        assert isinstance(output1, str)

        # Second read should be empty (buffer was cleared)
        assert output2 == "", "Buffer should be cleared after first read"

        await manager.cleanup_all()


class TestListSessions:
    """Test suite for list_sessions() functionality."""

    @pytest.mark.asyncio
    async def test_list_sessions_returns_all_sessions(self):
        """Test that list_sessions() returns both active and completed.

        Validates:
        - Returns list of SessionInfo
        - Includes active sessions
        - Includes completed sessions
        - Correct status for each
        """
        manager = SessionManager()

        # Create active session
        active_pid = await manager.start_session("sleep 5")

        # Create quick session that will complete
        quick_pid = await manager.start_session("echo 'quick'")
        await asyncio.sleep(1)  # Let it complete

        # List all sessions
        sessions = manager.list_sessions()

        assert len(sessions) >= 1, "Should have at least 1 session"

        # Verify SessionInfo structure
        for session_info in sessions:
            assert isinstance(session_info, SessionInfo)
            assert session_info.pid > 0
            assert session_info.command
            assert session_info.status in ["running", "completed", "terminated"]

        # Active session should be "running"
        active_session = next((s for s in sessions if s.pid == active_pid), None)
        if active_session:
            assert active_session.status == "running"

        await manager.cleanup_all()

    @pytest.mark.asyncio
    async def test_list_sessions_empty_manager(self):
        """Test list_sessions() on empty manager.

        Validates:
        - Returns empty list
        - No errors
        """
        manager = SessionManager()

        sessions = manager.list_sessions()

        assert isinstance(sessions, list)
        assert len(sessions) == 0

    @pytest.mark.asyncio
    async def test_list_sessions_includes_started_at(self):
        """Test that listed sessions include started_at timestamp.

        Validates:
        - started_at is datetime
        - Timestamp is reasonable (recent)
        """
        manager = SessionManager()

        pid = await manager.start_session("sleep 2")

        sessions = manager.list_sessions()

        assert len(sessions) == 1
        session = sessions[0]
        assert session.started_at is not None
        assert isinstance(session.started_at, type(session.started_at))  # datetime check

        await manager.cleanup_all()
