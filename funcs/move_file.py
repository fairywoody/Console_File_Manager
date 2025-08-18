import os
import sys
import shutil

def move_file(src, dst):
    """Переместить файл"""
    try:
        shutil.move(src, dst)
        print(f"Файл '{src}' перемещен в '{dst}'")
    except Exception as e:
        print(f"Ошибка при перемещении файла: {e}", file=sys.stderr)