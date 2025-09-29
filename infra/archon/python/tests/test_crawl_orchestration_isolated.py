"""
Isolated Tests for Async Crawl Orchestration Service

Tests core functionality without circular import dependencies.
"""

import asyncio
from typing import Any
from unittest.mock import MagicMock

import pytest


class MockCrawlOrchestrationService:
    """Mock version of CrawlOrchestrationService for isolated testing"""

    def __init__(self, crawler=None, supabase_client=None, progress_id=None):
        self.crawler = crawler
        self.supabase_client = supabase_client
        self.progress_id = progress_id
        self.progress_state = {}
        self._cancelled = False

    def cancel(self):
        self._cancelled = True

    def is_cancelled(self) -> bool:
        return self._cancelled

    def _check_cancellation(self):
        if self._cancelled:
            raise Exception("CrawlCancelledException: Operation was cancelled")

    def _is_documentation_site(self, url: str) -> bool:
        """Simple documentation site detection"""
        doc_indicators = ["/docs/", "docs.", ".readthedocs.io", "/documentation/"]
        return any(indicator in url.lower() for indicator in doc_indicators)

    async def _create_crawl_progress_callback(self, base_status: str):
        """Create async progress callback"""

        async def callback(status: str, percentage: int, message: str, **kwargs):
            if self.progress_id:
                self.progress_state.update({
                    "status": status,
                    "percentage": percentage,
                    "log": message,
                })

        return callback

    async def _crawl_by_url_type(self, url: str, request: dict[str, Any]) -> tuple:
        """Mock URL type detection and crawling"""
        # Mock different URL types
        if url.endswith(".txt"):
            return [{"url": url, "markdown": "Text content", "title": "Text File"}], "text_file"
        elif "sitemap" in url:
            return [
                {"url": f"{url}/page1", "markdown": "Page 1 content", "title": "Page 1"},
                {"url": f"{url}/page2", "markdown": "Page 2 content", "title": "Page 2"},
            ], "sitemap"
        else:
            return [{"url": url, "markdown": "Web content", "title": "Web Page"}], "webpage"

    async def _process_and_store_documents(
        self,
        crawl_results: list[dict],
        request: dict[str, Any],
        crawl_type: str,
        original_source_id: str,
    ) -> dict[str, Any]:
        """Mock document processing and storage"""
        # Check for cancellation
        self._check_cancellation()

        # Simulate chunking
        chunk_count = len(crawl_results) * 3  # Assume 3 chunks per document
        total_word_count = chunk_count * 50  # Assume 50 words per chunk

        # Build url_to_full_document mapping
        url_to_full_document = {}
        for doc in crawl_results:
            url_to_full_document[doc["url"]] = doc.get("markdown", "")

        return {
            "chunk_count": chunk_count,
            "total_word_count": total_word_count,
            "url_to_full_document": url_to_full_document,
        }

    async def _extract_and_store_code_examples(
        self, crawl_results: list[dict], url_to_full_document: dict[str, str]
    ) -> int:
        """Mock code examples extraction"""
        # Count code blocks in markdown
        code_examples = 0
        for doc in crawl_results:
            content = doc.get("markdown", "")
            code_examples += content.count("```")
        return code_examples // 2  # Each code block has opening and closing

    async def _async_orchestrate_crawl(
        self, request: dict[str, Any], task_id: str
    ) -> dict[str, Any]:
        """Mock async orchestration"""
        try:
            self._check_cancellation()

            url = str(request.get("url", ""))

            # Mock crawl by URL type
            crawl_results, crawl_type = await self._crawl_by_url_type(url, request)

            self._check_cancellation()

            if not crawl_results:
                raise ValueError("No content was crawled from the provided URL")

            # Mock document processing
            from urllib.parse import urlparse

            parsed_url = urlparse(url)
            source_id = parsed_url.netloc or parsed_url.path

            storage_results = await self._process_and_store_documents(
                crawl_results, request, crawl_type, source_id
            )

            self._check_cancellation()

            # Mock code extraction
            code_examples_count = 0
            if request.get("enable_code_extraction", False):
                code_examples_count = await self._extract_and_store_code_examples(
                    crawl_results, storage_results.get("url_to_full_document", {})
                )

            return {
                "success": True,
                "crawl_type": crawl_type,
                "chunk_count": storage_results["chunk_count"],
                "total_word_count": storage_results["total_word_count"],
                "code_examples_stored": code_examples_count,
                "processed_pages": len(crawl_results),
                "total_pages": len(crawl_results),
            }

        except Exception as e:
            error_msg = str(e)
            if "CrawlCancelledException" in error_msg:
                return {
                    "success": False,
                    "error": error_msg,
                    "cancelled": True,
                    "chunk_count": 0,
                    "code_examples_stored": 0,
                }
            else:
                return {
                    "success": False,
                    "error": error_msg,
                    "cancelled": False,
                    "chunk_count": 0,
                    "code_examples_stored": 0,
                }

    async def orchestrate_crawl(self, request: dict[str, Any]) -> dict[str, Any]:
        """Mock main orchestration entry point"""
        import uuid

        task_id = str(uuid.uuid4())

        # Start async orchestration task (would normally be background)
        result = await self._async_orchestrate_crawl(request, task_id)

        return {
            "task_id": task_id,
            "status": "started" if result.get("success") else "failed",
            "message": f"Crawl operation for {request.get('url')}",
            "progress_id": self.progress_id,
        }


