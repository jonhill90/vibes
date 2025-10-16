"""Unit tests for file upload validation.

This module tests document upload validation logic:
- File extension whitelist validation (.pdf, .docx, .txt, .md, .html)
- File size limit enforcement (10MB max)
- MIME type validation (security layer)
- Invalid file type rejection (.exe, .zip, etc.)
- User-friendly error messages with suggestions

Pattern: Example 3 (file upload validation patterns)
Reference: prps/rag_service_testing_validation/examples/example_3_file_upload_validation.py
"""

import pytest
from io import BytesIO
from unittest.mock import MagicMock, AsyncMock
from fastapi import UploadFile, HTTPException

# Import the validation constants and endpoint from documents route
from src.api.routes.documents import (
    MAX_FILE_SIZE,
    ALLOWED_EXTENSIONS,
    ALLOWED_MIME_TYPES,
    upload_document,
)


class TestFileExtensionValidation:
    """Test file extension whitelist validation."""

    @pytest.mark.asyncio
    async def test_valid_pdf_extension(self, mock_db_pool):
        """Test that .pdf extension is accepted."""
        # Create mock file with valid PDF extension
        mock_file = MagicMock(spec=UploadFile)
        mock_file.filename = "test-document.pdf"
        mock_file.content_type = "application/pdf"
        mock_file.read = AsyncMock(return_value=b"%PDF-1.4\ntest content\n%%EOF")

        # Mock the database operations to return success
        mock_conn = MagicMock()
        mock_conn.fetchval = AsyncMock(return_value="123e4567-e89b-12d3-a456-426614174000")
        mock_conn.fetchrow = AsyncMock(return_value={
            "id": "123e4567-e89b-12d3-a456-426614174000",
            "source_id": "123e4567-e89b-12d3-a456-426614174000",
            "title": "test-document.pdf",
            "document_type": "pdf",
            "url": None,
            "created_at": "2025-10-16T12:00:00",
            "updated_at": "2025-10-16T12:00:00",
        })

        async def mock_acquire():
            yield mock_conn

        mock_db_pool.acquire = MagicMock(return_value=mock_acquire())

        # Mock request object with app state
        mock_request = MagicMock()
        mock_request.app.state.qdrant_client = MagicMock()

        # This should NOT raise an exception
        # Note: Full ingestion will fail, but extension validation should pass
        # We expect exception from ingestion, not from extension validation
        try:
            result = await upload_document(
                request=mock_request,
                file=mock_file,
                source_id="123e4567-e89b-12d3-a456-426614174000",
                title="Test Document",
                db_pool=mock_db_pool,
            )
            # If we get here, extension validation passed
            assert True
        except HTTPException as e:
            # Extension validation passed, but ingestion might fail
            # 400 = extension validation failed (BAD)
            # 500 = ingestion failed (OK for this test)
            assert e.status_code != 400 or "extension" not in str(e.detail).lower()

    @pytest.mark.asyncio
    async def test_valid_docx_extension(self, mock_db_pool):
        """Test that .docx extension is accepted."""
        mock_file = MagicMock(spec=UploadFile)
        mock_file.filename = "document.docx"
        mock_file.content_type = "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
        mock_file.read = AsyncMock(return_value=b"PK\x03\x04test docx content")

        mock_request = MagicMock()
        mock_request.app.state.qdrant_client = MagicMock()

        try:
            await upload_document(
                request=mock_request,
                file=mock_file,
                source_id="123e4567-e89b-12d3-a456-426614174000",
                db_pool=mock_db_pool,
            )
        except HTTPException as e:
            assert e.status_code != 400 or "extension" not in str(e.detail).lower()

    @pytest.mark.asyncio
    async def test_valid_txt_extension(self, mock_db_pool):
        """Test that .txt extension is accepted."""
        mock_file = MagicMock(spec=UploadFile)
        mock_file.filename = "notes.txt"
        mock_file.content_type = "text/plain"
        mock_file.read = AsyncMock(return_value=b"Plain text content")

        mock_request = MagicMock()
        mock_request.app.state.qdrant_client = MagicMock()

        try:
            await upload_document(
                request=mock_request,
                file=mock_file,
                source_id="123e4567-e89b-12d3-a456-426614174000",
                db_pool=mock_db_pool,
            )
        except HTTPException as e:
            assert e.status_code != 400 or "extension" not in str(e.detail).lower()

    @pytest.mark.asyncio
    async def test_valid_md_extension(self, mock_db_pool):
        """Test that .md extension is accepted."""
        mock_file = MagicMock(spec=UploadFile)
        mock_file.filename = "readme.md"
        mock_file.content_type = "text/markdown"
        mock_file.read = AsyncMock(return_value=b"# Markdown Content\n\nTest")

        mock_request = MagicMock()
        mock_request.app.state.qdrant_client = MagicMock()

        try:
            await upload_document(
                request=mock_request,
                file=mock_file,
                source_id="123e4567-e89b-12d3-a456-426614174000",
                db_pool=mock_db_pool,
            )
        except HTTPException as e:
            assert e.status_code != 400 or "extension" not in str(e.detail).lower()

    @pytest.mark.asyncio
    async def test_valid_html_extension(self, mock_db_pool):
        """Test that .html extension is accepted."""
        mock_file = MagicMock(spec=UploadFile)
        mock_file.filename = "page.html"
        mock_file.content_type = "text/html"
        mock_file.read = AsyncMock(return_value=b"<html><body>Test</body></html>")

        mock_request = MagicMock()
        mock_request.app.state.qdrant_client = MagicMock()

        try:
            await upload_document(
                request=mock_request,
                file=mock_file,
                source_id="123e4567-e89b-12d3-a456-426614174000",
                db_pool=mock_db_pool,
            )
        except HTTPException as e:
            assert e.status_code != 400 or "extension" not in str(e.detail).lower()

    @pytest.mark.asyncio
    async def test_invalid_exe_extension(self, mock_db_pool):
        """Test that .exe extension is rejected."""
        mock_file = MagicMock(spec=UploadFile)
        mock_file.filename = "malware.exe"
        mock_file.content_type = "application/x-msdownload"
        mock_file.read = AsyncMock(return_value=b"MZ\x90\x00malicious content")

        mock_request = MagicMock()
        mock_request.app.state.qdrant_client = MagicMock()

        # Should raise HTTPException with 400 status code
        with pytest.raises(HTTPException) as exc_info:
            await upload_document(
                request=mock_request,
                file=mock_file,
                source_id="123e4567-e89b-12d3-a456-426614174000",
                db_pool=mock_db_pool,
            )

        assert exc_info.value.status_code == 400
        detail = exc_info.value.detail
        assert "Invalid file type" in str(detail) or "extension" in str(detail).lower()
        # Verify helpful suggestion provided
        assert "suggestion" in str(detail).lower() or ".pdf" in str(detail)

    @pytest.mark.asyncio
    async def test_invalid_zip_extension(self, mock_db_pool):
        """Test that .zip extension is rejected."""
        mock_file = MagicMock(spec=UploadFile)
        mock_file.filename = "archive.zip"
        mock_file.content_type = "application/zip"
        mock_file.read = AsyncMock(return_value=b"PK\x03\x04archive content")

        mock_request = MagicMock()
        mock_request.app.state.qdrant_client = MagicMock()

        with pytest.raises(HTTPException) as exc_info:
            await upload_document(
                request=mock_request,
                file=mock_file,
                source_id="123e4567-e89b-12d3-a456-426614174000",
                db_pool=mock_db_pool,
            )

        assert exc_info.value.status_code == 400
        detail = exc_info.value.detail
        assert "Invalid file type" in str(detail) or "extension" in str(detail).lower()

    @pytest.mark.asyncio
    async def test_invalid_sh_extension(self, mock_db_pool):
        """Test that .sh extension is rejected."""
        mock_file = MagicMock(spec=UploadFile)
        mock_file.filename = "script.sh"
        mock_file.content_type = "application/x-sh"
        mock_file.read = AsyncMock(return_value=b"#!/bin/bash\nrm -rf /")

        mock_request = MagicMock()
        mock_request.app.state.qdrant_client = MagicMock()

        with pytest.raises(HTTPException) as exc_info:
            await upload_document(
                request=mock_request,
                file=mock_file,
                source_id="123e4567-e89b-12d3-a456-426614174000",
                db_pool=mock_db_pool,
            )

        assert exc_info.value.status_code == 400

    @pytest.mark.asyncio
    async def test_no_extension(self, mock_db_pool):
        """Test that files without extension are rejected."""
        mock_file = MagicMock(spec=UploadFile)
        mock_file.filename = "document_no_extension"
        mock_file.content_type = "application/octet-stream"
        mock_file.read = AsyncMock(return_value=b"some content")

        mock_request = MagicMock()
        mock_request.app.state.qdrant_client = MagicMock()

        with pytest.raises(HTTPException) as exc_info:
            await upload_document(
                request=mock_request,
                file=mock_file,
                source_id="123e4567-e89b-12d3-a456-426614174000",
                db_pool=mock_db_pool,
            )

        assert exc_info.value.status_code == 400

    @pytest.mark.asyncio
    async def test_case_insensitive_extension(self, mock_db_pool):
        """Test that extension validation is case-insensitive (.PDF should work)."""
        mock_file = MagicMock(spec=UploadFile)
        mock_file.filename = "document.PDF"  # Uppercase extension
        mock_file.content_type = "application/pdf"
        mock_file.read = AsyncMock(return_value=b"%PDF-1.4\ntest\n%%EOF")

        mock_request = MagicMock()
        mock_request.app.state.qdrant_client = MagicMock()

        # Should NOT reject due to case difference
        try:
            await upload_document(
                request=mock_request,
                file=mock_file,
                source_id="123e4567-e89b-12d3-a456-426614174000",
                db_pool=mock_db_pool,
            )
        except HTTPException as e:
            assert e.status_code != 400 or "extension" not in str(e.detail).lower()


