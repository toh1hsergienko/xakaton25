import math
import folium

class TreeNode:
    def __init__(self, key, description):
        self.key = key  # Ключ узла (координаты точки: (широта, долгота))
        self.description = description  # Описание объекта
        self.left = None
        self.right = None
        self.height = 1

class AVLTree:
    def __init__(self):
        self.root = None

    def is_empty(self):
        return self.root is None

    def _height(self, node):
        return node.height if node else 0

    def _balance_factor(self, node):
        return self._height(node.left) - self._height(node.right) if node else 0

    def _update_height(self, node):
        if node:
            node.height = 1 + max(self._height(node.left), self._height(node.right))

    def _rotate_right(self, z):
        y = z.left
        T3 = y.right
        y.right = z
        z.left = T3
        self._update_height(z)
        self._update_height(y)
        return y

    def _rotate_left(self, z):
        y = z.right
        T2 = y.left
        y.left = z
        z.right = T2
        self._update_height(z)
        self._update_height(y)
        return y

    def insert(self, key, description):
        """Добавление нового объекта в дерево."""
        self.root = self._insert(self.root, key, description)

    def _insert(self, node, key, description):
        if not node:
            return TreeNode(key, description)
        if key[0] < node.key[0]:  # Сортировка по широте
            node.left = self._insert(node.left, key, description)
        else:
            node.right = self._insert(node.right, key, description)

        self._update_height(node)
        balance = self._balance_factor(node)

        # Балансировка
        if balance > 1 and key[0] < node.left.key[0]:
            return self._rotate_right(node)
        if balance < -1 and key[0] > node.right.key[0]:
            return self._rotate_left(node)
        if balance > 1 and key[0] > node.left.key[0]:
            node.left = self._rotate_left(node.left)
            return self._rotate_right(node)
        if balance < -1 and key[0] < node.right.key[0]:
            node.right = self._rotate_right(node.right)
            return self._rotate_left(node)
        return node

    def search_in_radius(self, center, radius):
        """Поиск всех объектов в радиусе R от центра."""
        result = []
        self._search_in_radius(self.root, center, radius, result)
        return result

    def _search_in_radius(self, node, center, radius, result):
        if not node:
            return
        x, y = node.key
        cx, cy = center
        distance = haversine_distance((x, y), (cx, cy))
        if distance <= radius:
            result.append((node.key, node.description))
        if node.left and cx - radius <= node.left.key[0]:
            self._search_in_radius(node.left, center, radius, result)
        if node.right and cx + radius >= node.right.key[0]:
            self._search_in_radius(node.right, center, radius, result)

    def get_all_points(self):
        """Возвращает список всех объектов в дереве."""
        result = []
        self._in_order_traversal(self.root, result)
        return result

    def _in_order_traversal(self, node, result):
        """Рекурсивный обход дерева в порядке возрастания ключей."""
        if not node:
            return
        self._in_order_traversal(node.left, result)
        result.append((node.key, node.description))
        self._in_order_traversal(node.right, result)

def haversine_distance(coord1, coord2):
    """Вычисление расстояния между двумя точками на сфере (в км)."""
    lat1, lon1 = coord1
    lat2, lon2 = coord2
    R = 6371  # Радиус Земли в км

    phi1 = math.radians(lat1)
    phi2 = math.radians(lat2)
    delta_phi = math.radians(lat2 - lat1)
    delta_lambda = math.radians(lon2 - lon1)

    a = math.sin(delta_phi / 2) ** 2 + math.cos(phi1) * math.cos(phi2) * math.sin(delta_lambda / 2) ** 2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))

    return R * c

def calculate_bounds(center, size_km):
    """
    Вычисление границ карты для заданного центра и размера.
    
    :param center: Центр карты (широта, долгота).
    :param size_km: Размер стороны карты в км (например, 100 км).
    :return: Координаты углов карты ((min_lat, min_lon), (max_lat, max_lon)).
    """
    lat, lon = center
    R = 6371  # Радиус Земли в км

    # Широта изменяется линейно
    delta_lat = size_km / (R * math.pi / 180)
    min_lat = lat - delta_lat / 2
    max_lat = lat + delta_lat / 2

    # Долгота зависит от широты
    delta_lon = size_km / (R * math.pi / 180 * math.cos(math.radians(lat)))
    min_lon = lon - delta_lon / 2
    max_lon = lon + delta_lon / 2

    return (min_lat, min_lon), (max_lat, max_lon)

def visualize_on_map(points, center, size_km):
    """
    Визуализация точек на карте OpenStreetMap с заданным размером.
    
    :param points: Список кортежей вида ((широта, долгота), описание).
    :param center: Центр карты (широта, долгота).
    :param size_km: Размер стороны карты в км.
    """
    # Вычисляем границы карты
    (min_lat, min_lon), (max_lat, max_lon) = calculate_bounds(center, size_km)

    # Создаем карту
    m = folium.Map(location=center, zoom_start=10, tiles="OpenStreetMap")

    # Добавляем маркеры для всех точек
    for point, description in points:
        folium.Marker(
            location=point,
            popup=description,
            icon=folium.Icon(color="blue")
        ).add_to(m)

    # Добавляем прямоугольник для границ карты
    folium.Rectangle(
        bounds=[(min_lat, min_lon), (max_lat, max_lon)],
        color="red",
        fill=False,
        weight=2
    ).add_to(m)

    # Сохраняем карту в HTML-файл
    m.save("map.html")
    print("Карта сохранена в файл 'map.html'. Откройте его в браузере.")

if __name__ == "__main__":
    tree = AVLTree()
    objects = {
        (55.7558, 37.6176): "Красная площадь",
        (55.7522, 37.6156): "Московский Кремль",
        (55.7587, 37.6194): "ГУМ",
        (55.7610, 37.6179): "Собор Василия Блаженного",
        (55.7539, 37.6214): "Александровский сад"
    }
    for point, description in objects.items():
        tree.insert(point, description)

    while True:
        print("\nМеню:")
        print("1. Добавить объект")
        print("2. Найти объекты в радиусе")
        print("3. Показать все объекты")
        print("4. Визуализировать объекты на карте")
        print("0. Выход")
        choice = int(input("Выберите операцию: "))

        if choice == 1:
            lat = float(input("Введите широту (Latitude): "))
            lon = float(input("Введите долготу (Longitude): "))
            description = input("Введите описание объекта: ")
            tree.insert((lat, lon), description)
            print(f"Объект '{description}' добавлен на координаты ({lat}, {lon}).")
        elif choice == 2:
            lat = float(input("Введите широту центра (Latitude): "))
            lon = float(input("Введите долготу центра (Longitude): "))
            radius = float(input("Введите радиус поиска (в км): "))
            found_objects = tree.search_in_radius((lat, lon), radius)
            print(f"Найденные объекты в радиусе {radius} км:")
            for point, description in found_objects:
                print(f"  {point}: {description}")
        elif choice == 3:
            all_objects = tree.get_all_points()
            print("Все объекты в дереве:")
            for point, description in all_objects:
                print(f"  {point}: {description}")
        elif choice == 4:
            lat = float(input("Введите широту центра карты (Latitude): "))
            lon = float(input("Введите долготу центра карты (Longitude): "))
            size_km = 100  # Размер карты 100×100 км
            all_objects = tree.get_all_points()
            visualize_on_map(all_objects, (lat, lon), size_km)
        elif choice == 0:
            break
        else:
            print("Неверный выбор. Попробуйте снова.")