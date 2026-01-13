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
from bot.keyboards import (
    get_main_menu_keyboard, 
    get_water_keyboard, 
    get_nav_keyboard, 
    get_back_to_menu_keyboard,
    get_settings_keyboard,
    get_timezone_keyboard,
    get_notifications_keyboard,
    get_time_keyboard
)

router = Router(name="menu")


@router.callback_query(F.data == "main_menu")
async def show_main_menu(callback: CallbackQuery, session: AsyncSession):
    """Показать главное меню"""
    await callback.answer()
    
    result = await session.execute(
        select(User).where(User.telegram_id == callback.from_user.id)
    )
    user = result.scalar_one_or_none()
    
    if not user:
        await callback.message.edit_text("Сначала пройди регистрацию! /start")
        return
    
    # Загружаем профиль
    profile_result = await session.execute(
        select(UserProfile).where(UserProfile.user_id == user.id)
    )
    profile = profile_result.scalar_one_or_none()
    
    name = profile.name if profile else user.first_name or "друг"
    
    await callback.message.edit_text(
        f"👋 {name}, выбери раздел:\n\n"
        f"🔥 Streak: {user.streak_days} дней\n"
        f"💪 Тренировок: {user.total_workouts}",
        reply_markup=get_nav_keyboard()
    )


