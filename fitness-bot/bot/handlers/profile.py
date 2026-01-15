"""
Обработчики для профиля пользователя
"""
from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext

from bot.keyboards.inline import InlineKeyboards
from bot.states import ProfileStates, OnboardingStates
from bot.config import Constants
from core.database import async_session
from services.user_service import UserService
from services.calculator import CalculatorService

router = Router()


@router.message(Command("profile"))
async def cmd_profile(message: Message, state: FSMContext):
    """Команда /profile"""
    await state.clear()
    await show_profile(message)


@router.callback_query(F.data == "menu:profile")
async def callback_profile_menu(callback: CallbackQuery, state: FSMContext):
    """Меню профиля"""
    await state.clear()
    
    async with async_session() as session:
        user_service = UserService(session)
        calculator = CalculatorService()
        
        user = await user_service.get_user_by_telegram_id(callback.from_user.id)
        if not user:
            await callback.answer("Сначала настройте профиль с помощью /start")
            return
        
        # BMI
        bmi_data = None
        if user.height and user.weight:
            bmi_data = calculator.calculate_bmi(user.weight, user.height)
        
        # Названия целей и активности
        goal_names = {
            "lose": "🔥 Похудение",
            "maintain": "⚖️ Поддержание",
            "gain": "💪 Набор массы"
        }
        
        activity_names = {
            "minimal": "🛋️ Минимальная",
            "low": "🚶 Низкая",
            "medium": "🏃 Средняя",
            "high": "🔥 Высокая",
            "extreme": "⚡ Очень высокая"
        }
        
        goal_name = goal_names.get(user.goal.value if user.goal else None, "—")
        activity_name = activity_names.get(user.activity_level.value if user.activity_level else None, "—")
        
        text = f"""
👤 *Твой профиль*

📊 *Физические данные:*
├ Рост: *{user.height or '—'}* см
├ Вес: *{user.weight or '—'}* кг
├ Возраст: *{user.age or '—'}* лет
├ Пол: {'👨 Мужской' if user.gender and user.gender.value == 'male' else '👩 Женский' if user.gender else '—'}
"""
        
        if bmi_data:
            text += f"└ BMI: *{bmi_data['bmi']}* ({bmi_data['category']}) {bmi_data['emoji']}\n"
        
        text += f"""
🎯 *Цели и активность:*
├ Цель: {goal_name}
├ Целевой вес: *{user.goal_weight or '—'}* кг
└ Активность: {activity_name}

📈 *Дневные нормы:*
├ 🔥 Калории: *{user.daily_calories or '—'}* ккал
├ 🥩 Белки: *{int(user.daily_protein) if user.daily_protein else '—'}* г
├ 🧈 Жиры: *{int(user.daily_fat) if user.daily_fat else '—'}* г
├ 🍞 Углеводы: *{int(user.daily_carbs) if user.daily_carbs else '—'}* г
└ 💧 Вода: *{user.daily_water or '—'}* л

⚡ *Метаболизм:*
├ BMR: {int(user.bmr) if user.bmr else '—'} ккал
└ TDEE: {int(user.tdee) if user.tdee else '—'} ккал
"""
        
        await callback.message.edit_text(
            text,
            parse_mode="Markdown",
            reply_markup=InlineKeyboards.profile_menu()
        )
    
    await callback.answer()


async def show_profile(message: Message):
    """Показать профиль"""
    async with async_session() as session:
        user_service = UserService(session)
        calculator = CalculatorService()
        
        user = await user_service.get_user_by_telegram_id(message.from_user.id)
        if not user:
            await message.answer("Сначала настройте профиль с помощью /start")
            return
        
        bmi_data = None
        if user.height and user.weight:
            bmi_data = calculator.calculate_bmi(user.weight, user.height)
        
        goal_names = {
            "lose": "🔥 Похудение",
            "maintain": "⚖️ Поддержание",
            "gain": "💪 Набор массы"
        }
        
        goal_name = goal_names.get(user.goal.value if user.goal else None, "—")
        
        text = f"""
👤 *Твой профиль*

📊 *Физические данные:*
├ Рост: *{user.height or '—'}* см
├ Вес: *{user.weight or '—'}* кг
├ Возраст: *{user.age or '—'}* лет
"""
        
        if bmi_data:
            text += f"└ BMI: *{bmi_data['bmi']}* ({bmi_data['category']}) {bmi_data['emoji']}\n"
        
        text += f"""
🎯 *Цель:* {goal_name}

📈 *Дневные нормы:*
├ 🔥 Калории: *{user.daily_calories or '—'}* ккал
├ 🥩 Белки: *{int(user.daily_protein) if user.daily_protein else '—'}* г
├ 🧈 Жиры: *{int(user.daily_fat) if user.daily_fat else '—'}* г
└ 🍞 Углеводы: *{int(user.daily_carbs) if user.daily_carbs else '—'}* г
"""
        
        await message.answer(
            text,
            parse_mode="Markdown",
            reply_markup=InlineKeyboards.profile_menu()
        )


@router.callback_query(F.data == "profile:goal")
async def callback_change_goal(callback: CallbackQuery, state: FSMContext):
    """Изменить цель"""
    await callback.message.edit_text(
        "🎯 *Выбери новую цель:*",
        parse_mode="Markdown",
        reply_markup=InlineKeyboards.goal_select()
    )
    await state.set_state(OnboardingStates.waiting_for_goal)
    await callback.answer()


