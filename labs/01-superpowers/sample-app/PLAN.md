# mdtodo Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a single-module Python CLI (`mdtodo.py`) that manages a markdown checkbox todo file via `add`, `list`, and `done` commands.

**Architecture:** Parse the file into a list of `Entry` objects (`TodoItem` or `RawLine`), mutate the list in memory, then serialize and write back. Each command is a pure function operating on the list — no filesystem I/O in command logic.

**Tech Stack:** Python 3.10+ standard library only (`re`, `os`, `sys`, `pathlib`, `dataclasses`, `unittest`, `subprocess`, `tempfile`).

---

## File Map

| File | Action | Responsibility |
|---|---|---|
| `mdtodo.py` | Create | All logic: data model, parse/serialize, commands, `main()` |
| `tests/__init__.py` | Create | Makes `tests/` a package |
| `tests/test_mdtodo.py` | Create | All unit + integration + end-to-end tests |

---

### Task 1: Project Skeleton

**Files:**
- Create: `mdtodo.py`
- Create: `tests/__init__.py`
- Create: `tests/test_mdtodo.py`

- [ ] **Step 1: Create `tests/__init__.py` (empty)**

```bash
touch tests/__init__.py
```

- [ ] **Step 2: Create skeleton `mdtodo.py`**

```python
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
```

- [ ] **Step 3: Create skeleton `tests/test_mdtodo.py`**

```python
# tests/test_mdtodo.py
import unittest


class TestParseSkeleton(unittest.TestCase):
    def test_placeholder(self):
        self.assertTrue(True)


if __name__ == '__main__':
    unittest.main()
```

- [ ] **Step 4: Verify skeleton runs**

```bash
python3 -m unittest discover -s tests
```

Expected: `Ran 1 test in ...OK`

- [ ] **Step 5: Commit**

```bash
git add mdtodo.py tests/__init__.py tests/test_mdtodo.py
git commit -m "chore: project skeleton"
```

---

### Task 2: parse() and serialize()

**Files:**
- Modify: `mdtodo.py` — implement `parse()` and `serialize()`
- Modify: `tests/test_mdtodo.py` — add parse/serialize tests

- [ ] **Step 1: Write the failing tests**

Replace the contents of `tests/test_mdtodo.py` with:

```python
# tests/test_mdtodo.py
import unittest
from mdtodo import parse, serialize, TodoItem, RawLine


class TestParse(unittest.TestCase):
    def test_empty_string(self):
        self.assertEqual(parse(''), [])

    def test_single_incomplete(self):
        result = parse('- [ ] buy milk')
        self.assertEqual(result, [TodoItem(text='buy milk', done=False)])

    def test_single_done(self):
        result = parse('- [x] buy milk')
        self.assertEqual(result, [TodoItem(text='buy milk', done=True)])

    def test_raw_line_preserved(self):
        result = parse('# My Tasks')
        self.assertEqual(result, [RawLine(content='# My Tasks')])

    def test_blank_line_preserved(self):
        result = parse('\n')
        self.assertEqual(result, [RawLine(content=''), RawLine(content='')])

    def test_mixed_content(self):
        text = '# Tasks\n- [ ] task one\n- [x] task two'
        result = parse(text)
        self.assertEqual(result, [
            RawLine(content='# Tasks'),
            TodoItem(text='task one', done=False),
            TodoItem(text='task two', done=True),
        ])


class TestSerialize(unittest.TestCase):
    def test_empty(self):
        self.assertEqual(serialize([]), '')

    def test_incomplete_item(self):
        entries = [TodoItem(text='buy milk', done=False)]
        self.assertEqual(serialize(entries), '- [ ] buy milk\n')

    def test_done_item(self):
        entries = [TodoItem(text='buy milk', done=True)]
        self.assertEqual(serialize(entries), '- [x] buy milk\n')

    def test_raw_line(self):
        entries = [RawLine(content='# Header')]
        self.assertEqual(serialize(entries), '# Header\n')

    def test_round_trip(self):
        text = '# Tasks\n- [ ] task one\n- [x] task two\n'
        self.assertEqual(serialize(parse(text)), text)


if __name__ == '__main__':
    unittest.main()
```

