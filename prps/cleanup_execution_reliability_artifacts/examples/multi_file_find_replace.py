#!/usr/bin/env python3
"""
Source: Feature analysis for cleanup_execution_reliability_artifacts
Pattern: Safe multi-file find/replace for documentation updates
Extracted: 2025-10-07
Relevance: 10/10 - Core pattern for documentation reference updates
"""

import re
import sys
from pathlib import Path
from typing import List, Dict, Tuple


# =============================================================================
# PATTERN 1: Safe Find and Replace in Single File
# =============================================================================
# Use Case: Update references in documentation files
# Example: Replace "execution_reliability" → "execution_reliability"

def find_replace_in_file(
    file_path: Path,
    old_text: str,
    new_text: str,
    dry_run: bool = True
) -> Dict[str, any]:
    """
    Find and replace text in a single file with safety checks.

    Args:
        file_path: Path to file to modify
        old_text: Text to find (exact match, case-sensitive)
        new_text: Text to replace with
        dry_run: If True, only report what would change (don't modify file)

    Returns:
        dict with keys:
            - matched: bool - Whether old_text was found
            - count: int - Number of replacements made/would be made
            - preview: str - First 200 chars of updated content
            - modified: bool - Whether file was actually modified
    """
    # Pre-flight check 1: File exists
    if not file_path.exists():
        raise FileNotFoundError(f"File does not exist: {file_path}")

    # Pre-flight check 2: File is readable
    try:
        original_content = file_path.read_text()
    except Exception as e:
        raise IOError(f"Cannot read file {file_path}: {e}")

    # Count occurrences
    count = original_content.count(old_text)

    if count == 0:
        return {
            "matched": False,
            "count": 0,
            "preview": None,
            "modified": False,
            "file": str(file_path)
        }

    # Perform replacement
    updated_content = original_content.replace(old_text, new_text)

    # Preview (first 200 chars of changed content)
    preview_lines = []
    for i, line in enumerate(updated_content.split('\n')[:5], 1):
        if old_text in original_content.split('\n')[i-1] if i <= len(original_content.split('\n')) else False:
            preview_lines.append(f"  Line {i}: {line[:100]}")

    preview = '\n'.join(preview_lines[:3]) if preview_lines else updated_content[:200]

    # Write back if not dry run
    modified = False
    if not dry_run:
        try:
            file_path.write_text(updated_content)
            modified = True
        except Exception as e:
            raise IOError(f"Cannot write file {file_path}: {e}")

    return {
        "matched": True,
        "count": count,
        "preview": preview,
        "modified": modified,
        "file": str(file_path)
    }


# =============================================================================
# PATTERN 2: Multi-File Find and Replace with Batch Processing
# =============================================================================
# Use Case: Update references across multiple documentation files
# Example: Update all 10 files referencing "execution_reliability"

def find_replace_in_files(
    file_paths: List[Path],
    old_text: str,
    new_text: str,
    dry_run: bool = True
) -> Dict[str, any]:
    """
    Find and replace text across multiple files.

    Args:
        file_paths: List of file paths to process
        old_text: Text to find
        new_text: Text to replace with
        dry_run: If True, only report what would change

    Returns:
        dict with summary statistics and per-file results
    """
    results = []
    total_matches = 0
    total_replacements = 0
    files_modified = 0

    for file_path in file_paths:
        try:
            result = find_replace_in_file(file_path, old_text, new_text, dry_run)
            results.append(result)

            if result["matched"]:
                total_matches += 1
                total_replacements += result["count"]
                if result["modified"]:
                    files_modified += 1

        except Exception as e:
            results.append({
                "matched": False,
                "count": 0,
                "preview": None,
                "modified": False,
                "file": str(file_path),
                "error": str(e)
            })

    return {
        "total_files": len(file_paths),
        "files_matched": total_matches,
        "total_replacements": total_replacements,
        "files_modified": files_modified,
        "results": results
    }


# =============================================================================
# PATTERN 3: File Path Updates (Special Case)
# =============================================================================
# Use Case: Update file paths in documentation
# Example: "prps/execution_reliability/examples/" → "prps/execution_reliability/examples/"

