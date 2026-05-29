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
    return path.read_text(encoding="utf-8").splitlines(keepends=True)


def write_lines(path, lines):
    path.write_text("".join(lines), encoding="utf-8")


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
