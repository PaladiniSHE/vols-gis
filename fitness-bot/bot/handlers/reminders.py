"""
Обработчики для напоминаний
"""
from datetime import time
from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

from bot.keyboards.inline import InlineKeyboards
from core.database import async_session
from core.models.reminders import ReminderType
from services.user_service import UserService
from services.reminder_service import ReminderService

router = Router()


class ReminderStates(StatesGroup):
    """Состояния для настройки напоминаний"""
    entering_time = State()


@router.message(Command("reminders"))
async def cmd_reminders(message: Message, state: FSMContext):
    """Команда /reminders"""
    await state.clear()
    await show_reminders_menu(message)


@router.callback_query(F.data == "menu:reminders")
async def callback_reminders_menu(callback: CallbackQuery, state: FSMContext):
    """Меню напоминаний"""
    await state.clear()
    
    async with async_session() as session:
        user_service = UserService(session)
        reminder_service = ReminderService(session)
        
        user = await user_service.get_user_by_telegram_id(callback.from_user.id)
        if not user:
            await callback.answer("Сначала настройте профиль")
            return
        
        reminders = await reminder_service.get_user_reminders(user.id)
        
        if not reminders:
            # Создаем стандартные напоминания
            reminders = await reminder_service.setup_default_reminders(user.id)
        
        text = await format_reminders_text(reminders)
        
        await callback.message.edit_text(
            text,
            parse_mode="Markdown",
            reply_markup=InlineKeyboards.reminders_menu(reminders)
        )
    
    await callback.answer()


async def show_reminders_menu(message: Message):
    """Показать меню напоминаний"""
    async with async_session() as session:
        user_service = UserService(session)
        reminder_service = ReminderService(session)
        
        user = await user_service.get_user_by_telegram_id(message.from_user.id)
        if not user:
            await message.answer("Сначала настройте профиль с помощью /start")
            return
        
        reminders = await reminder_service.get_user_reminders(user.id)
        
        if not reminders:
            reminders = await reminder_service.setup_default_reminders(user.id)
        
        text = await format_reminders_text(reminders)
        
        await message.answer(
            text,
            parse_mode="Markdown",
            reply_markup=InlineKeyboards.reminders_menu(reminders)
        )


async def format_reminders_text(reminders) -> str:
    """Форматировать текст напоминаний"""
    text = "⏰ *Напоминания*\n\n"
    
    reminder_names = {
        ReminderType.MEAL_BREAKFAST: "🍳 Завтрак",
        ReminderType.MEAL_LUNCH: "🍜 Обед",
        ReminderType.MEAL_DINNER: "🍽️ Ужин",
        ReminderType.WATER: "💧 Вода",
        ReminderType.WEIGHT: "⚖️ Взвеситься",
        ReminderType.WORKOUT: "🏋️ Тренировка",
    }
    
    active_count = 0
    
    for r in reminders:
        status = "✅" if r.is_active else "❌"
        name = reminder_names.get(r.reminder_type, "⏰ Напоминание")
        time_str = r.time.strftime("%H:%M")
        
        if r.is_active:
            active_count += 1
        
        text += f"{status} {name}: *{time_str}*\n"
    
    text += f"\n📊 Активных: {active_count} из {len(reminders)}\n"
    text += "\n_Нажми на напоминание чтобы включить/выключить_"
    
    return text


@router.callback_query(F.data.startswith("reminder:toggle:"))
async def callback_toggle_reminder(callback: CallbackQuery):
    """Переключить напоминание"""
    reminder_id = int(callback.data.split(":")[2])
    
    async with async_session() as session:
        user_service = UserService(session)
        reminder_service = ReminderService(session)
        
        user = await user_service.get_user_by_telegram_id(callback.from_user.id)
        reminder = await reminder_service.toggle_reminder(reminder_id)
        
        if reminder:
            status = "включено ✅" if reminder.is_active else "выключено ❌"
            await callback.answer(f"Напоминание {status}")
            
            # Обновляем список
            reminders = await reminder_service.get_user_reminders(user.id)
            text = await format_reminders_text(reminders)
            
            await callback.message.edit_text(
                text,
                parse_mode="Markdown",
                reply_markup=InlineKeyboards.reminders_menu(reminders)
            )
        else:
            await callback.answer("Ошибка")


@router.callback_query(F.data == "reminders:enable_all")
async def callback_enable_all_reminders(callback: CallbackQuery):
    """Включить все напоминания"""
    async with async_session() as session:
        user_service = UserService(session)
        reminder_service = ReminderService(session)
        
        user = await user_service.get_user_by_telegram_id(callback.from_user.id)
        reminders = await reminder_service.get_user_reminders(user.id)
        
        for r in reminders:
            if not r.is_active:
                r.is_active = True
        
        await session.commit()
        
        # Обновляем список
        reminders = await reminder_service.get_user_reminders(user.id)
        text = await format_reminders_text(reminders)
        
        await callback.message.edit_text(
            text,
            parse_mode="Markdown",
            reply_markup=InlineKeyboards.reminders_menu(reminders)
        )
    
    await callback.answer("Все напоминания включены ✅")


@router.callback_query(F.data == "reminders:disable_all")
async def callback_disable_all_reminders(callback: CallbackQuery):
    """Выключить все напоминания"""
    async with async_session() as session:
        user_service = UserService(session)
        reminder_service = ReminderService(session)
        
        user = await user_service.get_user_by_telegram_id(callback.from_user.id)
        reminders = await reminder_service.get_user_reminders(user.id)
        
        for r in reminders:
            if r.is_active:
                r.is_active = False
        
        await session.commit()
        
        # Обновляем список
        reminders = await reminder_service.get_user_reminders(user.id)
        text = await format_reminders_text(reminders)
        
        await callback.message.edit_text(
            text,
            parse_mode="Markdown",
            reply_markup=InlineKeyboards.reminders_menu(reminders)
        )
    
    await callback.answer("Все напоминания выключены ❌")
