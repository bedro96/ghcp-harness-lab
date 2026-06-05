# DESIGN — mdtodo

**Date:** 2026-06-05  
**Status:** Approved

## Overview

`mdtodo` is a small Python CLI that manages a markdown checkbox todo file. It supports three commands (`add`, `list`, `done`) and operates on a single file defined by the `MDTODO_FILE` environment variable or `./tasks.md` by default.

---

## File Format

The todo file contains markdown checkbox lines mixed with any other content (headers, blank lines). Non-todo lines are preserved verbatim.

```
- [ ] incomplete task
- [x] completed task
```

Only lines matching `- [ ] ...` or `- [x] ...` are treated as todo items.

---

## Data Model

The file is parsed into a sequence of **entries**:

- `TodoItem(text: str, done: bool)` — represents a checkbox line
- `RawLine(content: str)` — represents any other line, preserved as-is on write

---

## Architecture

Single module `mdtodo.py`, invoked as `python3 -m mdtodo`.

| Layer | Responsibility |
|---|---|
| `parse(text: str) → list[Entry]` | Converts raw file text to entries |
| `serialize(entries) → str` | Converts entries back to file text |
| `load_file(path) → list[Entry]` | Reads file; creates empty file if missing |
| `save_file(path, entries)` | Writes serialized entries to file |
| `cmd_add(entries, text) → str` | Appends a new `TodoItem`; returns confirmation message |
| `cmd_done(entries, n: int) → str` | Marks n-th incomplete item done; raises `ValueError` for invalid n |
| `cmd_list(entries) → list[str]` | Returns display lines for incomplete items |
| `main()` | Parses `sys.argv`, dispatches commands, handles errors |

---

## Command Behaviour

### `add <text>`

Appends `- [ ] <text>` to the file.

Output: `Added #<N>: <text>` where N is the total number of todo items (including done) after adding.

### `list`

Prints incomplete items only, renumbered from 1. One item per line:

```
- [ ] 1. task one
- [ ] 2. task two
```

Prints nothing if no incomplete items exist.

### `done <N>`

Marks the N-th incomplete item (as shown in `list`) as done by changing `[ ]` to `[x]`.

Output: `Done #<N>: <text>`

Invalid N (non-integer, out of range, zero, negative) → print `Error: no item #<N>` to stderr, exit code 1.

---

## Error Handling

| Situation | Output | Exit code |
|---|---|---|
| Unknown command | Usage message to stderr | 1 |
| Wrong number of arguments | Usage message to stderr | 1 |
| `done` with invalid/out-of-range N | `Error: no item #<N>` to stderr | 1 |

---

## File Auto-creation

If the target file does not exist, all three commands silently create an empty file before proceeding. (`list` on an empty file prints nothing; `done` on an empty file immediately errors.)

---

## Implementation Constraints

- Python 3.10+ standard library only (no third-party packages)
- Single module: `mdtodo.py` + entry point `python3 -m mdtodo ...`
- Tests: `tests/test_mdtodo.py`, run via `python3 -m unittest discover -s tests`

---

## Testing Strategy

- **Unit tests for `parse` / `serialize`**: round-trip correctness, edge cases (empty file, only done items, mixed content)
- **Unit tests for `cmd_add`, `cmd_done`, `cmd_list`**: operate purely on lists — no filesystem I/O
- **Integration tests for `load_file` / `save_file`**: use `tempfile.NamedTemporaryFile`
- **End-to-end tests for `main()`**: invoke via `subprocess` or by patching `sys.argv` + capturing stdout/stderr

---

## Non-Goals

- Due dates, priorities, or tags
- Remote sync
- TUI / interactive mode
