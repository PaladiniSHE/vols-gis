"""
Обработчики онбординга с поддержкой навигации назад и индикатором прогресса
"""
from datetime import date
from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext

from bot.keyboards.inline import InlineKeyboards
from bot.states import OnboardingStates
from core.database import async_session
from services.user_service import UserService
from services.calculator import CalculatorService

router = Router()

# Константы шагов онбординга
ONBOARDING_STEPS = {
    "gender": {"num": 1, "total": 6, "name": "Пол"},
    "birth_year": {"num": 2, "total": 6, "name": "Год рождения"},
    "height": {"num": 3, "total": 6, "name": "Рост"},
    "weight": {"num": 4, "total": 6, "name": "Вес"},
    "goal": {"num": 5, "total": 6, "name": "Цель"},
    "activity": {"num": 6, "total": 6, "name": "Активность"},
}


def get_progress_indicator(step: str) -> str:
    """Создать индикатор прогресса онбординга"""
    info = ONBOARDING_STEPS.get(step, {"num": 1, "total": 6})
    filled = "●" * info["num"]
    empty = "○" * (info["total"] - info["num"])
    return f"[{info['num']}/{info['total']}] {filled}{empty}"


# ==================== ШАГ 1: ПОЛ ====================

@router.callback_query(OnboardingStates.waiting_for_gender, F.data.startswith("gender:"))
async def process_gender(callback: CallbackQuery, state: FSMContext):
    """Обработка выбора пола"""
    gender = callback.data.split(":")[1]
    await state.update_data(gender=gender)
    
    progress = get_progress_indicator("birth_year")
    await callback.message.edit_text(
        f"{progress}\n\n"
        "📅 *Укажи год рождения*\n\n"
        "Например: 1990\n\n"
        "_Отправь /cancel для отмены_",
        parse_mode="Markdown",
        reply_markup=InlineKeyboards.onboarding_back("gender")
    )
    await state.set_state(OnboardingStates.waiting_for_birth_year)
    await callback.answer()


@router.callback_query(F.data == "onboarding:cancel")
async def cancel_onboarding(callback: CallbackQuery, state: FSMContext):
    """Отмена онбординга"""
    await state.clear()
    await callback.message.edit_text(
        "❌ Настройка профиля отменена.\n\n"
        "Чтобы начать заново, отправь /start"
    )
    await callback.answer()


# ==================== ШАГ 2: ГОД РОЖДЕНИЯ ====================

@router.callback_query(F.data == "onboarding:back_to_gender")
async def back_to_gender(callback: CallbackQuery, state: FSMContext):
    """Возврат к выбору пола"""
    progress = get_progress_indicator("gender")
    await callback.message.edit_text(
        f"{progress}\n\n"
        "👤 *Укажи свой пол*",
        parse_mode="Markdown",
        reply_markup=InlineKeyboards.gender_select()
    )
    await state.set_state(OnboardingStates.waiting_for_gender)
    await callback.answer()


@router.message(OnboardingStates.waiting_for_birth_year)
async def process_birth_year(message: Message, state: FSMContext):
    """Обработка года рождения"""
    if message.text == "/cancel":
        await state.clear()
        await message.answer("❌ Настройка профиля отменена.\n\nЧтобы начать заново, отправь /start")
        return
    
    try:
        year = int(message.text.strip())
        current_year = date.today().year
        
        if year < 1920 or year > current_year - 10:
            await message.answer(
                "⚠️ Пожалуйста, введи корректный год рождения (например: 1990)\n\n"
                "_Нажми кнопку Назад чтобы вернуться_",
                parse_mode="Markdown",
                reply_markup=InlineKeyboards.onboarding_back("gender")
            )
            return
        
        birth_date = date(year, 1, 1)
        await state.update_data(birth_date=birth_date)
        
        progress = get_progress_indicator("height")
        await message.answer(
            f"{progress}\n\n"
            "📏 *Укажи свой рост в сантиметрах*\n\n"
            "Например: 175",
            parse_mode="Markdown",
            reply_markup=InlineKeyboards.onboarding_back("birth_year")
        )
        await state.set_state(OnboardingStates.waiting_for_height)
        
    except ValueError:
        await message.answer(
            "⚠️ Пожалуйста, введи год числом (например: 1990)",
            reply_markup=InlineKeyboards.onboarding_back("gender")
        )


# ==================== ШАГ 3: РОСТ ====================

@router.callback_query(F.data == "onboarding:back_to_birth_year")
async def back_to_birth_year(callback: CallbackQuery, state: FSMContext):
    """Возврат к году рождения"""
    progress = get_progress_indicator("birth_year")
    await callback.message.edit_text(
        f"{progress}\n\n"
        "📅 *Укажи год рождения*\n\n"
        "Например: 1990",
        parse_mode="Markdown",
        reply_markup=InlineKeyboards.onboarding_back("gender")
    )
    await state.set_state(OnboardingStates.waiting_for_birth_year)
    await callback.answer()


