"""
Сервис для работы с пользователями
"""
from datetime import date, datetime
from typing import Optional
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from core.models.user import User, Gender, Goal, ActivityLevel
from services.calculator import CalculatorService
from bot.config import Constants


class UserService:
    """Сервис управления пользователями"""
    
    def __init__(self, session: AsyncSession):
        self.session = session
        self.calculator = CalculatorService()
    
    async def get_or_create_user(
        self,
        telegram_id: int,
        username: Optional[str] = None,
        first_name: Optional[str] = None,
        last_name: Optional[str] = None
    ) -> User:
        """Получить или создать пользователя"""
        result = await self.session.execute(
            select(User).where(User.telegram_id == telegram_id)
        )
        user = result.scalar_one_or_none()
        
        if user is None:
            user = User(
                telegram_id=telegram_id,
                username=username,
                first_name=first_name,
                last_name=last_name
            )
            self.session.add(user)
            await self.session.commit()
            await self.session.refresh(user)
        else:
            # Обновляем данные профиля если изменились
            if username != user.username or first_name != user.first_name:
                user.username = username
                user.first_name = first_name
                user.last_name = last_name
                await self.session.commit()
        
        return user
    
    async def get_user_by_telegram_id(self, telegram_id: int) -> Optional[User]:
        """Получить пользователя по Telegram ID"""
        result = await self.session.execute(
            select(User).where(User.telegram_id == telegram_id)
        )
        return result.scalar_one_or_none()
    
    async def update_user_profile(
        self,
        telegram_id: int,
        height: Optional[float] = None,
        weight: Optional[float] = None,
        birth_date: Optional[date] = None,
        gender: Optional[str] = None,
        goal: Optional[str] = None,
        activity_level: Optional[str] = None,
        goal_weight: Optional[float] = None
    ) -> User:
        """Обновить профиль пользователя"""
        user = await self.get_user_by_telegram_id(telegram_id)
        
        if user is None:
            raise ValueError(f"User with telegram_id {telegram_id} not found")
        
        if height is not None:
            user.height = height
        if weight is not None:
            user.weight = weight
        if birth_date is not None:
            user.birth_date = birth_date
        if gender is not None:
            user.gender = Gender(gender)
        if goal is not None:
            user.goal = Goal(goal)
        if activity_level is not None:
            user.activity_level = ActivityLevel(activity_level)
        if goal_weight is not None:
            user.goal_weight = goal_weight
        
        await self.session.commit()
        await self.session.refresh(user)
        
        return user
    
    async def calculate_and_save_norms(self, telegram_id: int) -> User:
        """Рассчитать и сохранить нормы КБЖУ для пользователя"""
        user = await self.get_user_by_telegram_id(telegram_id)
        
        if user is None:
            raise ValueError(f"User with telegram_id {telegram_id} not found")
        
        # Проверяем наличие необходимых данных
        if not all([user.height, user.weight, user.birth_date, user.gender]):
            raise ValueError("User profile is incomplete")
        
        age = user.age
        gender = user.gender.value
        activity = user.activity_level.value if user.activity_level else "medium"
        goal = user.goal.value if user.goal else "maintain"
        
        # Расчет BMR и TDEE
        bmr = self.calculator.calculate_bmr(user.weight, user.height, age, gender)
        tdee = self.calculator.calculate_tdee(bmr, activity)
        
        # Расчет целевых калорий
        target_calories = self.calculator.calculate_target_calories(tdee, goal, gender)
        
        # Расчет макросов
        macros = self.calculator.calculate_macros(target_calories, goal)
        
        # Расчет нормы воды
        water_norm = self.calculator.calculate_water_norm(user.weight, activity)
        
        # Сохранение
        user.bmr = bmr
        user.tdee = tdee
        user.daily_calories = target_calories
        user.daily_protein = macros["protein"]
        user.daily_fat = macros["fat"]
        user.daily_carbs = macros["carbs"]
        user.daily_water = water_norm
        user.is_onboarded = True
        
        await self.session.commit()
        await self.session.refresh(user)
        
        return user
    
    async def update_streak(self, telegram_id: int) -> User:
        """
        Обновить серию активности пользователя.
        
        Использует SELECT FOR UPDATE для предотвращения race condition
        при одновременных запросах от одного пользователя.
        """
        from sqlalchemy import select
        from sqlalchemy.orm import with_for_update
        
        # Блокируем запись для обновления (предотвращает race condition)
        result = await self.session.execute(
            select(User)
            .where(User.telegram_id == telegram_id)
            .with_for_update()
        )
        user = result.scalar_one_or_none()
        
        if user is None:
            raise ValueError(f"User with telegram_id {telegram_id} not found")
        
        today = date.today()
        
        if user.last_activity_date is None:
            # Первая активность
            user.current_streak = 1
        elif user.last_activity_date == today:
            # Уже была активность сегодня - не изменяем streak
            await self.session.commit()
            return user
        elif (today - user.last_activity_date).days == 1:
            # Продолжение серии
            user.current_streak += 1
        else:
            # Серия прервана
            user.current_streak = 1
        
        user.last_activity_date = today
        
        if user.current_streak > user.longest_streak:
            user.longest_streak = user.current_streak
        
        await self.session.commit()
        await self.session.refresh(user)
        
        return user
    
    async def add_xp(self, telegram_id: int, amount: int) -> User:
        """Добавить XP пользователю"""
        user = await self.get_user_by_telegram_id(telegram_id)
        
        if user is None:
            raise ValueError(f"User with telegram_id {telegram_id} not found")
        
        user.xp += amount
        
        # Проверка повышения уровня (каждые 100 XP)
        new_level = (user.xp // 100) + 1
        level_up = new_level > user.level
        user.level = new_level
        
        await self.session.commit()
        await self.session.refresh(user)
        
        return user
    
    async def get_user_stats_summary(self, telegram_id: int) -> dict:
        """Получить сводку статистики пользователя"""
        user = await self.get_user_by_telegram_id(telegram_id)
        
        if user is None:
            return None
        
        bmi_data = None
        if user.height and user.weight:
            bmi_data = self.calculator.calculate_bmi(user.weight, user.height)
        
        return {
            "user": user,
            "bmi": bmi_data,
            "xp": user.xp,
            "level": user.level,
            "streak": user.current_streak,
            "longest_streak": user.longest_streak
        }