def update_file_paths(
    file_path: Path,
    old_path_segment: str,
    new_path_segment: str,
    dry_run: bool = True
) -> Dict[str, any]:
    """
    Update file path references in documentation.

    This is a specialized version of find_replace that handles path variations:
    - With/without trailing slashes
    - Markdown links [text](path)
    - Inline code `path`
    - Plain text paths

    Args:
        file_path: File to update
        old_path_segment: Old path segment (e.g., "execution_reliability")
        new_path_segment: New path segment (e.g., "execution_reliability")
        dry_run: If True, only report changes

    Returns:
        dict with update statistics
    """
    if not file_path.exists():
        raise FileNotFoundError(f"File does not exist: {file_path}")

    original_content = file_path.read_text()
    updated_content = original_content

    # Pattern 1: Directory paths (with or without trailing slash)
    patterns = [
        (f"prps/{old_path_segment}/", f"prps/{new_path_segment}/"),
        (f"prps/{old_path_segment}", f"prps/{new_path_segment}"),  # No trailing slash
    ]

    total_replacements = 0
    for old_pattern, new_pattern in patterns:
        count = updated_content.count(old_pattern)
        if count > 0:
            updated_content = updated_content.replace(old_pattern, new_pattern)
            total_replacements += count

    # Write back if not dry run
    modified = False
    if not dry_run and updated_content != original_content:
        file_path.write_text(updated_content)
        modified = True

    return {
        "matched": total_replacements > 0,
        "count": total_replacements,
        "modified": modified,
        "file": str(file_path)
    }


# =============================================================================
# PATTERN 4: Validation After Replacement
# =============================================================================
# Use Case: Verify no old references remain after replacement

def validate_no_old_references(
    directory: Path,
    old_text: str,
    file_pattern: str = "*.md"
) -> Tuple[bool, List[str]]:
    """
    Validate that old references have been completely removed.

    Args:
        directory: Directory to search
        old_text: Old text that should no longer exist
        file_pattern: File glob pattern (default: *.md)

    Returns:
        Tuple of (all_clean: bool, files_with_old_text: List[str])
    """
    files_with_old_text = []

    for file_path in directory.rglob(file_pattern):
        try:
            content = file_path.read_text()
            if old_text in content:
                # Get line numbers for better debugging
                lines_with_text = [
                    (i + 1, line)
                    for i, line in enumerate(content.split('\n'))
                    if old_text in line
                ]
                files_with_old_text.append({
                    "file": str(file_path.relative_to(directory)),
                    "occurrences": len(lines_with_text),
                    "lines": lines_with_text[:3]  # First 3 occurrences
                })
        except Exception as e:
            print(f"⚠️  Cannot read {file_path}: {e}")

    return len(files_with_old_text) == 0, files_with_old_text


# =============================================================================
# PATTERN 5: Backup Before Modification
# =============================================================================
# Use Case: Create backups before making bulk changes

def backup_files(file_paths: List[Path], backup_suffix: str = ".bak") -> List[Path]:
    """
    Create backup copies of files before modification.

    Args:
        file_paths: Files to backup
        backup_suffix: Suffix for backup files (default: .bak)

    Returns:
        List of backup file paths created
    """
    backup_paths = []

    for file_path in file_paths:
        if not file_path.exists():
            continue

        backup_path = file_path.with_suffix(file_path.suffix + backup_suffix)

        # Read and write (don't use shutil.copy to avoid permissions issues)
        content = file_path.read_text()
        backup_path.write_text(content)

        backup_paths.append(backup_path)
        print(f"✅ Backed up: {file_path} → {backup_path}")

    return backup_paths


def restore_from_backups(backup_paths: List[Path], backup_suffix: str = ".bak") -> None:
    """
    Restore files from backups.

    Args:
        backup_paths: List of backup file paths
        backup_suffix: Suffix of backup files
    """
    for backup_path in backup_paths:
        if not backup_path.exists():
            continue

        # Remove backup suffix to get original path
        original_path = Path(str(backup_path).replace(backup_suffix, ""))

        content = backup_path.read_text()
        original_path.write_text(content)

        print(f"✅ Restored: {backup_path} → {original_path}")


# =============================================================================
# USAGE EXAMPLE: Update execution_reliability references
# =============================================================================

