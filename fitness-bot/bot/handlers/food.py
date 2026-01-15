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
from bot.utils import create_progress_bar
from core.database import async_session
from services.user_service import UserService
from services.food_service import FoodService
from services.stats_service import StatsService

router = Router()


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
        
        if protein < 0 or protein > 100:
            await message.answer("⚠️ Введите корректное значение белков (0-100 г/100г)")
            return
        
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
        
        if fat < 0 or fat > 100:
            await message.answer("⚠️ Введите корректное значение жиров (0-100 г/100г)")
            return
        
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
        
        if carbs < 0 or carbs > 100:
            await message.answer("⚠️ Введите корректное значение углеводов (0-100 г/100г)")
            return
        
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


# ===================== УДАЛЕНИЕ ЗАПИСЕЙ =====================

@router.callback_query(F.data.startswith("food:delete:"))
async def callback_delete_food_entry(callback: CallbackQuery):
    """Запрос на удаление записи о еде"""
    entry_id = int(callback.data.split(":")[2])
    
    await callback.message.edit_text(
        "🗑️ *Удалить эту запись?*\n\nДействие нельзя отменить.",
        parse_mode="Markdown",
        reply_markup=InlineKeyboards.confirm_delete(entry_id)
    )
    await callback.answer()


@router.callback_query(F.data.startswith("food:confirm_delete:"))
async def callback_confirm_delete_food(callback: CallbackQuery):
    """Подтверждение удаления записи"""
    entry_id = int(callback.data.split(":")[2])
    
    async with async_session() as session:
        food_service = FoodService(session)
        user_service = UserService(session)
        
        user = await user_service.get_user_by_telegram_id(callback.from_user.id)
        
        deleted = await food_service.delete_food_entry(entry_id, user.id)
        
        if deleted:
            await callback.message.edit_text(
                "✅ Запись удалена!",
                reply_markup=InlineKeyboards.back_to_menu()
            )
            await callback.answer("Удалено!")
        else:
            await callback.message.edit_text(
                "❌ Ошибка при удалении",
                reply_markup=InlineKeyboards.back_to_menu()
            )
            await callback.answer("Ошибка")


# ===================== ИЗБРАННОЕ =====================

@router.callback_query(F.data == "food:favorites")
async def callback_favorites(callback: CallbackQuery, state: FSMContext):
    """Показать избранные продукты"""
    from services.favorites_service import FavoritesService
    
    async with async_session() as session:
        user_service = UserService(session)
        favorites_service = FavoritesService(session)
        
        user = await user_service.get_user_by_telegram_id(callback.from_user.id)
        favorites = await favorites_service.get_user_favorites(user.id, limit=10)
        
        if favorites:
            await callback.message.edit_text(
                "⭐ *Избранные продукты:*",
                parse_mode="Markdown",
                reply_markup=InlineKeyboards.food_search_results(favorites)
            )
        else:
            await callback.message.edit_text(
                "📭 У вас пока нет избранных продуктов.\n\n"
                "Добавляйте продукты в избранное для быстрого доступа!",
                reply_markup=InlineKeyboards.food_add_method()
            )
    
    await callback.answer()


@router.callback_query(F.data.startswith("food:favorite:"))
async def callback_add_to_favorites(callback: CallbackQuery):
    """Добавить продукт в избранное"""
    from services.favorites_service import FavoritesService
    
    food_id = int(callback.data.split(":")[2])
    
    async with async_session() as session:
        user_service = UserService(session)
        favorites_service = FavoritesService(session)
        
        user = await user_service.get_user_by_telegram_id(callback.from_user.id)
        await favorites_service.add_to_favorites(user.id, food_id)
    
    await callback.answer("⭐ Добавлено в избранное!")


@router.callback_query(F.data.startswith("food:unfavorite:"))
async def callback_remove_from_favorites(callback: CallbackQuery):
    """Убрать продукт из избранного"""
    from services.favorites_service import FavoritesService
    
    food_id = int(callback.data.split(":")[2])
    
    async with async_session() as session:
        user_service = UserService(session)
        favorites_service = FavoritesService(session)
        
        user = await user_service.get_user_by_telegram_id(callback.from_user.id)
        await favorites_service.remove_from_favorites(user.id, food_id)
    
    await callback.answer("💔 Убрано из избранного")


# ===================== OPEN FOOD FACTS =====================

@router.callback_query(F.data == "food:search_off")
async def callback_search_off(callback: CallbackQuery, state: FSMContext):
    """Начать поиск в Open Food Facts"""
    await callback.message.edit_text(
        "🌐 *Поиск в Open Food Facts*\n\n"
        "Введи название продукта на русском или английском:\n\n"
        "_Open Food Facts содержит миллионы продуктов со всего мира_",
        parse_mode="Markdown"
    )
    await state.set_state(FoodStates.searching_food)
    await state.update_data(search_mode="off")
    await callback.answer()


