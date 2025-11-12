import sys
import shutil

def copy_file(src, dst):
    """Копировать файл"""
    try:
        shutil.copy2(src, dst)
        print(f"Файл '{src}' скопирован в '{dst}'")
    except Exception as e:
        print(f"Ошибка при копировании файла: {e}", file=sys.stderr)