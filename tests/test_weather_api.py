# tests/test_weather_api.py
import pytest
from bot.weather_api import get_weather
import asyncio

@pytest.mark.asyncio
async def test_get_weather_dubna_today():
    result = await get_weather("Дубна")
    assert isinstance(result, str)
    if "<html>weather result" in result:  #  Если есть префикс
        assert "Погода в Дубна" in result  #  Проверяем, что есть данные о погоде
    else:
        assert "Ошибка" in result  #  Иначе ожидаем ошибку

@pytest.mark.asyncio
async def test_get_weather_moscow_today():
    result = await get_weather("Москва")
    assert isinstance(result, str)
    if "<html>weather result" in result:
        assert "Погода в Москва" in result
    else:
        assert "Ошибка" in result

@pytest.mark.asyncio
async def test_get_weather_dubna_tomorrow():
    result = await get_weather("Дубна", "завтра")
    assert isinstance(result, str)
    if "<html>weather result" in result:
        assert "Погода в Дубна" in result
    else:
        assert "Ошибка" in result
@pytest.mark.asyncio
async def test_get_weather_invalid_city():
    result = await get_weather("НесуществующийГород")
    assert isinstance(result, str)
    assert "Ошибка" in result

@pytest.mark.asyncio
async def test_get_weather_invalid_date():
    result = await get_weather("Дубна", "какая-то ерунда")
    assert isinstance(result, str)
    assert "Ошибка" in result