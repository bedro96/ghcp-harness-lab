# mdtodo Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build `mdtodo`, a standard-library Python CLI that manages a markdown checkbox todo file.

**Architecture:** Use one focused module, `mdtodo.py`, with `main(argv=None)` for CLI dispatch, file helpers for path/read/write behavior, and pure helpers for parsing checkbox lines. Tests drive the public CLI behavior through `main()` while isolating filesystem and environment state.

**Tech Stack:** Python 3.10+, standard library only, `unittest`, `tempfile`, `contextlib`, `io`, `os`, `pathlib`.

---

## File Structure

- `mdtodo.py` — single CLI module runnable with `python3 -m mdtodo`.
- `tests/test_mdtodo.py` — unit tests for command behavior, filesystem behavior, stdout/stderr, and exit codes.
- `README.md` — short usage guide, no more than 30 lines.
- `RETRO.md` — lab retrospective, filled in after review.

---

## Task 1: Add and list behavior

**Files:**
- Create: `tests/test_mdtodo.py`
- Create: `mdtodo.py`

- [ ] **Step 1: Write failing tests for `add`, `list`, and missing files**

Create `tests/test_mdtodo.py`:

```python
import io
import os
import tempfile
import unittest
from pathlib import Path
from unittest import mock

import mdtodo


class CliTestCase(unittest.TestCase):
    def run_cli(self, args, *, todo_file=None, cwd=None):
        stdout = io.StringIO()
        stderr = io.StringIO()
        env = {}
        if todo_file is not None:
            env["MDTODO_FILE"] = str(todo_file)

        with mock.patch.dict(os.environ, env, clear=True):
            with mock.patch("sys.stdout", stdout), mock.patch("sys.stderr", stderr):
                if cwd is None:
                    code = mdtodo.main(args)
                else:
                    old_cwd = os.getcwd()
                    try:
                        os.chdir(cwd)
                        code = mdtodo.main(args)
                    finally:
                        os.chdir(old_cwd)

        return code, stdout.getvalue(), stderr.getvalue()


class AddAndListTests(CliTestCase):
    def test_add_creates_missing_file_and_reports_new_number(self):
        with tempfile.TemporaryDirectory() as tmp:
            todo_file = Path(tmp) / "tasks.md"

            code, stdout, stderr = self.run_cli(
                ["add", "랩 02 진행"],
                todo_file=todo_file,
            )

            self.assertEqual(code, 0)
            self.assertEqual(stdout, "Added #1: 랩 02 진행\n")
            self.assertEqual(stderr, "")
            self.assertEqual(todo_file.read_text(encoding="utf-8"), "- [ ] 랩 02 진행\n")

    def test_add_number_counts_existing_incomplete_items(self):
        with tempfile.TemporaryDirectory() as tmp:
            todo_file = Path(tmp) / "tasks.md"
            todo_file.write_text(
                "- [ ] 랩 01 README 읽기\n- [x] 완료한 일\n- [ ] Superpowers 설치\n",
                encoding="utf-8",
            )

            code, stdout, stderr = self.run_cli(
                ["add", "랩 02 진행"],
                todo_file=todo_file,
            )

            self.assertEqual(code, 0)
            self.assertEqual(stdout, "Added #3: 랩 02 진행\n")
            self.assertEqual(stderr, "")
            self.assertEqual(
                todo_file.read_text(encoding="utf-8"),
                "- [ ] 랩 01 README 읽기\n"
                "- [x] 완료한 일\n"
                "- [ ] Superpowers 설치\n"
                "- [ ] 랩 02 진행\n",
            )

    def test_list_prints_only_incomplete_items_renumbered(self):
        with tempfile.TemporaryDirectory() as tmp:
            todo_file = Path(tmp) / "tasks.md"
            todo_file.write_text(
                "# Tasks\n"
                "- [ ] 랩 01 README 읽기\n"
                "- [x] 완료한 일\n"
                "notes stay in the file\n"
                "- [ ] Superpowers 설치\n",
                encoding="utf-8",
            )

            code, stdout, stderr = self.run_cli(["list"], todo_file=todo_file)

            self.assertEqual(code, 0)
            self.assertEqual(
                stdout,
                "- [ ] 1. 랩 01 README 읽기\n"
                "- [ ] 2. Superpowers 설치\n",
            )
            self.assertEqual(stderr, "")

    def test_list_missing_file_prints_nothing(self):
        with tempfile.TemporaryDirectory() as tmp:
            todo_file = Path(tmp) / "tasks.md"

            code, stdout, stderr = self.run_cli(["list"], todo_file=todo_file)

            self.assertEqual(code, 0)
            self.assertEqual(stdout, "")
            self.assertEqual(stderr, "")
            self.assertFalse(todo_file.exists())


if __name__ == "__main__":
    unittest.main()
```

