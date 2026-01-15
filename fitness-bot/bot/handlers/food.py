"""
Обработчики для дневника питания
"""
from datetime import date
from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext

from bot.keyboards.inline import InlineKeyboards
from bot.states import FoodStates
from bot.config import Constants
from core.database import async_session
from services.user_service import UserService
from services.food_service import FoodService
from services.stats_service import StatsService

router = Router()


def create_progress_bar(current: float, goal: float, length: int = 12) -> str:
    """Создать прогресс-бар"""
    if goal <= 0:
        return "░" * length
    
    percent = min(current / goal, 1.5)
    filled = int(percent * length)
    
    if percent > 1:
        return "▓" * length + f" ⚠️"
    
    return "▓" * filled + "░" * (length - filled)


@router.message(Command("food"))
async def cmd_food(message: Message, state: FSMContext):
    """Команда /food"""
    await state.clear()
    await show_food_menu(message)


@router.callback_query(F.data == "menu:food")
async def callback_food_menu(callback: CallbackQuery, state: FSMContext):
    """Меню питания"""
    await state.clear()
    
    async with async_session() as session:
        user_service = UserService(session)
        stats_service = StatsService(session)
        
        user = await user_service.get_user_by_telegram_id(callback.from_user.id)
        if not user:
            await callback.answer("Сначала настройте профиль с помощью /start")
            return
        
        today = date.today()
        daily = await stats_service.get_daily_summary(user.id, today)
        
        cal_bar = create_progress_bar(daily["calories"], user.daily_calories or 2000)
        
        text = f"""
🍽️ *Дневник питания*

📅 Сегодня: {today.strftime('%d.%m.%Y')}

🔥 Калории: {int(daily["calories"])} / {user.daily_calories or '—'} ккал
{cal_bar}

📊 Макронутриенты:
├ 🥩 Белки: {daily["protein"]:.0f}г / {int(user.daily_protein or 0)}г
├ 🧈 Жиры: {daily["fat"]:.0f}г / {int(user.daily_fat or 0)}г
└ 🍞 Углеводы: {daily["carbs"]:.0f}г / {int(user.daily_carbs or 0)}г

Выбери прием пищи:
"""
        
        await callback.message.edit_text(
            text,
            parse_mode="Markdown",
            reply_markup=InlineKeyboards.meal_select()
        )
    
    await callback.answer()


async def show_food_menu(message: Message):
    """Показать меню питания"""
    async with async_session() as session:
        user_service = UserService(session)
        stats_service = StatsService(session)
        
        user = await user_service.get_user_by_telegram_id(message.from_user.id)
        if not user:
            await message.answer("Сначала настройте профиль с помощью /start")
            return
        
        today = date.today()
        daily = await stats_service.get_daily_summary(user.id, today)
        
        cal_bar = create_progress_bar(daily["calories"], user.daily_calories or 2000)
        
        text = f"""
🍽️ *Дневник питания*

📅 Сегодня: {today.strftime('%d.%m.%Y')}

🔥 Калории: {int(daily["calories"])} / {user.daily_calories or '—'} ккал
{cal_bar}

📊 Макронутриенты:
├ 🥩 Белки: {daily["protein"]:.0f}г / {int(user.daily_protein or 0)}г
├ 🧈 Жиры: {daily["fat"]:.0f}г / {int(user.daily_fat or 0)}г
└ 🍞 Углеводы: {daily["carbs"]:.0f}г / {int(user.daily_carbs or 0)}г

Выбери прием пищи:
"""
        
        await message.answer(
            text,
            parse_mode="Markdown",
            reply_markup=InlineKeyboards.meal_select()
        )


@router.callback_query(F.data.startswith("meal:"))
async def callback_select_meal(callback: CallbackQuery, state: FSMContext):
    """Выбор приема пищи"""
    meal_type = callback.data.split(":")[1]
    meal_data = Constants.MEAL_TYPES.get(meal_type, {})
    
    await state.update_data(meal_type=meal_type)
    
    async with async_session() as session:
        food_service = FoodService(session)
        user_service = UserService(session)
        
        user = await user_service.get_user_by_telegram_id(callback.from_user.id)
        if not user:
            await callback.answer("Ошибка")
            return
        
        # Получаем записи за этот прием пищи
        today = date.today()
        meal_totals = await food_service.get_meal_totals(user.id, today, meal_type)
        
        text = f"""
{meal_data.get('emoji', '🍽️')} *{meal_data.get('name', 'Прием пищи')}*

📊 Уже записано:
├ 🔥 Калории: {int(meal_totals['calories'])} ккал
├ 🥩 Белки: {meal_totals['protein']:.0f}г
├ 🧈 Жиры: {meal_totals['fat']:.0f}г
└ 🍞 Углеводы: {meal_totals['carbs']:.0f}г

Как добавить продукт?
"""
        
        await callback.message.edit_text(
            text,
            parse_mode="Markdown",
            reply_markup=InlineKeyboards.food_add_method()
        )
    
    await callback.answer()


