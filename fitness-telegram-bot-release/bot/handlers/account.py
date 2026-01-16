"""
Обработчики для управления аккаунтом и быстрых команд
Содержит: /quick_food, /export, /delete_account, /support
"""
import json
from datetime import date, datetime
from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, BufferedInputFile
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

from bot.keyboards.inline import InlineKeyboards
from bot.config import settings, Constants
from core.database import async_session
from services.user_service import UserService
from services.food_service import FoodService
from services.water_service import WaterService
from services.stats_service import StatsService

router = Router()


class AccountStates(StatesGroup):
    """Состояния для управления аккаунтом"""
    confirming_delete = State()
    entering_support_message = State()


# ==================== QUICK FOOD ====================

@router.message(Command("quick_food"))
async def cmd_quick_food(message: Message, state: FSMContext):
    """
    Быстрое добавление еды из недавних/избранного.
    /quick_food [название] [граммы]
    Пример: /quick_food Яблоко 150
    """
    await state.clear()
    
    async with async_session() as session:
        user_service = UserService(session)
        food_service = FoodService(session)
        
        user = await user_service.get_user_by_telegram_id(message.from_user.id)
        if not user or not user.is_onboarded:
            await message.answer("Сначала настройте профиль с помощью /start")
            return
        
        # Парсинг аргументов
        args = message.text.split()[1:]  # Убираем /quick_food
        
        if len(args) >= 2:
            # Быстрое добавление: /quick_food Яблоко 150
            food_name = " ".join(args[:-1])
            try:
                portion = float(args[-1].replace(",", "."))
            except ValueError:
                await message.answer(
                    "⚠️ Неверный формат. Используйте:\n"
                    "`/quick_food Название Граммы`\n\n"
                    "Пример: `/quick_food Яблоко 150`",
                    parse_mode="Markdown"
                )
                return
            
            # Ищем продукт в базе
            foods = await food_service.search_foods(food_name, limit=1)
            
            if not foods:
                await message.answer(
                    f"❌ Продукт «{food_name}» не найден.\n\n"
                    "Используйте /food для поиска или добавьте вручную."
                )
                return
            
            food = foods[0]
            
            # Добавляем запись
            entry = await food_service.add_food_entry(
                user_id=user.id,
                meal_type="snack",  # По умолчанию - перекус
                portion_size=portion,
                food_id=food.id
            )
            
            await user_service.update_streak(message.from_user.id)
            await user_service.add_xp(message.from_user.id, Constants.XP_LOG_FOOD)
            
            await message.answer(
                f"✅ *Добавлено!*\n\n"
                f"🍽️ {food.name}\n"
                f"├ Порция: {int(portion)}г\n"
                f"├ 🔥 {int(entry.calories)} ккал\n"
                f"└ +{Constants.XP_LOG_FOOD} XP ⭐",
                parse_mode="Markdown"
            )
            return
        
        # Если без аргументов - показываем последние 5 продуктов
        recent_entries = await food_service.get_recent_foods(user.id, limit=5)
        
        if not recent_entries:
            text = """
⚡ *Быстрое добавление еды*

Используйте команду с параметрами:
`/quick_food Название Граммы`

Примеры:
• `/quick_food Яблоко 150`
• `/quick_food Куриная грудка 200`
• `/quick_food Овсянка 100`

Или используйте меню /food для поиска продуктов.
"""
        else:
            text = "⚡ *Быстрое добавление еды*\n\n"
            text += "*Недавние продукты:*\n"
            
            for food in recent_entries[:5]:
                text += f"• `{food.name}` ({int(food.calories_100g)} ккал/100г)\n"
            
            text += "\n*Команда:*\n"
            text += "`/quick_food Название Граммы`\n\n"
            text += "Пример: `/quick_food " + recent_entries[0].name + " 100`"
        
        await message.answer(text, parse_mode="Markdown")


# ==================== EXPORT DATA ====================

