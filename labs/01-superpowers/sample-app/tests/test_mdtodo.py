# tests/test_mdtodo.py
import unittest
import tempfile
import os
import subprocess
import sys
from mdtodo import parse, serialize, TodoItem, RawLine, load_file, save_file, cmd_list, cmd_add, cmd_done


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


if __name__ == '__main__':
    unittest.main()
