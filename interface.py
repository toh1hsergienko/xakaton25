import flet as ft
import json
from typing import List, Dict
import requests
import random
from datetime import datetime, timedelta

class UserProfile:
    def __init__(self, username="Гость"):
        self.username = username
        self.saved_routes = []
        self.favorite_places = []
        self.join_date = datetime.now()
        self.preferences = {
            "categories": [],
            "price_range": "$$",
            "max_distance": 10
        }
    
    def to_dict(self):
        return {
            "username": self.username,
            "saved_routes": self.saved_routes,
            "favorite_places": self.favorite_places,
            "join_date": self.join_date.isoformat(),
            "preferences": self.preferences
        }
    
    @classmethod
    def from_dict(cls, data):
        profile = cls(data["username"])
        profile.saved_routes = data["saved_routes"]
        profile.favorite_places = data["favorite_places"]
        profile.join_date = datetime.fromisoformat(data["join_date"])
        profile.preferences = data["preferences"]
        return profile

class RoutePlannerApp:
    def __init__(self):
        self.places = []  # Список выбранных мест
        self.current_user = UserProfile()
        self.categories = {
            "Все категории": [],
            "Рестораны": ["ресторан", "кафе", "бар", "кофейня"],
            "Культура": ["театр", "кино", "музей", "галерея", "библиотека"],
            "Парки": ["парк", "сквер", "сад", "набережная"],
            "Развлечения": ["клуб", "бильярд", "боулинг", "аквапарк"],
            "Магазины": ["торговый центр", "магазин", "бутик", "супермаркет"],
            "Спорт": ["стадион", "спортивный комплекс", "бассейн", "фитнес"]
        }
        
        # Расширенные тестовые данные
        self.sample_places = [
            # Рестораны
            {"name": "Итальянский ресторан 'Паста'", "category": "Рестораны", "address": "ул. Гастрономическая, 15", "rating": 4.7, "price": "$$$", "hours": "10:00-23:00"},
            {"name": "Кофейня 'Утренний кофе'", "category": "Рестораны", "address": "пр. Центральный, 42", "rating": 4.5, "price": "$", "hours": "07:00-22:00"},
            {"name": "Суши-бар 'Токио'", "category": "Рестораны", "address": "ул. Восточная, 8", "rating": 4.3, "price": "$$", "hours": "11:00-23:00"},
            {"name": "Бар 'Красное вино'", "category": "Рестораны", "address": "пл. Вечерняя, 3", "rating": 4.6, "price": "$$$", "hours": "18:00-02:00"},
            
            # Культура
            {"name": "Театр драмы", "category": "Культура", "address": "пл. Театральная, 1", "rating": 4.8, "price": "$$", "hours": "10:00-20:00"},
            {"name": "Кинотеатр 'Современник'", "category": "Культура", "address": "пр. Кино, 10", "rating": 4.2, "price": "$$", "hours": "09:00-00:00"},
            {"name": "Художественный музей", "category": "Культура", "address": "ул. Музейная, 5", "rating": 4.9, "price": "$", "hours": "11:00-19:00"},
            {"name": "Галерея современного искусства", "category": "Культура", "address": "пер. Искусств, 12", "rating": 4.4, "price": "$$", "hours": "12:00-20:00"},
            
            # Парки
            {"name": "Центральный парк", "category": "Парки", "address": "ул. Парковая, 1", "rating": 4.6, "price": "Бесплатно", "hours": "круглосуточно"},
            {"name": "Ботанический сад", "category": "Парки", "address": "ул. Растительная, 25", "rating": 4.7, "price": "$", "hours": "08:00-20:00"},
            {"name": "Набережная реки", "category": "Парки", "address": "наб. Речная, 7", "rating": 4.5, "price": "Бесплатно", "hours": "круглосуточно"},
            {"name": "Сквер Победы", "category": "Парки", "address": "пл. Победы, 2", "rating": 4.3, "price": "Бесплатно", "hours": "круглосуточно"},
            
            # Развлечения
            {"name": "Боулинг-клуб 'Страйк'", "category": "Развлечения", "address": "ул. Спортивная, 8", "rating": 4.1, "price": "$$", "hours": "12:00-00:00"},
            {"name": "Ночной клуб 'Атмосфера'", "category": "Развлечения", "address": "пр. Ночной, 33", "rating": 4.4, "price": "$$$", "hours": "22:00-06:00"},
            {"name": "Аквапарк 'Волна'", "category": "Развлечения", "address": "ул. Водная, 18", "rating": 4.8, "price": "$$$", "hours": "10:00-22:00"},
            {"name": "Караоке-бар 'Голос'", "category": "Развлечения", "address": "ул. Музыкальная, 11", "rating": 4.2, "price": "$$", "hours": "16:00-02:00"},
            
            # Магазины
            {"name": "Торговый центр 'Глобус'", "category": "Магазины", "address": "ул. Торговая, 15", "rating": 4.0, "price": "$$", "hours": "09:00-22:00"},
            {"name": "Бутик 'Мода'", "category": "Магазины", "address": "ул. Стильная, 9", "rating": 4.3, "price": "$$$", "hours": "10:00-21:00"},
            {"name": "Супермаркет 'Продукты'", "category": "Магазины", "address": "пр. Продовольственный, 20", "rating": 4.1, "price": "$", "hours": "08:00-23:00"},
            {"name": "Книжный магазин 'Читай'", "category": "Магазины", "address": "ул. Книжная, 6", "rating": 4.6, "price": "$$", "hours": "09:00-20:00"},
            
            # Спорт
            {"name": "Спортивный комплекс 'Олимп'", "category": "Спорт", "address": "ул. Спортивная, 25", "rating": 4.7, "price": "$$", "hours": "06:00-23:00"},
            {"name": "Бассейн 'Волна'", "category": "Спорт", "address": "ул. Водная, 12", "rating": 4.5, "price": "$$", "hours": "07:00-22:00"},
            {"name": "Стадион 'Юность'", "category": "Спорт", "address": "пр. Стадионный, 5", "rating": 4.4, "price": "$", "hours": "06:00-22:00"},
            {"name": "Фитнес-клуб 'Энергия'", "category": "Спорт", "address": "ул. Здоровая, 14", "rating": 4.3, "price": "$$$", "hours": "05:00-00:00"}
        ]
        
    def main(self, page: ft.Page):
        self.page = page
        page.title = "🚗 Маршруты по городу - Планировщик"
        page.theme_mode = ft.ThemeMode.LIGHT
        page.padding = 20
        page.scroll = ft.ScrollMode.ADAPTIVE
        
        # Элементы интерфейса профиля
        self.profile_dialog = ft.AlertDialog(
            modal=True,
            title=ft.Text("👤 Профиль пользователя"),
            content=ft.Column([], tight=True, scroll=ft.ScrollMode.ADAPTIVE),
            actions=[
                ft.TextButton("Закрыть", on_click=self.close_profile_dialog),
            ],
            actions_alignment=ft.MainAxisAlignment.END,
        )
        
        # Основные элементы интерфейса
        self.search_field = ft.TextField(
            label="🔍 Поиск мест...",
            hint_text="Введите название или адрес",
            expand=True,
            on_submit=self.search_places
        )
        
        self.category_dropdown = ft.Dropdown(
            label="📂 Категория",
            options=[ft.dropdown.Option(cat) for cat in self.categories.keys()],
            on_change=self.filter_by_category,
            expand=True,
            value="Все категории"
        )
        
        self.places_list = ft.ListView(expand=True, spacing=10)
        self.selected_places_list = ft.Column(expand=True, spacing=5)
        self.route_info = ft.Column()
        
        # Статистика
        self.stats_text = ft.Text("", size=12, color=ft.colors.GREY_600)
        
        # Собираем интерфейс
        page.add(
            ft.Row([
                ft.Text("🗺️ Планировщик маршрутов по городу", 
                       size=24, weight=ft.FontWeight.BOLD, expand=True),
                ft.IconButton(
                    icon=ft.icons.INFO,
                    on_click=self.show_info
                ),
                ft.IconButton(
                    icon=ft.icons.PERSON,
                    tooltip="Профиль пользователя",
                    on_click=self.show_profile_dialog
                )
            ]),
            
            ft.Row([
                self.search_field,
                self.category_dropdown,
                ft.ElevatedButton("🔍 Поиск", on_click=self.search_places),
                ft.ElevatedButton("🎲 Случайный маршрут", on_click=self.random_route)
            ]),
            
            self.stats_text,
            
            ft.Row([
                # Левая колонка - найденные места
                ft.Container(
                    content=ft.Column([
                        ft.Row([
                            ft.Text("📋 Найденные места:", size=16, weight=ft.FontWeight.BOLD),
                            ft.Text("(кликните чтобы добавить в маршрут)", size=12, color=ft.colors.GREY)
                        ]),
                        ft.Container(
                            content=self.places_list,
                            expand=True
                        )
                    ]),
                    expand=2,
                    padding=10,
                    border=ft.border.all(1, ft.colors.GREY_300),
                    border_radius=10
                ),
                
                # Правая колонка - выбранные места и маршрут
                ft.Container(
                    content=ft.Column([
                        ft.Text("📍 Маршрут:", size=16, weight=ft.FontWeight.BOLD),
                        ft.Container(
                            content=ft.Column(
                                controls=[self.selected_places_list],
                                scroll=ft.ScrollMode.ADAPTIVE
                            ),
                            height=300,
                            expand=True
                        ),
                        ft.Divider(),
                        self.route_info,
                        ft.Row([
                            ft.ElevatedButton(
                                "🚀 Построить маршрут", 
                                on_click=self.build_route,
                                icon=ft.icons.ROUTE,
                                style=ft.ButtonStyle(color=ft.colors.WHITE, bgcolor=ft.colors.GREEN)
                            ),
                            ft.ElevatedButton(
                                "🧹 Очистить маршрут",
                                on_click=self.clear_route,
                                icon=ft.icons.CLEAR
                            ),
                            ft.ElevatedButton(
                                "💾 Сохранить маршрут",
                                on_click=self.save_route,
                                icon=ft.icons.SAVE
                            )
                        ])
                    ]),
                    expand=1,
                    padding=10,
                    border=ft.border.all(1, ft.colors.GREY_300),
                    border_radius=10
                )
            ], expand=True, height=500),
            
            # Карта (заглушка)
            ft.Container(
                content=ft.Column([
                    ft.Text("🗺️ Карта маршрута", size=18, weight=ft.FontWeight.BOLD),
                    ft.Text("Здесь будет отображаться карта с построенным маршрутом"),
                    ft.Container(
                        bgcolor=ft.colors.BLUE_50,
                        height=200,
                        border_radius=10,
                        alignment=ft.alignment.center,
                        content=ft.Column([
                            ft.Icon(ft.icons.MAP, size=48, color=ft.colors.BLUE_300),
                            ft.Text("Интерактивная карта", color=ft.colors.BLUE_300)
                        ], horizontal_alignment=ft.CrossAxisAlignment.CENTER)
                    )
                ]),
                padding=10
            )
        )
        
        # Загружаем тестовые данные
        self.load_sample_places()
        self.update_stats()
    
    def show_profile_dialog(self, e):
        """Показать диалог профиля"""
        self.update_profile_dialog_content()
        self.page.dialog = self.profile_dialog
        self.profile_dialog.open = True
        self.page.update()
    
    def close_profile_dialog(self, e):
        """Закрыть диалог профиля"""
        self.profile_dialog.open = False
        self.page.update()
    
    def update_profile_dialog_content(self):
        """Обновить содержимое диалога профиля"""
        # Информация о пользователе
        user_info = ft.Column([
            ft.Row([
                ft.Icon(ft.icons.PERSON, size=40, color=ft.colors.BLUE_500),
                ft.Column([
                    ft.Text(self.current_user.username, size=20, weight=ft.FontWeight.BOLD),
                    ft.Text(f"Участник с {self.current_user.join_date.strftime('%d.%m.%Y')}", 
                           size=12, color=ft.colors.GREY_600),
                ])
            ]),
            ft.Divider(),
        ])
        
        # Статистика
        stats_section = ft.Column([
            ft.Text("📊 Статистика", size=16, weight=ft.FontWeight.BOLD),
            ft.Row([
                ft.Column([
                    ft.Text(str(len(self.current_user.saved_routes)), size=24, weight=ft.FontWeight.BOLD),
                    ft.Text("сохраненных\nмаршрутов", size=12, text_align=ft.TextAlign.CENTER)
                ], expand=True, horizontal_alignment=ft.CrossAxisAlignment.CENTER),
                ft.Column([
                    ft.Text(str(len(self.current_user.favorite_places)), size=24, weight=ft.FontWeight.BOLD),
                    ft.Text("избранных\nмест", size=12, text_align=ft.TextAlign.CENTER)
                ], expand=True, horizontal_alignment=ft.CrossAxisAlignment.CENTER),
            ]),
            ft.Divider(),
        ])
        
        # Сохраненные маршруты
        saved_routes_section = ft.Column([
            ft.Text("💾 Сохраненные маршруты", size=16, weight=ft.FontWeight.BOLD),
        ])
        
        if self.current_user.saved_routes:
            for i, route in enumerate(self.current_user.saved_routes[-3:]):  # Показываем последние 3
                route_card = ft.Card(
                    content=ft.Container(
                        content=ft.Column([
                            ft.Text(route.get("name", f"Маршрут {i+1}"), weight=ft.FontWeight.BOLD),
                            ft.Text(f"{len(route.get('places', []))} мест", size=12),
                            ft.Text(route.get("created_at", ""), size=10, color=ft.colors.GREY),
                        ]),
                        padding=10,
                        on_click=lambda e, r=route: self.load_saved_route(r)
                    )
                )
                saved_routes_section.controls.append(route_card)
        else:
            saved_routes_section.controls.append(
                ft.Text("Нет сохраненных маршрутов", size=12, color=ft.colors.GREY)
            )
        
        # Настройки профиля
        settings_section = ft.Column([
            ft.Divider(),
            ft.Text("⚙️ Настройки", size=16, weight=ft.FontWeight.BOLD),
            ft.ElevatedButton(
                "✏️ Изменить имя",
                on_click=self.change_username,
                icon=ft.icons.EDIT
            ),
            ft.ElevatedButton(
                "⭐ Предпочтения",
                on_click=self.show_preferences,
                icon=ft.icons.SETTINGS
            ),
        ])
        
        # Собираем все секции
        self.profile_dialog.content = ft.Column([
            user_info,
            stats_section,
            saved_routes_section,
            settings_section
        ], height=400, scroll=ft.ScrollMode.ADAPTIVE)
    
    def change_username(self, e):
        """Изменить имя пользователя"""
        def save_username(e):
            if name_field.value.strip():
                self.current_user.username = name_field.value.strip()
                self.page.dialog.open = False
                self.update_profile_dialog_content()
                self.page.update()
                self.show_snackbar("✅ Имя пользователя изменено")
        
        name_field = ft.TextField(
            label="Новое имя",
            value=self.current_user.username,
            autofocus=True
        )
        
        username_dialog = ft.AlertDialog(
            title=ft.Text("✏️ Изменить имя пользователя"),
            content=name_field,
            actions=[
                ft.TextButton("Отмена", on_click=lambda e: setattr(self.page.dialog, 'open', False)),
                ft.TextButton("Сохранить", on_click=save_username),
            ]
        )
        
        self.page.dialog = username_dialog
        username_dialog.open = True
        self.page.update()
    
    def show_preferences(self, e):
        """Показать настройки предпочтений"""
        self.show_snackbar("⚙️ Настройки предпочтений (в разработке)")
    
    def load_saved_route(self, route):
        """Загрузить сохраненный маршрут"""
        self.clear_route(None)
        
        # Добавляем места из сохраненного маршрута
        for place_data in route.get("places", []):
            # Находим полные данные о месте
            place = next((p for p in self.sample_places if p["name"] == place_data.get("name")), None)
            if place:
                self.add_to_route(place)
        
        self.profile_dialog.open = False
        self.page.update()
        self.show_snackbar(f"✅ Маршрут '{route.get('name', '')}' загружен")
    
    def load_sample_places(self):
        """Загрузка тестовых данных о местах"""
        self.places_list.controls.clear()
        for place in self.sample_places:
            self.add_place_to_list(place)
        self.page.update()
    
    def add_place_to_list(self, place: Dict):
        """Добавление места в список найденных"""
        # Создаем иконку в зависимости от категории
        icons = {
            "Рестораны": ft.icons.RESTAURANT,
            "Культура": ft.icons.THEATER_COMEDY,
            "Парки": ft.icons.PARK,
            "Развлечения": ft.icons.ATTRACTIONS,
            "Магазины": ft.icons.SHOPPING_BAG,
            "Спорт": ft.icons.SPORTS
        }
        
        icon = icons.get(place["category"], ft.icons.PLACE)
        
        # Проверяем, есть ли место в избранном
        is_favorite = any(fav["name"] == place["name"] for fav in self.current_user.favorite_places)
        favorite_icon = ft.icons.FAVORITE if is_favorite else ft.icons.FAVORITE_BORDER
        
        place_card = ft.Card(
            content=ft.Container(
                content=ft.Column([
                    ft.Row([
                        ft.Icon(icon, color=ft.colors.BLUE_500),
                        ft.Text(place["name"], weight=ft.FontWeight.BOLD, expand=True),
                        ft.IconButton(
                            icon=favorite_icon,
                            icon_color=ft.colors.RED if is_favorite else ft.colors.GREY,
                            icon_size=20,
                            on_click=lambda e, p=place: self.toggle_favorite(p)
                        ),
                        ft.Badge(
                            content=ft.Text(place["price"]),
                            bgcolor=ft.colors.GREEN_100 if place["price"] == "$" else 
                                   ft.colors.ORANGE_100 if place["price"] == "$$" else 
                                   ft.colors.RED_100
                        )
                    ]),
                    ft.Text(place["address"], size=12, color=ft.colors.GREY_600),
                    ft.Row([
                        ft.Text(f"⭐ {place['rating']}", size=12),
                        ft.Text(place["category"], size=12, color=ft.colors.BLUE_600),
                        ft.Text(f"🕒 {place['hours']}", size=12, color=ft.colors.GREY),
                    ])
                ]),
                padding=10,
                on_click=lambda e, p=place: self.add_to_route(p)
            )
        )
        
        self.places_list.controls.append(place_card)
    
    def toggle_favorite(self, place: Dict):
        """Добавить/удалить место из избранного"""
        if any(fav["name"] == place["name"] for fav in self.current_user.favorite_places):
            # Удаляем из избранного
            self.current_user.favorite_places = [
                fav for fav in self.current_user.favorite_places 
                if fav["name"] != place["name"]
            ]
            self.show_snackbar(f"❌ {place['name']} удален из избранного")
        else:
            # Добавляем в избранное
            self.current_user.favorite_places.append(place)
            self.show_snackbar(f"⭐ {place['name']} добавлен в избранное")
        
        # Обновляем отображение
        self.load_sample_places()
        self.page.update()
    
    def add_to_route(self, place: Dict):
        """Добавление места в маршрут"""
        if place not in self.places:
            self.places.append(place)
            
            place_item = ft.ListTile(
                leading=ft.Icon(ft.icons.LOCATION_ON),
                title=ft.Text(place["name"]),
                subtitle=ft.Text(place["address"]),
                trailing=ft.IconButton(
                    icon=ft.icons.DELETE,
                    on_click=lambda e, p=place: self.remove_from_route(p)
                )
            )
            
            self.selected_places_list.controls.append(place_item)
            self.update_stats()
            self.page.update()
            self.show_snackbar(f"✅ {place['name']} добавлен в маршрут")
    
    def remove_from_route(self, place: Dict):
        """Удаление места из маршрута"""
        self.places.remove(place)
        self.selected_places_list.controls = [
            item for item in self.selected_places_list.controls 
            if hasattr(item, 'title') and item.title.value != place["name"]
        ]
        self.update_stats()
        self.page.update()
        self.show_snackbar(f"❌ {place['name']} удален из маршрута")
    
    def search_places(self, e):
        """Поиск мест по запросу"""
        query = self.search_field.value.lower().strip()
        category = self.category_dropdown.value
        
        self.places_list.controls.clear()
        
        filtered_places = self.sample_places
        
        # Фильтрация по поисковому запросу
        if query:
            filtered_places = [
                p for p in filtered_places 
                if query in p["name"].lower() or 
                   query in p["address"].lower() or
                   query in p["category"].lower()
            ]
        
        # Фильтрация по категории
        if category and category != "Все категории":
            filtered_places = [p for p in filtered_places if p["category"] == category]
        
        for place in filtered_places:
            self.add_place_to_list(place)
        
        self.update_stats()
        self.page.update()
        
        if not filtered_places:
            self.show_snackbar("🔍 Места не найдены. Попробуйте другой запрос.")
    
    def filter_by_category(self, e):
        """Фильтрация по категории"""
        self.search_places(e)
    
    def random_route(self, e):
        """Создание случайного маршрута"""
        self.clear_route(e)
        
        # Выбираем 3-5 случайных мест
        num_places = random.randint(3, 5)
        random_places = random.sample(self.sample_places, num_places)
        
        for place in random_places:
            self.add_to_route(place)
        
        self.show_snackbar(f"🎲 Создан случайный маршрут из {num_places} мест")
    
    def build_route(self, e):
        """Построение маршрута"""
        if len(self.places) < 2:
            self.show_snackbar("❌ Добавьте хотя бы 2 места для построения маршрута")
            return
        
        # Расчет примерного времени и дистанции
        total_time = len(self.places) * 15 + (len(self.places) - 1) * 10
        total_distance = len(self.places) * 2.5
        
        self.route_info.controls = [
            ft.Text("✅ Маршрут построен!", color=ft.colors.GREEN, weight=ft.FontWeight.BOLD),
            ft.Text(f"📍 Количество точек: {len(self.places)}"),
            ft.Text(f"⏱️ Примерное время: {total_time} мин"),
            ft.Text(f"📏 Примерная дистанция: {total_distance:.1f} км"),
            ft.Text(f"🛣️ Оптимальный порядок:", weight=ft.FontWeight.BOLD),
        ]
        
        # Добавляем порядок посещения
        for i, place in enumerate(self.places, 1):
            self.route_info.controls.append(
                ft.Text(f"{i}. {place['name']}", size=12)
            )
        
        self.show_snackbar(f"✅ Маршрут через {len(self.places)} точек успешно построен!")
        self.page.update()
    
    def clear_route(self, e):
        """Очистка маршрута"""
        self.places.clear()
        self.selected_places_list.controls.clear()
        self.route_info.controls.clear()
        self.update_stats()
        self.page.update()
        self.show_snackbar("🧹 Маршрут очищен")
    
    def save_route(self, e):
        """Сохранение маршрута"""
        if not self.places:
            self.show_snackbar("❌ Нет маршрута для сохранения")
            return
        
        route_data = {
            "name": f"Маршрут от {datetime.now().strftime('%d.%m.%Y %H:%M')}",
            "places": self.places.copy(),
            "created_at": datetime.now().strftime('%d.%m.%Y %H:%M')
        }
        
        self.current_user.saved_routes.append(route_data)
        self.show_snackbar("💾 Маршрут сохранен в профиле!")
    
    def update_stats(self):
        """Обновление статистики"""
        total_places = len(self.sample_places)
        filtered_places = len(self.places_list.controls)
        selected_places = len(self.places)
        
        self.stats_text.value = f"📊 Всего мест: {total_places} | Найдено: {filtered_places} | В маршруте: {selected_places}"
    
    def show_info(self, e):
        """Показать информацию о приложении"""
        self.show_snackbar("🗺️ Планировщик маршрутов v1.0 • Используйте поиск и добавляйте места в маршрут!")
    
    def show_snackbar(self, message: str):
        """Показ уведомления"""
        self.page.snack_bar = ft.SnackBar(
            content=ft.Text(message),
            action="OK",
            action_color=ft.colors.BLUE
        )
        self.page.snack_bar.open = True
        self.page.update()

# Запуск приложения
def main(page: ft.Page):
    app = RoutePlannerApp()
    app.main(page)

if __name__ == "__main__":
    ft.app(target=main)