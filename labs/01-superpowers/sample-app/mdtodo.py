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
    raise NotImplementedError


def cmd_add(entries: list[Entry], text: str) -> str:
    raise NotImplementedError


def cmd_done(entries: list[Entry], n: int) -> str:
    raise NotImplementedError


def main() -> None:
    raise NotImplementedError


if __name__ == '__main__':
    main()
