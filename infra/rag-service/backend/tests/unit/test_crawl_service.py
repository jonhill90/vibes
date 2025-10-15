"""Unit tests for CrawlerService.

Tests cover:
1. crawl_url with mocked AsyncWebCrawler
2. Rate limiting (verify delays)
3. Retry logic (3 attempts on failure)
4. Semaphore limits (max 3 concurrent)
5. Memory cleanup (context manager called)
6. Crawl job tracking (create, update status)

Pattern: pytest-asyncio for async tests
Reference: prps/rag_service_completion.md (Task 3, Validation section)
"""

import asyncio
from unittest.mock import AsyncMock, MagicMock, patch
from uuid import uuid4

import pytest

from src.services.crawler.crawl_service import CrawlerService


@pytest.fixture
def mock_db_pool():
    """Mock asyncpg connection pool."""
    pool = MagicMock()
    conn = MagicMock()

    # Mock acquire() as async context manager
    async def mock_acquire():
        yield conn

    pool.acquire = MagicMock(return_value=mock_acquire())
    return pool


@pytest.fixture
def crawler_service(mock_db_pool):
    """Create CrawlerService with mocked dependencies."""
    return CrawlerService(
        db_pool=mock_db_pool,
        max_concurrent=3,
        rate_limit_delay=0.1,  # Short delay for testing
        max_retries=3,
    )


@pytest.mark.asyncio
async def test_crawl_url_success(crawler_service):
    """Test successful single page crawl with mocked AsyncWebCrawler."""
    mock_result = MagicMock()
    mock_result.success = True
    mock_result.markdown = "# Test Page\n\nThis is test content." * 100

    mock_crawler = MagicMock()
    mock_crawler.arun = AsyncMock(return_value=mock_result)

    # Mock AsyncWebCrawler as async context manager
    async def mock_crawler_context(config):
        return mock_crawler

    with patch(
        "src.services.crawler.crawl_service.AsyncWebCrawler"
    ) as MockAsyncWebCrawler:
        # Setup context manager
        MockAsyncWebCrawler.return_value.__aenter__ = AsyncMock(
            return_value=mock_crawler
        )
        MockAsyncWebCrawler.return_value.__aexit__ = AsyncMock(return_value=None)

        # Crawl URL
        markdown = await crawler_service.crawl_url("https://example.com")

        # Verify result
        assert isinstance(markdown, str)
        assert len(markdown) > 0
        assert "Test Page" in markdown

        # Verify crawler was called
        mock_crawler.arun.assert_called_once_with(url="https://example.com")

        # Verify context manager cleanup (browser closed)
        MockAsyncWebCrawler.return_value.__aexit__.assert_called_once()


@pytest.mark.asyncio
async def test_crawl_url_truncation(crawler_service):
    """Test that result markdown is truncated to 100K chars max."""
    # Create markdown > 100K chars
    long_markdown = "x" * 150_000

    mock_result = MagicMock()
    mock_result.success = True
    mock_result.markdown = long_markdown

    mock_crawler = MagicMock()
    mock_crawler.arun = AsyncMock(return_value=mock_result)

    with patch(
        "src.services.crawler.crawl_service.AsyncWebCrawler"
    ) as MockAsyncWebCrawler:
        MockAsyncWebCrawler.return_value.__aenter__ = AsyncMock(
            return_value=mock_crawler
        )
        MockAsyncWebCrawler.return_value.__aexit__ = AsyncMock(return_value=None)

        markdown = await crawler_service.crawl_url("https://example.com")

        # Verify truncation to 100K chars
        assert len(markdown) == 100_000
        assert len(markdown) < len(long_markdown)