@router.message(OnboardingStates.waiting_for_height)
async def process_height(message: Message, state: FSMContext):
    """Обработка роста"""
    if message.text == "/cancel":
        await state.clear()
        await message.answer("❌ Настройка профиля отменена.\n\nЧтобы начать заново, отправь /start")
        return
    
    try:
        height = float(message.text.strip().replace(",", "."))
        
        if height < 100 or height > 250:
            await message.answer(
                "⚠️ Пожалуйста, введи корректный рост (100-250 см)",
                reply_markup=InlineKeyboards.onboarding_back("birth_year")
            )
            return
        
        await state.update_data(height=height)
        
        progress = get_progress_indicator("weight")
        await message.answer(
            f"{progress}\n\n"
            "⚖️ *Укажи свой текущий вес в килограммах*\n\n"
            "Например: 70.5",
            parse_mode="Markdown",
            reply_markup=InlineKeyboards.onboarding_back("height")
        )
        await state.set_state(OnboardingStates.waiting_for_weight)
        
    except ValueError:
        await message.answer(
            "⚠️ Пожалуйста, введи рост числом (например: 175)",
            reply_markup=InlineKeyboards.onboarding_back("birth_year")
        )


# ==================== ШАГ 4: ВЕС ====================

@router.callback_query(F.data == "onboarding:back_to_height")
async def back_to_height(callback: CallbackQuery, state: FSMContext):
    """Возврат к росту"""
    progress = get_progress_indicator("height")
    await callback.message.edit_text(
        f"{progress}\n\n"
        "📏 *Укажи свой рост в сантиметрах*\n\n"
        "Например: 175",
        parse_mode="Markdown",
        reply_markup=InlineKeyboards.onboarding_back("birth_year")
    )
    await state.set_state(OnboardingStates.waiting_for_height)
    await callback.answer()


@router.message(OnboardingStates.waiting_for_weight)
async def process_weight(message: Message, state: FSMContext):
    """Обработка веса"""
    if message.text == "/cancel":
        await state.clear()
        await message.answer("❌ Настройка профиля отменена.\n\nЧтобы начать заново, отправь /start")
        return
    
    try:
        weight = float(message.text.strip().replace(",", "."))
        
        if weight < 30 or weight > 300:
            await message.answer(
                "⚠️ Пожалуйста, введи корректный вес (30-300 кг)",
                reply_markup=InlineKeyboards.onboarding_back("height")
            )
            return
        
        await state.update_data(weight=weight)
        
        progress = get_progress_indicator("goal")
        await message.answer(
            f"{progress}\n\n"
            "🎯 *Какая у тебя цель?*",
            parse_mode="Markdown",
            reply_markup=InlineKeyboards.goal_select(with_back=True)
        )
        await state.set_state(OnboardingStates.waiting_for_goal)
        
    except ValueError:
        await message.answer(
            "⚠️ Пожалуйста, введи вес числом (например: 70.5)",
            reply_markup=InlineKeyboards.onboarding_back("height")
        )


# ==================== ШАГ 5: ЦЕЛЬ ====================

@router.callback_query(F.data == "onboarding:back_to_weight")
async def back_to_weight(callback: CallbackQuery, state: FSMContext):
    """Возврат к весу"""
    progress = get_progress_indicator("weight")
    await callback.message.edit_text(
        f"{progress}\n\n"
        "⚖️ *Укажи свой текущий вес в килограммах*\n\n"
        "Например: 70.5",
        parse_mode="Markdown",
        reply_markup=InlineKeyboards.onboarding_back("height")
    )
    await state.set_state(OnboardingStates.waiting_for_weight)
    await callback.answer()


@router.callback_query(OnboardingStates.waiting_for_goal, F.data.startswith("goal:"))
async def process_goal(callback: CallbackQuery, state: FSMContext):
    """Обработка выбора цели"""
    goal = callback.data.split(":")[1]
    await state.update_data(goal=goal)
    
    if goal == "lose":
        await callback.message.edit_text(
            "🎯 *Какой вес ты хочешь достичь?*\n\n"
            "Введи желаемый вес в кг:",
            parse_mode="Markdown",
            reply_markup=InlineKeyboards.onboarding_back("goal")
        )
        await state.set_state(OnboardingStates.waiting_for_goal_weight)
    elif goal == "gain":
        await callback.message.edit_text(
            "🎯 *Какой вес ты хочешь набрать?*\n\n"
            "Введи желаемый вес в кг:",
            parse_mode="Markdown",
            reply_markup=InlineKeyboards.onboarding_back("goal")
        )
        await state.set_state(OnboardingStates.waiting_for_goal_weight)
    else:
        progress = get_progress_indicator("activity")
        await callback.message.edit_text(
            f"{progress}\n\n"
            "🏃 *Какой у тебя уровень физической активности?*",
            parse_mode="Markdown",
            reply_markup=InlineKeyboards.activity_select(with_back=True)
        )
        await state.set_state(OnboardingStates.waiting_for_activity)
    
    await callback.answer()