def update_execution_reliability_references_example():
    """
    Example: Update all references from execution_reliability → execution_reliability
    """
    print("=" * 80)
    print("Example: Update execution_reliability References")
    print("=" * 80)

    # Step 1: Define files to update
    feature_dir = Path("prps/execution_reliability")
    files_to_update = [
        feature_dir / "execution_reliability.md",  # PRP file (after rename)
        feature_dir / "execution" / "EXECUTION_SUMMARY.md",
    ]

    # Add all TASK*_COMPLETION.md files
    files_to_update.extend(feature_dir.glob("execution/TASK*_COMPLETION.md"))

    # Verify files exist
    existing_files = [f for f in files_to_update if f.exists()]
    print(f"\nFound {len(existing_files)} files to update:")
    for f in existing_files:
        print(f"  - {f.relative_to(Path.cwd())}")

    # Step 2: DRY RUN - Preview changes
    print("\n" + "=" * 80)
    print("DRY RUN: Preview Changes")
    print("=" * 80)

    dry_run_results = find_replace_in_files(
        existing_files,
        old_text="execution_reliability",
        new_text="execution_reliability",
        dry_run=True
    )

    print(f"\nFiles to modify: {dry_run_results['files_matched']}/{dry_run_results['total_files']}")
    print(f"Total replacements: {dry_run_results['total_replacements']}")

    for result in dry_run_results['results']:
        if result['matched']:
            print(f"\n  File: {result['file']}")
            print(f"  Replacements: {result['count']}")
            if result.get('preview'):
                print(f"  Preview:\n{result['preview']}")

    # Step 3: Confirm before proceeding
    print("\n" + "=" * 80)
    response = input("Proceed with replacement? (yes/no): ")
    if response.lower() != "yes":
        print("Cancelled by user")
        return

    # Step 4: Create backups
    print("\n" + "=" * 80)
    print("Creating Backups")
    print("=" * 80)
    backup_paths = backup_files(existing_files)

    # Step 5: Execute replacement
    print("\n" + "=" * 80)
    print("Executing Replacement")
    print("=" * 80)

    try:
        actual_results = find_replace_in_files(
            existing_files,
            old_text="execution_reliability",
            new_text="execution_reliability",
            dry_run=False
        )

        print(f"\n✅ Files modified: {actual_results['files_modified']}/{actual_results['total_files']}")
        print(f"✅ Total replacements: {actual_results['total_replacements']}")

        # Step 6: Validate no old references remain
        print("\n" + "=" * 80)
        print("Validation: Checking for Old References")
        print("=" * 80)

        all_clean, remaining_refs = validate_no_old_references(
            feature_dir,
            "execution_reliability"
        )

        if all_clean:
            print("✅ VALIDATION PASSED: No old references found")
            # Delete backups
            for backup_path in backup_paths:
                backup_path.unlink()
            print("✅ Backups deleted (no longer needed)")
        else:
            print(f"❌ VALIDATION FAILED: Found {len(remaining_refs)} files with old references:")
            for ref in remaining_refs:
                print(f"\n  File: {ref['file']}")
                print(f"  Occurrences: {ref['occurrences']}")
                for line_num, line in ref['lines']:
                    print(f"    Line {line_num}: {line[:100]}")

    except Exception as e:
        print(f"\n❌ ERROR during replacement: {e}")
        print("\nRestoring from backups...")
        restore_from_backups(backup_paths)
        print("✅ Files restored from backups")


# =============================================================================
# PATTERN 6: Regex-Based Replacement (Advanced)
# =============================================================================

def regex_find_replace_in_file(
    file_path: Path,
    pattern: str,
    replacement: str,
    dry_run: bool = True
) -> Dict[str, any]:
    """
    Find and replace using regex patterns.

    Use Case: Complex replacements like updating version numbers, dates, etc.

    Args:
        file_path: File to modify
        pattern: Regex pattern to match
        replacement: Replacement text (can use \\1, \\2 for capture groups)
        dry_run: If True, only preview changes

    Returns:
        dict with replacement statistics
    """
    if not file_path.exists():
        raise FileNotFoundError(f"File does not exist: {file_path}")

    original_content = file_path.read_text()

    # Compile regex
    regex = re.compile(pattern)

    # Find all matches
    matches = list(regex.finditer(original_content))

    if not matches:
        return {
            "matched": False,
            "count": 0,
            "modified": False,
            "file": str(file_path)
        }

    # Perform replacement
    updated_content = regex.sub(replacement, original_content)

    # Write if not dry run
    modified = False
    if not dry_run:
        file_path.write_text(updated_content)
        modified = True

    return {
        "matched": True,
        "count": len(matches),
        "modified": modified,
        "file": str(file_path),
        "preview": updated_content[:200]
    }


# =============================================================================
# Main execution
# =============================================================================

if __name__ == "__main__":
    print("Multi-file find/replace script loaded")
    print("\nAvailable functions:")
    print("  - find_replace_in_file(file_path, old_text, new_text, dry_run=True)")
    print("  - find_replace_in_files(file_paths, old_text, new_text, dry_run=True)")
    print("  - update_file_paths(file_path, old_segment, new_segment, dry_run=True)")
    print("  - validate_no_old_references(directory, old_text)")
    print("  - update_execution_reliability_references_example()")
    print("\nExample usage:")
    print("  python multi_file_find_replace.py")
    print("  >>> update_execution_reliability_references_example()")
