#!/bin/bash
# Source: prps/codex_reorganization/planning/feature-analysis.md
# Lines: 571-575
# Pattern: Bulk path updates with sed and find
# Extracted: 2025-10-08
# Relevance: 9/10 - Needed for updating test file path references

set -euo pipefail

# =============================================================================
# PATTERN 1: Bulk Path Update in Shell Scripts
# =============================================================================
# Use Case: Update all references to scripts/codex/ in test files
# Pattern: find + sed for safe, repeatable bulk updates

update_test_paths_to_scripts() {
    echo "Updating test file references: scripts/codex/ → .codex/scripts/"

    # Find all .sh files in .codex/tests/ and update script paths
    # -i '': In-place editing (macOS requires empty string after -i)
    # Use | as delimiter instead of / to avoid escaping slashes in paths
    find .codex/tests -name "*.sh" -exec sed -i '' \
        's|${REPO_ROOT}/scripts/codex/|${REPO_ROOT}/.codex/scripts/|g' {} \;

    echo "✅ Updated script references in test files"
}

update_test_paths_to_tests() {
    echo "Updating test file references: tests/codex/ → .codex/tests/"

    # Update references to test directory itself
    find .codex/tests -name "*.sh" -exec sed -i '' \
        's|${REPO_ROOT}/tests/codex/|${REPO_ROOT}/.codex/tests/|g' {} \;

    echo "✅ Updated test directory references"
}

# =============================================================================
# PATTERN 2: Safe Sed with Backup Files
# =============================================================================
# Use Case: Create backups before modification for easy rollback

update_with_backup() {
    local pattern_old="$1"
    local pattern_new="$2"
    local target_dir="$3"

    echo "Updating paths with backup: ${pattern_old} → ${pattern_new}"

    # Create .bak files before modification
    # Can be restored if something goes wrong
    find "${target_dir}" -name "*.sh" -exec sed -i.bak \
        "s|${pattern_old}|${pattern_new}|g" {} \;

    echo "✅ Updated with backups (.bak files created)"
    echo "   To restore: find ${target_dir} -name '*.bak' -exec bash -c 'mv \"\$0\" \"\${0%.bak}\"' {} \;"
}

# =============================================================================
# PATTERN 3: Verification After Update
# =============================================================================
# Use Case: Verify all old paths are gone, new paths exist

verify_path_updates() {
    local old_pattern="$1"
    local new_pattern="$2"
    local search_dir="$3"

    echo "Verifying path updates in ${search_dir}..."

    # Check for lingering old pattern
    local old_count=$(grep -r "${old_pattern}" "${search_dir}" 2>/dev/null | wc -l | tr -d ' ')

    if [ "${old_count}" -gt 0 ]; then
        echo "❌ WARNING: Found ${old_count} instances of old pattern: ${old_pattern}"
        grep -rn "${old_pattern}" "${search_dir}" 2>/dev/null | head -5
        return 1
    fi

    echo "✅ No instances of old pattern found"

    # Check for new pattern
    local new_count=$(grep -r "${new_pattern}" "${search_dir}" 2>/dev/null | wc -l | tr -d ' ')

    if [ "${new_count}" -eq 0 ]; then
        echo "⚠️  WARNING: No instances of new pattern found"
        echo "   This might be expected if paths were removed, not replaced"
    else
        echo "✅ Found ${new_count} instances of new pattern"
    fi

    return 0
}

# =============================================================================
# PATTERN 4: Documentation Path Updates
# =============================================================================
# Use Case: Update README files and documentation

update_documentation_paths() {
    echo "Updating documentation references..."

    # Update all markdown files
    find .codex -name "*.md" -exec sed -i '' \
        's|scripts/codex/|.codex/scripts/|g' {} \;

    find .codex -name "*.md" -exec sed -i '' \
        's|tests/codex/|.codex/tests/|g' {} \;

    echo "✅ Updated documentation paths"
}

# =============================================================================
# PATTERN 5: Special Characters in Paths
# =============================================================================
# Demonstrates how to handle different path delimiters in sed

update_with_special_chars() {
    echo "Examples of sed with different delimiters:"

    # Standard delimiter: /
    # Requires escaping forward slashes
    # sed 's/old\/path/new\/path/g'

    # Pipe delimiter: | (preferred for paths)
    # No escaping needed for forward slashes
    # sed 's|old/path|new/path|g'

    # Hash delimiter: #
    # sed 's#old/path#new/path#g'

    echo "Recommended: Use | delimiter for file paths"
}

# =============================================================================
# PATTERN 6: Dry Run Before Actual Update
# =============================================================================
# Use Case: Preview changes before making them

