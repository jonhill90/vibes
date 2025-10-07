# Feature Analysis: Standardize PRP Naming Convention

## INITIAL.md Summary

This PRP establishes a consistent naming convention for PRPs that eliminates redundant prefixes (like `prp_`) and clarifies when to use `strip_prefix` in execute-prp.md. The goal is to prevent confusion about when prefixes should be stripped, standardize on `INITIAL_{feature_name}.md` for generated PRPs and `{feature_name}.md` for final PRPs, and ensure directory structures match PRP filenames without redundancy.

## Core Requirements

### Explicit Requirements (from INITIAL.md)

1. **Naming Convention Definition**
   - PRP files: `prps/{feature_name}.md` (no `prp_` prefix)
   - Initial PRPs: `prps/INITIAL_{feature_name}.md` (from /generate-prp)
   - Directories: `prps/{feature_name}/` (matches PRP filename)
   - Clear examples of correct vs incorrect naming

2. **Strip Prefix Rules Documentation**
   - Use `strip_prefix="INITIAL_"` for initial PRPs only
   - Use `strip_prefix=None` for final PRPs (default)
   - Never use `strip_prefix="prp_"` (not a workflow prefix)
   - Document rules in execute-prp.md Phase 0

3. **Workflow Documentation**
   - /generate-prp creates: `INITIAL_{feature_name}.md`
   - After refinement: Rename to `{feature_name}.md`
   - /execute-prp handles both formats
   - Document in CLAUDE.md and README.md

4. **Code Updates**
   - Update execute-prp.md Phase 0 with clear strip_prefix logic
   - Add validation to prevent redundant prefixes
   - Update /generate-prp to avoid creating `prp_` prefixed names
   - Optional: Add linter rule

5. **Retroactive Cleanup (Optional)**
   - Identify existing PRPs with redundant prefixes
   - Rename if desired (or leave for historical context)
   - Update references if renamed

### Implicit Requirements

1. **Developer Experience**
   - Clear decision tree: when to use INITIAL_ vs no prefix
   - FAQ section addressing common questions
   - Examples showing good vs bad naming patterns
   - Error messages that are actionable (not just warnings)

2. **Backward Compatibility**
   - Existing PRPs should continue to work
   - Validation should be opt-in for legacy files
   - Migration path for existing `prp_*` files

3. **Consistency with Security Patterns**
   - Maintain existing 5-level security validation in `extract_feature_name()`
   - Ensure strip_prefix doesn't bypass security checks
   - Validate feature names after prefix stripping

4. **Integration with Archon Workflow**
   - Project naming should follow convention
   - Task descriptions should reference correct paths
   - No breaking changes to Archon integration

5. **Testing Strategy**
   - Test cases for strip_prefix logic
   - Validation function test cases
   - Linter test cases (if implemented)
   - Edge cases: empty names, very long names, special characters

## Technical Components

### Data Models

**Feature Name Model** (string validation):
- Pattern: `^[a-zA-Z0-9_-]+$`
- Max length: 50 characters
- No path traversal characters
- No command injection characters
- Optional prefix stripping: `INITIAL_`

**PRP File Path Model**:
- Base path: `prps/`
- Initial format: `prps/INITIAL_{feature_name}.md`
- Final format: `prps/{feature_name}.md`
- Directory format: `prps/{feature_name}/`

**Report Coverage Model**:
```python
{
    "total_tasks": int,
    "reports_found": int,
    "coverage_percentage": float,
    "missing_tasks": list[int],
    "status": str  # "✅ COMPLETE" or "⚠️ INCOMPLETE"
}
```

### External Integrations

**None** - This is purely internal tooling/convention

### Core Logic

1. **Feature Name Extraction with Strip Prefix**
   ```python
   def extract_feature_name(filepath: str, strip_prefix: str = None, validate_no_redundant: bool = True) -> str:
       # 5-level security validation (existing)
       # Strip prefix if provided (INITIAL_)
       # Validate no redundant prp_ prefix (new)
       # Return validated feature name
   ```

2. **Auto-Detection Logic for INITIAL_ Prefix**
   ```python
   if "INITIAL_" in prp_path.split("/")[-1]:
       feature_name = extract_feature_name(prp_path, strip_prefix="INITIAL_")
   else:
       feature_name = extract_feature_name(prp_path)
   ```

3. **Redundant Prefix Validation**
   ```python
   if validate_no_redundant and feature_name.startswith("prp_"):
       raise ValueError(f"Redundant 'prp_' prefix detected...")
   ```

