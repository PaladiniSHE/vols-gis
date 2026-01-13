"""
Обработчики тренировок
"""
from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from datetime import date

from database.models import User, WorkoutLog
from bot.keyboards import (
    get_main_menu_keyboard,
    get_workout_status_keyboard,
    get_rating_keyboard,
    get_back_keyboard
)
from bot.states import WorkoutStates

router = Router(name="workout")


@router.callback_query(F.data == "workout")
async def show_workout(callback: CallbackQuery, session: AsyncSession):
    """Показать тренировку на сегодня"""
    await callback.answer()
    
    result = await session.execute(
        select(User).where(User.telegram_id == callback.from_user.id)
    )
    user = result.scalar_one_or_none()
    
    if not user:
        await callback.message.edit_text(
            "Сначала пройди регистрацию!",
            reply_markup=get_back_keyboard("menu")
        )
        return
    
    # Загружаем профиль
    from database.models import UserProfile
    profile_result = await session.execute(
        select(UserProfile).where(UserProfile.user_id == user.id)
    )
    profile = profile_result.scalar_one_or_none()
    
    today = date.today()
    weekday = today.weekday()  # 0 = Monday
    
    # Проверяем, есть ли тренировка сегодня
    # (упрощённая логика - тренировочные дни)
    training_days = profile.training_days_per_week if profile else 3
    
    # Пример тренировки
    workout_text = (
        f"🏋️ *ТРЕНИРОВКА НА СЕГОДНЯ*\n"
        f"📅 {today.strftime('%d.%m.%Y')}\n\n"
        f"🎯 *Верх тела + Кардио*\n"
        f"⏱️ Длительность: 45-50 мин\n\n"
        f"━━━━━━━━━━━━━━━━━━━━\n\n"
        f"🔥 *РАЗМИНКА* (5-7 мин)\n"
        f"├ Круговые движения руками — 30 сек\n"
        f"├ Наклоны в стороны — 30 сек\n"
        f"└ Приседания без веса — 15 раз\n\n"
        f"💪 *ОСНОВНАЯ ЧАСТЬ*\n\n"
        f"*1. Жим гантелей лёжа*\n"
        f"   Подходы: 4 | Повторы: 10-12\n"
        f"   Отдых: 90 сек\n\n"
        f"*2. Тяга гантели в наклоне*\n"
        f"   Подходы: 3 | Повторы: 12 на руку\n"
        f"   Отдых: 60 сек\n\n"
        f"*3. Жим гантелей сидя (плечи)*\n"
        f"   Подходы: 3 | Повторы: 10-12\n"
        f"   Отдых: 60 сек\n\n"
        f"*4. Сгибания на бицепс*\n"
        f"   Подходы: 3 | Повторы: 12\n"
        f"   Отдых: 45 сек\n\n"
        f"*5. Разгибания на трицепс*\n"
        f"   Подходы: 3 | Повторы: 12\n"
        f"   Отдых: 45 сек\n\n"
        f"🏃 *КАРДИО* (10 мин)\n"
        f"└ Ходьба в быстром темпе или велотренажёр\n\n"
        f"🧘 *ЗАМИНКА* (5 мин)\n"
        f"└ Растяжка всех групп мышц\n\n"
        f"━━━━━━━━━━━━━━━━━━━━\n\n"
        f"Готов приступить? После тренировки отметь результат!"
    )
    
    await callback.message.edit_text(
        workout_text,
        reply_markup=get_workout_status_keyboard(),
        parse_mode="Markdown"
    )


@router.message(Command("workout"))
async def cmd_workout(message: Message, session: AsyncSession):
    """Команда /workout"""
    result = await session.execute(
        select(User).where(User.telegram_id == message.from_user.id)
    )
    user = result.scalar_one_or_none()
    
    if not user or not user.is_onboarded:
        await message.answer("Сначала пройди регистрацию! /start")
        return
    
    # Отправляем тренировку
    class FakeCallback:
        def __init__(self, msg, from_user):
            self.message = msg
            self.from_user = from_user
        async def answer(self):
            pass
    
    fake = FakeCallback(message, message.from_user)
    await show_workout(fake, session)


