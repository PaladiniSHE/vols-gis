"""
Reply клавиатуры
"""
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove
from aiogram.utils.keyboard import ReplyKeyboardBuilder


class ReplyKeyboards:
    """Reply клавиатуры для бота"""
    
    @staticmethod
    def main_menu() -> ReplyKeyboardMarkup:
        """Главное меню (reply)"""
        builder = ReplyKeyboardBuilder()
        
        builder.row(
            KeyboardButton(text="🍽️ Питание"),
            KeyboardButton(text="💧 Вода")
        )
        builder.row(
            KeyboardButton(text="⚖️ Вес"),
            KeyboardButton(text="📊 Статистика")
        )
        builder.row(
            KeyboardButton(text="👤 Профиль")
        )
        
        return builder.as_markup(resize_keyboard=True)
    
    @staticmethod
    def cancel() -> ReplyKeyboardMarkup:
        """Кнопка отмены"""
        builder = ReplyKeyboardBuilder()
        builder.row(KeyboardButton(text="❌ Отмена"))
        return builder.as_markup(resize_keyboard=True)
    
    @staticmethod
    def skip() -> ReplyKeyboardMarkup:
        """Кнопка пропуска"""
        builder = ReplyKeyboardBuilder()
        builder.row(
            KeyboardButton(text="⏭️ Пропустить"),
            KeyboardButton(text="❌ Отмена")
        )
        return builder.as_markup(resize_keyboard=True)
    
    @staticmethod
    def remove() -> ReplyKeyboardRemove:
        """Удалить клавиатуру"""
        return ReplyKeyboardRemove()
