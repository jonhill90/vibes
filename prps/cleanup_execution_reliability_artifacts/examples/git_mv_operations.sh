#!/bin/bash
# Source: Feature analysis for cleanup_execution_reliability_artifacts
# Pattern: Safe git mv operations for directory consolidation and file renaming
# Extracted: 2025-10-07
# Relevance: 10/10 - Core pattern for file operations

set -e  # Exit on error
set -u  # Exit on undefined variable

# =============================================================================
# PATTERN 1: Directory Consolidation with Git History Preservation
# =============================================================================
# Use Case: Moving contents from split directory to consolidated location
# Example: prps/execution_reliability/ → prps/execution_reliability/

# Function: Safe directory move with pre-flight checks
move_directory_contents() {
    local source_dir="$1"
    local dest_parent="$2"
    local item_name="$3"  # Directory or file name to move

    echo "Moving: ${source_dir}/${item_name} → ${dest_parent}/${item_name}"

    # Pre-flight check 1: Source exists
    if [ ! -e "${source_dir}/${item_name}" ]; then
        echo "❌ ERROR: Source does not exist: ${source_dir}/${item_name}"
        return 1
    fi

    # Pre-flight check 2: Destination doesn't already exist (avoid overwrite)
    if [ -e "${dest_parent}/${item_name}" ]; then
        echo "❌ ERROR: Destination already exists: ${dest_parent}/${item_name}"
        echo "   Cannot overwrite. Please resolve manually."
        return 1
    fi

    # Pre-flight check 3: Destination parent directory exists
    if [ ! -d "${dest_parent}" ]; then
        echo "❌ ERROR: Destination parent directory does not exist: ${dest_parent}"
        return 1
    fi

    # Execute git mv (preserves history)
    git mv "${source_dir}/${item_name}" "${dest_parent}/${item_name}"

    echo "✅ Moved successfully"
}

# =============================================================================
# PATTERN 2: File Rename with Git History Preservation
# =============================================================================
# Use Case: Renaming files to remove redundant prefixes
# Example: execution_reliability.md → execution_reliability.md

rename_file_with_git() {
    local old_path="$1"
    local new_path="$2"

    echo "Renaming: ${old_path} → ${new_path}"

    # Pre-flight check 1: Source file exists
    if [ ! -f "${old_path}" ]; then
        echo "❌ ERROR: Source file does not exist: ${old_path}"
        return 1
    fi

    # Pre-flight check 2: Destination doesn't exist
    if [ -f "${new_path}" ]; then
        echo "❌ ERROR: Destination file already exists: ${new_path}"
        echo "   Cannot overwrite. Please resolve manually."
        return 1
    fi

    # Pre-flight check 3: Parent directory of destination exists
    local dest_parent=$(dirname "${new_path}")
    if [ ! -d "${dest_parent}" ]; then
        echo "❌ ERROR: Destination directory does not exist: ${dest_parent}"
        return 1
    fi

    # Execute git mv (preserves history)
    git mv "${old_path}" "${new_path}"

    echo "✅ Renamed successfully"
}

# =============================================================================
# PATTERN 3: Empty Directory Cleanup
# =============================================================================
# Use Case: Delete empty directories after consolidation
# CRITICAL: Only delete if truly empty (no hidden files)

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
# PATTERN 4: Idempotent Directory Creation
# =============================================================================
# Use Case: Create target directories for file moves
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
# USAGE EXAMPLE: Consolidate execution_reliability directories
# =============================================================================

