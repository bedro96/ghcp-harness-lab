# mdtodo

Small Python CLI for managing markdown checkbox todos.

## Usage

```bash
python3 -m mdtodo add "buy milk"   # Added #1: buy milk
python3 -m mdtodo list             # - [ ] 1. buy milk
python3 -m mdtodo done 1           # Done #1: buy milk
```

Set `MDTODO_FILE` to use a different file (default: `./tasks.md`):

```bash
MDTODO_FILE=/tmp/tasks.md python3 -m mdtodo list
```

## Format

```markdown
- [ ] incomplete task
- [x] completed task
```

`list` shows only incomplete items, renumbered from 1.
`done <N>` marks the N-th incomplete item as done. Invalid N → stderr + exit 1.

Python 3.10+, standard library only.
