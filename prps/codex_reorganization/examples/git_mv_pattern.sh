#!/bin/bash
# Source: prps/cleanup_execution_reliability_artifacts/examples/git_mv_operations.sh
# Lines: 16-47, 55-85
# Pattern: Safe git mv with pre-flight checks
# Extracted: 2025-10-08
# Relevance: 10/10 - Exact pattern needed for codex file moves

set -e  # Exit on error
set -u  # Exit on undefined variable

# =============================================================================
# PATTERN 1: Directory/File Move with Git History Preservation
# =============================================================================
# Use Case: Moving files from scripts/codex/ to .codex/scripts/
# Critical: Pre-flight checks prevent common errors

# Function: Safe file/directory move with validation
move_with_git() {
    local source_path="$1"
    local dest_path="$2"

    echo "Moving: ${source_path} → ${dest_path}"

    # Pre-flight check 1: Source exists
    if [ ! -e "${source_path}" ]; then
        echo "❌ ERROR: Source does not exist: ${source_path}"
        return 1
    fi

    # Pre-flight check 2: Destination doesn't already exist (avoid overwrite)
    if [ -e "${dest_path}" ]; then
        echo "❌ ERROR: Destination already exists: ${dest_path}"
        echo "   Cannot overwrite. Please resolve manually."
        return 1
    fi

    # Pre-flight check 3: Destination parent directory exists
    local dest_parent=$(dirname "${dest_path}")
    if [ ! -d "${dest_parent}" ]; then
        echo "❌ ERROR: Destination parent directory does not exist: ${dest_parent}"
        return 1
    fi

    # Execute git mv (preserves history)
    git mv "${source_path}" "${dest_path}"

    echo "✅ Moved successfully"
}

# =============================================================================
# PATTERN 2: Empty Directory Cleanup
# =============================================================================
# Use Case: Delete empty scripts/codex/ and tests/codex/ after moves
# CRITICAL: Only delete if truly empty (no hidden files like .gitkeep)

delete_empty_directory() {
    local dir_path="$1"

    echo "Checking if directory is empty: ${dir_path}"

    # Pre-flight check 1: Directory exists
    if [ ! -d "${dir_path}" ]; then
        echo "⚠️  Directory does not exist (already deleted?): ${dir_path}"
        return 0  # Not an error - goal achieved
    fi

    # Pre-flight check 2: Directory is truly empty (including hidden files)
    # Use find to catch hidden files (.gitkeep, .DS_Store, etc.)
    local file_count=$(find "${dir_path}" -mindepth 1 -maxdepth 1 | wc -l | tr -d ' ')

    if [ "${file_count}" -ne "0" ]; then
        echo "❌ ERROR: Directory is not empty (${file_count} items found)"
        echo "   Contents:"
        ls -la "${dir_path}"
        return 1
    fi

    # Safe to delete (use rmdir, not rm -rf, to ensure it's truly empty)
    rmdir "${dir_path}"

    echo "✅ Empty directory deleted"
}

# =============================================================================
# PATTERN 3: Idempotent Directory Creation
# =============================================================================
# Use Case: Create .codex/scripts/ and .codex/tests/ target directories
# Safe to run multiple times (won't fail if directory exists)

create_directory_if_needed() {
    local dir_path="$1"

    if [ -d "${dir_path}" ]; then
        echo "✅ Directory already exists: ${dir_path}"
    else
        mkdir -p "${dir_path}"
        echo "✅ Created directory: ${dir_path}"
    fi
}

# =============================================================================
# PATTERN 4: Git Working Tree Validation
# =============================================================================
# Use Case: Verify clean state before starting file operations
# Prevents conflicts with uncommitted changes

verify_clean_working_tree() {
    echo "Verifying git working tree is clean..."

    if ! git diff-index --quiet HEAD --; then
        echo "❌ ERROR: Working directory has uncommitted changes"
        echo "   Please commit or stash changes before running file operations"
        return 1
    fi

    echo "✅ Working tree is clean"
    return 0
}

# =============================================================================
# USAGE EXAMPLE: Codex Directory Reorganization
# =============================================================================

reorganize_codex_directories() {
    echo "========================================="
    echo "Codex Directory Reorganization"
    echo "========================================="

    # Step 1: Verify working directory is clean
    verify_clean_working_tree || return 1

    # Step 2: Create target directories
    create_directory_if_needed ".codex/scripts"
    create_directory_if_needed ".codex/tests"

    # Step 3: Move script files (example for one file)
    move_with_git "scripts/codex/parallel-exec.sh" ".codex/scripts/parallel-exec.sh"

    # Step 4: Move test files (example for one file)
    move_with_git "tests/codex/test_generate_prp.sh" ".codex/tests/test_generate_prp.sh"

    # Step 5: Move fixtures directory
    move_with_git "tests/codex/fixtures" ".codex/tests/fixtures"

    # Step 6: Verify source directories are empty before deleting
    delete_empty_directory "scripts/codex"
    delete_empty_directory "tests/codex"

    echo ""
    echo "========================================="
    echo "✅ Reorganization complete!"
    echo "========================================="
}

# =============================================================================
# ROLLBACK PATTERN
# =============================================================================

rollback_git_operations() {
    echo "========================================="
    echo "ROLLBACK: Undoing file operations"
    echo "========================================="

    # Check if there are staged changes
    if git diff --cached --quiet; then
        echo "⚠️  No staged changes to rollback"
        return 0
    fi

    # Show what will be rolled back
    echo "Changes to be rolled back:"
    git diff --cached --name-status

    # Reset staging area (undo git mv)
    git reset HEAD

    # Restore working directory to last commit
    git checkout -- .

    echo "✅ Rollback complete - all file operations undone"
}
