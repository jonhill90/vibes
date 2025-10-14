"""DocumentParser service for parsing documents using Docling.

This service provides document parsing capabilities for PDF, HTML, and DOCX files.
Uses ThreadPoolExecutor to prevent blocking the async event loop during CPU-intensive parsing.

Pattern: Follows thread pool pattern from PRP Gotcha #12
Critical Gotchas Addressed:
- Gotcha #12: Run CPU-bound Docling parsing in thread pool (prevents event loop blocking)
- Gotcha #15: Limit file size to 50MB max (memory protection)
- Semaphore limits concurrent parsing to 2 (prevents memory spikes)
"""

import asyncio
import logging
import os
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from typing import Optional

logger = logging.getLogger(__name__)


class DocumentParser:
    """Service for parsing documents using Docling with thread pool execution.

    Docling parsing is CPU-intensive (200-500ms per document), so we run it in a
    ThreadPoolExecutor to avoid blocking the async event loop.

    Attributes:
        MAX_FILE_SIZE: Maximum file size allowed (50MB) - prevents memory issues
        MAX_CONCURRENT_PARSING: Maximum concurrent parsing operations (2) - prevents memory spikes
        SUPPORTED_FORMATS: File extensions supported by this parser
    """

    # Gotcha #15: Limit file size to prevent memory issues with large PDFs
    MAX_FILE_SIZE = 50 * 1024 * 1024  # 50 MB

    # Gotcha #12: Limit concurrent parsing to prevent memory spikes
    MAX_CONCURRENT_PARSING = 2

    # Supported document formats
    SUPPORTED_FORMATS = {".pdf", ".html", ".htm", ".docx"}

    def __init__(self, max_workers: int = 4):
        """Initialize DocumentParser with thread pool executor.

        Args:
            max_workers: Maximum threads in pool (default 4)

        Pattern: Thread pool prevents blocking async event loop during parsing
        """
        # Gotcha #12: ThreadPoolExecutor for CPU-bound operations
        self.executor = ThreadPoolExecutor(max_workers=max_workers)

        # Gotcha #15: Semaphore to limit concurrent parsing
        self.semaphore = asyncio.Semaphore(self.MAX_CONCURRENT_PARSING)

        logger.info(
            f"DocumentParser initialized with {max_workers} workers, "
            f"max concurrent parsing: {self.MAX_CONCURRENT_PARSING}"
        )

    def _validate_file(self, file_path: str) -> None:
        """Validate file exists, is readable, and meets size requirements.

        Args:
            file_path: Path to file to validate

        Raises:
            FileNotFoundError: If file doesn't exist
            ValueError: If file format unsupported or size exceeds limit

        Critical Gotchas:
        - Gotcha #15: Reject files over 50MB (prevents memory issues)
        """
        path = Path(file_path)

        # Check file exists
        if not path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")

        # Check file is readable
        if not os.access(file_path, os.R_OK):
            raise ValueError(f"File not readable: {file_path}")

        # Check file format
        file_extension = path.suffix.lower()
        if file_extension not in self.SUPPORTED_FORMATS:
            raise ValueError(
                f"Unsupported file format: {file_extension}. "
                f"Supported formats: {', '.join(self.SUPPORTED_FORMATS)}"
            )

        # Gotcha #15: Check file size (prevent memory issues with large PDFs)
        file_size = path.stat().st_size
        if file_size > self.MAX_FILE_SIZE:
            size_mb = file_size / (1024 * 1024)
            max_size_mb = self.MAX_FILE_SIZE / (1024 * 1024)
            raise ValueError(
                f"File size {size_mb:.2f}MB exceeds maximum {max_size_mb:.0f}MB limit. "
                f"Large files can cause memory issues."
            )

        logger.debug(
            f"File validation passed: {path.name} "
            f"({file_size / 1024:.2f}KB, {file_extension})"
        )

    def _parse_sync(self, file_path: str) -> str:
        """Synchronous document parsing using Docling.

        This is the CPU-intensive operation that runs in the thread pool.
        DO NOT call this directly - use async parse_document() instead.

        Args:
            file_path: Path to document file

        Returns:
            str: Markdown-formatted text extracted from document

        Raises:
            ImportError: If docling not installed
            Exception: If parsing fails

        Pattern: This is the synchronous worker function for thread pool
        """
        try:
            # Import docling here (only in worker thread)
            from docling.document_converter import DocumentConverter
        except ImportError:
            raise ImportError(
                "docling package not installed. "
                "Install with: pip install docling"
            )

        try:
            # Initialize converter (thread-safe)
            converter = DocumentConverter()

            # Parse document (CPU-intensive operation)
            logger.debug(f"Starting Docling conversion for: {file_path}")
            result = converter.convert(file_path)

            # Export to markdown format
            markdown_text = result.document.export_to_markdown()

            logger.debug(
                f"Docling conversion complete: {len(markdown_text)} characters extracted"
            )
            return markdown_text

        except Exception as e:
            logger.error(f"Docling parsing failed for {file_path}: {e}")
            raise

    async def parse_document(self, file_path: str) -> str:
        """Parse document asynchronously using thread pool.

        This is the main entry point for document parsing. It validates the file,
        then runs the CPU-intensive parsing in a thread pool to avoid blocking
        the async event loop.

        Args:
            file_path: Path to document file (PDF, HTML, or DOCX)

        Returns:
            str: Markdown-formatted text extracted from document

        Raises:
            FileNotFoundError: If file doesn't exist
            ValueError: If file format unsupported or size exceeds limit
            ImportError: If docling not installed
            Exception: If parsing fails

        Critical Gotchas:
        - Gotcha #12: Uses run_in_executor to prevent blocking event loop
        - Gotcha #15: Validates file size before parsing (50MB max)

        Example:
            parser = DocumentParser()
            markdown_text = await parser.parse_document("document.pdf")
        """
        # Validate file before attempting to parse
        self._validate_file(file_path)

        # Gotcha #15: Semaphore limits concurrent parsing (prevents memory spikes)
        async with self.semaphore:
            logger.info(f"Parsing document: {file_path}")

            try:
                # Gotcha #12: Run CPU-intensive parsing in thread pool
                # This prevents blocking the async event loop
                loop = asyncio.get_event_loop()
                markdown_text = await loop.run_in_executor(
                    self.executor,
                    self._parse_sync,
                    file_path
                )

                logger.info(
                    f"Successfully parsed document: {Path(file_path).name} "
                    f"({len(markdown_text)} characters)"
                )
                return markdown_text

            except Exception as e:
                logger.error(f"Error parsing document {file_path}: {e}")
                raise

    async def parse_documents_batch(
        self,
        file_paths: list[str],
    ) -> dict[str, Optional[str]]:
        """Parse multiple documents concurrently (with semaphore limit).

        Args:
            file_paths: List of file paths to parse

        Returns:
            dict: Mapping of file_path -> markdown_text (or None if parsing failed)

        Pattern: Concurrent parsing with semaphore limit (max 2 concurrent)
        """
        results = {}

        # Parse all documents concurrently (semaphore limits concurrency)
        tasks = [self.parse_document(path) for path in file_paths]

        # Gather results, capturing exceptions
        parse_results = await asyncio.gather(*tasks, return_exceptions=True)

        # Map results back to file paths
        for file_path, result in zip(file_paths, parse_results):
            if isinstance(result, Exception):
                logger.error(f"Failed to parse {file_path}: {result}")
                results[file_path] = None
            else:
                results[file_path] = result

        successful = sum(1 for v in results.values() if v is not None)
        logger.info(
            f"Batch parsing complete: {successful}/{len(file_paths)} successful"
        )

        return results

    def shutdown(self) -> None:
        """Shutdown thread pool executor gracefully.

        Call this when the service is shutting down to ensure all threads complete.
        """
        logger.info("Shutting down DocumentParser thread pool")
        self.executor.shutdown(wait=True)

    def __del__(self):
        """Cleanup thread pool on object destruction."""
        try:
            self.executor.shutdown(wait=False)
        except Exception:
            pass  # Ignore errors during cleanup
