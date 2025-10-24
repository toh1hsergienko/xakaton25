import math
import matplotlib.pyplot as plt

class TreeNode:
    def __init__(self, key):
        self.key = key  # Ключ узла (координаты точки: (x, y))
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

    def insert(self, key):
        self.root = self._insert(self.root, key)

    def _insert(self, node, key):
        if not node:
            return TreeNode(key)
        if key[0] < node.key[0]:  # Сортировка по координате X
            node.left = self._insert(node.left, key)
        else:
            node.right = self._insert(node.right, key)

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
        """Поиск всех точек в радиусе R от центра."""
        result = []
        self._search_in_radius(self.root, center, radius, result)
        return result

    def _search_in_radius(self, node, center, radius, result):
        if not node:
            return
        x, y = node.key
        cx, cy = center
        distance = math.sqrt((x - cx) ** 2 + (y - cy) ** 2)
        if distance <= radius:
            result.append(node.key)
        if node.left and cx - radius <= node.left.key[0]:
            self._search_in_radius(node.left, center, radius, result)
        if node.right and cx + radius >= node.right.key[0]:
            self._search_in_radius(node.right, center, radius, result)

    def display(self, node, level=0):
        if node is not None:
            self.display(node.right, level + 1)
            print(' ' * 4 * level + '->', f"{node.key}(h:{node.height})")
            self.display(node.left, level + 1)

def visualize_points(points, center=None, radius=None):
    """Визуализация точек на карте."""
    plt.figure(figsize=(8, 8))
    xs, ys = zip(*points)
    plt.scatter(xs, ys, color='blue', label="Точки")
    if center:
        cx, cy = center
        circle = plt.Circle((cx, cy), radius, color='red', fill=False, label="Радиус поиска")
        plt.gca().add_artist(circle)
        plt.scatter([cx], [cy], color='green', label="Центр")
    plt.legend()
    plt.title("ГИС-система: Поиск ближайших объектов")
    plt.xlabel("X")
    plt.ylabel("Y")
    plt.grid(True)
    plt.axis('equal')
    plt.show()

if __name__ == "__main__":
    tree = AVLTree()
    points = [
        (1, 2), (3, 4), (5, 6), (7, 8), (9, 10),
        (2, 3), (4, 5), (6, 7), (8, 9), (10, 11)
    ]
    for point in points:
        tree.insert(point)

    while True:
        print("\nМеню:")
        print("1. Добавить точку")
        print("2. Найти точки в радиусе")
        print("3. Вывести дерево")
        print("4. Визуализировать точки")
        print("0. Выход")
        choice = int(input("Выберите операцию: "))

        if choice == 1:
            x = float(input("Введите координату X: "))
            y = float(input("Введите координату Y: "))
            tree.insert((x, y))
            print(f"Точка ({x}, {y}) добавлена.")
        elif choice == 2:
            cx = float(input("Введите координату X центра: "))
            cy = float(input("Введите координату Y центра: "))
            radius = float(input("Введите радиус поиска: "))
            found_points = tree.search_in_radius((cx, cy), radius)
            print(f"Найденные точки в радиусе {radius}: {found_points}")
            visualize_points(points, (cx, cy), radius)
        elif choice == 3:
            tree.display(tree.root)
        elif choice == 4:
            visualize_points(points)
        elif choice == 0:
            break
        else:
            print("Неверный выбор. Попробуйте снова.")
            # open street map