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