@router.callback_query(F.data == "profile:activity")
async def callback_change_activity(callback: CallbackQuery, state: FSMContext):
    """Изменить уровень активности"""
    await callback.message.edit_text(
        "🏃 *Выбери уровень активности:*",
        parse_mode="Markdown",
        reply_markup=InlineKeyboards.activity_select()
    )
    await state.set_state(OnboardingStates.waiting_for_activity)
    await callback.answer()


@router.callback_query(F.data == "profile:recalc")
async def callback_recalculate(callback: CallbackQuery):
    """Пересчитать нормы"""
    async with async_session() as session:
        user_service = UserService(session)
        
        try:
            user = await user_service.calculate_and_save_norms(callback.from_user.id)
            
            text = f"""
✅ *Нормы пересчитаны!*

📈 *Новые дневные нормы:*
├ 🔥 Калории: *{user.daily_calories}* ккал
├ 🥩 Белки: *{int(user.daily_protein)}* г
├ 🧈 Жиры: *{int(user.daily_fat)}* г
├ 🍞 Углеводы: *{int(user.daily_carbs)}* г
└ 💧 Вода: *{user.daily_water}* л

⚡ Метаболизм:
├ BMR: {int(user.bmr)} ккал
└ TDEE: {int(user.tdee)} ккал
"""
            
            await callback.message.edit_text(
                text,
                parse_mode="Markdown",
                reply_markup=InlineKeyboards.profile_menu()
            )
            
        except ValueError as e:
            await callback.message.edit_text(
                "⚠️ Для расчета нужны все данные профиля (рост, вес, возраст, пол).\n\n"
                "Заполните профиль с помощью /start",
                reply_markup=InlineKeyboards.back_to_menu()
            )
    
    await callback.answer()


@router.callback_query(F.data == "profile:edit")
async def callback_edit_profile(callback: CallbackQuery, state: FSMContext):
    """Редактировать данные профиля"""
    text = """
✏️ *Редактирование профиля*

Введи новый *рост* в сантиметрах:

(или отправь /cancel для отмены)
"""
    await callback.message.edit_text(text, parse_mode="Markdown")
    await state.set_state(ProfileStates.editing_height)
    await callback.answer()


@router.message(ProfileStates.editing_height)
async def process_edit_height(message: Message, state: FSMContext):
    """Обработка нового роста"""
    if message.text == "/cancel":
        await state.clear()
        await message.answer("❌ Редактирование отменено", reply_markup=InlineKeyboards.back_to_menu())
        return
    
    try:
        height = float(message.text.strip().replace(",", "."))
        
        if height < 100 or height > 250:
            await message.answer("⚠️ Введите корректный рост (100-250 см)")
            return
        
        await state.update_data(new_height=height)
        
        await message.answer(
            "✏️ Теперь введи *текущий вес* в килограммах:\n\n(или отправь /cancel для отмены)",
            parse_mode="Markdown"
        )
        await state.set_state(ProfileStates.editing_weight)
        
    except ValueError:
        await message.answer("⚠️ Введите рост числом (например: 175)")


@router.message(ProfileStates.editing_weight)
async def process_edit_weight(message: Message, state: FSMContext):
    """Обработка нового веса"""
    if message.text == "/cancel":
        await state.clear()
        await message.answer("❌ Редактирование отменено", reply_markup=InlineKeyboards.back_to_menu())
        return
    
    try:
        weight = float(message.text.strip().replace(",", "."))
        
        if weight < 30 or weight > 300:
            await message.answer("⚠️ Введите корректный вес (30-300 кг)")
            return
        
        data = await state.get_data()
        
        async with async_session() as session:
            user_service = UserService(session)
            
            # Обновляем профиль
            await user_service.update_user_profile(
                telegram_id=message.from_user.id,
                height=data.get("new_height"),
                weight=weight
            )
            
            # Пересчитываем нормы
            user = await user_service.calculate_and_save_norms(message.from_user.id)
            
            text = f"""
✅ *Профиль обновлен!*

📊 Новые данные:
├ Рост: *{user.height}* см
├ Вес: *{user.weight}* кг

📈 Пересчитанные нормы:
├ 🔥 Калории: *{user.daily_calories}* ккал
├ 🥩 Белки: *{int(user.daily_protein)}* г
├ 🧈 Жиры: *{int(user.daily_fat)}* г
└ 🍞 Углеводы: *{int(user.daily_carbs)}* г
"""
            
            await message.answer(
                text,
                parse_mode="Markdown",
                reply_markup=InlineKeyboards.back_to_menu()
            )
        
        await state.clear()
        
    except ValueError:
        await message.answer("⚠️ Введите вес числом (например: 70.5)")


@router.callback_query(F.data == "menu:settings")
async def callback_settings(callback: CallbackQuery):
    """Настройки"""
    async with async_session() as session:
        user_service = UserService(session)
        user = await user_service.get_user_by_telegram_id(callback.from_user.id)
        
        notif_status = "✅ Включены" if user.notifications_enabled else "❌ Выключены"
        
        text = f"""
⚙️ *Настройки*

🔔 Уведомления: {notif_status}
🌍 Часовой пояс: {user.timezone}

Функции настроек в разработке...
"""
        
        await callback.message.edit_text(
            text,
            parse_mode="Markdown",
            reply_markup=InlineKeyboards.back_to_menu()
        )
    
    await callback.answer()
