# Source: .claude/agents/prp-initial-example-curator.md (lines 16-101)
# Pattern: Code extraction methodology - ACTUAL files, not references
# Purpose: Shows correct way to extract code examples to physical files

## CRITICAL: Code Extraction, Not References

**WRONG** ❌:
```markdown
See src/api/auth.py for authentication pattern
See tests/test_api.py for testing approach
```

**RIGHT** ✅:
```python
# 1. Read the source file
source = Read("src/api/auth.py")

# 2. Extract relevant code sections
auth_pattern = extract_lines(source, start=45, end=67)

# 3. Write to examples directory
Write(f"examples/{feature_name}/auth_pattern.py", auth_pattern)

# 4. Document in README with "what to mimic" guidance
```

## Archon-First Search Strategy

```python
# 1. Search Archon for code examples (2-5 keywords!)
archon_examples = mcp__archon__rag_search_code_examples(
    query="async tool implementation",  # SHORT!
    match_count=5
)

# 2. If Archon has examples, extract and save them
if archon_examples:
    for example in archon_examples:
        extract_code_from_archon(example)
        save_to_examples_dir(example)

# 3. Search local codebase for additional patterns
local_files = Grep(pattern="@agent.tool", glob="**/*.py", output_mode="files_with_matches")

for file in local_files:
    extract_relevant_sections(file)
    save_to_examples_dir(file)
```

## Core Extraction Process

### 1. Read Requirements
- Input: `prps/research/feature-analysis.md`
- Extract: Technical components, implementation patterns needed

### 2. Search for Examples
- Search Archon code examples (SHORT queries!)
- Search local codebase with Grep/Glob
- Identify 2-4 most relevant examples

### 3. EXTRACT Code to Files
**This is the most critical step:**

```python
# Create examples directory
Bash(f"mkdir -p examples/{feature_name}")

# For each example found:
# 1. Read source
source_content = Read("path/to/source/file.py")

# 2. Extract relevant section (lines or full file)
if specific_pattern:
    # Extract specific lines
    code = extract_lines(source_content, start_line, end_line)
else:
    # Use entire file if small and relevant
    code = source_content

# 3. Create physical file in examples directory
Write(f"examples/{feature_name}/pattern_name.py", code)

# 4. Add source attribution as comment
attribution = f"""# Source: {original_file}
# Lines: {start_line}-{end_line}
# Pattern: {what_it_demonstrates}

{code}
"""
```

## Directory Structure to Create

```bash
examples/{feature_name}/
├── README.md                    # Comprehensive usage guide
├── {pattern_1}.py               # Extracted code file 1
├── {pattern_2}.py               # Extracted code file 2
├── {pattern_3}.py               # Extracted code file 3
└── test_{pattern}.py            # Test example if found
```

## README.md Requirements

Must include for EACH example:

### File Overview Table
| File | Source | Purpose | Relevance |
|------|--------|---------|-----------|
| pattern1.py | path/to/source:45-67 | What it shows | 9/10 |

### Detailed Guidance Per Example

**What to Mimic**:
- Specific technique 1
- Specific technique 2
- Specific technique 3

**What to Adapt**:
- Replace X with Y for your use case
- Adjust Z parameter
- Modify A to fit your requirements

**What to Skip**:
- Irrelevant code (specific to original context)
- UI logic (if not applicable)

**Pattern Highlights**:
```python
# Code snippet showing the key pattern
```

**Why This Example**:
1-2 sentences explaining value

## Key Patterns to Mimic

1. **Physical Files**: Create actual .py/.js/.md files, NOT markdown with code blocks
2. **Source Attribution**: Add comments at top of each file showing origin
3. **README Documentation**: Comprehensive "what to mimic" guidance for each example
4. **Relevance Scoring**: Rate each example X/10 for applicability
5. **Pattern Highlights**: Extract and highlight the key technique in README
6. **Complete Context**: Include enough code to be runnable/understandable
7. **Archon First**: Search Archon before local codebase
8. **Short Queries**: 2-5 keywords for Archon searches

This is the MOST IMPORTANT difference from current generate-prp - we extract ACTUAL CODE FILES, not just references to existing files.
