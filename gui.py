import flet as ft
import os
import subprocess
import sys
from datetime import datetime
import time
import stat


class FileManagerGUI:
    def __init__(self, page: ft.Page):
        self.page = page
        self.current_path = os.getcwd()
        self.selected_items = []
        self.show_detailed_view = False
        self.last_click_time = 0
        self.last_click_item = None
        self.setup_ui()

    def setup_ui(self):
        self.page.title = "Console File Manager"
        self.page.theme_mode = ft.ThemeMode.LIGHT
        self.page.padding = 10
        self.page.window.width = 1200
        self.page.window.height = 800

        self.path_text = ft.Text(self.current_path, size=14, expand=True)
        self.up_button = ft.IconButton(
            icon="arrow_upward",
            tooltip="На уровень выше",
            on_click=self.go_up
        )
        self.refresh_button = ft.IconButton(
            icon="refresh",
            tooltip="Обновить",
            on_click=self.refresh
        )
        self.home_button = ft.IconButton(
            icon="home",
            tooltip="Домашняя директория",
            on_click=self.go_home
        )
        self.back_button = ft.IconButton(
            icon="arrow_back",
            tooltip="Назад",
            on_click=self.go_back
        )
        self.forward_button = ft.IconButton(
            icon="arrow_forward",
            tooltip="Вперед",
            on_click=self.go_forward
        )

        self.navigation_history = []
        self.navigation_future = []
        self.navigation_index = -1

        self.delete_btn = ft.ElevatedButton(
            "Удалить",
            icon="delete",
            on_click=self.delete_item,
            disabled=True
        )
        self.copy_btn = ft.ElevatedButton(
            "Копировать",
            icon="content_copy",
            on_click=self.copy_item,
            disabled=True
        )
        self.move_btn = ft.ElevatedButton(
            "Переместить",
            icon="drive_file_move",
            on_click=self.move_item,
            disabled=True
        )
        self.count_btn = ft.ElevatedButton(
            "Подсчет",
            icon="calculate",
            on_click=self.count_files
        )
        self.add_date_btn = ft.ElevatedButton(
            "Добавить дату",
            icon="date_range",
            on_click=self.add_date
        )
        self.details_btn = ft.ElevatedButton(
            "Права и размер",
            icon="info",
            on_click=self.toggle_detailed_view,
            style=ft.ButtonStyle(bgcolor=ft.colors.BLUE_100 if self.show_detailed_view else None)
        )

        self.path_input = ft.TextField(
            label="Путь",
            value=self.current_path,
            on_submit=self.navigate_to_path,
            expand=True
        )
        self.go_button = ft.ElevatedButton(
            "Перейти",
            icon="arrow_forward",
            on_click=lambda e: self.navigate_to_path(e)
        )

        self.file_list = ft.ListView(expand=True)

        self.output_text = ft.TextField(
            label="Вывод команды",
            multiline=True,
            expand=True,
            read_only=True,
            height=150
        )

        self.status_text = ft.Text("Готово", size=12)

        self.page.add(
            ft.Row([
                self.back_button,
                self.forward_button,
                self.home_button,
                self.up_button,
                self.refresh_button,
                self.path_text
            ]),
            ft.Row([
                self.path_input,
                self.go_button
            ]),
            ft.Divider(),
            ft.Row([
                self.delete_btn,
                self.copy_btn,
                self.move_btn,
                self.count_btn,
                self.add_date_btn,
                self.details_btn
            ], wrap=True),
            ft.Divider(),
            ft.Container(
                self.file_list,
                border=ft.border.all(1),
                border_radius=5,
                expand=True
            ),
            ft.Divider(),
            self.output_text,
            ft.Divider(),
            self.status_text
        )

        self.refresh()
        self.add_to_history(self.current_path)

    def get_file_permissions(self, filepath):
        try:
            file_stat = os.stat(filepath)
            mode = file_stat.st_mode

            if stat.S_ISDIR(mode):
                file_type = 'd'
            elif stat.S_ISLNK(mode):
                file_type = 'l'
            else:
                file_type = '-'

            permissions = [
                'r' if mode & stat.S_IRUSR else '-',
                'w' if mode & stat.S_IWUSR else '-',
                'x' if mode & stat.S_IXUSR else '-',
                'r' if mode & stat.S_IRGRP else '-',
                'w' if mode & stat.S_IWGRP else '-',
                'x' if mode & stat.S_IXGRP else '-',
                'r' if mode & stat.S_IROTH else '-',
                'w' if mode & stat.S_IWOTH else '-',
                'x' if mode & stat.S_IXOTH else '-'
            ]

            return f"{file_type}{''.join(permissions)}"
        except:
            return "??????????"

    def format_size(self, size_bytes):
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size_bytes < 1024.0:
                return f"{size_bytes:.1f} {unit}"
            size_bytes /= 1024.0
        return f"{size_bytes:.1f} TB"

    def toggle_detailed_view(self, e):
        self.show_detailed_view = not self.show_detailed_view
        self.details_btn.style = ft.ButtonStyle(
            bgcolor="blue100" if self.show_detailed_view else None
        )
        self.refresh()

    def add_to_history(self, path):
        if not self.navigation_history or self.navigation_history[-1] != path:
            self.navigation_history.append(path)
            self.navigation_index = len(self.navigation_history) - 1
            self.navigation_future.clear()

        self.update_navigation_buttons()

    def update_navigation_buttons(self):
        self.back_button.disabled = self.navigation_index <= 0
        self.forward_button.disabled = not self.navigation_future
        self.page.update()

    def go_back(self, e):
        if self.navigation_index > 0:
            self.navigation_future.append(self.current_path)
            self.navigation_index -= 1
            self.current_path = self.navigation_history[self.navigation_index]
            self.selected_items.clear()
            self.refresh()
            self.update_navigation_buttons()

    def go_forward(self, e):
        if self.navigation_future:
            self.add_to_history(self.navigation_future.pop())
            self.current_path = self.navigation_history[self.navigation_index]
            self.selected_items.clear()
            self.refresh()

    def navigate_to_path(self, e):
        path = self.path_input.value.strip()
        if os.path.isdir(path):
            self.change_directory(path)
        else:
            self.output_text.value = f"Ошибка: путь '{path}' не существует или не является директорией"
            self.page.update()

    def change_directory(self, new_path):
        try:
            self.current_path = os.path.abspath(new_path)
            self.add_to_history(self.current_path)
            self.selected_items.clear()
            self.path_input.value = self.current_path
            self.refresh()
        except Exception as e:
            self.output_text.value = f"Ошибка перехода в директорию: {e}"
            self.page.update()

    def refresh(self, e=None):
        self.file_list.controls.clear()
        self.path_text.value = self.current_path
        self.path_input.value = self.current_path

        try:
            items = os.listdir(self.current_path)
            for item in sorted(items):
                full_path = os.path.join(self.current_path, item)
                is_dir = os.path.isdir(full_path)

                item_color = "blue" if is_dir else "black"

                size = ""
                mtime = ""
                permissions = ""

                try:
                    stat_info = os.stat(full_path)
                    size = self.format_size(stat_info.st_size)
                    mtime = datetime.fromtimestamp(stat_info.st_mtime).strftime('%Y-%m-%d %H:%M')
                    permissions = self.get_file_permissions(full_path)
                except:
                    size = "недоступно"
                    permissions = "??????????"

                if self.show_detailed_view:
                    subtitle_text = f"{permissions} | {size} | {mtime}"
                else:
                    subtitle_text = f"{size} | {mtime}"

                list_item = ft.ListTile(
                    leading=ft.Icon("folder" if is_dir else "insert_drive_file", color=item_color),
                    title=ft.Text(item, color=item_color),
                    subtitle=ft.Text(subtitle_text),
                    on_click=lambda e, path=full_path: self.on_item_click(path),
                    data=full_path
                )
                self.file_list.controls.append(list_item)

        except Exception as e:
            self.output_text.value = f"Ошибка чтения директории: {e}"

        self.status_text.value = f"Файлов: {len(self.file_list.controls)} | Выбрано: {len(self.selected_items)} | Режим: {'Подробный' if self.show_detailed_view else 'Обычный'}"
        self.page.update()

    def on_item_click(self, path):
        current_time = time.time()

        if (current_time - self.last_click_time < 0.5 and
                self.last_click_item == path and
                os.path.isdir(path)):
            self.change_directory(path)
            self.last_click_time = 0
            self.last_click_item = None
            return

        if path in self.selected_items:
            self.selected_items.remove(path)
        else:
            self.selected_items.append(path)

        for control in self.file_list.controls:
            if isinstance(control, ft.ListTile):
                control.bgcolor = "blue100" if control.data in self.selected_items else None

        self.delete_btn.disabled = len(self.selected_items) == 0
        self.copy_btn.disabled = len(self.selected_items) == 0
        self.move_btn.disabled = len(self.selected_items) == 0
        self.status_text.value = f"Файлов: {len(self.file_list.controls)} | Выбрано: {len(self.selected_items)} | Режим: {'Подробный' if self.show_detailed_view else 'Обычный'}"

        self.last_click_time = current_time
        self.last_click_item = path

        self.page.update()

    def go_up(self, e):
        parent = os.path.dirname(self.current_path)
        if parent != self.current_path:
            self.change_directory(parent)

    def go_home(self, e):
        self.change_directory(os.path.expanduser("~"))

    def delete_item(self, e):
        if not self.selected_items:
            return

        def confirm_delete(e):
            for item_path in self.selected_items:
                if os.path.isdir(item_path):
                    result = self.run_command(["delete_dir", item_path, "-r"])
                else:
                    result = self.run_command(["delete_file", item_path])
                self.output_text.value += result.stdout + result.stderr + "\n"

            self.selected_items.clear()
            self.refresh()
            self.page.close(dialog)

        dialog = ft.AlertDialog(
            title=ft.Text("Подтверждение удаления"),
            content=ft.Text(f"Удалить {len(self.selected_items)} элементов?"),
            actions=[
                ft.ElevatedButton("Удалить", on_click=confirm_delete),
                ft.OutlinedButton("Отмена", on_click=lambda e: self.page.close(dialog))
            ]
        )
        self.page.open(dialog)

    def copy_item(self, e):
        if not self.selected_items:
            return

        def copy_dialog(e):
            dest_path = dest_field.value
            for item_path in self.selected_items:
                result = self.run_command(["copy", item_path, dest_path])
                self.output_text.value += result.stdout + result.stderr + "\n"

            self.selected_items.clear()
            self.refresh()
            self.page.close(dialog)

        dest_field = ft.TextField(label="Путь назначения", value=self.current_path)
        dialog = ft.AlertDialog(
            title=ft.Text("Копирование файлов"),
            content=dest_field,
            actions=[
                ft.ElevatedButton("Копировать", on_click=copy_dialog),
                ft.OutlinedButton("Отмена", on_click=lambda e: self.page.close(dialog))
            ]
        )
        self.page.open(dialog)

    def move_item(self, e):
        if not self.selected_items:
            return

        def move_dialog(e):
            dest_path = dest_field.value
            for item_path in self.selected_items:
                result = self.run_command(["move", item_path, dest_path])
                self.output_text.value += result.stdout + result.stderr + "\n"

            self.selected_items.clear()
            self.refresh()
            self.page.close(dialog)

        dest_field = ft.TextField(label="Путь назначения", value=self.current_path)
        dialog = ft.AlertDialog(
            title=ft.Text("Перемещение файлов"),
            content=dest_field,
            actions=[
                ft.ElevatedButton("Переместить", on_click=move_dialog),
                ft.OutlinedButton("Отмена", on_click=lambda e: self.page.close(dialog))
            ]
        )
        self.page.open(dialog)

    def count_files(self, e):
        result = self.run_command(["count", self.current_path, "-d"])
        self.output_text.value = result.stdout + result.stderr
        self.page.update()

    def add_date(self, e):
        for item_path in self.selected_items:
            if os.path.isdir(item_path):
                result = self.run_command(["add_date", item_path, "-r"])
            else:
                result = self.run_command(["add_date", item_path])
            self.output_text.value += result.stdout + result.stderr + "\n"

        self.selected_items.clear()
        self.refresh()

    def run_command(self, command_args):
        try:
            command_args = [arg for arg in command_args if arg]

            result = subprocess.run(
                [sys.executable, "manager.py"] + command_args,
                capture_output=True,
                text=True,
                cwd=os.getcwd(),
                timeout=30
            )
            return result
        except subprocess.TimeoutExpired:
            return subprocess.CompletedProcess([], 1, "", "Команда превысила время выполнения")
        except Exception as e:
            return subprocess.CompletedProcess([], 1, "", str(e))


def main(page: ft.Page):
    FileManagerGUI(page)


if __name__ == "__main__":
    ft.app(target=main)