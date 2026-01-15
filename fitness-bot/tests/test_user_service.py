"""
Интеграционные тесты для UserService
"""
import pytest
from datetime import date, timedelta
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

from core.database import Base
from core.models.user import User, Gender, Goal, ActivityLevel
from services.user_service import UserService


# Используем SQLite in-memory для тестов
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
def user_service(session):
    """Создать экземпляр UserService"""
    return UserService(session)


class TestUserService:
    """Тесты для UserService"""
    
    @pytest.mark.asyncio
    async def test_create_user(self, user_service):
        """Тест создания пользователя"""
        user = await user_service.get_or_create_user(
            telegram_id=123456789,
            username="testuser",
            first_name="Test",
            last_name="User"
        )
        
        assert user is not None
        assert user.telegram_id == 123456789
        assert user.username == "testuser"
        assert user.first_name == "Test"
        assert user.is_onboarded == False
    
    @pytest.mark.asyncio
    async def test_get_existing_user(self, user_service):
        """Тест получения существующего пользователя"""
        # Создаем пользователя
        user1 = await user_service.get_or_create_user(
            telegram_id=111111111,
            username="user1"
        )
        
        # Получаем того же пользователя
        user2 = await user_service.get_or_create_user(
            telegram_id=111111111,
            username="user1_updated"
        )
        
        assert user1.id == user2.id
        assert user2.username == "user1_updated"  # Username обновился
    
    @pytest.mark.asyncio
    async def test_update_user_profile(self, user_service):
        """Тест обновления профиля пользователя"""
        # Создаем пользователя
        await user_service.get_or_create_user(telegram_id=222222222)
        
        # Обновляем профиль
        user = await user_service.update_user_profile(
            telegram_id=222222222,
            height=180.0,
            weight=75.0,
            birth_date=date(1990, 5, 15),
            gender="male",
            goal="lose",
            activity_level="medium"
        )
        
        assert user.height == 180.0
        assert user.weight == 75.0
        assert user.gender == Gender.MALE
        assert user.goal == Goal.LOSE
        assert user.activity_level == ActivityLevel.MEDIUM
    
    @pytest.mark.asyncio
    async def test_calculate_and_save_norms(self, user_service):
        """Тест расчета и сохранения норм КБЖУ"""
        # Создаем пользователя с полным профилем
        await user_service.get_or_create_user(telegram_id=333333333)
        await user_service.update_user_profile(
            telegram_id=333333333,
            height=175.0,
            weight=70.0,
            birth_date=date(1990, 1, 1),
            gender="male",
            goal="maintain",
            activity_level="medium"
        )
        
        # Рассчитываем нормы
        user = await user_service.calculate_and_save_norms(333333333)
        
        assert user.bmr is not None
        assert user.tdee is not None
        assert user.daily_calories is not None
        assert user.daily_protein is not None
        assert user.daily_fat is not None
        assert user.daily_carbs is not None
        assert user.daily_water is not None
        assert user.is_onboarded == True
        
        # Проверяем разумность значений
        assert 1500 < user.bmr < 2500
        assert 2000 < user.tdee < 4000
        assert 1500 < user.daily_calories < 4000
    
    @pytest.mark.asyncio
    async def test_update_streak_first_activity(self, user_service):
        """Тест первой активности пользователя"""
        await user_service.get_or_create_user(telegram_id=444444444)
        
        user = await user_service.update_streak(444444444)
        
        assert user.current_streak == 1
        assert user.longest_streak == 1
        assert user.last_activity_date == date.today()
    
    @pytest.mark.asyncio
    async def test_update_streak_same_day(self, user_service, session):
        """Тест повторной активности в тот же день"""
        await user_service.get_or_create_user(telegram_id=555555555)
        
        # Первая активность
        await user_service.update_streak(555555555)
        
        # Повторная активность в тот же день
        user = await user_service.update_streak(555555555)
        
        assert user.current_streak == 1  # Не увеличивается
    
    @pytest.mark.asyncio
    async def test_add_xp(self, user_service):
        """Тест добавления XP"""
        await user_service.get_or_create_user(telegram_id=666666666)
        
        user = await user_service.add_xp(666666666, 50)
        
        assert user.xp == 50
        assert user.level == 1
        
        # Добавляем еще XP для повышения уровня
        user = await user_service.add_xp(666666666, 60)
        
        assert user.xp == 110
        assert user.level == 2  # 100+ XP = уровень 2
    
    @pytest.mark.asyncio
    async def test_get_user_stats_summary(self, user_service):
        """Тест получения сводки статистики"""
        await user_service.get_or_create_user(telegram_id=777777777)
        await user_service.update_user_profile(
            telegram_id=777777777,
            height=170.0,
            weight=65.0
        )
        
        summary = await user_service.get_user_stats_summary(777777777)
        
        assert summary is not None
        assert "user" in summary
        assert "bmi" in summary
        assert summary["bmi"] is not None
        assert summary["bmi"]["bmi"] > 0
