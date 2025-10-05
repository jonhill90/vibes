---
argument-hint: [feature-name]
description: Archive or delete PRP planning/execution artifacts
---

# Cleanup PRP Artifacts

Archive or delete PRP planning/execution artifacts for completed features.

## Feature: $ARGUMENTS

This command manages completed PRP artifacts after execution, helping maintain a clean workspace while preserving essential files.

## What Gets Cleaned

- `prps/{feature}/planning/` - Research artifacts from generate-prp (5 files)
- `prps/{feature}/examples/` - Extracted code examples
- `prps/{feature}/execution/` - Implementation artifacts from execute-prp (3 reports)

## What Stays

- `prps/{feature}/INITIAL.md` - Original request
- `prps/{feature}/{feature}.md` - Final PRP deliverable

## Implementation

```python
import os
from datetime import datetime

feature_name = "$ARGUMENTS".strip()

# ============================================================================
# VALIDATION
# ============================================================================

if not feature_name:
    print("❌ Error: Feature name required")
    print("")
    print("Usage: /prp-cleanup <feature-name>")
    print("")
    print("Examples:")
    print("  /prp-cleanup user_auth")
    print("  /prp-cleanup web_scraper")
    exit(1)

# Security: Validate feature name (prevent command injection)
import re
if not re.match(r'^[a-zA-Z0-9_-]+$', feature_name):
    print(f"❌ Error: Invalid feature name '{feature_name}'")
    print("   Feature names must contain only: letters, numbers, hyphens, underscores")
    exit(1)

if len(feature_name) > 50:
    print(f"❌ Error: Feature name too long ({len(feature_name)} chars, max: 50)")
    exit(1)

# Check if feature exists
feature_dir = f"prps/{feature_name}"
if not os.path.exists(feature_dir):
    print(f"❌ Error: Feature not found: {feature_name}")
    print(f"   Expected directory: {feature_dir}")
    exit(1)

# ============================================================================
# SIZE CALCULATION
# ============================================================================

def get_dir_size_mb(path):
    """Calculate directory size in megabytes."""
    if not os.path.exists(path):
        return 0.0
    total = 0
    for dirpath, dirnames, filenames in os.walk(path):
        for filename in filenames:
            filepath = os.path.join(dirpath, filename)
            try:
                total += os.path.getsize(filepath)
            except:
                pass
    return total / (1024 * 1024)

def count_files(path):
    """Count files in directory."""
    if not os.path.exists(path):
        return 0
    count = 0
    for dirpath, dirnames, filenames in os.walk(path):
        count += len(filenames)
    return count

# Calculate sizes and counts
planning_dir = f"{feature_dir}/planning"
examples_dir = f"{feature_dir}/examples"
execution_dir = f"{feature_dir}/execution"

planning_size = get_dir_size_mb(planning_dir)
examples_size = get_dir_size_mb(examples_dir)
execution_size = get_dir_size_mb(execution_dir)
total_size = planning_size + examples_size + execution_size

planning_count = count_files(planning_dir)
examples_count = count_files(examples_dir)
execution_count = count_files(execution_dir)
total_count = planning_count + examples_count + execution_count

# Check if there's anything to clean
if total_count == 0:
    print(f"ℹ️  No artifacts to clean for {feature_name}")
    print(f"   The planning/, examples/, and execution/ directories are empty or don't exist.")
    exit(0)

# ============================================================================
# DISPLAY SUMMARY
# ============================================================================

print("")
print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
print(f"PRP Cleanup: {feature_name}")
print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
print("")
print("Files to clean:")
print(f"  - {feature_dir}/planning/     ({planning_count} files, {planning_size:.1f} MB)")
print(f"  - {feature_dir}/examples/     ({examples_count} files, {examples_size:.1f} MB)")
print(f"  - {feature_dir}/execution/    ({execution_count} files, {execution_size:.1f} MB)")
print(f"  Total: {total_count} files, {total_size:.1f} MB")
print("")
print("Files to keep:")

# Check what will be preserved
preserved_files = []
if os.path.exists(f"{feature_dir}/INITIAL.md"):
    preserved_files.append(f"{feature_dir}/INITIAL.md")
if os.path.exists(f"{feature_dir}/{feature_name}.md"):
    preserved_files.append(f"{feature_dir}/{feature_name}.md")
# Legacy location
if os.path.exists(f"prps/INITIAL_{feature_name}.md"):
    preserved_files.append(f"prps/INITIAL_{feature_name}.md")
if os.path.exists(f"prps/{feature_name}.md"):
    preserved_files.append(f"prps/{feature_name}.md")

if preserved_files:
    for file in preserved_files:
        print(f"  ✓ {file}")
else:
    print("  ⚠️  Warning: No INITIAL.md or PRP file found")
    print("     This may not be a completed feature.")

print("")
print("Choose action:")
print("  1. Archive (recommended) - Move to prps/archive/ with timestamp")
print("     → Can be restored later")
print("     → Safe option")
print("")
print("  2. Delete (permanent)    - Cannot be undone")
print("     → Only if you're certain you don't need them")
print("")
print("  3. Cancel                - No changes made")
print("")

# ============================================================================
# GET USER CHOICE
# ============================================================================

choice = input("Enter choice (1/2/3): ").strip()

# ============================================================================
# EXECUTE ACTION
# ============================================================================

if choice == "1":
    # ARCHIVE
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    archive_path = f"prps/archive/{feature_name}_{timestamp}"

    print("")
    print(f"📦 Archiving artifacts to: {archive_path}")
    print("")

    # Create archive directory
    os.makedirs(archive_path, exist_ok=True)

    # Move directories to archive
    archived = []
    for dirname in ["planning", "examples", "execution"]:
        src = f"{feature_dir}/{dirname}"
        if os.path.exists(src):
            import shutil
            dst = f"{archive_path}/{dirname}"
            shutil.move(src, dst)
            archived.append(dirname)
            print(f"  ✓ Archived {dirname}/")

    # Create archive manifest
    with open(f"{archive_path}/ARCHIVE_INFO.md", "w") as f:
        f.write(f"""# Archive Info

**Feature**: {feature_name}
**Archived**: {timestamp}
**Archive Location**: {archive_path}

## Contents

- planning/     - Research artifacts from generate-prp
- examples/     - Extracted code examples
- execution/    - Implementation artifacts from execute-prp

## Statistics

- Total files: {total_count}
- Total size: {total_size:.1f} MB
- Archived directories: {', '.join(archived)}

## Restoration

To restore these artifacts:

```bash
# Move directories back
mv {archive_path}/planning {feature_dir}/ 2>/dev/null || true
mv {archive_path}/examples {feature_dir}/ 2>/dev/null || true
mv {archive_path}/execution {feature_dir}/ 2>/dev/null || true
```

## Permanent Deletion

If you're sure you don't need these artifacts:

```bash
rm -rf {archive_path}
```
""")

    print("")
    print("✅ Archive complete!")
    print("")
    print(f"  Archive location: {archive_path}")
    print(f"  See {archive_path}/ARCHIVE_INFO.md for restoration instructions")
    print("")
    print("  To restore later:")
    print(f"    mv {archive_path}/* {feature_dir}/")
    print("")
    print("  To list all archives:")
    print("    ls -lh prps/archive/")
    print("")

elif choice == "2":
    # DELETE (with confirmation)
    print("")
    print("⚠️  PERMANENT DELETION (cannot be undone)")
    print("")
    print(f"  This will permanently delete {total_count} files ({total_size:.1f} MB):")
    print(f"    • {feature_dir}/planning/")
    print(f"    • {feature_dir}/examples/")
    print(f"    • {feature_dir}/execution/")
    print("")

    confirmation = input("Type 'yes' to confirm deletion: ").strip()

    if confirmation.lower() == "yes":
        import shutil
        deleted = []
        for dirname in ["planning", "examples", "execution"]:
            dirpath = f"{feature_dir}/{dirname}"
            if os.path.exists(dirpath):
                shutil.rmtree(dirpath)
                deleted.append(dirname)
                print(f"  ✓ Deleted {dirname}/")

        print("")
        print("✅ Deletion complete!")
        print(f"   Deleted: {', '.join(deleted)}")
        print("")
    else:
        print("")
        print("❌ Deletion cancelled (confirmation not received)")
        print("")

elif choice == "3":
    # CANCEL
    print("")
    print("No changes made.")
    print("")

else:
    print("")
    print(f"❌ Invalid choice: '{choice}'")
    print("   Cleanup cancelled.")
    print("")
```
