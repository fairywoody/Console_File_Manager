import os
import sys
import shutil


def delete_directory(dirname, recursive=False):
    """Удалить директорию"""
    try:
        if recursive:
            shutil.rmtree(dirname)
        else:
            os.rmdir(dirname)
        print(f"Директория '{dirname}' удалена")
    except Exception as e:
        print(f"Ошибка при удалении директории: {e}", file=sys.stderr)