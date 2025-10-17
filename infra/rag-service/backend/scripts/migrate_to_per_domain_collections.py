#!/usr/bin/env python3
"""Migration script: Migrate existing sources to per-domain collections.

This script migrates the RAG service from shared global collections (AI_DOCUMENTS,
AI_CODE, AI_MEDIA) to per-source domain-specific collections (e.g., AI_Knowledge_documents,
Network_Security_code).

PRP Reference: prps/per_domain_collections.md (Lines 456-507, Migration Strategy)

Usage:
    # Dry run (preview only, no changes)
    python scripts/migrate_to_per_domain_collections.py --dry-run

    # Execute migration
    python scripts/migrate_to_per_domain_collections.py

    # With custom database URL
    python scripts/migrate_to_per_domain_collections.py --database-url postgresql://...

    # Verbose logging
    python scripts/migrate_to_per_domain_collections.py -v

Migration Steps:
    1. Read all sources from database (with collection_names populated by Migration 004)
    2. Connect to Qdrant and verify connection
    3. For each source, create Qdrant collections using collection_names mapping
    4. Create payload index for source_id filtering on each collection
    5. Log progress and errors
    6. Optional: Migrate vectors from old shared collections (future enhancement)

Requirements:
    - Migration 004 must be applied (collection_names column exists)
    - Qdrant server must be running and accessible
    - Database must be accessible
    - OpenAI API key must be configured (for embedding dimensions)

Rollback:
    - Collections can be manually deleted from Qdrant if needed
    - Database schema rollback: See Migration 004 rollback section
"""

import argparse
import asyncio
import json
import logging
import sys
from pathlib import Path
from typing import Any

import asyncpg
from qdrant_client import AsyncQdrantClient
from qdrant_client.models import Distance, VectorParams, PayloadSchemaType

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from config.settings import settings

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler("migration_to_per_domain_collections.log"),
    ],
)
logger = logging.getLogger(__name__)


class MigrationStats:
    """Track migration statistics."""

    def __init__(self) -> None:
        self.sources_processed = 0
        self.collections_created = 0
        self.collections_already_exist = 0
        self.collections_failed = 0
        self.errors: list[str] = []

    def log_summary(self) -> None:
        """Log migration summary."""
        logger.info("=" * 60)
        logger.info("MIGRATION SUMMARY")
        logger.info("=" * 60)
        logger.info(f"Sources Processed: {self.sources_processed}")
        logger.info(f"Collections Created: {self.collections_created}")
        logger.info(f"Collections Already Exist: {self.collections_already_exist}")
        logger.info(f"Collections Failed: {self.collections_failed}")
        logger.info(f"Errors: {len(self.errors)}")
        if self.errors:
            logger.error("Error Details:")
            for error in self.errors:
                logger.error(f"  - {error}")
        logger.info("=" * 60)


async def get_all_sources(db_pool: asyncpg.Pool) -> list[dict[str, Any]]:
    """Fetch all sources from database with collection_names.

    Args:
        db_pool: Database connection pool

    Returns:
        List of source records with id, collection_names, enabled_collections

    Raises:
        Exception: If database query fails
    """
    query = """
        SELECT
            id,
            metadata->>'title' as title,
            collection_names,
            enabled_collections
        FROM sources
        WHERE collection_names IS NOT NULL
          AND collection_names != '{}'::JSONB
        ORDER BY created_at ASC
    """

    async with db_pool.acquire() as conn:
        rows = await conn.fetch(query)

    sources = []
    for row in rows:
        sources.append({
            "id": str(row["id"]),
            "title": row["title"],
            "collection_names": json.loads(row["collection_names"]),
            "enabled_collections": row["enabled_collections"],
        })

    logger.info(f"Found {len(sources)} sources with collection_names")
    return sources


