"""
Inline клавиатуры
"""
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder


def get_start_keyboard() -> InlineKeyboardMarkup:
    """Стартовая клавиатура"""
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(text="🚀 Начать!", callback_data="start_onboarding"),
        InlineKeyboardButton(text="❓ Подробнее", callback_data="about_bot")
    )
    return builder.as_markup()


def get_main_menu_keyboard() -> InlineKeyboardMarkup:
    """Главное меню"""
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(text="📅 План на сегодня", callback_data="today_plan")
    )
    builder.row(
        InlineKeyboardButton(text="🏋️ Тренировка", callback_data="workout"),
        InlineKeyboardButton(text="🍽️ Питание", callback_data="nutrition")
    )
    builder.row(
        InlineKeyboardButton(text="💧 Вода", callback_data="water"),
        InlineKeyboardButton(text="⚖️ Вес", callback_data="weight")
    )
    builder.row(
        InlineKeyboardButton(text="📊 Прогресс", callback_data="progress"),
        InlineKeyboardButton(text="⚙️ Настройки", callback_data="settings")
    )
    return builder.as_markup()


def get_gender_keyboard() -> InlineKeyboardMarkup:
    """Выбор пола"""
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(text="👨 Мужской", callback_data="gender_male"),
        InlineKeyboardButton(text="👩 Женский", callback_data="gender_female")
    )
    builder.row(
        InlineKeyboardButton(text="🌈 Другое", callback_data="gender_other")
    )
    return builder.as_markup()


def get_goal_keyboard() -> InlineKeyboardMarkup:
    """Выбор цели"""
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(text="🔻 Похудение", callback_data="goal_weight_loss")
    )
    builder.row(
        InlineKeyboardButton(text="💪 Набор массы", callback_data="goal_muscle_gain")
    )
    builder.row(
        InlineKeyboardButton(text="⚖️ Поддержание", callback_data="goal_maintenance")
    )
    builder.row(
        InlineKeyboardButton(text="🏃 Выносливость", callback_data="goal_endurance")
    )
    builder.row(
        InlineKeyboardButton(text="❤️ Здоровье", callback_data="goal_health")
    )
    return builder.as_markup()


def get_fitness_level_keyboard() -> InlineKeyboardMarkup:
    """Выбор уровня подготовки"""
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(text="🌱 Начинающий", callback_data="level_beginner")
    )
    builder.row(
        InlineKeyboardButton(text="📈 Средний", callback_data="level_intermediate")
    )
    builder.row(
        InlineKeyboardButton(text="🔥 Продвинутый", callback_data="level_advanced")
    )
    builder.row(
        InlineKeyboardButton(text="🏆 Профи", callback_data="level_pro")
    )
    return builder.as_markup()


def get_training_location_keyboard() -> InlineKeyboardMarkup:
    """Выбор места тренировок"""
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(text="🏋️ Тренажёрный зал", callback_data="location_gym")
    )
    builder.row(
        InlineKeyboardButton(text="🏠 Дома (есть инвентарь)", callback_data="location_home_equipped")
    )
    builder.row(
        InlineKeyboardButton(text="🏠 Дома (без инвентаря)", callback_data="location_home_basic")
    )
    builder.row(
        InlineKeyboardButton(text="🌳 На улице", callback_data="location_outdoor")
    )
    builder.row(
        InlineKeyboardButton(text="🔄 Комбинированно", callback_data="location_mixed")
    )
    return builder.as_markup()


def get_diet_type_keyboard() -> InlineKeyboardMarkup:
    """Выбор типа питания"""
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(text="🍖 Всеядное", callback_data="diet_omnivore")
    )
    builder.row(
        InlineKeyboardButton(text="🥬 Вегетарианство", callback_data="diet_vegetarian")
    )
    builder.row(
        InlineKeyboardButton(text="🌿 Веганство", callback_data="diet_vegan")
    )
    builder.row(
        InlineKeyboardButton(text="🥓 Кето", callback_data="diet_keto")
    )
    builder.row(
        InlineKeyboardButton(text="🚫🌾 Без глютена", callback_data="diet_gluten_free")
    )
    return builder.as_markup()


def get_work_type_keyboard() -> InlineKeyboardMarkup:
    """Выбор типа работы"""
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(text="🪑 Сидячая", callback_data="work_sedentary"),
        InlineKeyboardButton(text="🚶 Умеренная", callback_data="work_moderate")
    )
    builder.row(
        InlineKeyboardButton(text="🏃 Активная", callback_data="work_active"),
        InlineKeyboardButton(text="🔨 Физическая", callback_data="work_physical")
    )
    return builder.as_markup()


