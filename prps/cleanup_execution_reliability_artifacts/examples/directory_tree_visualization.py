#!/usr/bin/env python3
"""
Source: Feature analysis for cleanup_execution_reliability_artifacts
Pattern: Directory tree visualization for before/after comparisons
Extracted: 2025-10-07
Relevance: 9/10 - Useful for documenting directory structure changes
"""

import sys
from pathlib import Path
from typing import List, Set, Optional


# =============================================================================
# PATTERN 1: Generate Directory Tree (Similar to `tree` command)
# =============================================================================

def generate_tree(
    directory: Path,
    prefix: str = "",
    max_depth: Optional[int] = None,
    current_depth: int = 0,
    exclude_patterns: Set[str] = None
) -> List[str]:
    """
    Generate a tree-style representation of a directory structure.

    Args:
        directory: Root directory to visualize
        prefix: Current line prefix (used for recursion)
        max_depth: Maximum depth to traverse (None = unlimited)
        current_depth: Current recursion depth
        exclude_patterns: Set of patterns to exclude (e.g., {'.git', '__pycache__'})

    Returns:
        List of lines representing the tree
    """
    if exclude_patterns is None:
        exclude_patterns = {'.git', '__pycache__', '.pyc', '.DS_Store', 'node_modules'}

    lines = []

    # Check depth limit
    if max_depth is not None and current_depth >= max_depth:
        return lines

    # Get directory contents
    try:
        items = sorted(directory.iterdir(), key=lambda x: (not x.is_dir(), x.name))
    except PermissionError:
        return [f"{prefix}[Permission Denied]"]

    # Filter out excluded patterns
    items = [
        item for item in items
        if not any(pattern in item.name for pattern in exclude_patterns)
    ]

    for i, item in enumerate(items):
        is_last = i == len(items) - 1

        # Determine prefix characters
        if is_last:
            connector = "└── "
            extension = "    "
        else:
            connector = "├── "
            extension = "│   "

        # Add item to tree
        item_name = item.name + ("/" if item.is_dir() else "")
        lines.append(f"{prefix}{connector}{item_name}")

        # Recurse for directories
        if item.is_dir():
            sub_lines = generate_tree(
                item,
                prefix + extension,
                max_depth,
                current_depth + 1,
                exclude_patterns
            )
            lines.extend(sub_lines)

    return lines


def print_tree(
    directory: Path,
    max_depth: Optional[int] = None,
    exclude_patterns: Set[str] = None
) -> str:
    """
    Print a directory tree.

    Args:
        directory: Directory to visualize
        max_depth: Maximum depth to show
        exclude_patterns: Patterns to exclude

    Returns:
        String representation of tree
    """
    if not directory.exists():
        return f"Error: Directory does not exist: {directory}"

    # Start with root directory name
    lines = [str(directory) + "/"]

    # Generate tree
    tree_lines = generate_tree(directory, "", max_depth, 0, exclude_patterns)
    lines.extend(tree_lines)

    return "\n".join(lines)


# =============================================================================
# PATTERN 2: Before/After Directory Comparison
# =============================================================================

def compare_directory_structures(
    before_dir: Path,
    after_dir: Path,
    max_depth: Optional[int] = None
) -> str:
    """
    Generate side-by-side before/after directory comparison.

    Args:
        before_dir: Directory structure before changes
        after_dir: Directory structure after changes
        max_depth: Maximum depth to show

    Returns:
        Formatted comparison string
    """
    lines = []

    lines.append("=" * 80)
    lines.append("DIRECTORY STRUCTURE COMPARISON")
    lines.append("=" * 80)

    # Before structure
    lines.append("")
    lines.append("BEFORE:")
    lines.append("-" * 40)
    before_tree = print_tree(before_dir, max_depth)
    lines.append(before_tree)

    # After structure
    lines.append("")
    lines.append("AFTER:")
    lines.append("-" * 40)
    after_tree = print_tree(after_dir, max_depth)
    lines.append(after_tree)

    lines.append("")
    lines.append("=" * 80)

    return "\n".join(lines)


# =============================================================================
# PATTERN 3: Directory Summary Statistics
# =============================================================================

