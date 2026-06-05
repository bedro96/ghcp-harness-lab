# tests/test_mdtodo.py
import unittest
import tempfile
import os
from mdtodo import parse, serialize, TodoItem, RawLine, load_file, save_file, cmd_list


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



if __name__ == '__main__':
    unittest.main()
