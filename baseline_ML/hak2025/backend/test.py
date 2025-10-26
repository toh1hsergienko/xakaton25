# fix_db.py
import sqlite3

conn = sqlite3.connect("rostov_places.db")
cursor = conn.cursor()

# Проверим текущую структуру
cursor.execute("PRAGMA table_info(attractions)")
columns = [col[1] for col in cursor.fetchall()]
print("Текущие столбцы:", columns)

# Добавим недостающие столбцы, если их нет
if "description" not in columns:
    cursor.execute("ALTER TABLE attractions ADD COLUMN description TEXT")

if "category" not in columns:
    cursor.execute("ALTER TABLE attractions ADD COLUMN category TEXT")

if "rating" not in columns:
    cursor.execute("ALTER TABLE attractions ADD COLUMN rating TEXT")

conn.commit()
conn.close()
print("✅ Таблица обновлена: добавлены недостающие столбцы.")