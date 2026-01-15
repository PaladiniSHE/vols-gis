"""
Обработчики для трекера веса
"""
from datetime import date
from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext

from bot.keyboards.inline import InlineKeyboards
from bot.states import WeightStates
from bot.config import Constants
from core.database import async_session
from services.user_service import UserService
from services.stats_service import StatsService
from services.calculator import CalculatorService

router = Router()


@router.message(Command("weight"))
async def cmd_weight(message: Message, state: FSMContext):
    """Команда /weight"""
    await state.clear()
    await show_weight_menu(message)


@router.callback_query(F.data == "menu:weight")
async def callback_weight_menu(callback: CallbackQuery, state: FSMContext):
    """Меню веса"""
    await state.clear()
    
    async with async_session() as session:
        user_service = UserService(session)
        stats_service = StatsService(session)
        calculator = CalculatorService()
        
        user = await user_service.get_user_by_telegram_id(callback.from_user.id)
        if not user:
            await callback.answer("Сначала настройте профиль с помощью /start")
            return
        
        # Получаем историю веса
        weight_history = await stats_service.get_weight_history(user.id, days=30)
        week_change = await stats_service.get_weight_change(user.id, days=7)
        
        # BMI
        bmi_data = None
        if user.height and user.weight:
            bmi_data = calculator.calculate_bmi(user.weight, user.height)
        
        last_weight = weight_history[-1].weight if weight_history else user.weight
        
        text = f"""
⚖️ *Трекер веса*

📊 *Текущие данные:*
├ Вес: *{last_weight or '—'}* кг
├ Цель: {user.goal_weight or '—'} кг
"""
        
        if bmi_data:
            text += f"└ BMI: {bmi_data['bmi']} ({bmi_data['category']}) {bmi_data['emoji']}\n"
        
        text += f"""
📈 *Динамика:*
├ За неделю: {f'{week_change:+.1f}' if week_change else '—'} кг
└ Записей: {len(weight_history)} за 30 дней
"""
        
        if user.goal_weight and last_weight:
            diff = last_weight - user.goal_weight
            if diff > 0:
                text += f"\n🎯 До цели: *{diff:.1f}* кг"
            elif diff < 0:
                text += f"\n🎯 Цель достигнута! +{abs(diff):.1f} кг сверх"
            else:
                text += "\n🎯 *Цель достигнута!* 🎉"
        
        await callback.message.edit_text(
            text,
            parse_mode="Markdown",
            reply_markup=InlineKeyboards.weight_menu()
        )
    
    await callback.answer()


async def show_weight_menu(message: Message):
    """Показать меню веса"""
    async with async_session() as session:
        user_service = UserService(session)
        stats_service = StatsService(session)
        calculator = CalculatorService()
        
        user = await user_service.get_user_by_telegram_id(message.from_user.id)
        if not user:
            await message.answer("Сначала настройте профиль с помощью /start")
            return
        
        weight_history = await stats_service.get_weight_history(user.id, days=30)
        week_change = await stats_service.get_weight_change(user.id, days=7)
        
        bmi_data = None
        if user.height and user.weight:
            bmi_data = calculator.calculate_bmi(user.weight, user.height)
        
        last_weight = weight_history[-1].weight if weight_history else user.weight
        
        text = f"""
⚖️ *Трекер веса*

📊 *Текущие данные:*
├ Вес: *{last_weight or '—'}* кг
├ Цель: {user.goal_weight or '—'} кг
"""
        
        if bmi_data:
            text += f"└ BMI: {bmi_data['bmi']} ({bmi_data['category']}) {bmi_data['emoji']}\n"
        
        text += f"""
📈 *Динамика:*
├ За неделю: {f'{week_change:+.1f}' if week_change else '—'} кг
└ Записей: {len(weight_history)} за 30 дней
"""
        
        await message.answer(
            text,
            parse_mode="Markdown",
            reply_markup=InlineKeyboards.weight_menu()
        )


@router.callback_query(F.data == "weight:log")
async def callback_log_weight(callback: CallbackQuery, state: FSMContext):
    """Записать вес"""
    await callback.message.edit_text(
        "⚖️ *Введи свой текущий вес в килограммах:*\n\nНапример: 70.5",
        parse_mode="Markdown"
    )
    await state.set_state(WeightStates.entering_weight)
    await callback.answer()


