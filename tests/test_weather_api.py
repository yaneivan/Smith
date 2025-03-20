import pytest
import aiohttp
from bot.weather_api import get_weather

@pytest.mark.asyncio
async def test_get_weather_success():
    result = await get_weather("Moscow")
    assert "Погода в Moscow" in result
    assert "Температура:" in result  # More general checks
    assert "Описание:" in result
    assert "[WEATHER FORECAST TOOL CALL]" in result

@pytest.mark.asyncio
async def test_get_weather_invalid_city():
    result = await get_weather("InvalidCityThatDoesNotExist")
    assert "Ошибка при запросе погоды" in result
    # We can be more specific, wttr.in returns a 404 for unknown cities.
    assert "404" in result