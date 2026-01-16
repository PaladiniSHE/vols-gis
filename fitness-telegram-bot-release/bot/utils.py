"""
Утилиты бота
"""
from datetime import date, datetime, time
from typing import Optional
import pytz


def create_progress_bar(
    current: float,
    goal: float,
    length: int = 12,
    filled_char: str = "▓",
    empty_char: str = "░",
    show_overflow: bool = True
) -> str:
    """
    Создать визуальный прогресс-бар.
    
    Args:
        current: Текущее значение
        goal: Целевое значение
        length: Длина бара в символах
        filled_char: Символ заполненной части
        empty_char: Символ пустой части
        show_overflow: Показывать ли превышение
    
    Returns:
        Строка с прогресс-баром
    """
    if goal <= 0:
        return empty_char * length
    
    percent = current / goal
    capped_percent = min(percent, 1.5)  # Ограничиваем до 150%
    
    filled = min(int(capped_percent * length), length)
    empty = length - filled
    
    bar = filled_char * filled + empty_char * empty
    
    # Показываем превышение
    if show_overflow and percent > 1.0:
        overflow_percent = int((percent - 1.0) * 100)
        bar += f" ⚠️ +{overflow_percent}%"
    
    return bar


def create_water_bar(
    current_ml: float,
    goal_liters: float,
    length: int = 12
) -> str:
    """
    Создать прогресс-бар для воды с эмодзи.
    
    Args:
        current_ml: Текущее количество в мл
        goal_liters: Цель в литрах
    
    Returns:
        Строка с прогресс-баром
    """
    goal_ml = goal_liters * 1000
    return "💧 " + create_progress_bar(current_ml, goal_ml, length)


def format_number(value: float, decimals: int = 1) -> str:
    """Форматировать число для отображения"""
    if value == int(value):
        return str(int(value))
    return f"{value:.{decimals}f}"


def calculate_percent(current: float, goal: float) -> int:
    """Рассчитать процент выполнения"""
    if goal <= 0:
        return 0
    return int((current / goal) * 100)


def truncate_text(text: str, max_length: int = 30, suffix: str = "...") -> str:
    """Обрезать текст до указанной длины"""
    if len(text) <= max_length:
        return text
    return text[:max_length - len(suffix)] + suffix


# ==================== TIMEZONE UTILITIES ====================

# Список популярных часовых поясов для выбора
POPULAR_TIMEZONES = [
    ("Europe/Moscow", "🇷🇺 Москва (UTC+3)"),
    ("Europe/Kaliningrad", "🇷🇺 Калининград (UTC+2)"),
    ("Europe/Samara", "🇷🇺 Самара (UTC+4)"),
    ("Asia/Yekaterinburg", "🇷🇺 Екатеринбург (UTC+5)"),
    ("Asia/Novosibirsk", "🇷🇺 Новосибирск (UTC+7)"),
    ("Asia/Krasnoyarsk", "🇷🇺 Красноярск (UTC+7)"),
    ("Asia/Irkutsk", "🇷🇺 Иркутск (UTC+8)"),
    ("Asia/Vladivostok", "🇷🇺 Владивосток (UTC+10)"),
    ("Europe/Kiev", "🇺🇦 Киев (UTC+2)"),
    ("Europe/Minsk", "🇧🇾 Минск (UTC+3)"),
    ("Asia/Almaty", "🇰🇿 Алматы (UTC+6)"),
    ("Asia/Tashkent", "🇺🇿 Ташкент (UTC+5)"),
    ("Europe/Berlin", "🇩🇪 Берлин (UTC+1)"),
    ("America/New_York", "🇺🇸 Нью-Йорк (UTC-5)"),
]


def get_user_datetime(timezone_str: str = "Europe/Moscow") -> datetime:
    """
    Получить текущую дату/время в часовом поясе пользователя.
    
    Args:
        timezone_str: Строка часового пояса (например, 'Europe/Moscow')
    
    Returns:
        datetime в указанном часовом поясе
    """
    try:
        tz = pytz.timezone(timezone_str)
        return datetime.now(tz)
    except pytz.UnknownTimeZoneError:
        # Fallback на Moscow
        tz = pytz.timezone("Europe/Moscow")
        return datetime.now(tz)


def get_user_date(timezone_str: str = "Europe/Moscow") -> date:
    """
    Получить текущую дату в часовом поясе пользователя.
    
    Args:
        timezone_str: Строка часового пояса
    
    Returns:
        date в указанном часовом поясе
    """
    return get_user_datetime(timezone_str).date()


def get_user_time(timezone_str: str = "Europe/Moscow") -> time:
    """
    Получить текущее время в часовом поясе пользователя.
    
    Args:
        timezone_str: Строка часового пояса
    
    Returns:
        time в указанном часовом поясе
    """
    return get_user_datetime(timezone_str).time()


def format_datetime_for_user(
    dt: datetime,
    timezone_str: str = "Europe/Moscow",
    format_str: str = "%d.%m.%Y %H:%M"
) -> str:
    """
    Форматировать datetime для отображения пользователю в его часовом поясе.
    
    Args:
        dt: datetime (может быть UTC или naive)
        timezone_str: Часовой пояс пользователя
        format_str: Формат отображения
    
    Returns:
        Форматированная строка
    """
    try:
        tz = pytz.timezone(timezone_str)
        
        # Если datetime без timezone, считаем его UTC
        if dt.tzinfo is None:
            dt = pytz.UTC.localize(dt)
        
        # Конвертируем в часовой пояс пользователя
        local_dt = dt.astimezone(tz)
        return local_dt.strftime(format_str)
    except Exception:
        return dt.strftime(format_str)


def get_timezone_display_name(timezone_str: str) -> str:
    """Получить человеко-читаемое название часового пояса"""
    for tz_code, tz_name in POPULAR_TIMEZONES:
        if tz_code == timezone_str:
            return tz_name
    return timezone_str
