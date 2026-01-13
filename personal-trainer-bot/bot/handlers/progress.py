"""
Обработчики прогресса и весов
"""
from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from datetime import date

from database.models import User, WeightLog
from bot.keyboards import get_main_menu_keyboard, get_back_keyboard
from bot.states import ProgressStates

router = Router(name="progress")


@router.callback_query(F.data == "weight")
async def show_weight_menu(callback: CallbackQuery, state: FSMContext):
    """Показать меню веса"""
    await callback.answer()
    
    await state.set_state(ProgressStates.waiting_weight)
    
    await callback.message.edit_text(
        "⚖️ *Запись веса*\n\n"
        "Введи текущий вес в кг:\n\n"
        "Например: 75.5",
        parse_mode="Markdown"
    )


@router.message(Command("weight"))
async def cmd_weight(message: Message, state: FSMContext):
    """Команда /weight"""
    await state.set_state(ProgressStates.waiting_weight)
    
    await message.answer(
        "⚖️ *Запись веса*\n\n"
        "Введи текущий вес в кг:\n\n"
        "Например: 75.5",
        parse_mode="Markdown"
    )


@router.message(ProgressStates.waiting_weight)
async def process_weight(message: Message, state: FSMContext, session: AsyncSession):
    """Обработка веса"""
    try:
        weight = float(message.text.strip().replace(",", "."))
        if weight < 30 or weight > 300:
            raise ValueError
    except ValueError:
        await message.answer(
            "Пожалуйста, введи корректный вес (30-300 кг)\n"
            "Например: 75.5"
        )
        return
    
    result = await session.execute(
        select(User).where(User.telegram_id == message.from_user.id)
    )
    user = result.scalar_one_or_none()
    
    if not user:
        await message.answer("Ошибка. Попробуй /start")
        await state.clear()
        return
    
    today = date.today()
    
    # Проверяем, есть ли уже запись за сегодня
    existing_result = await session.execute(
        select(WeightLog).where(
            WeightLog.user_id == user.id,
            WeightLog.date == today
        )
    )
    existing_log = existing_result.scalar_one_or_none()
    
    if existing_log:
        existing_log.weight = weight
    else:
        weight_log = WeightLog(
            user_id=user.id,
            date=today,
            weight=weight
        )
        session.add(weight_log)
    
    # Загружаем и обновляем профиль
    from database.models import UserProfile
    profile_result = await session.execute(
        select(UserProfile).where(UserProfile.user_id == user.id)
    )
    profile = profile_result.scalar_one_or_none()
    
    old_weight = None
    target_weight = None
    
    if profile:
        old_weight = profile.current_weight
        target_weight = profile.target_weight
        profile.current_weight = weight
        
        if old_weight:
            diff = old_weight - weight
            if diff > 0:
                diff_text = f"📉 -{diff:.1f} кг с последнего взвешивания"
            elif diff < 0:
                diff_text = f"📈 +{abs(diff):.1f} кг с последнего взвешивания"
            else:
                diff_text = "⚖️ Вес не изменился"
        else:
            diff_text = "Первое взвешивание записано!"
    else:
        diff_text = ""
    
    await session.commit()
    await state.clear()
    
    # Получаем историю веса
    history_result = await session.execute(
        select(WeightLog)
        .where(WeightLog.user_id == user.id)
        .order_by(WeightLog.date.desc())
        .limit(7)
    )
    history = history_result.scalars().all()
    
    # Формируем историю
    history_text = ""
    if len(history) > 1:
        history_text = "\n📊 *История (последние 7 дней):*\n"
        for log in reversed(history):
            history_text += f"├ {log.date.strftime('%d.%m')}: {log.weight} кг\n"
    
    target_text = ""
    if target_weight:
        remaining = weight - target_weight
        if remaining > 0:
            target_text = f"\n🎯 До цели: {remaining:.1f} кг"
        else:
            target_text = "\n🎉 Цель достигнута!"
    
    await message.answer(
        f"✅ *Вес записан!*\n\n"
        f"⚖️ Текущий вес: {weight} кг\n"
        f"{diff_text}"
        f"{target_text}"
        f"{history_text}",
        reply_markup=get_main_menu_keyboard(),
        parse_mode="Markdown"
    )


@router.message(Command("progress"))
async def cmd_progress(message: Message, session: AsyncSession):
    """Команда /progress"""
    result = await session.execute(
        select(User).where(User.telegram_id == message.from_user.id)
    )
    user = result.scalar_one_or_none()
    
    if not user or not user.is_onboarded:
        await message.answer("Сначала пройди регистрацию! /start")
        return
    
    # Загружаем профиль
    from database.models import UserProfile
    profile_result = await session.execute(
        select(UserProfile).where(UserProfile.user_id == user.id)
    )
    profile = profile_result.scalar_one_or_none()
    
    # Получаем историю веса
    weight_result = await session.execute(
        select(WeightLog)
        .where(WeightLog.user_id == user.id)
        .order_by(WeightLog.date.desc())
        .limit(30)
    )
    weight_history = weight_result.scalars().all()
    
    text = (
        f"📊 *ОТЧЁТ О ПРОГРЕССЕ*\n\n"
        f"👤 {profile.name}\n"
        f"📅 Начало: —\n\n"
        f"━━━━━━━━━━━━━━━━━━━━\n\n"
        f"⚖️ *ВЕС*\n"
        f"├ Текущий: {profile.current_weight} кг\n"
    )
    
    if profile.target_weight:
        remaining = profile.current_weight - profile.target_weight
        text += f"├ Цель: {profile.target_weight} кг\n"
        text += f"└ Осталось: {remaining:.1f} кг\n\n"
    else:
        text += "\n"
    
    if weight_history:
        text += "📈 *Динамика веса (последние записи):*\n"
        for log in weight_history[:5]:
            text += f"├ {log.date.strftime('%d.%m.%Y')}: {log.weight} кг\n"
        text += "\n"
    
    text += (
        f"🏋️ *ТРЕНИРОВКИ*\n"
        f"├ Всего: {user.total_workouts}\n"
        f"└ Текущий streak: {user.streak_days} дней 🔥\n\n"
        f"💪 Продолжай в том же духе!"
    )
    
    await message.answer(
        text,
        reply_markup=get_main_menu_keyboard(),
        parse_mode="Markdown"
    )
