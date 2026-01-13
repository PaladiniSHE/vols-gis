"""
Управление подключением к базе данных
"""
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.pool import NullPool
from contextlib import asynccontextmanager
from typing import AsyncGenerator
import os

from config import settings
from .models import Base


class DatabaseManager:
    """Менеджер базы данных"""
    
    def __init__(self, database_url: str = None):
        self.database_url = database_url or settings.database_url
        self.engine = None
        self.session_factory = None
    
    async def connect(self):
        """Создать подключение к БД"""
        # Создаём директорию для SQLite если нужно
        if "sqlite" in self.database_url:
            db_path = self.database_url.split("///")[-1]
            db_dir = os.path.dirname(db_path)
            if db_dir:
                os.makedirs(db_dir, exist_ok=True)
        
        self.engine = create_async_engine(
            self.database_url,
            echo=settings.debug,
            poolclass=NullPool if "sqlite" in self.database_url else None
        )
        
        self.session_factory = async_sessionmaker(
            bind=self.engine,
            class_=AsyncSession,
            expire_on_commit=False,
            autoflush=False
        )
    
    async def disconnect(self):
        """Закрыть подключение к БД"""
        if self.engine:
            await self.engine.dispose()
    
    async def create_tables(self):
        """Создать все таблицы"""
        async with self.engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
    
    @asynccontextmanager
    async def session(self) -> AsyncGenerator[AsyncSession, None]:
        """Контекстный менеджер для сессии"""
        if not self.session_factory:
            await self.connect()
        
        async with self.session_factory() as session:
            try:
                yield session
                await session.commit()
            except Exception:
                await session.rollback()
                raise


# Глобальный экземпляр менеджера БД
db_manager = DatabaseManager()


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """Получить сессию БД"""
    async with db_manager.session() as session:
        yield session


async def init_db():
    """Инициализировать базу данных"""
    await db_manager.connect()
    await db_manager.create_tables()
