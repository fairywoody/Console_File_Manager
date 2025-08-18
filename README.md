# Console File Manager

Описание:
Простой менеджер для файловой системы
Для просмотра справки используйте ключ -h

Функционал:
    list                Показать содержимое директории
    delete_file         Удалить файл
    delete_dir          Удалить директорию
    copy                Копировать файл
    move                Переместить файл
    count               Подсчитать файлы в директории
    add_date            Добавить дату создания в имя файла

Примеры использования:
Для каждой из функции доступна справка (-h, --help)

python manager.py list <path_to_folder> (Доступные ключи: -a, --all - Показать скрытые файлы,
-a, --all - Показать подробный вывод (анализ) файлов в папке)
python manager.py delete_file <path_to_file>
python manager.py delete_dir <path_to_dir> (Используйте ключ -r если папка не пуска)
python manager.py copy <path_what_to_copy> <path_where_to_copy>
python manager.py move <path_from> <path_where>
python count <path_to_folder> (Используйте ключ -d, если хотите посчитать файлы вместе с папками и подпапками)
python add_date <path_to_file> (Используйте -r и путь к папке для того, чтобы заменились все файлы в папке и подпапках)