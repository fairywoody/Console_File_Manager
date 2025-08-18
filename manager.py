import argparse
import os
import shutil
import sys
from funcs import list_files, copy_file, delete_file, delete_dir, move_file, count_files, add_date

def main():
    parser = argparse.ArgumentParser(description='Файловый менеджер')
    subparsers = parser.add_subparsers(dest='command', required=True)

    # Команда list_files
    list_parser = subparsers.add_parser('list', help='Показать содержимое директории')
    list_parser.add_argument('path', nargs='?', default='.', help='Путь к директории')
    list_parser.add_argument('-a', '--all', action='store_true', help='Показать скрытые файлы')
    list_parser.add_argument('-l', '--long', action='store_true', help='Подробный вывод')

    # Команда delete file
    delete_file_parser = subparsers.add_parser('delete_file', help='Удалить файл')
    delete_file_parser.add_argument('filename', help='Имя файла')

    # Команда delete directory
    delete_dir_parser = subparsers.add_parser('delete_dir', help='Удалить директорию')
    delete_dir_parser.add_argument('dirname', help='Имя директории')
    delete_dir_parser.add_argument('-r', '--recursive', action='store_true',
                                   help='Рекурсивное удаление (включая поддиректории)')

    # Команда copy
    copy_parser = subparsers.add_parser('copy', help='Копировать файл')
    copy_parser.add_argument('src', help='Исходный файл')
    copy_parser.add_argument('dst', help='Целевой файл/директория')

    # Команда move
    move_parser = subparsers.add_parser('move', help='Переместить файл')
    move_parser.add_argument('src', help='Исходный файл')
    move_parser.add_argument('dst', help='Целевой файл/директория')

    # Команда count
    count_parser = subparsers.add_parser('count', help='Подсчитать файлы в директории')
    count_parser.add_argument('path', nargs='?', default='.', help='Путь к директории')
    count_parser.add_argument('-d', '--dirs', action='store_true',
                              help='Включать директории в подсчет')
    # Команда add_date
    add_date_parser = subparsers.add_parser('add_date', help='Добавить дату создания в имя файла')
    add_date_parser.add_argument('path', help='Файл или директория для обработки')
    add_date_parser.add_argument('-r', '--recursive', action='store_true',
                               help='Рекурсивная обработка поддиректорий')
    add_date_parser.add_argument('-f', '--format', default="%Y-%m-%d",
                               help='Формат даты (по умолчанию: %%Y-%%m-%%d)')

    args = parser.parse_args()

    if args.command == 'list':
        list_files.list_directory(args.path, args.all, args.long)
    elif args.command == 'delete_file':
        delete_file.delete_file(args.filename)
    elif args.command == 'delete_dir':
        delete_dir.delete_directory(args.dirname, args.recursive)
    elif args.command == 'copy':
        copy_file.copy_file(args.src, args.dst)
    elif args.command == 'move':
        move_file.move_file(args.src, args.dst)
    elif args.command == 'count':
        total = count_files.count_files(args.path, args.dirs)
        print(f"Всего файлов{' и директорий' if args.dirs else ''} в '{args.path}': {total}")
    elif args.command == 'add_date':
        add_date.add_date_to_filename(args.path, args.recursive)

if __name__ == '__main__':
    main()