def get_training_days_keyboard() -> InlineKeyboardMarkup:
    """Выбор количества тренировок в неделю"""
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(text="2️⃣", callback_data="days_2"),
        InlineKeyboardButton(text="3️⃣", callback_data="days_3"),
        InlineKeyboardButton(text="4️⃣", callback_data="days_4")
    )
    builder.row(
        InlineKeyboardButton(text="5️⃣", callback_data="days_5"),
        InlineKeyboardButton(text="6️⃣", callback_data="days_6"),
        InlineKeyboardButton(text="7️⃣", callback_data="days_7")
    )
    return builder.as_markup()


def get_confirmation_keyboard() -> InlineKeyboardMarkup:
    """Подтверждение"""
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(text="✅ Подтвердить", callback_data="confirm"),
        InlineKeyboardButton(text="✏️ Изменить", callback_data="edit")
    )
    return builder.as_markup()


def get_workout_status_keyboard() -> InlineKeyboardMarkup:
    """Статус тренировки"""
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(text="✅ Выполнено", callback_data="workout_completed")
    )
    builder.row(
        InlineKeyboardButton(text="⚡ Частично", callback_data="workout_partial")
    )
    builder.row(
        InlineKeyboardButton(text="❌ Пропущено", callback_data="workout_skipped")
    )
    builder.row(
        InlineKeyboardButton(text="🔄 Перенести", callback_data="workout_reschedule")
    )
    return builder.as_markup()


def get_meal_keyboard() -> InlineKeyboardMarkup:
    """Приём пищи"""
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(text="✅ По плану", callback_data="meal_on_plan"),
        InlineKeyboardButton(text="⚡ С изменениями", callback_data="meal_modified")
    )
    builder.row(
        InlineKeyboardButton(text="❌ Пропустил", callback_data="meal_skipped"),
        InlineKeyboardButton(text="🍕 Срыв", callback_data="meal_cheat")
    )
    return builder.as_markup()


def get_rating_keyboard(prefix: str = "rating") -> InlineKeyboardMarkup:
    """Оценка от 1 до 10"""
    builder = InlineKeyboardBuilder()
    for i in range(1, 6):
        builder.add(InlineKeyboardButton(text=str(i), callback_data=f"{prefix}_{i}"))
    builder.row()
    for i in range(6, 11):
        builder.add(InlineKeyboardButton(text=str(i), callback_data=f"{prefix}_{i}"))
    return builder.as_markup()


def get_skip_keyboard(next_callback: str) -> InlineKeyboardMarkup:
    """Пропустить вопрос"""
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(text="⏭️ Пропустить", callback_data=next_callback)
    )
    return builder.as_markup()


def get_yes_no_keyboard(prefix: str = "yn") -> InlineKeyboardMarkup:
    """Да/Нет"""
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(text="✅ Да", callback_data=f"{prefix}_yes"),
        InlineKeyboardButton(text="❌ Нет", callback_data=f"{prefix}_no")
    )
    return builder.as_markup()


def get_back_keyboard(callback: str = "back") -> InlineKeyboardMarkup:
    """Кнопка назад"""
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(text="⬅️ Назад", callback_data=callback)
    )
    return builder.as_markup()


def get_settings_keyboard() -> InlineKeyboardMarkup:
    """Клавиатура настроек"""
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(text="🔔 Уведомления", callback_data="settings_notifications")
    )
    builder.row(
        InlineKeyboardButton(text="⏰ Время подъёма", callback_data="settings_wake"),
        InlineKeyboardButton(text="🌙 Время сна", callback_data="settings_sleep")
    )
    builder.row(
        InlineKeyboardButton(text="🌍 Часовой пояс", callback_data="settings_timezone")
    )
    builder.row(
        InlineKeyboardButton(text="🏠 Главное меню", callback_data="main_menu")
    )
    return builder.as_markup()


def get_timezone_keyboard() -> InlineKeyboardMarkup:
    """Выбор часового пояса"""
    builder = InlineKeyboardBuilder()
    timezones = [
        ("🇷🇺 Калининград (UTC+2)", "Europe/Kaliningrad"),
        ("🇷🇺 Москва (UTC+3)", "Europe/Moscow"),
        ("🇷🇺 Самара (UTC+4)", "Europe/Samara"),
        ("🇷🇺 Екатеринбург (UTC+5)", "Asia/Yekaterinburg"),
        ("🇷🇺 Омск (UTC+6)", "Asia/Omsk"),
        ("🇷🇺 Красноярск (UTC+7)", "Asia/Krasnoyarsk"),
        ("🇷🇺 Иркутск (UTC+8)", "Asia/Irkutsk"),
        ("🇷🇺 Владивосток (UTC+10)", "Asia/Vladivostok"),
        ("🇺🇦 Киев (UTC+2)", "Europe/Kiev"),
        ("🇧🇾 Минск (UTC+3)", "Europe/Minsk"),
        ("🇰🇿 Алматы (UTC+6)", "Asia/Almaty"),
    ]
    
    for name, tz in timezones:
        builder.row(
            InlineKeyboardButton(text=name, callback_data=f"tz_{tz}")
        )
    
    builder.row(
        InlineKeyboardButton(text="⬅️ Назад", callback_data="settings")
    )
    return builder.as_markup()


