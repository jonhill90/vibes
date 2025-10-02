"""
Example: Safe File Operations Pattern

This module demonstrates best practices for file I/O operations in Vibes.

Key Patterns Demonstrated:
- Path validation and sanitization
- Atomic write operations
- Automatic backup creation
- Error recovery and rollback
- Context managers for resource safety
- Type hints for clarity
- Comprehensive error handling

Adapt this pattern for any file manipulation tasks in your projects.
"""

import os
import shutil
import tempfile
from pathlib import Path
from typing import Optional, List, Union, BinaryIO, TextIO
from contextlib import contextmanager
from datetime import datetime
import hashlib


# ==============================================================================
# Custom Exceptions
# ==============================================================================

class FileOperationError(Exception):
    """Base exception for file operations"""
    pass


class InvalidPathError(FileOperationError):
    """Path validation failed"""
    pass


class BackupError(FileOperationError):
    """Backup creation failed"""
    pass


class WriteError(FileOperationError):
    """Write operation failed"""
    pass


# ==============================================================================
# Path Validation
# ==============================================================================

class PathValidator:
    """
    Validates and sanitizes file paths to prevent security issues.
    """

    def __init__(self, allowed_base_paths: Optional[List[Path]] = None):
        """
        Initialize path validator.

        Args:
            allowed_base_paths: List of allowed base directories.
                               If None, allows all paths (use with caution!)
        """
        self.allowed_base_paths = allowed_base_paths or []

    def validate(self, path: Union[str, Path]) -> Path:
        """
        Validate and sanitize path.

        Args:
            path: Path to validate

        Returns:
            Validated Path object

        Raises:
            InvalidPathError: If path is invalid or outside allowed directories
        """
        # Convert to Path object
        path = Path(path).resolve()

        # Check for path traversal attempts
        if ".." in path.parts:
            raise InvalidPathError(f"Path traversal detected: {path}")

        # Check against allowed base paths
        if self.allowed_base_paths:
            is_allowed = any(
                self._is_subpath(path, base)
                for base in self.allowed_base_paths
            )
            if not is_allowed:
                raise InvalidPathError(
                    f"Path outside allowed directories: {path}"
                )

        return path

    @staticmethod
    def _is_subpath(path: Path, base: Path) -> bool:
        """Check if path is under base directory"""
        try:
            path.relative_to(base)
            return True
        except ValueError:
            return False


# ==============================================================================
# Atomic File Writer
# ==============================================================================