@router.message(Command("export"))
async def cmd_export(message: Message, state: FSMContext):
    """
    Экспорт всех данных пользователя в JSON формате.
    Соответствует требованиям GDPR о праве доступа к данным.
    """
    await state.clear()
    
    async with async_session() as session:
        user_service = UserService(session)
        food_service = FoodService(session)
        water_service = WaterService(session)
        stats_service = StatsService(session)
        
        user = await user_service.get_user_by_telegram_id(message.from_user.id)
        
        if not user:
            await message.answer("У вас нет данных для экспорта. Используйте /start для начала.")
            return
        
        await message.answer("⏳ Подготавливаю экспорт данных...")
        
        # Собираем все данные пользователя
        export_data = {
            "export_date": datetime.now().isoformat(),
            "user": {
                "telegram_id": user.telegram_id,
                "username": user.username,
                "first_name": user.first_name,
                "last_name": user.last_name,
                "created_at": user.created_at.isoformat() if user.created_at else None,
                "height": user.height,
                "weight": user.weight,
                "birth_date": user.birth_date.isoformat() if user.birth_date else None,
                "gender": user.gender.value if user.gender else None,
                "goal": user.goal.value if user.goal else None,
                "goal_weight": user.goal_weight,
                "activity_level": user.activity_level.value if user.activity_level else None,
                "bmr": user.bmr,
                "tdee": user.tdee,
                "daily_calories": user.daily_calories,
                "daily_protein": user.daily_protein,
                "daily_fat": user.daily_fat,
                "daily_carbs": user.daily_carbs,
                "daily_water": user.daily_water,
                "timezone": user.timezone,
                "xp": user.xp,
                "level": user.level,
                "current_streak": user.current_streak,
                "longest_streak": user.longest_streak,
            },
        }
        
        # Записи о питании за последние 30 дней
        from datetime import timedelta
        today = date.today()
        food_entries = []
        for i in range(30):
            day = today - timedelta(days=i)
            entries = await food_service.get_entries_by_date(user.id, day)
            for entry in entries:
                food_entries.append({
                    "date": entry.entry_date.isoformat(),
                    "meal_type": entry.meal_type,
                    "food_name": entry.food.name if entry.food else entry.custom_food_name,
                    "portion_g": entry.portion_size,
                    "calories": entry.calories,
                    "protein": entry.protein,
                    "fat": entry.fat,
                    "carbs": entry.carbs,
                    "logged_at": entry.logged_at.isoformat() if entry.logged_at else None
                })
        
        export_data["food_entries"] = food_entries
        
        # Записи о воде за последние 30 дней
        water_entries = []
        for i in range(30):
            day = today - timedelta(days=i)
            entries = await water_service.get_entries_by_date(user.id, day)
            for entry in entries:
                water_entries.append({
                    "date": entry.entry_date.isoformat(),
                    "amount_ml": entry.amount_ml,
                    "logged_at": entry.logged_at.isoformat() if entry.logged_at else None
                })
        
        export_data["water_entries"] = water_entries
        
        # История веса
        weight_history = await stats_service.get_weight_history(user.id, days=365)
        export_data["weight_history"] = [
            {
                "date": w.entry_date.isoformat(),
                "weight": w.weight
            }
            for w in weight_history
        ]
        
        # Создаем JSON файл
        json_content = json.dumps(export_data, ensure_ascii=False, indent=2)
        
        # Отправляем как файл
        document = BufferedInputFile(
            json_content.encode('utf-8'),
            filename=f"fitness_bot_export_{today.isoformat()}.json"
        )
        
        await message.answer_document(
            document,
            caption=(
                f"📦 *Экспорт данных*\n\n"
                f"✅ Ваши данные из бота «Личный тренер»\n"
                f"📅 Дата экспорта: {today.strftime('%d.%m.%Y')}\n\n"
                f"📊 Содержит:\n"
                f"├ Профиль пользователя\n"
                f"├ {len(food_entries)} записей питания\n"
                f"├ {len(water_entries)} записей воды\n"
                f"└ {len(weight_history)} записей веса"
            ),
            parse_mode="Markdown"
        )


# ==================== DELETE ACCOUNT ====================

@router.message(Command("delete_account"))
async def cmd_delete_account(message: Message, state: FSMContext):
    """
    Начать процесс удаления аккаунта.
    Соответствует требованиям GDPR о праве на удаление данных.
    """
    await state.clear()
    
    async with async_session() as session:
        user_service = UserService(session)
        user = await user_service.get_user_by_telegram_id(message.from_user.id)
        
        if not user:
            await message.answer("У вас нет аккаунта для удаления.")
            return
    
    text = """
⚠️ *УДАЛЕНИЕ АККАУНТА*

Вы собираетесь *безвозвратно* удалить:
• Профиль и настройки
• Всю историю питания
• Все записи о воде
• Историю веса
• Достижения и XP

🔴 *Это действие нельзя отменить!*

Если вы уверены, нажмите кнопку ниже:
"""
    
    await message.answer(
        text,
        parse_mode="Markdown",
        reply_markup=InlineKeyboards.confirm_delete_account()
    )


@router.callback_query(F.data == "account:confirm_delete")
async def callback_confirm_delete(callback: CallbackQuery, state: FSMContext):
    """Подтверждение удаления аккаунта"""
    
    await callback.message.edit_text(
        "🔐 *Последнее подтверждение*\n\n"
        "Для удаления аккаунта введите слово:\n\n"
        "`УДАЛИТЬ`\n\n"
        "Или отправьте /cancel для отмены.",
        parse_mode="Markdown"
    )
    await state.set_state(AccountStates.confirming_delete)
    await callback.answer()