4. **Linter Logic (Optional)**
   ```python
   for prp_file in prps_dir.glob("*.md"):
       if prp_file.stem.startswith("INITIAL_"):
           continue  # Valid workflow prefix
       if prp_file.stem.startswith("prp_"):
           errors.append(f"Redundant 'prp_' prefix: {prp_file}")
   ```

### UI/CLI Requirements

**No UI Changes** - This affects command-line workflows only:
- `/generate-prp INITIAL_{feature_name}.md` (output path)
- `/execute-prp prps/{feature_name}.md` (input path)
- Error messages in terminal output
- Validation warnings in terminal output

## Similar Implementations Found in Archon

### 1. Execution Reliability PRP (execution_reliability.md)
- **Relevance**: 8/10
- **Archon ID**: Not found in search (local codebase only)
- **Key Patterns**:
  - Uses validation gates for enforcing conventions
  - Implements fail-fast on naming violations
  - Provides actionable error messages with troubleshooting
  - Uses templates for standardization
- **Gotchas**:
  - Silent failures lead to technical debt (apply to naming too)
  - Inconsistent patterns make automation impossible (6 different report naming patterns discovered)
  - Validation must be mandatory, not optional

**Applicable Patterns**:
- Fail-fast validation with clear error messages
- Template-based standardization
- Coverage metrics (report coverage → naming convention compliance)
- Actionable error format: Problem → Expected → Impact → Troubleshooting → Resolution

### 2. Context Refactor PRP (prp_context_refactor.md)
- **Relevance**: 7/10
- **Archon ID**: Not found in search
- **Key Patterns**:
  - Uses `extract_feature_name()` with `strip_prefix="INITIAL_"`
  - Security validation pattern (5 levels)
  - Documentation of rationale alongside implementation
- **Gotchas**:
  - This file itself has `prp_` prefix (demonstrates the problem!)
  - Filename: `prp_context_refactor.md` should be `context_refactor.md`

**Applicable Patterns**:
- Same `extract_feature_name()` function signature to modify
- Security validation pattern to preserve
- Need to update this PRP's own filename as example

### 3. Security Validation Pattern (.claude/patterns/security-validation.md)
- **Relevance**: 9/10
- **Archon ID**: Not found in search
- **Key Patterns**:
  - 5-level security validation (already implemented)
  - Shows exact usage: `extract_feature_name(initial_md_path, strip_prefix="INITIAL_")`
  - Test cases included
- **Gotchas**:
  - Pattern is already correct for INITIAL_ stripping
  - Need to add validation for redundant prp_ prefix
  - Security checks must run AFTER prefix stripping

**Applicable Patterns**:
- Reuse existing 5-level validation structure
- Add 6th check for redundant prefix validation
- Maintain test case format

## Recommended Technology Stack

**No new technologies required** - uses existing stack:

- **Language**: Python 3 (for validation functions, linter)
- **Pattern Matching**: Python `re` module (regex)
- **File System**: Python `pathlib` (for linter globbing)
- **Documentation**: Markdown (existing format)
- **Validation**: Python exceptions (`ValueError`, `ValidationError`)
- **Testing**: Manual test cases in validation sections (no pytest needed)

## Assumptions Made

### 1. **Assumption Category**: Directory Structure
   - **Specific Assumption**: `prps/{feature_name}/` directories should always match PRP filename without prefix
   - **Reasoning**: This prevents confusion when navigating filesystem. If PRP is `task_management_ui.md`, directory should be `task_management_ui/`, not `prp_task_management_ui/`
   - **Source**: INITIAL.md explicit requirement + execution reliability pattern (shows feature_name used for directory creation)

### 2. **Assumption Category**: INITIAL_ Prefix Lifecycle
   - **Specific Assumption**: `INITIAL_{feature_name}.md` files should be renamed to `{feature_name}.md` after generation is complete and before execution
   - **Reasoning**: INITIAL_ indicates "work in progress from /generate-prp". Once refined, it becomes the canonical PRP
   - **Source**: INITIAL.md workflow section + observation that generate-prp creates INITIAL_ but execute-prp expects final name

### 3. **Assumption Category**: Backward Compatibility
   - **Specific Assumption**: Existing `prp_*` files should trigger warnings but not break execution
   - **Reasoning**: PRPs already executed (like prp_context_refactor.md) have historical value. Breaking them would require retroactive fixes
   - **Source**: Best practice for deprecation (warn first, enforce later) + INITIAL.md marks retroactive cleanup as "Optional"