@router.callback_query(F.data == "today_plan")
async def show_today_plan(callback: CallbackQuery, session: AsyncSession):
    """Показать план на сегодня"""
    await callback.answer()
    
    result = await session.execute(
        select(User).where(User.telegram_id == callback.from_user.id)
    )
    user = result.scalar_one_or_none()
    
    if not user:
        await callback.message.edit_text("Сначала пройди регистрацию!")
        return
    
    # Загружаем профиль отдельно
    profile_result = await session.execute(
        select(UserProfile).where(UserProfile.user_id == user.id)
    )
    profile = profile_result.scalar_one_or_none()
    
    if not profile:
        await callback.message.edit_text("Сначала пройди регистрацию!")
        return
    
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
        f"🔥 Streak: {user.streak_days} дней"
    )
    
    await callback.message.edit_text(
        text,
        reply_markup=get_nav_keyboard("today"),
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
    
    if not user:
        return
    
    # Загружаем профиль
    profile_result = await session.execute(
        select(UserProfile).where(UserProfile.user_id == user.id)
    )
    profile = profile_result.scalar_one_or_none()
    
    if not profile:
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
    target_water = profile.target_water or 2.5
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
    amount = int(callback.data.replace("water_", ""))  # в мл
    
    result = await session.execute(
        select(User).where(User.telegram_id == callback.from_user.id)
    )
    user = result.scalar_one_or_none()
    
    if not user:
        return
    
    # Загружаем профиль
    profile_result = await session.execute(
        select(UserProfile).where(UserProfile.user_id == user.id)
    )
    profile = profile_result.scalar_one_or_none()
    target_water = profile.target_water if profile else 2.5
    
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
    
    # Показываем обновлённый статус
    current_water = nutrition_log.water_liters
    percent = min(100, int((current_water / target_water) * 100))
    filled = int(percent / 10)
    progress_bar = "█" * filled + "░" * (10 - filled)
    
    # Мотивационное сообщение
    if percent >= 100:
        motivation = "🎉 Норма выполнена! Отлично!"
    elif percent >= 75:
        motivation = "💪 Почти у цели!"
    elif percent >= 50:
        motivation = "👍 Больше половины!"
    else:
        motivation = "💧 Продолжай пить воду!"
    
    await callback.answer(f"💧 +{amount}мл добавлено!")
    
    await callback.message.edit_text(
        f"💧 *Вода за сегодня*\n\n"
        f"Выпито: *{current_water:.1f}* / {target_water:.1f} л\n"
        f"[{progress_bar}] {percent}%\n\n"
        f"{motivation}\n\n"
        f"Добавить ещё:",
        reply_markup=get_water_keyboard(),
        parse_mode="Markdown"
    )


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
    
    # Красивое отображение часового пояса
    tz_names = {
        "Europe/Moscow": "Москва (UTC+3)",
        "Europe/Kaliningrad": "Калининград (UTC+2)",
        "Europe/Samara": "Самара (UTC+4)",
        "Asia/Yekaterinburg": "Екатеринбург (UTC+5)",
        "Asia/Omsk": "Омск (UTC+6)",
        "Asia/Krasnoyarsk": "Красноярск (UTC+7)",
        "Asia/Irkutsk": "Иркутск (UTC+8)",
        "Asia/Vladivostok": "Владивосток (UTC+10)",
        "Europe/Kiev": "Киев (UTC+2)",
        "Europe/Minsk": "Минск (UTC+3)",
        "Asia/Almaty": "Алматы (UTC+6)",
    }
    tz_display = tz_names.get(user.timezone, user.timezone)
    
    await callback.message.edit_text(
        f"⚙️ *Настройки*\n\n"
        f"🔔 Уведомления: {'✅ Вкл' if user.notifications_enabled else '❌ Выкл'}\n"
        f"⏰ Подъём: {user.wake_time}\n"
        f"🌙 Отход ко сну: {user.sleep_time}\n"
        f"🌍 Часовой пояс: {tz_display}\n\n"
        f"Выбери, что изменить:",
        reply_markup=get_settings_keyboard(),
        parse_mode="Markdown"
    )


@router.callback_query(F.data == "settings_timezone")
async def show_timezone_settings(callback: CallbackQuery):
    """Показать выбор часового пояса"""
    await callback.answer()
    
    await callback.message.edit_text(
        "🌍 *Выбор часового пояса*\n\n"
        "Выбери свой часовой пояс для корректной работы напоминаний:",
        reply_markup=get_timezone_keyboard(),
        parse_mode="Markdown"
    )


@router.callback_query(F.data.startswith("tz_"))
async def set_timezone(callback: CallbackQuery, session: AsyncSession):
    """Установить часовой пояс"""
    timezone = callback.data.replace("tz_", "")
    
    result = await session.execute(
        select(User).where(User.telegram_id == callback.from_user.id)
    )
    user = result.scalar_one_or_none()
    
    if user:
        user.timezone = timezone
        await session.commit()
    
    tz_names = {
        "Europe/Moscow": "Москва (UTC+3)",
        "Europe/Kaliningrad": "Калининград (UTC+2)",
        "Europe/Samara": "Самара (UTC+4)",
        "Asia/Yekaterinburg": "Екатеринбург (UTC+5)",
        "Asia/Omsk": "Омск (UTC+6)",
        "Asia/Krasnoyarsk": "Красноярск (UTC+7)",
        "Asia/Irkutsk": "Иркутск (UTC+8)",
        "Asia/Vladivostok": "Владивосток (UTC+10)",
        "Europe/Kiev": "Киев (UTC+2)",
        "Europe/Minsk": "Минск (UTC+3)",
        "Asia/Almaty": "Алматы (UTC+6)",
    }
    
    await callback.answer(f"✅ Часовой пояс установлен!")
    
    await callback.message.edit_text(
        f"✅ *Часовой пояс изменён!*\n\n"
        f"🌍 Новый часовой пояс: {tz_names.get(timezone, timezone)}\n\n"
        f"Теперь напоминания будут приходить в правильное время.",
        reply_markup=get_back_to_menu_keyboard(),
        parse_mode="Markdown"
    )


@router.callback_query(F.data == "settings_notifications")
async def show_notifications_settings(callback: CallbackQuery, session: AsyncSession):
    """Показать настройки уведомлений"""
    await callback.answer()
    
    result = await session.execute(
        select(User).where(User.telegram_id == callback.from_user.id)
    )
    user = result.scalar_one_or_none()
    
    if not user:
        return
    
    status = "✅ Включены" if user.notifications_enabled else "❌ Выключены"
    
    await callback.message.edit_text(
        f"🔔 *Настройки уведомлений*\n\n"
        f"Текущий статус: {status}\n\n"
        f"Уведомления включают:\n"
        f"• 🌅 Утреннее приветствие\n"
        f"• 🍽️ Напоминания о еде\n"
        f"• 💧 Напоминания о воде\n"
        f"• 🏋️ Напоминания о тренировке\n"
        f"• 🌙 Вечерний итог дня",
        reply_markup=get_notifications_keyboard(user.notifications_enabled),
        parse_mode="Markdown"
    )


@router.callback_query(F.data.in_({"notif_on", "notif_off"}))
async def toggle_notifications(callback: CallbackQuery, session: AsyncSession):
    """Включить/выключить уведомления"""
    enable = callback.data == "notif_on"
    
    result = await session.execute(
        select(User).where(User.telegram_id == callback.from_user.id)
    )
    user = result.scalar_one_or_none()
    
    if user:
        user.notifications_enabled = enable
        await session.commit()
    
    status = "включены ✅" if enable else "выключены ❌"
    await callback.answer(f"Уведомления {status}")
    
    await callback.message.edit_text(
        f"{'🔔' if enable else '🔕'} *Уведомления {status}*\n\n"
        f"{'Теперь ты будешь получать напоминания!' if enable else 'Напоминания отключены. Ты можешь включить их обратно в любое время.'}",
        reply_markup=get_back_to_menu_keyboard(),
        parse_mode="Markdown"
    )


@router.callback_query(F.data == "settings_wake")
async def show_wake_time_settings(callback: CallbackQuery, session: AsyncSession):
    """Показать настройку времени подъёма"""
    await callback.answer()
    
    result = await session.execute(
        select(User).where(User.telegram_id == callback.from_user.id)
    )
    user = result.scalar_one_or_none()
    
    current_time = user.wake_time if user else "07:00"
    
    await callback.message.edit_text(
        f"⏰ *Время подъёма*\n\n"
        f"Текущее время: {current_time}\n\n"
        f"Выбери время, когда ты обычно просыпаешься:",
        reply_markup=get_time_keyboard("wake"),
        parse_mode="Markdown"
    )


@router.callback_query(F.data == "settings_sleep")
async def show_sleep_time_settings(callback: CallbackQuery, session: AsyncSession):
    """Показать настройку времени сна"""
    await callback.answer()
    
    result = await session.execute(
        select(User).where(User.telegram_id == callback.from_user.id)
    )
    user = result.scalar_one_or_none()
    
    current_time = user.sleep_time if user else "23:00"
    
    await callback.message.edit_text(
        f"🌙 *Время отхода ко сну*\n\n"
        f"Текущее время: {current_time}\n\n"
        f"Выбери время, когда ты обычно ложишься спать:",
        reply_markup=get_time_keyboard("sleep"),
        parse_mode="Markdown"
    )


@router.callback_query(F.data.startswith("time_"))
async def set_time(callback: CallbackQuery, session: AsyncSession):
    """Установить время подъёма/сна"""
    parts = callback.data.split("_")
    time_type = parts[1]  # wake или sleep
    time_value = parts[2]  # HH:MM
    
    result = await session.execute(
        select(User).where(User.telegram_id == callback.from_user.id)
    )
    user = result.scalar_one_or_none()
    
    if user:
        if time_type == "wake":
            user.wake_time = time_value
            label = "подъёма"
            emoji = "⏰"
        else:
            user.sleep_time = time_value
            label = "сна"
            emoji = "🌙"
        await session.commit()
    
    await callback.answer(f"✅ Время установлено!")
    
    await callback.message.edit_text(
        f"{emoji} *Время {label} изменено!*\n\n"
        f"Новое время: {time_value}\n\n"
        f"Напоминания будут приходить с учётом этого времени.",
        reply_markup=get_back_to_menu_keyboard(),
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
    
    if not user:
        return
    
    # Загружаем профиль
    profile_result = await session.execute(
        select(UserProfile).where(UserProfile.user_id == user.id)
    )
    profile = profile_result.scalar_one_or_none()
    
    if not profile:
        return
    
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
        reply_markup=get_back_to_menu_keyboard(),
        parse_mode="Markdown"
    )
