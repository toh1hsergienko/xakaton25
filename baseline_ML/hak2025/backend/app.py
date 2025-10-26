import sqlite3
import math
import requests
import os
import heapq
from typing import List, Optional
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from openai import OpenAI
from dotenv import load_dotenv

# ==============================
# Настройка
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

app = FastAPI(title="Rostov Travel Planner API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ==============================
# Модели
# ==============================
class RouteRequest(BaseModel):
    current_lat: float
    current_lon: float
    transport: str  # "walking" или "driving"
    selected_places: List[str]

class AttractionResponse(BaseModel):
    name: str
    lat: float
    lon: float
    category: str
    description: str
    rating: Optional[str]
    distance_km: float

class RouteResponse(BaseModel):
    total_km: float
    route_order: List[str]
    route_geometry: List[List[float]]  # [[lat, lng], ...]

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
            full_route.extend([[lat, lon] for lon, lat in geometry])
    return full_route

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
    return best_path[:-1], best_cost

def get_llm_recommendations(places_list: List[str]) -> List[str]:
    prompt = LLM_PROMPT.format(places_list="\n".join(places_list))
    try:
        response = client.chat.completions.create(
            model="llama-4-scout",
            messages=[{"role": "user", "content": prompt}],
            timeout=20
        )
        raw_text = response.choices[0].message.content.strip()
        recommended_names = [line.strip() for line in raw_text.split("\n") if line.strip()]
        return recommended_names[:15]
    except Exception as e:
        print(f"⚠️ Ошибка LLM: {e}")
        return []

# ==============================
# Эндпоинты
# ==============================
@app.get("/api/places", response_model=List[AttractionResponse])
def get_all_places():
    conn = sqlite3.connect("rostov_places.db")
    cursor = conn.cursor()
    cursor.execute("SELECT name, lat, lon, category, description, rating FROM attractions")
    rows = cursor.fetchall()
    conn.close()
    # Возвращаем все места — фронтенд сам фильтрует по расстоянию/категории при необходимости
    return [
        AttractionResponse(
            name=r[0],
            lat=r[1],
            lon=r[2],
            category=r[3] or "Другое",
            description=r[4] or "",
            rating=r[5] or "4.0",
            distance_km=0.0  # будет пересчитано на фронтенде или в другом эндпоинте
        )
        for r in rows
    ]

@app.post("/api/build_route", response_model=RouteResponse)
def build_route(request: RouteRequest):
    current_lat = request.current_lat
    current_lon = request.current_lon
    transport = request.transport
    selected_names = request.selected_places

    if transport not in ("walking", "driving"):
        raise HTTPException(status_code=400, detail="transport must be 'walking' or 'driving'")

    radius_km = 1.0 if transport == "walking" else 5.0

    # Получаем все места из БД
    conn = sqlite3.connect("rostov_places.db")
    cursor = conn.cursor()
    cursor.execute("SELECT name, lat, lon FROM attractions WHERE name IN ({})".format(
        ','.join('?' * len(selected_names))
    ), selected_names)
    db_places = {row[0]: (row[1], row[2]) for row in cursor.fetchall()}
    conn.close()

    if len(db_places) != len(selected_names):
        missing = set(selected_names) - set(db_places.keys())
        raise HTTPException(status_code=400, detail=f"Не найдены места: {missing}")

    # Фильтруем по радиусу
    filtered_places = []
    for name in selected_names:
        lat, lon = db_places[name]
        dist = haversine(current_lat, current_lon, lat, lon)
        if dist <= radius_km:
            filtered_places.append((name, lat, lon))

    if not filtered_places:
        raise HTTPException(status_code=400, detail=f"Нет выбранных мест в радиусе {radius_km} км")

    # Подготавливаем координаты: старт + выбранные
    coords = [(current_lat, current_lon)] + [(lat, lon) for _, lat, lon in filtered_places]
    names = ["start"] + [name for name, _, _ in filtered_places]

    # Получаем матрицу расстояний от OSRM
    try:
        osrm_distances = get_osrm_distance_matrix(coords, profile=transport)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ошибка OSRM: {str(e)}")

    n = len(osrm_distances)
    distance_matrix = [
        [osrm_distances[i][j] / 1000.0 if i != j else float('inf') for j in range(n)]
        for i in range(n)
    ]

    # Решаем TSP
    best_path_indices, total_km = branch_and_bound_tsp(distance_matrix)

    # Формируем маршрут
    route_order = [names[i] for i in best_path_indices if names[i] != "start"]
    route_geometry = get_osrm_route_geometry(coords, best_path_indices, profile=transport)

    return RouteResponse(
        total_km=round(total_km, 2),
        route_order=route_order,
        route_geometry=route_geometry
    )