@router.message(AccountStates.confirming_delete)
async def process_delete_confirmation(message: Message, state: FSMContext):
    """Обработка подтверждения удаления"""
    
    if message.text == "/cancel":
        await state.clear()
        await message.answer("❌ Удаление отменено. Ваши данные в безопасности.")
        return
    
    if message.text != "УДАЛИТЬ":
        await message.answer(
            "⚠️ Неверное подтверждение.\n\n"
            "Введите `УДАЛИТЬ` для подтверждения или /cancel для отмены.",
            parse_mode="Markdown"
        )
        return
    
    # Удаляем все данные пользователя
    async with async_session() as session:
        from sqlalchemy import delete
        from core.models.user import User
        from core.models.food import FoodEntry
        from core.models.water import WaterEntry
        from core.models.weight import WeightLog
        from core.models.reminders import Reminder
        from core.models.favorites import UserFavoriteFood
        
        user_service = UserService(session)
        user = await user_service.get_user_by_telegram_id(message.from_user.id)
        
        if not user:
            await state.clear()
            await message.answer("Аккаунт уже удален.")
            return
        
        user_id = user.id
        
        # Удаляем все связанные данные
        await session.execute(delete(FoodEntry).where(FoodEntry.user_id == user_id))
        await session.execute(delete(WaterEntry).where(WaterEntry.user_id == user_id))
        await session.execute(delete(WeightLog).where(WeightLog.user_id == user_id))
        await session.execute(delete(Reminder).where(Reminder.user_id == user_id))
        await session.execute(delete(UserFavoriteFood).where(UserFavoriteFood.user_id == user_id))
        
        # Удаляем пользователя
        await session.execute(delete(User).where(User.id == user_id))
        await session.commit()
    
    await state.clear()
    
    await message.answer(
        "✅ *Аккаунт удален*\n\n"
        "Все ваши данные безвозвратно удалены.\n\n"
        "Спасибо, что пользовались ботом! 👋\n"
        "Если захотите вернуться — отправьте /start",
        parse_mode="Markdown"
    )


@router.callback_query(F.data == "account:cancel_delete")
async def callback_cancel_delete(callback: CallbackQuery, state: FSMContext):
    """Отмена удаления аккаунта"""
    await state.clear()
    await callback.message.edit_text(
        "✅ *Удаление отменено*\n\n"
        "Ваши данные в безопасности.",
        parse_mode="Markdown",
        reply_markup=InlineKeyboards.back_to_menu()
    )
    await callback.answer()


# ==================== SUPPORT ====================

@router.message(Command("support"))
async def cmd_support(message: Message, state: FSMContext):
    """
    Связь с поддержкой бота.
    """
    await state.clear()
    
    text = """
📞 *Поддержка*

Если у вас есть вопросы или проблемы с ботом:

1️⃣ *Частые вопросы:*
├ Как изменить цель? → Профиль → 🎯 Изменить цель
├ Как удалить запись? → Питание → История
└ Как отключить напоминания? → ⏰ Напоминания

2️⃣ *Нашли баг?*
Опишите проблему и отправьте нам.

3️⃣ *Предложения?*
Мы рады обратной связи!

Напишите ваше сообщение ниже 👇
(или /cancel для отмены)
"""
    
    await message.answer(text, parse_mode="Markdown")
    await state.set_state(AccountStates.entering_support_message)


@router.message(AccountStates.entering_support_message)
async def process_support_message(message: Message, state: FSMContext):
    """Обработка сообщения в поддержку"""
    
    if message.text == "/cancel":
        await state.clear()
        await message.answer("❌ Отменено", reply_markup=InlineKeyboards.back_to_menu())
        return
    
    # Сохраняем сообщение (в реальном проекте - отправка администраторам)
    support_text = message.text
    user_info = f"@{message.from_user.username}" if message.from_user.username else f"ID: {message.from_user.id}"
    
    # Логируем обращение
    import logging
    logger = logging.getLogger("support")
    logger.info(f"Support request from {user_info}: {support_text[:100]}...")
    
    # Отправляем администраторам (если настроены)
    if settings.bot_admin_ids:
        from aiogram import Bot
        bot = Bot(token=settings.bot_token)
        
        admin_text = (
            f"📩 *Новое обращение в поддержку*\n\n"
            f"👤 Пользователь: {message.from_user.full_name} ({user_info})\n"
            f"📅 Дата: {datetime.now().strftime('%d.%m.%Y %H:%M')}\n\n"
            f"📝 Сообщение:\n{support_text}"
        )
        
        for admin_id in settings.bot_admin_ids:
            try:
                await bot.send_message(admin_id, admin_text, parse_mode="Markdown")
            except Exception:
                pass
        
        await bot.session.close()
    
    await state.clear()
    
    await message.answer(
        "✅ *Сообщение отправлено!*\n\n"
        "Спасибо за обратную связь! Мы постараемся ответить как можно скорее.\n\n"
        "📧 Обычное время ответа: 1-2 рабочих дня",
        parse_mode="Markdown",
        reply_markup=InlineKeyboards.back_to_menu()
    )
