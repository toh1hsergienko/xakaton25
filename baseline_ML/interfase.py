import flet as ft
import os
import webbrowser
from flet import colors

def main(page: ft.Page):
    # Настройки страницы
    page.title = "City Routes"
    page.theme_mode = ft.ThemeMode.LIGHT
    page.padding = 0
    page.bgcolor = ft.colors.BLUE_GREY_50
    
    # Переменные состояния
    user_nickname = ""
    menu_open = False
    selected_tab = 0
    
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
    
    # Поисковая строка для меню
    search_field = ft.TextField(
        label="Поиск мест и маршрутов",
        prefix_icon=ft.icons.SEARCH,
        border_color=ft.colors.BLUE_400,
        filled=True,
        bgcolor=ft.colors.BLUE_GREY_50,
        expand=True
    )
    
    # Содержимое вкладок
    # Вкладка Категория
    category_content = ft.Column([
        ft.Checkbox(label="Интересные места", value=False),
        ft.Checkbox(label="Развлечения", value=False),
        ft.Checkbox(label="Спорт", value=False),
        ft.Checkbox(label="18+", value=False),
        ft.Checkbox(label="Туристическая инфраструктура", value=False),
    ], spacing=10, scroll=ft.ScrollMode.ADAPTIVE)
    
    # Вкладка Маршрут
    route_content = ft.Column([
        ft.ListTile(
            title=ft.Text("Текущий маршрут"),
            subtitle=ft.Text("Просмотр активного маршрута"),
            leading=ft.Icon(ft.icons.ROUTE),
            on_click=lambda e: print("Текущий маршрут")
        ),
        ft.ListTile(
            title=ft.Text("Новый маршрут"),
            subtitle=ft.Text("Создать новый маршрут"),
            leading=ft.Icon(ft.icons.ADD_ROAD),
            on_click=lambda e: print("Новый маршрут")
        ),
        ft.ListTile(
            title=ft.Text("Сохранить маршрут"),
            subtitle=ft.Text("Сохранить текущий маршрут"),
            leading=ft.Icon(ft.icons.SAVE),
            on_click=lambda e: print("Сохранить маршрут")
        ),
    ], spacing=5, scroll=ft.ScrollMode.ADAPTIVE)
    
    # Вкладка Маршруты пользователей
    user_routes_content = ft.Column([
        # Заголовок
        ft.Container(
            content=ft.Text("Популярные маршруты", size=18, weight=ft.FontWeight.BOLD),
            padding=10,
            alignment=ft.alignment.center
        ),
        
        # Карточка маршрута 1
        ft.Container(
            content=ft.Column([
                # Верхняя часть - фото и информация о пользователе
                ft.Row([
                    # Фото пользователя
                    ft.Container(
                        content=ft.CircleAvatar(
                            foreground_image_url="https://images.unsplash.com/photo-1472099645785-5658abf4ff4e?w=150",
                            radius=25,
                        ),
                        margin=ft.margin.only(right=10)
                    ),
                    # Информация о пользователе
                    ft.Column([
                        ft.Text("Александр", weight=ft.FontWeight.BOLD, size=16),
                        ft.Row([
                            ft.Icon(ft.icons.STAR, size=16, color=ft.colors.AMBER),
                            ft.Text("4.8", size=14),
                        ], spacing=5)
                    ], alignment=ft.MainAxisAlignment.CENTER, spacing=0),
                    ft.Container(expand=True),
                    # Кнопка подписки
                    ft.OutlinedButton("Подписаться", on_click=lambda e: follow_user(1))
                ], alignment=ft.MainAxisAlignment.START),
                
                # Информация о маршруте
                ft.Container(
                    content=ft.Column([
                        ft.Row([
                            ft.Icon(ft.icons.LOCATION_ON, size=16, color=ft.colors.BLUE),
                            ft.Text("Исторический центр", size=14, weight=ft.FontWeight.BOLD),
                        ], spacing=5),
                        ft.Row([
                            ft.Icon(ft.icons.STRAIGHTEN, size=16, color=ft.colors.GREEN),
                            ft.Text("5.2 км", size=14),
                            ft.Container(width=20),
                            ft.Icon(ft.icons.DIRECTIONS_WALK, size=16, color=ft.colors.ORANGE),
                            ft.Text("Пешком", size=14),
                        ], spacing=5),
                        ft.Text("Прогулка по основным достопримечательностям города", 
                               size=12, color=ft.colors.GREY_600),
                    ], spacing=5),
                    margin=ft.margin.only(top=10)
                ),
                
                # Действия
                ft.Row([
                    ft.TextButton(
                        content=ft.Row([
                            ft.Icon(ft.icons.FAVORITE_BORDER, size=16),
                            ft.Text("125")
                        ], spacing=5),
                        on_click=lambda e: like_route(1)
                    ),
                    ft.Container(expand=True),
                    ft.TextButton(
                        content=ft.Row([
                            ft.Icon(ft.icons.SHARE, size=16),
                            ft.Text("Поделиться")
                        ], spacing=5),
                        on_click=lambda e: share_route(1)
                    ),
                ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN)
            ]),
            padding=15,
            margin=ft.margin.only(bottom=10),
            bgcolor=ft.colors.WHITE,
            border_radius=10
        ),
        
        # Карточка маршрута 2
        ft.Container(
            content=ft.Column([
                # Верхняя часть - фото и информация о пользователе
                ft.Row([
                    # Фото пользователя
                    ft.Container(
                        content=ft.CircleAvatar(
                            foreground_image_url="https://images.unsplash.com/photo-1494790108755-2616b612b786?w=150",
                            radius=25,
                        ),
                        margin=ft.margin.only(right=10)
                    ),
                    # Информация о пользователе
                    ft.Column([
                        ft.Text("Мария", weight=ft.FontWeight.BOLD, size=16),
                        ft.Row([
                            ft.Icon(ft.icons.STAR, size=16, color=ft.colors.AMBER),
                            ft.Text("4.9", size=14),
                        ], spacing=5)
                    ], alignment=ft.MainAxisAlignment.CENTER, spacing=0),
                    ft.Container(expand=True),
                    # Кнопка подписки
                    ft.OutlinedButton("Подписаться", on_click=lambda e: follow_user(2))
                ], alignment=ft.MainAxisAlignment.START),
                
                # Информация о маршруте
                ft.Container(
                    content=ft.Column([
                        ft.Row([
                            ft.Icon(ft.icons.LOCATION_ON, size=16, color=ft.colors.BLUE),
                            ft.Text("Парки и скверы", size=14, weight=ft.FontWeight.BOLD),
                        ], spacing=5),
                        ft.Row([
                            ft.Icon(ft.icons.STRAIGHTEN, size=16, color=ft.colors.GREEN),
                            ft.Text("8.7 км", size=14),
                            ft.Container(width=20),
                            ft.Icon(ft.icons.DIRECTIONS_BIKE, size=16, color=ft.colors.BLUE),
                            ft.Text("На велосипеде", size=14),
                        ], spacing=5),
                        ft.Text("Маршрут через самые живописные парки города", 
                               size=12, color=ft.colors.GREY_600),
                    ], spacing=5),
                    margin=ft.margin.only(top=10)
                ),
                
                # Действия
                ft.Row([
                    ft.TextButton(
                        content=ft.Row([
                            ft.Icon(ft.icons.FAVORITE_BORDER, size=16),
                            ft.Text("89")
                        ], spacing=5),
                        on_click=lambda e: like_route(2)
                    ),
                    ft.Container(expand=True),
                    ft.TextButton(
                        content=ft.Row([
                            ft.Icon(ft.icons.SHARE, size=16),
                            ft.Text("Поделиться")
                        ], spacing=5),
                        on_click=lambda e: share_route(2)
                    ),
                ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN)
            ]),
            padding=15,
            margin=ft.margin.only(bottom=10),
            bgcolor=ft.colors.WHITE,
            border_radius=10
        ),
    ], 
    scroll=ft.ScrollMode.ADAPTIVE,
    spacing=0
    )
    
    # Вкладка Профиль
    profile_content = ft.Column([
        # Заголовок профиля
        ft.Container(
            content=ft.Column([
                # Аватар пользователя
                ft.Container(
                    content=ft.CircleAvatar(
                        foreground_image_url="https://via.placeholder.com/150",
                        radius=40,
                        content=ft.Icon(ft.icons.PERSON, size=40)
                    ),
                    alignment=ft.alignment.center,
                    margin=ft.margin.only(bottom=10)
                ),
                # Имя пользователя
                ft.Text(
                    user_nickname or "Пользователь",
                    size=20,
                    weight=ft.FontWeight.BOLD,
                    text_align=ft.TextAlign.CENTER
                ),
                # Email или дополнительная информация
                ft.Text(
                    "user@example.com",
                    size=14,
                    color=ft.colors.GREY_600,
                    text_align=ft.TextAlign.CENTER
                ),
            ],
            horizontal_alignment=ft.CrossAxisAlignment.CENTER
            ),
            padding=20,
            bgcolor=ft.colors.WHITE,
            border_radius=10,
            margin=ft.margin.only(bottom=10)
        ),
        
        # Раздел "Мои маршруты"
        ft.Container(
            content=ft.Column([
                ft.ListTile(
                    leading=ft.Icon(ft.icons.ROUTE, color=ft.colors.BLUE),
                    title=ft.Text("Мои маршруты", weight=ft.FontWeight.BOLD),
                    trailing=ft.Icon(ft.icons.CHEVRON_RIGHT),
                    on_click=lambda e: show_my_routes()
                ),
                # Примеры маршрутов
                ft.Container(
                    content=ft.Column([
                        ft.ListTile(
                            title=ft.Text("Исторический центр"),
                            subtitle=ft.Text("Создан 12.01.2024"),
                            leading=ft.Icon(ft.icons.PLACE, color=ft.colors.GREEN),
                        ),
                        ft.ListTile(
                            title=ft.Text("Парки и скверы"),
                            subtitle=ft.Text("Создан 10.01.2024"),
                            leading=ft.Icon(ft.icons.PARK, color=ft.colors.GREEN),
                        ),
                    ]),
                    padding=ft.padding.only(left=40)
                )
            ]),
            bgcolor=ft.colors.WHITE,
            border_radius=10,
            margin=ft.margin.only(bottom=10)
        ),
        
        # Раздел "Избранное"
        ft.Container(
            content=ft.Column([
                ft.ListTile(
                    leading=ft.Icon(ft.icons.FAVORITE, color=ft.colors.RED),
                    title=ft.Text("Избранное", weight=ft.FontWeight.BOLD),
                    trailing=ft.Icon(ft.icons.CHEVRON_RIGHT),
                    on_click=lambda e: show_favorites()
                ),
                # Примеры избранного
                ft.Container(
                    content=ft.Column([
                        ft.ListTile(
                            title=ft.Text("Кафе 'Уютное место'"),
                            subtitle=ft.Text("Добавлено в избранное"),
                            leading=ft.Icon(ft.icons.RESTAURANT, color=ft.colors.ORANGE),
                        ),
                        ft.ListTile(
                            title=ft.Text("Музей искусств"),
                            subtitle=ft.Text("Добавлено в избранное"),
                            leading=ft.Icon(ft.icons.ACCOUNT_BALANCE, color=ft.colors.ORANGE),
                        ),
                    ]),
                    padding=ft.padding.only(left=40)
                )
            ]),
            bgcolor=ft.colors.WHITE,
            border_radius=10,
            margin=ft.margin.only(bottom=10)
        ),
        
        # Настройки профиля
        ft.Container(
            content=ft.Column([
                ft.ListTile(
                    leading=ft.Icon(ft.icons.SETTINGS, color=ft.colors.GREY_600),
                    title=ft.Text("Настройки"),
                    trailing=ft.Icon(ft.icons.CHEVRON_RIGHT),
                    on_click=lambda e: show_settings()
                ),
                ft.ListTile(
                    leading=ft.Icon(ft.icons.HELP_OUTLINE, color=ft.colors.GREY_600),
                    title=ft.Text("Помощь"),
                    trailing=ft.Icon(ft.icons.CHEVRON_RIGHT),
                    on_click=lambda e: show_help()
                ),
                ft.ListTile(
                    leading=ft.Icon(ft.icons.LOGOUT, color=ft.colors.RED),
                    title=ft.Text("Выйти", color=ft.colors.RED),
                    trailing=ft.Icon(ft.icons.CHEVRON_RIGHT),
                    on_click=lambda e: logout()
                ),
            ]),
            bgcolor=ft.colors.WHITE,
            border_radius=10
        )
    ], 
    scroll=ft.ScrollMode.ADAPTIVE,
    spacing=0
    )
    
    # Контейнер для содержимого вкладок
    content_container = ft.Container(
        content=category_content,
        padding=10,
        margin=5,
        height=300
    )
    
    # Функция для обновления содержимого вкладки
    def update_tab_content(tab_index):
        if tab_index == 0:
            content_container.content = category_content
        elif tab_index == 1:
            content_container.content = route_content
        elif tab_index == 2:
            content_container.content = user_routes_content
        elif tab_index == 3:
            content_container.content = profile_content
        page.update()
    
    # Вкладки
    tabs = ft.Tabs(
        selected_index=0,
        animation_duration=300,
        tabs=[
            ft.Tab(text="Категория"),
            ft.Tab(text="Маршрут"),
            ft.Tab(text="Сообщество"),
            ft.Tab(text="Профиль"),
        ],
        on_change=lambda e: change_tab(e.control.selected_index),
        expand=True
    )
    
    def change_tab(tab_index):
        nonlocal selected_tab
        selected_tab = tab_index
        update_tab_content(tab_index)
    
    # Меню (диалоговое окно)
    menu_dialog = ft.AlertDialog(
        modal=True,
        title=ft.Row([
            ft.Text("Меню", size=20, weight=ft.FontWeight.BOLD),
            ft.Container(expand=True),
            ft.IconButton(
                icon=ft.icons.CLOSE,
                on_click=lambda e: close_menu(),
            )
        ]),
        content=ft.Column([
            # Поисковая строка
            ft.Row([
                search_field,
            ]),
            ft.Divider(height=10),
            # Вкладки
            tabs,
            # Контейнер с содержимым вкладки
            content_container,
        ],
        height=450,
        scroll=ft.ScrollMode.ADAPTIVE
        ),
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
    
    # ВСТРОЕННАЯ КАРТА В ПРИЛОЖЕНИИ
    map_content = ft.Container(
        content=ft.Column([
            # Панель управления картой
            ft.Container(
                content=ft.Row([
                    ft.TextField(
                        label="Откуда",
                        prefix_icon=ft.icons.LOCATION_ON,
                        width=140,
                        border_color=ft.colors.BLUE_400
                    ),
                    ft.TextField(
                        label="Куда",
                        prefix_icon=ft.icons.FLAG,
                        width=140,
                        border_color=ft.colors.BLUE_400
                    ),
                    ft.IconButton(
                        icon=ft.icons.SEARCH,
                        icon_color=ft.colors.WHITE,
                        bgcolor=ft.colors.BLUE,
                        on_click=lambda e: search_route()
                    )
                ], spacing=10),
                padding=15,
                bgcolor=ft.colors.WHITE,
                border_radius=10,
                margin=ft.margin.only(bottom=10)
            ),
            
            # Заглушка карты (в реальном приложении здесь будет настоящая карта)
            ft.Container(
                content=ft.Column([
                    ft.Icon(ft.icons.MAP, size=80, color=ft.colors.BLUE_300),
                    ft.Text("Интерактивная карта", size=20, weight=ft.FontWeight.BOLD),
                    ft.Text("Здесь будет отображаться ваш маршрут", size=14, color=ft.colors.GREY_600),
                    ft.Container(height=20),
                    ft.ElevatedButton(
                        "Построить маршрут",
                        icon=ft.icons.ROUTE,
                        on_click=lambda e: build_route(),
                        style=ft.ButtonStyle(
                            bgcolor=ft.colors.GREEN,
                            color=ft.colors.WHITE
                        )
                    )
                ],
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                alignment=ft.MainAxisAlignment.CENTER
                ),
                bgcolor=ft.colors.WHITE,
                border_radius=10,
                padding=20,
                expand=True
            ),
            
            # Панель действий
            ft.Container(
                content=ft.Row([
                    ft.ElevatedButton(
                        "Сохранить маршрут",
                        icon=ft.icons.SAVE,
                        on_click=lambda e: save_route()
                    ),
                    ft.Container(expand=True),
                    ft.ElevatedButton(
                        "Поделиться",
                        icon=ft.icons.SHARE,
                        on_click=lambda e: share_current_route(),
                        bgcolor=ft.colors.BLUE,
                        color=ft.colors.WHITE
                    )
                ]),
                padding=15,
                bgcolor=ft.colors.WHITE,
                border_radius=10,
                margin=ft.margin.only(top=10)
            )
        ]),
        padding=15,
        expand=True
    )
    
    # Страница карты
    map_page = ft.Column([
        custom_app_bar,
        map_content
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
            
        # Обновляем информацию в профиле
        update_profile_username()
            
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
    
    # Новые функции для профиля
    def update_profile_username():
        """Обновляет имя пользователя в профиле"""
        if hasattr(profile_content.controls[0].content, 'controls'):
            profile_content.controls[0].content.controls[1].value = user_nickname or "Пользователь"
    
    def show_my_routes():
        close_menu()
        print("Показать мои маршруты")
    
    def show_favorites():
        close_menu()
        print("Показать избранное")
    
    def show_settings():
        close_menu()
        print("Открыть настройки")
    
    def show_help():
        close_menu()
        page.dialog = ft.AlertDialog(
            title=ft.Text("Помощь"),
            content=ft.Text("Здесь будет раздел помощи"),
            actions=[ft.TextButton("OK", on_click=lambda e: close_help())]
        )
        page.dialog.open = True
        page.update()
        
        def close_help():
            page.dialog.open = False
            page.update()
    
    def logout():
        close_menu()
        print("Выход из аккаунта")
    
    # Функции для вкладки "Сообщество"
    def follow_user(user_id):
        print(f"Подписка на пользователя {user_id}")
    
    def like_route(route_id):
        print(f"Лайк маршрута {route_id}")
    
    def share_route(route_id):
        print(f"Поделиться маршрутом {route_id}")
    
    # Функции для карты
    def search_route():
        print("Поиск маршрута")
        # Здесь будет логика поиска маршрута
    
    def build_route():
        print("Построение маршрута")
        # Здесь будет логика построения маршрута
    
    def save_route():
        print("Сохранение маршрута")
        # Здесь будет логика сохранения маршрута
    
    def share_current_route():
        print("Поделиться текущим маршрутом")
        # Здесь будет логика分享 текущего маршрута
    
    # Инициализация приложения
    page.add(start_page)

# Запуск приложения
if __name__ == "__main__":
    ft.app(target=main, port=5000, view=ft.AppView.WEB_BROWSER)