- [ ] **Step 2: Run tests to verify they fail**

```bash
python3 -m unittest discover -s tests
```

Expected: multiple errors with `NotImplementedError`

- [ ] **Step 3: Implement `parse()` and `serialize()` in `mdtodo.py`**

Replace the stub bodies:

```python
def parse(text: str) -> list[Entry]:
    entries: list[Entry] = []
    for line in text.splitlines():
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
    return '\n'.join(lines) + '\n'
```

- [ ] **Step 4: Run tests and verify they pass**

```bash
python3 -m unittest tests.test_mdtodo.TestParse tests.test_mdtodo.TestSerialize -v
```

Expected: all `TestParse` and `TestSerialize` tests `OK`

- [ ] **Step 5: Commit**

```bash
git add mdtodo.py tests/test_mdtodo.py
git commit -m "feat: implement parse() and serialize()"
```

---

### Task 3: load_file() and save_file()

**Files:**
- Modify: `mdtodo.py` — implement `load_file()` and `save_file()`
- Modify: `tests/test_mdtodo.py` — append filesystem tests

- [ ] **Step 1: Write the failing tests**

Append to `tests/test_mdtodo.py` (before `if __name__ == '__main__':`):

```python
import tempfile
import os
from mdtodo import load_file, save_file


class TestLoadSaveFile(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.NamedTemporaryFile(
            mode='w', suffix='.md', delete=False
        )
        self.path = self.tmp.name
        self.tmp.close()
        os.unlink(self.path)  # start with no file

    def tearDown(self):
        if os.path.exists(self.path):
            os.unlink(self.path)

    def test_load_creates_file_when_missing(self):
        self.assertFalse(os.path.exists(self.path))
        entries = load_file(self.path)
        self.assertTrue(os.path.exists(self.path))
        self.assertEqual(entries, [])

    def test_load_reads_existing_content(self):
        with open(self.path, 'w') as f:
            f.write('- [ ] hello\n')
        entries = load_file(self.path)
        self.assertEqual(entries, [TodoItem(text='hello', done=False)])

    def test_save_writes_content(self):
        entries = [TodoItem(text='hello', done=False)]
        save_file(self.path, entries)
        with open(self.path) as f:
            self.assertEqual(f.read(), '- [ ] hello\n')

    def test_round_trip_through_files(self):
        original = [TodoItem(text='a', done=False), TodoItem(text='b', done=True)]
        save_file(self.path, original)
        loaded = load_file(self.path)
        self.assertEqual(loaded, original)
```

- [ ] **Step 2: Run tests to verify they fail**

```bash
python3 -m unittest tests.test_mdtodo.TestLoadSaveFile -v
```

Expected: errors with `NotImplementedError`

- [ ] **Step 3: Implement `load_file()` and `save_file()` in `mdtodo.py`**

```python
def load_file(path: str) -> list[Entry]:
    p = Path(path)
    if not p.exists():
        p.touch()
        return []
    return parse(p.read_text())


def save_file(path: str, entries: list[Entry]) -> None:
    Path(path).write_text(serialize(entries))
```

Also add `from pathlib import Path` at the top if not already present (it is in the skeleton).

- [ ] **Step 4: Run tests and verify they pass**

```bash
python3 -m unittest tests.test_mdtodo.TestLoadSaveFile -v
```

Expected: all `TestLoadSaveFile` tests `OK`

- [ ] **Step 5: Commit**

```bash
git add mdtodo.py tests/test_mdtodo.py
git commit -m "feat: implement load_file() and save_file()"
```

---

### Task 4: cmd_list()

**Files:**
- Modify: `mdtodo.py` — implement `cmd_list()`
- Modify: `tests/test_mdtodo.py` — append cmd_list tests

- [ ] **Step 1: Write the failing tests**

Append to `tests/test_mdtodo.py`:

