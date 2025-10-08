# Codex Commands - PRP Generation & Execution

**Production-ready Codex CLI commands for automated PRP (Product Requirements & Planning) workflows**

---

## Overview

This directory contains Codex CLI commands that replicate the Vibes five-phase PRP workflow with **parallel Phase 2 execution** for a **3x speedup** (5min vs 15min sequential). These commands enable complete automation from an initial requirements document (`INITIAL.md`) to validated implementation with battle-tested quality gates.

**Key Features**:
- Two production commands: `codex-generate-prp` and `codex-execute-prp`
- Parallel Phase 2 research (3 independent agents running simultaneously)
- Quality enforcement (≥8/10 PRP score, ≥70% test coverage)
- Security validation (6-level feature name validation)
- Complete automation with comprehensive error handling

---

## Quick Start

### 1. Prerequisites

**System Requirements**:
- Bash 4.0+ (for associative arrays)
- macOS, Linux, or WSL2
- Codex CLI installed and configured
- Git repository

**macOS Users** (Bash 3.x → 4.x upgrade):
```bash
# Install Bash 4.x via Homebrew
brew install bash

# Use new Bash for scripts
/opt/homebrew/bin/bash .codex/scripts/codex-generate-prp.sh <args>
```

**Dependencies** (auto-checked by scripts):
- `codex` CLI in PATH
- `timeout` command (GNU coreutils)
- Python 3.8+ with `ruff`, `mypy`, `pytest` (for execution)

### 2. Installation

No installation needed - commands are ready to use:

```bash
# Verify scripts exist
ls -la .codex/scripts/codex-*.sh
ls -la .codex/commands/codex-*.md

# Test a script (help message)
./.codex/scripts/codex-generate-prp.sh
```

### 3. Profile Configuration

Create `.codex/profiles/codex-prp.yaml`:

```yaml
# Codex profile for PRP generation and execution
# This profile is optimized for research and implementation tasks

name: codex-prp
model: o4-mini  # Cost-effective for research phases
# Alternative: gpt-5-codex (for execution)

# Approval policy (CRITICAL for parallel execution)
approval_policy: on-failure  # Phase 2 is read-only (safe to auto-approve)

# MCP servers (if Archon available)
mcp_servers:
  - archon  # Task tracking and knowledge base

# Timeouts
timeout: 600  # 10 minutes default

# Output settings
verbose: true
stream: true
```

**Profile Notes**:
- **`approval_policy: on-failure`** is CRITICAL for Phase 2 parallel execution
  - Phase 2 agents only read files (Archon search, file reads)
  - `on-request` would hang workflow waiting for approval in background
- Use `o4-mini` for PRP generation (cost-effective research)
- Use `gpt-5-codex` for PRP execution (better implementation)

---

## Commands

### Command 1: Generate PRP (`codex-generate-prp`)

**Purpose**: Generate a comprehensive PRP from an INITIAL.md file using 5-phase workflow with parallel Phase 2.

**Location**:
- **Command prompt**: `.codex/commands/codex-generate-prp.md`
- **Orchestration script**: `.codex/scripts/codex-generate-prp.sh`

**Usage**:
```bash
# Generate PRP from INITIAL.md
./.codex/scripts/codex-generate-prp.sh prps/INITIAL_user_auth.md

# With custom profile
CODEX_PROFILE=gpt-5-codex ./.codex/scripts/codex-generate-prp.sh prps/INITIAL_feature.md
```

**Workflow**:
1. **Phase 0**: Setup (create directories, initialize manifest)
2. **Phase 1**: Feature Analysis (sequential)
3. **Phase 2**: Parallel Research (3 agents simultaneously) **← 3x SPEEDUP**
   - Phase 2A: Codebase Research
   - Phase 2B: Documentation Hunt
   - Phase 2C: Example Curation
4. **Phase 3**: Gotcha Detection (sequential)
5. **Phase 4**: PRP Assembly (sequential)

