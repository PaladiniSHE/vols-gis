"""
Обработчики команд бота
"""
from aiogram import Router

from bot.handlers.start import router as start_router
from bot.handlers.onboarding import router as onboarding_router
from bot.handlers.food import router as food_router
from bot.handlers.water import router as water_router
from bot.handlers.weight import router as weight_router
from bot.handlers.stats import router as stats_router
from bot.handlers.profile import router as profile_router
from bot.handlers.reminders import router as reminders_router


def setup_routers() -> Router:
    """Настройка роутеров"""
    router = Router()
    
    router.include_router(start_router)
    router.include_router(onboarding_router)
    router.include_router(food_router)
    router.include_router(water_router)
    router.include_router(weight_router)
    router.include_router(stats_router)
    router.include_router(profile_router)
    router.include_router(reminders_router)
    
    return router