@router.callback_query(F.data == "food:search")
async def callback_food_search(callback: CallbackQuery, state: FSMContext):
    """Начать поиск продукта"""
    await callback.message.edit_text(
        "🔍 *Поиск продукта*\n\nВведи название продукта:",
        parse_mode="Markdown"
    )
    await state.set_state(FoodStates.searching_food)
    await callback.answer()


@router.message(FoodStates.searching_food)
async def process_food_search(message: Message, state: FSMContext):
    """Обработка поиска продукта"""
    query = message.text.strip()
    
    if len(query) < 2:
        await message.answer("⚠️ Введите минимум 2 символа для поиска")
        return
    
    async with async_session() as session:
        food_service = FoodService(session)
        foods = await food_service.search_foods(query, limit=8)
        
        if foods:
            await message.answer(
                f"🔍 Результаты поиска по запросу «{query}»:",
                reply_markup=InlineKeyboards.food_search_results(foods)
            )
        else:
            text = f"""
❌ По запросу «{query}» ничего не найдено.

Попробуй:
• Изменить запрос
• Добавить продукт вручную
"""
            await message.answer(
                text,
                reply_markup=InlineKeyboards.food_add_method()
            )


@router.callback_query(F.data.startswith("select_food:"))
async def callback_select_food(callback: CallbackQuery, state: FSMContext):
    """Выбор продукта из результатов поиска"""
    food_id = int(callback.data.split(":")[1])
    
    async with async_session() as session:
        food_service = FoodService(session)
        food = await food_service.get_food_by_id(food_id)
        
        if not food:
            await callback.answer("Продукт не найден")
            return
        
        await state.update_data(food_id=food_id, food_name=food.name)
        
        text = f"""
🍽️ *{food.name}*

📊 На 100г:
├ 🔥 Калории: {int(food.calories_100g)} ккал
├ 🥩 Белки: {food.protein_100g:.1f}г
├ 🧈 Жиры: {food.fat_100g:.1f}г
└ 🍞 Углеводы: {food.carbs_100g:.1f}г

Выбери размер порции:
"""
        
        await callback.message.edit_text(
            text,
            parse_mode="Markdown",
            reply_markup=InlineKeyboards.portion_select()
        )
    
    await callback.answer()


@router.callback_query(F.data.startswith("portion:"))
async def callback_select_portion(callback: CallbackQuery, state: FSMContext):
    """Выбор размера порции"""
    portion_str = callback.data.split(":")[1]
    
    if portion_str == "custom":
        await callback.message.edit_text(
            "✏️ *Введи размер порции в граммах:*",
            parse_mode="Markdown"
        )
        await state.set_state(FoodStates.entering_portion)
        await callback.answer()
        return
    
    portion = int(portion_str)
    await save_food_entry(callback, state, portion)


@router.message(FoodStates.entering_portion)
async def process_custom_portion(message: Message, state: FSMContext):
    """Обработка произвольной порции"""
    try:
        portion = float(message.text.strip().replace(",", "."))
        
        if portion <= 0 or portion > 5000:
            await message.answer("⚠️ Введите корректный размер порции (1-5000г)")
            return
        
        # Создаем фейковый callback для переиспользования логики
        data = await state.get_data()
        
        async with async_session() as session:
            food_service = FoodService(session)
            user_service = UserService(session)
            
            user = await user_service.get_user_by_telegram_id(message.from_user.id)
            food_id = data.get("food_id")
            meal_type = data.get("meal_type", "snack")
            
            # Добавляем запись
            entry = await food_service.add_food_entry(
                user_id=user.id,
                meal_type=meal_type,
                portion_size=portion,
                food_id=food_id
            )
            
            # Обновляем серию
            await user_service.update_streak(message.from_user.id)
            await user_service.add_xp(message.from_user.id, 10)
            
            meal_name = Constants.MEAL_TYPES.get(meal_type, {}).get("name", "Прием пищи")
            
            text = f"""
✅ *Добавлено в {meal_name}!*

🍽️ {data.get('food_name', 'Продукт')}
├ Порция: {portion}г
├ 🔥 Калории: {int(entry.calories)} ккал
├ 🥩 Белки: {entry.protein:.1f}г
├ 🧈 Жиры: {entry.fat:.1f}г
└ 🍞 Углеводы: {entry.carbs:.1f}г

+10 XP ⭐
"""
            
            await message.answer(
                text,
                parse_mode="Markdown",
                reply_markup=InlineKeyboards.back_to_menu()
            )
        
        await state.clear()
        
    except ValueError:
        await message.answer("⚠️ Введите размер порции числом (например: 150)")