**Output**:
```
prps/
├── user_auth.md              # Final PRP (comprehensive)
└── user_auth/
    └── codex/
        ├── planning/         # Phase 2 research outputs
        │   ├── codebase-patterns.md
        │   ├── documentation-links.md
        │   └── examples-to-include.md
        └── logs/
            ├── manifest.jsonl  # JSONL audit trail
            └── phase*.log      # Individual phase logs
```

**Quality Gate**:
- PRP score ≥8/10 or regeneration offered (max 3 attempts)
- Interactive retry/skip/abort on phase failure

**Performance**:
- Target: <15min for typical feature
- Parallel speedup: ≥2x (Phase 2 runs in ~5min vs ~15min sequential)

---

### Command 2: Execute PRP (`codex-execute-prp`)

**Purpose**: Execute a PRP with validation loop (ruff → mypy → pytest → coverage).

**Location**:
- **Command prompt**: `.codex/commands/codex-execute-prp.md`
- **Orchestration script**: `.codex/scripts/codex-execute-prp.sh`

**Usage**:
```bash
# Execute PRP with full validation
./.codex/scripts/codex-execute-prp.sh prps/user_auth.md

# Execute INITIAL PRP (auto-strips prefix)
./.codex/scripts/codex-execute-prp.sh prps/INITIAL_user_auth.md

# Custom validation settings
MAX_VALIDATION_ATTEMPTS=3 MIN_COVERAGE=80 ./.codex/scripts/codex-execute-prp.sh prps/feature.md

# Skip validation (testing only)
SKIP_VALIDATION=true ./.codex/scripts/codex-execute-prp.sh prps/feature.md
```

**Validation Loop** (max 5 attempts):
1. **Level 1**: Syntax & Style
   - `ruff check --fix` (Python linter with auto-fix)
   - `mypy` (type checking)
2. **Level 2**: Unit Tests
   - `pytest tests/` (all tests must pass)
3. **Level 3**: Coverage
   - `pytest --cov` (≥70% coverage required)

**On Validation Failure**:
- Extract error messages from logs
- Search PRP "Known Gotchas" section for solutions
- Offer manual intervention (pause for user fixes)
- Auto-retry after fixes

**After Max Attempts**:
- Generate completion report (files changed, coverage %, blockers)
- Offer choices:
  1. Continue anyway (accept partial implementation)
  2. Manual intervention (pause for user fixes)
  3. Abort workflow

**Output**:
```
prps/
└── user_auth/
    └── codex/
        └── logs/
            ├── manifest.jsonl           # JSONL audit trail
            ├── execution_report.md      # Completion report
            └── validation_level*.log    # Validation logs
```

---

## Usage Examples

### Example 1: End-to-End Workflow (INITIAL.md → Validated Code)

```bash
# Step 1: Create INITIAL.md with requirements
cat > prps/INITIAL_user_auth.md <<'EOF'
# INITIAL: User Authentication

Build user authentication system with:
- JWT token-based auth
- Password hashing (bcrypt)
- Login/logout endpoints
- User registration
- Email validation
EOF

# Step 2: Generate PRP (parallel Phase 2)
./.codex/scripts/codex-generate-prp.sh prps/INITIAL_user_auth.md
# Output: prps/user_auth.md (comprehensive PRP with ≥8/10 quality)

# Step 3: Execute PRP (with validation loop)
./.codex/scripts/codex-execute-prp.sh prps/user_auth.md
# Output: Validated implementation with ≥70% test coverage

# Step 4: Review completion report
cat prps/user_auth/codex/logs/execution_report.md

# Step 5: Commit changes
git add .
git commit -m "Implement user authentication"
```

**Total Time**: <30 minutes (PRP generation ~10min + execution ~15min)

---

### Example 2: PRP Generation Only (Research Phase)

```bash
# Generate PRP without execution
./.codex/scripts/codex-generate-prp.sh prps/INITIAL_api_client.md

# Review generated PRP
cat prps/api_client.md

# Review research outputs
ls prps/api_client/codex/planning/
# codebase-patterns.md
# documentation-links.md
# examples-to-include.md

# Check quality score
grep "Score:" prps/api_client.md
# Score: 9/10 (high confidence)

# Execute later
./.codex/scripts/codex-execute-prp.sh prps/api_client.md
```

