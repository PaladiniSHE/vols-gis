"""
Бизнес-логика приложения
"""
from services.calculator import CalculatorService
from services.user_service import UserService
from services.food_service import FoodService
from services.water_service import WaterService
from services.stats_service import StatsService

__all__ = [
    "CalculatorService",
    "UserService",
    "FoodService",
    "WaterService",
    "StatsService"
]
