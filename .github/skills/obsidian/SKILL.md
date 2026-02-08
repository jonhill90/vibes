---
name: obsidian
description: Read, write, search, and manage notes in Obsidian vaults using obsidian-cli. Use when working with Obsidian notes, vaults, knowledge bases, daily notes, or personal wikis.
argument-hint: <command or request>
---

# Obsidian Vault Operations

Interact with Obsidian vaults using obsidian-cli (Go binary).

**CLI:** `obsidian-cli`

## Prerequisites

```bash
# Verify installation
obsidian-cli --version
```

### Install

**macOS / Linux (Homebrew):**
```bash
brew tap yakitrak/yakitrak && brew install yakitrak/yakitrak/obsidian-cli
```

**Windows (Scoop):**
```powershell
scoop bucket add scoop-yakitrak https://github.com/yakitrak/scoop-yakitrak.git
scoop install obsidian-cli
```

**Any platform (GitHub release):**
Download the binary for your OS/arch from [GitHub Releases](https://github.com/yakitrak/obsidian-cli/releases) and place it on your PATH.

| OS | Asset |
|----|-------|
| macOS (universal) | `obsidian-cli_*_darwin_all.tar.gz` |
| Linux amd64 | `obsidian-cli_*_linux_amd64.tar.gz` |
| Linux arm64 | `obsidian-cli_*_linux_arm64.tar.gz` |
| Windows amd64 | `obsidian-cli_*_windows_amd64.tar.gz` |
| Windows arm64 | `obsidian-cli_*_windows_arm64.tar.gz` |

## Vault Setup

On first use, check if a default vault is configured:

```bash
obsidian-cli print-default
```

**If no vault is set**, discover available vaults from the Obsidian config and prompt the user:

```bash
# macOS
cat ~/Library/Application\ Support/obsidian/obsidian.json

# Linux
cat ~/.config/obsidian/obsidian.json

# Windows (PowerShell)
cat $env:APPDATA/obsidian/obsidian.json
```

This returns JSON with vault names and paths. Present the options to the user, then set the default:

```bash
obsidian-cli set-default "{vault-name}"
```

### CLAUDE.local.md Configuration

After setting the vault, check `CLAUDE.local.md` in the project root for vault configuration:

```markdown
## Obsidian
- Vault: {vault-name}
- Rules: {path to vault rules note}
```

If this section doesn't exist, ask the user:
1. Which vault to use (if multiple)
2. Whether the vault has a rules/guide file (and its path)

Then instruct the user to add the config to `CLAUDE.local.md`.

## Vault Rules

**On first use per session**, if `CLAUDE.local.md` specifies a rules path, read it:

```bash
obsidian-cli print "{rules-note-path}"
```

The rules file tells you how this specific vault is structured — folder paths, templates, naming conventions, tagging rules. **Follow those rules exactly when creating or organizing notes.**

If no rules file is configured, use the generic best practices in the [Note Creation Guide](references/templates.md).

## Read a Note

```bash
# Print note contents by name or path
obsidian-cli print "{note-name}"
obsidian-cli print "{path/to/note}"

# Print from a specific vault
obsidian-cli print "{note-name}" --vault "{vault-name}"
```

## Create a Note

**NEVER create a note without frontmatter.**

1. Determine intent (what type of note?)
2. Read vault rules for the correct template, folder, and naming convention
3. Search first — check if a similar note exists
4. List the target folder — verify you're writing to the right place
5. Create the note with proper frontmatter and body structure

See [Note Creation Guide](references/templates.md) for intent determination, generic best practices, and heredoc examples.

### Create / Append / Overwrite

```bash
# Create new note (always include frontmatter in content)
obsidian-cli create "{path}" --content "$(cat <<'EOF'
---
id: ...
type: ...
tags: ...
created: ...
updated: ...
---
# Content
EOF
)"

# Append to existing note
obsidian-cli create "{path}" --content "additional content" --append

# Overwrite existing note (read-modify-write pattern)
obsidian-cli create "{path}" --content "full replacement" --overwrite
```

**IMPORTANT:**
- Without `--append` or `--overwrite`, creating a note that exists makes a duplicate
- Always use `--overwrite` or `--append` when updating existing notes
- When overwriting, preserve the original frontmatter and update the `updated` field

## Search Notes

```bash
# Search note content (returns matching files with line numbers)
obsidian-cli search-content "search term"

# Search in a specific vault
obsidian-cli search-content "search term" --vault "{vault-name}"
```

**WARNING:** Do NOT use `obsidian-cli search` — it launches an interactive fuzzy finder that cannot be used in scripts or automation.

## List Files and Folders

```bash
# List vault root
obsidian-cli list

# List a subfolder
obsidian-cli list "{folder-path}"

# List in a specific vault
obsidian-cli list "{folder-path}" --vault "{vault-name}"
```

## Frontmatter Operations

```bash
# Print frontmatter
obsidian-cli frontmatter "{note-name}" --print

# Edit/add a field
obsidian-cli frontmatter "{note-name}" --edit --key "status" --value "done"

# Delete a field
obsidian-cli frontmatter "{note-name}" --delete --key "draft"

# Specific vault
obsidian-cli frontmatter "{note-name}" --print --vault "{vault-name}"
```

Alias: `obsidian-cli fm` works the same as `obsidian-cli frontmatter`.

### Multiple Frontmatter Edits

Run multiple commands sequentially:

```bash
obsidian-cli fm "{note}" --edit --key "status" --value "active" && \
obsidian-cli fm "{note}" --edit --key "priority" --value "high" && \
obsidian-cli fm "{note}" --edit --key "updated" --value "$(date +%Y-%m-%d)"
```

## Move, Rename, Delete

```bash
# Move or rename (updates all backlinks in vault)
obsidian-cli move "{current-path}" "{new-path}"

# Delete a note
obsidian-cli delete "{note-path}"

# With specific vault
obsidian-cli move "{current}" "{new}" --vault "{vault-name}"
obsidian-cli delete "{note-path}" --vault "{vault-name}"
```

## Open in Obsidian App

```bash
# Open a note in the Obsidian app
obsidian-cli open "{note-name}"

# Open at a specific heading
obsidian-cli open "{note-name}" --section "{heading-text}"

# Open today's daily note (creates from template if needed)
obsidian-cli daily
```

## Common Workflows

### Read-Modify-Write

When you need to edit specific parts of an existing note:

```bash
# 1. Read the current content
obsidian-cli print "{note-path}"

# 2. Modify the content (Claude edits in memory)

# 3. Write back the full modified content
obsidian-cli create "{note-path}" --content "$(cat <<'EOF'
... modified full content ...
EOF
)" --overwrite
```

### Find and Read Related Notes

```bash
# Search for related content
obsidian-cli search-content "topic"

# Read each relevant result
obsidian-cli print "{result-1}"
obsidian-cli print "{result-2}"
```

### Tag Management via Frontmatter

```bash
# Check current tags
obsidian-cli fm "{note}" --print

# Add/update tags (overwrites the tags field)
obsidian-cli fm "{note}" --edit --key "tags" --value "[tag1, tag2, tag3]"
```

## Gotchas

1. **`search` is interactive** — Always use `search-content` for scripted/automated search
2. **`create` makes duplicates** — Always pass `--overwrite` or `--append` when updating
3. **No surgical edits** — Use read-modify-write pattern (print, edit in memory, create --overwrite)
4. **Paths are from vault root** — Not from your terminal's current working directory
5. **Frontmatter is one key at a time** — Chain multiple `fm --edit` calls for multiple fields

## Troubleshooting

| Problem | Solution |
|---------|----------|
| "vault not found" | Run `obsidian-cli set-default "{vault-name}"` |
| "note not found" | Check path with `obsidian-cli list "{folder}"` |
| Duplicate note created | Use `--overwrite` or `--append` flag |
| Search hangs | You used `search` instead of `search-content` |
| Frontmatter not updating | Ensure note has valid YAML frontmatter block |

## References

- [Note Creation Guide](references/templates.md) — Intent determination and generic best practices
- [Command Reference](references/command-reference.md) — Flag-by-flag details for all commands
