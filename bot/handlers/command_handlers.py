# bot/handlers/command_handlers.py
import logging
from aiogram import Dispatcher
from aiogram.filters import Command, CommandObject
from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from openai import OpenAI
from ..config import OLLAMA_BASE_URL, OLLAMA_API_KEY, SYSTEM_PROMPT
from ..utils import get_ollama_model_names
from ..user_data import user_data

logger = logging.getLogger(__name__)

client = OpenAI(base_url=OLLAMA_BASE_URL, api_key=OLLAMA_API_KEY)
model_id_mapping = {}


def setup_command_handlers(dp: Dispatcher):
    @dp.message(Command("model"))
    async def model_command_handler(message: Message):
        available_models = get_ollama_model_names()
        if not available_models:
            await message.answer("Не удалось получить список моделей. Попробуйте позже.")
            return

        keyboard = InlineKeyboardMarkup(inline_keyboard=[])
        inline_keyboard_rows = []
        current_row = []
        row_width = 2

        for idx, model_name in enumerate(available_models):
            model_id = str(idx)
            model_id_mapping[model_id] = model_name
            button = InlineKeyboardButton(text=model_name, callback_data=f"model_select:{model_id}")
            current_row.append(button)
            if len(current_row) >= row_width:
                inline_keyboard_rows.append(current_row)
                current_row = []

        if current_row:
            inline_keyboard_rows.append(current_row)

        keyboard.inline_keyboard = inline_keyboard_rows
        await message.answer("Выберите модель:", reply_markup=keyboard)


    @dp.callback_query(lambda c: c.data.startswith('model_select:'))
    async def model_selection_callback_handler(query: CallbackQuery):
        user_id = query.from_user.id
        model_id = query.data.split(":")[1]

        full_model_name = model_id_mapping.get(model_id)
        if full_model_name:
            user_data.setdefault(user_id, {})["selected_model"] = full_model_name
            await query.answer(f"Выбрана модель: {full_model_name}")
            await query.message.edit_text(f"Выбрана модель: {full_model_name}")
        else:
            await query.answer("Ошибка: Модель не найдена.")
            await query.message.edit_text("Ошибка: Модель не найдена.")
            logger.error(f"Invalid model ID received: {model_id}")


    @dp.message(Command("clear"))
    async def clear_history_command_handler(message: Message):
        """Clears the user's message history."""
        user_id = message.from_user.id
        if user_id in user_data:
            user_data[user_id]["chat_history"] = []
            await message.answer("История сообщений очищена.")
        else:
            await message.answer("История сообщений уже пуста.")


    @dp.message(Command("setprompt"))
    async def set_prompt_command_handler(message: Message, command: CommandObject):
        """Sets the system prompt for the user."""
        user_id = message.from_user.id
        new_prompt = command.args

        if not new_prompt:
            await message.answer("Пожалуйста, укажите новый системный промпт.")
            return
        user_data.setdefault(user_id, {})["system_prompt"] = new_prompt
        await message.answer(f"Системный промпт обновлен:\n{new_prompt}")