async def save_food_entry(callback: CallbackQuery, state: FSMContext, portion: int):
    """Сохранение записи о еде"""
    data = await state.get_data()
    
    async with async_session() as session:
        food_service = FoodService(session)
        user_service = UserService(session)
        
        user = await user_service.get_user_by_telegram_id(callback.from_user.id)
        food_id = data.get("food_id")
        meal_type = data.get("meal_type", "snack")
        
        # Добавляем запись
        entry = await food_service.add_food_entry(
            user_id=user.id,
            meal_type=meal_type,
            portion_size=portion,
            food_id=food_id
        )
        
        # Обновляем серию и XP
        await user_service.update_streak(callback.from_user.id)
        await user_service.add_xp(callback.from_user.id, 10)
        
        meal_name = Constants.MEAL_TYPES.get(meal_type, {}).get("name", "Прием пищи")
        
        text = f"""
✅ *Добавлено в {meal_name}!*

🍽️ {data.get('food_name', 'Продукт')}
├ Порция: {portion}г
├ 🔥 Калории: {int(entry.calories)} ккал
├ 🥩 Белки: {entry.protein:.1f}г
├ 🧈 Жиры: {entry.fat:.1f}г
└ 🍞 Углеводы: {entry.carbs:.1f}г

+10 XP ⭐
"""
        
        await callback.message.edit_text(
            text,
            parse_mode="Markdown",
            reply_markup=InlineKeyboards.back_to_menu()
        )
    
    await state.clear()
    await callback.answer("✅ Добавлено!")


@router.callback_query(F.data == "food:manual")
async def callback_manual_food(callback: CallbackQuery, state: FSMContext):
    """Ручной ввод продукта"""
    await callback.message.edit_text(
        "✏️ *Добавление продукта вручную*\n\nВведи название продукта:",
        parse_mode="Markdown"
    )
    await state.set_state(FoodStates.entering_custom_food)
    await callback.answer()


@router.message(FoodStates.entering_custom_food)
async def process_custom_food_name(message: Message, state: FSMContext):
    """Обработка названия продукта"""
    await state.update_data(custom_food_name=message.text.strip())
    
    await message.answer(
        "🔥 *Введи калорийность на 100г:*\n\nНапример: 250",
        parse_mode="Markdown"
    )
    await state.set_state(FoodStates.entering_custom_calories)


@router.message(FoodStates.entering_custom_calories)
async def process_custom_calories(message: Message, state: FSMContext):
    """Обработка калорийности"""
    try:
        calories = float(message.text.strip().replace(",", "."))
        
        if calories < 0 or calories > 1000:
            await message.answer("⚠️ Введите корректную калорийность (0-1000 ккал/100г)")
            return
        
        await state.update_data(custom_calories=calories)
        
        await message.answer(
            "🥩 *Введи количество белков на 100г:*\n\nНапример: 25",
            parse_mode="Markdown"
        )
        await state.set_state(FoodStates.entering_custom_protein)
        
    except ValueError:
        await message.answer("⚠️ Введите число (например: 250)")


@router.message(FoodStates.entering_custom_protein)
async def process_custom_protein(message: Message, state: FSMContext):
    """Обработка белков"""
    try:
        protein = float(message.text.strip().replace(",", "."))
        await state.update_data(custom_protein=protein)
        
        await message.answer(
            "🧈 *Введи количество жиров на 100г:*\n\nНапример: 10",
            parse_mode="Markdown"
        )
        await state.set_state(FoodStates.entering_custom_fat)
        
    except ValueError:
        await message.answer("⚠️ Введите число (например: 25)")


@router.message(FoodStates.entering_custom_fat)
async def process_custom_fat(message: Message, state: FSMContext):
    """Обработка жиров"""
    try:
        fat = float(message.text.strip().replace(",", "."))
        await state.update_data(custom_fat=fat)
        
        await message.answer(
            "🍞 *Введи количество углеводов на 100г:*\n\nНапример: 30",
            parse_mode="Markdown"
        )
        await state.set_state(FoodStates.entering_custom_carbs)
        
    except ValueError:
        await message.answer("⚠️ Введите число (например: 10)")


