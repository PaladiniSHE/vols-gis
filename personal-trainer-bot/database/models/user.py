"""
Модель пользователя
"""
from sqlalchemy import Column, Integer, BigInteger, String, Boolean, DateTime, JSON
from sqlalchemy.orm import relationship
from datetime import datetime
from .base import Base, TimestampMixin


class User(Base, TimestampMixin):
    """Модель пользователя Telegram"""
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    telegram_id = Column(BigInteger, unique=True, nullable=False, index=True)
    username = Column(String(255), nullable=True)
    first_name = Column(String(255), nullable=True)
    last_name = Column(String(255), nullable=True)
    language_code = Column(String(10), default="ru")
    
    # Статус онбординга
    is_onboarded = Column(Boolean, default=False)
    onboarding_step = Column(String(50), default="start")
    
    # Настройки уведомлений
    notifications_enabled = Column(Boolean, default=True)
    wake_time = Column(String(5), default="07:00")  # HH:MM
    sleep_time = Column(String(5), default="23:00")
    timezone = Column(String(50), default="Europe/Moscow")
    
    # Статус
    is_active = Column(Boolean, default=True)
    is_paused = Column(Boolean, default=False)
    last_activity = Column(DateTime, default=datetime.utcnow)
    
    # Статистика
    streak_days = Column(Integer, default=0)
    total_workouts = Column(Integer, default=0)
    
    # Связи
    profile = relationship("UserProfile", back_populates="user", uselist=False)
    weight_logs = relationship("WeightLog", back_populates="user")
    workout_logs = relationship("WorkoutLog", back_populates="user")
    nutrition_logs = relationship("NutritionLog", back_populates="user")
    
    def __repr__(self):
        return f"<User(id={self.id}, telegram_id={self.telegram_id}, name={self.first_name})>"
