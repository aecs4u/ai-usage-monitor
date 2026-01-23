"""File state tracking for incremental data loading.

This module provides FileStateTracker for monitoring file modifications
and enabling efficient incremental reading of JSONL files during refreshes.
"""

import logging
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Tuple

logger = logging.getLogger(__name__)


@dataclass
class FileState:
    """Tracks the state of a monitored file.

    Attributes:
        path: Path to the file
        mtime: Last modification time (from stat)
        size: File size in bytes
        offset: Last read position in bytes
    """

    path: Path
    mtime: float
    size: int
    offset: int

    def has_changed(self) -> bool:
        """Check if the file has changed since last read.

        Returns:
            True if the file has been modified or grown in size.
        """
        try:
            stat = self.path.stat()
            # File changed if mtime is newer OR size changed
            return stat.st_mtime > self.mtime or stat.st_size != self.size
        except (FileNotFoundError, PermissionError, OSError) as e:
            logger.debug(f"Error checking file state for {self.path}: {e}")
            # If we can't stat the file, consider it changed to force re-read
            return True

    def update_from_stat(self, final_offset: int) -> None:
        """Update state after reading file.

        Args:
            final_offset: The byte offset after reading
        """
        try:
            stat = self.path.stat()
            self.mtime = stat.st_mtime
            self.size = stat.st_size
            self.offset = final_offset
        except (FileNotFoundError, PermissionError, OSError) as e:
            logger.warning(f"Failed to update file state for {self.path}: {e}")


class FileStateTracker:
    """Tracks file states for incremental reading.

    This class monitors JSONL files and determines which files need to be
    re-read based on modification time and size changes.

    Example:
        >>> tracker = FileStateTracker()
        >>> files_to_read = tracker.get_files_to_read(all_jsonl_files)
        >>> for file_path, start_offset in files_to_read:
        ...     entries = read_from_offset(file_path, start_offset)
        ...     tracker.update_file_state(file_path, final_offset)
    """

    def __init__(self) -> None:
        """Initialize the file state tracker."""
        self._file_states: Dict[str, FileState] = {}

    def get_files_to_read(
        self, all_files: List[Path]
    ) -> List[Tuple[Path, int]]:
        """Get list of files that need to be read with their start offsets.

        Args:
            all_files: List of all files to check

        Returns:
            List of (file_path, start_offset) tuples.
            - New files have offset=0 (read from beginning)
            - Changed files have offset=last_read_position
            - Unchanged files are not included
        """
        files_to_read: List[Tuple[Path, int]] = []

        for file_path in all_files:
            file_key = str(file_path)

            if file_key not in self._file_states:
                # New file: read from beginning
                files_to_read.append((file_path, 0))
                logger.debug(f"New file detected: {file_path}")
            else:
                # Check if file changed
                file_state = self._file_states[file_key]
                if file_state.has_changed():
                    # Changed file: read from last offset
                    start_offset = file_state.offset
                    files_to_read.append((file_path, start_offset))
                    logger.debug(
                        f"Changed file detected: {file_path} "
                        f"(reading from offset {start_offset})"
                    )
                # else: unchanged file, skip

        return files_to_read

    def update_file_state(self, file_path: Path, final_offset: int) -> None:
        """Update the state of a file after reading.

        Args:
            file_path: Path to the file that was read
            final_offset: Final byte offset after reading
        """
        file_key = str(file_path)

        try:
            stat = file_path.stat()

            if file_key in self._file_states:
                # Update existing state
                self._file_states[file_key].update_from_stat(final_offset)
            else:
                # Create new state
                self._file_states[file_key] = FileState(
                    path=file_path,
                    mtime=stat.st_mtime,
                    size=stat.st_size,
                    offset=final_offset,
                )
                logger.debug(f"Tracking new file: {file_path}")

        except (FileNotFoundError, PermissionError, OSError) as e:
            logger.warning(f"Failed to update state for {file_path}: {e}")

    def clear(self) -> None:
        """Clear all tracked file states (force full reload)."""
        self._file_states.clear()
        logger.debug("Cleared all file states")

    def get_tracked_files(self) -> List[Path]:
        """Get list of currently tracked files.

        Returns:
            List of file paths being tracked
        """
        return [state.path for state in self._file_states.values()]

    def is_tracking(self, file_path: Path) -> bool:
        """Check if a file is being tracked.

        Args:
            file_path: Path to check

        Returns:
            True if the file is being tracked
        """
        return str(file_path) in self._file_states

    def remove_file(self, file_path: Path) -> None:
        """Remove a file from tracking.

        Args:
            file_path: Path to stop tracking
        """
        file_key = str(file_path)
        if file_key in self._file_states:
            del self._file_states[file_key]
            logger.debug(f"Stopped tracking file: {file_path}")
