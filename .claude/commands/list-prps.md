# List PRPs

List all PRPs (Product Requirements Prompts) organized by status.

## Usage

```
/list-prps [status]
```

## Arguments

- `status` (optional): Filter by status
  - `active` - Show only PRPs in progress
  - `completed` - Show finished PRPs
  - `archived` - Show old/reference PRPs
  - If omitted: Show all PRPs from all directories

## Output Format

PRPs are displayed with:
- **Status**: Active, Completed, or Archived
- **Title**: Extracted from PRP frontmatter `name:` field
- **File**: Filename
- **Modified**: Last modification date
- **Path**: Full path to file

## Examples

### List all PRPs
```
/list-prps
```

Output:
```
ACTIVE PRPs (2):
✨ Context Engineering Foundation - INITIAL_context_engineering_foundation.md
   Modified: 2024-01-15 10:30
   Path: prps/active/INITIAL_context_engineering_foundation.md

✨ Multi-Agent System - multi_agent_research_email.md
   Modified: 2024-01-14 14:20
   Path: prps/active/multi_agent_research_email.md

COMPLETED PRPs (1):
✅ User Authentication - user_auth_endpoint.md
   Modified: 2024-01-10 09:15
   Path: prps/completed/user_auth_endpoint.md

ARCHIVED PRPs (3):
📦 Legacy Feature - legacy_feature.md
   Modified: 2023-12-01 16:45
   Path: prps/archived/legacy_feature.md
```

### List only active PRPs
```
/list-prps active
```

Output:
```
ACTIVE PRPs (2):
✨ Context Engineering Foundation - INITIAL_context_engineering_foundation.md
   Modified: 2024-01-15 10:30
   Path: prps/active/INITIAL_context_engineering_foundation.md

✨ Multi-Agent System - multi_agent_research_email.md
   Modified: 2024-01-14 14:20
   Path: prps/active/multi_agent_research_email.md
```

### List completed PRPs
```
/list-prps completed
```

### List archived PRPs
```
/list-prps archived
```

## Implementation

The command scans the following directories:
- `prps/active/` - In-progress PRPs
- `prps/completed/` - Finished PRPs
- `prps/archived/` - Old/reference PRPs

For each PRP file (`.md` extension):
1. Read the frontmatter to extract the `name:` field
2. Get file metadata (modification time)
3. Format and display with status indicator

## Sorting

PRPs are sorted by:
1. Status (active → completed → archived)
2. Within each status, by modification date (newest first)

## Notes

- Only `.md` files are considered PRPs
- If a PRP doesn't have a `name:` field in frontmatter, the filename is used
- Hidden files (starting with `.`) are ignored
- Empty directories show "No PRPs found"

## Related Commands

- `/generate-prp` - Create a new PRP
- `/execute-prp` - Execute an existing PRP

## Workflow Integration

Typical PRP lifecycle workflow:

1. Create PRP: `/generate-prp INITIAL_feature.md`
   - PRP created in `prps/active/`

2. Check status: `/list-prps active`
   - See all active PRPs

3. Execute PRP: `/execute-prp prps/active/feature.md`
   - Implement the feature

4. Move to completed:
   - `mv prps/active/feature.md prps/completed/`

5. List completed: `/list-prps completed`
   - Verify PRP is completed

6. Archive when no longer needed:
   - `mv prps/completed/feature.md prps/archived/`
