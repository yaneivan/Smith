# bot/handlers/__init__.py
from aiogram import Dispatcher
from .general_chat import setup_general_chat_handlers

def setup_handlers(dp: Dispatcher):
    setup_general_chat_handlers(dp)