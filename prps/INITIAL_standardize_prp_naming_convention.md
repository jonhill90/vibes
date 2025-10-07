# INITIAL: Standardize PRP Naming Convention

**Created**: 2025-10-07
**Type**: Process Improvement / Convention Standardization
**Priority**: MEDIUM (enables cleaner future PRPs)
**Estimated Time**: 60-90 minutes

---

## Goal

Establish and enforce a consistent naming convention for PRPs that eliminates redundant prefixes and clarifies when to use `strip_prefix` in execute-prp.md. Update /generate-prp and execute-prp workflows to follow the convention, document it clearly, and optionally apply it retroactively to existing PRPs.

**End State**:
- Clear naming convention: `prps/{feature_name}.md` (no `prp_` prefix)
- `INITIAL_{feature_name}.md` → `{feature_name}.md` workflow documented
- execute-prp.md correctly handles both INITIAL and final PRPs
- /generate-prp creates PRPs without redundant prefixes
- Documentation explains when to use strip_prefix parameter
- Optional: Existing PRPs renamed to follow convention

---

## Why

**Current Pain Points**:
1. **Ambiguous prefix usage**: When is `prp_` part of the name vs a prefix to strip?
2. **Inconsistent behavior**: `strip_prefix="prp_"` seems right but breaks directory structure
3. **No clear convention**: Some PRPs have `prp_` prefix, some don't
4. **Developer confusion**: Newcomers don't know when to strip prefixes
5. **Directory mismatches**: Feature name doesn't match directory structure

**Business Value**:
- Consistent naming across all PRPs (easier to find/organize)
- Clear rules for when to strip prefixes (less cognitive load)
- Better developer experience (obvious naming pattern)
- Prevents future naming bugs (like execution_reliability split)
- Self-documenting workflow (names explain lifecycle stage)

---

## What

### Core Features

1. **Naming Convention Definition**
   - PRP files: `prps/{feature_name}.md` (no redundant `prp_` prefix)
   - Initial PRPs: `prps/INITIAL_{feature_name}.md` (from /generate-prp)
   - Directories: `prps/{feature_name}/` (matches PRP filename)
   - Examples:
     - ✅ `prps/task_management_ui.md` → `prps/task_management_ui/`
     - ✅ `prps/execution_reliability.md` → `prps/execution_reliability/`
     - ❌ `prps/execution_reliability.md` (redundant prefix)

