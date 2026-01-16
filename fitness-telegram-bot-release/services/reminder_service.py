"""
Сервис для работы с напоминаниями
"""
from datetime import datetime, time, timedelta
from typing import List, Optional
from sqlalchemy import select, and_, delete
from sqlalchemy.ext.asyncio import AsyncSession

from core.models.reminders import Reminder, ReminderType


class ReminderService:
    """Сервис управления напоминаниями"""
    
    # Шаблоны сообщений напоминаний
    REMINDER_MESSAGES = {
        ReminderType.MEAL_BREAKFAST: "🍳 Время завтрака! Не забудь записать, что съел.",
        ReminderType.MEAL_LUNCH: "🍜 Время обеда! Запиши свой прием пищи.",
        ReminderType.MEAL_DINNER: "🍽️ Время ужина! Не забудь добавить еду в дневник.",
        ReminderType.WATER: "💧 Время попить воды! Поддерживай водный баланс.",
        ReminderType.WEIGHT: "⚖️ Время взвеситься! Отслеживай свой прогресс.",
        ReminderType.WORKOUT: "🏋️ Время тренировки! Не пропускай занятия.",
    }
    
    def __init__(self, session: AsyncSession):
        self.session = session
    
    async def create_reminder(
        self,
        user_id: int,
        reminder_type: ReminderType,
        reminder_time: time,
        weekdays_mask: int = 127,
        message: Optional[str] = None
    ) -> Reminder:
        """Создать напоминание"""
        reminder = Reminder(
            user_id=user_id,
            reminder_type=reminder_type,
            time=reminder_time,
            weekdays_mask=weekdays_mask,
            message=message
        )
        self.session.add(reminder)
        await self.session.commit()
        await self.session.refresh(reminder)
        return reminder
    
    async def get_reminder(self, reminder_id: int) -> Optional[Reminder]:
        """Получить напоминание по ID"""
        result = await self.session.execute(
            select(Reminder).where(Reminder.id == reminder_id)
        )
        return result.scalar_one_or_none()
    
    async def get_user_reminders(self, user_id: int) -> List[Reminder]:
        """Получить все напоминания пользователя"""
        result = await self.session.execute(
            select(Reminder)
            .where(Reminder.user_id == user_id)
            .order_by(Reminder.time)
        )
        return result.scalars().all()
    
    async def get_active_reminders(self, user_id: int) -> List[Reminder]:
        """Получить активные напоминания пользователя"""
        result = await self.session.execute(
            select(Reminder)
            .where(
                and_(
                    Reminder.user_id == user_id,
                    Reminder.is_active == True
                )
            )
            .order_by(Reminder.time)
        )
        return result.scalars().all()
    
    async def toggle_reminder(self, reminder_id: int, user_id: int = None) -> Optional[Reminder]:
        """Переключить статус напоминания
        
        Args:
            reminder_id: ID напоминания
            user_id: ID пользователя для проверки владельца (если указан)
        
        Returns:
            Reminder или None если не найдено или не принадлежит пользователю
        """
        reminder = await self.get_reminder(reminder_id)
        if reminder:
            # Проверяем владельца если user_id указан
            if user_id is not None and reminder.user_id != user_id:
                return None
            reminder.is_active = not reminder.is_active
            await self.session.commit()
            await self.session.refresh(reminder)
        return reminder
    
    async def delete_reminder(self, reminder_id: int, user_id: int) -> bool:
        """Удалить напоминание"""
        result = await self.session.execute(
            delete(Reminder)
            .where(
                and_(
                    Reminder.id == reminder_id,
                    Reminder.user_id == user_id
                )
            )
        )
        await self.session.commit()
        return result.rowcount > 0
    
    async def update_reminder_time(
        self,
        reminder_id: int,
        new_time: time
    ) -> Optional[Reminder]:
        """Обновить время напоминания"""
        reminder = await self.get_reminder(reminder_id)
        if reminder:
            reminder.time = new_time
            await self.session.commit()
            await self.session.refresh(reminder)
        return reminder
    
    async def get_reminders_for_time(
        self,
        current_time: time,
        current_weekday: int
    ) -> List[Reminder]:
        """Получить напоминания для текущего времени"""
        # Ищем напоминания в диапазоне ±2 минуты
        time_start = (datetime.combine(datetime.today(), current_time) - timedelta(minutes=2)).time()
        time_end = (datetime.combine(datetime.today(), current_time) + timedelta(minutes=2)).time()
        
        result = await self.session.execute(
            select(Reminder)
            .where(
                and_(
                    Reminder.is_active == True,
                    Reminder.time >= time_start,
                    Reminder.time <= time_end
                )
            )
        )
        
        reminders = result.scalars().all()
        
        # Фильтруем по дню недели
        return [r for r in reminders if r.should_trigger_on_weekday(current_weekday)]
    
    async def mark_triggered(self, reminder_id: int) -> None:
        """Отметить, что напоминание сработало"""
        reminder = await self.get_reminder(reminder_id)
        if reminder:
            reminder.last_triggered = datetime.utcnow()
            await self.session.commit()
    
    async def setup_default_reminders(self, user_id: int) -> List[Reminder]:
        """Создать стандартный набор напоминаний для пользователя"""
        default_reminders = [
            (ReminderType.MEAL_BREAKFAST, time(8, 0)),
            (ReminderType.MEAL_LUNCH, time(13, 0)),
            (ReminderType.MEAL_DINNER, time(19, 0)),
            (ReminderType.WATER, time(10, 0)),
            (ReminderType.WATER, time(15, 0)),
            (ReminderType.WEIGHT, time(7, 30)),
        ]
        
        created = []
        for reminder_type, reminder_time in default_reminders:
            reminder = await self.create_reminder(
                user_id=user_id,
                reminder_type=reminder_type,
                reminder_time=reminder_time
            )
            # Деактивируем по умолчанию - пользователь сам включит
            reminder.is_active = False
            created.append(reminder)
        
        await self.session.commit()
        return created
    
    def get_message_for_reminder(self, reminder: Reminder) -> str:
        """Получить текст сообщения для напоминания"""
        if reminder.message:
            return reminder.message
        return self.REMINDER_MESSAGES.get(
            reminder.reminder_type,
            "⏰ Напоминание!"
        )
