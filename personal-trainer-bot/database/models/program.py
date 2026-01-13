"""
Модели программ тренировок и питания
"""
from sqlalchemy import Column, Integer, String, Boolean, Date, ForeignKey, Text, JSON
from sqlalchemy.orm import relationship
from datetime import date
from .base import Base, TimestampMixin


class WorkoutProgram(Base, TimestampMixin):
    """Программа тренировок"""
    __tablename__ = "workout_programs"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    
    # Информация о программе
    name = Column(String(100), nullable=False)
    description = Column(Text, nullable=True)
    goal = Column(String(50), nullable=True)  # weight_loss, muscle_gain, etc.
    level = Column(String(20), nullable=True)  # beginner, intermediate, advanced
    
    # Период действия
    start_date = Column(Date, nullable=False)
    end_date = Column(Date, nullable=True)
    duration_weeks = Column(Integer, default=4)
    current_week = Column(Integer, default=1)
    
    # Статус
    is_active = Column(Boolean, default=True)
    
    # Расписание тренировок на неделю
    # {"monday": {"type": "upper", "name": "Верх тела", "exercises": [...]}, ...}
    weekly_schedule = Column(JSON, default=dict)
    
    # Параметры прогрессии
    progression_rules = Column(JSON, default=dict)
    # {"weight_increase": 2.5, "reps_before_increase": 12}


class MealPlan(Base, TimestampMixin):
    """План питания"""
    __tablename__ = "meal_plans"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    
    # Период действия
    start_date = Column(Date, nullable=False)
    end_date = Column(Date, nullable=True)
    
    # Статус
    is_active = Column(Boolean, default=True)
    
    # Целевые значения
    target_calories = Column(Integer, nullable=False)
    target_protein = Column(Integer, nullable=False)
    target_fat = Column(Integer, nullable=False)
    target_carbs = Column(Integer, nullable=False)
    
    # Меню на неделю
    # {"monday": {"breakfast": {...}, "lunch": {...}, ...}, ...}
    weekly_menu = Column(JSON, default=dict)
    
    # Список покупок
    shopping_list = Column(JSON, default=list)


class ScheduledNotification(Base, TimestampMixin):
    """Запланированные уведомления"""
    __tablename__ = "scheduled_notifications"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    
    # Тип уведомления
    notification_type = Column(String(50), nullable=False)
    # morning_greeting, meal_reminder, workout_reminder, water_reminder, evening_summary
    
    # Время отправки
    send_time = Column(String(5), nullable=False)  # HH:MM
    days_of_week = Column(JSON, default=list)  # [1,2,3,4,5,6,7] - дни недели
    
    # Контент (может генерироваться динамически)
    message_template = Column(Text, nullable=True)
    
    # Статус
    is_active = Column(Boolean, default=True)
    last_sent = Column(Date, nullable=True)