# ==================== ШАГ 5.5: ЦЕЛЕВОЙ ВЕС (опционально) ====================

@router.callback_query(F.data == "onboarding:back_to_goal")
async def back_to_goal(callback: CallbackQuery, state: FSMContext):
    """Возврат к выбору цели"""
    progress = get_progress_indicator("goal")
    await callback.message.edit_text(
        f"{progress}\n\n"
        "🎯 *Какая у тебя цель?*",
        parse_mode="Markdown",
        reply_markup=InlineKeyboards.goal_select(with_back=True)
    )
    await state.set_state(OnboardingStates.waiting_for_goal)
    await callback.answer()


@router.message(OnboardingStates.waiting_for_goal_weight)
async def process_goal_weight(message: Message, state: FSMContext):
    """Обработка целевого веса"""
    if message.text == "/cancel":
        await state.clear()
        await message.answer("❌ Настройка профиля отменена.\n\nЧтобы начать заново, отправь /start")
        return
    
    try:
        goal_weight = float(message.text.strip().replace(",", "."))
        
        if goal_weight < 30 or goal_weight > 300:
            await message.answer(
                "⚠️ Пожалуйста, введи корректный вес (30-300 кг)",
                reply_markup=InlineKeyboards.onboarding_back("goal")
            )
            return
        
        await state.update_data(goal_weight=goal_weight)
        
        progress = get_progress_indicator("activity")
        await message.answer(
            f"{progress}\n\n"
            "🏃 *Какой у тебя уровень физической активности?*",
            parse_mode="Markdown",
            reply_markup=InlineKeyboards.activity_select(with_back=True)
        )
        await state.set_state(OnboardingStates.waiting_for_activity)
        
    except ValueError:
        await message.answer(
            "⚠️ Пожалуйста, введи вес числом (например: 65)",
            reply_markup=InlineKeyboards.onboarding_back("goal")
        )


# ==================== ШАГ 6: АКТИВНОСТЬ (ФИНАЛ) ====================

@router.callback_query(OnboardingStates.waiting_for_activity, F.data.startswith("activity:"))
async def process_activity(callback: CallbackQuery, state: FSMContext):
    """Обработка уровня активности и завершение онбординга"""
    activity = callback.data.split(":")[1]
    data = await state.get_data()
    
    async with async_session() as session:
        user_service = UserService(session)
        calculator = CalculatorService()
        
        # Обновляем профиль
        await user_service.update_user_profile(
            telegram_id=callback.from_user.id,
            height=data.get("height"),
            weight=data.get("weight"),
            birth_date=data.get("birth_date"),
            gender=data.get("gender"),
            goal=data.get("goal"),
            activity_level=activity,
            goal_weight=data.get("goal_weight")
        )
        
        # Рассчитываем и сохраняем нормы
        user = await user_service.calculate_and_save_norms(callback.from_user.id)
        
        # Расчет BMI
        bmi_data = calculator.calculate_bmi(user.weight, user.height)
        
        # Расчет изменения веса в неделю
        weekly_change = calculator.calculate_weekly_weight_change(
            user.tdee - user.daily_calories if user.tdee else 0
        )
        
        # Формируем итоговое сообщение
        text = f"""
✅ *Отлично! Твой профиль настроен!*

📊 *Твои показатели:*
├ Рост: {user.height} см
├ Вес: {user.weight} кг
├ BMI: {bmi_data['bmi']} ({bmi_data['category']}) {bmi_data['emoji']}
└ Возраст: {user.age} лет

⚡ *Расчет метаболизма:*
├ BMR (базовый): {int(user.bmr)} ккал
└ TDEE (с активностью): {int(user.tdee)} ккал

🎯 *Твой план:*
├ Калории: *{user.daily_calories}* ккал/день
├ Белки: *{int(user.daily_protein)}* г
├ Жиры: *{int(user.daily_fat)}* г
├ Углеводы: *{int(user.daily_carbs)}* г
└ Вода: *{user.daily_water}* л/день
"""
        
        if user.goal and user.goal.value != "maintain":
            direction = "похудение" if user.goal.value == "lose" else "набор"
            text += f"""
📈 *Прогноз:*
{abs(weekly_change)} кг/неделю ({direction})
"""
        
        text += """
Теперь ты можешь начать отслеживать своё питание!
Используй меню ниже 👇
"""
        
        await callback.message.edit_text(
            text,
            parse_mode="Markdown",
            reply_markup=InlineKeyboards.main_menu()
        )
    
    await state.clear()
    await callback.answer("🎉 Профиль настроен!")
