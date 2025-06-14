# Agent-0 Development Workflow

## 🔄 Daily Workflow

### Start of Session
1. Read CONTEXT.md
2. Check current phase in PHASES.md
3. Review CAPABILITIES.md for gaps
4. Check PROGRESS.md for status

### During Development
1. Work on current phase tasks only
2. Test each component before moving on
3. Update PROGRESS.md with results
4. Document any blockers

### End of Session
1. Update PROGRESS.md
2. Commit context updates
3. Note next steps
4. Flag any blockers

## 📝 Progress Tracking

### Task States
- ⬜ Not Started
- 🟨 In Progress  
- ✅ Complete
- ❌ Blocked
- 🔄 Needs Revision

### Update Format
```markdown
## Date: YYYY-MM-DD
### Phase: X
### Tasks Completed:
- Task description
### Blockers:
- Blocker description
### Next Steps:
- Next task
```

## 🚧 Testing Protocol

### Before Moving Phases
1. All tasks must be ✅
2. Create test report
3. Get human approval
4. Update phase status
5. No skipping allowed!

### Test Documentation
```markdown
## Phase X Test Report
### Tests Performed:
- Test 1: Description - Result
### Issues Found:
- Issue description
### Resolution:
- How it was fixed
```

## 💡 Context Preservation

### Key Documents
1. **CONTEXT.md** - Project overview (rarely changes)
2. **PHASES.md** - Development phases (update phase status)
3. **CAPABILITIES.md** - Required tools (update as discovered)
4. **PROGRESS.md** - Daily progress (update frequently)
5. **WORKFLOW.md** - This document (process guide)

### When Confused
1. Re-read CONTEXT.md
2. Check current phase
3. Review recent progress
4. Ask for clarification
5. Don't assume - verify!

