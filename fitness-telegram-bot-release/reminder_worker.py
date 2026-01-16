"""
Фоновый воркер для отправки напоминаний.

Этот модуль должен запускаться отдельным процессом для отправки
напоминаний пользователям по расписанию.

Запуск:
    python reminder_worker.py

Или через systemd/supervisor в production.
"""
import asyncio
import logging
import sys
from datetime import datetime, timedelta

from aiogram import Bot
from aiogram.exceptions import TelegramForbiddenError, TelegramBadRequest
from sqlalchemy import select

from bot.config import settings
from core.database import init_db, async_session
from core.models.user import User
from core.models.reminders import Reminder
from services.reminder_service import ReminderService

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    stream=sys.stdout
)

logger = logging.getLogger("reminder_worker")

# Интервал проверки напоминаний (в секундах)
CHECK_INTERVAL = 60  # Каждую минуту


class ReminderWorker:
    """Воркер для отправки напоминаний"""
    
    def __init__(self):
        self.bot = Bot(token=settings.bot_token)
        self.is_running = False
        self._processed_reminders: dict = {}  # reminder_id -> last_sent_time
    
    async def start(self):
        """Запуск воркера"""
        logger.info("Starting reminder worker...")
        self.is_running = True
        
        # Инициализация базы данных
        await init_db()
        
        try:
            while self.is_running:
                try:
                    await self._process_reminders()
                except Exception as e:
                    logger.error(f"Error processing reminders: {e}", exc_info=True)
                
                # Ждем до следующей проверки
                await asyncio.sleep(CHECK_INTERVAL)
                
        finally:
            await self.bot.session.close()
            logger.info("Reminder worker stopped")
    
    async def stop(self):
        """Остановка воркера"""
        logger.info("Stopping reminder worker...")
        self.is_running = False
    
    async def _process_reminders(self):
        """Обработать напоминания для текущего времени"""
        now = datetime.now()
        current_time = now.time()
        current_weekday = now.weekday()  # 0 = Monday
        
        logger.debug(f"Checking reminders at {current_time} (weekday={current_weekday})")
        
        async with async_session() as session:
            reminder_service = ReminderService(session)
            
            # Получаем напоминания для текущего времени
            reminders = await reminder_service.get_reminders_for_time(
                current_time,
                current_weekday
            )
            
            if not reminders:
                return
            
            logger.info(f"Found {len(reminders)} reminders to process")
            
            for reminder in reminders:
                # Проверяем, не отправляли ли мы уже это напоминание недавно
                if self._was_recently_sent(reminder.id):
                    logger.debug(f"Reminder {reminder.id} was recently sent, skipping")
                    continue
                
                # Получаем пользователя
                user_result = await session.execute(
                    select(User).where(User.id == reminder.user_id)
                )
                user = user_result.scalar_one_or_none()
                
                if not user:
                    logger.warning(f"User {reminder.user_id} not found for reminder {reminder.id}")
                    continue
                
                # Проверяем, включены ли уведомления у пользователя
                if not user.notifications_enabled:
                    logger.debug(f"User {user.telegram_id} has notifications disabled")
                    continue
                
                # Отправляем напоминание
                await self._send_reminder(user, reminder, reminder_service)
    
    def _was_recently_sent(self, reminder_id: int, cooldown_minutes: int = 5) -> bool:
        """Проверить, отправлялось ли напоминание недавно"""
        last_sent = self._processed_reminders.get(reminder_id)
        if not last_sent:
            return False
        
        elapsed = datetime.now() - last_sent
        return elapsed < timedelta(minutes=cooldown_minutes)
    
    async def _send_reminder(
        self,
        user: User,
        reminder: Reminder,
        reminder_service: ReminderService
    ):
        """Отправить напоминание пользователю"""
        message = reminder_service.get_message_for_reminder(reminder)
        
        try:
            await self.bot.send_message(
                chat_id=user.telegram_id,
                text=f"{message}\n\n"
                     f"_💡 Отключить напоминания: /reminders_",
                parse_mode="Markdown"
            )
            
            # Отмечаем напоминание как отправленное
            await reminder_service.mark_triggered(reminder.id)
            self._processed_reminders[reminder.id] = datetime.now()
            
            logger.info(
                f"Sent reminder {reminder.id} ({reminder.reminder_type.value}) "
                f"to user {user.telegram_id}"
            )
            
        except TelegramForbiddenError:
            # Пользователь заблокировал бота
            logger.warning(f"User {user.telegram_id} blocked the bot, disabling notifications")
            user.notifications_enabled = False
            async with async_session() as session:
                result = await session.execute(
                    select(User).where(User.telegram_id == user.telegram_id)
                )
                db_user = result.scalar_one_or_none()
                if db_user:
                    db_user.notifications_enabled = False
                    await session.commit()
        
        except TelegramBadRequest as e:
            logger.error(f"Bad request when sending to {user.telegram_id}: {e}")
        
        except Exception as e:
            logger.error(
                f"Failed to send reminder {reminder.id} to user {user.telegram_id}: {e}",
                exc_info=True
            )
    
    def _cleanup_old_processed(self):
        """Очистить старые записи об отправленных напоминаниях"""
        now = datetime.now()
        cutoff = now - timedelta(hours=1)
        
        self._processed_reminders = {
            rid: sent_time
            for rid, sent_time in self._processed_reminders.items()
            if sent_time > cutoff
        }


async def main():
    """Главная функция запуска воркера"""
    worker = ReminderWorker()
    
    # Обработка сигналов остановки
    import signal
    
    def signal_handler(sig, frame):
        logger.info(f"Received signal {sig}, stopping...")
        asyncio.create_task(worker.stop())
    
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    await worker.start()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Worker stopped by user")
    except Exception as e:
        logger.error(f"Worker crashed: {e}")
        raise