dry_run_path_update() {
    local old_pattern="$1"
    local new_pattern="$2"
    local target_dir="$3"

    echo "DRY RUN: Showing what would be changed..."
    echo "Pattern: ${old_pattern} → ${new_pattern}"
    echo ""

    # Find files that contain the pattern
    local matching_files=$(grep -rl "${old_pattern}" "${target_dir}" 2>/dev/null || true)

    if [ -z "$matching_files" ]; then
        echo "No files contain the pattern"
        return 0
    fi

    echo "Files that would be modified:"
    echo "$matching_files"
    echo ""

    # Show actual changes that would be made
    echo "Preview of changes:"
    for file in $matching_files; do
        echo ""
        echo "File: ${file}"
        echo "---"
        grep -n "${old_pattern}" "$file" | head -3
        echo "Would become:"
        grep "${old_pattern}" "$file" | sed "s|${old_pattern}|${new_pattern}|g" | head -3
    done
}

# =============================================================================
# PATTERN 7: Rollback Backup Files
# =============================================================================

restore_from_backup() {
    local target_dir="$1"

    echo "Rolling back changes from .bak files..."

    # Count backup files
    local bak_count=$(find "${target_dir}" -name "*.bak" 2>/dev/null | wc -l | tr -d ' ')

    if [ "${bak_count}" -eq 0 ]; then
        echo "⚠️  No backup files found"
        return 0
    fi

    echo "Found ${bak_count} backup files"

    # Restore each backup
    find "${target_dir}" -name "*.bak" -exec bash -c '
        original="${1%.bak}"
        echo "Restoring: ${original}"
        mv "$1" "${original}"
    ' _ {} \;

    echo "✅ Rollback complete"
}

# =============================================================================
# PATTERN 8: Complete Update Workflow
# =============================================================================

complete_path_update_workflow() {
    echo "========================================="
    echo "Complete Path Update Workflow"
    echo "========================================="

    local old_pattern="scripts/codex"
    local new_pattern=".codex/scripts"

    # Step 1: Dry run
    echo "Step 1: Dry run preview"
    dry_run_path_update "\${REPO_ROOT}/${old_pattern}/" "\${REPO_ROOT}/${new_pattern}/" ".codex/tests"

    # Step 2: Create backups and update
    echo ""
    echo "Step 2: Update with backups"
    update_with_backup "\${REPO_ROOT}/${old_pattern}/" "\${REPO_ROOT}/${new_pattern}/" ".codex/tests"

    # Step 3: Verify
    echo ""
    echo "Step 3: Verify updates"
    if verify_path_updates "${old_pattern}" "${new_pattern}" ".codex/tests"; then
        echo "✅ Verification passed"

        # Step 4: Remove backups (optional)
        echo ""
        echo "Step 4: Cleanup backups"
        find .codex/tests -name "*.bak" -delete
        echo "✅ Backup files removed"
    else
        echo "❌ Verification failed - restoring from backup"
        restore_from_backup ".codex/tests"
        return 1
    fi

    echo ""
    echo "========================================="
    echo "✅ Path update workflow complete"
    echo "========================================="
}

# =============================================================================
# USAGE EXAMPLE: Codex Reorganization
# =============================================================================

codex_reorganization_path_updates() {
    echo "========================================="
    echo "Codex Reorganization: Path Updates"
    echo "========================================="

    # After git mv operations, update references

    # Step 1: Update test file script references
    update_test_paths_to_scripts

    # Step 2: Update test file test directory references
    update_test_paths_to_tests

    # Step 3: Update documentation
    update_documentation_paths

    # Step 4: Verify no old paths remain
    echo ""
    echo "Final verification..."
    verify_path_updates "scripts/codex/" ".codex/scripts/" ".codex/tests"
    verify_path_updates "tests/codex/" ".codex/tests/" ".codex/tests"

    echo ""
    echo "========================================="
    echo "✅ All path updates complete"
    echo "========================================="
}

# =============================================================================
# KEY INSIGHTS
# =============================================================================

show_key_insights() {
    cat <<'EOF'
========================================
Key Insights for Path Updates with Sed
========================================

1. USE PIPE DELIMITER (|) for file paths
   ✅ sed 's|old/path|new/path|g'
   ❌ sed 's/old\/path/new\/path/g'  (requires escaping)

2. CREATE BACKUPS for safety
   ✅ sed -i.bak 's|pattern|replacement|g' file.sh
   Can restore: mv file.sh.bak file.sh

3. VERIFY AFTER UPDATES
   ✅ grep -r "old_pattern" dir/  (should be empty)
   ✅ grep -r "new_pattern" dir/  (should find matches)

4. DRY RUN FIRST
   ✅ Preview changes before applying
   ✅ Catch unexpected matches

5. MACOS REQUIRES EMPTY STRING
   ✅ sed -i '' 's|pattern|replacement|g'  (macOS)
   ✅ sed -i 's|pattern|replacement|g'     (Linux)

6. USE FIND + SED for bulk updates
   ✅ find dir/ -name "*.sh" -exec sed -i '' 's|old|new|g' {} \;

7. VARIABLE ESCAPING
   When pattern contains ${VARIABLE}:
   ✅ Use single quotes: 's|${OLD}|${NEW}|g'
   Or escape: "s|\${OLD}|\${NEW}|g"

========================================
EOF
}

# Run if executed directly
if [ "${BASH_SOURCE[0]}" = "${0}" ]; then
    show_key_insights
fi
