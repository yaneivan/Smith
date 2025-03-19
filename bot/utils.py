# bot/utils.py
from openai import OpenAI
import os
import re
import logging
from colorama import Fore, Style, init
from .config import OLLAMA_BASE_URL, OLLAMA_API_KEY, LLM_CITY_EXTRACT_MODEL, tracer
from datetime import datetime
import dateparser

# Инициализируем colorama
init(autoreset=True)

# Устанавливаем уровень логирования для httpx
logging.getLogger("httpx").setLevel(logging.WARNING)


client = OpenAI(base_url=OLLAMA_BASE_URL, api_key=OLLAMA_API_KEY)

def get_ollama_model_names():
    try:
        models_info = client.models.list()
        model_names = [model.id for model in models_info.data]
        return model_names
    except Exception as e:
        logging.error(f"Failed to fetch model names: {e}")
        return []

async def extract_city(user_message_text: str):
    with tracer.start_as_current_span("extract city") as city_extract:
        prompt = """
        Определи название города из сообщения пользователя.
        Если город найден, ответь в формате: ```город\nНазвание_города```.
        Если город не найден, ответь: ```город\nNone```.
        Примеры:
        Пользователь: Какая погода в Москве?
        Ты: ```город\nМосква```
        Пользователь: Привет, а в Питере как?
        Ты: ```город\nПитер```
        Пользователь: Как дела?
        Ты: ```город\nNone```
        """
        messages = [
            {"role": "system", "content": prompt},
            {"role": "user", "content": user_message_text}
        ]

        completion = client.chat.completions.create(
            model=LLM_CITY_EXTRACT_MODEL, 
            messages=messages,
            temperature=0
        )

        response_content = completion.choices[0].message.content.strip()
        colored_print(f"City extract response: {response_content}", "blue")  
        match = re.search(r"```город\n(.*)```", response_content, re.DOTALL)
        if match:
            city = match.group(1).strip()
            if city == "None":
                return None
            return city 
        else:
            return None

def colored_print(text: str, color: str = "white"):
    colors = {
        "red": Fore.RED,
        "green": Fore.GREEN,
        "yellow": Fore.YELLOW,
        "blue": Fore.BLUE,
        "magenta": Fore.MAGENTA,
        "cyan": Fore.CYAN,
        "white": Fore.WHITE,
    }
    print(colors.get(color, Fore.WHITE) + text)