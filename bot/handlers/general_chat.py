import logging
from aiogram import Dispatcher
from aiogram.types import Message
from openai import OpenAI
from ..config import OLLAMA_BASE_URL, OLLAMA_API_KEY, SYSTEM_PROMPT, CHAT_HISTORY_LIMIT, LLM_CHAT_MODEL, tracer
from ..router import route_request
from .weather import handle_weather_message
from typing import List, Dict
from aiogram.filters import Command
from ..database import add_user, get_user, update_user_city, update_user_wakeup_time
import datetime

logger = logging.getLogger(__name__)

client = OpenAI(base_url=OLLAMA_BASE_URL, api_key=OLLAMA_API_KEY)

chat_histories = {}


def update_and_limit_history(user_id: int, new_entries: List[Dict[str, str]]):
    """Обновляет и ограничивает историю чата пользователя."""
    history = chat_histories.setdefault(user_id, [])
    history.extend(new_entries)
    if len(history) > CHAT_HISTORY_LIMIT * 2:
        chat_histories[user_id] = history[-(CHAT_HISTORY_LIMIT * 2):]


def get_user_context(user_data: tuple) -> str:
    """Формирует строку контекста пользователя."""
    now = datetime.datetime.now()
    current_time_str = now.strftime("%Y-%m-%d %H:%M:%S")

    if user_data:
        user_info_str = (
            f"ID пользователя: {user_data[0]}, "
            f"Имя: {user_data[1]}, "
            f"Фамилия: {user_data[2]}, "
            f"Город: {user_data[3]}, "
        )
    else:
        user_info_str = "Информация отсутствует."

    return f"Текущее время: {current_time_str}\n{user_info_str}"


def setup_general_chat_handlers(dp: Dispatcher):
    @dp.message(Command("clear"))
    async def clear_history_command_handler(message: Message):
        """Clears the user's message history."""
        user_id = message.from_user.id
        if user_id in chat_histories:
            chat_histories[user_id] = []
            await message.answer("История сообщений очищена.")
        else:
            await message.answer("История сообщений уже пуста.")

    @dp.message(Command("start"))
    async def start_command_handler(message: Message):
        user_id = message.from_user.id
        first_name = message.from_user.first_name
        last_name = message.from_user.last_name or ""

        await add_user(user_id, first_name, last_name)
        await message.answer(f"Привет, {first_name}! Вы добавлены в базу данных.")

    @dp.message()
    async def handle_general_chat_message(message: Message):
        with tracer.start_as_current_span("process_message", openinference_span_kind="chain") as main_span:
            user_id = message.from_user.id
            user_message_text = message.text

            user_data = await get_user(user_id)
            if user_data:
                logger.info(f"Received message from {user_id} ({user_data[1]} {user_data[2]}): {user_message_text}")
            else:
                logger.info(f"Received message from {user_id}: {user_message_text}")

            # Подготовка базовых сообщений для запроса к LLM
            messages = [
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "system", "content": get_user_context(user_data)},
            ]
            history = chat_histories.setdefault(user_id, [])
            messages.extend(history)
            messages.append({"role": "user", "content": user_message_text})

            route = await route_request(messages)
            model_to_use = LLM_CHAT_MODEL
            logger.debug(f"Model to use for request: {model_to_use}")

            weather_tool_call_message = None  # Initialize the variable

            try:
                if route == "weather":
                    weather_result = await handle_weather_message(message)
                    if weather_result.startswith("❌"):
                        await message.answer(weather_result)
                        update_and_limit_history(user_id, [
                            {"role": "user", "content": user_message_text},
                            {"role": "system", "content": weather_result}
                        ])
                        return  # Exit the function early
                    else:
                        # Добавляем информацию о погоде как системное сообщение *после* истории
                        messages.append({"role": "system", "content": weather_result})
                        weather_tool_call_message = "🌦️ Weather tool called" # Assign the message
                        

                # Единый блок для генерации ответа
                with tracer.start_as_current_span("generate_answer") as generate_answer:
                    completion = client.chat.completions.create(
                        model=model_to_use,
                        messages=messages,
                    )
                    full_answer_text = completion.choices[0].message.content

                    if weather_tool_call_message: # Check if the variable is set
                         await message.answer(weather_tool_call_message)

                    await message.answer(full_answer_text)


                    update_and_limit_history(user_id, [
                        {"role": "user", "content": user_message_text},
                        {"role": "assistant", "content": full_answer_text}
                    ])

            except Exception as e:
                error_message = f"❌ Общая ошибка: {str(e)}"
                await message.answer(error_message)
                logger.exception(f"General error: {e}")
                update_and_limit_history(user_id, [{"role": "system", "content": error_message}])