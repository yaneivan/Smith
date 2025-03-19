import aiohttp
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

async def get_weather(city: str, date_str: str = "today") -> str:
    """
    Получает прогноз погоды для указанного города и даты с помощью wttr.in.

    Args:
        city: Название города.
        date_str: Строка с датой в свободной форме (например, "сейчас", "завтра", "2024-03-18").

    Returns:
        Строка с прогнозом погоды или сообщение об ошибке.
    """
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(f"https://wttr.in/{city}?format=j1&lang=ru") as response:
                response.raise_for_status()
                data = await response.json()
    except aiohttp.ClientError as e:
        logger.error(f"Weather request error: {e}")
        return f"❌ Ошибка при запросе погоды: {e}"
    except Exception as e:
        logger.error(f"Unexpected error during weather request: {e}")
        return f"❌ Непредвиденная ошибка при запросе погоды: {e}"

    try:
        forecast = data['weather'][0]  # wttr.in по умолчанию дает данные на сегодняшний день
    except IndexError:
        return "❌ Ошибка: данные для этого дня недоступны."

    closest = None
    for slot in forecast['hourly']:
        closest = slot  # wttr по умолчанию дает текущий прогноз
        break  # Как только нашли слот, выходим

    if not closest:
        return "❌ Ошибка: данные о погоде не найдены."

    # Извлекаем время из прогноза
    forecast_time = closest['time']
    # Преобразуем время в удобный формат (например, "08:00")
    forecast_time_formatted = f"{forecast_time[:2]}:{forecast_time[2:]}"

    # Форматируем результат
    temp = closest['tempC']
    desc = closest['lang_ru'][0]['value']
    wind_speed = closest['windspeedKmph']
    wind_dir = closest["winddir16Point"]  # Тут нет перевода
    feels_like = closest["FeelsLikeC"]
    humidity = closest["humidity"]
    pressure = closest["pressure"]  # Давление в миллибарах
    precip = closest["precipMM"]  # Осадки в мм
    uv_index = closest["uvIndex"]  # UV-индекс
    cloud_cover = closest["cloudcover"]  # Облачность в процентах
    chance_of_rain = closest["chanceofrain"]  # Вероятность дождя в процентах
    chance_of_snow = closest["chanceofsnow"]  # Вероятность снега в процентах

    # Объединяем вероятности осадков
    chance_of_precipitation = max(int(chance_of_rain), int(chance_of_snow))


    return (
        f"[WEATHER FORECAST TOOL CALL]\n"  # Добавили префикс!
        f"Погода в {city} на {forecast_time_formatted}:\n"
        f"Температура: {temp}°C, ощущается как {feels_like}°C\n"
        f"Описание: {desc}\n"
        f"Ветер: {wind_dir} {wind_speed} км/ч\n"
        f"Влажность: {humidity}%\n"
        f"Давление: {pressure} мбар\n"
        f"Осадки: {precip} мм\n"
        f"UV-индекс: {uv_index}\n"
        f"Облачность: {cloud_cover}%\n"
        f"Вероятность осадков: {chance_of_precipitation}%"
        f"[/WEATHER FORECAST TOOL CALL]"
    )