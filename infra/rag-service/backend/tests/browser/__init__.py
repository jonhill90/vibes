"""Browser integration tests for RAG service frontend.

This package contains Playwright-based browser tests for validating
end-to-end user workflows in the RAG service frontend.

Test modules:
- test_document_upload.py: Document upload workflow validation
- test_search_filtering.py: Search with source filter validation
- test_delete_operations.py: Delete confirmation workflow validation

Pattern: Navigation → Interaction → Validation
Reference: .claude/patterns/browser-validation.md
"""