- [ ] **Step 2: Run tests to verify they fail**

Run:

```bash
python3 -m unittest discover -s tests
```

Expected: FAIL because `mdtodo` does not exist yet.

- [ ] **Step 3: Write minimal implementation for `add` and `list`**

Create `mdtodo.py`:

```python
import os
import sys
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class TodoLine:
    source_index: int
    done: bool
    text: str


def todo_path():
    return Path(os.environ.get("MDTODO_FILE", "./tasks.md"))


def read_lines(path):
    if not path.exists():
        return []
    with path.open(encoding="utf-8", newline="") as file:
        return file.read().splitlines(keepends=True)


def write_lines(path, lines):
    with path.open("w", encoding="utf-8", newline="") as file:
        file.write("".join(lines))


def trailing_newline(line):
    if line.endswith("\r\n"):
        return "\r\n"
    if line.endswith("\n"):
        return "\n"
    if line.endswith("\r"):
        return "\r"
    return ""


def parse_todo_line(index, line):
    body = line.rstrip("\n")
    if body.endswith("\r"):
        body = body[:-1]
    if body.startswith("- [ ] "):
        return TodoLine(index, False, body[len("- [ ] "):])
    if body.startswith("- [x] "):
        return TodoLine(index, True, body[len("- [x] "):])
    return None


def todo_lines(lines):
    parsed = []
    for index, line in enumerate(lines):
        todo = parse_todo_line(index, line)
        if todo is not None:
            parsed.append(todo)
    return parsed


def incomplete_todos(lines):
    return [todo for todo in todo_lines(lines) if not todo.done]


def command_add(text):
    path = todo_path()
    lines = read_lines(path)
    if lines and not lines[-1].endswith("\n"):
        lines[-1] = lines[-1] + "\n"
    lines.append(f"- [ ] {text}\n")
    write_lines(path, lines)
    number = len(incomplete_todos(lines))
    print(f"Added #{number}: {text}")
    return 0


def command_list():
    lines = read_lines(todo_path())
    for number, todo in enumerate(incomplete_todos(lines), start=1):
        print(f"- [ ] {number}. {todo.text}")
    return 0


def main(argv=None):
    if argv is None:
        argv = sys.argv[1:]

    if len(argv) >= 2 and argv[0] == "add":
        return command_add(" ".join(argv[1:]))
    if len(argv) == 1 and argv[0] == "list":
        return command_list()

    print("Usage: mdtodo add TEXT | list | done N", file=sys.stderr)
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
```

- [ ] **Step 4: Run tests to verify they pass**

Run:

```bash
python3 -m unittest discover -s tests
```

Expected: all 4 tests pass.

- [ ] **Step 5: Commit**

```bash
git add mdtodo.py tests/test_mdtodo.py
git commit -m "Add mdtodo add and list commands

Co-authored-by: Copilot <223556219+Copilot@users.noreply.github.com>"
```

---

## Task 2: Done behavior and invalid indexes

**Files:**
- Modify: `tests/test_mdtodo.py`
- Modify: `mdtodo.py`

- [ ] **Step 1: Write failing tests for `done`**

Append the following class inside `tests/test_mdtodo.py`, before the `if __name__ == "__main__":` block:

```python
class DoneTests(CliTestCase):
    def test_done_preserves_crlf_line_endings_when_rewriting_item(self):
        with tempfile.TemporaryDirectory() as tmp:
            todo_file = Path(tmp) / "tasks.md"
            todo_file.write_bytes(b"- [ ] first\r\n- [ ] second\r\n")

            code, stdout, stderr = self.run_cli(["done", "1"], todo_file=todo_file)

            self.assertEqual(code, 0)
            self.assertEqual(stdout, "Done: first\n")
            self.assertEqual(stderr, "")
            self.assertEqual(
                todo_file.read_bytes(),
                b"- [x] first\r\n- [ ] second\r\n",
            )

    def test_done_marks_nth_incomplete_item_and_preserves_other_lines(self):
        with tempfile.TemporaryDirectory() as tmp:
            todo_file = Path(tmp) / "tasks.md"
            todo_file.write_text(
                "# Tasks\n"
                "- [ ] 랩 01 README 읽기\n"
                "- [x] 이미 완료\n"
                "plain note\n"
                "- [ ] Superpowers 설치\n"
                "- [ ] 랩 02 진행\n",
                encoding="utf-8",
            )

            code, stdout, stderr = self.run_cli(["done", "2"], todo_file=todo_file)

            self.assertEqual(code, 0)
            self.assertEqual(stdout, "Done: Superpowers 설치\n")
            self.assertEqual(stderr, "")
            self.assertEqual(
                todo_file.read_text(encoding="utf-8"),
                "# Tasks\n"
                "- [ ] 랩 01 README 읽기\n"
                "- [x] 이미 완료\n"
                "plain note\n"
                "- [x] Superpowers 설치\n"
                "- [ ] 랩 02 진행\n",
            )

    def test_done_then_list_renumbers_remaining_incomplete_items(self):
        with tempfile.TemporaryDirectory() as tmp:
            todo_file = Path(tmp) / "tasks.md"
            todo_file.write_text(
                "- [ ] 랩 01 README 읽기\n"
                "- [ ] Superpowers 설치\n"
                "- [ ] 랩 02 진행\n",
                encoding="utf-8",
            )

            done_code, done_stdout, done_stderr = self.run_cli(["done", "2"], todo_file=todo_file)
            list_code, list_stdout, list_stderr = self.run_cli(["list"], todo_file=todo_file)

            self.assertEqual(done_code, 0)
            self.assertEqual(done_stdout, "Done: Superpowers 설치\n")
            self.assertEqual(done_stderr, "")
            self.assertEqual(list_code, 0)
            self.assertEqual(
                list_stdout,
                "- [ ] 1. 랩 01 README 읽기\n"
                "- [ ] 2. 랩 02 진행\n",
            )
            self.assertEqual(list_stderr, "")

    def test_done_rejects_non_integer_index(self):
        with tempfile.TemporaryDirectory() as tmp:
            todo_file = Path(tmp) / "tasks.md"
            todo_file.write_text("- [ ] one\n", encoding="utf-8")

            code, stdout, stderr = self.run_cli(["done", "abc"], todo_file=todo_file)

            self.assertEqual(code, 1)
            self.assertEqual(stdout, "")
            self.assertEqual(stderr, "Invalid todo number: abc\n")
            self.assertEqual(todo_file.read_text(encoding="utf-8"), "- [ ] one\n")

    def test_done_rejects_out_of_range_index(self):
        with tempfile.TemporaryDirectory() as tmp:
            todo_file = Path(tmp) / "tasks.md"
            todo_file.write_text("- [ ] one\n", encoding="utf-8")

            code, stdout, stderr = self.run_cli(["done", "2"], todo_file=todo_file)

            self.assertEqual(code, 1)
            self.assertEqual(stdout, "")
            self.assertEqual(stderr, "Invalid todo number: 2\n")
            self.assertEqual(todo_file.read_text(encoding="utf-8"), "- [ ] one\n")

    def test_done_missing_file_is_invalid_index(self):
        with tempfile.TemporaryDirectory() as tmp:
            todo_file = Path(tmp) / "tasks.md"

            code, stdout, stderr = self.run_cli(["done", "1"], todo_file=todo_file)

            self.assertEqual(code, 1)
            self.assertEqual(stdout, "")
            self.assertEqual(stderr, "Invalid todo number: 1\n")
            self.assertFalse(todo_file.exists())
```