consolidate_execution_reliability_example() {
    echo "========================================="
    echo "Example: Consolidate execution_reliability"
    echo "========================================="

    # Step 1: Verify working directory is clean
    if ! git diff-index --quiet HEAD --; then
        echo "❌ ERROR: Working directory has uncommitted changes"
        echo "   Please commit or stash changes before running file operations"
        return 1
    fi

    # Step 2: Define paths
    SOURCE_DIR="prps/execution_reliability"
    DEST_DIR="prps/execution_reliability"

    # Step 3: Move directory contents
    echo ""
    echo "Step 1/4: Moving examples/ directory"
    move_directory_contents "${SOURCE_DIR}" "${DEST_DIR}" "examples"

    echo ""
    echo "Step 2/4: Moving planning/ directory"
    move_directory_contents "${SOURCE_DIR}" "${DEST_DIR}" "planning"

    echo ""
    echo "Step 3/4: Moving TASK8_TEST_RESULTS.md file"
    move_directory_contents "${SOURCE_DIR}/execution" "${DEST_DIR}/execution" "TASK8_TEST_RESULTS.md"

    # Step 4: Verify source directory is empty before deleting
    echo ""
    echo "Step 4/4: Deleting empty source directory"
    delete_empty_directory "${SOURCE_DIR}/execution"  # Delete subdirectory first
    delete_empty_directory "${SOURCE_DIR}"            # Then parent

    # Step 5: Rename PRP file
    echo ""
    echo "Step 5/5: Renaming PRP file"
    rename_file_with_git "prps/execution_reliability.md" "prps/execution_reliability.md"

    echo ""
    echo "========================================="
    echo "✅ Consolidation complete!"
    echo "========================================="
    echo ""
    echo "Next steps:"
    echo "1. Review changes: git status"
    echo "2. Verify file paths: ls -R prps/execution_reliability/"
    echo "3. Update documentation references"
    echo "4. Commit changes: git commit -m 'Consolidate execution_reliability artifacts'"
}

# =============================================================================
# PATTERN 5: Rollback on Error
# =============================================================================
# Use Case: Undo file operations if something goes wrong
# CRITICAL: Only works if operations used git mv (not shell mv)

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

    # Confirm rollback
    read -p "Rollback these changes? (y/N): " confirm
    if [ "${confirm}" != "y" ]; then
        echo "Rollback cancelled"
        return 1
    fi

    # Reset staging area (undo git mv)
    git reset HEAD

    # Restore working directory to last commit
    git checkout -- .

    echo "✅ Rollback complete - all file operations undone"
}

# =============================================================================
# VALIDATION PATTERN: Verify Operations Completed
# =============================================================================

validate_consolidation() {
    local feature_name="$1"
    local expected_dirs=("examples" "planning" "execution")

    echo "========================================="
    echo "VALIDATION: Checking consolidation"
    echo "========================================="

    local all_valid=true

    # Check 1: All expected directories exist
    for dir in "${expected_dirs[@]}"; do
        if [ -d "prps/${feature_name}/${dir}" ]; then
            echo "✅ Directory exists: prps/${feature_name}/${dir}"
        else
            echo "❌ Directory missing: prps/${feature_name}/${dir}"
            all_valid=false
        fi
    done

    # Check 2: Old directory does not exist
    if [ ! -d "prps/prp_${feature_name}" ]; then
        echo "✅ Old directory removed: prps/prp_${feature_name}"
    else
        echo "❌ Old directory still exists: prps/prp_${feature_name}"
        all_valid=false
    fi

    # Check 3: PRP file exists with correct name
    if [ -f "prps/${feature_name}.md" ]; then
        echo "✅ PRP file exists: prps/${feature_name}.md"
    else
        echo "❌ PRP file missing: prps/${feature_name}.md"
        all_valid=false
    fi

    # Check 4: Old PRP file does not exist
    if [ ! -f "prps/prp_${feature_name}.md" ]; then
        echo "✅ Old PRP file removed: prps/prp_${feature_name}.md"
    else
        echo "❌ Old PRP file still exists: prps/prp_${feature_name}.md"
        all_valid=false
    fi

    echo ""
    if [ "${all_valid}" = true ]; then
        echo "✅ VALIDATION PASSED - Consolidation complete"
        return 0
    else
        echo "❌ VALIDATION FAILED - Issues found above"
        return 1
    fi
}

# =============================================================================
# Main execution (if script is run directly)
# =============================================================================

if [ "${BASH_SOURCE[0]}" = "${0}" ]; then
    echo "Git mv operations script loaded"
    echo ""
    echo "Available functions:"
    echo "  - move_directory_contents <source_dir> <dest_parent> <item_name>"
    echo "  - rename_file_with_git <old_path> <new_path>"
    echo "  - delete_empty_directory <dir_path>"
    echo "  - consolidate_execution_reliability_example"
    echo "  - rollback_git_operations"
    echo "  - validate_consolidation <feature_name>"
    echo ""
    echo "Example usage:"
    echo "  source git_mv_operations.sh"
    echo "  consolidate_execution_reliability_example"
fi
