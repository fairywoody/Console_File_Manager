import os
from datetime import datetime

def list_directory(path, show_hidden=False, long_format=False):
    """Показать содержимое директории"""
    try:
        items = os.listdir(path)
        if not show_hidden:
            items = [item for item in items if not item.startswith('.')]

        if long_format:
            for item in items:
                full_path = os.path.join(path, item)
                stat = os.stat(full_path)
                size = stat.st_size
                mtime = datetime.fromtimestamp(stat.st_mtime).strftime('%Y-%m-%d %H:%M:%S')
                mode = os.stat(full_path).st_mode
                permissions = (
                    'd' if os.path.isdir(full_path) else '-',
                    'r' if mode & 0o400 else '-',
                    'w' if mode & 0o200 else '-',
                    'x' if mode & 0o100 else '-',
                    'r' if mode & 0o040 else '-',
                    'w' if mode & 0o020 else '-',
                    'x' if mode & 0o010 else '-',
                    'r' if mode & 0o004 else '-',
                    'w' if mode & 0o002 else '-',
                    'x' if mode & 0o001 else '-'
                )
                print(f"{''.join(permissions)} {mtime} {size:8} {item}")
        else:
            for item in items:
                print(item)
    except Exception as e:
        print(f"Ошибка при чтении директории: {e}", file=sys.stderr)