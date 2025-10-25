import sqlite3
import csv
import os

def create_database():
    db_path = "rostov_places.db"
    if os.path.exists(db_path):
        os.remove(db_path)
        print("Удалена существующая база данных.")

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE attractions (
            id INTEGER PRIMARY KEY,
            name TEXT NOT NULL,
            lat REAL NOT NULL,
            lon REAL NOT NULL,
            category TEXT,
            website TEXT,
            opening_hours TEXT
        )
    """)

    cursor.execute("""
        CREATE TABLE restaurants (
            id INTEGER PRIMARY KEY,
            name TEXT NOT NULL,
            lat REAL NOT NULL,
            lon REAL NOT NULL,
            type TEXT,
            cuisine TEXT,
            price_level TEXT,
            opening_hours TEXT,
            website TEXT,
            addr TEXT
        )
    """)

    conn.commit()
    return conn

def clean_field(value):
    return value if value != "" else None

def import_attractions(conn):
    filename = "rostov_attractions.csv"
    if not os.path.exists(filename):
        print(f"⚠️ Файл {filename} не найден. Пропускаем.")
        return

    with open(filename, "r", encoding="utf-8-sig") as f:  # utf-8-sig — чтобы игнорировать BOM
        sample = f.read(200)
        f.seek(0)
        # Проверим, есть ли в начале цифры — тогда, возможно, нет заголовков
        first_line = f.readline().strip()
        f.seek(0)

        print(f"🔍 Первая строка {filename}: {first_line}")

        reader = csv.DictReader(f)
        expected_fields = {"id", "name", "lat", "lon", "category", "website", "opening_hours"}
        actual_fields = set(reader.fieldnames or [])
        if not expected_fields.issubset(actual_fields):
            print(f"❌ Ошибка: в {filename} отсутствуют нужные заголовки.")
            print(f"Ожидались: {expected_fields}")
            print(f"Получены: {actual_fields}")
            raise ValueError(f"Неверные заголовки в {filename}")

        cursor = conn.cursor()
        for row in reader:
            cursor.execute("""
                INSERT INTO attractions (
                    id, name, lat, lon, category, website, opening_hours
                ) VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (
                int(row["id"]),
                row["name"],
                float(row["lat"]),
                float(row["lon"]),
                clean_field(row["category"]),
                clean_field(row["website"]),
                clean_field(row["opening_hours"])
            ))
    conn.commit()
    print("✅ Достопримечательности импортированы.")

def import_restaurants(conn):
    filename = "rostov_restaurants.csv"
    if not os.path.exists(filename):
        print(f"⚠️ Файл {filename} не найден. Пропускаем.")
        return

    with open(filename, "r", encoding="utf-8-sig") as f:
        sample = f.read(200)
        f.seek(0)
        first_line = f.readline().strip()
        f.seek(0)

        print(f"🔍 Первая строка {filename}: {first_line}")

        reader = csv.DictReader(f)
        expected_fields = {"id", "name", "lat", "lon", "type", "cuisine", "price_level", "opening_hours", "website", "addr"}
        actual_fields = set(reader.fieldnames or [])
        if not expected_fields.issubset(actual_fields):
            print(f"❌ Ошибка: в {filename} отсутствуют нужные заголовки.")
            print(f"Ожидались: {expected_fields}")
            print(f"Получены: {actual_fields}")
            raise ValueError(f"Неверные заголовки в {filename}")

        cursor = conn.cursor()
        for row in reader:
            cursor.execute("""
                INSERT INTO restaurants (
                    id, name, lat, lon, type, cuisine,
                    price_level, opening_hours, website, addr
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                int(row["id"]),
                row["name"],
                float(row["lat"]),
                float(row["lon"]),
                clean_field(row["type"]),
                clean_field(row["cuisine"]),
                clean_field(row["price_level"]),
                clean_field(row["opening_hours"]),
                clean_field(row["website"]),
                clean_field(row["addr"])
            ))
    conn.commit()
    print("✅ Рестораны импортированы.")

def main():
    print("Создаём базу данных rostov_places.db...")
    conn = create_database()
    import_attractions(conn)
    import_restaurants(conn)
    conn.close()
    print("\n🎉 База данных успешно создана!")

if __name__ == "__main__":
    main()