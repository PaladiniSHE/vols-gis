"""
Модели базы данных
"""
from core.models.user import User
from core.models.food import Food, FoodEntry
from core.models.water import WaterEntry
from core.models.weight import WeightLog
from core.models.workout import Exercise, Workout, WorkoutExercise
from core.models.favorites import FavoriteFood
from core.models.reminders import Reminder, ReminderType

__all__ = [
    "User",
    "Food",
    "FoodEntry", 
    "WaterEntry",
    "WeightLog",
    "Exercise",
    "Workout",
    "WorkoutExercise",
    "FavoriteFood",
    "Reminder",
    "ReminderType"
]
