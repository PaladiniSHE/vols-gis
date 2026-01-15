"""
Обработчики для трекера воды
"""
from datetime import date
from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext

from bot.keyboards.inline import InlineKeyboards
from bot.states import WaterStates
from bot.config import Constants
from bot.utils import create_water_bar
from core.database import async_session
from services.user_service import UserService
from services.water_service import WaterService

router = Router()


@router.message(Command("water"))
async def cmd_water(message: Message, state: FSMContext):
    """Команда /water"""
    await state.clear()
    await show_water_menu(message)


@router.callback_query(F.data == "menu:water")
async def callback_water_menu(callback: CallbackQuery, state: FSMContext):
    """Меню воды"""
    await state.clear()
    
    async with async_session() as session:
        user_service = UserService(session)
        water_service = WaterService(session)
        
        user = await user_service.get_user_by_telegram_id(callback.from_user.id)
        if not user:
            await callback.answer("Сначала настройте профиль с помощью /start")
            return
        
        today = date.today()
        total_ml = await water_service.get_daily_total(user.id, today)
        goal_liters = user.daily_water or 2.0
        
        water_bar = create_water_bar(total_ml, goal_liters)
        current_liters = total_ml / 1000
        percent = int((total_ml / (goal_liters * 1000)) * 100) if goal_liters > 0 else 0
        
        glasses = total_ml // 250  # Стаканов по 250мл
        
        text = f"""
💧 *Водный баланс*

📅 Сегодня: {today.strftime('%d.%m.%Y')}

💧 Выпито: *{current_liters:.1f}л* / {goal_liters}л ({percent}%)
{water_bar}

🥤 Это примерно *{glasses}* стаканов воды

Добавь выпитую воду:
"""
        
        await callback.message.edit_text(
            text,
            parse_mode="Markdown",
            reply_markup=InlineKeyboards.water_amounts()
        )
    
    await callback.answer()


async def show_water_menu(message: Message):
    """Показать меню воды"""
    async with async_session() as session:
        user_service = UserService(session)
        water_service = WaterService(session)
        
        user = await user_service.get_user_by_telegram_id(message.from_user.id)
        if not user:
            await message.answer("Сначала настройте профиль с помощью /start")
            return
        
        today = date.today()
        total_ml = await water_service.get_daily_total(user.id, today)
        goal_liters = user.daily_water or 2.0
        
        water_bar = create_water_bar(total_ml, goal_liters)
        current_liters = total_ml / 1000
        percent = int((total_ml / (goal_liters * 1000)) * 100) if goal_liters > 0 else 0
        
        glasses = total_ml // 250
        
        text = f"""
💧 *Водный баланс*

📅 Сегодня: {today.strftime('%d.%m.%Y')}

💧 Выпито: *{current_liters:.1f}л* / {goal_liters}л ({percent}%)
{water_bar}

🥤 Это примерно *{glasses}* стаканов воды

Добавь выпитую воду:
"""
        
        await message.answer(
            text,
            parse_mode="Markdown",
            reply_markup=InlineKeyboards.water_amounts()
        )


@router.callback_query(F.data.startswith("water:") & ~F.data.in_(["water:custom", "water:undo"]))
async def callback_add_water(callback: CallbackQuery, state: FSMContext):
    """Добавить воду"""
    amount = int(callback.data.split(":")[1])
    
    async with async_session() as session:
        user_service = UserService(session)
        water_service = WaterService(session)
        
        user = await user_service.get_user_by_telegram_id(callback.from_user.id)
        today = date.today()
        
        # Добавляем запись
        await water_service.add_water_entry(user.id, amount, today)
        
        # Обновляем серию и XP
        await user_service.update_streak(callback.from_user.id)
        await user_service.add_xp(callback.from_user.id, Constants.XP_LOG_WATER)
        
        # Получаем обновленные данные
        total_ml = await water_service.get_daily_total(user.id, today)
        goal_liters = user.daily_water or 2.0
        
        water_bar = create_water_bar(total_ml, goal_liters)
        current_liters = total_ml / 1000
        percent = int((total_ml / (goal_liters * 1000)) * 100) if goal_liters > 0 else 0
        
        # Проверяем достижение цели
        goal_reached = total_ml >= (goal_liters * 1000)
        bonus_text = ""
        if goal_reached and total_ml - amount < (goal_liters * 1000):
            bonus_text = "\n\n🎉 *Поздравляем!* Дневная норма выполнена!"
        
        glasses = total_ml // 250
        
        text = f"""
💧 *Водный баланс*

✅ Добавлено: *+{amount}мл* (+{Constants.XP_LOG_WATER} XP ⭐)

💧 Выпито: *{current_liters:.1f}л* / {goal_liters}л ({percent}%)
{water_bar}

🥤 Это примерно *{glasses}* стаканов воды
{bonus_text}

Добавь ещё воды:
"""
        
        await callback.message.edit_text(
            text,
            parse_mode="Markdown",
            reply_markup=InlineKeyboards.water_amounts()
        )
    
    await callback.answer(f"✅ +{amount}мл")