---

### Example 3: PRP Execution with Custom Settings

```bash
# Custom validation thresholds
MAX_VALIDATION_ATTEMPTS=3 \
MIN_COVERAGE=80 \
./.codex/scripts/codex-execute-prp.sh prps/feature.md

# Custom timeout values
PHASE1_TIMEOUT=900 \
PHASE2_TIMEOUT=1200 \
./.codex/scripts/codex-generate-prp.sh prps/INITIAL_complex_feature.md
```

---

### Example 4: Debugging Failed PRP Generation

```bash
# Run PRP generation
./.codex/scripts/codex-generate-prp.sh prps/INITIAL_feature.md
# ❌ Phase 2a failed (exit 124 = timeout)

# Check individual phase logs
cat prps/feature/codex/logs/phase2a.log
# [timeout details]

# Check manifest for timing
cat prps/feature/codex/logs/manifest.jsonl
# {"phase":"phase2a","status":"failed","exit_code":124,"duration":600}

# Retry with increased timeout
PHASE2_TIMEOUT=1200 ./.codex/scripts/codex-generate-prp.sh prps/INITIAL_feature.md
```

---

## Comparison with Claude Commands

| Feature | Codex Commands | Claude Commands |
|---------|---------------|-----------------|
| **PRP Generation** | `codex-generate-prp.sh` | `/generate-prp` |
| **Parallelization** | Bash job control (`&` + `wait`) | `Task()` subagents |
| **Phase 2 Speedup** | 3x (5min vs 15min) | 3x (same) |
| **Quality Gate** | ≥8/10 PRP score | ≥8/10 PRP score |
| **Validation Loop** | `codex-execute-prp.sh` | `/execute-prp` |
| **Coverage Requirement** | ≥70% | ≥70% |
| **Archon Integration** | Optional (graceful degradation) | Optional |
| **Profile** | `codex-prp.yaml` | Claude uses Tasks |
| **Manifest Logging** | JSONL (same format) | JSONL (same format) |
| **Model Choice** | o4-mini / gpt-5-codex | claude-opus / sonnet |
| **Cost** | Lower (o4-mini for research) | Higher (opus for all) |

**When to use Codex**:
- Cost optimization (o4-mini is cheaper)
- Prefer OpenAI models
- Need CLI automation (CI/CD)

**When to use Claude**:
- Interactive development
- Prefer Claude models
- Need Task() parallelization (built-in)

**Cross-Validation**: Same `INITIAL.md` through both → compare outputs

---

## Troubleshooting

### Common Errors

#### Error 1: "Bash 4.0 or higher is required"

**Cause**: macOS ships with Bash 3.x (associative arrays require 4.0+)

**Solution**:
```bash
# Install Bash 4.x
brew install bash

# Run with new Bash
/opt/homebrew/bin/bash .codex/scripts/codex-generate-prp.sh <args>

# Or set as default (optional)
echo "/opt/homebrew/bin/bash" | sudo tee -a /etc/shells
chsh -s /opt/homebrew/bin/bash
```

---

#### Error 2: "timeout not installed"

**Cause**: GNU `timeout` command missing

**Symptoms**: Exit code 125 (timeout command failed)

**Solution**:
```bash
# macOS
brew install coreutils
# Creates 'gtimeout' (GNU timeout)

# Update scripts to use gtimeout on macOS
# (scripts auto-detect and use gtimeout if available)

# Linux (Ubuntu/Debian)
sudo apt-get install coreutils

# Already installed on most Linux distros
```

---

#### Error 3: "Path traversal detected"

**Cause**: Invalid feature name (security validation)

**Examples**:
```bash
# ❌ WRONG
./.codex/scripts/codex-generate-prp.sh ../../../etc/passwd
# Error: Path traversal detected

# ❌ WRONG
./.codex/scripts/codex-generate-prp.sh prps/prp_feature.md
# Error: Redundant 'prp_' prefix

# ❌ WRONG
./.codex/scripts/codex-generate-prp.sh "test;rm -rf /"
# Error: Dangerous character ';'

# ✅ RIGHT
./.codex/scripts/codex-generate-prp.sh prps/INITIAL_user_auth.md
```

