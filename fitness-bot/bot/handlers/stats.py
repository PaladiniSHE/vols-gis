"""
Обработчики для статистики
"""
from datetime import date, timedelta
from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext

from bot.keyboards.inline import InlineKeyboards
from bot.utils import create_progress_bar, create_water_bar
from core.database import async_session
from services.user_service import UserService
from services.stats_service import StatsService

router = Router()


@router.message(Command("stats"))
async def cmd_stats(message: Message, state: FSMContext):
    """Команда /stats"""
    await state.clear()
    await show_stats_menu(message)


@router.callback_query(F.data == "menu:stats")
async def callback_stats_menu(callback: CallbackQuery, state: FSMContext):
    """Меню статистики"""
    await state.clear()
    
    await callback.message.edit_text(
        "📊 *Статистика*\n\nВыбери период:",
        parse_mode="Markdown",
        reply_markup=InlineKeyboards.stats_menu()
    )
    await callback.answer()


async def show_stats_menu(message: Message):
    """Показать меню статистики"""
    await message.answer(
        "📊 *Статистика*\n\nВыбери период:",
        parse_mode="Markdown",
        reply_markup=InlineKeyboards.stats_menu()
    )


@router.callback_query(F.data == "stats:today")
async def callback_stats_today(callback: CallbackQuery):
    """Статистика за сегодня"""
    async with async_session() as session:
        user_service = UserService(session)
        stats_service = StatsService(session)
        
        user = await user_service.get_user_by_telegram_id(callback.from_user.id)
        if not user:
            await callback.answer("Сначала настройте профиль")
            return
        
        today = date.today()
        daily = await stats_service.get_daily_summary(user.id, today)
        
        # Прогресс-бары (length=10 для более компактного отображения)
        cal_bar = create_progress_bar(daily["calories"], user.daily_calories or 2000, length=10)
        prot_bar = create_progress_bar(daily["protein"], user.daily_protein or 100, length=10)
        fat_bar = create_progress_bar(daily["fat"], user.daily_fat or 65, length=10)
        carb_bar = create_progress_bar(daily["carbs"], user.daily_carbs or 250, length=10)
        water_bar = create_water_bar(daily["water_ml"], user.daily_water or 2.0, length=10)
        
        # Проценты
        cal_pct = int((daily["calories"] / (user.daily_calories or 1)) * 100)
        prot_pct = int((daily["protein"] / (user.daily_protein or 1)) * 100)
        fat_pct = int((daily["fat"] / (user.daily_fat or 1)) * 100)
        carb_pct = int((daily["carbs"] / (user.daily_carbs or 1)) * 100)
        water_pct = int((daily["water_liters"] / (user.daily_water or 1)) * 100)
        
        text = f"""
📊 *Статистика за сегодня*
📅 {today.strftime('%d.%m.%Y')}

🔥 *Калории:* {int(daily["calories"])} / {user.daily_calories or '—'} ккал ({cal_pct}%)
{cal_bar}

🥩 *Белки:* {daily["protein"]:.0f}г / {int(user.daily_protein or 0)}г ({prot_pct}%)
{prot_bar}

🧈 *Жиры:* {daily["fat"]:.0f}г / {int(user.daily_fat or 0)}г ({fat_pct}%)
{fat_bar}

🍞 *Углеводы:* {daily["carbs"]:.0f}г / {int(user.daily_carbs or 0)}г ({carb_pct}%)
{carb_bar}

💧 *Вода:* {daily["water_liters"]:.1f}л / {user.daily_water or 2.0}л ({water_pct}%)
{water_bar}
"""
        
        # Оценка дня
        goals_met = sum([
            cal_pct >= 80 and cal_pct <= 110,
            prot_pct >= 80,
            fat_pct <= 120,
            carb_pct >= 80 and carb_pct <= 120,
            water_pct >= 80
        ])
        
        if goals_met == 5:
            text += "\n🏆 *Отличный день!* Все цели выполнены!"
        elif goals_met >= 3:
            text += "\n👍 *Хороший день!* Большинство целей выполнено."
        else:
            text += "\n💪 *Продолжай стараться!* Завтра будет лучше."
        
        await callback.message.edit_text(
            text,
            parse_mode="Markdown",
            reply_markup=InlineKeyboards.stats_menu()
        )
    
    await callback.answer()