@router.message(FoodStates.searching_food)
async def process_food_search(message: Message, state: FSMContext):
    """Обработка поиска продукта"""
    query = message.text.strip()
    
    if len(query) < 2:
        await message.answer("⚠️ Введите минимум 2 символа для поиска")
        return
    
    data = await state.get_data()
    search_mode = data.get("search_mode", "local")
    
    if search_mode == "off":
        # Поиск в Open Food Facts
        from external.openfoodfacts import off_client
        import asyncio
        import aiohttp
        
        await message.answer("🔍 Ищу в Open Food Facts...")
        
        try:
            products = await off_client.search_products(query, limit=8)
            
            if not products:
                # Попробуем глобальный поиск
                products = await off_client.search_products_global(query, limit=8)
            
            if products:
                # Сохраняем результаты в состояние
                await state.update_data(off_products=products)
                
                await message.answer(
                    f"🌐 Найдено {len(products)} продуктов в Open Food Facts:",
                    reply_markup=InlineKeyboards.off_search_results(products)
                )
            else:
                await message.answer(
                    f"❌ По запросу «{query}» ничего не найдено в Open Food Facts.\n\n"
                    "Попробуйте:\n"
                    "• Изменить запрос\n"
                    "• Поискать в локальной базе\n"
                    "• Добавить продукт вручную",
                    reply_markup=InlineKeyboards.food_add_method()
                )
        
        except asyncio.TimeoutError:
            await message.answer(
                "⏳ Превышено время ожидания ответа от Open Food Facts.\n\n"
                "Попробуйте:\n"
                "• Повторить поиск позже\n"
                "• Поискать в локальной базе\n"
                "• Добавить продукт вручную",
                reply_markup=InlineKeyboards.food_add_method()
            )
        except aiohttp.ClientError:
            await message.answer(
                "🌐 Ошибка подключения к Open Food Facts.\n\n"
                "Проверьте интернет-соединение или попробуйте:\n"
                "• Поискать в локальной базе\n"
                "• Добавить продукт вручную",
                reply_markup=InlineKeyboards.food_add_method()
            )
        except Exception as e:
            import logging
            logging.getLogger(__name__).error(f"OFF search error: {e}")
            await message.answer(
                "❌ Произошла ошибка при поиске.\n\n"
                "Попробуйте:\n"
                "• Поискать в локальной базе\n"
                "• Добавить продукт вручную",
                reply_markup=InlineKeyboards.food_add_method()
            )
    else:
        # Локальный поиск с пагинацией
        async with async_session() as session:
            food_service = FoodService(session)
            page_size = 8
            foods = await food_service.search_foods(query, limit=page_size, offset=0)
            total_count = await food_service.count_search_results(query)
            
            if foods:
                # Сохраняем запрос для пагинации
                await state.update_data(last_search_query=query)
                
                await message.answer(
                    f"🔍 Найдено *{total_count}* продуктов по запросу «{query}»:",
                    parse_mode="Markdown",
                    reply_markup=InlineKeyboards.food_search_results(
                        foods, 
                        query=query, 
                        page=0, 
                        total_count=total_count,
                        page_size=page_size
                    )
                )
            else:
                text = f"""
❌ По запросу «{query}» ничего не найдено.

Попробуй:
• Изменить запрос
• Поискать в Open Food Facts 🌐
• Добавить продукт вручную
"""
                await message.answer(
                    text,
                    reply_markup=InlineKeyboards.food_add_method()
                )


@router.callback_query(F.data.startswith("food:page:"))
async def callback_food_page(callback: CallbackQuery, state: FSMContext):
    """Переключение страницы поиска продуктов"""
    parts = callback.data.split(":")
    page = int(parts[2])
    query = ":".join(parts[3:]) if len(parts) > 3 else ""
    
    if not query:
        data = await state.get_data()
        query = data.get("last_search_query", "")
    
    if not query:
        await callback.answer("Повторите поиск")
        return
    
    async with async_session() as session:
        food_service = FoodService(session)
        page_size = 8
        offset = page * page_size
        
        foods = await food_service.search_foods(query, limit=page_size, offset=offset)
        total_count = await food_service.count_search_results(query)
        
        if foods:
            await callback.message.edit_text(
                f"🔍 Найдено *{total_count}* продуктов по запросу «{query}»:",
                parse_mode="Markdown",
                reply_markup=InlineKeyboards.food_search_results(
                    foods,
                    query=query,
                    page=page,
                    total_count=total_count,
                    page_size=page_size
                )
            )
        else:
            await callback.answer("Больше результатов нет")
    
    await callback.answer()


@router.callback_query(F.data == "noop")
async def callback_noop(callback: CallbackQuery):
    """Пустой обработчик для информационных кнопок"""
    await callback.answer()


@router.callback_query(F.data.startswith("off_food:"))
async def callback_select_off_food(callback: CallbackQuery, state: FSMContext):
    """Выбор продукта из Open Food Facts"""
    index = int(callback.data.split(":")[1])
    
    data = await state.get_data()
    products = data.get("off_products", [])
    
    if index >= len(products):
        await callback.answer("Продукт не найден")
        return
    
    product = products[index]
    
    # Сохраняем в локальную базу
    async with async_session() as session:
        food_service = FoodService(session)
        user_service = UserService(session)
        
        user = await user_service.get_user_by_telegram_id(callback.from_user.id)
        
        # Проверяем, есть ли уже в базе
        existing = await food_service.get_food_by_barcode(product.barcode) if product.barcode else None
        
        if existing:
            food = existing
        else:
            # Создаем новый продукт
            food = await food_service.create_food(
                name=product.name,
                calories_100g=product.calories_100g,
                protein_100g=product.protein_100g,
                fat_100g=product.fat_100g,
                carbs_100g=product.carbs_100g,
                brand=product.brand,
                barcode=product.barcode,
                created_by_user_id=user.id
            )
        
        await state.update_data(food_id=food.id, food_name=food.name)
        
        brand_text = f"\n🏭 Бренд: {product.brand}" if product.brand else ""
        
        text = f"""
🌐 *{product.name}*{brand_text}

📊 На 100г:
├ 🔥 Калории: {int(product.calories_100g)} ккал
├ 🥩 Белки: {product.protein_100g:.1f}г
├ 🧈 Жиры: {product.fat_100g:.1f}г
└ 🍞 Углеводы: {product.carbs_100g:.1f}г

Выбери размер порции:
"""
        
        await callback.message.edit_text(
            text,
            parse_mode="Markdown",
            reply_markup=InlineKeyboards.portion_select()
        )
    
    await callback.answer()
