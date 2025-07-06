# Updated Preferences Prompt - Corrected Paths

## Recommended Preferences Prompt
```
CRITICAL: Container operations use /workspace/vibes/, host mounts use actual paths.
Read docs/claude-capabilities.md for core tools.
Check /workspace/vibes/.vibes/user-config/ for additional capabilities (auto-create if missing).
```

## Path Corrections Made

### Original Issue
- Used ~/.vibes/user-config/ (container home directory)
- Created at /root/.vibes/user-config/ inside container
- Would NOT persist when container recreated

### Fixed Location  
- Now using /workspace/vibes/.vibes/user-config/
- Part of mounted vibes folder structure
- WILL persist on host filesystem
- Files accessible at /Users/jon/vibes/.vibes/user-config/ on host

## Current Structure
```
/workspace/vibes/
├── .vibes/
│   └── user-config/
│       ├── mcp-servers.md
│       ├── behavioral-rules.md
│       └── session-context.md
├── docs/
│   └── claude-capabilities.md
└── projects/vibes/
    └── [planning files]
```

## Benefits
✅ User config persists across container restarts
✅ Config files are part of vibes folder structure  
✅ Can be version controlled if desired (.gitignore or include)
✅ Accessible from host filesystem for inspection/editing
