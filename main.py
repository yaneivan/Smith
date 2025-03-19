# main.py
import asyncio
import logging

from aiogram import Bot, Dispatcher
from bot.handlers import setup_handlers #  Вот так
from bot.commands import set_default_commands
from bot.config import TELEGRAM_TOKEN

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def main():
    bot = Bot(token=TELEGRAM_TOKEN)
    dp = Dispatcher()

    setup_handlers(dp)
    await set_default_commands(bot)

    logger.setLevel(logging.DEBUG)
    await dp.start_polling(bot)

if __name__ == '__main__':
    asyncio.run(main())