class AtomicFileWriter:
    """
    Atomic file write operations with automatic backup and rollback.

    Ensures file is either completely written or not modified at all.
    """

    def __init__(
        self,
        path: Union[str, Path],
        create_backup: bool = True,
        backup_suffix: str = ".bak"
    ):
        """
        Initialize atomic file writer.

        Args:
            path: File path to write
            create_backup: Whether to create backup of existing file
            backup_suffix: Backup file suffix
        """
        self.path = Path(path)
        self.create_backup = create_backup
        self.backup_suffix = backup_suffix
        self.backup_path: Optional[Path] = None
        self.temp_path: Optional[Path] = None

    @contextmanager
    def open(self, mode: str = "w", **kwargs):
        """
        Open file for atomic writing.

        Usage:
            writer = AtomicFileWriter("output.txt")
            with writer.open() as f:
                f.write("content")

        Args:
            mode: File open mode
            **kwargs: Additional arguments for open()

        Yields:
            File object for writing
        """
        # Create backup if file exists
        if self.create_backup and self.path.exists():
            try:
                self.backup_path = self._create_backup()
            except Exception as e:
                raise BackupError(f"Failed to create backup: {e}")

        # Create temporary file in same directory
        # (ensures atomic move works on same filesystem)
        try:
            temp_dir = self.path.parent
            temp_fd, temp_path_str = tempfile.mkstemp(
                dir=temp_dir,
                prefix=f".{self.path.name}.",
                suffix=".tmp"
            )
            self.temp_path = Path(temp_path_str)

            # Write to temporary file
            with os.fdopen(temp_fd, mode, **kwargs) as f:
                try:
                    yield f
                    f.flush()
                    os.fsync(f.fileno())  # Ensure written to disk

                    # Atomic move (replaces target file)
                    self.temp_path.replace(self.path)

                    # Success - remove backup
                    if self.backup_path:
                        self.backup_path.unlink(missing_ok=True)

                except Exception as e:
                    # Error during write - rollback
                    self._rollback()
                    raise WriteError(f"Write failed: {e}")

        except Exception as e:
            # Error creating temp file - rollback
            self._rollback()
            raise WriteError(f"Failed to create temp file: {e}")

        finally:
            # Clean up temp file if still exists
            if self.temp_path and self.temp_path.exists():
                self.temp_path.unlink(missing_ok=True)

    def _create_backup(self) -> Path:
        """Create backup of existing file"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_path = self.path.with_suffix(
            f"{self.path.suffix}{self.backup_suffix}.{timestamp}"
        )
        shutil.copy2(self.path, backup_path)
        return backup_path

    def _rollback(self):
        """Rollback to backup if it exists"""
        if self.backup_path and self.backup_path.exists():
            shutil.copy2(self.backup_path, self.path)


# ==============================================================================
# Safe File Operations
# ==============================================================================

class SafeFileOps:
    """
    Collection of safe file operation utilities.
    """

    def __init__(self, validator: Optional[PathValidator] = None):
        """
        Initialize safe file operations.

        Args:
            validator: PathValidator instance (optional)
        """
        self.validator = validator or PathValidator()

    def read_text(self, path: Union[str, Path], encoding: str = "utf-8") -> str:
        """
        Safely read text file.

        Args:
            path: File path
            encoding: Text encoding

        Returns:
            File contents as string

        Raises:
            InvalidPathError: Path validation failed
            FileOperationError: Read failed
        """
        path = self.validator.validate(path)

        try:
            return path.read_text(encoding=encoding)
        except Exception as e:
            raise FileOperationError(f"Failed to read {path}: {e}")

    def read_bytes(self, path: Union[str, Path]) -> bytes:
        """
        Safely read binary file.

        Args:
            path: File path

        Returns:
            File contents as bytes
        """
        path = self.validator.validate(path)

        try:
            return path.read_bytes()
        except Exception as e:
            raise FileOperationError(f"Failed to read {path}: {e}")

    def write_text(
        self,
        path: Union[str, Path],
        content: str,
        encoding: str = "utf-8",
        atomic: bool = True,
        create_backup: bool = True
    ):
        """
        Safely write text file.

        Args:
            path: File path
            content: Content to write
            encoding: Text encoding
            atomic: Use atomic write operation
            create_backup: Create backup of existing file

        Raises:
            InvalidPathError: Path validation failed
            WriteError: Write failed
        """
        path = self.validator.validate(path)

        # Ensure parent directory exists
        path.parent.mkdir(parents=True, exist_ok=True)

        if atomic:
            # Atomic write with backup
            writer = AtomicFileWriter(path, create_backup=create_backup)
            with writer.open("w", encoding=encoding) as f:
                f.write(content)
        else:
            # Simple write (not atomic)
            try:
                path.write_text(content, encoding=encoding)
            except Exception as e:
                raise WriteError(f"Failed to write {path}: {e}")

    def write_bytes(
        self,
        path: Union[str, Path],
        content: bytes,
        atomic: bool = True,
        create_backup: bool = True
    ):
        """
        Safely write binary file.

        Args:
            path: File path
            content: Binary content
            atomic: Use atomic write operation
            create_backup: Create backup of existing file
        """
        path = self.validator.validate(path)

        # Ensure parent directory exists
        path.parent.mkdir(parents=True, exist_ok=True)

        if atomic:
            writer = AtomicFileWriter(path, create_backup=create_backup)
            with writer.open("wb") as f:
                f.write(content)
        else:
            try:
                path.write_bytes(content)
            except Exception as e:
                raise WriteError(f"Failed to write {path}: {e}")

    def copy_file(
        self,
        src: Union[str, Path],
        dst: Union[str, Path],
        create_backup: bool = True
    ):
        """
        Safely copy file with optional backup.

        Args:
            src: Source file path
            dst: Destination file path
            create_backup: Create backup if destination exists

        Raises:
            InvalidPathError: Path validation failed
            FileOperationError: Copy failed
        """
        src_path = self.validator.validate(src)
        dst_path = self.validator.validate(dst)

        # Create backup if destination exists
        if create_backup and dst_path.exists():
            backup_path = dst_path.with_suffix(f"{dst_path.suffix}.bak")
            shutil.copy2(dst_path, backup_path)

        try:
            # Ensure destination directory exists
            dst_path.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(src_path, dst_path)
        except Exception as e:
            raise FileOperationError(f"Failed to copy {src_path} to {dst_path}: {e}")

    def move_file(
        self,
        src: Union[str, Path],
        dst: Union[str, Path],
        create_backup: bool = True
    ):
        """
        Safely move file with optional backup.

        Args:
            src: Source file path
            dst: Destination file path
            create_backup: Create backup if destination exists
        """
        src_path = self.validator.validate(src)
        dst_path = self.validator.validate(dst)

        # Create backup if destination exists
        if create_backup and dst_path.exists():
            backup_path = dst_path.with_suffix(f"{dst_path.suffix}.bak")
            shutil.copy2(dst_path, backup_path)

        try:
            # Ensure destination directory exists
            dst_path.parent.mkdir(parents=True, exist_ok=True)
            shutil.move(src_path, dst_path)
        except Exception as e:
            raise FileOperationError(f"Failed to move {src_path} to {dst_path}: {e}")

    def delete_file(self, path: Union[str, Path], create_backup: bool = True):
        """
        Safely delete file with optional backup.

        Args:
            path: File path to delete
            create_backup: Create backup before deletion
        """
        path = self.validator.validate(path)

        if not path.exists():
            return  # Already deleted

        # Create backup before deletion
        if create_backup:
            backup_path = path.with_suffix(f"{path.suffix}.bak")
            shutil.copy2(path, backup_path)

        try:
            path.unlink()
        except Exception as e:
            raise FileOperationError(f"Failed to delete {path}: {e}")

    @staticmethod
    def compute_checksum(path: Union[str, Path], algorithm: str = "sha256") -> str:
        """
        Compute file checksum.

        Args:
            path: File path
            algorithm: Hash algorithm (md5, sha1, sha256, etc.)

        Returns:
            Hexadecimal checksum string
        """
        path = Path(path)
        hash_obj = hashlib.new(algorithm)

        with path.open("rb") as f:
            # Read in chunks for large files
            for chunk in iter(lambda: f.read(8192), b""):
                hash_obj.update(chunk)

        return hash_obj.hexdigest()


# ==============================================================================
# Example Usage
# ==============================================================================

def example_usage():
    """Demonstrate safe file operations"""

    # Initialize with path validation
    allowed_dirs = [Path("/workspace/vibes")]
    validator = PathValidator(allowed_base_paths=allowed_dirs)
    file_ops = SafeFileOps(validator=validator)

    # Example 1: Safe write with automatic backup
    print("Writing file with backup...")
    file_ops.write_text(
        "/workspace/vibes/test.txt",
        "Hello, Vibes!",
        atomic=True,
        create_backup=True
    )

    # Example 2: Read file
    print("Reading file...")
    content = file_ops.read_text("/workspace/vibes/test.txt")
    print(f"Content: {content}")

    # Example 3: Copy file with backup
    print("Copying file...")
    file_ops.copy_file(
        "/workspace/vibes/test.txt",
        "/workspace/vibes/test_copy.txt",
        create_backup=True
    )

    # Example 4: Compute checksum
    print("Computing checksum...")
    checksum = file_ops.compute_checksum("/workspace/vibes/test.txt")
    print(f"SHA256: {checksum}")

    # Example 5: Atomic write with context manager
    print("Atomic write...")
    writer = AtomicFileWriter("/workspace/vibes/atomic.txt")
    with writer.open() as f:
        f.write("Atomic write example\n")
        f.write("This is written atomically\n")

    print("Done!")


if __name__ == "__main__":
    example_usage()
