"""
Конфигурация бота
"""
import os
from typing import List, Optional
from pydantic_settings import BaseSettings
from pydantic import Field


class Settings(BaseSettings):
    """Настройки приложения"""
    
    # Telegram
    bot_token: str = Field(..., env="BOT_TOKEN")
    bot_admin_ids: List[int] = Field(default_factory=list, env="BOT_ADMIN_IDS")
    
    # Database
    database_url: str = Field(
        default="sqlite+aiosqlite:///./fitness_bot.db",
        env="DATABASE_URL"
    )
    
    # Redis (optional, recommended for production)
    redis_url: Optional[str] = Field(default=None, env="REDIS_URL")
    
    # Monitoring (Sentry)
    sentry_dsn: Optional[str] = Field(default=None, env="SENTRY_DSN")
    sentry_environment: str = Field(default="development", env="SENTRY_ENVIRONMENT")
    
    # Application
    debug: bool = Field(default=False, env="DEBUG")
    timezone: str = Field(default="Europe/Moscow", env="TIMEZONE")
    
    # Rate limiting
    rate_limit_interval: float = Field(default=0.5, env="RATE_LIMIT_INTERVAL")
    rate_limit_max_per_minute: int = Field(default=30, env="RATE_LIMIT_MAX_PER_MINUTE")
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        extra = "ignore"


# Глобальный экземпляр настроек
settings = Settings()


# Константы приложения
class Constants:
    """Константы приложения"""
    
    # Коэффициенты активности для расчета TDEE
    ACTIVITY_LEVELS = {
        "minimal": {"factor": 1.2, "name": "🛋️ Минимальная", "desc": "Сидячий образ жизни"},
        "low": {"factor": 1.375, "name": "🚶 Низкая", "desc": "1-2 тренировки в неделю"},
        "medium": {"factor": 1.55, "name": "🏃 Средняя", "desc": "3-4 тренировки в неделю"},
        "high": {"factor": 1.725, "name": "🔥 Высокая", "desc": "5-6 тренировок в неделю"},
        "extreme": {"factor": 1.9, "name": "⚡ Очень высокая", "desc": "Профессиональный спорт"}
    }
    
    # Цели пользователя
    GOALS = {
        "lose": {"name": "🔥 Похудеть", "deficit": -500, "protein_ratio": 0.30},
        "maintain": {"name": "⚖️ Поддерживать вес", "deficit": 0, "protein_ratio": 0.25},
        "gain": {"name": "💪 Набрать массу", "deficit": 500, "protein_ratio": 0.25}
    }
    
    # Типы приемов пищи
    MEAL_TYPES = {
        "breakfast": {"name": "🌅 Завтрак", "emoji": "🍳"},
        "lunch": {"name": "☀️ Обед", "emoji": "🍜"},
        "dinner": {"name": "🌆 Ужин", "emoji": "🍽️"},
        "snack": {"name": "🍎 Перекус", "emoji": "🥤"}
    }
    
    # Объемы воды
    WATER_AMOUNTS = [100, 200, 250, 300, 500]
    
    # Минимальные калории
    MIN_CALORIES_MALE = 1500
    MIN_CALORIES_FEMALE = 1200
    
    # XP за действия
    XP_LOG_FOOD = 10
    XP_LOG_WATER = 5
    XP_LOG_WEIGHT = 15
    XP_WORKOUT = 50
    XP_DAILY_GOAL = 25
    XP_STREAK_WEEK = 100
