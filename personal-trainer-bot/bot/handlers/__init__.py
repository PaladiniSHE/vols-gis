from aiogram import Router

from .start import router as start_router
from .onboarding import router as onboarding_router
from .menu import router as menu_router
from .workout import router as workout_router
from .nutrition import router as nutrition_router
from .progress import router as progress_router


def setup_routers() -> Router:
    """Настроить все роутеры"""
    router = Router()
    
    router.include_router(start_router)
    router.include_router(onboarding_router)
    router.include_router(menu_router)
    router.include_router(workout_router)
    router.include_router(nutrition_router)
    router.include_router(progress_router)
    
    return router


__all__ = ["setup_routers"]