### 4. **Assumption Category**: Validation Strictness
   - **Specific Assumption**: New PRPs should fail validation with redundant prefix, but existing PRPs should warn only
   - **Reasoning**: Prevents new technical debt while allowing time to migrate legacy files
   - **Source**: Execution reliability pattern (validation gates) + INITIAL.md optional cleanup tasks

### 5. **Assumption Category**: Strip Prefix Scope
   - **Specific Assumption**: Only `INITIAL_` is a valid workflow prefix to strip. `prp_` is never valid for stripping
   - **Reasoning**: `INITIAL_` indicates lifecycle stage. `prp_` is redundant with `prps/` directory
   - **Source**: INITIAL.md explicit rule + security validation pattern showing INITIAL_ usage

### 6. **Assumption Category**: Documentation Placement
   - **Specific Assumption**: Create new `.claude/conventions/prp-naming.md` file rather than modifying existing files inline
   - **Reasoning**: Conventions deserve their own directory for discoverability. Keeps CLAUDE.md concise with references
   - **Source**: INITIAL.md Task 1 specification + observation that `.claude/patterns/` exists for reusable patterns

### 7. **Assumption Category**: Linter Implementation
   - **Specific Assumption**: Linter should be standalone Python script, not integrated into execute-prp.md
   - **Reasoning**: Separation of concerns - linter is for proactive checking, execute-prp is for execution
   - **Source**: INITIAL.md Task 8 shows `scripts/lint_prp_names.py` + common linting practices

### 8. **Assumption Category**: Auto-Detection Logic
   - **Specific Assumption**: execute-prp.md should auto-detect INITIAL_ prefix in filename and strip it automatically
   - **Reasoning**: Reduces developer cognitive load. No need to remember strip_prefix parameter
   - **Source**: INITIAL.md Task 2 shows detection logic + DX improvement principle

### 9. **Assumption Category**: Error Message Format
   - **Specific Assumption**: Use execution reliability error format (Problem → Expected → Impact → Troubleshooting → Resolution)
   - **Reasoning**: Consistency with existing validation gates. Proven to be actionable
   - **Source**: Execution reliability PRP validation gate pattern (format_missing_report_error function)

### 10. **Assumption Category**: Archon Integration
   - **Specific Assumption**: Archon project titles and task descriptions should use feature_name (without prefixes)
   - **Reasoning**: Archon UI is user-facing. Clean names improve readability
   - **Source**: Archon workflow pattern + INITIAL.md requirement for consistent naming

## Success Criteria

From INITIAL.md (explicit):
- [ ] Naming convention documented in CLAUDE.md
- [ ] execute-prp.md Phase 0 has clear strip_prefix logic with comments
- [ ] /generate-prp creates PRPs without redundant prefixes
- [ ] Validation catches redundant prefixes (raises error)
- [ ] Developer guide explains when to strip prefixes
- [ ] Optional: Existing PRPs conform to convention

Additional (inferred from analysis):
- [ ] All 5 research docs created (feature-analysis, codebase-patterns, documentation-links, examples-to-include, gotchas)
- [ ] Auto-detection logic works for INITIAL_ prefix
- [ ] Validation warnings are actionable
- [ ] Backward compatibility maintained
- [ ] `.claude/conventions/prp-naming.md` created with comprehensive rules
- [ ] FAQ addresses common developer questions
- [ ] Test cases validate strip_prefix logic
- [ ] Linter (if implemented) catches violations without false positives

## Next Steps for Downstream Agents

### Codebase Researcher (Phase 2A)
**Focus on**:
1. Find all occurrences of `extract_feature_name()` in codebase
   - Files: `.claude/commands/execute-prp.md`, `.claude/commands/generate-prp.md`, `.claude/patterns/security-validation.md`
   - Pattern: Look for function definition and all call sites
2. Identify current strip_prefix usage patterns
   - Search: `strip_prefix="INITIAL_"` and `strip_prefix="prp_"`
   - Document which files use which patterns
3. Find all existing PRP files with naming variations
   - Pattern: `prps/prp_*.md` (redundant prefix)
   - Pattern: `prps/INITIAL_*.md` (workflow prefix)
   - Pattern: `prps/*.md` (clean names)
