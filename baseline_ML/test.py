import sqlite3
import math
import requests
import folium
import heapq
import os
from openai import OpenAI
from dotenv import load_dotenv

# ==============================
# Настройка LLM
# ==============================
load_dotenv()
api_key = os.getenv("BOTHUB_API_KEY")
if not api_key:
    raise ValueError("Переменная окружения BOTHUB_API_KEY не установлена")

client = OpenAI(
    api_key=api_key,
    base_url="https://bothub.chat/api/v2/openai/v1"
)

LLM_PROMPT = """
Ты — умный помощник для подбора персонализированного маршрута по Ростову-на-Дону.
Пользователь находится в определённой точке и видит следующие достопримечательности поблизости.
Твоя задача — выбрать из этого списка **до 15 самых интересных и разнообразных мест** для посещения.
Учитывай: популярность, уникальность, разнообразие категорий (парки, музеи, памятники, набережные, храмы и т.д.).
Верни **только названия мест**, каждое с новой строки. Ничего больше не пиши. Максимум — 15 мест.

Список доступных мест:
{places_list}
"""

# ==============================
# Вспомогательные функции
# ==============================

def haversine(lat1, lon1, lat2, lon2):
    R = 6371.0
    lat1, lon1, lat2, lon2 = map(math.radians, [lat1, lon1, lat2, lon2])
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    a = math.sin(dlat/2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon/2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return R * c

def get_osrm_distance_matrix(coords, profile="walking"):
    lon_lat_str = ";".join([f"{lon},{lat}" for lat, lon in coords])
    url = f"http://router.project-osrm.org/table/v1/{profile}/{lon_lat_str}?annotations=distance"
    response = requests.get(url, timeout=10)
    if response.status_code != 200:
        raise RuntimeError("OSRM request failed")
    return response.json()["distances"]

def get_osrm_route_geometry(coords, path, profile="walking"):
    full_route = []
    for i in range(len(path) - 1):
        start_lat, start_lon = coords[path[i]]
        end_lat, end_lon = coords[path[i + 1]]
        url = f"http://router.project-osrm.org/route/v1/{profile}/{start_lon},{start_lat};{end_lon},{end_lat}?geometries=geojson"
        resp = requests.get(url, timeout=10)
        if resp.status_code == 200:
            geometry = resp.json()["routes"][0]["geometry"]["coordinates"]
            full_route.extend([(lat, lon) for lon, lat in geometry])
    return full_route

# ==============================
# TSP: Branch and Bound
# ==============================

def reduce_matrix(matrix):
    n = len(matrix)
    cost = 0
    for i in range(n):
        min_val = min(matrix[i])
        if min_val != float('inf'):
            cost += min_val
            for j in range(n):
                matrix[i][j] -= min_val
    for j in range(n):
        col_min = min(matrix[i][j] for i in range(n))
        if col_min != float('inf'):
            cost += col_min
            for i in range(n):
                matrix[i][j] -= col_min
    return cost

def copy_matrix(matrix):
    return [row[:] for row in matrix]

def branch_and_bound_tsp(distance_matrix):
    n = len(distance_matrix)
    if n == 0:
        return [], 0
    pq = []
    initial_matrix = copy_matrix(distance_matrix)
    reduction_cost = reduce_matrix(initial_matrix)
    heapq.heappush(pq, (reduction_cost, 0, [0], initial_matrix, 0))
    best_cost = float('inf')
    best_path = None
    while pq:
        bound, current, path, matrix, path_cost = heapq.heappop(pq)
        if bound >= best_cost:
            continue
        if len(path) == n:
            total_cost = path_cost + distance_matrix[current][0]
            if total_cost < best_cost:
                best_cost = total_cost
                best_path = path + [0]
            continue
        for next_city in range(n):
            if next_city not in path:
                new_matrix = copy_matrix(matrix)
                for i in range(n):
                    new_matrix[current][i] = float('inf')
                    new_matrix[i][next_city] = float('inf')
                new_matrix[next_city][current] = float('inf')
                move_cost = distance_matrix[current][next_city]
                new_path_cost = path_cost + move_cost
                new_bound = new_path_cost + reduce_matrix(new_matrix)
                if new_bound < best_cost:
                    heapq.heappush(pq, (new_bound, next_city, path + [next_city], new_matrix, new_path_cost))
    return best_path, best_cost

# ==============================
# Основная функция
# ==============================

def get_llm_recommendations(places_list):
    prompt = LLM_PROMPT.format(places_list="\n".join(places_list))
    try:
        response = client.chat.completions.create(
            model="llama-4-scout",
            messages=[{"role": "user", "content": prompt}],
            timeout=20
        )
        raw_text = response.choices[0].message.content.strip()
        recommended_names = [line.strip() for line in raw_text.split("\n") if line.strip()]
        # Ограничиваем 15 местами, как просили
        return recommended_names[:15]
    except Exception as e:
        print(f"⚠️ Ошибка LLM: {e}")
        return None

def main():
    conn = sqlite3.connect("rostov_places.db")
    cursor = conn.cursor()

    # Текущая позиция
    try:
        print("📍 Укажите вашу текущую геопозицию:")
        current_lat = float(input("Широта (lat): ").strip())
        current_lon = float(input("Долгота (lon): ").strip())
    except ValueError:
        print("❌ Неверный формат координат.")
        return

    # Транспорт
    print("\nВыберите способ передвижения:")
    print("1. Пешком (радиус 1 км)")
    print("2. На автомобиле (радиус 5 км)")
    transport_choice = input("Введите 1 или 2: ").strip()
    radius_km = 1.0 if transport_choice == "1" else 5.0
    profile = "walking" if transport_choice == "1" else "driving"
    transport_name = "пешком" if transport_choice == "1" else "на автомобиле"

    # Получаем достопримечательности
    cursor.execute("SELECT name, lat, lon FROM attractions")
    all_places = cursor.fetchall()

    nearby = []
    for name, lat, lon in all_places:
        dist = haversine(current_lat, current_lon, lat, lon)
        if dist <= radius_km:
            nearby.append((name, lat, lon, dist))

    if not nearby:
        print(f"❌ В радиусе {radius_km} км нет достопримечательностей.")
        conn.close()
        return

    nearby.sort(key=lambda x: x[3])
    names_list = [item[0] for item in nearby]

    print(f"\n✅ Найдено {len(nearby)} мест в радиусе {radius_km} км.")

    # Получаем рекомендации от LLM
    print("\n🧠 Запрашиваем до 15 рекомендаций у ИИ...")
    llm_recs = get_llm_recommendations(names_list)

    candidate_places = []
    if llm_recs:
        # Фильтруем только существующие названия
        valid_recs = [name for name in llm_recs if name in names_list]
        if valid_recs:
            print(f"\n✨ ИИ рекомендует (всего {len(valid_recs)} мест):")
            for i, name in enumerate(valid_recs, 1):
                print(f"{i}. {name}")
            candidate_places = [(name, lat, lon) for name, lat, lon, _ in nearby if name in valid_recs]
        else:
            print("⚠️ ИИ вернул нераспознаваемые названия. Используем полный список.")
            candidate_places = [(name, lat, lon) for name, lat, lon, _ in nearby]
    else:
        print("⚠️ Не удалось получить рекомендации. Используем все доступные места.")
        candidate_places = [(name, lat, lon) for name, lat, lon, _ in nearby]

    # Пользователь выбирает из кандидатов (рекомендованных или всех)
    print("\nВыберите номера мест для посещения через запятую (например: 1,3,5):")
    try:
        selection = input("Ваши выборы: ").strip()
        if not selection:
            print("❌ Ничего не выбрано.")
            return
        indices = [int(x.strip()) - 1 for x in selection.split(",")]
        selected_places = [candidate_places[i] for i in indices if 0 <= i < len(candidate_places)]
    except (ValueError, IndexError):
        print("❌ Неверный формат выбора.")
        return

    if not selected_places:
        print("❌ Нет корректных выборов.")
        return

    print(f"\nВы выбрали {len(selected_places)} мест.")

    # Подготавливаем координаты
    coords = [(current_lat, current_lon)] + [(lat, lon) for _, lat, lon in selected_places]
    names = ["Ваша позиция"] + [name for name, _, _ in selected_places]

    # OSRM
    print(f"\nПолучаем реальные расстояния ({transport_name})...")
    try:
        osrm_distances = get_osrm_distance_matrix(coords, profile=profile)
    except Exception as e:
        print(f"❌ Ошибка OSRM: {e}")
        return

    n = len(osrm_distances)
    distance_matrix = [
        [osrm_distances[i][j] / 1000.0 if i != j else float('inf') for j in range(n)]
        for i in range(n)
    ]

    # TSP
    print("Строим оптимальный маршрут...")
    best_path, total_km = branch_and_bound_tsp(distance_matrix)

    # Вывод
    print("\n✅ Оптимальный маршрут:")
    for step, idx in enumerate(best_path[:-1], 1):
        print(f"{step}. {names[idx]}")
    print(f"\nОбщая длина маршрута: {total_km:.2f} км ({transport_name})")

    # Карта
    route_geom = get_osrm_route_geometry(coords, best_path[:-1], profile=profile)
    m = folium.Map(location=[current_lat, current_lon], zoom_start=13)
    folium.Marker([current_lat, current_lon], popup="Ваша позиция", icon=folium.Icon(color="red")).add_to(m)
    for name, lat, lon in selected_places:
        folium.Marker([lat, lon], popup=name).add_to(m)
    if route_geom:
        folium.PolyLine(route_geom, color="blue", weight=5).add_to(m)
    m.save("rostov_llm_route.html")
    print("\nКарта сохранена: rostov_llm_route.html")

    conn.close()

if __name__ == "__main__":
    main()