#!/usr/bin/env python3
"""
Cleanup Legacy Qdrant Collections

Removes old shared collections (AI_DOCUMENTS, AI_CODE, AI_MEDIA) that were replaced
by per-domain collections in the per_domain_collections migration.

Per-domain collections follow the pattern: {source_title}_{collection_type}
Example: DevOps_Knowledge_documents, AI_Knowledge_code

This script safely removes only the legacy global collections.
"""

import asyncio
import sys
from pathlib import Path

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from qdrant_client import AsyncQdrantClient
from config import settings

# Legacy collections to remove
LEGACY_COLLECTIONS = [
    "AI_DOCUMENTS",  # Old shared documents collection
    "AI_CODE",       # Old shared code collection
    "AI_MEDIA",      # Old shared media collection
    "documents",     # Test collection (likely orphaned)
]


async def list_collections(client: AsyncQdrantClient) -> list[str]:
    """List all collection names in Qdrant."""
    response = await client.get_collections()
    return [c.name for c in response.collections]


async def delete_collection_safe(client: AsyncQdrantClient, collection_name: str) -> bool:
    """
    Safely delete a collection from Qdrant.

    Returns:
        True if deleted successfully, False if collection doesn't exist or error occurred
    """
    try:
        await client.delete_collection(collection_name)
        print(f"✅ Deleted: {collection_name}")
        return True
    except Exception as e:
        print(f"⚠️  Failed to delete {collection_name}: {e}")
        return False


async def main():
    """Main cleanup script."""
    print("=" * 80)
    print("Legacy Qdrant Collection Cleanup")
    print("=" * 80)
    print()
    print("This script removes old shared collections that were replaced by")
    print("per-domain collections in the per_domain_collections migration.")
    print()

    # Initialize Qdrant client
    qdrant_url = settings.QDRANT_URL
    print(f"Connecting to Qdrant: {qdrant_url}")
    client = AsyncQdrantClient(url=qdrant_url)

    # List all collections
    print("\n📋 Current collections:")
    all_collections = await list_collections(client)
    for name in sorted(all_collections):
        is_legacy = name in LEGACY_COLLECTIONS
        marker = "❌ LEGACY" if is_legacy else "✅ KEEP"
        print(f"  {marker}: {name}")

    # Identify collections to remove
    to_remove = [c for c in all_collections if c in LEGACY_COLLECTIONS]

    if not to_remove:
        print("\n✅ No legacy collections found. All clean!")
        return

    print(f"\n🗑️  Collections to remove: {len(to_remove)}")
    for name in to_remove:
        print(f"  - {name}")

    # Confirm deletion
    print("\n⚠️  WARNING: This will permanently delete these collections and all their vectors!")
    response = input("\nProceed with deletion? (yes/no): ").strip().lower()

    if response != "yes":
        print("❌ Deletion cancelled.")
        return

    # Delete collections
    print("\n🔥 Deleting legacy collections...")
    deleted_count = 0

    for collection_name in to_remove:
        success = await delete_collection_safe(client, collection_name)
        if success:
            deleted_count += 1

    # Summary
    print("\n" + "=" * 80)
    print(f"✅ Cleanup complete: {deleted_count}/{len(to_remove)} collections deleted")
    print("=" * 80)

    # List remaining collections
    print("\n📋 Remaining collections:")
    remaining = await list_collections(client)
    if remaining:
        for name in sorted(remaining):
            print(f"  ✅ {name}")
    else:
        print("  (none)")

    print("\n🎉 Legacy collections cleanup complete!")
    print("\nAll remaining collections follow the per-domain naming pattern:")
    print("  {source_title}_{collection_type}")
    print()


if __name__ == "__main__":
    asyncio.run(main())