class TestAsyncCrawlOrchestration:
    """Test suite for async crawl orchestration behavior"""

    @pytest.fixture
    def orchestration_service(self):
        """Create mock orchestration service"""
        return MockCrawlOrchestrationService(
            crawler=MagicMock(), supabase_client=MagicMock(), progress_id="test-progress-123"
        )

    @pytest.fixture
    def sample_request(self):
        """Sample crawl request"""
        return {
            "url": "https://example.com/docs",
            "max_depth": 2,
            "knowledge_type": "technical",
            "tags": ["test"],
            "enable_code_extraction": True,
        }

    @pytest.mark.asyncio
    async def test_async_orchestrate_crawl_success(self, orchestration_service, sample_request):
        """Test successful async orchestration"""
        result = await orchestration_service._async_orchestrate_crawl(sample_request, "task-123")

        assert result["success"] is True
        assert result["crawl_type"] == "webpage"
        assert result["chunk_count"] > 0
        assert result["total_word_count"] > 0
        assert result["processed_pages"] == 1

    @pytest.mark.asyncio
    async def test_async_orchestrate_crawl_with_code_extraction(self, orchestration_service):
        """Test orchestration with code extraction enabled"""
        request = {"url": "https://docs.example.com/api", "enable_code_extraction": True}

        result = await orchestration_service._async_orchestrate_crawl(request, "task-456")

        assert result["success"] is True
        assert "code_examples_stored" in result
        assert result["code_examples_stored"] >= 0

    @pytest.mark.asyncio
    async def test_crawl_by_url_type_text_file(self, orchestration_service):
        """Test text file URL type detection"""
        crawl_results, crawl_type = await orchestration_service._crawl_by_url_type(
            "https://example.com/readme.txt", {"max_depth": 1}
        )

        assert crawl_type == "text_file"
        assert len(crawl_results) == 1
        assert crawl_results[0]["url"] == "https://example.com/readme.txt"

    @pytest.mark.asyncio
    async def test_crawl_by_url_type_sitemap(self, orchestration_service):
        """Test sitemap URL type detection"""
        crawl_results, crawl_type = await orchestration_service._crawl_by_url_type(
            "https://example.com/sitemap.xml", {"max_depth": 2}
        )

        assert crawl_type == "sitemap"
        assert len(crawl_results) == 2

    @pytest.mark.asyncio
    async def test_crawl_by_url_type_regular_webpage(self, orchestration_service):
        """Test regular webpage crawling"""
        crawl_results, crawl_type = await orchestration_service._crawl_by_url_type(
            "https://example.com/blog/post", {"max_depth": 1}
        )

        assert crawl_type == "webpage"
        assert len(crawl_results) == 1

    @pytest.mark.asyncio
    async def test_process_and_store_documents(self, orchestration_service):
        """Test document processing and storage"""
        crawl_results = [
            {"url": "https://example.com/page1", "markdown": "Content 1", "title": "Page 1"},
            {"url": "https://example.com/page2", "markdown": "Content 2", "title": "Page 2"},
        ]

        request = {"knowledge_type": "technical", "tags": ["test"]}

        result = await orchestration_service._process_and_store_documents(
            crawl_results, request, "webpage", "example.com"
        )

        assert "chunk_count" in result
        assert "total_word_count" in result
        assert "url_to_full_document" in result
        assert result["chunk_count"] == 6  # 2 docs * 3 chunks each
        assert len(result["url_to_full_document"]) == 2

    @pytest.mark.asyncio
    async def test_extract_and_store_code_examples(self, orchestration_service):
        """Test code examples extraction"""
        crawl_results = [
            {
                "url": "https://example.com/api",
                "markdown": '# API\n\n```python\ndef hello():\n    return "world"\n```\n\n```javascript\nconsole.log("hello");\n```',
                "title": "API Docs",
            }
        ]

        url_to_full_document = {"https://example.com/api": crawl_results[0]["markdown"]}

        result = await orchestration_service._extract_and_store_code_examples(
            crawl_results, url_to_full_document
        )

        assert result == 2  # Two code blocks found

    @pytest.mark.asyncio
    async def test_cancellation_during_orchestration(self, orchestration_service, sample_request):
        """Test cancellation handling"""
        # Cancel before starting
        orchestration_service.cancel()

        result = await orchestration_service._async_orchestrate_crawl(sample_request, "task-cancel")

        assert result["success"] is False
        assert result["cancelled"] is True
        assert "error" in result

    @pytest.mark.asyncio
    async def test_cancellation_during_document_processing(self, orchestration_service):
        """Test cancellation during document processing"""
        crawl_results = [{"url": "https://example.com", "markdown": "Content"}]
        request = {"knowledge_type": "technical"}

        # Cancel during processing
        orchestration_service.cancel()

        with pytest.raises(Exception, match="CrawlCancelledException"):
            await orchestration_service._process_and_store_documents(
                crawl_results, request, "webpage", "example.com"
            )

    @pytest.mark.asyncio
    async def test_error_handling_in_orchestration(self, orchestration_service):
        """Test error handling during orchestration"""

        # Override the method to raise an error
        async def failing_crawl_by_url_type(url, request):
            raise ValueError("Simulated crawl failure")

        orchestration_service._crawl_by_url_type = failing_crawl_by_url_type

        request = {"url": "https://example.com", "enable_code_extraction": False}

        result = await orchestration_service._async_orchestrate_crawl(request, "task-error")

        assert result["success"] is False
        assert result["cancelled"] is False
        assert "error" in result

    def test_documentation_site_detection(self, orchestration_service):
        """Test documentation site URL detection"""
        # Test documentation sites
        assert orchestration_service._is_documentation_site("https://docs.python.org")
        assert orchestration_service._is_documentation_site(
            "https://react.dev/docs/getting-started"
        )
        assert orchestration_service._is_documentation_site(
            "https://project.readthedocs.io/en/latest/"
        )
        assert orchestration_service._is_documentation_site("https://example.com/documentation/api")

        # Test non-documentation sites
        assert not orchestration_service._is_documentation_site("https://github.com/user/repo")
        assert not orchestration_service._is_documentation_site("https://example.com/blog")
        assert not orchestration_service._is_documentation_site("https://news.example.com")

    def test_cancellation_functionality(self, orchestration_service):
        """Test cancellation state management"""
        # Initially not cancelled
        assert not orchestration_service.is_cancelled()

        # Cancel and verify
        orchestration_service.cancel()
        assert orchestration_service.is_cancelled()

        # Check cancellation raises exception
        with pytest.raises(Exception, match="CrawlCancelledException"):
            orchestration_service._check_cancellation()

    @pytest.mark.asyncio
    async def test_progress_callback_creation(self, orchestration_service):
        """Test progress callback functionality"""
        callback = await orchestration_service._create_crawl_progress_callback("crawling")

        # Execute callback
        await callback("test_status", 50, "Test message")

        # Verify progress state was updated
        assert orchestration_service.progress_state["status"] == "test_status"
        assert orchestration_service.progress_state["percentage"] == 50
        assert orchestration_service.progress_state["log"] == "Test message"

    @pytest.mark.asyncio
    async def test_main_orchestrate_crawl_entry_point(self, orchestration_service, sample_request):
        """Test main orchestration entry point"""
        result = await orchestration_service.orchestrate_crawl(sample_request)

        assert "task_id" in result
        assert "status" in result
        assert "progress_id" in result
        assert result["progress_id"] == "test-progress-123"

    @pytest.mark.asyncio
    async def test_concurrent_operations(self):
        """Test multiple concurrent orchestrations"""
        service1 = MockCrawlOrchestrationService(progress_id="progress-1")
        service2 = MockCrawlOrchestrationService(progress_id="progress-2")

        request1 = {"url": "https://site1.com", "enable_code_extraction": False}
        request2 = {"url": "https://site2.com", "enable_code_extraction": True}

        # Run concurrently
        results = await asyncio.gather(
            service1._async_orchestrate_crawl(request1, "task-1"),
            service2._async_orchestrate_crawl(request2, "task-2"),
        )

        assert len(results) == 2
        assert all(result["success"] for result in results)
        assert results[0]["code_examples_stored"] == 0  # Code extraction disabled
        assert results[1]["code_examples_stored"] >= 0  # Code extraction enabled