def get_directory_stats(directory: Path, max_depth: Optional[int] = None) -> dict:
    """
    Get statistics about a directory structure.

    Args:
        directory: Directory to analyze
        max_depth: Maximum depth to traverse

    Returns:
        dict with statistics
    """
    stats = {
        "total_files": 0,
        "total_dirs": 0,
        "total_size_bytes": 0,
        "file_types": {},
        "largest_files": [],  # List of (size, path) tuples
    }

    def traverse(path: Path, depth: int = 0):
        if max_depth is not None and depth >= max_depth:
            return

        for item in path.iterdir():
            if item.name.startswith('.'):
                continue  # Skip hidden files

            if item.is_file():
                stats["total_files"] += 1
                size = item.stat().st_size
                stats["total_size_bytes"] += size

                # Track file type
                suffix = item.suffix or "(no extension)"
                stats["file_types"][suffix] = stats["file_types"].get(suffix, 0) + 1

                # Track largest files (keep top 10)
                stats["largest_files"].append((size, str(item)))
                stats["largest_files"].sort(reverse=True)
                stats["largest_files"] = stats["largest_files"][:10]

            elif item.is_dir():
                stats["total_dirs"] += 1
                traverse(item, depth + 1)

    traverse(directory)

    return stats


def print_directory_stats(stats: dict) -> str:
    """Format directory statistics for display."""
    lines = []

    lines.append("Directory Statistics:")
    lines.append(f"  Total files: {stats['total_files']}")
    lines.append(f"  Total directories: {stats['total_dirs']}")
    lines.append(f"  Total size: {stats['total_size_bytes']:,} bytes ({stats['total_size_bytes'] / 1024:.1f} KB)")

    if stats['file_types']:
        lines.append("")
        lines.append("  File types:")
        for file_type, count in sorted(stats['file_types'].items(), key=lambda x: x[1], reverse=True):
            lines.append(f"    {file_type}: {count}")

    if stats['largest_files']:
        lines.append("")
        lines.append("  Largest files:")
        for size, path in stats['largest_files'][:5]:
            lines.append(f"    {size:,} bytes - {path}")

    return "\n".join(lines)


# =============================================================================
# PATTERN 4: Markdown Directory Tree (For Documentation)
# =============================================================================

def generate_markdown_tree(
    directory: Path,
    max_depth: Optional[int] = None,
    include_stats: bool = False
) -> str:
    """
    Generate a markdown-formatted directory tree.

    Args:
        directory: Directory to visualize
        max_depth: Maximum depth to show
        include_stats: Include statistics at the end

    Returns:
        Markdown-formatted tree
    """
    lines = []

    # Title
    lines.append(f"# Directory Structure: {directory.name}")
    lines.append("")

    # Tree in code block
    lines.append("```")
    tree = print_tree(directory, max_depth)
    lines.append(tree)
    lines.append("```")

    # Optional statistics
    if include_stats:
        lines.append("")
        lines.append("## Statistics")
        lines.append("")
        stats = get_directory_stats(directory, max_depth)
        lines.append(print_directory_stats(stats))

    return "\n".join(lines)


# =============================================================================
# USAGE EXAMPLE: Document execution_reliability cleanup
# =============================================================================

