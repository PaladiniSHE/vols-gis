"""
Inline клавиатуры
"""
from typing import List, Optional
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder

from bot.config import Constants


class InlineKeyboards:
    """Inline клавиатуры для бота"""
    
    @staticmethod
    def main_menu() -> InlineKeyboardMarkup:
        """Главное меню"""
        builder = InlineKeyboardBuilder()
        
        builder.row(
            InlineKeyboardButton(text="🍽️ Питание", callback_data="menu:food"),
            InlineKeyboardButton(text="💧 Вода", callback_data="menu:water")
        )
        builder.row(
            InlineKeyboardButton(text="⚖️ Вес", callback_data="menu:weight"),
            InlineKeyboardButton(text="📊 Статистика", callback_data="menu:stats")
        )
        builder.row(
            InlineKeyboardButton(text="⏰ Напоминания", callback_data="menu:reminders"),
            InlineKeyboardButton(text="👤 Профиль", callback_data="menu:profile")
        )
        
        return builder.as_markup()
    
    @staticmethod
    def gender_select() -> InlineKeyboardMarkup:
        """Выбор пола (Шаг 1 - без кнопки Назад)"""
        builder = InlineKeyboardBuilder()
        
        builder.row(
            InlineKeyboardButton(text="👨 Мужской", callback_data="gender:male"),
            InlineKeyboardButton(text="👩 Женский", callback_data="gender:female")
        )
        builder.row(
            InlineKeyboardButton(text="❌ Отмена", callback_data="onboarding:cancel")
        )
        
        return builder.as_markup()
    
    @staticmethod
    def goal_select(with_back: bool = False) -> InlineKeyboardMarkup:
        """Выбор цели"""
        builder = InlineKeyboardBuilder()
        
        for goal_id, goal_data in Constants.GOALS.items():
            builder.row(
                InlineKeyboardButton(
                    text=goal_data["name"],
                    callback_data=f"goal:{goal_id}"
                )
            )
        
        if with_back:
            builder.row(
                InlineKeyboardButton(text="◀️ Назад", callback_data="onboarding:back_to_weight")
            )
        
        return builder.as_markup()
    
    @staticmethod
    def activity_select(with_back: bool = False) -> InlineKeyboardMarkup:
        """Выбор уровня активности"""
        builder = InlineKeyboardBuilder()
        
        for level_id, level_data in Constants.ACTIVITY_LEVELS.items():
            builder.row(
                InlineKeyboardButton(
                    text=f"{level_data['name']}\n{level_data['desc']}",
                    callback_data=f"activity:{level_id}"
                )
            )
        
        if with_back:
            builder.row(
                InlineKeyboardButton(text="◀️ Назад", callback_data="onboarding:back_to_goal")
            )
        
        return builder.as_markup()
    
    @staticmethod
    def onboarding_back(step: str) -> InlineKeyboardMarkup:
        """Кнопка назад для текстовых шагов онбординга"""
        builder = InlineKeyboardBuilder()
        builder.row(
            InlineKeyboardButton(text="◀️ Назад", callback_data=f"onboarding:back_to_{step}")
        )
        return builder.as_markup()
    
    @staticmethod
    def meal_select() -> InlineKeyboardMarkup:
        """Выбор приема пищи"""
        builder = InlineKeyboardBuilder()
        
        builder.row(
            InlineKeyboardButton(text="🍳 Завтрак", callback_data="meal:breakfast"),
            InlineKeyboardButton(text="🍜 Обед", callback_data="meal:lunch")
        )
        builder.row(
            InlineKeyboardButton(text="🍽️ Ужин", callback_data="meal:dinner"),
            InlineKeyboardButton(text="🍎 Перекус", callback_data="meal:snack")
        )
        builder.row(
            InlineKeyboardButton(text="📊 Итого за день", callback_data="food:daily_stats")
        )
        builder.row(
            InlineKeyboardButton(text="◀️ Назад", callback_data="menu:main")
        )
        
        return builder.as_markup()
    
    @staticmethod
    def food_add_method() -> InlineKeyboardMarkup:
        """Способ добавления еды"""
        builder = InlineKeyboardBuilder()
        
        builder.row(
            InlineKeyboardButton(text="🔍 Поиск продукта", callback_data="food:search")
        )
        builder.row(
            InlineKeyboardButton(text="🌐 Поиск онлайн (OFF)", callback_data="food:search_off")
        )
        builder.row(
            InlineKeyboardButton(text="⭐ Избранное", callback_data="food:favorites"),
            InlineKeyboardButton(text="🕐 Недавние", callback_data="food:recent")
        )
        builder.row(
            InlineKeyboardButton(text="✏️ Ввести вручную", callback_data="food:manual")
        )
        builder.row(
            InlineKeyboardButton(text="◀️ Назад", callback_data="menu:food")
        )
        
        return builder.as_markup()
    
    @staticmethod
    def food_search_results(
        foods: list, 
        query: str = "", 
        page: int = 0, 
        total_count: int = 0,
        page_size: int = 8
    ) -> InlineKeyboardMarkup:
        """Результаты поиска продуктов с пагинацией"""
        builder = InlineKeyboardBuilder()
        
        for food in foods[:page_size]:
            name = food.name[:30] + "..." if len(food.name) > 30 else food.name
            builder.row(
                InlineKeyboardButton(
                    text=f"{name} ({int(food.calories_100g)} ккал)",
                    callback_data=f"select_food:{food.id}"
                )
            )
        
        # Пагинация если есть больше результатов
        has_prev = page > 0
        has_next = (page + 1) * page_size < total_count
        
        if has_prev or has_next:
            nav_row = []
            if has_prev:
                nav_row.append(InlineKeyboardButton(
                    text="◀️ Пред.",
                    callback_data=f"food:page:{page-1}:{query}"
                ))
            
            # Показываем информацию о странице
            total_pages = (total_count + page_size - 1) // page_size
            nav_row.append(InlineKeyboardButton(
                text=f"{page+1}/{total_pages}",
                callback_data="noop"
            ))
            
            if has_next:
                nav_row.append(InlineKeyboardButton(
                    text="След. ▶️",
                    callback_data=f"food:page:{page+1}:{query}"
                ))
            
            builder.row(*nav_row)
        
        builder.row(
            InlineKeyboardButton(text="✏️ Добавить свой", callback_data="food:manual"),
            InlineKeyboardButton(text="◀️ Назад", callback_data="food:search")
        )
        
        return builder.as_markup()
    
    @staticmethod
    def portion_select() -> InlineKeyboardMarkup:
        """Выбор порции"""
        builder = InlineKeyboardBuilder()
        
        portions = [50, 100, 150, 200, 250, 300]
        
        for i in range(0, len(portions), 3):
            row = []
            for p in portions[i:i+3]:
                row.append(InlineKeyboardButton(
                    text=f"{p}г",
                    callback_data=f"portion:{p}"
                ))
            builder.row(*row)
        
        builder.row(
            InlineKeyboardButton(text="✏️ Другое", callback_data="portion:custom")
        )
        builder.row(
            InlineKeyboardButton(text="◀️ Назад", callback_data="food:add")
        )
        
        return builder.as_markup()
    
    @staticmethod
    def water_amounts() -> InlineKeyboardMarkup:
        """Кнопки для добавления воды"""
        builder = InlineKeyboardBuilder()
        
        builder.row(
            InlineKeyboardButton(text="🥤 100мл", callback_data="water:100"),
            InlineKeyboardButton(text="🥤 200мл", callback_data="water:200"),
            InlineKeyboardButton(text="🥤 250мл", callback_data="water:250")
        )
        builder.row(
            InlineKeyboardButton(text="🥤 300мл", callback_data="water:300"),
            InlineKeyboardButton(text="🥤 500мл", callback_data="water:500")
        )
        builder.row(
            InlineKeyboardButton(text="✏️ Другое", callback_data="water:custom"),
            InlineKeyboardButton(text="📋 История", callback_data="water:history")
        )
        builder.row(
            InlineKeyboardButton(text="↩️ Отменить последнее", callback_data="water:undo")
        )
        builder.row(
            InlineKeyboardButton(text="◀️ Назад", callback_data="menu:main")
        )
        
        return builder.as_markup()
    
    @staticmethod
    def water_history_back() -> InlineKeyboardMarkup:
        """Кнопка назад из истории воды"""
        builder = InlineKeyboardBuilder()
        builder.row(
            InlineKeyboardButton(text="◀️ Назад к воде", callback_data="menu:water")
        )
        return builder.as_markup()
    
    @staticmethod
    def confirm_water_undo() -> InlineKeyboardMarkup:
        """Подтверждение отмены последней записи воды"""
        builder = InlineKeyboardBuilder()
        builder.row(
            InlineKeyboardButton(text="✅ Да, отменить", callback_data="water:confirm_undo"),
            InlineKeyboardButton(text="❌ Нет", callback_data="menu:water")
        )
        return builder.as_markup()
    
    @staticmethod
    def weight_menu() -> InlineKeyboardMarkup:
        """Меню веса"""
        builder = InlineKeyboardBuilder()
        
        builder.row(
            InlineKeyboardButton(text="⚖️ Записать вес", callback_data="weight:log")
        )
        builder.row(
            InlineKeyboardButton(text="📈 История", callback_data="weight:history"),
            InlineKeyboardButton(text="📊 График", callback_data="weight:chart")
        )
        builder.row(
            InlineKeyboardButton(text="◀️ Назад", callback_data="menu:main")
        )
        
        return builder.as_markup()
    
    @staticmethod
    def stats_menu() -> InlineKeyboardMarkup:
        """Меню статистики"""
        builder = InlineKeyboardBuilder()
        
        builder.row(
            InlineKeyboardButton(text="📅 Сегодня", callback_data="stats:today"),
            InlineKeyboardButton(text="📆 Неделя", callback_data="stats:week")
        )
        builder.row(
            InlineKeyboardButton(text="📊 Прогресс", callback_data="stats:progress")
        )
        builder.row(
            InlineKeyboardButton(text="◀️ Назад", callback_data="menu:main")
        )
        
        return builder.as_markup()
    
    @staticmethod
    def profile_menu() -> InlineKeyboardMarkup:
        """Меню профиля"""
        builder = InlineKeyboardBuilder()
        
        builder.row(
            InlineKeyboardButton(text="📝 Изменить данные", callback_data="profile:edit")
        )
        builder.row(
            InlineKeyboardButton(text="🎯 Изменить цель", callback_data="profile:goal"),
            InlineKeyboardButton(text="🏃 Активность", callback_data="profile:activity")
        )
        builder.row(
            InlineKeyboardButton(text="🔄 Пересчитать нормы", callback_data="profile:recalc")
        )
        builder.row(
            InlineKeyboardButton(text="◀️ Назад", callback_data="menu:main")
        )
        
        return builder.as_markup()
    
    @staticmethod
    def confirm_action(action: str) -> InlineKeyboardMarkup:
        """Подтверждение действия"""
        builder = InlineKeyboardBuilder()
        
        builder.row(
            InlineKeyboardButton(text="✅ Да", callback_data=f"confirm:{action}"),
            InlineKeyboardButton(text="❌ Нет", callback_data="cancel")
        )
        
        return builder.as_markup()
    
    @staticmethod
    def back_to_menu() -> InlineKeyboardMarkup:
        """Кнопка возврата в меню"""
        builder = InlineKeyboardBuilder()
        builder.row(
            InlineKeyboardButton(text="◀️ В главное меню", callback_data="menu:main")
        )
        return builder.as_markup()
    
    @staticmethod
    def reminders_menu(reminders: list) -> InlineKeyboardMarkup:
        """Меню напоминаний"""
        from core.models.reminders import ReminderType
        
        builder = InlineKeyboardBuilder()
        
        reminder_names = {
            ReminderType.MEAL_BREAKFAST: "🍳 Завтрак",
            ReminderType.MEAL_LUNCH: "🍜 Обед",
            ReminderType.MEAL_DINNER: "🍽️ Ужин",
            ReminderType.WATER: "💧 Вода",
            ReminderType.WEIGHT: "⚖️ Вес",
            ReminderType.WORKOUT: "🏋️ Тренировка",
        }
        
        for r in reminders:
            status = "✅" if r.is_active else "❌"
            name = reminder_names.get(r.reminder_type, "⏰")
            time_str = r.time.strftime("%H:%M")
            
            builder.row(
                InlineKeyboardButton(
                    text=f"{status} {name} {time_str}",
                    callback_data=f"reminder:toggle:{r.id}"
                )
            )
        
        builder.row(
            InlineKeyboardButton(text="✅ Включить все", callback_data="reminders:enable_all"),
            InlineKeyboardButton(text="❌ Выключить все", callback_data="reminders:disable_all")
        )
        builder.row(
            InlineKeyboardButton(text="◀️ Назад", callback_data="menu:main")
        )
        
        return builder.as_markup()
    
    @staticmethod
    def food_entry_actions(entry_id: int, food_id: Optional[int] = None, is_favorite: bool = False) -> InlineKeyboardMarkup:
        """Действия с записью о еде"""
        builder = InlineKeyboardBuilder()
        
        if food_id:
            fav_text = "💔 Убрать из избранного" if is_favorite else "⭐ В избранное"
            fav_action = "unfavorite" if is_favorite else "favorite"
            builder.row(
                InlineKeyboardButton(
                    text=fav_text,
                    callback_data=f"food:{fav_action}:{food_id}"
                )
            )
        
        builder.row(
            InlineKeyboardButton(
                text="🗑️ Удалить запись",
                callback_data=f"food:delete:{entry_id}"
            )
        )
        builder.row(
            InlineKeyboardButton(text="◀️ Назад", callback_data="menu:food")
        )
        
        return builder.as_markup()
    
    @staticmethod
    def confirm_delete(entry_id: int) -> InlineKeyboardMarkup:
        """Подтверждение удаления"""
        builder = InlineKeyboardBuilder()
        
        builder.row(
            InlineKeyboardButton(text="✅ Да, удалить", callback_data=f"food:confirm_delete:{entry_id}"),
            InlineKeyboardButton(text="❌ Отмена", callback_data="menu:food")
        )
        
        return builder.as_markup()
    
    @staticmethod
    def off_search_results(products: list) -> InlineKeyboardMarkup:
        """Результаты поиска в Open Food Facts"""
        builder = InlineKeyboardBuilder()
        
        for i, product in enumerate(products[:8]):
            name = product.name[:35] + "..." if len(product.name) > 35 else product.name
            builder.row(
                InlineKeyboardButton(
                    text=f"{name} ({int(product.calories_100g)} ккал)",
                    callback_data=f"off_food:{i}"
                )
            )
        
        builder.row(
            InlineKeyboardButton(text="🔍 Искать в базе", callback_data="food:search"),
            InlineKeyboardButton(text="◀️ Назад", callback_data="food:add")
        )
        
        return builder.as_markup()
    
    @staticmethod
    def food_with_favorite(food_id: int, is_favorite: bool) -> InlineKeyboardMarkup:
        """Кнопки для продукта с избранным"""
        builder = InlineKeyboardBuilder()
        
        portions = [50, 100, 150, 200, 250, 300]
        
        for i in range(0, len(portions), 3):
            row = []
            for p in portions[i:i+3]:
                row.append(InlineKeyboardButton(
                    text=f"{p}г",
                    callback_data=f"portion:{p}"
                ))
            builder.row(*row)
        
        builder.row(
            InlineKeyboardButton(text="✏️ Другое", callback_data="portion:custom")
        )
        
        # Кнопка избранного
        if is_favorite:
            builder.row(
                InlineKeyboardButton(text="💔 Убрать из избранного", callback_data=f"food:unfavorite:{food_id}")
            )
        else:
            builder.row(
                InlineKeyboardButton(text="⭐ Добавить в избранное", callback_data=f"food:favorite:{food_id}")
            )
        
        builder.row(
            InlineKeyboardButton(text="◀️ Назад", callback_data="food:add")
        )
        
        return builder.as_markup()
