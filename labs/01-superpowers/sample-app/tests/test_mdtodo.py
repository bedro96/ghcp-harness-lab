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
