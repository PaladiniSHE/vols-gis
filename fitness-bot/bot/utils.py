"""
Утилиты бота
"""
from typing import Optional


def create_progress_bar(
    current: float, 
    goal: float, 
    length: int = 12,
    filled_char: str = "▓",
    empty_char: str = "░",
    show_overflow: bool = True
) -> str:
    """
    Создать текстовый прогресс-бар
    
    Args:
        current: текущее значение
        goal: целевое значение
        length: длина бара в символах
        filled_char: символ заполнения
        empty_char: символ пустого места
        show_overflow: показывать превышение
    
    Returns:
        Строка прогресс-бара
    """
    if goal <= 0:
        return empty_char * length
    
    percent = current / goal
    capped_percent = min(percent, 1.5)
    filled = int(capped_percent * length)
    filled = min(filled, length)
    
    bar = filled_char * filled + empty_char * (length - filled)
    
    if show_overflow and percent > 1:
        overflow = int((percent - 1) * 100)
        return bar + f" ⚠️ +{overflow}%"
    elif percent >= 1:
        return bar + " ✅"
    
    return bar


def create_water_bar(current_ml: int, goal_liters: float, length: int = 12) -> str:
    """Создать прогресс-бар для воды"""
    goal_ml = goal_liters * 1000
    return create_progress_bar(
        current_ml, 
        goal_ml, 
        length, 
        filled_char="💧",
        show_overflow=False
    )


def format_number(value: float, decimals: int = 1) -> str:
    """Форматирование числа"""
    if value == int(value):
        return str(int(value))
    return f"{value:.{decimals}f}"


def calculate_percent(current: float, goal: float) -> int:
    """Рассчитать процент выполнения"""
    if goal <= 0:
        return 0
    return min(int((current / goal) * 100), 999)


def format_macro_line(name: str, emoji: str, current: float, goal: float) -> str:
    """Форматировать строку макронутриента"""
    percent = calculate_percent(current, goal)
    return f"{emoji} {name}: {format_number(current)}г / {int(goal)}г ({percent}%)"


def truncate_text(text: str, max_length: int = 50) -> str:
    """Обрезать текст до максимальной длины"""
    if len(text) <= max_length:
        return text
    return text[:max_length-3] + "..."


def format_date_ru(date_obj) -> str:
    """Форматировать дату на русском"""
    months = [
        "января", "февраля", "марта", "апреля", "мая", "июня",
        "июля", "августа", "сентября", "октября", "ноября", "декабря"
    ]
    return f"{date_obj.day} {months[date_obj.month - 1]}"


def format_weekday_ru(date_obj) -> str:
    """Получить день недели на русском"""
    weekdays = ["Пн", "Вт", "Ср", "Чт", "Пт", "Сб", "Вс"]
    return weekdays[date_obj.weekday()]
