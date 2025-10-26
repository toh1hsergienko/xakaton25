from pydantic import BaseModel
from typing import List, Optional

class RecommendationRequest(BaseModel):
    lat: float
    lon: float
    transport: str  # "walking" или "driving"

class AttractionResponse(BaseModel):
    id: int
    name: str
    lat: float
    lon: float
    category: Optional[str]
    distance_km: float
    rating: Optional[float] = None  # можно добавить позже

class CategoriesResponse(BaseModel):
    categories: List[str]