def get_notifications_keyboard(enabled: bool) -> InlineKeyboardMarkup:
    """Клавиатура настройки уведомлений"""
    builder = InlineKeyboardBuilder()
    
    if enabled:
        builder.row(
            InlineKeyboardButton(text="🔕 Выключить уведомления", callback_data="notif_off")
        )
    else:
        builder.row(
            InlineKeyboardButton(text="🔔 Включить уведомления", callback_data="notif_on")
        )
    
    builder.row(
        InlineKeyboardButton(text="⬅️ Назад", callback_data="settings")
    )
    return builder.as_markup()


def get_time_keyboard(time_type: str) -> InlineKeyboardMarkup:
    """Клавиатура выбора времени"""
    builder = InlineKeyboardBuilder()
    
    if time_type == "wake":
        times = ["05:00", "05:30", "06:00", "06:30", "07:00", "07:30", "08:00", "08:30", "09:00", "09:30", "10:00"]
    else:  # sleep
        times = ["21:00", "21:30", "22:00", "22:30", "23:00", "23:30", "00:00", "00:30", "01:00"]
    
    # По 3 кнопки в ряд
    row = []
    for i, t in enumerate(times):
        row.append(InlineKeyboardButton(text=t, callback_data=f"time_{time_type}_{t}"))
        if len(row) == 3:
            builder.row(*row)
            row = []
    if row:
        builder.row(*row)
    
    builder.row(
        InlineKeyboardButton(text="⬅️ Назад", callback_data="settings")
    )
    return builder.as_markup()


def get_water_keyboard() -> InlineKeyboardMarkup:
    """Добавление воды"""
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(text="🥛 200мл", callback_data="water_200"),
        InlineKeyboardButton(text="🥛 250мл", callback_data="water_250"),
        InlineKeyboardButton(text="🥛 300мл", callback_data="water_300")
    )
    builder.row(
        InlineKeyboardButton(text="🍶 500мл", callback_data="water_500"),
        InlineKeyboardButton(text="🧴 1л", callback_data="water_1000")
    )
    builder.row(
        InlineKeyboardButton(text="🏠 Главное меню", callback_data="main_menu")
    )
    return builder.as_markup()


def get_nav_keyboard(current: str = None) -> InlineKeyboardMarkup:
    """Навигационная клавиатура с подсветкой текущего раздела"""
    builder = InlineKeyboardBuilder()
    
    # Основные разделы
    today_text = "📅 Сегодня" if current != "today" else "📅 • Сегодня •"
    workout_text = "🏋️ Тренировка" if current != "workout" else "🏋️ • Тренировка •"
    meal_text = "🍽️ Питание" if current != "meal" else "🍽️ • Питание •"
    
    builder.row(
        InlineKeyboardButton(text=today_text, callback_data="today_plan")
    )
    builder.row(
        InlineKeyboardButton(text=workout_text, callback_data="workout"),
        InlineKeyboardButton(text=meal_text, callback_data="nutrition")
    )
    builder.row(
        InlineKeyboardButton(text="💧 Вода", callback_data="water"),
        InlineKeyboardButton(text="⚖️ Вес", callback_data="weight")
    )
    builder.row(
        InlineKeyboardButton(text="📊 Прогресс", callback_data="progress"),
        InlineKeyboardButton(text="⚙️ Настройки", callback_data="settings")
    )
    return builder.as_markup()


def get_back_to_menu_keyboard() -> InlineKeyboardMarkup:
    """Кнопка возврата в меню"""
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(text="⬅️ Назад в меню", callback_data="main_menu")
    )
    return builder.as_markup()


def get_workout_keyboard() -> InlineKeyboardMarkup:
    """Клавиатура тренировки"""
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(text="✅ Выполнено", callback_data="workout_completed")
    )
    builder.row(
        InlineKeyboardButton(text="⚡ Частично", callback_data="workout_partial"),
        InlineKeyboardButton(text="❌ Пропущено", callback_data="workout_skipped")
    )
    builder.row(
        InlineKeyboardButton(text="🔄 Перенести", callback_data="workout_reschedule")
    )
    builder.row(
        InlineKeyboardButton(text="🏠 Главное меню", callback_data="main_menu")
    )
    return builder.as_markup()


def get_meal_status_keyboard() -> InlineKeyboardMarkup:
    """Клавиатура статуса приёма пищи"""
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(text="✅ По плану", callback_data="meal_on_plan"),
        InlineKeyboardButton(text="⚡ С изменениями", callback_data="meal_modified")
    )
    builder.row(
        InlineKeyboardButton(text="❌ Пропустил", callback_data="meal_skipped"),
        InlineKeyboardButton(text="🍕 Срыв", callback_data="meal_cheat")
    )
    builder.row(
        InlineKeyboardButton(text="🏠 Главное меню", callback_data="main_menu")
    )
    return builder.as_markup()
