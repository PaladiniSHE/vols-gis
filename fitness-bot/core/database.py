"""
Настройка подключения к базе данных
"""
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase

from bot.config import settings


# Создаем асинхронный движок
engine = create_async_engine(
    settings.database_url,
    echo=settings.debug,
    future=True
)

# Фабрика сессий
async_session = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False
)


class Base(DeclarativeBase):
    """Базовый класс для моделей"""
    pass


async def get_session() -> AsyncSession:
    """Получить сессию базы данных"""
    async with async_session() as session:
        yield session


async def init_db():
    """Инициализация базы данных - создание таблиц"""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def close_db():
    """Закрытие подключения к базе данных"""
    await engine.dispose()