@router.callback_query(F.data == "water:custom")
async def callback_custom_water(callback: CallbackQuery, state: FSMContext):
    """Ввести произвольное количество воды"""
    await callback.message.edit_text(
        "💧 *Введи количество воды в миллилитрах:*\n\nНапример: 350",
        parse_mode="Markdown"
    )
    await state.set_state(WaterStates.entering_amount)
    await callback.answer()


@router.message(WaterStates.entering_amount)
async def process_custom_water(message: Message, state: FSMContext):
    """Обработка произвольного количества воды"""
    try:
        amount = int(message.text.strip())
        
        if amount <= 0 or amount > 5000:
            await message.answer("⚠️ Введите корректное количество (1-5000 мл)")
            return
        
        async with async_session() as session:
            user_service = UserService(session)
            water_service = WaterService(session)
            
            user = await user_service.get_user_by_telegram_id(message.from_user.id)
            today = date.today()
            
            # Добавляем запись
            await water_service.add_water_entry(user.id, amount, today)
            
            # Обновляем серию и XP
            await user_service.update_streak(message.from_user.id)
            await user_service.add_xp(message.from_user.id, Constants.XP_LOG_WATER)
            
            # Получаем обновленные данные
            total_ml = await water_service.get_daily_total(user.id, today)
            goal_liters = user.daily_water or 2.0
            
            water_bar = create_water_bar(total_ml, goal_liters)
            current_liters = total_ml / 1000
            percent = int((total_ml / (goal_liters * 1000)) * 100) if goal_liters > 0 else 0
            
            text = f"""
💧 *Водный баланс*

✅ Добавлено: *+{amount}мл* (+{Constants.XP_LOG_WATER} XP ⭐)

💧 Выпито: *{current_liters:.1f}л* / {goal_liters}л ({percent}%)
{water_bar}

Добавь ещё воды:
"""
            
            await message.answer(
                text,
                parse_mode="Markdown",
                reply_markup=InlineKeyboards.water_amounts()
            )
        
        await state.clear()
        
    except ValueError:
        await message.answer("⚠️ Введите число в миллилитрах (например: 350)")


@router.callback_query(F.data == "water:undo")
async def callback_undo_water(callback: CallbackQuery):
    """Отменить последнюю запись воды"""
    async with async_session() as session:
        user_service = UserService(session)
        water_service = WaterService(session)
        
        user = await user_service.get_user_by_telegram_id(callback.from_user.id)
        today = date.today()
        
        # Удаляем последнюю запись
        deleted = await water_service.delete_last_entry(user.id, today)
        
        if deleted:
            # Получаем обновленные данные
            total_ml = await water_service.get_daily_total(user.id, today)
            goal_liters = user.daily_water or 2.0
            
            water_bar = create_water_bar(total_ml, goal_liters)
            current_liters = total_ml / 1000
            percent = int((total_ml / (goal_liters * 1000)) * 100) if goal_liters > 0 else 0
            
            text = f"""
💧 *Водный баланс*

↩️ Последняя запись отменена

💧 Выпито: *{current_liters:.1f}л* / {goal_liters}л ({percent}%)
{water_bar}

Добавь воду:
"""
            
            await callback.message.edit_text(
                text,
                parse_mode="Markdown",
                reply_markup=InlineKeyboards.water_amounts()
            )
            await callback.answer("↩️ Отменено")
        else:
            await callback.answer("❌ Нет записей для отмены")


@router.message(Command("quick_water"))
async def cmd_quick_water(message: Message):
    """Быстро добавить 250мл воды"""
    async with async_session() as session:
        user_service = UserService(session)
        water_service = WaterService(session)
        
        user = await user_service.get_user_by_telegram_id(message.from_user.id)
        if not user:
            await message.answer("Сначала настройте профиль с помощью /start")
            return
        
        today = date.today()
        
        # Добавляем 250мл
        await water_service.add_water_entry(user.id, 250, today)
        await user_service.update_streak(message.from_user.id)
        await user_service.add_xp(message.from_user.id, Constants.XP_LOG_WATER)
        
        total_ml = await water_service.get_daily_total(user.id, today)
        goal_liters = user.daily_water or 2.0
        current_liters = total_ml / 1000
        percent = int((total_ml / (goal_liters * 1000)) * 100) if goal_liters > 0 else 0
        
        await message.answer(
            f"💧 +250мл | Всего: *{current_liters:.1f}л* / {goal_liters}л ({percent}%)",
            parse_mode="Markdown"
        )