@pytest.mark.asyncio
async def test_rate_limiting(crawler_service):
    """Test that rate limiting enforces 2-3 second delays between requests."""
    mock_result = MagicMock()
    mock_result.success = True
    mock_result.markdown = "Test content"

    mock_crawler = MagicMock()
    mock_crawler.arun = AsyncMock(return_value=mock_result)

    with patch(
        "src.services.crawler.crawl_service.AsyncWebCrawler"
    ) as MockAsyncWebCrawler:
        MockAsyncWebCrawler.return_value.__aenter__ = AsyncMock(
            return_value=mock_crawler
        )
        MockAsyncWebCrawler.return_value.__aexit__ = AsyncMock(return_value=None)

        # Crawl two URLs and measure time
        start_time = asyncio.get_event_loop().time()

        await crawler_service.crawl_url("https://example.com/page1")
        await crawler_service.crawl_url("https://example.com/page2")

        elapsed = asyncio.get_event_loop().time() - start_time

        # Should have at least one rate_limit_delay (0.1s for testing)
        # Two crawls = one delay between them
        assert elapsed >= 0.1, f"Rate limiting not working: elapsed {elapsed}s < 0.1s"


@pytest.mark.asyncio
async def test_retry_logic_exponential_backoff(crawler_service):
    """Test exponential backoff for failed pages (3 retries max)."""
    mock_crawler = MagicMock()

    # First 2 attempts fail, third succeeds
    call_count = 0

    async def mock_arun_with_failures(url):
        nonlocal call_count
        call_count += 1

        if call_count < 3:
            # First 2 attempts fail
            mock_result = MagicMock()
            mock_result.success = False
            mock_result.error_message = f"Attempt {call_count} failed"
            return mock_result
        else:
            # Third attempt succeeds
            mock_result = MagicMock()
            mock_result.success = True
            mock_result.markdown = "Success after retries"
            return mock_result

    mock_crawler.arun = mock_arun_with_failures

    with patch(
        "src.services.crawler.crawl_service.AsyncWebCrawler"
    ) as MockAsyncWebCrawler:
        MockAsyncWebCrawler.return_value.__aenter__ = AsyncMock(
            return_value=mock_crawler
        )
        MockAsyncWebCrawler.return_value.__aexit__ = AsyncMock(return_value=None)

        # Should succeed on third attempt
        markdown = await crawler_service.crawl_url("https://example.com")

        assert markdown == "Success after retries"
        assert call_count == 3, f"Expected 3 attempts, got {call_count}"


@pytest.mark.asyncio
async def test_retry_logic_max_retries_exceeded(crawler_service):
    """Test that crawl fails after max retries (3 attempts total)."""
    mock_result = MagicMock()
    mock_result.success = False
    mock_result.error_message = "Persistent failure"

    mock_crawler = MagicMock()
    mock_crawler.arun = AsyncMock(return_value=mock_result)

    with patch(
        "src.services.crawler.crawl_service.AsyncWebCrawler"
    ) as MockAsyncWebCrawler:
        MockAsyncWebCrawler.return_value.__aenter__ = AsyncMock(
            return_value=mock_crawler
        )
        MockAsyncWebCrawler.return_value.__aexit__ = AsyncMock(return_value=None)

        # Should fail after 4 attempts (initial + 3 retries)
        with pytest.raises(Exception) as exc_info:
            await crawler_service.crawl_url("https://example.com")

        assert "Crawl failed after" in str(exc_info.value)
        assert mock_crawler.arun.call_count == 4  # Initial + 3 retries


