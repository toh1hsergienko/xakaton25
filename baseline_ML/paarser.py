import requests
import pandas as pd
import time

s, w, n, e = 47.15, 39.60, 47.35, 39.85

# Упрощённый запрос: только node (без way)
query = f'[out:json][timeout:60];(node["tourism"="museum"]({s},{w},{n},{e});node["amenity"="museum"]({s},{w},{n},{e});node["tourism"="attraction"]({s},{w},{n},{e});node["amenity"="theatre"]({s},{w},{n},{e});node["leisure"="park"]({s},{w},{n},{e});node["amenity"="place_of_worship"]({s},{w},{n},{e});node["historic"="monument"]({s},{w},{n},{e});node["historic"="memorial"]({s},{w},{n},{e}););out;'

url = "https://overpass-api.de/api/interpreter"

max_retries = 3
for attempt in range(max_retries):
    print(f"Попытка {attempt + 1} из {max_retries}...")
    try:
        response = requests.post(url, data=query, timeout=90)
        
        if response.status_code == 200:
            try:
                data = response.json()
                break
            except Exception as e:
                print("❌ Не JSON:", e)
                print(response.text[:300])
        else:
            print(f"❌ HTTP {response.status_code}")
            if "timeout" in response.text or "too busy" in response.text:
                print("Сервер перегружен. Ждём 10 сек...")
                time.sleep(10)
            else:
                print("Другая ошибка:", response.text[:300])
                
    except Exception as e:
        print("❌ Исключение:", e)
        time.sleep(5)
else:
    print("❌ Все попытки исчерпаны. Попробуйте позже или уменьшите регион.")
    exit()

# Обработка данных
places = []
for el in data.get('elements', []):
    if el['type'] != 'node':
        continue
    tags = el.get('tags', {})
    places.append({
        'id': el['id'],
        'name': tags.get('name', tags.get('name:ru', 'Без названия')),
        'lat': el['lat'],
        'lon': el['lon'],
        'category': (
            'museum' if tags.get('tourism') == 'museum' or tags.get('amenity') == 'museum' else
            'theatre' if tags.get('amenity') == 'theatre' else
            'park' if tags.get('leisure') == 'park' else
            'worship' if tags.get('amenity') == 'place_of_worship' else
            'monument' if tags.get('historic') in ['monument', 'memorial'] else
            'attraction' if tags.get('tourism') == 'attraction' else
            'other'
        ),
        'website': tags.get('website'),
        'opening_hours': tags.get('opening_hours')
    })

df = pd.DataFrame(places)
df = df.drop_duplicates(subset=['name', 'lat', 'lon'])
df.to_csv("rostov_attractions.csv", index=False, encoding='utf-8-sig')
print(f"\n✅ Успешно получено {len(df)} достопримечательностей!")
print("Файл сохранён: rostov_attractions.csv")