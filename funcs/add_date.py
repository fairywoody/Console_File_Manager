import os
import sys
from datetime import datetime


def get_creation_date(filepath):
    """Получить дату создания файла"""
    try:
        stat = os.stat(filepath)
        if sys.platform == 'win32':
            return datetime.fromtimestamp(stat.st_ctime)
        else:
            return datetime.fromtimestamp(stat.st_mtime)
    except Exception as e:
        print(f"Ошибка при получении даты создания {filepath}: {e}", file=sys.stderr)
        return datetime.now()


def add_date_to_filename(filepath, recursive=False):
    """Добавить дату создания в название файла"""
    try:
        if os.path.isfile(filepath):
            dirname, filename = os.path.split(filepath)
            basename, ext = os.path.splitext(filename)

            creation_date = get_creation_date(filepath)
            date_str = creation_date.strftime("%Y-%m-%d")

            new_basename = f"{basename}_{date_str}"
            new_filename = f"{new_basename}{ext}"
            new_filepath = os.path.join(dirname, new_filename)

            counter = 1
            while os.path.exists(new_filepath):
                new_basename = f"{basename}_{date_str}_{counter}"
                new_filename = f"{new_basename}{ext}"
                new_filepath = os.path.join(dirname, new_filename)
                counter += 1

            os.rename(filepath, new_filepath)
            print(f"Переименован: {filename} -> {new_filename}")

        elif os.path.isdir(filepath):
            for entry in os.scandir(filepath):
                if entry.is_file():
                    add_date_to_filename(entry.path, False)
                elif recursive and entry.is_dir():
                    add_date_to_filename(entry.path, recursive)

    except Exception as e:
        print(f"Ошибка при обработке {filepath}: {e}", file=sys.stderr)