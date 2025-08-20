import unittest
import os
import shutil
import tempfile
from datetime import datetime
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from funcs import count_files, list_files, delete_file, delete_dir, copy_file, move_file, add_date
from io import StringIO


class TestFileManager(unittest.TestCase):
    def setUp(self):
        self.test_dir = tempfile.mkdtemp()
        self.file1 = os.path.join(self.test_dir, 'file1.txt')
        self.file2 = os.path.join(self.test_dir, 'file2.txt')
        self.subdir = os.path.join(self.test_dir, 'subdir')
        self.subfile = os.path.join(self.subdir, 'subfile.txt')

        with open(self.file1, 'w') as f:
            f.write('test content')
        with open(self.file2, 'w') as f:
            f.write('test content')
        os.makedirs(self.subdir)
        with open(self.subfile, 'w') as f:
            f.write('test content')

        self.creation_time = datetime.now().strftime("%Y-%m-%d")

    def DeleteTestDir(self):
        shutil.rmtree(self.test_dir)

    def test_count_files(self):
        self.assertEqual(count_files.count_files(self.test_dir), 3)
        self.assertEqual(count_files.count_files(self.subdir), 1)
        self.assertEqual(count_files.count_files(self.test_dir, count_dirs=True), 4)
        self.assertEqual(count_files.count_files(self.subdir, count_dirs=True), 1)

    def test_list_files(self):
        sys.stdout = StringIO()
        list_files.list_directory(self.test_dir)
        output = sys.stdout.getvalue()
        sys.stdout = sys.__stdout__
        self.assertIn('file1.txt', output)
        self.assertIn('file2.txt', output)

        sys.stderr = StringIO()
        list_files.list_directory('/invalid/path')
        error_output = sys.stderr.getvalue()
        sys.stderr = sys.__stderr__
        self.assertIn('Ошибка', error_output)
        self.assertIn('Системе не удается найти указанный путь', error_output)

        hidden_file = os.path.join(self.test_dir, '.hidden')
        with open(hidden_file, 'w') as f:
            f.write('test')

        sys.stdout = StringIO()
        list_files.list_directory(self.test_dir)
        output = sys.stdout.getvalue()
        sys.stdout = sys.__stdout__
        self.assertNotIn('.hidden', output)

        sys.stdout = StringIO()
        list_files.list_directory(self.test_dir, show_hidden=True)
        output = sys.stdout.getvalue()
        sys.stdout = sys.__stdout__
        self.assertIn('.hidden', output)

        sys.stdout = StringIO()
        list_files.list_directory(self.test_dir, long_format=True)
        output = sys.stdout.getvalue()
        sys.stdout = sys.__stdout__
        self.assertIn('file1.txt', output)
        self.assertIn('rw', output)

    def test_delete_file(self):
        self.assertTrue(os.path.exists(self.file1))
        delete_file.delete_file(self.file1)
        self.assertFalse(os.path.exists(self.file1))

        non_existent_file = os.path.join(self.test_dir, 'non_existent.txt')

        original_stderr = sys.stderr
        sys.stderr = StringIO()

        delete_file.delete_file(non_existent_file)

        stderr_output = sys.stderr.getvalue()
        sys.stderr = original_stderr

        self.assertIn('Ошибка при удалении файла', stderr_output)

        original_stderr = sys.stderr
        sys.stderr = StringIO()

        delete_file.delete_file(self.subdir)

        stderr_output = sys.stderr.getvalue()
        sys.stderr = original_stderr

        self.assertIn('является директорией', stderr_output)
        self.assertTrue(os.path.exists(self.subdir))

    def test_delete_dir(self):
        empty_dir = os.path.join(self.test_dir, 'empty_dir')
        os.makedirs(empty_dir)

        old_stdout = sys.stdout
        sys.stdout = StringIO()

        delete_dir.delete_directory(empty_dir)

        output = sys.stdout.getvalue()
        sys.stdout = old_stdout

        self.assertFalse(os.path.exists(empty_dir))
        self.assertIn('удалена', output)

        nested_dir = os.path.join(self.test_dir, 'nested_dir')
        os.makedirs(nested_dir)
        with open(os.path.join(nested_dir, 'test.txt'), 'w') as f:
            f.write('test')

        sys.stdout = StringIO()
        delete_dir.delete_directory(nested_dir, recursive=True)
        output = sys.stdout.getvalue()
        sys.stdout = old_stdout

        self.assertFalse(os.path.exists(nested_dir))
        self.assertIn('удалена', output)

        non_empty_dir = os.path.join(self.test_dir, 'non_empty_dir')
        os.makedirs(non_empty_dir)
        with open(os.path.join(non_empty_dir, 'test.txt'), 'w') as f:
            f.write('test')

        old_stderr = sys.stderr
        sys.stderr = StringIO()

        delete_dir.delete_directory(non_empty_dir)

        error_output = sys.stderr.getvalue()
        sys.stderr = old_stderr

        self.assertTrue(os.path.exists(non_empty_dir))
        self.assertIn('Папка не пуста', error_output)

        non_existent_dir = os.path.join(self.test_dir, 'non_existent')

        sys.stderr = StringIO()
        delete_dir.delete_directory(non_existent_dir)
        error_output = sys.stderr.getvalue()
        sys.stderr = old_stderr

        self.assertIn('Не удается найти указанный файл', error_output)

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