**Solution**: Use valid feature names (alphanumeric + underscore + hyphen only)

---

#### Error 4: "Quality gate failed (score 6/10)"

**Cause**: PRP quality below threshold (≥8/10 required)

**Solution**:
```bash
# Option 1: Regenerate (offered interactively)
Choose (1/2/3): 1  # Regenerate

# Option 2: Accept anyway (with warning)
Choose (1/2/3): 2  # Accept

# Option 3: Improve INITIAL.md and retry
# Add more details to INITIAL.md
# Re-run generation
./.codex/scripts/codex-generate-prp.sh prps/INITIAL_feature.md
```

---

#### Error 5: "Phase 2 failed (exit 124 = timeout)"

**Cause**: Phase 2 agent exceeded 10-minute timeout

**Solutions**:
```bash
# Solution 1: Increase timeout (offered interactively)
# Choose option 2: "Retry with increased timeout (+50%)"

# Solution 2: Manual timeout override
PHASE2_TIMEOUT=1200 ./.codex/scripts/codex-generate-prp.sh prps/INITIAL_feature.md

# Solution 3: Check if Codex server is slow
# Test Codex CLI directly
codex exec --profile codex-prp --prompt "Hello"
```

---

#### Error 6: "Validation failed: coverage 45% < 70%"

**Cause**: Test coverage below minimum threshold

**Solution**:
```bash
# Option 1: Lower threshold (if acceptable)
MIN_COVERAGE=45 ./.codex/scripts/codex-execute-prp.sh prps/feature.md

# Option 2: Add more tests (recommended)
# Validation loop will pause for manual intervention
# Add tests to increase coverage
# Press Enter to retry

# Option 3: Check coverage report
cat prps/feature/codex/logs/validation_level3.log
# TOTAL coverage: 45%
# Missing coverage in: src/module.py (20%)
```

---

#### Error 7: "Archon CLI not found"

**Cause**: Archon MCP server not installed (optional dependency)

**Impact**: PRP generation proceeds without task tracking

**Solution** (optional):
```bash
# Install Archon (if desired)
# Follow Archon installation instructions

# Or proceed without Archon
# ℹ️  Archon CLI not found - proceeding without project tracking
# [workflow continues normally]
```

---

#### Error 8: "Codex profile 'codex-prp' not found"

**Cause**: Missing profile configuration

**Solution**:
```bash
# Create profile
mkdir -p .codex/profiles
cat > .codex/profiles/codex-prp.yaml <<'EOF'
name: codex-prp
model: o4-mini
approval_policy: on-failure
timeout: 600
EOF

# Verify profile
codex profiles list
# codex-prp ✓

# Retry
./.codex/scripts/codex-generate-prp.sh prps/INITIAL_feature.md
```

---

### Gotchas Reference

All 13 gotchas from the PRP are handled by the scripts:

| # | Gotcha | Script Handling |
|---|--------|-----------------|
| 1 | Exit code loss (timing race) | Immediate capture: `wait $PID; EXIT=$?` |
| 2 | Security bypass (path traversal) | 6-level validation in `security-validation.sh` |
| 3 | Zombie processes (no timeout) | All `codex exec` wrapped with `timeout` |
| 4 | Profile omission | Explicit `--profile codex-prp` in all calls |
| 5 | Output interleaving | Separate log files per agent |
| 6 | Sequential execution | Phase 2 uses `&` + `wait` for parallelism |
| 7 | PID race condition | Immediate `$!` capture after `&` |
| 8 | Timeout exit code confusion | Case statement for 124/125/137 |
| 9 | JSONL corruption | Separate manifests, merged after Phase 2 |
| 10 | Approval policy blocking | `on-failure` in profile (Phase 2 read-only) |
| 11 | Dependency validation omission | `check_dependencies()` before each phase |
| 12 | Redundant prp_ prefix | Validation rejects `prp_*` names |
| 13 | removeprefix() vs replace() | `${var#prefix}` (NOT `${var//pattern/}`) |

