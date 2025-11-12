import sys
import os

def count_files(path, count_dirs=False):
    """Рекурсивно подсчитать количество файлов в директории"""
    total = 0
    try:
        for entry in os.scandir(path):
            if entry.is_file():
                total += 1
            elif entry.is_dir():
                if count_dirs:
                    total += 1
                total += count_files(entry.path, count_dirs)
        return total
    except Exception as e:
        print(f"Ошибка при подсчете файлов в {path}: {e}", file=sys.stderr)
        return 0