def document_execution_reliability_cleanup():
    """
    Example: Generate before/after documentation for execution_reliability cleanup.
    """
    print("=" * 80)
    print("Directory Visualization Example: execution_reliability Cleanup")
    print("=" * 80)

    # Define before state (conceptual - these directories may not exist)
    print("\n## BEFORE STATE (Conceptual)")
    print("-" * 80)

    before_structure = """
prps/
├── prp_execution_reliability.md (PRP file with redundant prefix)
├── prp_execution_reliability/
│   ├── examples/ (split location 1)
│   │   └── validation_gate_pattern.py
│   ├── planning/ (split location 1)
│   │   └── feature-analysis.md
│   └── execution/
│       └── TASK8_TEST_RESULTS.md (orphaned file)
└── execution_reliability/
    └── execution/
        ├── TASK1_COMPLETION.md
        ├── TASK2_COMPLETION.md
        ├── TASK3_COMPLETION.md
        ├── TASK4_COMPLETION.md
        ├── TASK5_COMPLETION.md
        ├── TASK6_COMPLETION.md
        ├── TASK7_COMPLETION.md
        ├── TASK8_COMPLETION.md
        └── EXECUTION_SUMMARY.md

test_validation_gates_script.py (orphaned in root)
"""
    print(before_structure)

    print("\n## AFTER STATE (Expected)")
    print("-" * 80)

    after_structure = """
prps/
├── execution_reliability.md (renamed, no redundant prefix)
└── execution_reliability/
    ├── examples/ (consolidated)
    │   └── validation_gate_pattern.py
    ├── planning/ (consolidated)
    │   └── feature-analysis.md
    └── execution/
        ├── TASK1_COMPLETION.md
        ├── TASK2_COMPLETION.md
        ├── TASK3_COMPLETION.md
        ├── TASK4_COMPLETION.md
        ├── TASK5_COMPLETION.md
        ├── TASK6_COMPLETION.md
        ├── TASK7_COMPLETION.md
        ├── TASK8_COMPLETION.md
        ├── TASK8_TEST_RESULTS.md (moved here)
        └── EXECUTION_SUMMARY.md

prps/test_validation_gates/
└── test_script.py (relocated from root)
"""
    print(after_structure)

    # If actual directory exists, show real tree
    actual_dir = Path("prps/execution_reliability")
    if actual_dir.exists():
        print("\n## ACTUAL STATE (Current)")
        print("-" * 80)
        print(print_tree(actual_dir, max_depth=3))

        print("\n## STATISTICS")
        print("-" * 80)
        stats = get_directory_stats(actual_dir)
        print(print_directory_stats(stats))


def generate_cleanup_documentation(feature_name: str, output_file: Optional[Path] = None):
    """
    Generate markdown documentation for a cleanup operation.

    Args:
        feature_name: Name of feature being cleaned up
        output_file: Optional file to write documentation to
    """
    feature_dir = Path(f"prps/{feature_name}")

    if not feature_dir.exists():
        print(f"Error: Directory does not exist: {feature_dir}")
        return

    # Generate markdown
    markdown = []

    markdown.append(f"# Cleanup Documentation: {feature_name}")
    markdown.append("")
    markdown.append(f"**Date**: {Path(__file__).stat().st_mtime}")
    markdown.append("")

    # Current structure
    markdown.append("## Current Directory Structure")
    markdown.append("")
    markdown.append("```")
    tree = print_tree(feature_dir, max_depth=4)
    markdown.append(tree)
    markdown.append("```")
    markdown.append("")

    # Statistics
    markdown.append("## Statistics")
    markdown.append("")
    stats = get_directory_stats(feature_dir)
    markdown.append(print_directory_stats(stats))
    markdown.append("")

    # File listing
    markdown.append("## File Listing")
    markdown.append("")
    markdown.append("| File | Type | Size |")
    markdown.append("|------|------|------|")

    for file_path in sorted(feature_dir.rglob("*")):
        if file_path.is_file():
            relative = file_path.relative_to(feature_dir)
            file_type = file_path.suffix or "(none)"
            size = file_path.stat().st_size
            markdown.append(f"| {relative} | {file_type} | {size:,} bytes |")

    markdown.append("")

    # Combine
    result = "\n".join(markdown)

    # Output
    if output_file:
        output_file.write_text(result)
        print(f"✅ Documentation written to: {output_file}")
    else:
        print(result)


# =============================================================================
# Main execution
# =============================================================================

if __name__ == "__main__":
    print("Directory tree visualization script loaded")
    print("\nAvailable functions:")
    print("  - print_tree(directory, max_depth=None)")
    print("  - compare_directory_structures(before_dir, after_dir)")
    print("  - get_directory_stats(directory)")
    print("  - generate_markdown_tree(directory, include_stats=False)")
    print("  - document_execution_reliability_cleanup()")
    print("  - generate_cleanup_documentation(feature_name, output_file=None)")
    print("\nExample usage:")
    print("  python directory_tree_visualization.py")
    print("  >>> document_execution_reliability_cleanup()")

    # Run example if executed directly
    if len(sys.argv) > 1:
        feature = sys.argv[1]
        output = Path(sys.argv[2]) if len(sys.argv) > 2 else None
        generate_cleanup_documentation(feature, output)
    else:
        document_execution_reliability_cleanup()