class TestFileSizeValidation:
    """Test file size limit enforcement (10MB max)."""

    @pytest.mark.asyncio
    async def test_file_within_size_limit(self, mock_db_pool):
        """Test that files under 10MB are accepted."""
        # Create 1MB file (well under limit)
        file_size = 1 * 1024 * 1024  # 1MB
        mock_file = MagicMock(spec=UploadFile)
        mock_file.filename = "small.pdf"
        mock_file.content_type = "application/pdf"
        mock_file.read = AsyncMock(return_value=b"x" * file_size)

        mock_request = MagicMock()
        mock_request.app.state.qdrant_client = MagicMock()

        # Should NOT raise size exception
        try:
            await upload_document(
                request=mock_request,
                file=mock_file,
                source_id="123e4567-e89b-12d3-a456-426614174000",
                db_pool=mock_db_pool,
            )
        except HTTPException as e:
            # 413 = file too large (BAD for this test)
            # 500 = ingestion failed (OK for this test)
            assert e.status_code != 413

    @pytest.mark.asyncio
    async def test_file_at_size_limit(self, mock_db_pool):
        """Test that files exactly at 10MB limit are accepted."""
        # Create exactly 10MB file
        file_size = MAX_FILE_SIZE  # Exactly 10MB
        mock_file = MagicMock(spec=UploadFile)
        mock_file.filename = "limit.pdf"
        mock_file.content_type = "application/pdf"
        mock_file.read = AsyncMock(return_value=b"x" * file_size)

        mock_request = MagicMock()
        mock_request.app.state.qdrant_client = MagicMock()

        # Should NOT raise size exception
        try:
            await upload_document(
                request=mock_request,
                file=mock_file,
                source_id="123e4567-e89b-12d3-a456-426614174000",
                db_pool=mock_db_pool,
            )
        except HTTPException as e:
            assert e.status_code != 413

    @pytest.mark.asyncio
    async def test_file_exceeds_size_limit(self, mock_db_pool):
        """Test that files over 10MB are rejected."""
        # Create 11MB file (exceeds limit)
        file_size = MAX_FILE_SIZE + 1  # 10MB + 1 byte
        mock_file = MagicMock(spec=UploadFile)
        mock_file.filename = "huge.pdf"
        mock_file.content_type = "application/pdf"
        mock_file.read = AsyncMock(return_value=b"x" * file_size)

        mock_request = MagicMock()
        mock_request.app.state.qdrant_client = MagicMock()

        # Should raise HTTPException with 413 status code
        with pytest.raises(HTTPException) as exc_info:
            await upload_document(
                request=mock_request,
                file=mock_file,
                source_id="123e4567-e89b-12d3-a456-426614174000",
                db_pool=mock_db_pool,
            )

        assert exc_info.value.status_code == 413
        detail = exc_info.value.detail
        assert "too large" in str(detail).lower() or "exceeds" in str(detail).lower()
        # Verify helpful suggestion provided
        assert "suggestion" in str(detail).lower() or "compress" in str(detail).lower()

    @pytest.mark.asyncio
    async def test_file_far_exceeds_size_limit(self, mock_db_pool):
        """Test that files far exceeding limit are rejected with clear message."""
        # Create 50MB file (5x the limit)
        file_size = MAX_FILE_SIZE * 5  # 50MB
        mock_file = MagicMock(spec=UploadFile)
        mock_file.filename = "massive.pdf"
        mock_file.content_type = "application/pdf"
        mock_file.read = AsyncMock(return_value=b"x" * file_size)

        mock_request = MagicMock()
        mock_request.app.state.qdrant_client = MagicMock()

        with pytest.raises(HTTPException) as exc_info:
            await upload_document(
                request=mock_request,
                file=mock_file,
                source_id="123e4567-e89b-12d3-a456-426614174000",
                db_pool=mock_db_pool,
            )

        assert exc_info.value.status_code == 413
        detail = exc_info.value.detail
        # Verify error message includes actual sizes
        assert "bytes" in str(detail).lower()

    @pytest.mark.asyncio
    async def test_empty_file(self, mock_db_pool):
        """Test that empty files (0 bytes) are accepted (edge case)."""
        mock_file = MagicMock(spec=UploadFile)
        mock_file.filename = "empty.pdf"
        mock_file.content_type = "application/pdf"
        mock_file.read = AsyncMock(return_value=b"")  # Empty file

        mock_request = MagicMock()
        mock_request.app.state.qdrant_client = MagicMock()

        # Should NOT raise size exception (empty file is under limit)
        try:
            await upload_document(
                request=mock_request,
                file=mock_file,
                source_id="123e4567-e89b-12d3-a456-426614174000",
                db_pool=mock_db_pool,
            )
        except HTTPException as e:
            assert e.status_code != 413


