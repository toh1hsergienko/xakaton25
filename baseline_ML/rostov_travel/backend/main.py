from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from typing import List
from models import RecommendationRequest, AttractionResponse, CategoriesResponse
from database import get_all_categories, get_attractions_in_radius
from untils import haversine
from llm import get_llm_recommendations
import os

app = FastAPI(title="Rostov Travel Planner API")

# Раздача статики (ваш HTML)
app.mount("/static", StaticFiles(directory="../static"), name="static")

@app.get("/")
async def read_root():
    return FileResponse("../static/index.html")

# 1. Получить категории
@app.get("/api/categories", response_model=CategoriesResponse)
async def api_categories():
    cats = get_all_categories()
    return {"categories": cats}

# 2. Получить рекомендации
@app.post("/api/get-recommendations")
async def api_get_recommendations(req: RecommendationRequest):
    radius_km = 1.0 if req.transport == "walking" else 5.0

    # Получаем все достопримечательности
    all_places = get_attractions_in_radius(req.lat, req.lon, radius_km)

    # Фильтруем по радиусу и считаем расстояние
    nearby = []
    for pid, name, lat, lon, category in all_places:
        dist = haversine(req.lat, req.lon, lat, lon)
        if dist <= radius_km:
            nearby.append({
                "id": pid,
                "name": name,
                "lat": lat,
                "lon": lon,
                "category": category,
                "distance_km": dist
            })

    if not nearby:
        return {"recommendations": []}

    # Получаем рекомендации от LLM
    place_names = [p["name"] for p in nearby]
    llm_recs = get_llm_recommendations(place_names)

    # Сопоставляем с базой
    name_to_place = {p["name"]: p for p in nearby}
    recommended_places = []
    for name in llm_recs:
        if name in name_to_place:
            place = name_to_place[name]
            recommended_places.append(AttractionResponse(
                id=place["id"],
                name=place["name"],
                lat=place["lat"],
                lon=place["lon"],
                category=place["category"],
                distance_km=place["distance_km"],
                rating=4.3  # заглушка; можно добавить в БД позже
            ))

    return {"recommendations": recommended_places}