@pytest.mark.asyncio
async def test_semaphore_limits_concurrent_browsers(crawler_service):
    """Test that semaphore limits max 3 concurrent browser instances."""
    mock_result = MagicMock()
    mock_result.success = True
    mock_result.markdown = "Test content"

    mock_crawler = MagicMock()

    # Track concurrent calls
    concurrent_calls = 0
    max_concurrent = 0

    async def mock_arun_with_tracking(url):
        nonlocal concurrent_calls, max_concurrent
        concurrent_calls += 1
        max_concurrent = max(max_concurrent, concurrent_calls)

        # Simulate some work
        await asyncio.sleep(0.05)

        concurrent_calls -= 1
        return mock_result

    mock_crawler.arun = mock_arun_with_tracking

    with patch(
        "src.services.crawler.crawl_service.AsyncWebCrawler"
    ) as MockAsyncWebCrawler:
        MockAsyncWebCrawler.return_value.__aenter__ = AsyncMock(
            return_value=mock_crawler
        )
        MockAsyncWebCrawler.return_value.__aexit__ = AsyncMock(return_value=None)

        # Launch 10 concurrent crawls
        tasks = [
            crawler_service.crawl_url(f"https://example.com/page{i}")
            for i in range(10)
        ]

        await asyncio.gather(*tasks)

        # Verify max concurrent was <= 3 (semaphore limit)
        assert (
            max_concurrent <= 3
        ), f"Semaphore failed: max_concurrent={max_concurrent} > 3"


@pytest.mark.asyncio
async def test_memory_cleanup_context_manager(crawler_service):
    """Test that async context manager is called for browser cleanup."""
    mock_result = MagicMock()
    mock_result.success = True
    mock_result.markdown = "Test content"

    mock_crawler = MagicMock()
    mock_crawler.arun = AsyncMock(return_value=mock_result)

    with patch(
        "src.services.crawler.crawl_service.AsyncWebCrawler"
    ) as MockAsyncWebCrawler:
        # Track context manager calls
        aenter_called = False
        aexit_called = False

        async def mock_aenter(self):
            nonlocal aenter_called
            aenter_called = True
            return mock_crawler

        async def mock_aexit(self, *args):
            nonlocal aexit_called
            aexit_called = True

        MockAsyncWebCrawler.return_value.__aenter__ = mock_aenter
        MockAsyncWebCrawler.return_value.__aexit__ = mock_aexit

        await crawler_service.crawl_url("https://example.com")

        # Verify both context manager methods were called
        assert aenter_called, "Context manager __aenter__ not called"
        assert aexit_called, "Context manager __aexit__ not called (memory leak!)"


@pytest.mark.asyncio
async def test_create_crawl_job(crawler_service, mock_db_pool):
    """Test creating crawl job record in database."""
    job_id = uuid4()
    source_id = uuid4()

    # Mock database response
    mock_conn = MagicMock()
    mock_conn.fetchrow = AsyncMock(return_value={"id": job_id})

    async def mock_acquire():
        yield mock_conn

    mock_db_pool.acquire = MagicMock(return_value=mock_acquire())

    # Create crawl job
    result_job_id = await crawler_service.create_crawl_job(
        source_id=source_id, max_pages=50, max_depth=2, metadata={"test": "metadata"}
    )

    assert result_job_id == job_id

    # Verify database INSERT was called with correct parameters
    mock_conn.fetchrow.assert_called_once()
    call_args = mock_conn.fetchrow.call_args

    # Verify SQL query
    assert "INSERT INTO crawl_jobs" in call_args[0][0]
    assert "source_id" in call_args[0][0]
    assert "max_pages" in call_args[0][0]

    # Verify parameters
    assert call_args[0][1] == source_id
    assert call_args[0][2] == "pending"
    assert call_args[0][3] == 50
    assert call_args[0][4] == 2


@pytest.mark.asyncio
async def test_update_crawl_job_status(crawler_service, mock_db_pool):
    """Test updating crawl job status and metadata."""
    job_id = uuid4()

    # Mock database connection
    mock_conn = MagicMock()
    mock_conn.execute = AsyncMock()

    async def mock_acquire():
        yield mock_conn

    mock_db_pool.acquire = MagicMock(return_value=mock_acquire())

    # Update job to 'completed'
    await crawler_service.update_crawl_job_status(
        job_id=job_id, status="completed", pages_crawled=25
    )

    # Verify database UPDATE was called
    mock_conn.execute.assert_called_once()
    call_args = mock_conn.execute.call_args

    # Verify SQL query
    assert "UPDATE crawl_jobs" in call_args[0][0]
    assert "status" in call_args[0][0]
    assert "pages_crawled" in call_args[0][0]
    assert "completed_at" in call_args[0][0]

    # Verify parameters
    assert job_id in call_args[0][1:]
    assert "completed" in call_args[0][1:]
    assert 25 in call_args[0][1:]


