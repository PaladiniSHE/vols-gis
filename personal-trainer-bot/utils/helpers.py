"""
Вспомогательные функции
"""
from datetime import datetime, date
from typing import Union


def format_number(value: Union[int, float], decimals: int = 1) -> str:
    """Форматирование числа"""
    if isinstance(value, float):
        return f"{value:.{decimals}f}"
    return str(value)


def format_date(d: Union[date, datetime], fmt: str = "%d.%m.%Y") -> str:
    """Форматирование даты"""
    return d.strftime(fmt)


def format_time(t: Union[datetime, str], fmt: str = "%H:%M") -> str:
    """Форматирование времени"""
    if isinstance(t, str):
        return t
    return t.strftime(fmt)


def calculate_bmi(weight: float, height: float) -> float:
    """Расчёт ИМТ"""
    height_m = height / 100
    return round(weight / (height_m ** 2), 1)


def get_bmi_category(bmi: float) -> str:
    """Категория ИМТ"""
    if bmi < 18.5:
        return "Недостаточный вес"
    elif bmi < 25:
        return "Норма"
    elif bmi < 30:
        return "Избыточный вес"
    elif bmi < 35:
        return "Ожирение I степени"
    elif bmi < 40:
        return "Ожирение II степени"
    else:
        return "Ожирение III степени"


def calculate_water_goal(weight: float) -> float:
    """Расчёт нормы воды (мл на кг)"""
    return round(weight * 30 / 1000, 1)  # литры


def days_until(target_date: date) -> int:
    """Дней до даты"""
    delta = target_date - date.today()
    return max(0, delta.days)


def progress_bar(current: float, target: float, length: int = 10) -> str:
    """Текстовый прогресс-бар"""
    if target <= 0:
        return "░" * length
    
    percent = min(1.0, current / target)
    filled = int(percent * length)
    
    return "█" * filled + "░" * (length - filled)
