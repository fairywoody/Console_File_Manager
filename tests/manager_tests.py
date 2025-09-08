import unittest
import os
import shutil
import tempfile
import subprocess
import sys


class TestFileManagerCLI(unittest.TestCase):
    def setUp(self):
        self.test_dir = tempfile.mkdtemp()
        self.script_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                                        'manager.py')

        self.file1 = os.path.join(self.test_dir, 'file1.txt')
        self.file2 = os.path.join(self.test_dir, 'file2.txt')
        self.subdir = os.path.join(self.test_dir, 'subdir')
        self.subfile = os.path.join(self.subdir, 'subfile.txt')

        with open(self.file1, 'w') as f:
            f.write('test content 1')
        with open(self.file2, 'w') as f:
            f.write('test content 2')
        os.makedirs(self.subdir)
        with open(self.subfile, 'w') as f:
            f.write('sub content')

    def tearDown(self):
        shutil.rmtree(self.test_dir)

    def run_command(self, command_args):
        """Запускает команду и возвращает результат"""
        try:
            result = subprocess.run(
                [sys.executable, self.script_path] + command_args,
                capture_output=True,
                text=True,
                cwd=self.test_dir,
                timeout=10
            )
            return result
        except subprocess.TimeoutExpired:
            self.fail("Command timed out")

    def test_list_command(self):
        """Тестирует команду list"""
        result = self.run_command(['list'])
        self.assertEqual(result.returncode, 0)
        self.assertIn('file1.txt', result.stdout)
        self.assertIn('file2.txt', result.stdout)
        self.assertIn('subdir', result.stdout)

    def test_list_with_long_format(self):
        """Тестирует команду list с флагом -l"""
        result = self.run_command(['list', '-l'])
        self.assertEqual(result.returncode, 0)
        self.assertIn('file1.txt', result.stdout)
        self.assertIn('rw', result.stdout)  # Права доступа

    def test_list_with_hidden(self):
        """Тестирует команду list с флагом -a"""
        hidden_file = os.path.join(self.test_dir, '.hidden')
        with open(hidden_file, 'w') as f:
            f.write('hidden')

        result = self.run_command(['list', '-a'])
        self.assertEqual(result.returncode, 0)
        self.assertIn('.hidden', result.stdout)

    def test_delete_file_command(self):
        """Тестирует команду delete_file"""
        result = self.run_command(['delete_file', 'file1.txt'])
        self.assertEqual(result.returncode, 0)
        self.assertIn('удален', result.stdout)
        self.assertFalse(os.path.exists(self.file1))

    def test_delete_directory_command(self):
        """Тестирует команду delete_dir"""
        empty_dir = os.path.join(self.test_dir, 'empty_dir')
        os.makedirs(empty_dir)

        result = self.run_command(['delete_dir', 'empty_dir'])
        self.assertEqual(result.returncode, 0)
        self.assertIn('удалена', result.stdout)
        self.assertFalse(os.path.exists(empty_dir))

    def test_delete_directory_recursive(self):
        """Тестирует команду delete_dir с рекурсивным удалением"""
        result = self.run_command(['delete_dir', 'subdir', '--recursive'])
        self.assertEqual(result.returncode, 0)
        self.assertIn('удалена', result.stdout)
        self.assertFalse(os.path.exists(self.subdir))

    def test_copy_command(self):
        """Тестирует команду copy"""
        result = self.run_command(['copy', 'file1.txt', 'file1_copy.txt'])
        self.assertEqual(result.returncode, 0)
        self.assertIn('скопирован', result.stdout)
        self.assertTrue(os.path.exists(os.path.join(self.test_dir, 'file1_copy.txt')))

    def test_move_command(self):
        """Тестирует команду move"""
        result = self.run_command(['move', 'file1.txt', 'file1_moved.txt'])
        self.assertEqual(result.returncode, 0)
        self.assertIn('перемещен', result.stdout)
        self.assertFalse(os.path.exists(self.file1))
        self.assertTrue(os.path.exists(os.path.join(self.test_dir, 'file1_moved.txt')))

    def test_count_command(self):
        """Тестирует команду count"""
        result = self.run_command(['count'])
        self.assertEqual(result.returncode, 0)
        self.assertIn('Всего файлов', result.stdout)
        self.assertIn('3', result.stdout)  # file1.txt, file2.txt, subfile.txt

    def test_count_with_dirs(self):
        """Тестирует команду count с флагом -d"""
        result = self.run_command(['count', '--dirs'])
        self.assertEqual(result.returncode, 0)
        self.assertIn('и директорий', result.stdout)

    def test_add_date_command(self):
        """Тестирует команду add_date"""
        result = self.run_command(['add_date', 'file1.txt'])
        self.assertEqual(result.returncode, 0)
        self.assertIn('Переименован', result.stdout)

        files = os.listdir(self.test_dir)
        renamed_files = [f for f in files if f.startswith('file1_') and f.endswith('.txt')]
        self.assertEqual(len(renamed_files), 1)

    def test_add_date_recursive(self):
        """Тестирует команду add_date с рекурсией"""
        result = self.run_command(['add_date', '.', '--recursive'])
        self.assertEqual(result.returncode, 0)

        sub_files = os.listdir(self.subdir)
        renamed_sub_files = [f for f in sub_files if f.startswith('subfile_') and f.endswith('.txt')]
        self.assertEqual(len(renamed_sub_files), 1)

    def test_invalid_command(self):
        """Тестирует обработку неверной команды"""
        result = self.run_command(['invalid_command'])
        self.assertNotEqual(result.returncode, 0)
        self.assertIn('error', result.stderr.lower())

    def test_missing_arguments(self):
        """Тестирует обработку отсутствующих аргументов"""
        result = self.run_command(['create_file'])  # Нет имени файла
        self.assertNotEqual(result.returncode, 0)
        self.assertIn('error', result.stderr.lower())

    def test_help_command(self):
        """Тестирует вывод справки"""
        result = self.run_command(['--help'])
        self.assertEqual(result.returncode, 0)
        self.assertIn('usage', result.stdout.lower())
        self.assertIn('help', result.stdout.lower())


if __name__ == '__main__':
    unittest.main()