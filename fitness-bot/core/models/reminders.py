"""
Модель напоминаний
"""
from datetime import datetime, time
from typing import Optional
from sqlalchemy import Integer, String, Time, DateTime, Boolean, ForeignKey, Enum as SQLEnum
from sqlalchemy.orm import Mapped, mapped_column
import enum

from core.database import Base


class ReminderType(str, enum.Enum):
    """Тип напоминания"""
    MEAL_BREAKFAST = "meal_breakfast"
    MEAL_LUNCH = "meal_lunch"
    MEAL_DINNER = "meal_dinner"
    WATER = "water"
    WEIGHT = "weight"
    WORKOUT = "workout"
    CUSTOM = "custom"


class Reminder(Base):
    """Напоминание пользователя"""
    __tablename__ = "reminders"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"), index=True)
    
    reminder_type: Mapped[ReminderType] = mapped_column(SQLEnum(ReminderType))
    
    # Время напоминания
    time: Mapped[time] = mapped_column(Time)
    
    # Дни недели (битовая маска: Пн=1, Вт=2, Ср=4, Чт=8, Пт=16, Сб=32, Вс=64)
    # 127 = все дни, 31 = будни, 96 = выходные
    weekdays_mask: Mapped[int] = mapped_column(Integer, default=127)
    
    # Текст напоминания (для кастомных)
    message: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    
    # Статус
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    
    # Последнее срабатывание
    last_triggered: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f"<Reminder(id={self.id}, type={self.reminder_type}, time={self.time})>"
    
    def should_trigger_on_weekday(self, weekday: int) -> bool:
        """Проверить, должно ли напоминание сработать в этот день недели (0=Пн, 6=Вс)"""
        bit = 1 << weekday
        return bool(self.weekdays_mask & bit)