@router.callback_query(F.data == "workout_completed")
async def workout_completed(callback: CallbackQuery, state: FSMContext, session: AsyncSession):
    """Тренировка выполнена"""
    await callback.answer("💪 Отлично!")
    
    result = await session.execute(
        select(User).where(User.telegram_id == callback.from_user.id)
    )
    user = result.scalar_one_or_none()
    
    if user:
        # Создаём лог тренировки
        today = date.today()
        workout_log = WorkoutLog(
            user_id=user.id,
            date=today,
            workout_type="strength",
            workout_name="Верх тела + Кардио",
            duration_minutes=50,
            status="completed",
            completion_percent=100
        )
        session.add(workout_log)
        
        # Обновляем статистику
        user.total_workouts += 1
        user.streak_days += 1
        
        await session.commit()
    
    await state.set_state(WorkoutStates.waiting_workout_rating)
    
    await callback.message.edit_text(
        "🎉 *Отличная работа!*\n\n"
        "Как ты оцениваешь тренировку по нагрузке?\n"
        "(1 — легко, 10 — на пределе)",
        reply_markup=get_rating_keyboard("effort"),
        parse_mode="Markdown"
    )


@router.callback_query(F.data == "workout_partial")
async def workout_partial(callback: CallbackQuery, session: AsyncSession):
    """Тренировка выполнена частично"""
    await callback.answer()
    
    result = await session.execute(
        select(User).where(User.telegram_id == callback.from_user.id)
    )
    user = result.scalar_one_or_none()
    
    if user:
        today = date.today()
        workout_log = WorkoutLog(
            user_id=user.id,
            date=today,
            workout_type="strength",
            status="partial",
            completion_percent=50
        )
        session.add(workout_log)
        await session.commit()
    
    await callback.message.edit_text(
        "👍 *Частичное выполнение — тоже результат!*\n\n"
        "Главное, что ты не пропустил день полностью.\n"
        "Любое движение лучше, чем ничего! 💪\n\n"
        "Завтра продолжим!",
        reply_markup=get_main_menu_keyboard(),
        parse_mode="Markdown"
    )


@router.callback_query(F.data == "workout_skipped")
async def workout_skipped(callback: CallbackQuery, session: AsyncSession):
    """Тренировка пропущена"""
    await callback.answer()
    
    result = await session.execute(
        select(User).where(User.telegram_id == callback.from_user.id)
    )
    user = result.scalar_one_or_none()
    
    if user:
        today = date.today()
        workout_log = WorkoutLog(
            user_id=user.id,
            date=today,
            status="skipped",
            completion_percent=0
        )
        session.add(workout_log)
        
        # Сбрасываем streak
        user.streak_days = 0
        
        await session.commit()
    
    await callback.message.edit_text(
        "😔 *Ничего страшного!*\n\n"
        "Пропуск одной тренировки — это не конец света.\n"
        "Бывают дни, когда отдых важнее.\n\n"
        "Главное — не пропускать два дня подряд!\n"
        "Завтра вернёмся в строй! 💪",
        reply_markup=get_main_menu_keyboard(),
        parse_mode="Markdown"
    )


@router.callback_query(F.data == "workout_reschedule")
async def workout_reschedule(callback: CallbackQuery):
    """Перенести тренировку"""
    await callback.answer()
    
    await callback.message.edit_text(
        "📅 *Перенос тренировки*\n\n"
        "Хорошо, перенесём тренировку на завтра.\n"
        "Не забудь выделить время! ⏰",
        reply_markup=get_main_menu_keyboard(),
        parse_mode="Markdown"
    )


@router.callback_query(WorkoutStates.waiting_workout_rating, F.data.startswith("effort_"))
async def process_workout_rating(callback: CallbackQuery, state: FSMContext, session: AsyncSession):
    """Обработка оценки тренировки"""
    await callback.answer()
    
    rating = int(callback.data.replace("effort_", ""))
    
    # Обновляем лог тренировки
    result = await session.execute(
        select(User).where(User.telegram_id == callback.from_user.id)
    )
    user = result.scalar_one_or_none()
    
    if user:
        today = date.today()
        log_result = await session.execute(
            select(WorkoutLog).where(
                WorkoutLog.user_id == user.id,
                WorkoutLog.date == today
            )
        )
        workout_log = log_result.scalar_one_or_none()
        
        if workout_log:
            workout_log.perceived_effort = rating
            await session.commit()
    
    await state.clear()
    
    # Сообщение в зависимости от оценки
    if rating <= 3:
        feedback = "Лёгкая тренировка! В следующий раз можно добавить нагрузку 📈"
    elif rating <= 6:
        feedback = "Отличная рабочая интенсивность! Так держать! 👍"
    elif rating <= 8:
        feedback = "Хорошая нагрузка! Ты работаешь на результат! 💪"
    else:
        feedback = "Мощная тренировка! Не забудь хорошо восстановиться! 🔥"
    
    await callback.message.edit_text(
        f"📊 *Записано!*\n\n"
        f"Нагрузка: {rating}/10\n\n"
        f"{feedback}\n\n"
        f"Не забудь поесть в ближайшие 30-60 минут! 🍽️",
        reply_markup=get_main_menu_keyboard(),
        parse_mode="Markdown"
    )
