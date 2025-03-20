# bot/handlers/general_chat.py
import logging
from aiogram import Dispatcher
from aiogram.types import Message
from openai import OpenAI
from ..config import OLLAMA_BASE_URL, OLLAMA_API_KEY, SYSTEM_PROMPT, CHAT_HISTORY_LIMIT, LLM_CHAT_MODEL, tracer
from ..router import route_request
from ..user_data import user_data
from .weather import handle_weather_message
from typing import List, Dict

logger = logging.getLogger(__name__)

client = OpenAI(base_url=OLLAMA_BASE_URL, api_key=OLLAMA_API_KEY)

def update_and_limit_history(user_id: int, new_entries: List[Dict[str, str]]):
    """Обновляет и ограничивает историю чата пользователя."""
    history = user_data.setdefault(user_id, {}).setdefault("chat_history", [])
    history.extend(new_entries)

    if len(history) > CHAT_HISTORY_LIMIT * 2:
        user_data[user_id]["chat_history"] = history[-(CHAT_HISTORY_LIMIT * 2):]
    else:
        user_data[user_id]["chat_history"] = history


def setup_general_chat_handlers(dp: Dispatcher):
    @dp.message()
    async def handle_general_chat_message(message: Message):
        with tracer.start_as_current_span("process_message", openinference_span_kind="chain") as main_span:
            user_id = message.from_user.id
            user_message_text = message.text

            logger.info(f"Received message from {user_id}: {user_message_text}")

            history = user_data.setdefault(user_id, {}).setdefault("chat_history", [])
            system_prompt = user_data.setdefault(user_id, {}).setdefault("system_prompt", SYSTEM_PROMPT)
            messages = [] 
            messages.extend(history)
            messages.append({"role": "user", "content": user_message_text})


            route = await route_request(messages) # route_request тоже не должен видеть системный промпт.
            model_to_use = user_data.setdefault(user_id, {}).setdefault("selected_model", LLM_CHAT_MODEL)
            logger.debug(f"Model to use for request: {model_to_use}")

            try:
                if route == "general":
                    with tracer.start_as_current_span("general_answer") as general_answer:
                        completion = client.chat.completions.create(
                            model=model_to_use,
                            messages=[{"role": "system", "content": system_prompt}] + messages,  
                        )
                        full_answer_text = completion.choices[0].message.content
                        await message.answer(full_answer_text)
                        update_and_limit_history(user_id, [
                            {"role": "user", "content": user_message_text},
                            {"role": "assistant", "content": full_answer_text}
                        ])

                elif route == "weather":
                    weather_result = await handle_weather_message(message)

                    if weather_result.startswith("❌"):
                        await message.answer(weather_result)
                        update_and_limit_history(user_id, [
                            {"role": "user", "content": user_message_text},
                            {"role": "system", "content": weather_result}  # system, потому что это ошибка от *системы*
                        ])
                    else:
                        # Добавляем system_prompt и weather_result ПЕРЕД отправкой
                        completion = client.chat.completions.create(
                            model=model_to_use,
                            messages=[{"role": "system", "content": system_prompt}, {"role": "system", "content": weather_result}] + messages, # Добавили оба system сообщения
                        )
                        full_answer_text = completion.choices[0].message.content
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