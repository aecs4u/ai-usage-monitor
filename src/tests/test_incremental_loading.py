"""Tests for incremental loading functionality."""

import json
import tempfile
import time
from datetime import datetime, timezone
from pathlib import Path

import pytest

from ai_usage_monitor.core.models import CostMode
from ai_usage_monitor.data.reader import (
    load_usage_entries_incremental,
)
from ai_usage_monitor.monitoring.data_manager import DataManager
from ai_usage_monitor.monitoring.file_tracker import FileState, FileStateTracker


@pytest.fixture
def temp_data_dir():
    """Create a temporary directory for test data."""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield Path(tmpdir)


@pytest.fixture
def sample_jsonl_entry():
    """Create a sample JSONL entry."""
    return {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "model": "claude-sonnet-4",
        "input_tokens": 100,
        "output_tokens": 50,
        "cache_creation_input_tokens": 0,
        "cache_read_input_tokens": 0,
        "cost_usd": 0.001,
        "message_id": "msg_test123",
        "request_id": "req_test123",
    }


def write_jsonl_file(file_path: Path, entries: list):
    """Write entries to a JSONL file."""
    with open(file_path, "w", encoding="utf-8") as f:
        for entry in entries:
            f.write(json.dumps(entry) + "\n")


def append_to_jsonl_file(file_path: Path, entries: list):
    """Append entries to a JSONL file."""
    with open(file_path, "a", encoding="utf-8") as f:
        for entry in entries:
            f.write(json.dumps(entry) + "\n")


class TestFileStateTracker:
    """Tests for FileStateTracker class."""

    def test_new_file_detected(self, temp_data_dir):
        """Test that new files are detected and returned with offset 0."""
        tracker = FileStateTracker()

        file1 = temp_data_dir / "test1.jsonl"
        file1.touch()

        files_to_read = tracker.get_files_to_read([file1])

        assert len(files_to_read) == 1
        assert files_to_read[0] == (file1, 0)

    def test_unchanged_file_skipped(self, temp_data_dir):
        """Test that unchanged files are not returned."""
        tracker = FileStateTracker()

        file1 = temp_data_dir / "test1.jsonl"
        file1.touch()

        # First read: detect as new
        files_to_read = tracker.get_files_to_read([file1])
        assert len(files_to_read) == 1

        # Update tracker state
        tracker.update_file_state(file1, file1.stat().st_size)

        # Second read: should be skipped (no changes)
        files_to_read = tracker.get_files_to_read([file1])
        assert len(files_to_read) == 0

    def test_modified_file_detected(self, temp_data_dir, sample_jsonl_entry):
        """Test that modified files are detected with correct offset."""
        tracker = FileStateTracker()

        file1 = temp_data_dir / "test1.jsonl"
        write_jsonl_file(file1, [sample_jsonl_entry])

        # First read
        files_to_read = tracker.get_files_to_read([file1])
        initial_size = file1.stat().st_size
        tracker.update_file_state(file1, initial_size)

        # Modify file by appending
        time.sleep(0.01)  # Ensure mtime changes
        append_to_jsonl_file(file1, [sample_jsonl_entry])

        # Second read: should detect change
        files_to_read = tracker.get_files_to_read([file1])
        assert len(files_to_read) == 1
        assert files_to_read[0] == (file1, initial_size)

    def test_file_state_has_changed(self, temp_data_dir):
        """Test FileState.has_changed() method."""
        file1 = temp_data_dir / "test1.jsonl"
        file1.touch()

        stat = file1.stat()
        state = FileState(
            path=file1, mtime=stat.st_mtime, size=stat.st_size, offset=0
        )

        # Initially unchanged
        assert not state.has_changed()

        # Modify file
        time.sleep(0.01)
        file1.write_text("new content")

        # Should detect change
        assert state.has_changed()

    def test_clear_tracker(self, temp_data_dir):
        """Test that clearing tracker resets all state."""
        tracker = FileStateTracker()

        file1 = temp_data_dir / "test1.jsonl"
        file1.touch()

        # Track a file
        tracker.get_files_to_read([file1])
        tracker.update_file_state(file1, 100)

        assert tracker.is_tracking(file1)

        # Clear tracker
        tracker.clear()

        # File should not be tracked anymore
        assert not tracker.is_tracking(file1)

    def test_remove_file(self, temp_data_dir):
        """Test removing a file from tracking."""
        tracker = FileStateTracker()

        file1 = temp_data_dir / "test1.jsonl"
        file1.touch()

        # Track a file
        tracker.get_files_to_read([file1])
        tracker.update_file_state(file1, 100)

        assert tracker.is_tracking(file1)

        # Remove file from tracking
        tracker.remove_file(file1)

        assert not tracker.is_tracking(file1)

    def test_get_tracked_files(self, temp_data_dir):
        """Test getting list of tracked files."""
        tracker = FileStateTracker()

        file1 = temp_data_dir / "test1.jsonl"
        file2 = temp_data_dir / "test2.jsonl"
        file1.touch()
        file2.touch()

        # Track files
        tracker.get_files_to_read([file1, file2])
        tracker.update_file_state(file1, 100)
        tracker.update_file_state(file2, 200)

        tracked = tracker.get_tracked_files()
        assert len(tracked) == 2
        assert file1 in tracked
        assert file2 in tracked