@router.message(FoodStates.entering_custom_carbs)
async def process_custom_carbs(message: Message, state: FSMContext):
    """Обработка углеводов и сохранение продукта"""
    try:
        carbs = float(message.text.strip().replace(",", "."))
        data = await state.get_data()
        
        async with async_session() as session:
            food_service = FoodService(session)
            user_service = UserService(session)
            
            user = await user_service.get_user_by_telegram_id(message.from_user.id)
            
            # Создаем продукт
            food = await food_service.create_food(
                name=data.get("custom_food_name"),
                calories_100g=data.get("custom_calories"),
                protein_100g=data.get("custom_protein"),
                fat_100g=data.get("custom_fat"),
                carbs_100g=carbs,
                created_by_user_id=user.id
            )
            
            await state.update_data(food_id=food.id, food_name=food.name)
            
            text = f"""
✅ *Продукт создан!*

🍽️ {food.name}

📊 На 100г:
├ 🔥 Калории: {int(food.calories_100g)} ккал
├ 🥩 Белки: {food.protein_100g:.1f}г
├ 🧈 Жиры: {food.fat_100g:.1f}г
└ 🍞 Углеводы: {food.carbs_100g:.1f}г

Теперь выбери размер порции:
"""
            
            await message.answer(
                text,
                parse_mode="Markdown",
                reply_markup=InlineKeyboards.portion_select()
            )
        
    except ValueError:
        await message.answer("⚠️ Введите число (например: 30)")


@router.callback_query(F.data == "food:recent")
async def callback_recent_foods(callback: CallbackQuery, state: FSMContext):
    """Показать недавние продукты"""
    async with async_session() as session:
        food_service = FoodService(session)
        user_service = UserService(session)
        
        user = await user_service.get_user_by_telegram_id(callback.from_user.id)
        foods = await food_service.get_recent_foods(user.id, limit=8)
        
        if foods:
            await callback.message.edit_text(
                "🕐 *Недавние продукты:*",
                parse_mode="Markdown",
                reply_markup=InlineKeyboards.food_search_results(foods)
            )
        else:
            await callback.message.edit_text(
                "📭 У вас пока нет записей о еде.\n\nДобавьте первый продукт!",
                reply_markup=InlineKeyboards.food_add_method()
            )
    
    await callback.answer()


@router.callback_query(F.data == "food:daily_stats")
async def callback_daily_food_stats(callback: CallbackQuery):
    """Статистика питания за день"""
    async with async_session() as session:
        user_service = UserService(session)
        food_service = FoodService(session)
        
        user = await user_service.get_user_by_telegram_id(callback.from_user.id)
        today = date.today()
        
        # Получаем записи по каждому приему пищи
        text = f"📊 *Питание за {today.strftime('%d.%m.%Y')}*\n\n"
        
        total_cal = 0
        total_p = 0
        total_f = 0
        total_c = 0
        
        for meal_id, meal_data in Constants.MEAL_TYPES.items():
            meal_totals = await food_service.get_meal_totals(user.id, today, meal_id)
            entries = await food_service.get_entries_by_meal(user.id, today, meal_id)
            
            if meal_totals["calories"] > 0:
                text += f"{meal_data['emoji']} *{meal_data['name']}*: {int(meal_totals['calories'])} ккал\n"
                
                for entry in entries:
                    food_name = entry.food.name if entry.food else entry.custom_food_name or "Продукт"
                    text += f"   • {food_name} ({int(entry.portion_size)}г) - {int(entry.calories)} ккал\n"
                
                text += "\n"
                
                total_cal += meal_totals["calories"]
                total_p += meal_totals["protein"]
                total_f += meal_totals["fat"]
                total_c += meal_totals["carbs"]
        
        text += f"""
━━━━━━━━━━━━━━━
📈 *Итого за день:*
├ 🔥 Калории: {int(total_cal)} / {user.daily_calories or '—'} ккал
├ 🥩 Белки: {total_p:.0f}г / {int(user.daily_protein or 0)}г
├ 🧈 Жиры: {total_f:.0f}г / {int(user.daily_fat or 0)}г
└ 🍞 Углеводы: {total_c:.0f}г / {int(user.daily_carbs or 0)}г
"""
        
        await callback.message.edit_text(
            text,
            parse_mode="Markdown",
            reply_markup=InlineKeyboards.back_to_menu()
        )
    
    await callback.answer()
