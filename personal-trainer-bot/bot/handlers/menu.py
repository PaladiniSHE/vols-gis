"""
Обработчики главного меню
"""
from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from datetime import date

from database.models import User, UserProfile, WorkoutLog, NutritionLog
from bot.keyboards import get_main_menu_keyboard, get_water_keyboard

router = Router(name="menu")


@router.callback_query(F.data == "today_plan")
async def show_today_plan(callback: CallbackQuery, session: AsyncSession):
    """Показать план на сегодня"""
    await callback.answer()
    
    result = await session.execute(
        select(User).where(User.telegram_id == callback.from_user.id)
    )
    user = result.scalar_one_or_none()
    
    if not user or not user.profile:
        await callback.message.edit_text("Сначала пройди регистрацию!")
        return
    
    profile = user.profile
    today = date.today()
    weekday = today.strftime("%A")
    weekday_ru = {
        "Monday": "Понедельник",
        "Tuesday": "Вторник",
        "Wednesday": "Среда",
        "Thursday": "Четверг",
        "Friday": "Пятница",
        "Saturday": "Суббота",
        "Sunday": "Воскресенье"
    }
    
    # Получаем логи за сегодня
    workout_result = await session.execute(
        select(WorkoutLog).where(
            WorkoutLog.user_id == user.id,
            WorkoutLog.date == today
        )
    )
    workout_log = workout_result.scalar_one_or_none()
    
    nutrition_result = await session.execute(
        select(NutritionLog).where(
            NutritionLog.user_id == user.id,
            NutritionLog.date == today
        )
    )
    nutrition_log = nutrition_result.scalar_one_or_none()
    
    workout_status = "✅" if workout_log and workout_log.status == "completed" else "⏳"
    water_status = f"{nutrition_log.water_liters:.1f}" if nutrition_log else "0.0"
    
    text = (
        f"📅 *{weekday_ru.get(weekday, weekday)}, {today.strftime('%d.%m.%Y')}*\n\n"
        f"🏋️ *ТРЕНИРОВКА* {workout_status}\n"
        f"└ Сегодня: Силовая (верх тела) — 45 мин\n\n"
        f"🍽️ *ПИТАНИЕ* ({profile.target_calories} ккал)\n"
        f"├ Белки: {profile.target_protein} г\n"
        f"├ Жиры: {profile.target_fat} г\n"
        f"└ Углеводы: {profile.target_carbs} г\n\n"
        f"💧 *ВОДА*: {water_status} / {profile.target_water} л\n\n"
        f"🔥 Streak: {user.streak_days} дней\n\n"
        "Выбери действие:"
    )
    
    await callback.message.edit_text(
        text,
        reply_markup=get_main_menu_keyboard(),
        parse_mode="Markdown"
    )


@router.message(Command("today"))
async def cmd_today(message: Message, session: AsyncSession):
    """Команда /today"""
    result = await session.execute(
        select(User).where(User.telegram_id == message.from_user.id)
    )
    user = result.scalar_one_or_none()
    
    if not user or not user.is_onboarded:
        await message.answer("Сначала пройди регистрацию! /start")
        return
    
    # Создаём фейковый callback для переиспользования логики
    class FakeCallback:
        def __init__(self, message, from_user):
            self.message = message
            self.from_user = from_user
        async def answer(self):
            pass
    
    fake = FakeCallback(message, message.from_user)
    await show_today_plan(fake, session)


@router.callback_query(F.data == "water")
async def show_water_menu(callback: CallbackQuery, session: AsyncSession):
    """Меню воды"""
    await callback.answer()
    
    result = await session.execute(
        select(User).where(User.telegram_id == callback.from_user.id)
    )
    user = result.scalar_one_or_none()
    
    if not user or not user.profile:
        return
    
    # Получаем лог питания за сегодня
    today = date.today()
    nutrition_result = await session.execute(
        select(NutritionLog).where(
            NutritionLog.user_id == user.id,
            NutritionLog.date == today
        )
    )
    nutrition_log = nutrition_result.scalar_one_or_none()
    
    current_water = nutrition_log.water_liters if nutrition_log else 0.0
    target_water = user.profile.target_water or 2.5
    percent = min(100, int((current_water / target_water) * 100))
    
    # Визуализация прогресса
    filled = int(percent / 10)
    progress_bar = "█" * filled + "░" * (10 - filled)
    
    await callback.message.edit_text(
        f"💧 *Вода за сегодня*\n\n"
        f"Выпито: {current_water:.1f} / {target_water:.1f} л\n"
        f"[{progress_bar}] {percent}%\n\n"
        f"Добавь воду:",
        reply_markup=get_water_keyboard(),
        parse_mode="Markdown"
    )