- [ ] **Step 2: Run tests to verify the new tests fail**

Run:

```bash
python3 -m unittest discover -s tests
```

Expected: FAIL because `done` is not yet implemented.

- [ ] **Step 3: Implement `done N` in `mdtodo.py`**

Add the following functions before `main()` in `mdtodo.py`:

```python
def invalid_number(raw_number):
    print(f"Invalid todo number: {raw_number}", file=sys.stderr)
    return 1


def command_done(raw_number):
    try:
        number = int(raw_number)
    except ValueError:
        return invalid_number(raw_number)

    if number < 1:
        return invalid_number(raw_number)

    path = todo_path()
    lines = read_lines(path)
    incomplete = incomplete_todos(lines)
    if number > len(incomplete):
        return invalid_number(raw_number)

    todo = incomplete[number - 1]
    original_line = lines[todo.source_index]
    lines[todo.source_index] = f"- [x] {todo.text}{trailing_newline(original_line)}"
    write_lines(path, lines)
    print(f"Done: {todo.text}")
    return 0
```

Then update `main()` to handle the `done` command:

```python
def main(argv=None):
    if argv is None:
        argv = sys.argv[1:]

    if len(argv) >= 2 and argv[0] == "add":
        return command_add(" ".join(argv[1:]))
    if len(argv) == 1 and argv[0] == "list":
        return command_list()
    if len(argv) == 2 and argv[0] == "done":
        return command_done(argv[1])

    print("Usage: mdtodo add TEXT | list | done N", file=sys.stderr)
    return 1
```

- [ ] **Step 4: Run tests to verify they all pass**

Run:

```bash
python3 -m unittest discover -s tests
```

Expected: all 10 tests pass.

- [ ] **Step 5: Commit**

```bash
git add mdtodo.py tests/test_mdtodo.py
git commit -m "Add mdtodo done command

Co-authored-by: Copilot <223556219+Copilot@users.noreply.github.com>"
```

---

## Task 3: Default path, command shape, and module execution

**Files:**
- Modify: `tests/test_mdtodo.py`
- Modify: `mdtodo.py`

- [ ] **Step 1: Write tests for default path and CLI shape**

Append the following class inside `tests/test_mdtodo.py`, before the `if __name__ == "__main__":` block:

```python
class PathAndCliTests(CliTestCase):
    def test_default_path_is_tasks_md_in_current_directory(self):
        with tempfile.TemporaryDirectory() as tmp:
            code, stdout, stderr = self.run_cli(
                ["add", "default path task"],
                cwd=tmp,
            )

            self.assertEqual(code, 0)
            self.assertEqual(stdout, "Added #1: default path task\n")
            self.assertEqual(stderr, "")
            self.assertEqual(
                (Path(tmp) / "tasks.md").read_text(encoding="utf-8"),
                "- [ ] default path task\n",
            )

    def test_no_arguments_prints_usage_to_stderr(self):
        code, stdout, stderr = self.run_cli([])

        self.assertEqual(code, 1)
        self.assertEqual(stdout, "")
        self.assertEqual(stderr, "Usage: mdtodo add TEXT | list | done N\n")

    def test_add_without_text_prints_usage_to_stderr(self):
        code, stdout, stderr = self.run_cli(["add"])

        self.assertEqual(code, 1)
        self.assertEqual(stdout, "")
        self.assertEqual(stderr, "Usage: mdtodo add TEXT | list | done N\n")

    def test_done_with_extra_argument_prints_usage_to_stderr(self):
        code, stdout, stderr = self.run_cli(["done", "1", "extra"])

        self.assertEqual(code, 1)
        self.assertEqual(stdout, "")
        self.assertEqual(stderr, "Usage: mdtodo add TEXT | list | done N\n")
```

- [ ] **Step 2: Run tests to verify they pass**

Run:

```bash
python3 -m unittest discover -s tests
```

