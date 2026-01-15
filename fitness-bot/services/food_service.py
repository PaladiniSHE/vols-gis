"""
Сервис для работы с питанием
"""
from datetime import date, datetime
from typing import List, Optional, Dict
from sqlalchemy import select, func, and_
from sqlalchemy.ext.asyncio import AsyncSession

from core.models.food import Food, FoodEntry, MealType
from services.calculator import CalculatorService


class FoodService:
    """Сервис управления питанием"""
    
    def __init__(self, session: AsyncSession):
        self.session = session
        self.calculator = CalculatorService()
    
    async def search_foods(self, query: str, limit: int = 10) -> List[Food]:
        """Поиск продуктов по названию"""
        result = await self.session.execute(
            select(Food)
            .where(Food.name.ilike(f"%{query}%"))
            .order_by(Food.usage_count.desc())
            .limit(limit)
        )
        return result.scalars().all()
    
    async def get_food_by_id(self, food_id: int) -> Optional[Food]:
        """Получить продукт по ID"""
        result = await self.session.execute(
            select(Food).where(Food.id == food_id)
        )
        return result.scalar_one_or_none()
    
    async def get_food_by_barcode(self, barcode: str) -> Optional[Food]:
        """Получить продукт по штрих-коду"""
        result = await self.session.execute(
            select(Food).where(Food.barcode == barcode)
        )
        return result.scalar_one_or_none()
    
    async def create_food(
        self,
        name: str,
        calories_100g: float,
        protein_100g: float = 0,
        fat_100g: float = 0,
        carbs_100g: float = 0,
        brand: Optional[str] = None,
        barcode: Optional[str] = None,
        category: Optional[str] = None,
        created_by_user_id: Optional[int] = None
    ) -> Food:
        """Создать новый продукт"""
        food = Food(
            name=name,
            calories_100g=calories_100g,
            protein_100g=protein_100g,
            fat_100g=fat_100g,
            carbs_100g=carbs_100g,
            brand=brand,
            barcode=barcode,
            category=category,
            created_by_user_id=created_by_user_id,
            source="user"
        )
        
        self.session.add(food)
        await self.session.commit()
        await self.session.refresh(food)
        
        return food
    
    async def add_food_entry(
        self,
        user_id: int,
        meal_type: str,
        portion_size: float,
        food_id: Optional[int] = None,
        custom_food_name: Optional[str] = None,
        calories: Optional[float] = None,
        protein: Optional[float] = None,
        fat: Optional[float] = None,
        carbs: Optional[float] = None,
        entry_date: Optional[date] = None
    ) -> FoodEntry:
        """Добавить запись о приеме пищи"""
        if entry_date is None:
            entry_date = date.today()
        
        # Если указан food_id, получаем нутриенты из базы
        if food_id:
            food = await self.get_food_by_id(food_id)
            if food:
                nutrients = self.calculator.calculate_food_nutrients(
                    food.calories_100g,
                    food.protein_100g,
                    food.fat_100g,
                    food.carbs_100g,
                    portion_size
                )
                calories = nutrients["calories"]
                protein = nutrients["protein"]
                fat = nutrients["fat"]
                carbs = nutrients["carbs"]
                
                # Увеличиваем счетчик использования
                food.usage_count += 1
        
        entry = FoodEntry(
            user_id=user_id,
            food_id=food_id,
            custom_food_name=custom_food_name,
            meal_type=MealType(meal_type),
            portion_size=portion_size,
            calories=calories or 0,
            protein=protein or 0,
            fat=fat or 0,
            carbs=carbs or 0,
            entry_date=entry_date
        )
        
        self.session.add(entry)
        await self.session.commit()
        await self.session.refresh(entry)
        
        return entry
    
    async def get_entries_by_date(
        self,
        user_id: int,
        entry_date: date
    ) -> List[FoodEntry]:
        """Получить записи питания за день"""
        result = await self.session.execute(
            select(FoodEntry)
            .where(
                and_(
                    FoodEntry.user_id == user_id,
                    FoodEntry.entry_date == entry_date
                )
            )
            .order_by(FoodEntry.logged_at)
        )
        return result.scalars().all()
    
    async def get_entries_by_meal(
        self,
        user_id: int,
        entry_date: date,
        meal_type: str
    ) -> List[FoodEntry]:
        """Получить записи по типу приема пищи"""
        result = await self.session.execute(
            select(FoodEntry)
            .where(
                and_(
                    FoodEntry.user_id == user_id,
                    FoodEntry.entry_date == entry_date,
                    FoodEntry.meal_type == MealType(meal_type)
                )
            )
            .order_by(FoodEntry.logged_at)
        )
        return result.scalars().all()
    
    async def get_daily_totals(self, user_id: int, entry_date: date) -> Dict[str, float]:
        """Получить суммарные показатели за день"""
        result = await self.session.execute(
            select(
                func.sum(FoodEntry.calories).label("calories"),
                func.sum(FoodEntry.protein).label("protein"),
                func.sum(FoodEntry.fat).label("fat"),
                func.sum(FoodEntry.carbs).label("carbs")
            )
            .where(
                and_(
                    FoodEntry.user_id == user_id,
                    FoodEntry.entry_date == entry_date
                )
            )
        )
        row = result.one()
        
        return {
            "calories": float(row.calories or 0),
            "protein": float(row.protein or 0),
            "fat": float(row.fat or 0),
            "carbs": float(row.carbs or 0)
        }
    
    async def get_meal_totals(
        self,
        user_id: int,
        entry_date: date,
        meal_type: str
    ) -> Dict[str, float]:
        """Получить суммарные показатели за прием пищи"""
        result = await self.session.execute(
            select(
                func.sum(FoodEntry.calories).label("calories"),
                func.sum(FoodEntry.protein).label("protein"),
                func.sum(FoodEntry.fat).label("fat"),
                func.sum(FoodEntry.carbs).label("carbs")
            )
            .where(
                and_(
                    FoodEntry.user_id == user_id,
                    FoodEntry.entry_date == entry_date,
                    FoodEntry.meal_type == MealType(meal_type)
                )
            )
        )
        row = result.one()
        
        return {
            "calories": float(row.calories or 0),
            "protein": float(row.protein or 0),
            "fat": float(row.fat or 0),
            "carbs": float(row.carbs or 0)
        }
    
    async def delete_food_entry(self, entry_id: int, user_id: int) -> bool:
        """Удалить запись о еде"""
        result = await self.session.execute(
            select(FoodEntry)
            .where(
                and_(
                    FoodEntry.id == entry_id,
                    FoodEntry.user_id == user_id
                )
            )
        )
        entry = result.scalar_one_or_none()
        
        if entry:
            await self.session.delete(entry)
            await self.session.commit()
            return True
        return False
    
    async def get_recent_foods(self, user_id: int, limit: int = 10) -> List[Food]:
        """Получить недавно использованные продукты"""
        result = await self.session.execute(
            select(Food)
            .join(FoodEntry, Food.id == FoodEntry.food_id)
            .where(FoodEntry.user_id == user_id)
            .order_by(FoodEntry.logged_at.desc())
            .distinct()
            .limit(limit)
        )
        return result.scalars().all()
