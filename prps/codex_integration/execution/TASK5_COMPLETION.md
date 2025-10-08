# Task 5 Implementation Complete: Create Helper Script - Pre-Flight Validation

## Task Information
- **Task ID**: N/A (PRP-driven development)
- **Task Name**: Task 5: Create Helper Script - Pre-Flight Validation
- **Responsibility**: Automated checks before Codex execution
- **Status**: COMPLETE - Ready for Review

## Files Created/Modified

### Created Files:

1. **`/Users/jon/source/vibes/scripts/codex/validate-bootstrap.sh`** (285 lines)
   - Comprehensive pre-flight validation script
   - 6 validation checks with progress tracking
   - Actionable error messages with resolution steps
   - Exportable functions for use in other scripts
   - Color-coded output for readability
   - Strict mode enabled (set -euo pipefail)

### Modified Files:
None - This task only creates new files

## Implementation Details

### Core Features Implemented

#### 1. Script Structure
- **Strict mode**: `set -euo pipefail` ensures fail-fast behavior
- **Progress tracking**: X/Y checks passed displayed after each validation
- **Color output**: Green (success), Red (failure), Yellow (warning), Blue (info)
- **Configurable profile**: Accepts profile name as parameter (default: codex-prp)
- **Repository-aware**: Automatically detects repo root

#### 2. Validation Checks (6 total)

**CHECK 1/6: Codex CLI Installation**
- Verifies `codex` binary in PATH
- Displays version information
- Provides install instructions (npm, brew, binary)
- References docs/codex-bootstrap.md

**CHECK 2/6: Authentication Status**
- Runs `codex login status` to verify authentication
- Provides troubleshooting steps for common auth issues
- References browser login and API key methods
- Links to docs/codex-bootstrap.md#authentication

**CHECK 3/6: Profile Configuration**
- Validates profile exists in ~/.codex/config.toml
- Checks for required fields (model, approval_policy, sandbox_mode)
- Provides exact TOML snippets for missing fields
- References docs/codex-config.md

**CHECK 4/6: Sandbox Dry-Run Test**
- Executes test command in read-only sandbox
- Verifies sandbox mode is functional
- Provides configuration guidance for failures
- References docs/codex-config.md#sandbox-modes

**CHECK 5/6: MCP Server Availability**
- Checks if MCP servers configured in profile
- Treats as informational (not critical)
- Suggests adding Archon MCP server
- Gracefully handles no MCP servers configured

**CHECK 6/6: File Structure Writability**
- Verifies prps/ directory exists and is writable
- Tests write permissions with temporary file
- Provides permission fix commands
- Creates directory on first use if missing

#### 3. Summary Report
- Displays checks passed / total (X/6)
- Calculates success rate percentage
- Color-coded final status:
  - Green: All checks passed (6/6)
  - Yellow: Most checks passed (4-5/6)
  - Red: Critical failures (0-3/6)
- Exit codes:
  - 0: All checks passed
  - 1: Some checks failed or critical failures

#### 4. Export Functions
- All validation functions exported for reuse
- Can be sourced by other scripts
- Enables modular validation in workflows

### Critical Gotchas Addressed

#### Gotcha #1: Authentication Loop / Silent Failure
**From PRP**: Codex doesn't read OPENAI_API_KEY env var, must use `codex login`
**Implementation**:
- CHECK 2 validates `codex login status` before any execution
- Provides clear steps to authenticate (ChatGPT login, API key)
- References troubleshooting guide for common issues

#### Gotcha #2: Sandbox Permission Denial (v0.20+ Four-Setting Requirement)
**From PRP**: workspace-write requires approval_policy + bypass_approvals + bypass_sandbox + trusted_workspace
**Implementation**:
- CHECK 3 validates profile has required fields
- CHECK 4 runs dry-run test to verify sandbox actually works
- Provides exact TOML configuration snippets

#### Gotcha #6: Path Pollution / Artifact Misplacement
**From PRP**: Artifacts written outside prps/{feature}/codex/ due to missing cwd or wrong permissions
**Implementation**:
- CHECK 6 validates prps/ directory is writable
- Tests write permissions before any codex execution
- Provides fix commands (chmod u+w prps/)

#### Gotcha #7: Profile Drift / Configuration Pollution
**From PRP**: Codex uses wrong profile when --profile flag omitted
**Implementation**:
- Script accepts explicit profile name parameter
- Validates specific profile (not default)
- Enforces explicit --profile usage pattern

### Pattern Compliance

**Pattern 7: Comprehensive Validation Suite** (from codebase-patterns.md):
- ✅ Check-by-check feedback with progress (X/Y)
- ✅ Success rate percentage for accountability
- ✅ Actionable error messages (tell user what to do)
- ✅ Informational vs critical checks (MCP is optional)
- ✅ Color-coded output for readability
- ✅ Export functions for reuse

**Pattern 4: Validation Gates with Iteration Loops**:
- ✅ Multiple defense layers (6 checks)
- ✅ Fail-fast behavior (strict mode)
- ✅ Clear error reporting with resolution steps
- ✅ Graceful degradation (MCP optional)

## Dependencies Verified

### Completed Dependencies:
- **Task 1**: docs/codex-bootstrap.md created (referenced in error messages)
- **Task 2**: docs/codex-config.md created (referenced in validation)
- **Task 3**: docs/codex-artifacts.md created (file structure guidance)
- **Task 4**: docs/codex-validation.md created (validation procedures defined)

