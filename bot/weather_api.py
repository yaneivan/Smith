import aiohttp
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

async def get_weather(city: str) -> str:  # Removed date_str
    """
    Получает прогноз погоды для указанного города с помощью wttr.in.

    Args:
        city: Название города.

    Returns:
        Строка с прогнозом погоды или сообщение об ошибке.
    """
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(f"https://wttr.in/{city}?format=j1&lang=ru") as response:
                response.raise_for_status()  # Raise HTTPError for bad responses (4xx or 5xx)
                data = await response.json()
    except aiohttp.ClientResponseError as e:
        logger.error(f"Weather request failed: {e.status} - {e.message} - URL: {e.request_info.url if e.request_info else 'N/A'}")
        return (f"❌ Ошибка при запросе погоды: {e.status} - {e.message}. "
                f"Возможно, неверно указан город ({city}) или проблемы с сервисом wttr.in.")
    except aiohttp.ClientConnectorError as e:
        logger.error(f"Weather request connection error: {e}")
        return f"❌ Ошибка подключения к сервису погоды: {e}. Проверьте подключение к интернету."
    except aiohttp.ContentTypeError as e:
        logger.error(f"Weather request: invalid content type: {e}")
        return f"❌ Ошибка: Сервер вернул данные в некорректном формате.  Попробуйте позже."
    except aiohttp.ClientError as e:  # Catch other aiohttp errors
        logger.error(f"Weather request error: {type(e).__name__} - {e}")
        return f"❌ Ошибка при запросе погоды: {type(e).__name__} - {e}"
    except Exception as e:
        logger.error(f"Unexpected error during weather request: {type(e).__name__} - {e}")
        return f"❌ Непредвиденная ошибка при запросе погоды: {type(e).__name__} - {e}"

    try:
        forecast = data['weather'][0]
    except (IndexError, KeyError) as e:
        logger.error(f"Weather data parsing error: {type(e).__name__} - {e} - Data: {data}")
        return f"❌ Ошибка: Не удалось получить данные о погоде для города {city}. Возможно, сервис временно недоступен."

    try:
      closest = forecast['hourly'][0]
    except (IndexError, KeyError) as e:
       logger.error(f"Weather data (hourly) parsing error: {type(e).__name__} - {e} - Forecast data: {forecast}")
       return "❌ Ошибка: данные о погоде не найдены или имеют неверный формат."


    # Извлекаем время из прогноза
    try:
        forecast_time = closest['time']
        forecast_time_formatted = f"{forecast_time[:2]}:{forecast_time[2:]}"

        # Форматируем результат
        temp = closest['tempC']
        desc = closest['lang_ru'][0]['value']
        wind_speed = closest['windspeedKmph']
        wind_dir = closest["winddir16Point"]
        feels_like = closest["FeelsLikeC"]
        humidity = closest["humidity"]
        pressure = closest["pressure"]
        precip = closest["precipMM"]
        uv_index = closest["uvIndex"]
        cloud_cover = closest["cloudcover"]
        chance_of_rain = closest["chanceofrain"]
        chance_of_snow = closest["chanceofsnow"]

        # Объединяем вероятности осадков
        chance_of_precipitation = max(int(chance_of_rain), int(chance_of_snow))

    except (KeyError, IndexError, ValueError, TypeError) as e:
        logger.error(f"Error extracting weather data: {type(e).__name__} - {e} - Closest data: {closest}")
        return f"❌ Ошибка при обработке данных о погоде: {type(e).__name__} - {e}"

    return (
        f"[WEATHER FORECAST TOOL CALL]\n"
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