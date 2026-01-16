"""
Модели для питания
"""
from datetime import datetime, date
from typing import Optional
from sqlalchemy import String, Float, Integer, Date, DateTime, Boolean, ForeignKey, Enum as SQLEnum, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
import enum

from core.database import Base


class MealType(str, enum.Enum):
    """Тип приема пищи"""
    BREAKFAST = "breakfast"
    LUNCH = "lunch"
    DINNER = "dinner"
    SNACK = "snack"


class Food(Base):
    """Модель продукта"""
    __tablename__ = "foods"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(500), index=True)
    brand: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    barcode: Mapped[Optional[str]] = mapped_column(String(50), unique=True, index=True, nullable=True)
    
    # Нутриенты на 100г
    calories_100g: Mapped[float] = mapped_column(Float)
    protein_100g: Mapped[float] = mapped_column(Float, default=0)
    fat_100g: Mapped[float] = mapped_column(Float, default=0)
    carbs_100g: Mapped[float] = mapped_column(Float, default=0)
    fiber_100g: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    sugar_100g: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    
    # Типичная порция
    serving_size: Mapped[Optional[float]] = mapped_column(Float, nullable=True)  # граммы
    serving_name: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)  # "1 штука", "1 стакан"
    
    # Категория
    category: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    
    # Источник и верификация
    source: Mapped[str] = mapped_column(String(50), default="user")  # 'user', 'usda', 'openfoodfacts'
    is_verified: Mapped[bool] = mapped_column(Boolean, default=False)
    usage_count: Mapped[int] = mapped_column(Integer, default=0)
    
    # Создатель (для пользовательских продуктов)
    created_by_user_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("users.id"), nullable=True)
    
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f"<Food(id={self.id}, name={self.name}, cal={self.calories_100g})>"


class FoodEntry(Base):
    """Запись о приеме пищи"""
    __tablename__ = "food_entries"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"), index=True)
    food_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("foods.id"), nullable=True)
    
    # Если продукт добавлен вручную без создания в базе
    custom_food_name: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    
    meal_type: Mapped[MealType] = mapped_column(SQLEnum(MealType))
    portion_size: Mapped[float] = mapped_column(Float)  # граммы
    
    # Рассчитанные нутриенты на порцию
    calories: Mapped[float] = mapped_column(Float)
    protein: Mapped[float] = mapped_column(Float, default=0)
    fat: Mapped[float] = mapped_column(Float, default=0)
    carbs: Mapped[float] = mapped_column(Float, default=0)
    fiber: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    
    # Время записи
    logged_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    entry_date: Mapped[date] = mapped_column(Date, index=True)
    
    # Связи
    food: Mapped[Optional["Food"]] = relationship("Food", lazy="selectin")
    
    def __repr__(self):
        return f"<FoodEntry(id={self.id}, user_id={self.user_id}, calories={self.calories})>"
