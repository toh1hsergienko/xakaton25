import sqlite3
from typing import List, Tuple

DB_PATH = "../rostov_places.db"

def get_all_categories() -> List[str]:
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT DISTINCT category FROM attractions WHERE category IS NOT NULL")
    categories = [row[0] for row in cursor.fetchall()]
    conn.close()
    return sorted(categories)

def get_attractions_in_radius(lat: float, lon: float, radius_km: float) -> List[Tuple]:
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT id, name, lat, lon, category FROM attractions")
    all_places = cursor.fetchall()
    conn.close()
    return all_places