"""
Модели для тренировок
"""
from datetime import datetime, date
from typing import Optional, List
from sqlalchemy import String, Float, Integer, Date, DateTime, ForeignKey, Text, Enum as SQLEnum, JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship
import enum

from core.database import Base


class MuscleGroup(str, enum.Enum):
    """Группы мышц"""
    CHEST = "chest"
    BACK = "back"
    SHOULDERS = "shoulders"
    BICEPS = "biceps"
    TRICEPS = "triceps"
    LEGS = "legs"
    ABS = "abs"
    CARDIO = "cardio"
    FULL_BODY = "full_body"


class ExerciseType(str, enum.Enum):
    """Тип упражнения"""
    STRENGTH = "strength"
    CARDIO = "cardio"
    FLEXIBILITY = "flexibility"


class Exercise(Base):
    """Упражнение"""
    __tablename__ = "exercises"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(255), index=True)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    exercise_type: Mapped[ExerciseType] = mapped_column(SQLEnum(ExerciseType))
    muscle_group: Mapped[MuscleGroup] = mapped_column(SQLEnum(MuscleGroup))
    
    # Мультимедиа
    video_url: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    gif_url: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    
    # Калории за минуту (примерное значение)
    calories_per_minute: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    
    # Инструкции
    instructions: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    tips: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    def __repr__(self):
        return f"<Exercise(id={self.id}, name={self.name})>"


class Workout(Base):
    """Тренировка пользователя"""
    __tablename__ = "workouts"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"), index=True)
    
    name: Mapped[str] = mapped_column(String(255))
    workout_type: Mapped[ExerciseType] = mapped_column(SQLEnum(ExerciseType))
    
    started_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    finished_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    duration_minutes: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    
    calories_burned: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    
    notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    rating: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)  # 1-5
    
    entry_date: Mapped[date] = mapped_column(Date, index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    
    # Связи
    exercises: Mapped[List["WorkoutExercise"]] = relationship("WorkoutExercise", back_populates="workout", lazy="selectin")
    
    def __repr__(self):
        return f"<Workout(id={self.id}, name={self.name})>"


class WorkoutExercise(Base):
    """Упражнение в тренировке"""
    __tablename__ = "workout_exercises"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    workout_id: Mapped[int] = mapped_column(Integer, ForeignKey("workouts.id"), index=True)
    exercise_id: Mapped[int] = mapped_column(Integer, ForeignKey("exercises.id"))
    
    order: Mapped[int] = mapped_column(Integer, default=0)
    
    # Для силовых упражнений
    sets_completed: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    reps_per_set: Mapped[Optional[List[int]]] = mapped_column(JSON, nullable=True)  # [12, 10, 8]
    weight_per_set: Mapped[Optional[List[float]]] = mapped_column(JSON, nullable=True)  # [60, 65, 70]
    
    # Для кардио
    duration_seconds: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    distance_meters: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    
    notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    # Связи
    workout: Mapped["Workout"] = relationship("Workout", back_populates="exercises")
    exercise: Mapped["Exercise"] = relationship("Exercise", lazy="selectin")
    
    def __repr__(self):
        return f"<WorkoutExercise(id={self.id}, workout_id={self.workout_id})>"
