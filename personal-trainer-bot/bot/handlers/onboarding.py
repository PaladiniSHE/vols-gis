"""
Обработчики онбординга (анкеты)
"""
from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from database.models import User, UserProfile
from bot.keyboards import (
    get_gender_keyboard,
    get_goal_keyboard,
    get_fitness_level_keyboard,
    get_training_location_keyboard,
    get_diet_type_keyboard,
    get_work_type_keyboard,
    get_training_days_keyboard,
    get_confirmation_keyboard,
    get_main_menu_keyboard,
    get_skip_keyboard
)
from bot.states import OnboardingStates

router = Router(name="onboarding")


# === ЛИЧНЫЕ ДАННЫЕ ===

@router.message(OnboardingStates.waiting_name)
async def process_name(message: Message, state: FSMContext, session: AsyncSession):
    """Обработка имени"""
    name = message.text.strip()
    
    if len(name) < 2 or len(name) > 50:
        await message.answer("Пожалуйста, введи корректное имя (2-50 символов)")
        return
    
    await state.update_data(name=name)
    await state.set_state(OnboardingStates.waiting_age)
    
    await message.answer(
        f"Приятно познакомиться, {name}! 😊\n\n"
        "Сколько тебе лет?"
    )


@router.message(OnboardingStates.waiting_age)
async def process_age(message: Message, state: FSMContext):
    """Обработка возраста"""
    try:
        age = int(message.text.strip())
        if age < 14 or age > 100:
            raise ValueError
    except ValueError:
        await message.answer("Пожалуйста, введи корректный возраст (14-100)")
        return
    
    await state.update_data(age=age)
    await state.set_state(OnboardingStates.waiting_gender)
    
    await message.answer(
        "Отлично! Укажи свой пол:",
        reply_markup=get_gender_keyboard()
    )


@router.callback_query(OnboardingStates.waiting_gender, F.data.startswith("gender_"))
async def process_gender(callback: CallbackQuery, state: FSMContext):
    """Обработка пола"""
    await callback.answer()
    
    gender = callback.data.replace("gender_", "")
    await state.update_data(gender=gender)
    await state.set_state(OnboardingStates.waiting_height)
    
    await callback.message.edit_text(
        "Какой у тебя рост? (в см)\n\n"
        "Например: 175"
    )


@router.message(OnboardingStates.waiting_height)
async def process_height(message: Message, state: FSMContext):
    """Обработка роста"""
    try:
        height = float(message.text.strip().replace(",", "."))
        if height < 100 or height > 250:
            raise ValueError
    except ValueError:
        await message.answer("Пожалуйста, введи корректный рост в см (100-250)")
        return
    
    await state.update_data(height=height)
    await state.set_state(OnboardingStates.waiting_weight)
    
    await message.answer(
        "А текущий вес? (в кг)\n\n"
        "Например: 70.5"
    )


@router.message(OnboardingStates.waiting_weight)
async def process_weight(message: Message, state: FSMContext):
    """Обработка веса"""
    try:
        weight = float(message.text.strip().replace(",", "."))
        if weight < 30 or weight > 300:
            raise ValueError
    except ValueError:
        await message.answer("Пожалуйста, введи корректный вес в кг (30-300)")
        return
    
    await state.update_data(current_weight=weight)
    await state.set_state(OnboardingStates.waiting_goal)
    
    await message.answer(
        "Супер! Теперь самое важное — твоя цель 🎯\n\n"
        "Чего ты хочешь достичь?",
        reply_markup=get_goal_keyboard()
    )


# === ЦЕЛИ ===

@router.callback_query(OnboardingStates.waiting_goal, F.data.startswith("goal_"))
async def process_goal(callback: CallbackQuery, state: FSMContext):
    """Обработка цели"""
    await callback.answer()
    
    goal = callback.data.replace("goal_", "")
    await state.update_data(primary_goal=goal)
    
    goal_names = {
        "weight_loss": "похудение",
        "muscle_gain": "набор массы",
        "maintenance": "поддержание формы",
        "endurance": "выносливость",
        "health": "улучшение здоровья"
    }
    
    if goal == "weight_loss":
        await state.set_state(OnboardingStates.waiting_target_weight)
        await callback.message.edit_text(
            "Отлично! Какой вес ты хочешь достичь? (в кг)\n\n"
            "Например: 65"
        )
    else:
        await state.set_state(OnboardingStates.waiting_fitness_level)
        await callback.message.edit_text(
            f"Цель: {goal_names.get(goal, goal)} 👍\n\n"
            "Какой у тебя текущий уровень физической подготовки?",
            reply_markup=get_fitness_level_keyboard()
        )


