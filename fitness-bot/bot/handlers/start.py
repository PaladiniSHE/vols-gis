"""
Обработчики стартовых команд
"""
from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command, CommandStart
from aiogram.fsm.context import FSMContext

from bot.keyboards.inline import InlineKeyboards
from bot.keyboards.reply import ReplyKeyboards
from bot.states import OnboardingStates
from bot.utils import create_progress_bar, create_water_bar
from core.database import async_session
from services.user_service import UserService
from services.stats_service import StatsService

router = Router()


@router.message(CommandStart())
async def cmd_start(message: Message, state: FSMContext):
    """Команда /start"""
    await state.clear()
    
    async with async_session() as session:
        user_service = UserService(session)
        user = await user_service.get_or_create_user(
            telegram_id=message.from_user.id,
            username=message.from_user.username,
            first_name=message.from_user.first_name,
            last_name=message.from_user.last_name
        )
        
        if not user.is_onboarded:
            # Начинаем онбординг с индикатором прогресса
            progress = "[1/6] ●○○○○○"
            text = f"""
👋 Привет, {user.display_name}!

Я твой *личный тренер* в Telegram! 🏋️

Помогу тебе:
• Отслеживать питание и считать калории
• Контролировать водный баланс
• Следить за весом и прогрессом
• Достигать фитнес-целей

Давай начнём с настройки твоего профиля!
Это займёт всего пару минут.

{progress}

👤 *Укажи свой пол:*
"""
            await message.answer(
                text,
                parse_mode="Markdown",
                reply_markup=InlineKeyboards.gender_select()
            )
            await state.set_state(OnboardingStates.waiting_for_gender)
        else:
            # Показываем главное меню с текущей статистикой
            await show_main_menu(message, user, session)


async def show_main_menu(message: Message, user, session):
    """Показать главное меню с текущей статистикой"""
    from datetime import date
    
    stats_service = StatsService(session)
    daily = await stats_service.get_daily_summary(user.id, date.today())
    
    # Формируем текст
    cal_bar = create_progress_bar(daily["calories"], user.daily_calories or 2000)
    water_bar = create_water_bar(daily["water_ml"], user.daily_water or 2.0)
    
    text = f"""
🏠 *Главное меню*

👋 Привет, {user.display_name}!

📊 *Сегодня:*

🔥 Калории: {int(daily["calories"])} / {user.daily_calories or '—'} ккал
{cal_bar}

🥩 Б: {daily["protein"]:.0f}г  🧈 Ж: {daily["fat"]:.0f}г  🍞 У: {daily["carbs"]:.0f}г

💧 Вода: {daily["water_liters"]}л / {user.daily_water or 2.0}л
{water_bar}

🔥 Серия: {user.current_streak} дней | ⭐ Уровень: {user.level}
"""
    
    await message.answer(
        text,
        parse_mode="Markdown",
        reply_markup=InlineKeyboards.main_menu()
    )


@router.message(Command("menu"))
async def cmd_menu(message: Message, state: FSMContext):
    """Команда /menu"""
    await state.clear()
    
    async with async_session() as session:
        user_service = UserService(session)
        user = await user_service.get_user_by_telegram_id(message.from_user.id)
        
        if user and user.is_onboarded:
            await show_main_menu(message, user, session)
        else:
            await cmd_start(message, state)


@router.message(Command("help"))
async def cmd_help(message: Message):
    """Команда /help"""
    text = """
📖 *Помощь по боту "Личный тренер"*

*Основные команды:*
/start - Запуск бота
/menu - Главное меню
/food - Дневник питания
/water - Трекер воды
/weight - Записать вес
/stats - Статистика
/profile - Профиль
/reminders - Настройка напоминаний

*Быстрые команды:*
/quick\_food - Быстро добавить еду
/quick\_water - Добавить воду (250мл)

*Управление аккаунтом:*
/export - Экспорт ваших данных
/delete\_account - Удаление аккаунта
/support - Связь с поддержкой

*Как пользоваться:*
1. Записывай все приемы пищи
2. Отмечай выпитую воду
3. Взвешивайся регулярно
4. Следи за прогрессом

💡 *Совет:* Для лучших результатов веди дневник каждый день!
"""
    await message.answer(text, parse_mode="Markdown")


@router.callback_query(F.data == "menu:main")
async def callback_main_menu(callback: CallbackQuery, state: FSMContext):
    """Возврат в главное меню"""
    await state.clear()
    
    async with async_session() as session:
        user_service = UserService(session)
        user = await user_service.get_user_by_telegram_id(callback.from_user.id)
        
        if user and user.is_onboarded:
            stats_service = StatsService(session)
            from datetime import date
            daily = await stats_service.get_daily_summary(user.id, date.today())
            
            cal_bar = create_progress_bar(daily["calories"], user.daily_calories or 2000)
            water_bar = create_water_bar(daily["water_ml"], user.daily_water or 2.0)
            
            text = f"""
🏠 *Главное меню*

📊 *Сегодня:*

🔥 Калории: {int(daily["calories"])} / {user.daily_calories or '—'} ккал
{cal_bar}

🥩 Б: {daily["protein"]:.0f}г  🧈 Ж: {daily["fat"]:.0f}г  🍞 У: {daily["carbs"]:.0f}г

💧 Вода: {daily["water_liters"]}л / {user.daily_water or 2.0}л
{water_bar}

🔥 Серия: {user.current_streak} дней | ⭐ Уровень: {user.level}
"""
            
            await callback.message.edit_text(
                text,
                parse_mode="Markdown",
                reply_markup=InlineKeyboards.main_menu()
            )
    
    await callback.answer()


@router.callback_query(F.data == "cancel")
async def callback_cancel(callback: CallbackQuery, state: FSMContext):
    """Отмена действия"""
    await state.clear()
    await callback.message.edit_text("❌ Действие отменено")
    await callback.answer()
