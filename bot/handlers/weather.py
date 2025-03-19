# bot/handlers/weather.py
import logging
from aiogram.types import Message
from openai import OpenAI
from ..config import (
    OLLAMA_BASE_URL,
    OLLAMA_API_KEY,
    LLM_CHAT_MODEL,
    tracer
)
from ..weather_api import get_weather
from ..utils import extract_city, colored_print
from ..user_data import user_data # Важно для доступа к user_data


logger = logging.getLogger(__name__)

client = OpenAI(base_url=OLLAMA_BASE_URL, api_key=OLLAMA_API_KEY)

async def handle_weather_message(message: Message) -> str:
    """Обрабатывает запрос погоды и возвращает строку с результатом."""
    with tracer.start_as_current_span("handle_weather_request", openinference_span_kind="chain") as weather_span:
        user_id = message.from_user.id
        user_message_text = message.text
        logger.info(f"Received message from {user_id}: {user_message_text}")

        city = await extract_city(user_message_text)
        colored_print(f"City: {city}", "cyan")
        logger.info(f"Extracted city: {city}")

        if city:
            with tracer.start_as_current_span("weather_tool", openinference_span_kind="tool") as weather_tool:
                weather_tool.set_input(city)
                weather_data_formatted = await get_weather(city)
                weather_tool.set_output(weather_data_formatted)

            if weather_data_formatted and not weather_data_formatted.startswith("❌"):
                return weather_data_formatted 

            else:  
                return weather_data_formatted

        else:
            return "Не могу понять, для какого города вы хотите узнать погоду. Пожалуйста, уточните запрос."