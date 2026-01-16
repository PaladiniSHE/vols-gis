"""
Интеграционные тесты для FoodService
"""
import pytest
from datetime import date
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

from core.database import Base
from core.models.user import User
from core.models.food import Food, FoodEntry, MealType
from services.food_service import FoodService


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
async def test_foods(session):
    """Создать тестовые продукты"""
    foods = [
        Food(name="Куриная грудка", calories_100g=165, protein_100g=31, fat_100g=3.6, carbs_100g=0),
        Food(name="Рис белый", calories_100g=130, protein_100g=2.7, fat_100g=0.3, carbs_100g=28),
        Food(name="Яблоко", calories_100g=52, protein_100g=0.3, fat_100g=0.2, carbs_100g=14),
        Food(name="Молоко 2.5%", calories_100g=52, protein_100g=2.9, fat_100g=2.5, carbs_100g=4.7),
    ]
    
    for food in foods:
        session.add(food)
    
    await session.commit()
    
    for food in foods:
        await session.refresh(food)
    
    return foods


@pytest.fixture
def food_service(session):
    """Создать экземпляр FoodService"""
    return FoodService(session)


class TestFoodService:
    """Тесты для FoodService"""
    
    @pytest.mark.asyncio
    async def test_search_foods(self, food_service, test_foods):
        """Тест поиска продуктов"""
        results = await food_service.search_foods("курин")
        
        assert len(results) == 1
        assert results[0].name == "Куриная грудка"
    
    @pytest.mark.asyncio
    async def test_search_foods_no_results(self, food_service, test_foods):
        """Тест поиска без результатов"""
        results = await food_service.search_foods("несуществующий продукт")
        
        assert len(results) == 0
    
    @pytest.mark.asyncio
    async def test_search_foods_pagination(self, food_service, test_foods):
        """Тест пагинации поиска"""
        # Поиск с limit=2
        results = await food_service.search_foods("", limit=2, offset=0)
        assert len(results) == 2
        
        # Следующая страница
        results2 = await food_service.search_foods("", limit=2, offset=2)
        assert len(results2) == 2
    
    @pytest.mark.asyncio
    async def test_count_search_results(self, food_service, test_foods):
        """Тест подсчета результатов поиска"""
        count = await food_service.count_search_results("")
        assert count == 4
        
        count = await food_service.count_search_results("молоко")
        assert count == 1
    
    @pytest.mark.asyncio
    async def test_get_food_by_id(self, food_service, test_foods):
        """Тест получения продукта по ID"""
        food = await food_service.get_food_by_id(test_foods[0].id)
        
        assert food is not None
        assert food.name == "Куриная грудка"
    
    @pytest.mark.asyncio
    async def test_create_food(self, food_service, test_user):
        """Тест создания нового продукта"""
        food = await food_service.create_food(
            name="Творог 5%",
            calories_100g=121,
            protein_100g=17.2,
            fat_100g=5,
            carbs_100g=1.8,
            created_by_user_id=test_user.id
        )
        
        assert food.id is not None
        assert food.name == "Творог 5%"
        assert food.calories_100g == 121
        assert food.source == "user"
    
    @pytest.mark.asyncio
    async def test_add_food_entry(self, food_service, test_user, test_foods):
        """Тест добавления записи о еде"""
        entry = await food_service.add_food_entry(
            user_id=test_user.id,
            meal_type="breakfast",
            portion_size=150,
            food_id=test_foods[0].id  # Куриная грудка
        )
        
        assert entry.id is not None
        assert entry.meal_type == MealType.BREAKFAST
        assert entry.portion_size == 150
        
        # Проверяем расчет нутриентов (150г куриной грудки)
        assert entry.calories == 248  # 165 * 1.5
        assert entry.protein == 46.5  # 31 * 1.5
    
    @pytest.mark.asyncio
    async def test_get_daily_totals(self, food_service, test_user, test_foods):
        """Тест получения суммы за день"""
        today = date.today()
        
        # Добавляем записи
        await food_service.add_food_entry(
            user_id=test_user.id,
            meal_type="breakfast",
            portion_size=100,
            food_id=test_foods[0].id
        )
        await food_service.add_food_entry(
            user_id=test_user.id,
            meal_type="lunch",
            portion_size=200,
            food_id=test_foods[1].id
        )
        
        totals = await food_service.get_daily_totals(test_user.id, today)
        
        # 165 + 260 = 425 ккал
        assert totals["calories"] == 425
        assert totals["protein"] > 0
        assert totals["carbs"] > 0
    
    @pytest.mark.asyncio
    async def test_get_meal_totals(self, food_service, test_user, test_foods):
        """Тест получения суммы по приему пищи"""
        today = date.today()
        
        await food_service.add_food_entry(
            user_id=test_user.id,
            meal_type="breakfast",
            portion_size=100,
            food_id=test_foods[0].id
        )
        await food_service.add_food_entry(
            user_id=test_user.id,
            meal_type="breakfast",
            portion_size=50,
            food_id=test_foods[2].id  # Яблоко
        )
        
        totals = await food_service.get_meal_totals(test_user.id, today, "breakfast")
        
        # 165 + 26 = 191 ккал
        assert totals["calories"] == 191
    
    @pytest.mark.asyncio
    async def test_delete_food_entry(self, food_service, test_user, test_foods):
        """Тест удаления записи о еде"""
        entry = await food_service.add_food_entry(
            user_id=test_user.id,
            meal_type="dinner",
            portion_size=100,
            food_id=test_foods[0].id
        )
        
        # Удаляем
        result = await food_service.delete_food_entry(entry.id, test_user.id)
        assert result == True
        
        # Проверяем, что удалено
        totals = await food_service.get_daily_totals(test_user.id, date.today())
        assert totals["calories"] == 0
    
    @pytest.mark.asyncio
    async def test_delete_food_entry_wrong_user(self, food_service, test_user, test_foods, session):
        """Тест удаления записи чужим пользователем"""
        entry = await food_service.add_food_entry(
            user_id=test_user.id,
            meal_type="dinner",
            portion_size=100,
            food_id=test_foods[0].id
        )
        
        # Пытаемся удалить от другого пользователя
        result = await food_service.delete_food_entry(entry.id, 999999)
        assert result == False
    
    @pytest.mark.asyncio
    async def test_get_recent_foods(self, food_service, test_user, test_foods):
        """Тест получения недавних продуктов"""
        # Добавляем записи с разными продуктами
        await food_service.add_food_entry(
            user_id=test_user.id,
            meal_type="breakfast",
            portion_size=100,
            food_id=test_foods[0].id
        )
        await food_service.add_food_entry(
            user_id=test_user.id,
            meal_type="lunch",
            portion_size=200,
            food_id=test_foods[1].id
        )
        
        recent = await food_service.get_recent_foods(test_user.id, limit=5)
        
        assert len(recent) >= 1
