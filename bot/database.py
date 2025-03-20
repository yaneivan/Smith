import aiosqlite
import logging
from .config import DATABASE_FILE
from typing import Optional, Tuple

logger = logging.getLogger(__name__)

async def init_db():
    """Инициализирует базу данных (создает таблицу, если ее нет)."""
    async with aiosqlite.connect(DATABASE_FILE) as db:
        await db.execute("""
            CREATE TABLE IF NOT EXISTS users (
                user_id INTEGER PRIMARY KEY,
                first_name TEXT,
                last_name TEXT,
                city TEXT DEFAULT 'Дубна',
                wakeup_time TEXT DEFAULT '07:00'
            )
        """)
        await db.commit()
        logger.info("Database initialized.")


async def add_user(user_id: int, first_name: str, last_name: str) -> None:
    """Добавляет пользователя в базу данных, если его там еще нет."""
    async with aiosqlite.connect(DATABASE_FILE) as db:
        async with db.execute("SELECT user_id FROM users WHERE user_id = ?", (user_id,)) as cursor:
            if await cursor.fetchone() is None:  # Проверяем, есть ли пользователь
                await db.execute("""
                    INSERT INTO users (user_id, first_name, last_name)
                    VALUES (?, ?, ?)
                """, (user_id, first_name, last_name))
                await db.commit()
                logger.info(f"User {user_id} ({first_name} {last_name}) added to the database.")
            else:
                logger.info(f"User {user_id} already exists in the database.")

async def get_user(user_id: int) -> Optional[Tuple]:
    """Возвращает данные пользователя по ID или None, если пользователя нет."""
    async with aiosqlite.connect(DATABASE_FILE) as db:
        async with db.execute("SELECT * FROM users WHERE user_id = ?", (user_id,)) as cursor:
            return await cursor.fetchone()

async def update_user_city(user_id: int, city: str) -> None:
    """Обновляет город пользователя."""
    async with aiosqlite.connect(DATABASE_FILE) as db:
        await db.execute("UPDATE users SET city = ? WHERE user_id = ?", (city, user_id))
        await db.commit()
        logger.info(f"User {user_id} city updated to {city}.")

async def update_user_wakeup_time(user_id: int, wakeup_time: str) -> None:
    """Обновляет время пробуждения пользователя."""
    async with aiosqlite.connect(DATABASE_FILE) as db:
        await db.execute("UPDATE users SET wakeup_time = ? WHERE user_id = ?", (wakeup_time, user_id))
        await db.commit()
        logger.info(f"User {user_id} wakeup time updated to {wakeup_time}.")


async def get_all_users():
    """Получает список всех пользователей из базы данных."""
    async with aiosqlite.connect(DATABASE_FILE) as db:
        async with db.execute("SELECT * FROM users") as cursor:
            return await cursor.fetchall()
        
async def get_users_for_wakeup(current_time: str) -> list:
    """Возвращает список пользователей, у которых время пробуждения совпадает с текущим."""
    async with aiosqlite.connect(DATABASE_FILE) as db:
        async with db.execute("SELECT * FROM users WHERE wakeup_time = ?", (current_time,)) as cursor:
            return await cursor.fetchall()