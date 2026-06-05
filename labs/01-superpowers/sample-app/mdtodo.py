# mdtodo.py
from __future__ import annotations
from dataclasses import dataclass
from pathlib import Path
from typing import Union
import os
import re
import sys


@dataclass
class TodoItem:
    text: str
    done: bool


@dataclass
class RawLine:
    content: str


Entry = Union[TodoItem, RawLine]

TODO_RE = re.compile(r'^- \[([ x])\] (.+)$')

DEFAULT_FILE = './tasks.md'


def parse(text: str) -> list[Entry]:
    if not text:
        return []
    
    entries: list[Entry] = []
    lines = text.split('\n')
    # Remove trailing empty line created by trailing newline, but preserve if all lines are empty
    if lines and lines[-1] == '' and any(line for line in lines[:-1]):
        lines = lines[:-1]
    
    for line in lines:
        m = TODO_RE.match(line)
        if m:
            entries.append(TodoItem(text=m.group(2), done=m.group(1) == 'x'))
        else:
            entries.append(RawLine(content=line))
    return entries


def serialize(entries: list[Entry]) -> str:
    if not entries:
        return ''
    lines = []
    for e in entries:
        if isinstance(e, TodoItem):
            mark = 'x' if e.done else ' '
            lines.append(f'- [{mark}] {e.text}')
        else:
            lines.append(e.content)
    
    result = '\n'.join(lines) + '\n'
    return result


def load_file(path: str) -> list[Entry]:
    p = Path(path)
    if not p.exists():
        p.touch()
        return []
    return parse(p.read_text())


def save_file(path: str, entries: list[Entry]) -> None:
    Path(path).write_text(serialize(entries))


def cmd_list(entries: list[Entry]) -> list[str]:
    incomplete = [e for e in entries if isinstance(e, TodoItem) and not e.done]
    return [f'- [ ] {i + 1}. {item.text}' for i, item in enumerate(incomplete)]


def cmd_add(entries: list[Entry], text: str) -> str:
    entries.append(TodoItem(text=text, done=False))
    total = sum(1 for e in entries if isinstance(e, TodoItem))
    return f'Added #{total}: {text}'


def cmd_done(entries: list[Entry], n: int) -> str:
    incomplete = [
        (i, e) for i, e in enumerate(entries)
        if isinstance(e, TodoItem) and not e.done
    ]
    if n < 1 or n > len(incomplete):
        raise ValueError(n)
    idx, item = incomplete[n - 1]
    entries[idx] = TodoItem(text=item.text, done=True)
    return f'Done #{n}: {item.text}'


def main() -> None:
    args = sys.argv[1:]
    if not args:
        print('Usage: python3 -m mdtodo <add|list|done> [args]', file=sys.stderr)
        sys.exit(1)

    path = os.environ.get('MDTODO_FILE', DEFAULT_FILE)
    cmd = args[0]
    entries = load_file(path)

    if cmd == 'add':
        if len(args) != 2:
            print('Usage: python3 -m mdtodo add <text>', file=sys.stderr)
            sys.exit(1)
        print(cmd_add(entries, args[1]))
        save_file(path, entries)

    elif cmd == 'list':
        if len(args) != 1:
            print('Usage: python3 -m mdtodo list', file=sys.stderr)
            sys.exit(1)
        for line in cmd_list(entries):
            print(line)

    elif cmd == 'done':
        if len(args) != 2:
            print('Usage: python3 -m mdtodo done <N>', file=sys.stderr)
            sys.exit(1)
        try:
            n = int(args[1])
        except ValueError:
            print(f'Error: no item #{args[1]}', file=sys.stderr)
            sys.exit(1)
        try:
            print(cmd_done(entries, n))
        except ValueError:
            print(f'Error: no item #{n}', file=sys.stderr)
            sys.exit(1)
        save_file(path, entries)

    else:
        print(f'Unknown command: {cmd}', file=sys.stderr)
        print('Usage: python3 -m mdtodo <add|list|done> [args]', file=sys.stderr)
        sys.exit(1)


if __name__ == '__main__':
    main()
