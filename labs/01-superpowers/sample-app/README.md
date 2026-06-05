# mdtodo

Small Python CLI for managing markdown checkbox todos.

## Usage

```bash
python3 -m mdtodo add "buy milk"      # Added #1: buy milk
python3 -m mdtodo list                # - [ ] 1. buy milk
python3 -m mdtodo done 1              # Done #1: buy milk
```

By default, `mdtodo` reads and writes `./tasks.md`.
Set `MDTODO_FILE` to use another file:

```bash
MDTODO_FILE=/tmp/tasks.md python3 -m mdtodo list
```

## Todo format

```markdown
- [ ] incomplete task
- [x] completed task
```

`list` shows only incomplete items, renumbered from 1.
`done <N>` marks the N-th incomplete item (as shown by `list`) as done.
Invalid `N` prints an error to stderr and exits with code 1.

## Requirements

Python 3.10+, standard library only.