2. **Strip Prefix Rules**
   - Use `strip_prefix="INITIAL_"` for initial PRPs only
   - Use `strip_prefix=None` for final PRPs
   - Never use `strip_prefix="prp_"` (it's not a workflow prefix)
   - Document in execute-prp.md Phase 0

3. **Workflow Documentation**
   - /generate-prp creates: `INITIAL_{feature_name}.md`
   - After refinement: Rename to `{feature_name}.md`
   - /execute-prp handles both formats
   - Document in CLAUDE.md and README.md

4. **Code Updates**
   - Update execute-prp.md Phase 0 with clear strip_prefix logic
   - Add validation to prevent redundant prefixes
   - Update /generate-prp to avoid creating `prp_` prefixed names
   - Add linter rule (optional)

5. **Retroactive Cleanup (Optional)**
   - Identify existing PRPs with redundant prefixes
   - Rename if desired (or leave as-is for historical context)
   - Update references if renamed

### Success Criteria

- [ ] Naming convention documented in CLAUDE.md
- [ ] execute-prp.md Phase 0 has clear strip_prefix logic with comments
- [ ] /generate-prp creates PRPs without redundant prefixes
- [ ] Validation catches redundant prefixes (raises error)
- [ ] Developer guide explains when to strip prefixes
- [ ] Optional: Existing PRPs conform to convention

---

## Tasks

```yaml
Task 1: Define and Document Naming Convention
RESPONSIBILITY: Create comprehensive naming convention documentation
FILES TO CREATE:
  - .claude/conventions/prp-naming.md
FILES TO MODIFY:
  - CLAUDE.md (add reference to naming convention)
  - README.md (add naming convention section)
SPECIFIC STEPS:
  1. Create .claude/conventions/prp-naming.md:
     - Section: "PRP Naming Convention"
     - Rules for PRP files (no redundant prefixes)
     - Rules for directories (match PRP name)
     - Workflow prefixes (INITIAL_, not prp_)
     - Examples (good vs bad)
     - Rationale for each rule
  2. Add "Naming Convention" section to CLAUDE.md:
     - Reference .claude/conventions/prp-naming.md
     - Quick rules summary
     - Link to full documentation
  3. Add naming convention to README.md:
     - Under "PRP-Driven Development" section
     - Or new "Conventions" section
VALIDATION:
  - .claude/conventions/prp-naming.md explains all rules
  - CLAUDE.md references naming convention
  - README.md includes convention overview
  - Examples are clear and correct

Task 2: Update execute-prp.md with Clear Strip Prefix Logic
RESPONSIBILITY: Add comments and validation to Phase 0 feature name extraction
FILES TO MODIFY:
  - .claude/commands/execute-prp.md (Phase 0)
SPECIFIC STEPS:
  1. Locate extract_feature_name() call in Phase 0
  2. Add comprehensive comments:
     ```python
     # Feature name extraction with prefix stripping
     #
     # NAMING CONVENTION:
     # - PRP files: prps/{feature_name}.md (no prp_ prefix)
     # - Initial PRPs: prps/INITIAL_{feature_name}.md (from /generate-prp)
     # - Directories: prps/{feature_name}/ (matches PRP filename)
     #
     # STRIP PREFIX RULES:
     # - Use strip_prefix="INITIAL_" for initial PRPs ONLY
     #   Example: prps/INITIAL_user_auth.md → feature_name="user_auth"
     #
     # - Use strip_prefix=None for final PRPs (default)
     #   Example: prps/user_auth.md → feature_name="user_auth"
     #
     # - NEVER use strip_prefix="prp_" (it's not a workflow prefix!)
     #   Bad: prps/prp_user_auth.md (redundant prefix, don't create these)
     #
     # DETECTION LOGIC:
     if "INITIAL_" in prp_path.split("/")[-1]:
         feature_name = extract_feature_name(prp_path, strip_prefix="INITIAL_")
     else:
         feature_name = extract_feature_name(prp_path)
     ```
  3. Add validation check:
     ```python
     # Validate no redundant prefixes
     if feature_name.startswith("prp_"):
         print(f"⚠️  WARNING: Feature name '{feature_name}' has redundant 'prp_' prefix")
         print(f"    Recommended: Rename prps/{feature_name}.md → prps/{feature_name[4:]}.md")
         print(f"    Continuing with current name for now...")
     ```
VALIDATION:
  - Comments explain when to use strip_prefix
  - Auto-detection logic for INITIAL_ prefix
  - Validation warns about redundant prp_ prefixes
  - Code is clear and self-documenting

Task 3: Update /generate-prp to Avoid Redundant Prefixes
RESPONSIBILITY: Ensure generated PRPs follow naming convention
FILES TO MODIFY:
  - .claude/commands/generate-prp.md
SPECIFIC STEPS:
  1. Read generate-prp.md to find PRP naming logic
  2. Locate where PRP filename is generated
  3. Ensure format is: `prps/INITIAL_{feature_name}.md`
  4. Add validation to prevent "prp_" in feature name:
     ```python
     # Extract feature name from INITIAL.md
     feature_name = initial_path.split("/")[-1].replace("INITIAL_", "").replace(".md", "")

     # Validate no redundant prp_ prefix
     if feature_name.startswith("prp_"):
         print(f"⚠️  WARNING: Feature '{feature_name}' has redundant 'prp_' prefix")
         print(f"    This creates confusion with workflow prefixes")
         print(f"    Recommended: Use '{feature_name[4:]}' instead")
         # Optionally: auto-strip or raise error
     ```
  5. Update template if needed to guide users away from "prp_" names
VALIDATION:
  - Generated PRPs use INITIAL_{feature_name}.md format
  - No "prp_" in feature names (unless explicitly part of feature)
  - Validation catches redundant prefixes
  - Documentation explains naming

Task 4: Add Prefix Validation to extract_feature_name()
RESPONSIBILITY: Prevent redundant prefixes at source
FILES TO MODIFY:
  - .claude/commands/execute-prp.md (Phase 0)
SPECIFIC STEPS:
  1. Locate extract_feature_name() function definition
  2. Add optional validation parameter:
     ```python
     def extract_feature_name(filepath: str, strip_prefix: str = None, validate_no_redundant: bool = True) -> str:
         # ... existing security checks ...

         feature = filepath.split("/")[-1].replace(".md", "")
         if strip_prefix:
             feature = feature.replace(strip_prefix, "")

         # Validate no redundant prp_ prefix (prps/ already implies PRP)
         if validate_no_redundant and feature.startswith("prp_"):
             raise ValueError(
                 f"Redundant 'prp_' prefix detected in feature name: {feature}\n"
                 f"  PRP files are already in prps/ directory - 'prp_' is redundant\n"
                 f"  Recommended: Rename prps/{feature}.md → prps/{feature[4:]}.md"
             )

         # ... rest of function ...
     ```
  3. Document validate_no_redundant parameter
  4. Allow opt-out for backward compatibility (validate_no_redundant=False)
VALIDATION:
  - Function raises clear error for redundant prefixes
  - Error message is actionable
  - Can be disabled if needed (backward compatibility)
  - Documented in function docstring

Task 5: Create Developer Guide Section
RESPONSIBILITY: Explain naming convention to developers
FILES TO CREATE:
  - docs/developer-guide.md (or add section to existing guide)
FILES TO MODIFY:
  - CLAUDE.md (link to developer guide)
SPECIFIC STEPS:
  1. Create developer guide section "PRP Naming Convention":
     - When to use INITIAL_ prefix (always from /generate-prp)
     - When to strip INITIAL_ (always in execute-prp)
     - Why no prp_ prefix (redundant with prps/ directory)
     - Examples of good naming
     - Common mistakes and how to fix
  2. Add flowchart or decision tree:
     ```
     Is this a new PRP from /generate-prp?
       Yes → Use INITIAL_{feature_name}.md
       No → Use {feature_name}.md

     Does feature_name start with "prp_"?
       Yes → Remove "prp_" (redundant)
       No → Good to go!
     ```
  3. Add FAQ section:
     - Q: Why not prp_feature_name.md?
     - Q: When do I rename INITIAL_*.md to *.md?
     - Q: What if I have an existing prp_*.md file?
VALIDATION:
  - Developer guide section is clear and comprehensive
  - Flowchart helps with decision-making
  - FAQ addresses common questions
  - Examples are actionable

Task 6: Optional - Identify Existing PRPs with Redundant Prefixes
RESPONSIBILITY: Find all PRPs that violate naming convention
FILES TO CREATE:
  - prps/naming_audit.md (audit results)
SPECIFIC STEPS:
  1. Find all PRP files:
     ```bash
     find prps -name "*.md" -type f | grep -v "INITIAL_" | grep -v "/execution/" | grep -v "/planning/"
     ```
  2. Identify those with "prp_" prefix:
     ```bash
     find prps -name "prp_*.md" -type f | grep -v "INITIAL_"
     ```
  3. Create audit report:
     - List of files with redundant prefixes
     - Recommended new names
     - Impact assessment (what would break)
     - Prioritization (which to rename first)
  4. Document in prps/naming_audit.md
VALIDATION:
  - Audit report lists all PRPs with redundant prefixes
  - Impact assessment is accurate
  - Recommendations are clear
  - Prioritization makes sense

Task 7: Optional - Rename Existing PRPs (if audit recommends)
RESPONSIBILITY: Apply naming convention retroactively
FILES TO MODIFY:
  - PRPs identified in Task 6 audit
SPECIFIC STEPS:
  1. Review audit report from Task 6
  2. For each PRP with redundant prefix:
     - Backup current state
     - Rename PRP file (prp_X.md → X.md)
     - Rename directory (prp_X/ → X/)
     - Update references in documentation
     - Test that nothing broke
  3. Document renames in git commit message
  4. Update any broken references
VALIDATION:
  - All renamed PRPs follow convention
  - No broken references
  - Directories match PRP names
  - Git history preserved (use git mv)

Task 8: Add Linter Rule (Optional)
RESPONSIBILITY: Automate redundant prefix detection
FILES TO CREATE:
  - scripts/lint_prp_names.py
FILES TO MODIFY:
  - .github/workflows/lint.yml (or CI config)
SPECIFIC STEPS:
  1. Create linter script:
     ```python
     # scripts/lint_prp_names.py
     import sys
     from pathlib import Path

     def check_prp_names():
         errors = []
         prps_dir = Path("prps")

         for prp_file in prps_dir.glob("*.md"):
             if prp_file.stem.startswith("INITIAL_"):
                 continue  # INITIAL_ is valid workflow prefix

             if prp_file.stem.startswith("prp_"):
                 errors.append(
                     f"{prp_file}: Redundant 'prp_' prefix (already in prps/ directory)\n"
                     f"  → Rename to: prps/{prp_file.stem[4:]}.md"
                 )

         if errors:
             print("❌ PRP Naming Violations:")
             for error in errors:
                 print(f"  {error}")
             sys.exit(1)
         else:
             print("✅ All PRP names follow convention")

     if __name__ == "__main__":
         check_prp_names()
     ```
  2. Add to CI/lint workflow
  3. Document in developer guide
VALIDATION:
  - Linter catches redundant prefixes
  - Can be run locally (pre-commit hook)
  - Integrated into CI if desired
  - Clear error messages
```

---

## Validation Loop

### Level 1: Documentation Validation
```bash
# Verify convention documented
cat .claude/conventions/prp-naming.md
# Should explain all naming rules

# Verify referenced in CLAUDE.md
grep -A 3 "Naming Convention" CLAUDE.md
# Should reference convention document

# Verify developer guide exists
cat docs/developer-guide.md | grep "PRP Naming"
# Should have comprehensive section
```

### Level 2: Code Validation
```bash
# Test strip_prefix logic
python3 << 'EOF'
# Simulate Phase 0 logic
test_cases = [
    ("prps/INITIAL_user_auth.md", "INITIAL_", "user_auth"),
    ("prps/user_auth.md", None, "user_auth"),
    ("prps/execution_reliability.md", None, "should_warn"),
]
# Verify correct feature names extracted
EOF

# Test validation function
python3 << 'EOF'
from pathlib import Path
# Should raise error for redundant prefix
try:
    extract_feature_name("prps/prp_redundant.md", validate_no_redundant=True)
    print("❌ Should have raised error")
except ValueError as e:
    print(f"✅ Validation caught redundant prefix: {e}")
EOF
```

### Level 3: Audit Validation (if Task 6/7 done)
```bash
# Check no more redundant prefixes
find prps -name "prp_*.md" -type f | grep -v "INITIAL_" | grep -v "prp_base.md"
# Should return empty (or only intentional cases)

# Verify directories match names
for prp in prps/*.md; do
    name=$(basename "$prp" .md)
    if [[ ! "$name" =~ ^INITIAL_ ]] && [[ -d "prps/$name" ]]; then
        echo "✅ $name has matching directory"
    fi
done
```

### Level 4: Linter Validation (if Task 8 done)
```bash
# Run linter
python scripts/lint_prp_names.py
# Should pass with no violations

# Test linter catches violations
echo "prp_bad_name.md" > prps/prp_test.md
python scripts/lint_prp_names.py
# Should fail and show error
rm prps/prp_test.md
```

---

## Success Metrics

### Quantitative
- 100% of PRPs follow naming convention (after Task 7 if done)
- 0 false positives from linter (if Task 8 done)
- All strip_prefix calls documented with comments
- Convention documented in 3+ places (CLAUDE.md, README.md, developer guide)

### Qualitative
- Developers understand when to strip prefixes
- Clear distinction between workflow prefixes (INITIAL_) and redundant prefixes (prp_)
- New PRPs automatically follow convention
- Reduced confusion and naming bugs

---

## Dependencies

**Depends On**:
- Option A: Cleanup execution_reliability artifacts (should be done first for consistency)

**Enables**:
- Cleaner PRP organization going forward
- Easier to find and reference PRPs
- Self-documenting naming convention
- Automated validation of naming

---

## Notes

**Scope**:
- This PRP establishes the convention and updates tooling
- Task 6-7 (retroactive renames) are optional and can be skipped
- Focus on preventing future issues, not fixing all historical ones

**Alternatives Considered**:
1. Keep "prp_" prefix everywhere (consistent but redundant)
2. Use "prp-" instead of "prp_" (still redundant)
3. Move all PRPs to "features/" instead of "prps/" (larger refactor)

**Why This Approach**:
- Minimal redundancy (prps/ directory already implies PRP)
- Clear workflow stage (INITIAL_ vs final)
- Easy to understand and follow
- Matches common naming patterns in other projects

---

**Estimated Effort**: 60-90 minutes (without retroactive renames), 120+ minutes (with)
**Risk Level**: MEDIUM (changes naming logic in execute-prp.md)
**Dependencies**: Option A recommended but not required
