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
    raise NotImplementedError


def serialize(entries: list[Entry]) -> str:
    raise NotImplementedError


def load_file(path: str) -> list[Entry]:
    raise NotImplementedError


def save_file(path: str, entries: list[Entry]) -> None:
    raise NotImplementedError


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