Expected: all 14 tests pass. If any fail, the command shape or default path logic in `main()` needs adjustment.

- [ ] **Step 3: Commit**

```bash
git add mdtodo.py tests/test_mdtodo.py
git commit -m "Cover mdtodo path and usage behavior

Co-authored-by: Copilot <223556219+Copilot@users.noreply.github.com>"
```

---

## Task 4: README

**Files:**
- Create: `README.md`

- [ ] **Step 1: Create the short README**

Create `README.md`:

```markdown
# mdtodo

Small Python CLI for managing markdown checkbox todos.

## Usage

```bash
python3 -m mdtodo add "랩 02 진행"
python3 -m mdtodo list
python3 -m mdtodo done 2
```

By default, `mdtodo` reads and writes `./tasks.md`.
Set `MDTODO_FILE` to use another file:

```bash
MDTODO_FILE=/tmp/tasks.md python3 -m mdtodo list
```

Todo lines use markdown checkbox syntax:

```markdown
- [ ] incomplete task
- [x] completed task
```

`list` shows only incomplete items and renumbers them from 1.
```

- [ ] **Step 2: Verify README length is ≤ 30 lines**

Run:

```bash
python3 -c "
from pathlib import Path
lines = Path('README.md').read_text(encoding='utf-8').splitlines()
print(len(lines))
raise SystemExit(0 if len(lines) <= 30 else 1)
"
```

Expected: prints a number ≤ 30 and exits 0.

- [ ] **Step 3: Run the full test suite**

Run:

```bash
python3 -m unittest discover -s tests
```

Expected: all 14 tests pass.

- [ ] **Step 4: Commit**

```bash
git add README.md
git commit -m "Add mdtodo README

Co-authored-by: Copilot <223556219+Copilot@users.noreply.github.com>"
```

---

## Task 5: Retrospective and final verification

**Files:**
- Create: `RETRO.md`

- [ ] **Step 1: Create the lab retrospective**

Create `RETRO.md`:

```markdown
# mdtodo Retrospective

## What worked

- Brainstorming clarified ambiguous `done` output before implementation.
- The small layered design kept CLI behavior and parsing easy to test.
- TDD gave quick feedback for file handling and index edge cases.

## Most useful skill

The brainstorming skill was most useful because it converted a short brief into
explicit command behavior, missing-file behavior, and preservation rules.

## Follow-up

No follow-up features are needed for this lab. Due dates, priorities, remote
sync, and TUI behavior remain out of scope.
```

- [ ] **Step 2: Run final verification**

Run:

```bash
python3 -m unittest discover -s tests
```

Expected: all 14 tests pass.

- [ ] **Step 3: Check all required files exist**

Run:

```bash
python3 -c "
from pathlib import Path
required = ['DESIGN.md', 'PLAN.md', 'RETRO.md', 'README.md', 'mdtodo.py', 'tests/test_mdtodo.py']
missing = [name for name in required if not Path(name).exists()]
if missing:
    print('Missing:', ', '.join(missing))
    raise SystemExit(1)
print('All required files exist')
"
```

Expected: prints `All required files exist`.

- [ ] **Step 4: Commit**

```bash
git add RETRO.md
git commit -m "Add mdtodo retrospective

Co-authored-by: Copilot <223556219+Copilot@users.noreply.github.com>"
```

---

## Self-Review

- **Spec coverage:** Tasks cover `MDTODO_FILE`, default `./tasks.md`, markdown checkbox parsing, `add`, `list`, `done`, invalid `N`, preservation of non-todo markdown, CRLF line endings, README ≤ 30 lines, DESIGN.md, PLAN.md, and RETRO.md.
- **Placeholder scan:** No unresolved placeholders in this plan.
- **Type consistency:** All tasks consistently use `main(argv=None)`, `TodoLine`, `todo_path()`, `read_lines()`, `write_lines()`, `trailing_newline()`, `parse_todo_line()`, `todo_lines()`, `incomplete_todos()`, `invalid_number()`, `command_add()`, `command_list()`, and `command_done()`.