@router.message(OnboardingStates.waiting_target_weight)
async def process_target_weight(message: Message, state: FSMContext):
    """Обработка целевого веса"""
    try:
        target_weight = float(message.text.strip().replace(",", "."))
        data = await state.get_data()
        current_weight = data.get("current_weight", 100)
        
        if target_weight < 30 or target_weight > current_weight:
            await message.answer(
                f"Целевой вес должен быть меньше текущего ({current_weight} кг) "
                "и не менее 30 кг"
            )
            return
    except ValueError:
        await message.answer("Пожалуйста, введи корректный вес в кг")
        return
    
    await state.update_data(target_weight=target_weight)
    await state.set_state(OnboardingStates.waiting_fitness_level)
    
    diff = current_weight - target_weight
    await message.answer(
        f"Цель: -{diff:.1f} кг 📉\n\n"
        "Какой у тебя текущий уровень физической подготовки?",
        reply_markup=get_fitness_level_keyboard()
    )


# === УРОВЕНЬ ПОДГОТОВКИ ===

@router.callback_query(OnboardingStates.waiting_fitness_level, F.data.startswith("level_"))
async def process_fitness_level(callback: CallbackQuery, state: FSMContext):
    """Обработка уровня подготовки"""
    await callback.answer()
    
    level = callback.data.replace("level_", "")
    await state.update_data(fitness_level=level)
    await state.set_state(OnboardingStates.waiting_training_days)
    
    await callback.message.edit_text(
        "Сколько дней в неделю ты готов тренироваться?",
        reply_markup=get_training_days_keyboard()
    )


@router.callback_query(OnboardingStates.waiting_training_days, F.data.startswith("days_"))
async def process_training_days(callback: CallbackQuery, state: FSMContext):
    """Обработка количества тренировочных дней"""
    await callback.answer()
    
    days = int(callback.data.replace("days_", ""))
    await state.update_data(training_days_per_week=days)
    await state.set_state(OnboardingStates.waiting_training_location)
    
    await callback.message.edit_text(
        f"Отлично, {days} дней в неделю! 💪\n\n"
        "Где ты планируешь заниматься?",
        reply_markup=get_training_location_keyboard()
    )


@router.callback_query(OnboardingStates.waiting_training_location, F.data.startswith("location_"))
async def process_training_location(callback: CallbackQuery, state: FSMContext):
    """Обработка места тренировок"""
    await callback.answer()
    
    location = callback.data.replace("location_", "")
    await state.update_data(training_location=location)
    await state.set_state(OnboardingStates.waiting_work_type)
    
    await callback.message.edit_text(
        "Какой у тебя тип работы?",
        reply_markup=get_work_type_keyboard()
    )


# === ОБРАЗ ЖИЗНИ ===

@router.callback_query(OnboardingStates.waiting_work_type, F.data.startswith("work_"))
async def process_work_type(callback: CallbackQuery, state: FSMContext):
    """Обработка типа работы"""
    await callback.answer()
    
    work_type = callback.data.replace("work_", "")
    await state.update_data(work_type=work_type)
    await state.set_state(OnboardingStates.waiting_diet_type)
    
    await callback.message.edit_text(
        "Теперь о питании 🍽️\n\n"
        "Какой тип питания тебе подходит?",
        reply_markup=get_diet_type_keyboard()
    )


# === ПИТАНИЕ ===