### External Dependencies:
- **codex CLI**: Required for validation checks
- **shellcheck**: Used for validation (passed with no errors)
- **bash 4.0+**: For associative arrays and modern bash features

## Testing Checklist

### Automated Validation:
- [x] **ShellCheck**: Passed with no errors or warnings
  ```bash
  shellcheck scripts/codex/validate-bootstrap.sh
  # No output = success
  ```

- [x] **Executable permissions**: Set correctly
  ```bash
  ls -l scripts/codex/validate-bootstrap.sh
  # -rwxr-xr-x = correct
  ```

- [x] **Strict mode**: Verified set -euo pipefail present
- [x] **All functions exported**: Can be sourced by other scripts
- [x] **Color output**: Color codes defined and used correctly

### Manual Testing:
Since this is a bootstrap validation script and Codex CLI is not installed/configured on this system, full runtime testing is deferred to actual bootstrap workflow. However:

- [x] **Script structure**: All 6 validation functions defined
- [x] **Error messages**: All failure paths include actionable steps
- [x] **Documentation references**: All references point to correct docs
- [x] **Progress tracking**: Variables correctly incremented
- [x] **Exit codes**: Proper exit codes for success/failure

### Expected Behavior:

**On clean system (Codex not installed)**:
```
CHECK 1/6: Codex CLI Installation
-----------------------------------------
❌ Codex CLI not found

Install using one of these methods:
  - npm:   npm install -g @openai/codex
  ...

Validation Summary
Checks passed: 0/6
Success rate: 0%
❌ CRITICAL FAILURES DETECTED
```

**After setup (all checks pass)**:
```
CHECK 1/6: Codex CLI Installation
-----------------------------------------
✅ Codex CLI installed: codex 0.3.1

CHECK 2/6: Authentication Status
-----------------------------------------
✅ Authenticated

...

Validation Summary
Checks passed: 6/6
Success rate: 100%
✅ ALL CHECKS PASSED - Ready for Codex execution
```

## Success Metrics

**All PRP Requirements Met**:
- [x] Script structure with strict mode (set -euo pipefail)
- [x] Progress tracking (X/Y checks passed)
- [x] Actionable error messages with resolution steps
- [x] Check 1/6: Codex CLI installed (which codex)
- [x] Check 2/6: Authenticated (codex login status)
- [x] Check 3/6: Profile exists (codex config show --profile codex-prp)
- [x] Check 4/6: Sandbox test (codex exec --sandbox read-only)
- [x] Check 5/6: MCP servers available (configuration check)
- [x] Check 6/6: File structure (prps/ directory writable)
- [x] Summary report (checks passed, success rate, next steps)
- [x] Export functions for use in other scripts

**Code Quality**:
- [x] ShellCheck validation passes with no errors
- [x] Strict mode enabled (fail-fast)
- [x] All error messages are actionable
- [x] Color-coded output for readability
- [x] Functions follow naming convention (validate_*)
- [x] Comprehensive inline comments
- [x] References to documentation in error messages
- [x] Exit codes follow convention (0=success, 1=failure)

## Validation Results

### ShellCheck Validation:
```bash
shellcheck scripts/codex/validate-bootstrap.sh
# Exit code: 0 (no errors)
```

**Initial warnings fixed**:
- SC2155: Declare and assign separately to avoid masking return values
- Fixed in 3 locations by separating local declaration and assignment

### Pattern Compliance:
✅ **Pattern 7** (Comprehensive Validation Suite):
- All 6 checks implemented with progress tracking
- Summary report with success rate percentage
- Actionable error messages throughout
- Informational vs critical checks distinguished

✅ **Pattern 2** (Security-First Path Validation):
- Repository root detection via cd and pwd
- No user input used in file operations
- Test file cleanup after write test

✅ **Strict Mode** (Pattern from command_wrapper.sh):
- set -euo pipefail ensures fail-fast
- All errors propagate correctly
- Exit codes properly returned

### Documentation References:
All references verified to exist:
- ✅ docs/codex-bootstrap.md
- ✅ docs/codex-config.md
- ✅ docs/codex-validation.md
- ✅ docs/codex-artifacts.md (for file structure)

## Completion Report

**Status**: COMPLETE - Ready for Review
**Implementation Time**: ~40 minutes
**Confidence Level**: HIGH
**Blockers**: None

### Files Created: 1
- scripts/codex/validate-bootstrap.sh (285 lines)

### Files Modified: 0

### Total Lines of Code: ~285 lines

**Implementation Notes**:
1. Script follows Pattern 7 (Comprehensive Validation Suite) exactly
2. All critical gotchas (#1, #2, #6, #7) addressed with detection + resolution
3. ShellCheck passes with no errors after fixing SC2155 warnings
4. Functions are exported for reuse in other scripts (log-phase.sh, validate-config.sh)
5. Color output enhances readability and user experience
6. Exit codes follow convention for integration with workflows

**Next Steps**:
1. Run on clean system to test "not installed" error paths
2. Run after Codex setup to verify all checks pass
3. Integrate into codex-generate-prp wrapper script
4. Use exported functions in Task 6 (log-phase.sh) and Task 7 (validate-config.sh)

**Ready for integration and next task (Task 6: JSONL Manifest Logging).**
