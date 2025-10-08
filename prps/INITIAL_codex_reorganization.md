# INITIAL: Codex Directory Reorganization

## Goal

Reorganize Codex-related files from scattered root directories into a unified `.codex/` structure for better project organization and cleaner root directory.

## Current Pain Point

**Problem**: Codex files are currently scattered across root directories:
- `scripts/codex/` - Bash orchestration scripts (5 files, 2,713 lines)
- `tests/codex/` - Integration test suites (3 files, 1,505 lines)
- `.codex/commands/` - Command prompts (2 files, 62KB)
- `.codex/README.md` - User documentation

**Impact**:
- Root `scripts/` and `tests/` directories polluted with Codex-specific code
- Inconsistent organization (some in `.codex/`, some in root)
- Harder to find and maintain Codex-related files
- Violates single-responsibility principle (mixed concerns in root dirs)

## Desired End State

**Unified `.codex/` structure**:
```
.codex/
├── commands/              # Command prompts (EXISTING)
│   ├── codex-execute-prp.md
│   └── codex-generate-prp.md
├── scripts/               # Bash orchestration (MOVE FROM scripts/codex/)
│   ├── security-validation.sh
│   ├── parallel-exec.sh
│   ├── codex-generate-prp.sh
│   ├── codex-execute-prp.sh
│   ├── quality-gate.sh
│   ├── log-phase.sh
│   └── README.md
├── tests/                 # Integration tests (MOVE FROM tests/codex/)
│   ├── test_generate_prp.sh
│   ├── test_parallel_timing.sh
│   ├── test_execute_prp.sh
│   └── fixtures/
│       └── INITIAL_test_codex_prp_generation.md
└── README.md              # User documentation (EXISTING)
```

**Benefits**:
- ✅ All Codex files in one logical location
- ✅ Cleaner root `scripts/` and `tests/` directories (only Vibes-specific code)
- ✅ Easier to find, maintain, and understand Codex workflow
- ✅ Consistent with `.claude/` organization pattern
- ✅ Self-contained Codex system (can be extracted/shared easily)

## What Needs to Change

### File Moves (10 files)

**From `scripts/codex/` to `.codex/scripts/`**:
1. `scripts/codex/security-validation.sh` → `.codex/scripts/security-validation.sh`
2. `scripts/codex/parallel-exec.sh` → `.codex/scripts/parallel-exec.sh`
3. `scripts/codex/codex-generate-prp.sh` → `.codex/scripts/codex-generate-prp.sh`
4. `scripts/codex/codex-execute-prp.sh` → `.codex/scripts/codex-execute-prp.sh`
5. `scripts/codex/quality-gate.sh` → `.codex/scripts/quality-gate.sh`
6. `scripts/codex/log-phase.sh` → `.codex/scripts/log-phase.sh`
7. `scripts/codex/README.md` → `.codex/scripts/README.md`

**From `tests/codex/` to `.codex/tests/`**:
8. `tests/codex/test_generate_prp.sh` → `.codex/tests/test_generate_prp.sh`
9. `tests/codex/test_parallel_timing.sh` → `.codex/tests/test_parallel_timing.sh`
10. `tests/codex/test_execute_prp.sh` → `.codex/tests/test_execute_prp.sh`
11. `tests/codex/fixtures/` → `.codex/tests/fixtures/` (entire directory)

### Path Updates (Critical)

**Scripts that source other scripts** (update relative paths):
- `.codex/scripts/parallel-exec.sh` - sources `security-validation.sh` and `log-phase.sh`
- `.codex/scripts/codex-generate-prp.sh` - sources `security-validation.sh`, `parallel-exec.sh`, `log-phase.sh`
- `.codex/scripts/codex-execute-prp.sh` - sources `security-validation.sh`, `log-phase.sh`
- `.codex/scripts/quality-gate.sh` - sources `security-validation.sh`

**Change**: `$(dirname "$0")/script.sh` → Same pattern works (all in same dir)

**Tests that reference scripts** (update paths):
- `.codex/tests/test_generate_prp.sh` - references `../../.codex/scripts/codex-generate-prp.sh`
- `.codex/tests/test_parallel_timing.sh` - references `../../.codex/scripts/parallel-exec.sh`
- `.codex/tests/test_execute_prp.sh` - references `../../.codex/scripts/codex-execute-prp.sh`

**Change**: `../../scripts/codex/` → `../.codex/scripts/` (or use absolute paths from repo root)

### Documentation Updates

**`.codex/README.md`** - Update all paths in examples:
- `scripts/codex/codex-generate-prp.sh` → `.codex/scripts/codex-generate-prp.sh`
- `tests/codex/test_*.sh` → `.codex/tests/test_*.sh`

**`.codex/scripts/README.md`** - Update all internal references:
- Dependency graph paths
- Usage examples
- File references

### Git Operations

**Use `git mv` to preserve history**:
```bash
git mv scripts/codex .codex/scripts
git mv tests/codex .codex/tests
```

**Clean up empty directories**:
```bash
# After git mv, remove if empty:
rmdir scripts/codex 2>/dev/null || true
rmdir tests/codex 2>/dev/null || true
```

## Success Criteria

**Organization**:
- [ ] All Codex scripts in `.codex/scripts/` (7 files)
- [ ] All Codex tests in `.codex/tests/` (3 files + fixtures)
- [ ] Root `scripts/codex/` and `tests/codex/` directories removed
- [ ] `.codex/` directory is self-contained and complete

**Functionality**:
- [ ] All script sourcing works (relative paths correct)
- [ ] All tests run successfully with new paths
- [ ] All documentation examples updated and accurate
- [ ] Git history preserved for all moved files

**Validation**:
- [ ] `bash -n .codex/scripts/*.sh` - All scripts have valid syntax
- [ ] `.codex/tests/test_*.sh` - All tests pass
- [ ] Examples in `.codex/README.md` work correctly
- [ ] No broken references to old paths

## Constraints

**MUST preserve**:
- ✅ Git history (use `git mv`, not `rm` + `add`)
- ✅ File permissions (executable bits on .sh files)
- ✅ Functionality (all scripts and tests work after move)

**MUST update**:
- ✅ All relative paths in scripts (sourcing)
- ✅ All references in tests (script paths)
- ✅ All documentation examples
- ✅ Any hardcoded paths in code

**MUST NOT break**:
- ✅ Existing PRP execution workflows
- ✅ Integration with other Vibes components
- ✅ Test suite execution

## Risk Assessment

**Low Risk**:
- Simple file moves with `git mv`
- All files self-contained (no external dependencies beyond repo)
- Comprehensive test suite to validate

**Medium Risk**:
- Path references in scripts (mitigated by systematic find/replace)
- Documentation accuracy (mitigated by verification of all examples)

**Mitigation**:
- Use PRP to generate comprehensive migration plan
- Validate all scripts with `bash -n` before and after
- Run full test suite before and after
- Update documentation last (after validating code changes)

## Notes

**Pattern to follow**: Similar to `.claude/` organization
- `.claude/commands/` - Command prompts
- `.claude/patterns/` - Reusable patterns
- **NEW**: `.codex/scripts/` - Bash scripts (parallel to Claude's subagents)
- **NEW**: `.codex/tests/` - Test suites (validation for Codex workflow)

**Why this is better**:
- Logical grouping (all Codex in `.codex/`)
- Mirrors `.claude/` structure (consistency)
- Cleaner root directories (separation of concerns)
- Easier to share/extract Codex system independently