```python
from mdtodo import cmd_list


class TestCmdList(unittest.TestCase):
    def test_empty_entries(self):
        self.assertEqual(cmd_list([]), [])

    def test_all_done(self):
        entries = [TodoItem(text='done task', done=True)]
        self.assertEqual(cmd_list(entries), [])

    def test_single_incomplete(self):
        entries = [TodoItem(text='buy milk', done=False)]
        self.assertEqual(cmd_list(entries), ['- [ ] 1. buy milk'])

    def test_multiple_incomplete(self):
        entries = [
            TodoItem(text='task one', done=False),
            TodoItem(text='task two', done=False),
        ]
        result = cmd_list(entries)
        self.assertEqual(result, ['- [ ] 1. task one', '- [ ] 2. task two'])

    def test_skips_done_items_and_renumbers(self):
        entries = [
            TodoItem(text='task one', done=False),
            TodoItem(text='done task', done=True),
            TodoItem(text='task two', done=False),
        ]
        result = cmd_list(entries)
        self.assertEqual(result, ['- [ ] 1. task one', '- [ ] 2. task two'])

    def test_raw_lines_ignored(self):
        entries = [
            RawLine(content='# Header'),
            TodoItem(text='task one', done=False),
        ]
        result = cmd_list(entries)
        self.assertEqual(result, ['- [ ] 1. task one'])
```

- [ ] **Step 2: Run tests to verify they fail**

```bash
python3 -m unittest tests.test_mdtodo.TestCmdList -v
```

Expected: errors with `NotImplementedError`

- [ ] **Step 3: Implement `cmd_list()` in `mdtodo.py`**

```python
def cmd_list(entries: list[Entry]) -> list[str]:
    incomplete = [e for e in entries if isinstance(e, TodoItem) and not e.done]
    return [f'- [ ] {i + 1}. {item.text}' for i, item in enumerate(incomplete)]
```

- [ ] **Step 4: Run tests and verify they pass**

```bash
python3 -m unittest tests.test_mdtodo.TestCmdList -v
```

Expected: all `TestCmdList` tests `OK`

- [ ] **Step 5: Commit**

```bash
git add mdtodo.py tests/test_mdtodo.py
git commit -m "feat: implement cmd_list()"
```

---

### Task 5: cmd_add()

**Files:**
- Modify: `mdtodo.py` — implement `cmd_add()`
- Modify: `tests/test_mdtodo.py` — append cmd_add tests

- [ ] **Step 1: Write the failing tests**

Append to `tests/test_mdtodo.py`:

```python
from mdtodo import cmd_add


class TestCmdAdd(unittest.TestCase):
    def test_add_to_empty(self):
        entries: list = []
        msg = cmd_add(entries, 'buy milk')
        self.assertEqual(msg, 'Added #1: buy milk')
        self.assertEqual(entries, [TodoItem(text='buy milk', done=False)])

    def test_add_increments_total_count(self):
        entries = [TodoItem(text='existing', done=False)]
        msg = cmd_add(entries, 'new task')
        self.assertEqual(msg, 'Added #2: new task')

    def test_add_counts_done_items_too(self):
        entries = [TodoItem(text='done', done=True)]
        msg = cmd_add(entries, 'new task')
        self.assertEqual(msg, 'Added #2: new task')

    def test_add_appends_to_end(self):
        entries = [
            TodoItem(text='first', done=False),
            RawLine(content='# section'),
        ]
        cmd_add(entries, 'last')
        self.assertIsInstance(entries[-1], TodoItem)
        self.assertEqual(entries[-1].text, 'last')
```

- [ ] **Step 2: Run tests to verify they fail**

```bash
python3 -m unittest tests.test_mdtodo.TestCmdAdd -v
```

Expected: errors with `NotImplementedError`

- [ ] **Step 3: Implement `cmd_add()` in `mdtodo.py`**

```python
def cmd_add(entries: list[Entry], text: str) -> str:
    entries.append(TodoItem(text=text, done=False))
    total = sum(1 for e in entries if isinstance(e, TodoItem))
    return f'Added #{total}: {text}'
```

- [ ] **Step 4: Run tests and verify they pass**

```bash
python3 -m unittest tests.test_mdtodo.TestCmdAdd -v
```