@router.callback_query(F.data.startswith("water_"))
async def add_water(callback: CallbackQuery, session: AsyncSession):
    """Добавить воду"""
    if callback.data == "water_stats":
        await show_water_menu(callback, session)
        return
    
    await callback.answer("💧 Записано!")
    
    amount = int(callback.data.replace("water_", ""))  # в мл
    
    result = await session.execute(
        select(User).where(User.telegram_id == callback.from_user.id)
    )
    user = result.scalar_one_or_none()
    
    if not user:
        return
    
    # Получаем или создаём лог питания за сегодня
    today = date.today()
    nutrition_result = await session.execute(
        select(NutritionLog).where(
            NutritionLog.user_id == user.id,
            NutritionLog.date == today
        )
    )
    nutrition_log = nutrition_result.scalar_one_or_none()
    
    if not nutrition_log:
        nutrition_log = NutritionLog(user_id=user.id, date=today)
        session.add(nutrition_log)
    
    nutrition_log.water_liters = (nutrition_log.water_liters or 0) + (amount / 1000)
    await session.commit()
    
    # Обновляем сообщение
    await show_water_menu(callback, session)


@router.callback_query(F.data == "settings")
async def show_settings(callback: CallbackQuery, session: AsyncSession):
    """Показать настройки"""
    await callback.answer()
    
    result = await session.execute(
        select(User).where(User.telegram_id == callback.from_user.id)
    )
    user = result.scalar_one_or_none()
    
    if not user:
        return
    
    await callback.message.edit_text(
        f"⚙️ *Настройки*\n\n"
        f"🔔 Уведомления: {'✅ Вкл' if user.notifications_enabled else '❌ Выкл'}\n"
        f"⏰ Подъём: {user.wake_time}\n"
        f"🌙 Отход ко сну: {user.sleep_time}\n"
        f"🌍 Часовой пояс: {user.timezone}\n\n"
        f"Для изменения настроек напиши мне!",
        reply_markup=get_main_menu_keyboard(),
        parse_mode="Markdown"
    )


@router.callback_query(F.data == "progress")
async def show_progress(callback: CallbackQuery, session: AsyncSession):
    """Показать прогресс"""
    await callback.answer()
    
    result = await session.execute(
        select(User).where(User.telegram_id == callback.from_user.id)
    )
    user = result.scalar_one_or_none()
    
    if not user or not user.profile:
        return
    
    profile = user.profile
    
    text = (
        f"📊 *Твой прогресс*\n\n"
        f"⚖️ *Вес*\n"
        f"├ Текущий: {profile.current_weight} кг\n"
    )
    
    if profile.target_weight:
        diff = profile.current_weight - profile.target_weight
        text += f"├ Цель: {profile.target_weight} кг\n"
        text += f"└ Осталось: {diff:.1f} кг\n\n"
    else:
        text += "\n"
    
    text += (
        f"🏋️ *Тренировки*\n"
        f"├ Всего: {user.total_workouts}\n"
        f"└ Streak: {user.streak_days} дней 🔥\n\n"
        f"📈 *Статистика за неделю*\n"
        f"├ Тренировок: - / {profile.training_days_per_week}\n"
        f"├ Питание: -% соблюдение\n"
        f"└ Вода: - / 7 дней норма\n"
    )
    
    await callback.message.edit_text(
        text,
        reply_markup=get_main_menu_keyboard(),
        parse_mode="Markdown"
    )