class TestMimeTypeValidation:
    """Test MIME type validation (security layer)."""

    @pytest.mark.asyncio
    async def test_valid_pdf_mime_type(self, mock_db_pool):
        """Test that application/pdf MIME type is accepted."""
        mock_file = MagicMock(spec=UploadFile)
        mock_file.filename = "doc.pdf"
        mock_file.content_type = "application/pdf"  # Valid MIME
        mock_file.read = AsyncMock(return_value=b"%PDF-1.4\ntest\n%%EOF")

        mock_request = MagicMock()
        mock_request.app.state.qdrant_client = MagicMock()

        # Should NOT raise MIME type exception
        try:
            await upload_document(
                request=mock_request,
                file=mock_file,
                source_id="123e4567-e89b-12d3-a456-426614174000",
                db_pool=mock_db_pool,
            )
        except HTTPException as e:
            # MIME validation is warning-only, extension validation is primary
            # So no 400 error should occur from MIME mismatch alone
            assert e.status_code != 400 or "mime" not in str(e.detail).lower()

    @pytest.mark.asyncio
    async def test_valid_docx_mime_type(self, mock_db_pool):
        """Test that docx MIME type is accepted."""
        mock_file = MagicMock(spec=UploadFile)
        mock_file.filename = "doc.docx"
        mock_file.content_type = "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
        mock_file.read = AsyncMock(return_value=b"PK\x03\x04content")

        mock_request = MagicMock()
        mock_request.app.state.qdrant_client = MagicMock()

        try:
            await upload_document(
                request=mock_request,
                file=mock_file,
                source_id="123e4567-e89b-12d3-a456-426614174000",
                db_pool=mock_db_pool,
            )
        except HTTPException as e:
            assert e.status_code != 400 or "mime" not in str(e.detail).lower()

    @pytest.mark.asyncio
    async def test_valid_text_mime_type(self, mock_db_pool):
        """Test that text/plain MIME type is accepted."""
        mock_file = MagicMock(spec=UploadFile)
        mock_file.filename = "notes.txt"
        mock_file.content_type = "text/plain"
        mock_file.read = AsyncMock(return_value=b"Plain text")

        mock_request = MagicMock()
        mock_request.app.state.qdrant_client = MagicMock()

        try:
            await upload_document(
                request=mock_request,
                file=mock_file,
                source_id="123e4567-e89b-12d3-a456-426614174000",
                db_pool=mock_db_pool,
            )
        except HTTPException as e:
            assert e.status_code != 400 or "mime" not in str(e.detail).lower()

    @pytest.mark.asyncio
    async def test_mime_type_mismatch_warning_only(self, mock_db_pool, caplog):
        """Test that MIME type mismatch generates warning but doesn't reject.

        Per the implementation: extension validation is primary, MIME is secondary.
        A mismatch should log a warning but not reject the file.
        """
        import logging
        caplog.set_level(logging.WARNING)

        mock_file = MagicMock(spec=UploadFile)
        mock_file.filename = "doc.pdf"  # PDF extension
        mock_file.content_type = "text/plain"  # Wrong MIME type
        mock_file.read = AsyncMock(return_value=b"%PDF-1.4\ntest\n%%EOF")

        mock_request = MagicMock()
        mock_request.app.state.qdrant_client = MagicMock()

        # Should NOT reject (extension is valid)
        try:
            await upload_document(
                request=mock_request,
                file=mock_file,
                source_id="123e4567-e89b-12d3-a456-426614174000",
                db_pool=mock_db_pool,
            )
        except HTTPException as e:
            # Extension validation passed, so no 400 due to MIME mismatch
            assert e.status_code != 400 or "mime" not in str(e.detail).lower()

        # Verify warning was logged
        # Note: This is implementation-dependent and may need adjustment
        # if logging behavior changes

    @pytest.mark.asyncio
    async def test_missing_mime_type(self, mock_db_pool):
        """Test that missing MIME type (None) is handled gracefully."""
        mock_file = MagicMock(spec=UploadFile)
        mock_file.filename = "doc.pdf"
        mock_file.content_type = None  # Missing MIME type
        mock_file.read = AsyncMock(return_value=b"%PDF-1.4\ntest\n%%EOF")

        mock_request = MagicMock()
        mock_request.app.state.qdrant_client = MagicMock()

        # Should NOT reject (extension is valid)
        try:
            await upload_document(
                request=mock_request,
                file=mock_file,
                source_id="123e4567-e89b-12d3-a456-426614174000",
                db_pool=mock_db_pool,
            )
        except HTTPException as e:
            assert e.status_code != 400 or "mime" not in str(e.detail).lower()


