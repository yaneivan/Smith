import asyncio
import logging

from aiogram import Bot, Dispatcher
from bot.handlers import setup_handlers
from bot.config import TELEGRAM_TOKEN
from bot.database import init_db  # Импортируем функцию инициализации БД

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def main():
    bot = Bot(token=TELEGRAM_TOKEN)
    dp = Dispatcher()

    setup_handlers(dp)

    logger.setLevel(logging.DEBUG)

    # Инициализируем базу данных перед запуском бота
    await init_db()

    await dp.start_polling(bot)

if __name__ == '__main__':
    asyncio.run(main())