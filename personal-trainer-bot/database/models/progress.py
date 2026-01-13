"""
Модели для отслеживания прогресса
"""
from sqlalchemy import Column, Integer, Float, String, Boolean, Date, DateTime, ForeignKey, Text, JSON
from sqlalchemy.orm import relationship
from datetime import datetime, date
from .base import Base, TimestampMixin


class WeightLog(Base, TimestampMixin):
    """Лог измерений веса"""
    __tablename__ = "weight_logs"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    date = Column(Date, default=date.today, nullable=False)
    weight = Column(Float, nullable=False)
    note = Column(String(255), nullable=True)
    
    user = relationship("User", back_populates="weight_logs")
    
    def __repr__(self):
        return f"<WeightLog(user_id={self.user_id}, date={self.date}, weight={self.weight})>"


class MeasurementLog(Base, TimestampMixin):
    """Лог замеров тела"""
    __tablename__ = "measurement_logs"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    date = Column(Date, default=date.today, nullable=False)
    
    # Замеры в см
    chest = Column(Float, nullable=True)
    waist = Column(Float, nullable=True)
    hips = Column(Float, nullable=True)
    bicep_left = Column(Float, nullable=True)
    bicep_right = Column(Float, nullable=True)
    thigh_left = Column(Float, nullable=True)
    thigh_right = Column(Float, nullable=True)
    
    note = Column(String(255), nullable=True)


class WorkoutLog(Base, TimestampMixin):
    """Лог тренировок"""
    __tablename__ = "workout_logs"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    date = Column(Date, default=date.today, nullable=False)
    
    # Информация о тренировке
    workout_type = Column(String(50), nullable=True)  # strength, cardio, hiit, yoga
    workout_name = Column(String(100), nullable=True)
    duration_minutes = Column(Integer, nullable=True)
    
    # Статус
    status = Column(String(20), default="completed")  # completed, partial, skipped
    completion_percent = Column(Integer, default=100)
    
    # Детали (упражнения, веса, повторы)
    exercises = Column(JSON, default=list)
    # [{"name": "Жим лёжа", "sets": [{"weight": 60, "reps": 10}, ...]}]
    
    # Субъективные метрики
    perceived_effort = Column(Integer, nullable=True)  # 1-10
    mood_before = Column(Integer, nullable=True)  # 1-10
    mood_after = Column(Integer, nullable=True)  # 1-10
    
    note = Column(Text, nullable=True)
    
    user = relationship("User", back_populates="workout_logs")
    
    def __repr__(self):
        return f"<WorkoutLog(user_id={self.user_id}, date={self.date}, type={self.workout_type})>"


class NutritionLog(Base, TimestampMixin):
    """Лог питания"""
    __tablename__ = "nutrition_logs"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    date = Column(Date, default=date.today, nullable=False)
    
    # Приёмы пищи
    meals = Column(JSON, default=dict)
    # {"breakfast": {"eaten": True, "on_plan": True}, "lunch": {...}, ...}
    
    # Итоги дня
    total_calories = Column(Integer, nullable=True)
    total_protein = Column(Integer, nullable=True)
    total_fat = Column(Integer, nullable=True)
    total_carbs = Column(Integer, nullable=True)
    water_liters = Column(Float, default=0)
    
    # Статус
    adherence_percent = Column(Integer, default=100)  # Соблюдение плана
    had_cheat = Column(Boolean, default=False)
    
    note = Column(Text, nullable=True)
    
    user = relationship("User", back_populates="nutrition_logs")
    
    def __repr__(self):
        return f"<NutritionLog(user_id={self.user_id}, date={self.date})>"


class DailyLog(Base, TimestampMixin):
    """Общий дневной лог (сводка)"""
    __tablename__ = "daily_logs"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    date = Column(Date, default=date.today, nullable=False, unique=True)
    
    # Сон
    sleep_hours = Column(Float, nullable=True)
    sleep_quality = Column(Integer, nullable=True)  # 1-10
    
    # Самочувствие
    energy_level = Column(Integer, nullable=True)  # 1-10
    stress_level = Column(Integer, nullable=True)  # 1-10
    mood = Column(Integer, nullable=True)  # 1-10
    
    # Общая оценка дня
    day_rating = Column(Integer, nullable=True)  # 1-10
    
    note = Column(Text, nullable=True)
