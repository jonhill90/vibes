# obsidian-cli Command Reference

Complete flag-by-flag reference for all obsidian-cli commands.

## set-default

Set the default vault for all future commands.

```bash
obsidian-cli set-default "{vault-name}"
```

| Argument | Required | Description |
|----------|----------|-------------|
| `vault-name` | Yes | Name of the Obsidian vault (not the path) |

## print-default

Print the currently configured default vault.

```bash
obsidian-cli print-default [flags]
```

| Flag | Description |
|------|-------------|
| `--path-only` | Print only the vault path (useful for scripting) |

## open

Open a note in the Obsidian application.

```bash
obsidian-cli open "{note-name}" [flags]
```

| Argument/Flag | Required | Description |
|---------------|----------|-------------|
| `note-name` | Yes | Note name or path from vault root |
| `--vault` / `-v` | No | Vault name (uses default if omitted) |
| `--section` / `-s` | No | Heading text to scroll to (case-sensitive) |

## daily

Open today's daily note in Obsidian. Creates from template if it doesn't exist.

```bash
obsidian-cli daily [flags]
```

| Flag | Description |
|------|-------------|
| `--vault` / `-v` | Vault name (uses default if omitted) |

## search

**DO NOT USE in scripts or automation.** Launches an interactive fuzzy finder in the terminal. Use `search-content` instead.

```bash
obsidian-cli search [flags]
```

| Flag | Description |
|------|-------------|
| `--vault` / `-v` | Vault name |
| `--editor` / `-e` | Open selected note in `$EDITOR` instead of Obsidian |

## search-content

Search for notes containing a term in their content. Returns file paths with line numbers and matching snippets.

```bash
obsidian-cli search-content "{term}" [flags]
```

| Argument/Flag | Required | Description |
|---------------|----------|-------------|
| `term` | Yes | Text to search for in note content |
| `--vault` / `-v` | No | Vault name (uses default if omitted) |
| `--editor` / `-e` | No | Open selected note in `$EDITOR` instead of Obsidian |

## list

List files and folders at a vault path.

```bash
obsidian-cli list [path] [flags]
```

| Argument/Flag | Required | Description |
|---------------|----------|-------------|
| `path` | No | Folder path from vault root (lists root if omitted) |
| `--vault` / `-v` | No | Vault name (uses default if omitted) |

**Note:** Lists one level only (no recursive depth option).

## print

Print the contents of a note to stdout.

```bash
obsidian-cli print "{note}" [flags]
```

| Argument/Flag | Required | Description |
|---------------|----------|-------------|
| `note` | Yes | Note name or path from vault root |
| `--vault` / `-v` | No | Vault name (uses default if omitted) |

## create

Create a new note, or update an existing note with `--overwrite` or `--append`.

```bash
obsidian-cli create "{note-path}" [flags]
```

| Argument/Flag | Required | Description |
|---------------|----------|-------------|
| `note-path` | Yes | Note name or path from vault root |
| `--content` / `-c` | No | Note content (creates empty note if omitted) |
| `--overwrite` | No | Replace existing note content |
| `--append` | No | Append to existing note content |
| `--open` / `-o` | No | Open note after creating |
| `--editor` / `-e` | No | Open in `$EDITOR` instead of Obsidian |
| `--vault` / `-v` | No | Vault name (uses default if omitted) |

**Behavior without --overwrite or --append:** If the note already exists, a duplicate is created (e.g., `note 1.md`). Always use `--overwrite` or `--append` for existing notes.

### Heredoc Pattern for Multiline Content

```bash
obsidian-cli create "{note-path}" --content "$(cat <<'EOF'
---
title: Example
tags:
  - example
---

# Example

Multi-line content with frontmatter.
EOF
)" --overwrite
```

### Pipe Pattern

```bash
echo "Content from pipe" | obsidian-cli create "{note-path}" --content "$(cat -)"
```

## move

Move or rename a note. Updates all backlinks in the vault automatically.

```bash
obsidian-cli move "{current-path}" "{new-path}" [flags]
```

| Argument/Flag | Required | Description |
|---------------|----------|-------------|
| `current-path` | Yes | Current note path from vault root |
| `new-path` | Yes | New note path from vault root |
| `--open` / `-o` | No | Open note after moving |
| `--editor` / `-e` | No | Open in `$EDITOR` instead of Obsidian |
| `--vault` / `-v` | No | Vault name (uses default if omitted) |

**Note:** If same folder but different name, treated as a rename.

## delete

Delete a note from the vault.

```bash
obsidian-cli delete "{note-path}" [flags]
```

| Argument/Flag | Required | Description |
|---------------|----------|-------------|
| `note-path` | Yes | Note path from vault root |
| `--vault` / `-v` | No | Vault name (uses default if omitted) |

**Warning:** No confirmation prompt. Deletion is permanent (not moved to trash).

## frontmatter

View and modify YAML frontmatter in notes. **Alias:** `fm`

```bash
obsidian-cli frontmatter "{note}" [flags]
obsidian-cli fm "{note}" [flags]
```

### Print Frontmatter

```bash
obsidian-cli fm "{note}" --print
```

### Edit/Add a Field

```bash
obsidian-cli fm "{note}" --edit --key "{key}" --value "{value}"
```

### Delete a Field

```bash
obsidian-cli fm "{note}" --delete --key "{key}"
```

| Flag | Description |
|------|-------------|
| `--print` / `-p` | Print the frontmatter |
| `--edit` / `-e` | Edit or add a frontmatter field |
| `--delete` / `-d` | Delete a frontmatter field |
| `--key` / `-k` | Field name (required with `--edit` and `--delete`) |
| `--value` | Field value (required with `--edit`) |
| `--vault` / `-v` | Vault name (uses default if omitted) |

**Note:** One key per invocation. Chain commands for multiple fields:

```bash
obsidian-cli fm "{note}" --edit --key "status" --value "done" && \
obsidian-cli fm "{note}" --edit --key "priority" --value "1"
```

## Aliases Quick Reference

| Alias | Full Command |
|-------|-------------|
| `fm` | `frontmatter` |

## Global Flag

All commands that interact with vault content support:

| Flag | Description |
|------|-------------|
| `--vault` / `-v` | Override default vault for this command |

## Error Patterns

| Error | Cause | Fix |
|-------|-------|-----|
| `default vault not set` | No default vault configured | `obsidian-cli set-default "{name}"` |
| `vault not found` | Vault name doesn't match Obsidian's config | Check vault name in Obsidian settings |
| `note not found` | Path doesn't exist in vault | Use `list` to verify path |
| `frontmatter not found` | Note has no YAML frontmatter block | Add `---` block at top of note |
| Duplicate file created | Used `create` without `--overwrite`/`--append` | Delete duplicate, use correct flag |
| Command hangs | Used `search` (interactive) instead of `search-content` | Ctrl+C and use `search-content` |
