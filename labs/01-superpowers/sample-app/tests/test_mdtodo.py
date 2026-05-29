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


if __name__ == "__main__":
    unittest.main()
