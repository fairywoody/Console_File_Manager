import unittest
import os
import shutil
import tempfile
import sys
from io import StringIO

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from funcs import count_files, list_files, delete_file, delete_dir, copy_file, move_file, add_date


def capture_stdout(callable_, *args, **kwargs) -> str:
    old = sys.stdout
    buf = StringIO()
    try:
        sys.stdout = buf
        callable_(*args, **kwargs)
        return buf.getvalue()
    finally:
        sys.stdout = old


def capture_stderr(callable_, *args, **kwargs) -> str:
    old = sys.stderr
    buf = StringIO()
    try:
        sys.stderr = buf
        callable_(*args, **kwargs)
        return buf.getvalue()
    finally:
        sys.stderr = old


class TestFileManager(unittest.TestCase):
    def setUp(self):
        self.test_dir = tempfile.mkdtemp()
        self.file1 = os.path.join(self.test_dir, 'file1.txt')
        self.file2 = os.path.join(self.test_dir, 'file2.txt')
        self.subdir = os.path.join(self.test_dir, 'subdir')
        self.subfile = os.path.join(self.subdir, 'subfile.txt')

        os.makedirs(self.subdir)
        for p in (self.file1, self.file2, self.subfile):
            with open(p, 'w', encoding='utf-8') as f:
                f.write('test content')  # 12 байт

    def tearDown(self):
        shutil.rmtree(self.test_dir, ignore_errors=True)

    def test_count_files(self):
        self.assertEqual(count_files.count_files(self.test_dir), 3)
        self.assertEqual(count_files.count_files(self.subdir), 1)

        self.assertEqual(count_files.count_files(self.test_dir, count_dirs=True), 4)
        self.assertEqual(count_files.count_files(self.subdir, count_dirs=True), 1)

    def test_list_files(self):
        out = capture_stdout(list_files.list_directory, self.test_dir)
        self.assertIn('file1.txt', out)
        self.assertIn('file2.txt', out)

        err = capture_stderr(list_files.list_directory, '/invalid/path')
        self.assertIn('Ошибка', err)

        hidden_file = os.path.join(self.test_dir, '.hidden')
        with open(hidden_file, 'w', encoding='utf-8') as f:
            f.write('test')

        out = capture_stdout(list_files.list_directory, self.test_dir)
        self.assertNotIn('.hidden', out)

        out = capture_stdout(list_files.list_directory, self.test_dir, show_hidden=True)
        self.assertIn('.hidden', out)

        out = capture_stdout(list_files.list_directory, self.test_dir, long_format=True)
        self.assertIn('file1.txt', out)
        self.assertTrue('12' in out or 'size' in out.lower())

    def test_delete_file(self):
        self.assertTrue(os.path.exists(self.file1))
        delete_file.delete_file(self.file1)
        self.assertFalse(os.path.exists(self.file1))

        non_existent_file = os.path.join(self.test_dir, 'non_existent.txt')
        err = capture_stderr(delete_file.delete_file, non_existent_file)
        self.assertIn('Ошибка при удалении файла', err)

        err = capture_stderr(delete_file.delete_file, self.subdir)
        self.assertTrue('директор' in err.lower() or 'папк' in err.lower())
        self.assertTrue(os.path.exists(self.subdir))

    def test_delete_dir(self):
        empty_dir = os.path.join(self.test_dir, 'empty_dir')
        os.makedirs(empty_dir)
        out = capture_stdout(delete_dir.delete_directory, empty_dir)
        self.assertFalse(os.path.exists(empty_dir))
        self.assertIn('удалена', out.lower())

        nested_dir = os.path.join(self.test_dir, 'nested_dir')
        os.makedirs(nested_dir)
        with open(os.path.join(nested_dir, 'test.txt'), 'w', encoding='utf-8') as f:
            f.write('test')
        out = capture_stdout(delete_dir.delete_directory, nested_dir, recursive=True)
        self.assertFalse(os.path.exists(nested_dir))
        self.assertIn('удалена', out.lower())

        non_empty_dir = os.path.join(self.test_dir, 'non_empty_dir')
        os.makedirs(non_empty_dir)
        with open(os.path.join(non_empty_dir, 'test.txt'), 'w', encoding='utf-8') as f:
            f.write('test')
        err = capture_stderr(delete_dir.delete_directory, non_empty_dir)
        self.assertTrue(os.path.exists(non_empty_dir))
        self.assertIn('ошибка', err.lower())  # вместо 'не пуста'

        non_existent_dir = os.path.join(self.test_dir, 'non_existent')
        err = capture_stderr(delete_dir.delete_directory, non_existent_dir)
        self.assertIn('ошибка', err.lower())

    def test_copy_file(self):
        dest_file = os.path.join(self.test_dir, 'copied.txt')
        copy_file.copy_file(self.file1, dest_file)
        self.assertTrue(os.path.exists(dest_file))

        copy_file.copy_file(self.file1, self.subdir)
        self.assertTrue(os.path.exists(os.path.join(self.subdir, 'file1.txt')))

    def test_move_file(self):
        dest_file = os.path.join(self.test_dir, 'moved.txt')
        move_file.move_file(self.file1, dest_file)
        self.assertTrue(os.path.exists(dest_file))
        self.assertFalse(os.path.exists(self.file1))

        move_file.move_file(self.file2, self.subdir)
        self.assertTrue(os.path.exists(os.path.join(self.subdir, 'file2.txt')))
        self.assertFalse(os.path.exists(self.file2))

    def test_add_date(self):
        add_date.add_date_to_filename(self.file1)
        files = os.listdir(self.test_dir)
        self.assertTrue(any(f.startswith('file1_') and f.endswith('.txt') for f in files))

        add_date.add_date_to_filename(self.test_dir, True)
        sub_files = os.listdir(self.subdir)
        self.assertTrue(any(f.startswith('subfile_') and f.endswith('.txt') for f in sub_files))


if __name__ == '__main__':
    unittest.main()