4. Examine error message patterns in execute-prp.md
   - Look for: `ValidationError`, `format_missing_report_error`
   - Extract pattern for actionable error messages
5. Search for directory creation logic
   - Pattern: `mkdir -p prps/{feature_name}/`
   - Verify feature_name is used consistently

### Documentation Hunter (Phase 2B)
**Find docs for**:
1. **Python regex patterns**
   - Focus: `re.match()`, character classes, anchors
   - Need: Examples of whitelist validation patterns
2. **Python pathlib usage**
   - Focus: `Path.glob()`, `Path.stem`, `Path.read_text()`
   - Need: Examples for linter implementation
3. **Markdown documentation best practices**
   - Focus: Convention documentation structure
   - Need: Examples of "good vs bad" comparison tables
4. **Error message design**
   - Focus: Actionable error messages, troubleshooting guides
   - Need: Examples of Problem → Resolution format
5. **File naming conventions** (general software engineering)
   - Focus: Why avoid redundant prefixes
   - Need: Industry best practices citations

### Example Curator (Phase 2C)
**Extract examples showing**:
1. **Validation function patterns** from `execution_reliability/examples/validation_gate_pattern.py`
   - EXTRACT: Full validation gate functions with docstrings
   - WHAT TO MIMIC: EAFP pattern, actionable errors, security checks
2. **Error message formatting** from `execute-prp.md`
   - EXTRACT: `format_missing_report_error()` function
   - WHAT TO MIMIC: Problem → Expected → Impact → Troubleshooting → Resolution structure
3. **Security validation** from `.claude/patterns/security-validation.md`
   - EXTRACT: 5-level validation with test cases
   - WHAT TO MIMIC: Layered validation approach, clear reasoning for each check
4. **Linter patterns** from any existing linter scripts (if found)
   - SEARCH: `scripts/lint_*.py` or similar
   - WHAT TO MIMIC: Error accumulation, clear exit codes, helpful messages
5. **Documentation examples** from `.claude/patterns/` or `.claude/commands/`
   - EXTRACT: Well-structured documentation with examples
   - WHAT TO MIMIC: Clear sections, code blocks, decision trees

### Gotcha Detective (Phase 3)
**Investigate known problem areas**:
1. **Path Traversal in strip_prefix**
   - GOTCHA: If strip_prefix contains "..", could bypass security
   - SOLUTION: Validate strip_prefix parameter itself, or only allow hardcoded values
2. **Race Conditions in File Existence Checks**
   - GOTCHA: TOCTOU (Time-of-check-time-of-use) if using `os.path.exists()` then `open()`
   - SOLUTION: Use EAFP pattern (try/except FileNotFoundError) like execution reliability
3. **Regex Injection in Feature Names**
   - GOTCHA: If feature_name is used in regex patterns without escaping
   - SOLUTION: Use `re.escape()` or stick to whitelist validation
4. **Unicode in Filenames**
   - GOTCHA: Some filesystems handle Unicode differently
   - SOLUTION: Stick to ASCII alphanumeric + underscore/hyphen (already in pattern)
5. **Case Sensitivity**
   - GOTCHA: `INITIAL_` vs `initial_` on case-insensitive filesystems
   - SOLUTION: Use exact case matching in detection logic
6. **Partial Matches in strip_prefix**
   - GOTCHA: `feature.replace(strip_prefix, "")` replaces ALL occurrences
   - SOLUTION: Use `feature.removeprefix(strip_prefix)` (Python 3.9+) or check starts_with
7. **Empty Feature Names After Stripping**
   - GOTCHA: File named exactly `INITIAL_.md` would produce empty feature name
   - SOLUTION: Add length check after stripping (already have max length check)
8. **Directory/File Mismatch**
   - GOTCHA: PRP file exists but directory doesn't match
   - SOLUTION: Validation should check directory existence and name match
9. **Breaking Existing PRPs**
   - GOTCHA: Strict validation breaks legacy `prp_*` files
   - SOLUTION: Make validation opt-in via parameter, default to warnings only
10. **Archon Project Naming**
    - GOTCHA: Changing feature_name format could break Archon project references
    - SOLUTION: Update Archon integration to use consistent feature_name format

## Validation Strategy

### Level 1: Documentation Validation
```bash
# Verify convention documented
test -f .claude/conventions/prp-naming.md
grep "Naming Convention" CLAUDE.md
grep "prp-naming.md" README.md
```

