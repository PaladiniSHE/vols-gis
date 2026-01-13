"""
Обработчики питания
"""
from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from datetime import date

from database.models import User, NutritionLog
from bot.keyboards import get_main_menu_keyboard, get_meal_keyboard, get_back_keyboard

router = Router(name="nutrition")


@router.callback_query(F.data == "nutrition")
async def show_nutrition(callback: CallbackQuery, session: AsyncSession):
    """Показать план питания на сегодня"""
    await callback.answer()
    
    result = await session.execute(
        select(User).where(User.telegram_id == callback.from_user.id)
    )
    user = result.scalar_one_or_none()
    
    if not user or not user.profile:
        await callback.message.edit_text(
            "Сначала пройди регистрацию!",
            reply_markup=get_back_keyboard("menu")
        )
        return
    
    profile = user.profile
    today = date.today()
    
    nutrition_text = (
        f"🍽️ *МЕНЮ НА {today.strftime('%d.%m.%Y')}*\n\n"
        f"📊 Целевые показатели:\n"
        f"├ Калории: {profile.target_calories} ккал\n"
        f"├ Белки: {profile.target_protein} г\n"
        f"├ Жиры: {profile.target_fat} г\n"
        f"└ Углеводы: {profile.target_carbs} г\n\n"
        f"━━━━━━━━━━━━━━━━━━━━\n\n"
        f"🌅 *ЗАВТРАК* (8:00) — ~450 ккал\n"
        f"├ Овсянка на воде — 60 г (сухой)\n"
        f"├ Банан — 1 шт\n"
        f"├ Грецкие орехи — 20 г\n"
        f"└ Мёд — 1 ч.л.\n\n"
        f"☀️ *ПЕРЕКУС 1* (11:00) — ~200 ккал\n"
        f"├ Творог 5% — 150 г\n"
        f"└ Ягоды — 50 г\n\n"
        f"🌞 *ОБЕД* (13:30) — ~550 ккал\n"
        f"├ Куриная грудка — 150 г\n"
        f"├ Гречка — 80 г (сухой)\n"
        f"├ Овощной салат — 150 г\n"
        f"└ Оливковое масло — 1 ст.л.\n\n"
        f"🌤️ *ПЕРЕКУС 2* (16:30) — ~250 ккал\n"
        f"├ Яблоко — 1 шт\n"
        f"└ Миндаль — 25 г\n\n"
        f"🌆 *УЖИН* (19:30) — ~450 ккал\n"
        f"├ Лосось запечённый — 150 г\n"
        f"├ Брокколи на пару — 200 г\n"
        f"└ Рис бурый — 50 г (сухой)\n\n"
        f"━━━━━━━━━━━━━━━━━━━━\n\n"
        f"📊 *ИТОГО:*\n"
        f"├ Калории: ~1900 ккал\n"
        f"├ Белки: ~140 г\n"
        f"├ Жиры: ~70 г\n"
        f"└ Углеводы: ~180 г\n\n"
        f"💧 Не забудь пить воду! Норма: {profile.target_water} л"
    )
    
    await callback.message.edit_text(
        nutrition_text,
        reply_markup=get_main_menu_keyboard(),
        parse_mode="Markdown"
    )


@router.message(Command("meal"))
async def cmd_meal(message: Message, session: AsyncSession):
    """Команда /meal"""
    result = await session.execute(
        select(User).where(User.telegram_id == message.from_user.id)
    )
    user = result.scalar_one_or_none()
    
    if not user or not user.is_onboarded:
        await message.answer("Сначала пройди регистрацию! /start")
        return
    
    class FakeCallback:
        def __init__(self, msg, from_user):
            self.message = msg
            self.from_user = from_user
        async def answer(self):
            pass
    
    fake = FakeCallback(message, message.from_user)
    await show_nutrition(fake, session)


@router.callback_query(F.data.startswith("meal_"))
async def process_meal(callback: CallbackQuery, session: AsyncSession):
    """Обработка приёма пищи"""
    await callback.answer()
    
    meal_status = callback.data.replace("meal_", "")
    
    result = await session.execute(
        select(User).where(User.telegram_id == callback.from_user.id)
    )
    user = result.scalar_one_or_none()
    
    if not user:
        return
    
    today = date.today()
    
    # Получаем или создаём лог питания
    log_result = await session.execute(
        select(NutritionLog).where(
            NutritionLog.user_id == user.id,
            NutritionLog.date == today
        )
    )
    nutrition_log = log_result.scalar_one_or_none()
    
    if not nutrition_log:
        nutrition_log = NutritionLog(user_id=user.id, date=today)
        session.add(nutrition_log)
    
    messages = {
        "on_plan": (
            "✅ *Отлично!*\n\n"
            "Приём пищи по плану — это путь к результату!\n"
            "Так держать! 💪"
        ),
        "modified": (
            "👍 *Хорошо!*\n\n"
            "Небольшие изменения — это нормально.\n"
            "Главное — придерживаться общей калорийности."
        ),
        "skipped": (
            "⚠️ *Пропуск приёма пищи*\n\n"
            "Старайся не пропускать приёмы пищи —\n"
            "это может привести к перееданию позже."
        ),
        "cheat": (
            "🍕 *Срыв случился*\n\n"
            "Это бывает, не кори себя!\n"
            "Один приём пищи не испортит всё.\n"
            "Важно вернуться к плану со следующего приёма."
        )
    }
    
    if meal_status == "cheat":
        nutrition_log.had_cheat = True
    
    await session.commit()
    
    await callback.message.edit_text(
        messages.get(meal_status, "Записано!"),
        reply_markup=get_main_menu_keyboard(),
        parse_mode="Markdown"
    )