@router.callback_query(F.data == "stats:week")
async def callback_stats_week(callback: CallbackQuery):
    """Статистика за неделю"""
    async with async_session() as session:
        user_service = UserService(session)
        stats_service = StatsService(session)
        
        user = await user_service.get_user_by_telegram_id(callback.from_user.id)
        if not user:
            await callback.answer("Сначала настройте профиль")
            return
        
        # Получаем данные за неделю
        weekly = await stats_service.get_weekly_summary(user.id)
        averages = await stats_service.get_weekly_averages(user.id)
        weight_change = await stats_service.get_weight_change(user.id, days=7)
        
        text = "📊 *Статистика за неделю*\n\n"
        
        # Таблица по дням
        text += "```\n"
        text += "День   | Ккал  | Б  | Ж  | У  | 💧\n"
        text += "─" * 35 + "\n"
        
        for day_data in reversed(weekly):
            day_name = day_data["date"].strftime("%a")
            cal = int(day_data["calories"])
            p = int(day_data["protein"])
            f = int(day_data["fat"])
            c = int(day_data["carbs"])
            w = day_data["water_liters"]
            
            text += f"{day_name:6} | {cal:5} | {p:2} | {f:2} | {c:3} | {w:.1f}\n"
        
        text += "```\n"
        
        text += f"""
📈 *Средние показатели:*
├ 🔥 Калории: {int(averages['avg_calories'])} ккал/день
├ 🥩 Белки: {averages['avg_protein']:.0f}г/день
├ 🧈 Жиры: {averages['avg_fat']:.0f}г/день
└ 🍞 Углеводы: {averages['avg_carbs']:.0f}г/день
"""
        
        if weight_change:
            emoji = "📉" if weight_change < 0 else "📈" if weight_change > 0 else "➡️"
            text += f"\n⚖️ *Изменение веса:* {weight_change:+.1f} кг {emoji}"
        
        await callback.message.edit_text(
            text,
            parse_mode="Markdown",
            reply_markup=InlineKeyboards.stats_menu()
        )
    
    await callback.answer()


@router.callback_query(F.data == "stats:progress")
async def callback_stats_progress(callback: CallbackQuery):
    """Общий прогресс"""
    async with async_session() as session:
        user_service = UserService(session)
        stats_service = StatsService(session)
        
        user = await user_service.get_user_by_telegram_id(callback.from_user.id)
        if not user:
            await callback.answer("Сначала настройте профиль")
            return
        
        # Данные пользователя
        weight_history = await stats_service.get_weight_history(user.id, days=30)
        
        text = f"""
🏆 *Твой прогресс*

👤 *Профиль:*
├ 🔥 Серия: *{user.current_streak}* дней
├ 🏆 Рекорд: *{user.longest_streak}* дней
├ ⭐ Уровень: *{user.level}*
└ 💫 XP: *{user.xp}*

📊 *До следующего уровня:*
"""
        
        next_level_xp = user.level * 100
        current_level_xp = (user.level - 1) * 100
        xp_in_level = user.xp - current_level_xp
        xp_needed = next_level_xp - current_level_xp
        progress = int((xp_in_level / xp_needed) * 10)
        
        xp_bar = "▓" * progress + "░" * (10 - progress)
        text += f"{xp_bar} {xp_in_level}/{xp_needed} XP\n"
        
        text += "\n📈 *Достижения:*\n"
        
        # Достижения
        achievements = []
        
        if user.current_streak >= 7:
            achievements.append("🔥 Неделя дисциплины (7 дней подряд)")
        if user.current_streak >= 30:
            achievements.append("💪 Месяц силы воли (30 дней)")
        if user.longest_streak >= 100:
            achievements.append("🏆 Железная привычка (100 дней)")
        if user.level >= 10:
            achievements.append("⭐ Продвинутый (уровень 10)")
        if user.level >= 25:
            achievements.append("🌟 Эксперт (уровень 25)")
        if len(weight_history) >= 10:
            achievements.append("⚖️ Следящий за весом (10+ записей)")
        
        if achievements:
            for a in achievements[:5]:
                text += f"├ {a}\n"
        else:
            text += "├ Пока нет достижений\n"
            text += "├ Продолжай вести дневник!\n"
        
        text += "\n💡 *Советы:*\n"
        
        if user.current_streak < 7:
            text += "• Веди дневник 7 дней подряд для первого достижения\n"
        if user.level < 10:
            text += "• Набери XP за записи питания и воды\n"
        
        await callback.message.edit_text(
            text,
            parse_mode="Markdown",
            reply_markup=InlineKeyboards.stats_menu()
        )
    
    await callback.answer()
