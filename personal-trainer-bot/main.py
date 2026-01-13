"""
Главный файл запуска бота "Личный Тренер"
"""
import asyncio
import sys
from loguru import logger

from aiogram import Bot, Dispatcher
from aiogram.enums import ParseMode
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.client.default import DefaultBotProperties

from config import settings
from database import init_db, db_manager
from bot.handlers import setup_routers
from bot.middlewares import DatabaseMiddleware
from bot.services import scheduler


# Настройка логирования
logger.remove()
logger.add(
    sys.stdout,
    format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
    level="DEBUG" if settings.debug else "INFO"
)
logger.add(
    "logs/bot.log",
    rotation="1 day",
    retention="7 days",
    level="INFO"
)


async def on_startup(bot: Bot):
    """Действия при запуске бота"""
    logger.info("Starting bot...")
    
    # Инициализация БД
    await init_db()
    logger.info("Database initialized")
    
    # Инициализация планировщика
    scheduler.init(bot, db_manager.session_factory)
    scheduler.start()
    logger.info("Scheduler started")
    
    # Получаем информацию о боте
    bot_info = await bot.get_me()
    logger.info(f"Bot started: @{bot_info.username}")


async def on_shutdown(bot: Bot):
    """Действия при остановке бота"""
    logger.info("Shutting down bot...")
    
    # Остановка планировщика
    scheduler.stop()
    
    # Закрытие соединения с БД
    await db_manager.disconnect()
    
    logger.info("Bot stopped")


async def main():
    """Главная функция запуска"""
    
    # Проверка токена
    if not settings.bot_token or settings.bot_token == "your_telegram_bot_token_here":
        logger.error("BOT_TOKEN is not set! Please set it in .env file")
        return
    
    # Создание бота
    bot = Bot(
        token=settings.bot_token,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML)
    )
    
    # Создание диспетчера
    dp = Dispatcher(storage=MemoryStorage())
    
    # Подключение middleware
    await db_manager.connect()
    dp.message.middleware(DatabaseMiddleware(db_manager.session_factory))
    dp.callback_query.middleware(DatabaseMiddleware(db_manager.session_factory))
    
    # Подключение роутеров
    router = setup_routers()
    dp.include_router(router)
    
    # Регистрация событий
    dp.startup.register(on_startup)
    dp.shutdown.register(on_shutdown)
    
    # Запуск
    try:
        logger.info("Starting polling...")
        await dp.start_polling(bot, allowed_updates=dp.resolve_used_update_types())
    finally:
        await bot.session.close()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Bot stopped by user")
    except Exception as e:
        logger.exception(f"Fatal error: {e}")
