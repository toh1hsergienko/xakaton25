import flet as ft
import os
import webbrowser

def main(page: ft.Page):
    # Настройки страницы
    page.title = "City Routes"
    page.theme_mode = ft.ThemeMode.LIGHT
    page.padding = 0
    page.bgcolor = ft.colors.BLUE_GREY_50
    
    # Переменные состояния
    user_nickname = ""
    menu_open = False
    
    # Элементы интерфейса
    
    # Стартовая страница
    nickname_field = ft.TextField(
        label="Введите ваш ник",
        width=300,
        border_color=ft.colors.BLUE_400
    )
    
    start_button = ft.ElevatedButton(
        "Построить первый маршрут",
        on_click=lambda e: show_map_page(),
        bgcolor=ft.colors.BLUE,
        color=ft.colors.WHITE,
        style=ft.ButtonStyle(
            shape=ft.RoundedRectangleBorder(radius=10)
        )
    )
    
    start_page = ft.Container(
        content=ft.Column([
            ft.Container(height=100),
            ft.Icon(
                name=ft.icons.LOCATION_ON,
                size=80,
                color=ft.colors.BLUE
            ),
            ft.Text(
                "Постройте свой\nпервый маршрут!",
                size=32,
                weight=ft.FontWeight.BOLD,
                text_align=ft.TextAlign.CENTER,
                color=ft.colors.BLUE_900
            ),
            ft.Container(height=30),
            nickname_field,
            ft.Container(height=20),
            start_button
        ],
        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        alignment=ft.MainAxisAlignment.CENTER
        ),
        padding=20,
        alignment=ft.alignment.center
    )
    
    # Кнопка меню
    menu_button = ft.IconButton(
        icon=ft.icons.MENU,
        icon_color=ft.colors.WHITE,
        on_click=lambda e: toggle_menu(),
        style=ft.ButtonStyle(
            bgcolor=ft.colors.BLUE,
            shape=ft.RoundedRectangleBorder(radius=8)
        )
    )
    
    # Меню (диалоговое окно)
    menu_dialog = ft.AlertDialog(
        modal=True,
        title=ft.Text("Интересные места"),
        content=ft.Column([
            ft.Checkbox(label="Развлечения", value=False),
            ft.Checkbox(label="Спорт", value=False),
            ft.Checkbox(label="18+", value=False),
            ft.Checkbox(label="Туристическая инфраструктура", value=False),
        ],
        tight=True,
        spacing=15
        ),
        actions=[
            ft.TextButton("Применить", on_click=lambda e: close_menu()),
        ],
        actions_alignment=ft.MainAxisAlignment.END,
    )
    
    # Кастомная панель навигации вместо AppBar
    custom_app_bar = ft.Container(
        content=ft.Row([
            ft.Text("Маршрут", 
                   size=20, 
                   weight=ft.FontWeight.BOLD, 
                   color=ft.colors.WHITE),
            ft.Container(expand=True),  # Пустое пространство
            menu_button
        ],
        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
        vertical_alignment=ft.CrossAxisAlignment.CENTER
        ),
        padding=ft.padding.symmetric(horizontal=15, vertical=10),
        bgcolor=ft.colors.BLUE,
        height=60
    )
    
    # Кнопка для открытия карты в браузере
    open_map_button = ft.ElevatedButton(
        "Открыть карту",
        icon=ft.icons.MAP,
        on_click=lambda e: open_map_in_browser(),
        style=ft.ButtonStyle(
            bgcolor=ft.colors.GREEN,
            color=ft.colors.WHITE
        )
    )
    
    # Страница карты
    map_page = ft.Column([
        custom_app_bar,  # Используем кастомную панель вместо AppBar
        ft.Container(
            content=ft.Column([
                ft.Text(
                    "Карта маршрутов",
                    size=24,
                    weight=ft.FontWeight.BOLD,
                    text_align=ft.TextAlign.CENTER
                ),
                ft.Text(
                    "Нажмите кнопку ниже чтобы открыть интерактивную карту",
                    size=16,
                    text_align=ft.TextAlign.CENTER,
                    color=ft.colors.GREY_600
                ),
                ft.Container(height=20),
                open_map_button,
                ft.Container(height=20),
                ft.Text(
                    "В интерактивной карте вы можете:",
                    size=14,
                    weight=ft.FontWeight.BOLD
                ),
                ft.Column([
                    ft.Text("• Строить маршруты между точками"),
                    ft.Text("• Искать интересные места"),
                    ft.Text("• Сохранять историю маршрутов"),
                ], spacing=5)
            ],
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            alignment=ft.MainAxisAlignment.CENTER
            ),
            padding=30,
            margin=10,
            bgcolor=ft.colors.WHITE,
            border_radius=10,
            expand=True
        )
    ],
    spacing=0,
    expand=True
    )
    
    # Функции
    def show_map_page():
        nonlocal user_nickname
        user_nickname = nickname_field.value.strip()
        
        if not user_nickname:
            nickname_field.error_text = "Пожалуйста, введите ваш ник"
            page.update()
            return
            
        page.controls.clear()
        page.add(map_page)
        page.update()
    
    def toggle_menu():
        nonlocal menu_open
        menu_open = not menu_open
        if menu_open:
            page.dialog = menu_dialog
            menu_dialog.open = True
        else:
            menu_dialog.open = False
        page.update()
    
    def close_menu():
        nonlocal menu_open
        menu_open = False
        menu_dialog.open = False
        page.update()
    
    def open_map_in_browser():
        # Открываем HTML файл в браузере
        html_file_path = os.path.abspath("map.html")
        if os.path.exists(html_file_path):
            webbrowser.open(f"file://{html_file_path}")
        else:
            # Если файла нет, показываем ошибку
            show_error("Файл map.html не найден. Убедитесь, что он находится в той же папке, что и приложение.")
    
    def show_error(message):
        error_dialog = ft.AlertDialog(
            title=ft.Text("Ошибка"),
            content=ft.Text(message),
            actions=[ft.TextButton("OK", on_click=lambda e: close_error())]
        )
        page.dialog = error_dialog
        error_dialog.open = True
        page.update()
        
        def close_error():
            error_dialog.open = False
            page.update()
    
    # Инициализация приложения
    page.add(start_page)

# Запуск приложения
if __name__ == "__main__":
    ft.app(target=main)