"""
Модель пользователя
"""
from datetime import datetime, date
from typing import Optional
from sqlalchemy import BigInteger, String, Float, Integer, Date, DateTime, Boolean, Enum as SQLEnum
from sqlalchemy.orm import Mapped, mapped_column
import enum

from core.database import Base


class Gender(str, enum.Enum):
    """Пол пользователя"""
    MALE = "male"
    FEMALE = "female"


class Goal(str, enum.Enum):
    """Цель пользователя"""
    LOSE = "lose"
    MAINTAIN = "maintain"
    GAIN = "gain"


class ActivityLevel(str, enum.Enum):
    """Уровень активности"""
    MINIMAL = "minimal"
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    EXTREME = "extreme"


class User(Base):
    """Модель пользователя"""
    __tablename__ = "users"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    telegram_id: Mapped[int] = mapped_column(BigInteger, unique=True, index=True)
    username: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    first_name: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    last_name: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    
    # Физические параметры
    height: Mapped[Optional[float]] = mapped_column(Float, nullable=True)  # см
    weight: Mapped[Optional[float]] = mapped_column(Float, nullable=True)  # кг
    birth_date: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    gender: Mapped[Optional[Gender]] = mapped_column(SQLEnum(Gender), nullable=True)
    
    # Расчетные показатели
    bmr: Mapped[Optional[float]] = mapped_column(Float, nullable=True)  # Базовый метаболизм
    tdee: Mapped[Optional[float]] = mapped_column(Float, nullable=True)  # Суточный расход
    
    # Цели
    goal: Mapped[Optional[Goal]] = mapped_column(SQLEnum(Goal), nullable=True)
    goal_weight: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    activity_level: Mapped[Optional[ActivityLevel]] = mapped_column(
        SQLEnum(ActivityLevel), 
        nullable=True,
        default=ActivityLevel.MEDIUM
    )
    
    # Дневные нормы
    daily_calories: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    daily_protein: Mapped[Optional[float]] = mapped_column(Float, nullable=True)  # граммы
    daily_fat: Mapped[Optional[float]] = mapped_column(Float, nullable=True)  # граммы
    daily_carbs: Mapped[Optional[float]] = mapped_column(Float, nullable=True)  # граммы
    daily_water: Mapped[Optional[float]] = mapped_column(Float, nullable=True, default=2.0)  # литры
    
    # Геймификация
    xp: Mapped[int] = mapped_column(Integer, default=0)
    level: Mapped[int] = mapped_column(Integer, default=1)
    current_streak: Mapped[int] = mapped_column(Integer, default=0)
    longest_streak: Mapped[int] = mapped_column(Integer, default=0)
    last_activity_date: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    
    # Настройки
    notifications_enabled: Mapped[bool] = mapped_column(Boolean, default=True)
    timezone: Mapped[str] = mapped_column(String(50), default="Europe/Moscow")
    is_onboarded: Mapped[bool] = mapped_column(Boolean, default=False)
    
    # Метаданные
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[Optional[datetime]] = mapped_column(DateTime, onupdate=datetime.utcnow, nullable=True)
    
    def __repr__(self):
        return f"<User(id={self.id}, telegram_id={self.telegram_id}, name={self.first_name})>"
    
    @property
    def age(self) -> Optional[int]:
        """Возраст пользователя"""
        if self.birth_date:
            today = date.today()
            return today.year - self.birth_date.year - (
                (today.month, today.day) < (self.birth_date.month, self.birth_date.day)
            )
        return None
    
    @property
    def display_name(self) -> str:
        """Отображаемое имя"""
        if self.first_name:
            return self.first_name
        if self.username:
            return f"@{self.username}"
        return f"User {self.telegram_id}"
