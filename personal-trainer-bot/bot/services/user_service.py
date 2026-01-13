"""
Сервис для работы с пользователями
"""
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import Optional, Dict, Any

from database.models import User, UserProfile


class UserService:
    """Сервис для работы с пользователями"""
    
    @staticmethod
    async def get_user_by_telegram_id(session: AsyncSession, telegram_id: int) -> Optional[User]:
        """Получить пользователя по Telegram ID"""
        result = await session.execute(
            select(User).where(User.telegram_id == telegram_id)
        )
        return result.scalar_one_or_none()
    
    @staticmethod
    async def get_or_create_user(session: AsyncSession, telegram_id: int, 
                                  user_data: Dict[str, Any]) -> User:
        """Получить или создать пользователя"""
        user = await UserService.get_user_by_telegram_id(session, telegram_id)
        
        if not user:
            user = User(
                telegram_id=telegram_id,
                username=user_data.get("username"),
                first_name=user_data.get("first_name"),
                last_name=user_data.get("last_name"),
                language_code=user_data.get("language_code", "ru")
            )
            session.add(user)
            await session.flush()
            
            # Создаём пустой профиль
            profile = UserProfile(user_id=user.id)
            session.add(profile)
            await session.commit()
        
        return user
    
    @staticmethod
    async def update_profile(session: AsyncSession, user_id: int, 
                            profile_data: Dict[str, Any]) -> Optional[UserProfile]:
        """Обновить профиль пользователя"""
        result = await session.execute(
            select(UserProfile).where(UserProfile.user_id == user_id)
        )
        profile = result.scalar_one_or_none()
        
        if profile:
            for key, value in profile_data.items():
                if hasattr(profile, key):
                    setattr(profile, key, value)
            
            # Пересчитываем метрики
            profile.calculate_metrics()
            await session.commit()
        
        return profile
    
    @staticmethod
    async def get_user_profile_dict(session: AsyncSession, telegram_id: int) -> Dict[str, Any]:
        """Получить профиль пользователя в виде словаря"""
        user = await UserService.get_user_by_telegram_id(session, telegram_id)
        
        if not user or not user.profile:
            return {}
        
        profile = user.profile
        
        return {
            "name": profile.name,
            "age": profile.age,
            "gender": profile.gender,
            "height": profile.height,
            "current_weight": profile.current_weight,
            "target_weight": profile.target_weight,
            "primary_goal": profile.primary_goal,
            "fitness_level": profile.fitness_level,
            "training_days_per_week": profile.training_days_per_week,
            "training_location": profile.training_location,
            "training_duration": profile.training_duration,
            "diet_type": profile.diet_type,
            "allergies": profile.allergies or [],
            "health_conditions": profile.health_conditions or [],
            "disliked_foods": profile.disliked_foods or [],
            "available_equipment": profile.available_equipment or [],
            "target_calories": profile.target_calories,
            "target_protein": profile.target_protein,
            "target_fat": profile.target_fat,
            "target_carbs": profile.target_carbs,
            "target_water": profile.target_water,
            "meals_per_day": profile.meals_per_day
        }
    
    @staticmethod
    async def complete_onboarding(session: AsyncSession, user_id: int) -> bool:
        """Завершить онбординг пользователя"""
        result = await session.execute(
            select(User).where(User.id == user_id)
        )
        user = result.scalar_one_or_none()
        
        if user:
            user.is_onboarded = True
            await session.commit()
            return True
        
        return False
    
    @staticmethod
    async def update_streak(session: AsyncSession, user_id: int, 
                           increment: bool = True) -> int:
        """Обновить streak пользователя"""
        result = await session.execute(
            select(User).where(User.id == user_id)
        )
        user = result.scalar_one_or_none()
        
        if user:
            if increment:
                user.streak_days += 1
            else:
                user.streak_days = 0
            
            await session.commit()
            return user.streak_days
        
        return 0