async def create_qdrant_collection(
    qdrant_client: AsyncQdrantClient,
    collection_name: str,
    dimension: int,
    stats: MigrationStats,
    dry_run: bool = False,
) -> bool:
    """Create a Qdrant collection with proper vector configuration.

    Args:
        qdrant_client: Qdrant async client
        collection_name: Name of collection to create
        dimension: Vector dimension for this collection type
        stats: Migration statistics tracker
        dry_run: If True, only log actions without executing

    Returns:
        True if collection created, False if already exists or failed
    """
    try:
        # Check if collection already exists
        collections = await qdrant_client.get_collections()
        existing_names = [c.name for c in collections.collections]

        if collection_name in existing_names:
            logger.info(f"  ✓ Collection already exists: {collection_name}")
            stats.collections_already_exist += 1
            return False

        if dry_run:
            logger.info(f"  [DRY RUN] Would create collection: {collection_name} ({dimension}d)")
            stats.collections_created += 1
            return True

        # Create collection with proper vector configuration
        await qdrant_client.create_collection(
            collection_name=collection_name,
            vectors_config=VectorParams(
                size=dimension,
                distance=Distance.COSINE
            )
        )

        # Create payload index for source_id filtering
        # This enables efficient filtering by source in search queries
        await qdrant_client.create_payload_index(
            collection_name=collection_name,
            field_name="source_id",
            field_schema=PayloadSchemaType.KEYWORD
        )

        logger.info(f"  ✓ Created collection: {collection_name} ({dimension}d, source_id indexed)")
        stats.collections_created += 1
        return True

    except Exception as e:
        error_msg = f"Failed to create collection {collection_name}: {e}"
        logger.error(f"  ✗ {error_msg}")
        stats.errors.append(error_msg)
        stats.collections_failed += 1
        return False


async def migrate_source(
    source: dict[str, Any],
    qdrant_client: AsyncQdrantClient,
    stats: MigrationStats,
    dry_run: bool = False,
) -> None:
    """Migrate a single source to per-domain collections.

    Args:
        source: Source record with collection_names mapping
        qdrant_client: Qdrant async client
        stats: Migration statistics tracker
        dry_run: If True, only log actions without executing
    """
    logger.info(f"Processing source: {source['title']} (ID: {source['id']})")
    logger.info(f"  Enabled collections: {source['enabled_collections']}")
    logger.info(f"  Collection names: {source['collection_names']}")

    collection_names = source["collection_names"]

    if not collection_names:
        logger.warning(f"  ⚠ No collection_names found for source {source['title']}")
        stats.errors.append(f"Source {source['title']}: No collection_names")
        return

    # Create each collection for this source
    for collection_type, collection_name in collection_names.items():
        # Get dimension for this collection type
        dimension = settings.COLLECTION_DIMENSIONS.get(collection_type)
        if not dimension:
            error_msg = f"Unknown collection type: {collection_type}"
            logger.error(f"  ✗ {error_msg}")
            stats.errors.append(error_msg)
            continue

        # Create collection in Qdrant
        await create_qdrant_collection(
            qdrant_client=qdrant_client,
            collection_name=collection_name,
            dimension=dimension,
            stats=stats,
            dry_run=dry_run,
        )

    stats.sources_processed += 1
    logger.info(f"  ✓ Completed source: {source['title']}")


async def verify_migration(
    db_pool: asyncpg.Pool,
    qdrant_client: AsyncQdrantClient,
) -> None:
    """Verify migration completed successfully.

    Args:
        db_pool: Database connection pool
        qdrant_client: Qdrant async client
    """
    logger.info("=" * 60)
    logger.info("VERIFYING MIGRATION")
    logger.info("=" * 60)

    # Get all sources
    sources = await get_all_sources(db_pool)

    # Get all Qdrant collections
    collections = await qdrant_client.get_collections()
    existing_collection_names = [c.name for c in collections.collections]

    # Verify each source has its collections
    missing_collections = []
    for source in sources:
        for collection_type, collection_name in source["collection_names"].items():
            if collection_name not in existing_collection_names:
                missing_collections.append({
                    "source": source["title"],
                    "collection": collection_name,
                })

    if missing_collections:
        logger.warning(f"⚠ Found {len(missing_collections)} missing collections:")
        for missing in missing_collections:
            logger.warning(f"  - {missing['source']}: {missing['collection']}")
    else:
        logger.info("✓ All source collections exist in Qdrant")

    # Log collection count summary
    total_expected = sum(len(s["collection_names"]) for s in sources)
    logger.info(f"Expected collections: {total_expected}")
    logger.info(f"Qdrant collections: {len(existing_collection_names)}")
    logger.info("=" * 60)


