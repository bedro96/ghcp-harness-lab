# mdtodo Design

## Summary

`mdtodo` is a small Python CLI for managing a markdown checkbox todo file. It
supports adding todos, listing incomplete todos, and marking the Nth incomplete
todo done. It uses only the Python standard library and runs as:

```bash
python3 -m mdtodo ...
```

## Scope

### Goals

- Read the todo file from `MDTODO_FILE`, or use `./tasks.md` by default.
- Store todos as markdown checkbox lines: `- [ ] text` or `- [x] text`.
- Append new incomplete todos with `add TEXT`.
- List only incomplete todos, renumbered from 1.
- Mark the Nth incomplete todo complete with `done N`.
- Preserve completed todos and non-todo markdown lines.
- Report invalid `N` on stderr and exit with code 1.

### Non-goals

- Due dates.
- Priorities.
- Remote sync.
- TUI behavior.
- Non-standard-library dependencies.

## Architecture

The implementation is a single module, `mdtodo.py`, with small internal seams:

- `main(argv=None)` handles CLI parsing, command dispatch, user-visible output,
  and process-style exit codes.
- A path helper resolves `MDTODO_FILE`, defaulting to `./tasks.md` relative to
  the current working directory.
- File helpers read and write raw lines. They preserve all existing lines except
  for the single checkbox line changed by `done`.
- Pure todo helpers identify markdown checkbox lines, collect incomplete items
  in display order, and map a displayed number back to the source line.

This keeps command behavior easy to test while avoiding unnecessary classes or
packaging.

## Command Behavior

### `add TEXT`

`add` resolves the todo file path and appends a new line:

```markdown
- [ ] TEXT
```

If the file does not exist, `add` creates it. The command prints:

```text
Added #N: TEXT
```

`N` is the new todo's incomplete-list number after appending.

### `list`

`list` prints only incomplete todo lines. Completed todos and non-todo markdown
are omitted from output but remain in the file. Output is renumbered from 1:

```markdown
- [ ] 1. First incomplete task
- [ ] 2. Second incomplete task
```

If the file does not exist, `list` prints nothing and exits 0.

### `done N`

`done` treats `N` as the displayed number among incomplete todos. It updates the
matching source line from `- [ ] TEXT` to `- [x] TEXT`, preserves all other
lines, writes the file back, and prints:

```text
Done: TEXT
```

If the file does not exist, if `N` is not an integer, if `N < 1`, or if `N`
exceeds the number of incomplete todos, the command writes an error to stderr
and exits 1.

## Parsing Rules

The parser recognizes these todo line forms:

- `- [ ] text`
- `- [x] text`

Only lowercase `x` is treated as completed. Lines that do not match these forms
are non-todo markdown and are preserved. Line endings are preserved where
possible; rewritten `done` lines keep the original trailing newline.

## Error Handling

User-facing command shape and invalid index errors are surfaced through stderr
with exit code 1. Successful commands write their normal output to stdout and
exit 0. The implementation does not silently ignore invalid `done` indexes.

## Testing

Tests live in `tests/test_mdtodo.py` and run with:

```bash
python3 -m unittest discover -s tests
```

Tests use temporary directories or files and isolate `MDTODO_FILE`. Coverage
includes:

- adding to a missing file;
- listing incomplete todos with renumbering;
- marking the Nth incomplete todo done;
- preserving completed todos and unrelated markdown;
- using `MDTODO_FILE` instead of `./tasks.md`;
- invalid `done` indexes and non-integer values;
- missing-file behavior for `list` and `done`.