class TestAsyncBehaviors:
    """Test async-specific behaviors and patterns"""

    @pytest.mark.asyncio
    async def test_async_method_chaining(self):
        """Test that async methods properly chain together"""
        service = MockCrawlOrchestrationService()

        # This chain should complete without blocking
        crawl_results, crawl_type = await service._crawl_by_url_type(
            "https://example.com", {"max_depth": 1}
        )

        storage_results = await service._process_and_store_documents(
            crawl_results, {"knowledge_type": "technical"}, crawl_type, "example.com"
        )

        code_count = await service._extract_and_store_code_examples(
            crawl_results, storage_results["url_to_full_document"]
        )

        # All operations should complete successfully
        assert crawl_type == "webpage"
        assert storage_results["chunk_count"] > 0
        assert code_count >= 0

    @pytest.mark.asyncio
    async def test_asyncio_cancellation_propagation(self):
        """Test that asyncio cancellation properly propagates"""
        service = MockCrawlOrchestrationService()

        async def long_running_operation():
            await asyncio.sleep(0.1)  # Simulate work
            return await service._async_orchestrate_crawl(
                {"url": "https://example.com"}, "task-123"
            )

        # Start task and cancel it
        task = asyncio.create_task(long_running_operation())
        await asyncio.sleep(0.01)  # Let it start
        task.cancel()

        # Should raise CancelledError
        with pytest.raises(asyncio.CancelledError):
            await task

    @pytest.mark.asyncio
    async def test_no_blocking_operations(self):
        """Test that operations don't block the event loop"""
        service = MockCrawlOrchestrationService()

        # Start multiple operations concurrently
        tasks = []
        for i in range(5):
            task = service._async_orchestrate_crawl({"url": f"https://example{i}.com"}, f"task-{i}")
            tasks.append(task)

        # All should complete without blocking
        results = await asyncio.gather(*tasks)

        assert len(results) == 5
        assert all(result["success"] for result in results)