### Level 2: Code Validation
```python
# Test strip_prefix logic
test_cases = [
    ("prps/INITIAL_user_auth.md", "INITIAL_", "user_auth"),
    ("prps/user_auth.md", None, "user_auth"),
    ("prps/prp_redundant.md", None, "should_raise_error"),
]
for path, prefix, expected in test_cases:
    result = extract_feature_name(path, strip_prefix=prefix)
    assert result == expected or "should_raise_error"
```

### Level 3: Integration Validation
```bash
# Test with actual PRP workflow
/generate-prp prps/INITIAL_test_feature.md
# Should create INITIAL_test_feature.md
test -f prps/INITIAL_test_feature.md

# Execute should auto-detect INITIAL_ prefix
/execute-prp prps/INITIAL_test_feature.md
# Should create prps/test_feature/ directory (not INITIAL_test_feature/)
test -d prps/test_feature
```

### Level 4: Linter Validation (if implemented)
```bash
# Linter should catch violations
python scripts/lint_prp_names.py
# Should pass if no prp_*.md files exist

# Test linter catches violations
echo "test" > prps/prp_bad.md
python scripts/lint_prp_names.py
# Should fail with clear error message
rm prps/prp_bad.md
```

## Migration Path for Existing PRPs

Current state analysis (from codebase search):
```
✅ Clean names (no prefix):
- execution_reliability.md
- cleanup_execution_reliability_artifacts.md
- readme_update.md
- task_management_ui.md

❌ Redundant prp_ prefix:
- prp_context_refactor.md

🔄 INITIAL_ prefix (work in progress):
- INITIAL_standardize_prp_naming_convention.md
- INITIAL_cleanup_execution_reliability_artifacts.md
- INITIAL_readme_update.md
- INITIAL_task_management_ui.md
- INITIAL_prp_context_refactor.md
- INITIAL_prp_execution_reliability.md

📁 Example (not a real PRP):
- EXAMPLE_multi_agent_prp.md
```

**Recommended Migration**:
1. Phase 1: Implement validation with warnings only (no breaking changes)
2. Phase 2: Document convention and update tooling
3. Phase 3 (optional): Rename `prp_context_refactor.md` to `context_refactor.md`
4. Phase 4 (optional): Add validation gate to prevent new `prp_*` files

## Risk Assessment

### Medium Risk Areas

1. **Breaking Existing Workflows**
   - Risk: Strict validation could break existing PRPs mid-execution
   - Mitigation: Opt-in validation, warnings-first approach, backward compatibility

2. **Developer Confusion During Transition**
   - Risk: Mix of old and new conventions during migration period
   - Mitigation: Clear documentation, actionable error messages, FAQ section

3. **Archon Integration Changes**
   - Risk: Changing feature_name format could affect Archon project tracking
   - Mitigation: Test Archon integration, ensure project_id mapping still works

### Low Risk Areas

1. **Security Validation Changes**
   - Risk: Adding validation could miss edge cases
   - Mitigation: Preserve existing 5-level validation, add 6th check separately

2. **Linter False Positives**
   - Risk: Linter could flag legitimate prp_ names (if part of actual feature)
   - Mitigation: Document exceptions, allow linter bypass for special cases

## Estimated Implementation Time

Based on INITIAL.md and task complexity:

**Core Tasks (60-90 minutes)**:
- Task 1: Documentation (15 min)
- Task 2: Update execute-prp.md (15 min)
- Task 3: Update generate-prp.md (10 min)
- Task 4: Add validation function (20 min)
- Task 5: Developer guide (20 min)
- Testing and validation (10 min)

**Optional Tasks (30-60 minutes)**:
- Task 6: Audit existing PRPs (15 min)
- Task 7: Rename PRPs (15 min)
- Task 8: Linter implementation (30 min)

**Total**: 60-150 minutes depending on scope

## Quality Score Assessment

Based on quality-gates.md criteria:

**Confidence Level**: 8.5/10

**Reasoning**:
- ✅ Clear requirements from detailed INITIAL.md
- ✅ Similar patterns found in execution_reliability PRP
- ✅ Security validation pattern already exists to build on
- ✅ Validation strategy well-defined
- ✅ Backward compatibility considered
- ⚠️ No Archon knowledge base matches (relying on local codebase)
- ⚠️ Edge cases around partial stripping need careful handling
- ✅ Migration path clear with low-risk approach

**Readiness for PRP Generation**: HIGH - Downstream agents have clear guidance on what to research and extract.
