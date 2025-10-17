#!/usr/bin/env python3
"""Quick test script for recursive crawling feature.

This script tests the recursive crawling implementation by:
1. Creating a test source
2. Starting a recursive crawl with max_pages=5, max_depth=2
3. Monitoring progress
4. Verifying results

Run from host:
    docker exec rag-backend python /app/test_recursive_crawl.py
"""
import asyncio
import asyncpg
import os
from uuid import UUID

from src.services.crawler.crawl_service import CrawlerService

async def test_recursive_crawl():
    """Test recursive crawling with real database."""

    # Connect to database
    db_url = os.getenv("DATABASE_URL", "postgresql://raguser:ragpassword@postgres:5432/ragservice")
    pool = await asyncpg.create_pool(db_url)

    try:
        # Create test source
        async with pool.acquire() as conn:
            row = await conn.fetchrow(
                """
                INSERT INTO sources (source_type, url, status, metadata)
                VALUES ('crawl', $1, 'active', '{}'::jsonb)
                RETURNING id
                """,
                "https://docs.python.org/3/",
            )
            source_id = row["id"]

        print(f"✅ Created test source: {source_id}")

        # Initialize crawler service
        crawler = CrawlerService(db_pool=pool)

        # Start recursive crawl
        print("\n🕷️  Starting recursive crawl...")
        print("   URL: https://docs.python.org/3/library/asyncio.html")
        print("   Max Pages: 5")
        print("   Max Depth: 2 (will follow links 2 levels deep)")
        print()

        success, result = await crawler.crawl_website(
            source_id=source_id,
            url="https://docs.python.org/3/library/asyncio.html",
            max_pages=5,
            recursive=True,  # Enable recursive crawling
        )

        if success:
            print(f"\n✅ Crawl completed successfully!")
            print(f"   Job ID: {result['job_id']}")
            print(f"   Pages Crawled: {result['pages_crawled']}")
            print(f"   Content Size: {len(result['content']):,} chars")
            print(f"   Crawl Time: {result['crawl_time_ms']}ms")
            print(f"   Message: {result['message']}")

            # Verify crawl job details
            async with pool.acquire() as conn:
                job = await conn.fetchrow(
                    """
                    SELECT status, pages_crawled, pages_total, max_depth,
                           current_depth, error_count
                    FROM crawl_jobs
                    WHERE id = $1
                    """,
                    UUID(result['job_id'])
                )

            print(f"\n📊 Crawl Job Details:")
            print(f"   Status: {job['status']}")
            print(f"   Pages Crawled: {job['pages_crawled']}")
            print(f"   Pages Total (discovered): {job['pages_total']}")
            print(f"   Max Depth: {job['max_depth']}")
            print(f"   Current Depth: {job['current_depth']}")
            print(f"   Error Count: {job['error_count']}")

            # Cleanup
            async with pool.acquire() as conn:
                await conn.execute("DELETE FROM sources WHERE id = $1", source_id)

            print(f"\n🧹 Cleaned up test source")

        else:
            print(f"\n❌ Crawl failed: {result.get('error')}")

    finally:
        await pool.close()

if __name__ == "__main__":
    asyncio.run(test_recursive_crawl())
