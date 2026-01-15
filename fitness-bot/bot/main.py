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
from bot.middlewares import ThrottlingMiddleware, AntiFloodMiddleware
from core.database import init_db, close_db


# Настройка логирования
logging.basicConfig(
    level=logging.DEBUG if settings.debug else logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    stream=sys.stdout
)

logger = logging.getLogger(__name__)


def setup_sentry():
    """Настройка Sentry для мониторинга ошибок"""
    if not settings.sentry_dsn:
        logger.info("Sentry DSN not configured, error monitoring disabled")
        return False
    
    try:
        import sentry_sdk
        from sentry_sdk.integrations.asyncio import AsyncioIntegration
        from sentry_sdk.integrations.logging import LoggingIntegration
        
        sentry_sdk.init(
            dsn=settings.sentry_dsn,
            environment=settings.sentry_environment,
            traces_sample_rate=0.1 if settings.debug else 0.01,  # 10% в dev, 1% в prod
            profiles_sample_rate=0.1 if settings.debug else 0.01,
            integrations=[
                AsyncioIntegration(),
                LoggingIntegration(
                    level=logging.INFO,
                    event_level=logging.ERROR
                ),
            ],
            # Не отправлять PII данные
            send_default_pii=False,
            # Информация о релизе
            release=f"fitness-bot@1.1.0",
        )
        
        logger.info(f"Sentry initialized (environment: {settings.sentry_environment})")
        return True
        
    except ImportError:
        logger.warning("sentry-sdk not installed, error monitoring disabled")
        return False
    except Exception as e:
        logger.error(f"Failed to initialize Sentry: {e}")
        return False


def get_storage():
    """
    Получить хранилище для FSM.
    Использует Redis если доступен, иначе MemoryStorage.
    """
    if settings.redis_url:
        try:
            from aiogram.fsm.storage.redis import RedisStorage
            from redis.asyncio import Redis
            
            redis = Redis.from_url(settings.redis_url)
            logger.info(f"Using RedisStorage: {settings.redis_url}")
            return RedisStorage(redis=redis)
        except ImportError:
            logger.warning("redis package not installed, falling back to MemoryStorage")
        except Exception as e:
            logger.warning(f"Failed to connect to Redis: {e}, falling back to MemoryStorage")
    
    logger.info("Using MemoryStorage (FSM data will be lost on restart)")
    return MemoryStorage()


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
    # Инициализация Sentry для мониторинга ошибок
    sentry_enabled = setup_sentry()
    
    # Инициализация бота
    bot = Bot(
        token=settings.bot_token,
        default=DefaultBotProperties(parse_mode=ParseMode.MARKDOWN)
    )
    
    # Хранилище состояний (Redis для production, MemoryStorage для development)
    storage = get_storage()
    
    # Инициализация диспетчера
    dp = Dispatcher(storage=storage)
    
    # Подключаем rate limiting middleware для защиты от спама
    dp.message.middleware(ThrottlingMiddleware(
        rate_limit=settings.rate_limit_interval,
        max_burst=5,
        cooldown=3.0
    ))
    dp.callback_query.middleware(ThrottlingMiddleware(
        rate_limit=settings.rate_limit_interval * 0.6,  # Быстрее для callback
        max_burst=10,
        cooldown=2.0
    ))
    dp.message.middleware(AntiFloodMiddleware(
        max_requests_per_minute=settings.rate_limit_max_per_minute
    ))
    
    logger.info(f"Rate limiting: {settings.rate_limit_interval}s interval, {settings.rate_limit_max_per_minute} req/min")
    
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