@router.callback_query(OnboardingStates.waiting_diet_type, F.data.startswith("diet_"))
async def process_diet_type(callback: CallbackQuery, state: FSMContext):
    """Обработка типа питания"""
    await callback.answer()
    
    diet_type = callback.data.replace("diet_", "")
    await state.update_data(diet_type=diet_type)
    await state.set_state(OnboardingStates.waiting_allergies)
    
    await callback.message.edit_text(
        "Есть ли у тебя пищевые аллергии или непереносимости?\n\n"
        "Напиши через запятую или отправь «нет»\n"
        "Например: орехи, молочные продукты, глютен"
    )


@router.message(OnboardingStates.waiting_allergies)
async def process_allergies(message: Message, state: FSMContext):
    """Обработка аллергий"""
    text = message.text.strip().lower()
    
    if text in ["нет", "нету", "-", "0"]:
        allergies = []
    else:
        allergies = [a.strip() for a in text.split(",") if a.strip()]
    
    await state.update_data(allergies=allergies)
    await state.set_state(OnboardingStates.waiting_health_conditions)
    
    await message.answer(
        "Есть ли у тебя хронические заболевания или травмы, "
        "которые нужно учитывать?\n\n"
        "Напиши через запятую или отправь «нет»\n"
        "Например: больная спина, проблемы с коленями"
    )


@router.message(OnboardingStates.waiting_health_conditions)
async def process_health_conditions(message: Message, state: FSMContext, session: AsyncSession):
    """Обработка состояния здоровья и завершение онбординга"""
    text = message.text.strip().lower()
    
    if text in ["нет", "нету", "-", "0"]:
        conditions = []
    else:
        conditions = [c.strip() for c in text.split(",") if c.strip()]
    
    await state.update_data(health_conditions=conditions)
    
    # Получаем все данные
    data = await state.get_data()
    
    # Обновляем профиль в БД
    result = await session.execute(
        select(User).where(User.telegram_id == message.from_user.id)
    )
    user = result.scalar_one_or_none()
    
    if user and user.profile:
        profile = user.profile
        profile.name = data.get("name")
        profile.age = data.get("age")
        profile.gender = data.get("gender")
        profile.height = data.get("height")
        profile.current_weight = data.get("current_weight")
        profile.target_weight = data.get("target_weight")
        profile.primary_goal = data.get("primary_goal")
        profile.fitness_level = data.get("fitness_level")
        profile.training_days_per_week = data.get("training_days_per_week")
        profile.training_location = data.get("training_location")
        profile.work_type = data.get("work_type")
        profile.diet_type = data.get("diet_type")
        profile.allergies = data.get("allergies", [])
        profile.health_conditions = conditions
        
        # Рассчитываем метрики
        profile.calculate_metrics()
        
        # Отмечаем онбординг завершённым
        user.is_onboarded = True
        
        await session.commit()
    
    # Очищаем состояние
    await state.clear()
    
    # Формируем итоговое сообщение
    goal_names = {
        "weight_loss": "🔻 Похудение",
        "muscle_gain": "💪 Набор массы",
        "maintenance": "⚖️ Поддержание",
        "endurance": "🏃 Выносливость",
        "health": "❤️ Здоровье"
    }
    
    summary = (
        f"🎉 Отлично, {data.get('name')}! Анкета заполнена!\n\n"
        f"📋 *Твои данные:*\n"
        f"├ Возраст: {data.get('age')} лет\n"
        f"├ Рост: {data.get('height')} см\n"
        f"├ Вес: {data.get('current_weight')} кг\n"
        f"└ Цель: {goal_names.get(data.get('primary_goal', ''), '?')}\n\n"
    )
    
    if user and user.profile:
        summary += (
            f"📊 *Рассчитанные параметры:*\n"
            f"├ Калории: {user.profile.target_calories} ккал/день\n"
            f"├ Белки: {user.profile.target_protein} г\n"
            f"├ Жиры: {user.profile.target_fat} г\n"
            f"├ Углеводы: {user.profile.target_carbs} г\n"
            f"└ Вода: {user.profile.target_water} л\n\n"
        )
    
    summary += (
        "✅ Теперь я готов составить для тебя программу тренировок "
        "и план питания!\n\n"
        "Выбери, что хочешь сделать:"
    )
    
    await message.answer(
        summary,
        reply_markup=get_main_menu_keyboard(),
        parse_mode="Markdown"
    )
