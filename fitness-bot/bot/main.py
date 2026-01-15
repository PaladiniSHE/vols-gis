"""
Главный модуль бота "Личный тренер"
"""
import asyncio
import logging
import sys

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.fsm.storage.memory import MemoryStorage

from bot.config import settings
from bot.handlers import setup_routers
from core.database import init_db, close_db


# Настройка логирования
logging.basicConfig(
    level=logging.DEBUG if settings.debug else logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    stream=sys.stdout
)

logger = logging.getLogger(__name__)


async def on_startup(bot: Bot):
    """Действия при запуске бота"""
    logger.info("Initializing database...")
    await init_db()
    
    # Загружаем начальные данные
    await load_initial_data()
    
    logger.info("Bot started successfully!")
    
    # Информация о боте
    bot_info = await bot.get_me()
    logger.info(f"Bot: @{bot_info.username} ({bot_info.first_name})")


async def on_shutdown(bot: Bot):
    """Действия при остановке бота"""
    logger.info("Shutting down...")
    await close_db()
    logger.info("Bot stopped.")


async def load_initial_data():
    """Загрузка начальных данных в базу"""
    import json
    from pathlib import Path
    from core.database import async_session
    from core.models.food import Food
    from sqlalchemy import select
    
    data_file = Path(__file__).parent.parent / "data" / "foods.json"
    
    if not data_file.exists():
        logger.warning("Initial foods data file not found")
        return
    
    async with async_session() as session:
        # Проверяем, есть ли уже данные
        result = await session.execute(select(Food).limit(1))
        if result.scalar_one_or_none():
            logger.info("Foods data already loaded")
            return
        
        # Загружаем данные
        with open(data_file, "r", encoding="utf-8") as f:
            foods_data = json.load(f)
        
        for food_data in foods_data:
            food = Food(
                name=food_data["name"],
                calories_100g=food_data["calories"],
                protein_100g=food_data.get("protein", 0),
                fat_100g=food_data.get("fat", 0),
                carbs_100g=food_data.get("carbs", 0),
                category=food_data.get("category"),
                source="system",
                is_verified=True
            )
            session.add(food)
        
        await session.commit()
        logger.info(f"Loaded {len(foods_data)} foods into database")


async def main():
    """Главная функция запуска бота"""
    # Инициализация бота
    bot = Bot(
        token=settings.bot_token,
        default=DefaultBotProperties(parse_mode=ParseMode.MARKDOWN)
    )
    
    # Хранилище состояний (в памяти, можно заменить на Redis)
    storage = MemoryStorage()
    
    # Инициализация диспетчера
    dp = Dispatcher(storage=storage)
    
    # Регистрация роутеров
    dp.include_router(setup_routers())
    
    # Регистрация событий startup/shutdown
    dp.startup.register(on_startup)
    dp.shutdown.register(on_shutdown)
    
    # Запуск polling
    logger.info("Starting bot...")
    
    try:
        await dp.start_polling(bot, allowed_updates=dp.resolve_used_update_types())
    finally:
        await bot.session.close()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Bot stopped by user")
    except Exception as e:
        logger.error(f"Bot crashed: {e}")
        raise
