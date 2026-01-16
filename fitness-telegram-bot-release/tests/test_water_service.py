"""
Интеграционные тесты для WaterService
"""
import pytest
from datetime import date
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

from core.database import Base
from core.models.user import User
from core.models.water import WaterEntry
from services.water_service import WaterService


TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"


@pytest.fixture
async def engine():
    """Создать тестовый движок БД"""
    engine = create_async_engine(TEST_DATABASE_URL, echo=False)
    
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    yield engine
    
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    
    await engine.dispose()


@pytest.fixture
async def session(engine):
    """Создать тестовую сессию"""
    async_session = sessionmaker(
        engine, class_=AsyncSession, expire_on_commit=False
    )
    
    async with async_session() as session:
        yield session


@pytest.fixture
async def test_user(session):
    """Создать тестового пользователя"""
    user = User(
        telegram_id=123456789,
        username="testuser",
        first_name="Test"
    )
    session.add(user)
    await session.commit()
    await session.refresh(user)
    return user


@pytest.fixture
def water_service(session):
    """Создать экземпляр WaterService"""
    return WaterService(session)


class TestWaterService:
    """Тесты для WaterService"""
    
    @pytest.mark.asyncio
    async def test_add_water_entry(self, water_service, test_user):
        """Тест добавления записи о воде"""
        entry = await water_service.add_water_entry(
            user_id=test_user.id,
            amount_ml=250
        )
        
        assert entry.id is not None
        assert entry.amount_ml == 250
        assert entry.entry_date == date.today()
    
    @pytest.mark.asyncio
    async def test_add_water_entry_custom_date(self, water_service, test_user):
        """Тест добавления записи за другую дату"""
        yesterday = date.today().replace(day=date.today().day - 1) if date.today().day > 1 else date.today()
        
        entry = await water_service.add_water_entry(
            user_id=test_user.id,
            amount_ml=500,
            entry_date=yesterday
        )
        
        assert entry.entry_date == yesterday
    
    @pytest.mark.asyncio
    async def test_get_daily_total(self, water_service, test_user):
        """Тест получения суммы воды за день"""
        today = date.today()
        
        await water_service.add_water_entry(test_user.id, 250, today)
        await water_service.add_water_entry(test_user.id, 300, today)
        await water_service.add_water_entry(test_user.id, 200, today)
        
        total = await water_service.get_daily_total(test_user.id, today)
        
        assert total == 750
    
    @pytest.mark.asyncio
    async def test_get_daily_total_no_entries(self, water_service, test_user):
        """Тест суммы при отсутствии записей"""
        total = await water_service.get_daily_total(test_user.id, date.today())
        
        assert total == 0
    
    @pytest.mark.asyncio
    async def test_get_entries_by_date(self, water_service, test_user):
        """Тест получения записей за день"""
        today = date.today()
        
        await water_service.add_water_entry(test_user.id, 100, today)
        await water_service.add_water_entry(test_user.id, 200, today)
        await water_service.add_water_entry(test_user.id, 300, today)
        
        entries = await water_service.get_entries_by_date(test_user.id, today)
        
        assert len(entries) == 3
        # Проверяем порядок (по времени добавления)
        assert entries[0].amount_ml == 100
        assert entries[1].amount_ml == 200
        assert entries[2].amount_ml == 300
    
    @pytest.mark.asyncio
    async def test_delete_last_entry(self, water_service, test_user):
        """Тест удаления последней записи"""
        today = date.today()
        
        await water_service.add_water_entry(test_user.id, 100, today)
        await water_service.add_water_entry(test_user.id, 200, today)
        await water_service.add_water_entry(test_user.id, 300, today)
        
        # Удаляем последнюю
        result = await water_service.delete_last_entry(test_user.id, today)
        assert result == True
        
        # Проверяем
        total = await water_service.get_daily_total(test_user.id, today)
        assert total == 300  # 100 + 200
    
    @pytest.mark.asyncio
    async def test_delete_last_entry_no_entries(self, water_service, test_user):
        """Тест удаления при отсутствии записей"""
        result = await water_service.delete_last_entry(test_user.id, date.today())
        
        assert result == False
    
    @pytest.mark.asyncio
    async def test_multiple_users_isolation(self, water_service, session):
        """Тест изоляции данных разных пользователей"""
        # Создаем двух пользователей
        user1 = User(telegram_id=111, username="user1")
        user2 = User(telegram_id=222, username="user2")
        session.add(user1)
        session.add(user2)
        await session.commit()
        await session.refresh(user1)
        await session.refresh(user2)
        
        today = date.today()
        
        # User1 пьет 1000мл
        await water_service.add_water_entry(user1.id, 1000, today)
        
        # User2 пьет 500мл
        await water_service.add_water_entry(user2.id, 500, today)
        
        # Проверяем изоляцию
        total1 = await water_service.get_daily_total(user1.id, today)
        total2 = await water_service.get_daily_total(user2.id, today)
        
        assert total1 == 1000
        assert total2 == 500