@pytest.mark.asyncio
async def test_crawl_website_integration(crawler_service, mock_db_pool):
    """Test full crawl_website flow with job tracking."""
    source_id = uuid4()
    job_id = uuid4()

    # Mock database connection
    mock_conn = MagicMock()
    mock_conn.fetchrow = AsyncMock(return_value={"id": job_id})
    mock_conn.execute = AsyncMock()

    async def mock_acquire():
        yield mock_conn

    mock_db_pool.acquire = MagicMock(return_value=mock_acquire())

    # Mock crawler
    mock_result = MagicMock()
    mock_result.success = True
    mock_result.markdown = "# Test Page\n\nContent here."

    mock_crawler = MagicMock()
    mock_crawler.arun = AsyncMock(return_value=mock_result)

    with patch(
        "src.services.crawler.crawl_service.AsyncWebCrawler"
    ) as MockAsyncWebCrawler:
        MockAsyncWebCrawler.return_value.__aenter__ = AsyncMock(
            return_value=mock_crawler
        )
        MockAsyncWebCrawler.return_value.__aexit__ = AsyncMock(return_value=None)

        # Crawl website
        success, result = await crawler_service.crawl_website(
            source_id=source_id, url="https://example.com", max_pages=10
        )

        # Verify success
        assert success is True
        assert "job_id" in result
        assert result["pages_crawled"] == 1
        assert "content" in result
        assert "Test Page" in result["content"]

        # Verify database calls
        # 1. Create job (INSERT)
        # 2. Update to 'running' (UPDATE)
        # 3. Update to 'completed' (UPDATE)
        assert mock_conn.fetchrow.call_count == 1  # CREATE
        assert mock_conn.execute.call_count == 2  # UPDATE x2


@pytest.mark.asyncio
async def test_crawl_website_failure_handling(crawler_service, mock_db_pool):
    """Test crawl_website error handling and job status update."""
    source_id = uuid4()
    job_id = uuid4()

    # Mock database connection
    mock_conn = MagicMock()
    mock_conn.fetchrow = AsyncMock(return_value={"id": job_id})
    mock_conn.execute = AsyncMock()

    async def mock_acquire():
        yield mock_conn

    mock_db_pool.acquire = MagicMock(return_value=mock_acquire())

    # Mock crawler to always fail
    mock_result = MagicMock()
    mock_result.success = False
    mock_result.error_message = "Network error"

    mock_crawler = MagicMock()
    mock_crawler.arun = AsyncMock(return_value=mock_result)

    with patch(
        "src.services.crawler.crawl_service.AsyncWebCrawler"
    ) as MockAsyncWebCrawler:
        MockAsyncWebCrawler.return_value.__aenter__ = AsyncMock(
            return_value=mock_crawler
        )
        MockAsyncWebCrawler.return_value.__aexit__ = AsyncMock(return_value=None)

        # Crawl website (should fail)
        success, result = await crawler_service.crawl_website(
            source_id=source_id, url="https://example.com", max_pages=10
        )

        # Verify failure
        assert success is False
        assert "error" in result
        assert "job_id" in result

        # Verify database calls
        # 1. Create job (INSERT)
        # 2. Update to 'running' (UPDATE)
        # 3. Update to 'failed' (UPDATE)
        assert mock_conn.fetchrow.call_count == 1
        assert mock_conn.execute.call_count == 2

        # Verify last update was to 'failed' status
        last_call_args = mock_conn.execute.call_args_list[-1][0]
        assert "failed" in last_call_args[1:]
