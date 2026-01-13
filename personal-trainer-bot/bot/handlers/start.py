"""
Обработчик команды /start и базовых команд
"""
from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command, CommandStart
from aiogram.fsm.context import FSMContext
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from database.models import User, UserProfile
from bot.keyboards import get_start_keyboard, get_main_menu_keyboard
from bot.states import OnboardingStates

router = Router(name="start")


@router.message(CommandStart())
async def cmd_start(message: Message, session: AsyncSession, state: FSMContext):
    """Обработка команды /start"""
    
    # Проверяем, есть ли пользователь в БД
    result = await session.execute(
        select(User).where(User.telegram_id == message.from_user.id)
    )
    user = result.scalar_one_or_none()
    
    if user and user.is_onboarded:
        # Пользователь уже зарегистрирован
        await message.answer(
            f"С возвращением, {user.profile.name or user.first_name}! 👋\n\n"
            "Рад снова тебя видеть! Что будем делать?",
            reply_markup=get_main_menu_keyboard()
        )
    else:
        # Новый пользователь или не завершил онбординг
        if not user:
            # Создаём нового пользователя
            user = User(
                telegram_id=message.from_user.id,
                username=message.from_user.username,
                first_name=message.from_user.first_name,
                last_name=message.from_user.last_name,
                language_code=message.from_user.language_code or "ru"
            )
            session.add(user)
            await session.flush()
            
            # Создаём профиль
            profile = UserProfile(user_id=user.id)
            session.add(profile)
            await session.commit()
        
        await message.answer(
            "Привет! 👋 Я — твой персональный ИИ-тренер!\n\n"
            "Я помогу тебе:\n"
            "✅ Составить программу тренировок\n"
            "✅ Создать план питания\n"
            "✅ Отслеживать прогресс\n"
            "✅ Достичь твоих целей!\n\n"
            "Давай начнём с короткой анкеты (5-7 минут).\n"
            "Это поможет мне создать идеальный план именно для тебя.",
            reply_markup=get_start_keyboard()
        )


@router.callback_query(F.data == "start_onboarding")
async def start_onboarding(callback: CallbackQuery, state: FSMContext):
    """Начать онбординг"""
    await callback.answer()
    
    await state.set_state(OnboardingStates.waiting_name)
    
    await callback.message.edit_text(
        "Отлично! Давай познакомимся 🤝\n\n"
        "Как тебя зовут?",
    )


@router.callback_query(F.data == "about_bot")
async def about_bot(callback: CallbackQuery):
    """Информация о боте"""
    await callback.answer()
    
    await callback.message.edit_text(
        "🤖 *О боте «Личный Тренер»*\n\n"
        "Я — ИИ-тренер, который поможет тебе достичь фитнес-целей!\n\n"
        "*Что я умею:*\n"
        "🏋️ Создаю персональные программы тренировок\n"
        "🍽️ Составляю план питания с рецептами\n"
        "📊 Отслеживаю твой прогресс\n"
        "⏰ Напоминаю о тренировках и питании\n"
        "💪 Мотивирую и поддерживаю!\n\n"
        "*Как это работает:*\n"
        "1. Ты заполняешь анкету (5-7 минут)\n"
        "2. Я создаю индивидуальную программу\n"
        "3. Каждый день получаешь план и напоминания\n"
        "4. Отмечаешь выполнение\n"
        "5. Достигаешь результата! 🎯\n\n"
        "Готов начать?",
        reply_markup=get_start_keyboard(),
        parse_mode="Markdown"
    )


@router.message(Command("menu"))
async def cmd_menu(message: Message, session: AsyncSession):
    """Показать главное меню"""
    result = await session.execute(
        select(User).where(User.telegram_id == message.from_user.id)
    )
    user = result.scalar_one_or_none()
    
    if not user or not user.is_onboarded:
        await message.answer(
            "Для доступа к меню нужно сначала пройти регистрацию! 📝",
            reply_markup=get_start_keyboard()
        )
        return
    
    await message.answer(
        f"Привет, {user.profile.name or user.first_name}! 👋\n"
        "Что будем делать?",
        reply_markup=get_main_menu_keyboard()
    )


@router.message(Command("help"))
async def cmd_help(message: Message):
    """Помощь"""
    await message.answer(
        "🆘 *Помощь*\n\n"
        "*Основные команды:*\n"
        "/start — Начать работу с ботом\n"
        "/menu — Главное меню\n"
        "/today — План на сегодня\n"
        "/workout — Тренировка на сегодня\n"
        "/meal — Питание на сегодня\n"
        "/water — Отметить воду\n"
        "/weight — Записать вес\n"
        "/progress — Мой прогресс\n"
        "/settings — Настройки\n"
        "/help — Эта справка\n\n"
        "*Есть вопросы?*\n"
        "Просто напиши мне — я постараюсь помочь! 💬",
        parse_mode="Markdown"
    )
