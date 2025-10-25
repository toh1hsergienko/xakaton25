from openai import OpenAI
from dotenv import load_dotenv
import os

load_dotenv()  # загружает переменные из .env

api_key = os.getenv("BOTHUB_API_KEY")
if not api_key:
    raise ValueError("Переменная окружения BOTHUB_API_KEY не установлена")

client = OpenAI(
    api_key=api_key,
    base_url="https://bothub.chat/api/v2/openai/v1"
)
promt = """
Ты умный помощник для подбора персонализированного маршрута для людей путешествующих в Ростове-на-Дону.
Тебе необходимо анализировать маршруты, тебе будет пресылаться список мест для посещения пользователя. 
Так же тебе будет присылаться его прошлые маршруты и места которые посещал пользователь. 
Тебе будет необходимо присыылать список мест которые ты будишь рекомендовать да пользователя.

"""
response = client.chat.completions.create(
    model="llama-4-scout",
    messages=[{"role": "user", "content": ''}]
)

print(response.choices[0].message.content)