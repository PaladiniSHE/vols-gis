"""
Обработчики онбординга
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


@router.callback_query(OnboardingStates.waiting_for_gender, F.data.startswith("gender:"))
async def process_gender(callback: CallbackQuery, state: FSMContext):
    """Обработка выбора пола"""
    gender = callback.data.split(":")[1]
    await state.update_data(gender=gender)
    
    await callback.message.edit_text(
        "📅 *Укажи год рождения*\n\nНапример: 1990",
        parse_mode="Markdown"
    )
    await state.set_state(OnboardingStates.waiting_for_birth_year)
    await callback.answer()


@router.message(OnboardingStates.waiting_for_birth_year)
async def process_birth_year(message: Message, state: FSMContext):
    """Обработка года рождения"""
    try:
        year = int(message.text.strip())
        current_year = date.today().year
        
        if year < 1920 or year > current_year - 10:
            await message.answer("⚠️ Пожалуйста, введи корректный год рождения (например: 1990)")
            return
        
        birth_date = date(year, 1, 1)
        await state.update_data(birth_date=birth_date)
        
        await message.answer(
            "📏 *Укажи свой рост в сантиметрах*\n\nНапример: 175",
            parse_mode="Markdown"
        )
        await state.set_state(OnboardingStates.waiting_for_height)
        
    except ValueError:
        await message.answer("⚠️ Пожалуйста, введи год числом (например: 1990)")


@router.message(OnboardingStates.waiting_for_height)
async def process_height(message: Message, state: FSMContext):
    """Обработка роста"""
    try:
        height = float(message.text.strip().replace(",", "."))
        
        if height < 100 or height > 250:
            await message.answer("⚠️ Пожалуйста, введи корректный рост (100-250 см)")
            return
        
        await state.update_data(height=height)
        
        await message.answer(
            "⚖️ *Укажи свой текущий вес в килограммах*\n\nНапример: 70.5",
            parse_mode="Markdown"
        )
        await state.set_state(OnboardingStates.waiting_for_weight)
        
    except ValueError:
        await message.answer("⚠️ Пожалуйста, введи рост числом (например: 175)")


@router.message(OnboardingStates.waiting_for_weight)
async def process_weight(message: Message, state: FSMContext):
    """Обработка веса"""
    try:
        weight = float(message.text.strip().replace(",", "."))
        
        if weight < 30 or weight > 300:
            await message.answer("⚠️ Пожалуйста, введи корректный вес (30-300 кг)")
            return
        
        await state.update_data(weight=weight)
        
        await message.answer(
            "🎯 *Какая у тебя цель?*",
            parse_mode="Markdown",
            reply_markup=InlineKeyboards.goal_select()
        )
        await state.set_state(OnboardingStates.waiting_for_goal)
        
    except ValueError:
        await message.answer("⚠️ Пожалуйста, введи вес числом (например: 70.5)")


@router.callback_query(OnboardingStates.waiting_for_goal, F.data.startswith("goal:"))
async def process_goal(callback: CallbackQuery, state: FSMContext):
    """Обработка выбора цели"""
    goal = callback.data.split(":")[1]
    await state.update_data(goal=goal)
    
    if goal == "lose":
        await callback.message.edit_text(
            "🎯 *Какой вес ты хочешь достичь?*\n\nВведи желаемый вес в кг:",
            parse_mode="Markdown"
        )
        await state.set_state(OnboardingStates.waiting_for_goal_weight)
    elif goal == "gain":
        await callback.message.edit_text(
            "🎯 *Какой вес ты хочешь набрать?*\n\nВведи желаемый вес в кг:",
            parse_mode="Markdown"
        )
        await state.set_state(OnboardingStates.waiting_for_goal_weight)
    else:
        await callback.message.edit_text(
            "🏃 *Какой у тебя уровень физической активности?*",
            parse_mode="Markdown",
            reply_markup=InlineKeyboards.activity_select()
        )
        await state.set_state(OnboardingStates.waiting_for_activity)
    
    await callback.answer()


@router.message(OnboardingStates.waiting_for_goal_weight)
async def process_goal_weight(message: Message, state: FSMContext):
    """Обработка целевого веса"""
    try:
        goal_weight = float(message.text.strip().replace(",", "."))
        
        if goal_weight < 30 or goal_weight > 300:
            await message.answer("⚠️ Пожалуйста, введи корректный вес (30-300 кг)")
            return
        
        await state.update_data(goal_weight=goal_weight)
        
        await message.answer(
            "🏃 *Какой у тебя уровень физической активности?*",
            parse_mode="Markdown",
            reply_markup=InlineKeyboards.activity_select()
        )
        await state.set_state(OnboardingStates.waiting_for_activity)
        
    except ValueError:
        await message.answer("⚠️ Пожалуйста, введи вес числом (например: 65)")


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
