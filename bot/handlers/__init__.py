# bot/handlers/__init__.py
from aiogram import Dispatcher
from .command_handlers import setup_command_handlers
from .general_chat import setup_general_chat_handlers

def setup_handlers(dp: Dispatcher):
    setup_command_handlers(dp)
    setup_general_chat_handlers(dp)