Expected: all `TestCmdAdd` tests `OK`

- [ ] **Step 5: Commit**

```bash
git add mdtodo.py tests/test_mdtodo.py
git commit -m "feat: implement cmd_add()"
```

---

### Task 6: cmd_done()

**Files:**
- Modify: `mdtodo.py` — implement `cmd_done()`
- Modify: `tests/test_mdtodo.py` — append cmd_done tests

- [ ] **Step 1: Write the failing tests**

Append to `tests/test_mdtodo.py`:

```python
from mdtodo import cmd_done


class TestCmdDone(unittest.TestCase):
    def test_marks_first_item_done(self):
        entries = [TodoItem(text='task one', done=False)]
        msg = cmd_done(entries, 1)
        self.assertEqual(msg, 'Done #1: task one')
        self.assertTrue(entries[0].done)

    def test_marks_second_incomplete_done(self):
        entries = [
            TodoItem(text='first', done=False),
            TodoItem(text='second', done=False),
        ]
        msg = cmd_done(entries, 2)
        self.assertEqual(msg, 'Done #2: second')
        self.assertFalse(entries[0].done)
        self.assertTrue(entries[1].done)

    def test_skips_already_done_items(self):
        entries = [
            TodoItem(text='already done', done=True),
            TodoItem(text='target', done=False),
        ]
        msg = cmd_done(entries, 1)
        self.assertEqual(msg, 'Done #1: target')
        self.assertTrue(entries[1].done)

    def test_invalid_n_zero_raises(self):
        entries = [TodoItem(text='task', done=False)]
        with self.assertRaises(ValueError):
            cmd_done(entries, 0)

    def test_invalid_n_too_large_raises(self):
        entries = [TodoItem(text='task', done=False)]
        with self.assertRaises(ValueError):
            cmd_done(entries, 2)

    def test_invalid_n_negative_raises(self):
        entries = [TodoItem(text='task', done=False)]
        with self.assertRaises(ValueError):
            cmd_done(entries, -1)

    def test_empty_list_raises(self):
        with self.assertRaises(ValueError):
            cmd_done([], 1)

    def test_raw_lines_ignored(self):
        entries = [
            RawLine(content='# header'),
            TodoItem(text='the task', done=False),
        ]
        msg = cmd_done(entries, 1)
        self.assertEqual(msg, 'Done #1: the task')
        self.assertTrue(entries[1].done)
```

- [ ] **Step 2: Run tests to verify they fail**

```bash
python3 -m unittest tests.test_mdtodo.TestCmdDone -v
```

Expected: errors with `NotImplementedError`

- [ ] **Step 3: Implement `cmd_done()` in `mdtodo.py`**

```python
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
```

- [ ] **Step 4: Run tests and verify they pass**

```bash
python3 -m unittest tests.test_mdtodo.TestCmdDone -v
```

Expected: all `TestCmdDone` tests `OK`

- [ ] **Step 5: Commit**

```bash
git add mdtodo.py tests/test_mdtodo.py
git commit -m "feat: implement cmd_done()"
```

---

### Task 7: main() and end-to-end tests

**Files:**
- Modify: `mdtodo.py` — implement `main()`
- Modify: `tests/test_mdtodo.py` — append end-to-end tests via subprocess

- [ ] **Step 1: Write the failing tests**

Append to `tests/test_mdtodo.py`:

```python
import subprocess
import sys


class TestMainEndToEnd(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.NamedTemporaryFile(
            mode='w', suffix='.md', delete=False
        )
        self.path = self.tmp.name
        self.tmp.close()
        os.unlink(self.path)

    def tearDown(self):
        if os.path.exists(self.path):
            os.unlink(self.path)

    def run_cmd(self, *args):
        import os
        env = os.environ.copy()
        env['MDTODO_FILE'] = self.path
        result = subprocess.run(
            [sys.executable, '-m', 'mdtodo'] + list(args),
            capture_output=True, text=True, env=env,
            cwd=os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
        )
        return result.stdout.strip(), result.stderr.strip(), result.returncode

    def test_add_creates_file_and_prints(self):
        out, err, rc = self.run_cmd('add', 'buy milk')
        self.assertEqual(rc, 0)
        self.assertEqual(out, 'Added #1: buy milk')
        self.assertTrue(os.path.exists(self.path))

    def test_list_empty_prints_nothing(self):
        out, err, rc = self.run_cmd('list')
        self.assertEqual(rc, 0)
        self.assertEqual(out, '')

    def test_add_then_list(self):
        self.run_cmd('add', 'task one')
        self.run_cmd('add', 'task two')
        out, err, rc = self.run_cmd('list')
        self.assertEqual(rc, 0)
        self.assertIn('1. task one', out)
        self.assertIn('2. task two', out)

    def test_done_marks_item(self):
        self.run_cmd('add', 'task one')
        self.run_cmd('add', 'task two')
        out, err, rc = self.run_cmd('done', '1')
        self.assertEqual(rc, 0)
        self.assertIn('Done #1: task one', out)
        list_out, _, _ = self.run_cmd('list')
        self.assertNotIn('task one', list_out)
        self.assertIn('task two', list_out)

    def test_done_invalid_n_exits_1(self):
        out, err, rc = self.run_cmd('done', '99')
        self.assertEqual(rc, 1)
        self.assertIn('Error: no item #99', err)

    def test_done_non_integer_exits_1(self):
        out, err, rc = self.run_cmd('done', 'abc')
        self.assertEqual(rc, 1)
        self.assertIn('Error: no item #abc', err)

    def test_unknown_command_exits_1(self):
        out, err, rc = self.run_cmd('foobar')
        self.assertEqual(rc, 1)
        self.assertIn('foobar', err)

    def test_no_args_exits_1(self):
        out, err, rc = self.run_cmd()
        self.assertEqual(rc, 1)

    def test_full_scenario_from_brief(self):
        """Validates the exact scenario in BRIEF.md."""
        self.run_cmd('add', '랩 01 README 읽기')
        self.run_cmd('add', 'Superpowers 설치')
        self.run_cmd('add', '랩 02 진행')
        list_out, _, rc = self.run_cmd('list')
        self.assertEqual(rc, 0)
        self.assertIn('1. 랩 01 README 읽기', list_out)
        self.assertIn('2. Superpowers 설치', list_out)
        self.assertIn('3. 랩 02 진행', list_out)
        done_out, _, rc = self.run_cmd('done', '2')
        self.assertEqual(rc, 0)
        self.assertIn('Done #2: Superpowers 설치', done_out)
        list_out2, _, _ = self.run_cmd('list')
        self.assertIn('1. 랩 01 README 읽기', list_out2)
        self.assertIn('2. 랩 02 진행', list_out2)
        self.assertNotIn('Superpowers 설치', list_out2)
```

- [ ] **Step 2: Run tests to verify they fail**

```bash
python3 -m unittest tests.test_mdtodo.TestMainEndToEnd -v
```

Expected: errors with `NotImplementedError` from `main()`

- [ ] **Step 3: Implement `main()` in `mdtodo.py`**

```python
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
```

- [ ] **Step 4: Run all tests and verify they pass**

```bash
python3 -m unittest discover -s tests -v
```

Expected: all tests `OK`

- [ ] **Step 5: Commit**

```bash
git add mdtodo.py tests/test_mdtodo.py
git commit -m "feat: implement main() and end-to-end tests"
```

---

### Task 8: Update README

**Files:**
- Modify: `README.md` — ensure content is ≤ 30 lines

- [ ] **Step 1: Verify README is ≤ 30 lines and accurate**

The existing `README.md` already documents the commands. Verify it's complete and accurate. If changes are needed, the README should cover:
- One-line description
- Install/run instructions (`python3 -m mdtodo`)
- All three commands with examples
- `MDTODO_FILE` env var
- Todo line format

- [ ] **Step 2: Commit if changed**

```bash
git add README.md
git commit -m "docs: update README"
```

---

### Final Verification

- [ ] Run full test suite:

```bash
python3 -m unittest discover -s tests -v
```

Expected: all tests pass, exit 0.