**All gotchas are automatically handled** - no manual intervention required.

---

## Performance Metrics

**PRP Generation** (typical feature):
- **Sequential baseline**: ~20 minutes
  - Phase 1: 5 min
  - Phase 2A: 5 min
  - Phase 2B: 4 min
  - Phase 2C: 5 min
  - Phase 3: 4 min
  - Phase 4: 2 min
- **Parallel actual**: ~10 minutes (Phase 2 runs concurrently)
- **Speedup**: 2x (100% faster)

**PRP Execution** (typical feature):
- **Validation loop**: 1-3 attempts (usually)
- **Duration**: 10-20 minutes (depends on implementation size)
- **Success rate**: >90% (with quality PRP ≥8/10)

**End-to-End** (INITIAL.md → Validated Code):
- **Total time**: <30 minutes (vs ~40 minutes sequential)
- **Quality**: ≥8/10 PRP, ≥70% test coverage

---

## Advanced Usage

### Custom Phase Prompts

Create custom prompts in `.codex/prompts/`:

```bash
# Create custom Phase 1 prompt
cat > .codex/prompts/phase1.md <<'EOF'
# Phase 1: Feature Analysis

[Your custom analysis instructions]
EOF

# Run with custom prompt
./.codex/scripts/codex-generate-prp.sh prps/INITIAL_feature.md
```

---

### CI/CD Integration

```yaml
# GitHub Actions example
name: PRP Workflow
on: [push]

jobs:
  generate-prp:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3

      - name: Install Codex CLI
        run: |
          # [Install Codex CLI]

      - name: Generate PRP
        run: |
          ./.codex/scripts/codex-generate-prp.sh prps/INITIAL_feature.md

      - name: Check Quality
        run: |
          score=$(grep "Score:" prps/feature.md | sed 's/.*Score: \([0-9]\+\).*/\1/')
          if [ "$score" -lt 8 ]; then
            echo "Quality gate failed: $score/10 < 8/10"
            exit 1
          fi

      - name: Execute PRP
        run: |
          ./.codex/scripts/codex-execute-prp.sh prps/feature.md

      - name: Upload Artifacts
        uses: actions/upload-artifact@v3
        with:
          name: prp-outputs
          path: prps/feature/
```

---

## Files Reference

```
.codex/
├── README.md                          # This file (user-facing docs)
├── commands/
│   ├── codex-generate-prp.md         # PRP generation command prompt
│   └── codex-execute-prp.md          # PRP execution command prompt
└── profiles/
    └── codex-prp.yaml                # Codex profile configuration

.codex/scripts/
├── README.md                          # Technical/internal docs
├── codex-generate-prp.sh             # Main PRP generation orchestrator
├── codex-execute-prp.sh              # Main PRP execution orchestrator
├── parallel-exec.sh                   # Phase 2 parallel execution helper
├── security-validation.sh             # 6-level security validation
├── quality-gate.sh                    # PRP quality enforcement (≥8/10)
└── log-phase.sh                       # JSONL manifest logging

prps/
├── INITIAL_feature.md                # Input: requirements
├── feature.md                        # Output: comprehensive PRP
└── feature/
    └── codex/
        ├── planning/                 # Phase 2 research outputs
        │   ├── codebase-patterns.md
        │   ├── documentation-links.md
        │   └── examples-to-include.md
        └── logs/
            ├── manifest.jsonl        # JSONL audit trail
            ├── execution_report.md   # Completion report (execution)
            └── phase*.log            # Individual phase logs
```

---

## Support

**Questions?** Check:
1. This README (user-facing docs)
2. `.codex/scripts/README.md` (technical/internal docs)
3. PRP: `prps/codex_commands.md` (complete specification)
4. Examples: `prps/codex_commands/examples/README.md`

**Issues?** See [Troubleshooting](#troubleshooting) section above.

**Contributing?** Follow existing patterns and update both READMEs.

---

## License

Part of Vibes project. See main repository LICENSE.

---

**Last Updated**: 2025-10-07
**Version**: 1.0.0 (Production Ready)
