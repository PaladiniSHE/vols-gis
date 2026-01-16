"""
Интеграционные тесты для StatsService
"""
import pytest
from datetime import date, timedelta
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

from core.database import Base
from core.models.user import User
from core.models.food import Food, FoodEntry, MealType
from core.models.water import WaterEntry
from core.models.weight import WeightLog
from services.stats_service import StatsService


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
        first_name="Test",
        daily_calories=2000,
        daily_protein=150,
        daily_fat=65,
        daily_carbs=250,
        daily_water=2.0
    )
    session.add(user)
    await session.commit()
    await session.refresh(user)
    return user


@pytest.fixture
async def test_food(session):
    """Создать тестовый продукт"""
    food = Food(
        name="Тестовый продукт",
        calories_100g=100,
        protein_100g=10,
        fat_100g=5,
        carbs_100g=15
    )
    session.add(food)
    await session.commit()
    await session.refresh(food)
    return food


@pytest.fixture
def stats_service(session):
    """Создать экземпляр StatsService"""
    return StatsService(session)


class TestStatsService:
    """Тесты для StatsService"""
    
    @pytest.mark.asyncio
    async def test_get_daily_summary_empty(self, stats_service, test_user):
        """Тест дневной сводки без данных"""
        summary = await stats_service.get_daily_summary(test_user.id, date.today())
        
        assert summary["calories"] == 0
        assert summary["protein"] == 0
        assert summary["fat"] == 0
        assert summary["carbs"] == 0
        assert summary["water_ml"] == 0
        assert summary["water_liters"] == 0
    
    @pytest.mark.asyncio
    async def test_get_daily_summary_with_data(self, stats_service, test_user, test_food, session):
        """Тест дневной сводки с данными"""
        today = date.today()
        
        # Добавляем еду
        entry = FoodEntry(
            user_id=test_user.id,
            food_id=test_food.id,
            meal_type=MealType.BREAKFAST,
            portion_size=200,
            calories=200,
            protein=20,
            fat=10,
            carbs=30,
            entry_date=today
        )
        session.add(entry)
        
        # Добавляем воду
        water = WaterEntry(
            user_id=test_user.id,
            amount_ml=1500,
            entry_date=today
        )
        session.add(water)
        
        await session.commit()
        
        summary = await stats_service.get_daily_summary(test_user.id, today)
        
        assert summary["calories"] == 200
        assert summary["protein"] == 20
        assert summary["water_ml"] == 1500
        assert summary["water_liters"] == 1.5
    
    @pytest.mark.asyncio
    async def test_get_weekly_summary(self, stats_service, test_user, test_food, session):
        """Тест недельной сводки"""
        today = date.today()
        
        # Добавляем данные за несколько дней
        for i in range(3):
            day = today - timedelta(days=i)
            entry = FoodEntry(
                user_id=test_user.id,
                food_id=test_food.id,
                meal_type=MealType.LUNCH,
                portion_size=100,
                calories=100 + i * 50,
                protein=10,
                fat=5,
                carbs=15,
                entry_date=day
            )
            session.add(entry)
        
        await session.commit()
        
        weekly = await stats_service.get_weekly_summary(test_user.id)
        
        assert len(weekly) == 7  # 7 дней
        # Проверяем что есть данные
        days_with_data = [d for d in weekly if d["calories"] > 0]
        assert len(days_with_data) == 3
    
    @pytest.mark.asyncio
    async def test_get_weekly_averages(self, stats_service, test_user, test_food, session):
        """Тест расчета средних за неделю"""
        today = date.today()
        
        # День 1: 1000 ккал (одна запись)
        entry1 = FoodEntry(
            user_id=test_user.id,
            food_id=test_food.id,
            meal_type=MealType.BREAKFAST,
            portion_size=100,
            calories=1000,
            protein=50,
            fat=30,
            carbs=100,
            entry_date=today
        )
        session.add(entry1)
        
        # День 2: 2000 ккал (две записи по 1000)
        yesterday = today - timedelta(days=1)
        entry2a = FoodEntry(
            user_id=test_user.id,
            food_id=test_food.id,
            meal_type=MealType.BREAKFAST,
            portion_size=100,
            calories=1000,
            protein=50,
            fat=30,
            carbs=100,
            entry_date=yesterday
        )
        entry2b = FoodEntry(
            user_id=test_user.id,
            food_id=test_food.id,
            meal_type=MealType.LUNCH,
            portion_size=100,
            calories=1000,
            protein=50,
            fat=30,
            carbs=100,
            entry_date=yesterday
        )
        session.add(entry2a)
        session.add(entry2b)
        
        await session.commit()
        
        averages = await stats_service.get_weekly_averages(test_user.id)
        
        # Среднее по дням: (1000 + 2000) / 2 = 1500
        # А не по записям: (1000 + 1000 + 1000) / 3 = 1000
        assert averages["avg_calories"] == 1500
        assert averages["days_with_data"] == 2
    
    @pytest.mark.asyncio
    async def test_log_weight(self, stats_service, test_user):
        """Тест записи веса"""
        log = await stats_service.log_weight(
            user_id=test_user.id,
            weight=75.5
        )
        
        assert log.id is not None
        assert log.weight == 75.5
        assert log.entry_date == date.today()
    
    @pytest.mark.asyncio
    async def test_log_weight_update_same_day(self, stats_service, test_user):
        """Тест обновления веса в тот же день"""
        today = date.today()
        
        # Первая запись
        await stats_service.log_weight(test_user.id, 75.0, entry_date=today)
        
        # Обновление
        log = await stats_service.log_weight(test_user.id, 74.5, entry_date=today)
        
        # Должна быть одна запись с обновленным весом
        history = await stats_service.get_weight_history(test_user.id, days=30)
        today_logs = [h for h in history if h.entry_date == today]
        
        assert len(today_logs) == 1
        assert today_logs[0].weight == 74.5
    
    @pytest.mark.asyncio
    async def test_get_weight_history(self, stats_service, test_user, session):
        """Тест получения истории веса"""
        today = date.today()
        
        # Добавляем записи за несколько дней
        for i in range(5):
            log = WeightLog(
                user_id=test_user.id,
                weight=75 - i * 0.5,
                entry_date=today - timedelta(days=i)
            )
            session.add(log)
        
        await session.commit()
        
        history = await stats_service.get_weight_history(test_user.id, days=30)
        
        assert len(history) == 5
        # Проверяем порядок (по дате возрастания)
        assert history[0].entry_date < history[-1].entry_date
    
    @pytest.mark.asyncio
    async def test_get_weight_change(self, stats_service, test_user, session):
        """Тест расчета изменения веса"""
        today = date.today()
        
        # Первая запись (неделю назад)
        log1 = WeightLog(
            user_id=test_user.id,
            weight=76.0,
            entry_date=today - timedelta(days=7)
        )
        session.add(log1)
        
        # Последняя запись (сегодня)
        log2 = WeightLog(
            user_id=test_user.id,
            weight=75.0,
            entry_date=today
        )
        session.add(log2)
        
        await session.commit()
        
        change = await stats_service.get_weight_change(test_user.id, days=7)
        
        assert change == -1.0  # Похудел на 1 кг
    
    @pytest.mark.asyncio
    async def test_get_weight_change_no_data(self, stats_service, test_user):
        """Тест изменения веса без данных"""
        change = await stats_service.get_weight_change(test_user.id, days=7)
        
        assert change is None
    
    @pytest.mark.asyncio
    async def test_calculate_progress(self, stats_service, test_user, test_food, session):
        """Тест расчета прогресса к целям"""
        today = date.today()
        
        # Добавляем 50% от нормы калорий
        entry = FoodEntry(
            user_id=test_user.id,
            food_id=test_food.id,
            meal_type=MealType.LUNCH,
            portion_size=100,
            calories=1000,  # 50% от 2000
            protein=75,     # 50% от 150
            fat=32,         # ~50% от 65
            carbs=125,      # 50% от 250
            entry_date=today
        )
        session.add(entry)
        
        # Добавляем воду
        water = WaterEntry(
            user_id=test_user.id,
            amount_ml=1000,  # 50% от 2л
            entry_date=today
        )
        session.add(water)
        
        await session.commit()
        
        progress = await stats_service.calculate_progress(
            test_user.id,
            {
                "calories": test_user.daily_calories,
                "protein": test_user.daily_protein,
                "fat": test_user.daily_fat,
                "carbs": test_user.daily_carbs,
                "water": test_user.daily_water
            }
        )
        
        assert progress["calories"]["percent"] == 50
        assert progress["protein"]["percent"] == 50
        assert progress["water"]["percent"] == 50
