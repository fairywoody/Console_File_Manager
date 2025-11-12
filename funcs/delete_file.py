import sys
import os


def delete_file(filename):
    """Удалить файл"""
    try:
        if os.path.isdir(filename):
            print(f"'{filename}' является директорией. Используйте команду удаления директории.", file=sys.stderr)
            return
        os.remove(filename)
        print(f"Файл '{filename}' удален")
    except Exception as e:
        print(f"Ошибка при удалении файла: {e}", file=sys.stderr)