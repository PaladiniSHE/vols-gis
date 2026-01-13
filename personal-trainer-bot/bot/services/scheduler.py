"""
Планировщик уведомлений
"""
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from datetime import datetime, time
from typing import Optional, Callable
import pytz

from config import settings
from loguru import logger


class NotificationScheduler:
    """Планировщик уведомлений для пользователей"""
    
    def __init__(self):
        self.scheduler = AsyncIOScheduler(timezone=pytz.timezone(settings.default_timezone))
        self.bot = None
        self.session_factory = None
    
    def init(self, bot, session_factory):
        """Инициализация с ботом и фабрикой сессий БД"""
        self.bot = bot
        self.session_factory = session_factory
    
    def start(self):
        """Запуск планировщика"""
        if not self.scheduler.running:
            self.scheduler.start()
            logger.info("Notification scheduler started")
    
    def stop(self):
        """Остановка планировщика"""
        if self.scheduler.running:
            self.scheduler.shutdown()
            logger.info("Notification scheduler stopped")
    
    async def schedule_user_notifications(self, user_id: int, telegram_id: int, 
                                          wake_time: str = "07:00",
                                          sleep_time: str = "23:00",
                                          timezone: str = "Europe/Moscow"):
        """Настройка уведомлений для пользователя"""
        
        user_tz = pytz.timezone(timezone)
        
        # Удаляем старые задачи пользователя
        self._remove_user_jobs(user_id)
        
        # Парсим время
        wake_hour, wake_minute = map(int, wake_time.split(":"))
        sleep_hour, sleep_minute = map(int, sleep_time.split(":"))
        
        # 1. Утреннее приветствие (через 30 мин после подъёма)
        morning_hour = wake_hour if wake_minute < 30 else (wake_hour + 1) % 24
        morning_minute = (wake_minute + 30) % 60
        
        self.scheduler.add_job(
            self._send_morning_greeting,
            CronTrigger(hour=morning_hour, minute=morning_minute, timezone=user_tz),
            args=[telegram_id],
            id=f"morning_{user_id}",
            replace_existing=True
        )
        
        # 2. Напоминание о воде (каждые 2 часа с 9 до 21)
        for hour in range(9, 22, 2):
            self.scheduler.add_job(
                self._send_water_reminder,
                CronTrigger(hour=hour, minute=0, timezone=user_tz),
                args=[telegram_id],
                id=f"water_{user_id}_{hour}",
                replace_existing=True
            )
        
        # 3. Напоминания о приёмах пищи
        meal_times = [
            ("breakfast", 8, 0, "завтрак"),
            ("lunch", 13, 0, "обед"),
            ("dinner", 19, 0, "ужин")
        ]
        
        for meal_id, hour, minute, meal_name in meal_times:
            self.scheduler.add_job(
                self._send_meal_reminder,
                CronTrigger(hour=hour, minute=minute, timezone=user_tz),
                args=[telegram_id, meal_name],
                id=f"{meal_id}_{user_id}",
                replace_existing=True
            )
        
        # 4. Вечерний итог (за 1 час до сна)
        evening_hour = (sleep_hour - 1) % 24
        
        self.scheduler.add_job(
            self._send_evening_summary,
            CronTrigger(hour=evening_hour, minute=0, timezone=user_tz),
            args=[telegram_id],
            id=f"evening_{user_id}",
            replace_existing=True
        )
        
        logger.info(f"Scheduled notifications for user {user_id}")
    
    def _remove_user_jobs(self, user_id: int):
        """Удаление всех задач пользователя"""
        job_prefixes = ["morning_", "water_", "breakfast_", "lunch_", 
                       "dinner_", "workout_", "evening_"]
        
        for job in self.scheduler.get_jobs():
            for prefix in job_prefixes:
                if job.id.startswith(prefix) and job.id.endswith(f"_{user_id}"):
                    self.scheduler.remove_job(job.id)
                    break
    
    async def schedule_workout_reminder(self, user_id: int, telegram_id: int,
                                        workout_time: str, timezone: str = "Europe/Moscow"):
        """Напоминание о тренировке (за 1 час до)"""
        user_tz = pytz.timezone(timezone)
        hour, minute = map(int, workout_time.split(":"))
        
        # За 1 час до тренировки
        reminder_hour = (hour - 1) % 24
        
        self.scheduler.add_job(
            self._send_workout_reminder,
            CronTrigger(hour=reminder_hour, minute=minute, timezone=user_tz),
            args=[telegram_id],
            id=f"workout_reminder_{user_id}",
            replace_existing=True
        )
    
    # === Функции отправки уведомлений ===
    
    async def _send_morning_greeting(self, telegram_id: int):
        """Отправка утреннего приветствия"""
        if not self.bot:
            return
        
        try:
            # Получаем данные пользователя из БД
            from sqlalchemy import select
            from database.models import User
            
            async with self.session_factory() as session:
                result = await session.execute(
                    select(User).where(User.telegram_id == telegram_id)
                )
                user = result.scalar_one_or_none()
                
                if not user or not user.notifications_enabled:
                    return
                
                name = user.profile.name if user.profile else "друг"
                
                message = (
                    f"🌅 Доброе утро, {name}!\n\n"
                    f"Новый день — новые возможности! 💪\n"
                    f"🔥 Твой streak: {user.streak_days} дней\n\n"
                    f"Готов к свершениям? Нажми /today чтобы увидеть план!"
                )
                
                await self.bot.send_message(telegram_id, message)
                logger.info(f"Sent morning greeting to {telegram_id}")
                
        except Exception as e:
            logger.error(f"Failed to send morning greeting: {e}")
    
    async def _send_water_reminder(self, telegram_id: int):
        """Напоминание о воде"""
        if not self.bot:
            return
        
        try:
            from sqlalchemy import select
            from database.models import User
            
            async with self.session_factory() as session:
                result = await session.execute(
                    select(User).where(User.telegram_id == telegram_id)
                )
                user = result.scalar_one_or_none()
                
                if not user or not user.notifications_enabled:
                    return
                
                await self.bot.send_message(
                    telegram_id,
                    "💧 Время попить воды!\n\nНе забывай о водном балансе. "
                    "Нажми /water чтобы отметить."
                )
                logger.info(f"Sent water reminder to {telegram_id}")
                
        except Exception as e:
            logger.error(f"Failed to send water reminder: {e}")
    
    async def _send_meal_reminder(self, telegram_id: int, meal_name: str):
        """Напоминание о приёме пищи"""
        if not self.bot:
            return
        
        try:
            from sqlalchemy import select
            from database.models import User
            
            async with self.session_factory() as session:
                result = await session.execute(
                    select(User).where(User.telegram_id == telegram_id)
                )
                user = result.scalar_one_or_none()
                
                if not user or not user.notifications_enabled:
                    return
                
                emoji = {"завтрак": "🌅", "обед": "☀️", "ужин": "🌆"}.get(meal_name, "🍽️")
                
                await self.bot.send_message(
                    telegram_id,
                    f"{emoji} Время {meal_name}а!\n\n"
                    f"Нажми /meal чтобы посмотреть план питания."
                )
                logger.info(f"Sent {meal_name} reminder to {telegram_id}")
                
        except Exception as e:
            logger.error(f"Failed to send meal reminder: {e}")
    
    async def _send_workout_reminder(self, telegram_id: int):
        """Напоминание о тренировке"""
        if not self.bot:
            return
        
        try:
            from sqlalchemy import select
            from database.models import User
            
            async with self.session_factory() as session:
                result = await session.execute(
                    select(User).where(User.telegram_id == telegram_id)
                )
                user = result.scalar_one_or_none()
                
                if not user or not user.notifications_enabled:
                    return
                
                name = user.profile.name if user.profile else "друг"
                
                await self.bot.send_message(
                    telegram_id,
                    f"🏋️ {name}, через час тренировка!\n\n"
                    f"Не забудь перекусить за 1.5 часа до неё.\n"
                    f"Нажми /workout чтобы посмотреть план!"
                )
                logger.info(f"Sent workout reminder to {telegram_id}")
                
        except Exception as e:
            logger.error(f"Failed to send workout reminder: {e}")
    
    async def _send_evening_summary(self, telegram_id: int):
        """Вечерний итог дня"""
        if not self.bot:
            return
        
        try:
            from sqlalchemy import select
            from database.models import User, WorkoutLog, NutritionLog
            from datetime import date
            
            async with self.session_factory() as session:
                result = await session.execute(
                    select(User).where(User.telegram_id == telegram_id)
                )
                user = result.scalar_one_or_none()
                
                if not user or not user.notifications_enabled:
                    return
                
                today = date.today()
                name = user.profile.name if user.profile else "друг"
                
                # Получаем данные за день
                workout_result = await session.execute(
                    select(WorkoutLog).where(
                        WorkoutLog.user_id == user.id,
                        WorkoutLog.date == today
                    )
                )
                workout = workout_result.scalar_one_or_none()
                
                nutrition_result = await session.execute(
                    select(NutritionLog).where(
                        NutritionLog.user_id == user.id,
                        NutritionLog.date == today
                    )
                )
                nutrition = nutrition_result.scalar_one_or_none()
                
                workout_status = "✅" if workout and workout.status == "completed" else "❌"
                water = f"{nutrition.water_liters:.1f}" if nutrition else "0.0"
                target_water = user.profile.target_water if user.profile else 2.5
                
                message = (
                    f"🌙 Итоги дня, {name}!\n\n"
                    f"🏋️ Тренировка: {workout_status}\n"
                    f"💧 Вода: {water}/{target_water} л\n"
                    f"🔥 Streak: {user.streak_days} дней\n\n"
                    f"Хорошего отдыха! Завтра продолжим 💪"
                )
                
                await self.bot.send_message(telegram_id, message)
                logger.info(f"Sent evening summary to {telegram_id}")
                
        except Exception as e:
            logger.error(f"Failed to send evening summary: {e}")


# Глобальный экземпляр планировщика
scheduler = NotificationScheduler()
