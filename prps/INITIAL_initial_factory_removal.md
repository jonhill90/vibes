## FEATURE:

Remove the INITIAL.md Factory workflow and all associated components from the vibes repository. This factory added unnecessary complexity by automating the manual creation of INITIAL.md files - a task that requires human thinking and only takes 10-20 minutes.

**What to Remove:**
1. All 6 INITIAL factory subagent definitions in `.claude/agents/`:
   - `prp-initial-feature-clarifier.md`
   - `prp-initial-codebase-researcher.md`
   - `prp-initial-documentation-hunter.md`
   - `prp-initial-example-curator.md`
   - `prp-initial-gotcha-detective.md`
   - `prp-initial-assembler.md`

2. The `/create-initial` slash command in `.claude/commands/create-initial.md`

3. INITIAL.md Factory documentation from `CLAUDE.md`:
   - Remove entire "INITIAL.md Factory Workflow" section (~200-300 lines)
   - Keep only the clean workflow: Manual INITIAL.md → /generate-prp → /execute-prp

**What to Keep:**
- All PRP generation agents (`prp-gen-*`) - these provide valuable parallel research
- All PRP execution agents (`prp-exec-*`) - these provide valuable parallel implementation
- `/generate-prp` and `/execute-prp` commands
- The simple INITIAL.md template
- INITIAL_EXAMPLE.md

**Expected Outcome:**
- Cleaner workflow: Human writes INITIAL.md → automated generate-prp → automated execute-prp
- Reduced agent count: 12+ agents → 6 agents (50% reduction)
- Simpler CLAUDE.md: Remove ~200-300 lines of INITIAL factory documentation
- Clearer focus: Automation targets mechanical work (research/implementation), not creative thinking

## EXAMPLES:

No specific code examples needed - this is a deletion/cleanup task.

## DOCUMENTATION:

Reference the original context-engineering-intro workflow:
- Location: `repos/context-engineering-intro/`
- Original flow: Manual INITIAL.md → /generate-prp → /execute-prp
- This is what we're returning to (with enhanced parallel subagents kept)

## OTHER CONSIDERATIONS:

**Duplicate Detection:**
- Some agents may have both `prp-gen-*` and `prp-initial-*` versions
- Check for duplicates before deleting (e.g., `prp-gen-documentation-hunter.md` vs `prp-initial-documentation-hunter.md`)
- If duplicates exist, keep the `prp-gen-*` version, delete the `prp-initial-*` version

**CLAUDE.md Cleanup:**
- The INITIAL.md Factory section is large (~200-300 lines starting with "## INITIAL.md Factory Workflow")
- Remove the entire section including:
  - Overview
  - When to Use This Workflow
  - Immediate Recognition Actions
  - The 5-Phase Workflow
  - Subagent Reference
  - Archon Integration
  - Key Principles
  - Error Handling
  - Quality Gates
  - Success Metrics
- Update the main workflow documentation to show: Manual INITIAL → /generate-prp → /execute-prp

**Git Status:**
- Currently 4 uncommitted agent file modifications (shown in git status)
- These may be prp-gen vs prp-initial duplicates
- Review and clean up before committing

**Testing After Cleanup:**
- Verify `/generate-prp` still works
- Verify `/execute-prp` still works
- Verify no broken references to removed agents
- Check CLAUDE.md renders properly and makes sense
