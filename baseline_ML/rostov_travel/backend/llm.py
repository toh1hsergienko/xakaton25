import os
from openai import OpenAI
from dotenv import load_dotenv
from typing import List, Dict

load_dotenv()

client = OpenAI(
    api_key=os.getenv("BOTHUB_API_KEY"),
    base_url="https://bothub.chat/api/v2/openai/v1"
)

def get_llm_recommendations(place_names: List[str]) -> List[str]:
    prompt = f"""
Ты — умный помощник для подбора персонализированного маршрута по Ростову-на-Дону.
Пользователь находится рядом со следующими местами.
Выбери до 15 самых интересных и разнообразных мест для посещения.
Верни ТОЛЬКО названия, каждое с новой строки. Ничего больше.

Список мест:
{chr(10).join(place_names)}
"""
    try:
        response = client.chat.completions.create(
            model="llama-4-scout",
            messages=[{"role": "user", "content": prompt}],
            timeout=20
        )
        text = response.choices[0].message.content.strip()
        names = [line.strip() for line in text.split("\n") if line.strip()]
        return names[:15]
    except Exception as e:
        print(f"LLM error: {e}")
        return place_names[:15]  # fallback