class TestIncrementalLoading:
    """Tests for incremental loading functionality."""

    def test_load_new_entries_only(self, temp_data_dir, sample_jsonl_entry):
        """Test that only new entries are loaded on subsequent reads."""
        file1 = temp_data_dir / "test1.jsonl"

        # Write initial entries
        entry1 = {**sample_jsonl_entry, "message_id": "msg_001", "request_id": "req_001"}
        write_jsonl_file(file1, [entry1])

        # First load: should get 1 entry
        entries1, tracker1 = load_usage_entries_incremental(
            data_path=str(temp_data_dir), mode=CostMode.AUTO
        )
        assert len(entries1) == 1
        assert entries1[0].message_id == "msg_001"

        # Second load without changes: should get 0 entries
        entries2, tracker2 = load_usage_entries_incremental(
            data_path=str(temp_data_dir), file_tracker=tracker1, mode=CostMode.AUTO
        )
        assert len(entries2) == 0

        # Append new entry
        time.sleep(0.01)
        entry2 = {**sample_jsonl_entry, "message_id": "msg_002", "request_id": "req_002"}
        append_to_jsonl_file(file1, [entry2])

        # Third load: should get only the new entry
        entries3, tracker3 = load_usage_entries_incremental(
            data_path=str(temp_data_dir), file_tracker=tracker2, mode=CostMode.AUTO
        )
        assert len(entries3) == 1
        assert entries3[0].message_id == "msg_002"

    def test_load_multiple_files(self, temp_data_dir, sample_jsonl_entry):
        """Test incremental loading with multiple files."""
        file1 = temp_data_dir / "test1.jsonl"
        file2 = temp_data_dir / "test2.jsonl"

        entry1 = {**sample_jsonl_entry, "message_id": "msg_001", "request_id": "req_001"}
        entry2 = {**sample_jsonl_entry, "message_id": "msg_002", "request_id": "req_002"}

        write_jsonl_file(file1, [entry1])
        write_jsonl_file(file2, [entry2])

        # First load: should get 2 entries
        entries1, tracker1 = load_usage_entries_incremental(
            data_path=str(temp_data_dir), mode=CostMode.AUTO
        )
        assert len(entries1) == 2

        # Modify only file2
        time.sleep(0.01)
        entry3 = {**sample_jsonl_entry, "message_id": "msg_003", "request_id": "req_003"}
        append_to_jsonl_file(file2, [entry3])

        # Second load: should only read from file2
        entries2, tracker2 = load_usage_entries_incremental(
            data_path=str(temp_data_dir), file_tracker=tracker1, mode=CostMode.AUTO
        )
        assert len(entries2) == 1
        assert entries2[0].message_id == "msg_003"

    def test_empty_directory(self, temp_data_dir):
        """Test incremental loading with empty directory."""
        entries, tracker = load_usage_entries_incremental(
            data_path=str(temp_data_dir), mode=CostMode.AUTO
        )
        assert len(entries) == 0
        assert tracker is not None


