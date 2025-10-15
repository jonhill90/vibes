"""Web Crawling Service using Crawl4AI with Playwright.

This service implements web crawling for knowledge base ingestion with:
1. Playwright-based AsyncWebCrawler with memory management
2. Rate limiting (2-3 second delays) to avoid bans
3. Exponential backoff for failed pages (3 retries max)
4. Crawl job tracking in database
5. Integration with ingestion pipeline

Critical Gotchas Addressed:
- Gotcha #9: Use async context manager for AsyncWebCrawler to prevent memory leaks
- Gotcha #9: Limit concurrent browsers to 3 (200MB each = 600MB total)
- Gotcha #8: Always use async with pool.acquire() for connection management
- Gotcha #3: Use $1, $2 placeholders (asyncpg style, NOT %s)

Pattern: Crawl4AI docs https://docs.crawl4ai.com/
Reference: prps/rag_service_completion.md (Task 3, lines 976-1021)
"""

import asyncio
import logging
import time
from typing import Any
from uuid import UUID

import asyncpg
from crawl4ai import AsyncWebCrawler, BrowserConfig

logger = logging.getLogger(__name__)


class CrawlerService:
    """Web crawling service with memory management and rate limiting.

    This service manages web crawling operations with:
    - Memory-safe browser management (max 3 concurrent browsers)
    - Rate limiting (2-3 second delays between requests)
    - Exponential backoff for failed pages (3 retries max)
    - Crawl job tracking in database
    - Result truncation (100K chars max) to prevent memory issues

    CRITICAL PATTERN (Gotcha #9):
    Always use async context manager for AsyncWebCrawler to ensure
    browser cleanup. Without this, browsers leak 200MB each and cause OOM.

    Usage:
        crawler_service = CrawlerService(
            db_pool=db_pool,
            max_concurrent=3,  # Max concurrent browsers (600MB RAM)
        )

        # Crawl single URL
        markdown = await crawler_service.crawl_url("https://example.com")

        # Crawl with job tracking
        success, result = await crawler_service.crawl_website(
            source_id=source_uuid,
            url="https://example.com",
            max_pages=10,
        )

    Attributes:
        db_pool: asyncpg connection pool for database operations
        semaphore: Limits concurrent browsers to prevent memory exhaustion
        browser_config: Playwright browser configuration with memory optimization
        rate_limit_delay: Delay between requests (2-3 seconds)
        max_retries: Maximum retry attempts for failed pages (3)
    """

    def __init__(
        self,
        db_pool: asyncpg.Pool,
        max_concurrent: int = 3,
        rate_limit_delay: float = 2.5,
        max_retries: int = 3,
    ):
        """Initialize CrawlerService with memory and rate limiting.

        Args:
            db_pool: asyncpg connection pool for PostgreSQL
            max_concurrent: Max concurrent browser instances (default 3 = ~600MB RAM)
            rate_limit_delay: Delay between requests in seconds (default 2.5)
            max_retries: Max retry attempts for failed pages (default 3)

        Critical Gotcha #9:
        Limit concurrent browsers to 3 (200MB each) to stay under 1GB total.
        Each browser instance consumes ~200MB RAM.
        """
        self.db_pool = db_pool
        self.rate_limit_delay = rate_limit_delay
        self.max_retries = max_retries

        # CRITICAL (Gotcha #9): Semaphore limits concurrent browsers
        self.semaphore = asyncio.Semaphore(max_concurrent)

        # Browser configuration with memory-saving flags
        self.browser_config = BrowserConfig(
            headless=True,
            verbose=False,
            extra_args=[
                "--disable-dev-shm-usage",  # Use /tmp instead of /dev/shm
                "--disable-gpu",  # No GPU in headless mode
                "--no-sandbox",  # Required for Docker
                "--disable-web-security",  # Allow cross-origin requests
                "--disable-features=IsolateOrigins,site-per-process",  # Reduce memory
            ],
        )

        logger.info(
            f"CrawlerService initialized: max_concurrent={max_concurrent}, "
            f"rate_limit={rate_limit_delay}s, max_retries={max_retries}"
        )

    async def crawl_url(self, url: str) -> str:
        """Crawl a single URL and return markdown content.

        This method:
        1. Uses async context manager for browser cleanup (Gotcha #9)
        2. Limits concurrent browsers with semaphore
        3. Implements exponential backoff for retries
        4. Truncates result to 100K chars max
        5. Applies rate limiting between requests

        Args:
            url: URL to crawl

        Returns:
            Markdown content from crawled page (max 100K chars)

        Raises:
            Exception: If crawl fails after max retries

        Critical Gotcha #9:
        MUST use async with AsyncWebCrawler to prevent memory leaks.
        Browser instances consume 200MB each and leak without cleanup.

        Example:
            markdown = await crawler_service.crawl_url("https://docs.example.com")
            print(f"Crawled {len(markdown)} characters")
        """
        async with self.semaphore:  # Limit concurrent browsers
            retry_count = 0
            last_error = None

            while retry_count <= self.max_retries:
                try:
                    # CRITICAL (Gotcha #9): Use async context manager
                    # This ensures browser cleanup even on exceptions
                    async with AsyncWebCrawler(config=self.browser_config) as crawler:
                        logger.info(
                            f"Crawling URL (attempt {retry_count + 1}/{self.max_retries + 1}): {url}"
                        )

                        # Run crawler with default configuration
                        result = await crawler.arun(url=url)

                        if result.success and result.markdown:
                            # Truncate to 100K chars to prevent memory issues
                            markdown = result.markdown[:100_000]

                            logger.info(
                                f"Successfully crawled {url}: {len(markdown)} chars "
                                f"(truncated from {len(result.markdown)} chars)"
                            )

                            # Rate limiting: delay before next request
                            await asyncio.sleep(self.rate_limit_delay)

                            return markdown
                        else:
                            error_msg = getattr(result, "error_message", "Unknown error")
                            raise Exception(f"Crawl failed: {error_msg}")

                except Exception as e:
                    last_error = e
                    retry_count += 1

                    if retry_count <= self.max_retries:
                        # Exponential backoff: 2^retry seconds (2s, 4s, 8s)
                        backoff_delay = 2**retry_count
                        logger.warning(
                            f"Crawl failed for {url} (attempt {retry_count}/{self.max_retries + 1}): {e}. "
                            f"Retrying in {backoff_delay}s..."
                        )
                        await asyncio.sleep(backoff_delay)
                    else:
                        logger.error(
                            f"Crawl failed for {url} after {retry_count} attempts: {e}"
                        )
                        raise Exception(
                            f"Crawl failed after {retry_count} retries: {last_error}"
                        )

        # Should never reach here, but satisfy type checker
        raise Exception(f"Crawl failed: {last_error}")

    async def create_crawl_job(
        self,
        source_id: UUID,
        max_pages: int = 10,
        max_depth: int = 1,
        metadata: dict[str, Any] | None = None,
    ) -> UUID:
        """Create a new crawl job record in database.

        Args:
            source_id: UUID of source this crawl belongs to
            max_pages: Maximum pages to crawl (default 10)
            max_depth: Maximum crawl depth (default 1, single page only)
            metadata: Optional metadata for crawl job

        Returns:
            UUID of created crawl job

        Critical Gotcha #3: Use $1, $2 placeholders (asyncpg)
        Critical Gotcha #8: Always use async with pool.acquire()

        Example:
            job_id = await crawler_service.create_crawl_job(
                source_id=source_uuid,
                max_pages=50,
                max_depth=2,
            )
        """
        import json

        metadata_json = json.dumps(metadata or {})

        async with self.db_pool.acquire() as conn:
            row = await conn.fetchrow(
                """
                INSERT INTO crawl_jobs (
                    source_id, status, max_pages, max_depth, metadata, created_at
                )
                VALUES ($1, $2, $3, $4, $5::jsonb, NOW())
                RETURNING id
                """,
                source_id,
                "pending",
                max_pages,
                max_depth,
                metadata_json,
            )

        job_id = row["id"]
        logger.info(f"Created crawl job: {job_id} for source {source_id}")
        return job_id

    async def update_crawl_job_status(
        self,
        job_id: UUID,
        status: str,
        pages_crawled: int | None = None,
        error_message: str | None = None,
    ) -> None:
        """Update crawl job status and metadata.

        Args:
            job_id: UUID of crawl job to update
            status: New status ('running', 'completed', 'failed', 'cancelled')
            pages_crawled: Number of pages successfully crawled
            error_message: Error message if status is 'failed'

        Critical Gotcha #3: Use $1, $2 placeholders
        Critical Gotcha #8: Always use async with

        Example:
            # Start crawl
            await crawler_service.update_crawl_job_status(
                job_id=job_uuid,
                status='running',
            )

            # Complete crawl
            await crawler_service.update_crawl_job_status(
                job_id=job_uuid,
                status='completed',
                pages_crawled=25,
            )
        """
        # Build dynamic update based on provided fields
        set_clauses = ["status = $2", "updated_at = NOW()"]
        params = [job_id, status]
        param_idx = 3

        if status == "running" and pages_crawled is None:
            # Starting crawl - set started_at
            set_clauses.append("started_at = NOW()")

        if status in ("completed", "failed", "cancelled"):
            # Ending crawl - set completed_at
            set_clauses.append("completed_at = NOW()")

        if pages_crawled is not None:
            set_clauses.append(f"pages_crawled = ${param_idx}")
            params.append(pages_crawled)
            param_idx += 1

        if error_message is not None:
            set_clauses.append(f"error_message = ${param_idx}")
            params.append(error_message)
            param_idx += 1

        query = f"""
            UPDATE crawl_jobs
            SET {', '.join(set_clauses)}
            WHERE id = $1
        """

        async with self.db_pool.acquire() as conn:
            await conn.execute(query, *params)

        logger.info(f"Updated crawl job {job_id}: status={status}, pages={pages_crawled}")

    async def crawl_website(
        self,
        source_id: UUID,
        url: str,
        max_pages: int = 10,
        recursive: bool = False,
    ) -> tuple[bool, dict[str, Any]]:
        """Crawl a website and track job in database.

        This is the high-level entry point for crawling operations. It:
        1. Creates crawl job record (status='pending')
        2. Updates to 'running' and sets started_at
        3. Crawls URL(s) with rate limiting and retries
        4. Updates to 'completed' or 'failed' on finish
        5. Returns success status and metadata

        For now, only single-page crawling is implemented (recursive=False).
        Multi-page crawling will be added later.

        Args:
            source_id: UUID of source this crawl belongs to
            url: Starting URL to crawl
            max_pages: Maximum pages to crawl (default 10)
            recursive: If True, follow links (not yet implemented)

        Returns:
            Tuple of (success, result_dict) where result_dict contains:
                On success:
                - job_id: UUID of crawl job
                - pages_crawled: Number of pages successfully crawled
                - content: Markdown content (truncated to 100K chars)
                On failure:
                - error: Error message
                - job_id: UUID of crawl job (if created)

        Example:
            success, result = await crawler_service.crawl_website(
                source_id=source_uuid,
                url="https://docs.example.com",
                max_pages=50,
            )

            if success:
                job_id = result["job_id"]
                content = result["content"]
                print(f"Crawled {len(content)} chars, job {job_id}")
            else:
                print(f"Error: {result['error']}")
        """
        start_time = time.time()

        # Create crawl job
        try:
            job_id = await self.create_crawl_job(
                source_id=source_id,
                max_pages=max_pages,
                max_depth=2 if recursive else 1,
                metadata={"url": url, "recursive": recursive},
            )
        except Exception as e:
            logger.error(f"Failed to create crawl job: {e}", exc_info=True)
            return False, {"error": f"Failed to create crawl job: {str(e)}"}

        # Update to 'running'
        try:
            await self.update_crawl_job_status(job_id=job_id, status="running")
        except Exception as e:
            logger.error(f"Failed to update job status: {e}", exc_info=True)
            return False, {
                "error": f"Failed to start crawl job: {str(e)}",
                "job_id": str(job_id),
            }

        # Crawl URL
        try:
            if recursive:
                # TODO: Implement recursive crawling in future iteration
                # For now, just crawl the single page
                logger.warning(
                    f"Recursive crawling not yet implemented for job {job_id}. "
                    "Crawling single page only."
                )

            # Crawl single page
            markdown = await self.crawl_url(url)

            # Update to 'completed'
            await self.update_crawl_job_status(
                job_id=job_id, status="completed", pages_crawled=1
            )

            elapsed_ms = int((time.time() - start_time) * 1000)

            logger.info(
                f"Crawl job {job_id} completed: 1 page, {len(markdown)} chars, {elapsed_ms}ms"
            )

            return True, {
                "job_id": str(job_id),
                "pages_crawled": 1,
                "content": markdown,
                "crawl_time_ms": elapsed_ms,
                "message": "Website crawled successfully",
            }

        except Exception as e:
            # Update to 'failed'
            error_msg = str(e)
            try:
                await self.update_crawl_job_status(
                    job_id=job_id, status="failed", error_message=error_msg
                )
            except Exception as update_error:
                logger.error(
                    f"Failed to update job status to failed: {update_error}",
                    exc_info=True,
                )

            logger.error(f"Crawl job {job_id} failed: {e}", exc_info=True)

            return False, {
                "error": f"Crawl failed: {error_msg}",
                "job_id": str(job_id),
            }