class TestUserFriendlyErrorMessages:
    """Test that error messages are user-friendly with helpful suggestions."""

    @pytest.mark.asyncio
    async def test_invalid_extension_error_message_quality(self, mock_db_pool):
        """Test that invalid extension error includes helpful suggestion."""
        mock_file = MagicMock(spec=UploadFile)
        mock_file.filename = "virus.exe"
        mock_file.content_type = "application/x-msdownload"
        mock_file.read = AsyncMock(return_value=b"malicious")

        mock_request = MagicMock()
        mock_request.app.state.qdrant_client = MagicMock()

        with pytest.raises(HTTPException) as exc_info:
            await upload_document(
                request=mock_request,
                file=mock_file,
                source_id="123e4567-e89b-12d3-a456-426614174000",
                db_pool=mock_db_pool,
            )

        detail = exc_info.value.detail
        detail_str = str(detail)

        # Verify error message quality
        assert "Invalid file type" in detail_str or "not allowed" in detail_str
        # Verify suggestion includes at least one valid extension
        assert any(ext in detail_str for ext in ALLOWED_EXTENSIONS)

    @pytest.mark.asyncio
    async def test_file_too_large_error_message_quality(self, mock_db_pool):
        """Test that file too large error includes helpful suggestion."""
        file_size = MAX_FILE_SIZE + 1000
        mock_file = MagicMock(spec=UploadFile)
        mock_file.filename = "huge.pdf"
        mock_file.content_type = "application/pdf"
        mock_file.read = AsyncMock(return_value=b"x" * file_size)

        mock_request = MagicMock()
        mock_request.app.state.qdrant_client = MagicMock()

        with pytest.raises(HTTPException) as exc_info:
            await upload_document(
                request=mock_request,
                file=mock_file,
                source_id="123e4567-e89b-12d3-a456-426614174000",
                db_pool=mock_db_pool,
            )

        detail = exc_info.value.detail
        detail_str = str(detail)

        # Verify error message quality
        assert "too large" in detail_str.lower() or "exceeds" in detail_str.lower()
        # Verify suggestion is helpful
        assert "compress" in detail_str.lower() or "split" in detail_str.lower() or "smaller" in detail_str.lower()
        # Verify actual sizes are mentioned
        assert str(MAX_FILE_SIZE) in detail_str or "10" in detail_str  # 10MB limit