class TestDataManagerIncremental:
    """Tests for DataManager incremental loading integration."""

    def test_incremental_mode_enabled_by_default(self):
        """Test that incremental mode is enabled by default."""
        manager = DataManager(data_path="~/test")
        assert manager.use_incremental is True

    def test_incremental_mode_disabled(self):
        """Test that incremental mode can be disabled."""
        manager = DataManager(data_path="~/test", use_incremental=False)
        assert manager.use_incremental is False
        assert manager._file_tracker is None

    def test_should_use_incremental_with_adapter(self):
        """Test that incremental mode is not used with adapters."""
        from unittest.mock import MagicMock

        mock_adapter = MagicMock()

        manager = DataManager(
            data_path="~/test", adapter=mock_adapter, use_incremental=True
        )

        # Should not use incremental with adapter
        assert not manager._should_use_incremental()

    def test_should_use_incremental_without_data_path(self):
        """Test that incremental mode requires data_path."""
        manager = DataManager(data_path=None, use_incremental=True)

        # Should not use incremental without data_path
        assert not manager._should_use_incremental()

    def test_cache_invalidation_clears_tracker(self, temp_data_dir):
        """Test that cache invalidation also clears file tracker."""
        manager = DataManager(data_path=str(temp_data_dir), use_incremental=True)

        # Simulate some tracker state
        if manager._file_tracker:
            file1 = temp_data_dir / "test1.jsonl"
            file1.touch()
            manager._file_tracker.update_file_state(file1, 100)
            assert manager._file_tracker.is_tracking(file1)

        # Invalidate cache
        manager.invalidate_cache()

        # Tracker should be cleared
        if manager._file_tracker:
            assert not manager._file_tracker.is_tracking(file1)

    def test_check_files_changed_no_tracker(self):
        """Test file change check without tracker."""
        manager = DataManager(data_path="~/test", use_incremental=False)
        result = manager._check_files_changed()
        assert result is True  # Default to changed when no tracker

    def test_check_files_changed_no_data_path(self):
        """Test file change check without data_path."""
        manager = DataManager(data_path=None, use_incremental=True)
        result = manager._check_files_changed()
        assert result is True  # Default to changed when no data_path

    def test_check_files_changed_empty_directory(self, temp_data_dir):
        """Test file change check with empty directory."""
        manager = DataManager(data_path=str(temp_data_dir), use_incremental=True)
        result = manager._check_files_changed()
        assert result is False  # No files to read

    def test_update_file_tracker_no_tracker(self):
        """Test update file tracker without tracker (should not crash)."""
        manager = DataManager(data_path="~/test", use_incremental=False)
        manager._update_file_tracker()  # Should not raise

    def test_update_file_tracker_no_data_path(self):
        """Test update file tracker without data_path (should not crash)."""
        manager = DataManager(data_path=None, use_incremental=True)
        manager._update_file_tracker()  # Should not raise

    def test_update_file_tracker_empty_directory(self, temp_data_dir):
        """Test update file tracker with empty directory."""
        manager = DataManager(data_path=str(temp_data_dir), use_incremental=True)
        manager._update_file_tracker()  # Should not raise


class TestIncrementalLoadingPerformance:
    """Performance-related tests for incremental loading."""

    def test_skip_unchanged_files_performance(
        self, temp_data_dir, sample_jsonl_entry
    ):
        """Test that unchanged files are truly skipped (performance)."""
        # Create a large file
        file1 = temp_data_dir / "large.jsonl"
        entries = [
            {
                **sample_jsonl_entry,
                "message_id": f"msg_{i:05d}",
                "request_id": f"req_{i:05d}",
            }
            for i in range(1000)
        ]
        write_jsonl_file(file1, entries)

        # First load
        start = time.time()
        entries1, tracker1 = load_usage_entries_incremental(
            data_path=str(temp_data_dir), mode=CostMode.AUTO
        )
        first_load_time = time.time() - start

        assert len(entries1) == 1000

        # Second load (no changes)
        start = time.time()
        entries2, tracker2 = load_usage_entries_incremental(
            data_path=str(temp_data_dir), file_tracker=tracker1, mode=CostMode.AUTO
        )
        second_load_time = time.time() - start

        assert len(entries2) == 0
        # Second load should be significantly faster
        assert second_load_time < first_load_time * 0.1  # At least 10x faster

    def test_incremental_read_performance(self, temp_data_dir, sample_jsonl_entry):
        """Test that incremental reads are faster than full reads."""
        file1 = temp_data_dir / "large.jsonl"

        # Create initial large file
        initial_entries = [
            {
                **sample_jsonl_entry,
                "message_id": f"msg_{i:05d}",
                "request_id": f"req_{i:05d}",
            }
            for i in range(1000)
        ]
        write_jsonl_file(file1, initial_entries)

        # First load
        entries1, tracker1 = load_usage_entries_incremental(
            data_path=str(temp_data_dir), mode=CostMode.AUTO
        )
        assert len(entries1) == 1000

        # Append a small number of entries
        time.sleep(0.01)
        new_entries = [
            {
                **sample_jsonl_entry,
                "message_id": f"msg_{i:05d}",
                "request_id": f"req_{i:05d}",
            }
            for i in range(1000, 1010)
        ]
        append_to_jsonl_file(file1, new_entries)

        # Incremental load (should read only new entries)
        start = time.time()
        entries2, tracker2 = load_usage_entries_incremental(
            data_path=str(temp_data_dir), file_tracker=tracker1, mode=CostMode.AUTO
        )
        incremental_time = time.time() - start

        assert len(entries2) == 10

        # Full reload for comparison
        from ai_usage_monitor.data.reader import load_usage_entries

        start = time.time()
        entries3, _ = load_usage_entries(
            data_path=str(temp_data_dir), mode=CostMode.AUTO
        )
        full_load_time = time.time() - start

        assert len(entries3) == 1010

        # Incremental should be faster than full reload
        assert incremental_time < full_load_time