async def run_migration(
    database_url: str | None = None,
    qdrant_url: str | None = None,
    dry_run: bool = False,
) -> None:
    """Run the full migration.

    Args:
        database_url: Database connection URL (uses settings if None)
        qdrant_url: Qdrant server URL (uses settings if None)
        dry_run: If True, only log actions without executing
    """
    stats = MigrationStats()

    # Use settings if URLs not provided
    db_url = database_url or settings.DATABASE_URL
    qdrant_server_url = qdrant_url or settings.QDRANT_URL

    logger.info("=" * 60)
    logger.info("STARTING MIGRATION TO PER-DOMAIN COLLECTIONS")
    logger.info("=" * 60)
    logger.info(f"Database: {db_url[:30]}...")
    logger.info(f"Qdrant: {qdrant_server_url}")
    logger.info(f"Dry Run: {dry_run}")
    logger.info("=" * 60)

    # Connect to database
    logger.info("Connecting to database...")
    db_pool = await asyncpg.create_pool(
        db_url,
        min_size=1,
        max_size=5,
    )
    if not db_pool:
        raise RuntimeError("Failed to create database pool")
    logger.info("✓ Database connected")

    # Connect to Qdrant
    logger.info("Connecting to Qdrant...")
    qdrant_client = AsyncQdrantClient(url=qdrant_server_url)
    # Test connection
    await qdrant_client.get_collections()
    logger.info("✓ Qdrant connected")

    try:
        # Get all sources
        sources = await get_all_sources(db_pool)

        if not sources:
            logger.warning("⚠ No sources found with collection_names")
            logger.warning("Make sure Migration 004 has been applied to the database")
            return

        # Migrate each source
        logger.info(f"Migrating {len(sources)} sources...")
        for source in sources:
            await migrate_source(
                source=source,
                qdrant_client=qdrant_client,
                stats=stats,
                dry_run=dry_run,
            )

        # Verify migration (skip for dry run)
        if not dry_run:
            await verify_migration(db_pool, qdrant_client)

        # Log summary
        stats.log_summary()

        if stats.collections_failed > 0:
            logger.error("Migration completed with errors - review log for details")
            sys.exit(1)
        else:
            logger.info("✓ Migration completed successfully")

    except Exception as e:
        logger.error(f"Migration failed: {e}", exc_info=True)
        stats.errors.append(f"Migration failed: {e}")
        stats.log_summary()
        sys.exit(1)

    finally:
        # Cleanup
        await db_pool.close()
        await qdrant_client.close()


def main() -> None:
    """Main entry point for migration script."""
    parser = argparse.ArgumentParser(
        description="Migrate RAG service to per-domain collections",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
    # Dry run (preview only)
    python scripts/migrate_to_per_domain_collections.py --dry-run

    # Execute migration
    python scripts/migrate_to_per_domain_collections.py

    # Custom database URL
    python scripts/migrate_to_per_domain_collections.py \\
        --database-url postgresql://user:pass@localhost:5432/ragservice

    # Verbose logging
    python scripts/migrate_to_per_domain_collections.py -v

Notes:
    - Requires Migration 004 to be applied first
    - Idempotent: safe to run multiple times (skips existing collections)
    - Logs to both console and migration_to_per_domain_collections.log
        """,
    )

    parser.add_argument(
        "--database-url",
        type=str,
        help="PostgreSQL connection URL (default: from settings)",
    )

    parser.add_argument(
        "--qdrant-url",
        type=str,
        help="Qdrant server URL (default: from settings)",
    )

    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Preview migration without making changes",
    )

    parser.add_argument(
        "-v", "--verbose",
        action="store_true",
        help="Enable verbose logging (DEBUG level)",
    )

    args = parser.parse_args()

    # Configure logging level
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
        logger.setLevel(logging.DEBUG)

    # Run migration
    try:
        asyncio.run(
            run_migration(
                database_url=args.database_url,
                qdrant_url=args.qdrant_url,
                dry_run=args.dry_run,
            )
        )
    except KeyboardInterrupt:
        logger.warning("\nMigration interrupted by user")
        sys.exit(130)
    except Exception as e:
        logger.error(f"Unexpected error: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()