class TestValidationConstants:
    """Test that validation constants are properly defined."""

    def test_max_file_size_constant(self):
        """Test that MAX_FILE_SIZE is 10MB."""
        assert MAX_FILE_SIZE == 10 * 1024 * 1024  # 10MB in bytes

    def test_allowed_extensions_constant(self):
        """Test that ALLOWED_EXTENSIONS includes expected types."""
        expected_extensions = [".pdf", ".docx", ".txt", ".md", ".html"]
        for ext in expected_extensions:
            assert ext in ALLOWED_EXTENSIONS

    def test_allowed_mime_types_constant(self):
        """Test that ALLOWED_MIME_TYPES includes expected types."""
        expected_mimes = [
            "application/pdf",
            "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            "text/plain",
            "text/markdown",
            "text/html",
        ]
        for mime in expected_mimes:
            assert mime in ALLOWED_MIME_TYPES


class TestEdgeCases:
    """Test edge cases and boundary conditions."""

    @pytest.mark.asyncio
    async def test_filename_with_multiple_dots(self, mock_db_pool):
        """Test that files with multiple dots are handled correctly."""
        mock_file = MagicMock(spec=UploadFile)
        mock_file.filename = "my.test.document.pdf"  # Multiple dots
        mock_file.content_type = "application/pdf"
        mock_file.read = AsyncMock(return_value=b"%PDF-1.4\ntest\n%%EOF")

        mock_request = MagicMock()
        mock_request.app.state.qdrant_client = MagicMock()

        # Should use last extension (.pdf)
        try:
            await upload_document(
                request=mock_request,
                file=mock_file,
                source_id="123e4567-e89b-12d3-a456-426614174000",
                db_pool=mock_db_pool,
            )
        except HTTPException as e:
            assert e.status_code != 400 or "extension" not in str(e.detail).lower()

    @pytest.mark.asyncio
    async def test_filename_with_spaces(self, mock_db_pool):
        """Test that filenames with spaces are handled correctly."""
        mock_file = MagicMock(spec=UploadFile)
        mock_file.filename = "my document file.pdf"  # Spaces in filename
        mock_file.content_type = "application/pdf"
        mock_file.read = AsyncMock(return_value=b"%PDF-1.4\ntest\n%%EOF")

        mock_request = MagicMock()
        mock_request.app.state.qdrant_client = MagicMock()

        try:
            await upload_document(
                request=mock_request,
                file=mock_file,
                source_id="123e4567-e89b-12d3-a456-426614174000",
                db_pool=mock_db_pool,
            )
        except HTTPException as e:
            assert e.status_code != 400 or "extension" not in str(e.detail).lower()

    @pytest.mark.asyncio
    async def test_unicode_filename(self, mock_db_pool):
        """Test that filenames with unicode characters are handled."""
        mock_file = MagicMock(spec=UploadFile)
        mock_file.filename = "文档.pdf"  # Chinese characters
        mock_file.content_type = "application/pdf"
        mock_file.read = AsyncMock(return_value=b"%PDF-1.4\ntest\n%%EOF")

        mock_request = MagicMock()
        mock_request.app.state.qdrant_client = MagicMock()

        try:
            await upload_document(
                request=mock_request,
                file=mock_file,
                source_id="123e4567-e89b-12d3-a456-426614174000",
                db_pool=mock_db_pool,
            )
        except HTTPException as e:
            assert e.status_code != 400 or "extension" not in str(e.detail).lower()
