# Source: infra/rag-service/backend/src/api/routes/documents.py
# Lines: 39-173
# Pattern: File upload validation with size, type, and security checks
# Extracted: 2025-10-16
# Relevance: 9/10

"""Document upload validation patterns.

This example shows:
- File extension validation
- File size limits
- MIME type checking
- Error handling with user-friendly messages

Key security patterns:
- Extension whitelist
- Size limit enforcement
- MIME type validation
- Magic byte checking (TODO in original)

Pattern: Defensive file upload validation
"""

from typing import Optional
from fastapi import APIRouter, HTTPException, UploadFile, File, Form
import logging

logger = logging.getLogger(__name__)

# File upload configuration
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB
ALLOWED_EXTENSIONS = [".pdf", ".docx", ".txt", ".md", ".html"]
ALLOWED_MIME_TYPES = [
    "application/pdf",
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    "text/plain",
    "text/markdown",
    "text/html",
]


async def upload_document_validation_example(
    file: UploadFile = File(..., description="Document file to upload"),
    source_id: str = Form(..., description="Source UUID where document belongs"),
    title: Optional[str] = Form(None, description="Optional document title"),
):
    """Upload document with comprehensive validation.

    This example demonstrates:
    1. File extension validation
    2. File size validation
    3. MIME type checking
    4. User-friendly error messages with suggestions
    """
    try:
        # Validate file extension
        filename = file.filename or "unknown"
        file_extension = "." + filename.split(".")[-1].lower() if "." in filename else ""

        if file_extension not in ALLOWED_EXTENSIONS:
            raise HTTPException(
                status_code=400,
                detail={
                    "success": False,
                    "error": "Invalid file type",
                    "detail": f"File extension '{file_extension}' not allowed",
                    "suggestion": f"Upload one of: {', '.join(ALLOWED_EXTENSIONS)}",
                },
            )

        # Read file content for size validation
        # NOTE: We read the full file here for validation. For very large files,
        # consider streaming validation instead.
        file_content = await file.read()

        # Validate file size
        if len(file_content) > MAX_FILE_SIZE:
            raise HTTPException(
                status_code=413,
                detail={
                    "success": False,
                    "error": "File too large",
                    "detail": f"File size {len(file_content)} bytes exceeds max {MAX_FILE_SIZE} bytes",
                    "suggestion": "Compress file or split into smaller documents",
                },
            )

        # TODO: Add magic byte validation here (python-magic)
        # For now, we rely on extension + MIME type check

        # Validate MIME type
        content_type = file.content_type or ""
        if content_type and content_type not in ALLOWED_MIME_TYPES:
            logger.warning(
                f"File uploaded with unexpected MIME type: {content_type} "
                f"(filename: {filename}, extension: {file_extension})"
            )
            # Don't reject - extension validation is primary check

        # Determine document type from extension
        document_type_mapping = {
            ".pdf": "pdf",
            ".docx": "docx",
            ".txt": "text",
            ".md": "markdown",
            ".html": "html",
        }
        document_type = document_type_mapping.get(file_extension, "text")

        # Use provided title or default to filename
        document_title = title or filename

        logger.info(
            f"Document validation passed: {filename} "
            f"(type: {document_type}, size: {len(file_content)} bytes)"
        )

        return {
            "filename": filename,
            "document_type": document_type,
            "title": document_title,
            "size": len(file_content),
            "content_type": content_type,
        }

    except HTTPException:
        raise  # Re-raise HTTP exceptions as-is

    except Exception as e:
        logger.error(f"Document validation error: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail={
                "success": False,
                "error": "Failed to validate document",
                "detail": str(e),
                "suggestion": "Check server logs for details",
            },
        )


# Test example usage
async def test_file_upload_validation():
    """Example test demonstrating file upload validation testing."""
    from unittest.mock import MagicMock

    # Create mock file that exceeds size limit
    mock_file = MagicMock(spec=UploadFile)
    mock_file.filename = "test.pdf"
    mock_file.content_type = "application/pdf"
    mock_file.read = lambda: b"x" * (MAX_FILE_SIZE + 1)  # Too large

    try:
        await upload_document_validation_example(
            file=mock_file,
            source_id="123e4567-e89b-12d3-a456-426614174000",
            title="Test Document"
        )
        assert False, "Should have raised HTTPException"
    except HTTPException as e:
        assert e.status_code == 413
        assert "too large" in str(e.detail).lower()
        print("✅ File size validation works correctly")

    # Create mock file with invalid extension
    mock_file2 = MagicMock(spec=UploadFile)
    mock_file2.filename = "test.exe"  # Invalid extension
    mock_file2.content_type = "application/x-msdownload"
    mock_file2.read = lambda: b"test content"

    try:
        await upload_document_validation_example(
            file=mock_file2,
            source_id="123e4567-e89b-12d3-a456-426614174000",
            title="Test Document"
        )
        assert False, "Should have raised HTTPException"
    except HTTPException as e:
        assert e.status_code == 400
        assert "invalid file type" in str(e.detail).lower()
        print("✅ File extension validation works correctly")