@router.message(WeightStates.entering_weight)
async def process_weight_entry(message: Message, state: FSMContext):
    """Обработка ввода веса"""
    try:
        weight = float(message.text.strip().replace(",", "."))
        
        if weight < 30 or weight > 300:
            await message.answer("⚠️ Введите корректный вес (30-300 кг)")
            return
        
        async with async_session() as session:
            user_service = UserService(session)
            stats_service = StatsService(session)
            calculator = CalculatorService()
            
            user = await user_service.get_user_by_telegram_id(message.from_user.id)
            today = date.today()
            
            # Сохраняем вес
            log = await stats_service.log_weight(user.id, weight, entry_date=today)
            
            # Обновляем вес в профиле
            await user_service.update_user_profile(message.from_user.id, weight=weight)
            
            # Обновляем серию и XP
            await user_service.update_streak(message.from_user.id)
            await user_service.add_xp(message.from_user.id, Constants.XP_LOG_WEIGHT)
            
            # Получаем изменение за неделю
            week_change = await stats_service.get_weight_change(user.id, days=7)
            
            # BMI
            bmi_data = calculator.calculate_bmi(weight, user.height) if user.height else None
            
            text = f"""
✅ *Вес записан!*

⚖️ Вес: *{weight}* кг (+{Constants.XP_LOG_WEIGHT} XP ⭐)
"""
            
            if bmi_data:
                text += f"📊 BMI: {bmi_data['bmi']} ({bmi_data['category']}) {bmi_data['emoji']}\n"
            
            if week_change:
                emoji = "📉" if week_change < 0 else "📈" if week_change > 0 else "➡️"
                text += f"\n{emoji} За неделю: *{week_change:+.1f}* кг"
            
            if user.goal_weight:
                diff = weight - user.goal_weight
                if diff > 0:
                    text += f"\n🎯 До цели: {diff:.1f} кг"
                elif diff < 0:
                    text += f"\n🎉 Цель достигнута! +{abs(diff):.1f} кг сверх"
                else:
                    text += "\n🎉 *Цель достигнута!*"
            
            await message.answer(
                text,
                parse_mode="Markdown",
                reply_markup=InlineKeyboards.back_to_menu()
            )
        
        await state.clear()
        
    except ValueError:
        await message.answer("⚠️ Введите вес числом (например: 70.5)")


@router.callback_query(F.data == "weight:history")
async def callback_weight_history(callback: CallbackQuery):
    """История веса"""
    async with async_session() as session:
        user_service = UserService(session)
        stats_service = StatsService(session)
        
        user = await user_service.get_user_by_telegram_id(callback.from_user.id)
        weight_history = await stats_service.get_weight_history(user.id, days=30)
        
        if not weight_history:
            await callback.message.edit_text(
                "📭 Нет записей о весе.\n\nНачни вести дневник веса!",
                reply_markup=InlineKeyboards.weight_menu()
            )
            await callback.answer()
            return
        
        text = "📈 *История веса (последние 30 дней):*\n\n"
        
        prev_weight = None
        for log in reversed(weight_history[-10:]):  # Последние 10 записей
            change = ""
            if prev_weight:
                diff = log.weight - prev_weight
                if diff > 0:
                    change = f" (+{diff:.1f})"
                elif diff < 0:
                    change = f" ({diff:.1f})"
            
            text += f"📅 {log.entry_date.strftime('%d.%m')}: *{log.weight}* кг{change}\n"
            prev_weight = log.weight
        
        if len(weight_history) > 1:
            first = weight_history[0].weight
            last = weight_history[-1].weight
            total_change = last - first
            
            text += f"\n━━━━━━━━━━━━━━━\n"
            text += f"📊 Изменение за период: *{total_change:+.1f}* кг"
        
        await callback.message.edit_text(
            text,
            parse_mode="Markdown",
            reply_markup=InlineKeyboards.weight_menu()
        )
    
    await callback.answer()


@router.callback_query(F.data == "weight:chart")
async def callback_weight_chart(callback: CallbackQuery):
    """График веса (текстовый)"""
    async with async_session() as session:
        user_service = UserService(session)
        stats_service = StatsService(session)
        
        user = await user_service.get_user_by_telegram_id(callback.from_user.id)
        weight_history = await stats_service.get_weight_history(user.id, days=14)
        
        if len(weight_history) < 2:
            await callback.message.edit_text(
                "📭 Недостаточно данных для графика.\n\nДобавьте больше записей о весе!",
                reply_markup=InlineKeyboards.weight_menu()
            )
            await callback.answer()
            return
        
        # Создаем текстовый график
        weights = [log.weight for log in weight_history]
        min_w = min(weights)
        max_w = max(weights)
        range_w = max_w - min_w if max_w != min_w else 1
        
        text = "📊 *График веса (14 дней):*\n\n"
        text += f"Max: {max_w} кг\n"
        
        chart_height = 8
        chart_width = min(len(weights), 14)
        
        for row in range(chart_height, 0, -1):
            line = ""
            threshold = min_w + (range_w * row / chart_height)
            
            for w in weights[-chart_width:]:
                if w >= threshold:
                    line += "█"
                else:
                    line += "░"
            
            text += f"{line}\n"
        
        text += f"Min: {min_w} кг\n"
        text += f"\n📅 Период: {weight_history[0].entry_date.strftime('%d.%m')} - {weight_history[-1].entry_date.strftime('%d.%m')}"
        
        total_change = weights[-1] - weights[0]
        trend = "📉 снижение" if total_change < 0 else "📈 рост" if total_change > 0 else "➡️ стабильно"
        text += f"\n📈 Тренд: *{total_change:+.1f}* кг ({trend})"
        
        await callback.message.edit_text(
            text,
            parse_mode="Markdown",
            reply_markup=InlineKeyboards.weight_menu()
        )
    
    await callback.answer()
