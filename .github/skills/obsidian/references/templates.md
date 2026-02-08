# Note Creation Guide

## Intent Determination

Before creating a note, determine the type from the user's intent. Common note types include:

- **Atomic/General note** — Findings, observations, general information
- **Research** — Investigations, tool evaluations, deep dives
- **Thought** — Quick ideas, reflections, opinions
- **Meeting** — Meeting notes, call summaries
- **Project** — Project tracking and planning
- **Map of Content (MOC)** — Linking related notes by domain
- **Daily** — Daily journal entries

## Vault Rules File

Every vault may have a rules file that defines:
- Folder structure and paths for each note type
- Templates with specific frontmatter fields and body structure
- Naming conventions (timestamp, title-based, etc.)
- Tagging conventions
- Subfolder rules (e.g., project categories)

**On first use per session**, read the vault rules file (path configured in `CLAUDE.local.md`) to learn the vault's specific conventions. Follow those rules exactly.

If no rules file exists, apply the generic best practices below.

## Generic Best Practices

### Always Include Frontmatter

**Never create a note without frontmatter.** At minimum include:

```yaml
---
id: {YYYYMMDDHHmm}
type: {note type}
tags:
  - {type-tag}
  - {MM-YYYY}
created: {YYYY-MM-DD}
updated: {YYYY-MM-DD}
---
```

### Timestamp Generation

```bash
TIMESTAMP=$(date +"%Y%m%d%H%M")
DATE_TAG=$(date +"%m-%Y")
DATE_ISO=$(date +"%Y-%m-%d")
```

### Multiline Content via Heredoc

```bash
obsidian-cli create "{path}" --content "$(cat <<'EOF'
---
id: ...
type: ...
tags:
  - ...
created: ...
updated: ...
---

# Title

Content here.
EOF
)"
```

### Before Creating

1. **Search first** — check if a similar note exists: `obsidian-cli search-content "topic"`
2. **List the target folder** — verify you're writing to the right place: `obsidian-cli list "{folder}"`
3. **Check vault rules** — use the correct template for the note type
4. **If unsure about location** — list parent folders to discover subfolders, ask the user if ambiguous

### Updating Existing Notes

When modifying an existing note, always preserve the frontmatter. Use the read-modify-write pattern:

1. `obsidian-cli print "{path}"` — read current content
2. Modify content (keep frontmatter intact, update `updated` field)
3. `obsidian-cli create "{path}" --content "..." --overwrite`

To update just the `updated` field after editing:

```bash
obsidian-cli fm "{path}" --edit --key "updated" --value "$(date +%Y-%m-%d)"
```

### Tags

Tags are managed via frontmatter, not inline. When updating tags:

```bash
obsidian-cli fm "{path}" --edit --key "tags" --value "[tag1, tag2, tag3]"
```

**Warning:** This overwrites the entire tags field. Include existing tags in the value.
