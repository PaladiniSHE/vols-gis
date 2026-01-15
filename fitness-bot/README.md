# 🏋️ Личный тренер - Telegram Bot

Профессиональный русскоязычный Telegram-бот для отслеживания питания, водного баланса, веса и прогресса к фитнес-целям.

## 📱 Telegram

**Бот:** [@mytrener1_bot](https://t.me/mytrener1_bot)

## ✨ Возможности

### 🍽️ Дневник питания
- Поиск продуктов из базы данных (330+ продуктов)
- Интеграция с Open Food Facts (миллионы продуктов)
- Добавление своих продуктов
- Избранные продукты для быстрого доступа
- Пагинация результатов поиска
- Подсчет калорий и БЖУ
- История приемов пищи по дням

### 💧 Трекер воды
- Быстрое добавление воды (100-500мл)
- Расчет индивидуальной нормы
- История записей за день
- Визуальный прогресс-бар
- Отмена с подтверждением

### ⚖️ Трекер веса
- Запись веса с BMI
- История изменений за 30 дней
- Текстовые графики прогресса
- Отслеживание цели

### 📊 Статистика
- Дневная статистика с прогресс-барами
- Недельные отчеты (корректный расчет по дням)
- Средние показатели
- Отслеживание достижений

### ⏰ Напоминания
- Напоминания о приемах пищи
- Напоминания о воде
- Напоминание взвеситься
- Включение/выключение отдельных напоминаний

### 👤 Персонализация
- Онбординг с навигацией и прогрессом [1/6]
- Расчет BMR и TDEE
- Индивидуальные нормы КБЖУ
- Выбор цели (похудение/набор/поддержание)
- Учет уровня активности

### 🎮 Геймификация
- Система XP и уровней
- Серии (streaks) активности
- Достижения
- Мотивационные награды

### 🔒 Безопасность
- Rate limiting (защита от спама)
- Anti-flood middleware
- Проверка владельца при действиях

## 🚀 Быстрый старт

### Требования
- Python 3.11+
- pip
- Redis (опционально, для production)

### Установка

```bash
# Клонировать репозиторий
git clone <repository-url>
cd fitness-bot

# Создать виртуальное окружение
python -m venv venv
source venv/bin/activate  # Linux/macOS
# или
venv\Scripts\activate  # Windows

# Установить зависимости
pip install -r requirements.txt
```

### Настройка

1. Создайте файл `.env` на основе `.env.example`:

```bash
cp .env.example .env
```

2. Заполните обязательные параметры в `.env`:

```env
# Обязательно
BOT_TOKEN=your_bot_token_here

# Для production (рекомендуется)
REDIS_URL=redis://localhost:6379/0
SENTRY_DSN=https://your-dsn@sentry.io/0
DEBUG=False
```

### Запуск

```bash
# Development
python -m bot.main

# или
python run.py
```

### Запуск тестов

```bash
# Все тесты
pytest

# С покрытием
pytest --cov=services --cov=bot --cov-report=html

# Конкретный файл
pytest tests/test_calculator.py -v
```

## 📁 Структура проекта

```
fitness-bot/
├── bot/                      # Telegram бот
│   ├── main.py              # Точка входа + Sentry
│   ├── config.py            # Конфигурация
│   ├── utils.py             # Утилиты (progress bars)
│   ├── handlers/            # Обработчики команд
│   │   ├── start.py         # /start, главное меню
│   │   ├── onboarding.py    # Настройка с навигацией
│   │   ├── food.py          # Питание + OFF + пагинация
│   │   ├── water.py         # Вода + история
│   │   ├── weight.py        # Вес
│   │   ├── stats.py         # Статистика
│   │   ├── profile.py       # Профиль
│   │   └── reminders.py     # Напоминания
│   ├── keyboards/           # Клавиатуры
│   ├── middlewares/         # Middleware
│   │   └── throttling.py    # Rate limiting
│   └── states/              # FSM состояния
│
├── core/                     # Ядро приложения
│   ├── database.py          # Async SQLAlchemy
│   └── models/              # Модели
│
├── services/                 # Бизнес-логика
│   ├── calculator.py        # КБЖУ, BMI
│   ├── user_service.py      # Пользователи
│   ├── food_service.py      # Питание
│   ├── water_service.py     # Вода
│   ├── stats_service.py     # Статистика
│   ├── favorites_service.py # Избранное
│   └── reminder_service.py  # Напоминания
│
├── external/                 # Внешние API
│   └── openfoodfacts.py     # Open Food Facts
│
├── tests/                    # Тесты (72 теста)
│   ├── test_calculator.py
│   ├── test_user_service.py
│   ├── test_food_service.py
│   ├── test_water_service.py
│   ├── test_stats_service.py
│   └── test_middleware.py
│
├── data/
│   └── foods.json           # База продуктов (330+)
│
├── requirements.txt
├── .env.example             # Пример конфигурации
├── QA_TEST_REPORT.md        # Отчет тестирования
├── PRIVACY_POLICY.md        # Политика конфиденциальности
└── README.md
```

## 🔧 Конфигурация

### Переменные окружения

| Переменная | Описание | По умолчанию |
|------------|----------|--------------|
| `BOT_TOKEN` | Токен Telegram бота | **обязательно** |
| `DATABASE_URL` | URL базы данных | `sqlite+aiosqlite:///./fitness_bot.db` |
| `REDIS_URL` | URL Redis для FSM | `None` (MemoryStorage) |
| `SENTRY_DSN` | DSN для Sentry | `None` (отключено) |
| `DEBUG` | Режим отладки | `False` |
| `TIMEZONE` | Часовой пояс | `Europe/Moscow` |
| `RATE_LIMIT_INTERVAL` | Интервал между запросами | `0.5` сек |
| `RATE_LIMIT_MAX_PER_MINUTE` | Макс. запросов в минуту | `30` |

### Production настройка

```env
BOT_TOKEN=your_token
DATABASE_URL=postgresql+asyncpg://user:pass@localhost/fitness_bot
REDIS_URL=redis://localhost:6379/0
SENTRY_DSN=https://key@sentry.io/123
SENTRY_ENVIRONMENT=production
DEBUG=False
TIMEZONE=Europe/Moscow
```

## 🤖 Команды бота

| Команда | Описание |
|---------|----------|
| `/start` | Запуск бота / главное меню |
| `/menu` | Главное меню |
| `/food` | Дневник питания |
| `/water` | Трекер воды |
| `/weight` | Записать вес |
| `/stats` | Статистика |
| `/profile` | Профиль |
| `/reminders` | Настройка напоминаний |
| `/help` | Помощь |
| `/quick_water` | +250мл воды |

## 📐 Формулы расчета

### BMR (Mifflin-St Jeor)
```
Мужчины: 10×вес + 6.25×рост − 5×возраст + 5
Женщины: 10×вес + 6.25×рост − 5×возраст − 161
```

### TDEE
```
TDEE = BMR × коэффициент активности (1.2 - 1.9)
```

### Целевые калории
```
Похудение: TDEE - 500 (мин. 1200/1500)
Набор: TDEE + 500
```

## 🛠️ Технологии

- **Python 3.11+**
- **aiogram 3.4** - Telegram Bot API
- **SQLAlchemy 2.0** - Async ORM
- **Redis** - FSM Storage (production)
- **Sentry** - Error monitoring
- **aiohttp** - HTTP клиент
- **pytest** - Тестирование

## 📊 QA Оценка

| Категория | Оценка |
|-----------|--------|
| Функциональность | 85/100 |
| Юзабилити (UX) | 80/100 |
| Надежность | 85/100 |
| Безопасность | 90/100 |
| Код-качество | 85/100 |
| Тестовое покрытие | 70/100 |
| **ИТОГО** | **82.5/100** |

Подробный отчет: [QA_TEST_REPORT.md](QA_TEST_REPORT.md)

## 📝 Лицензия

MIT License

## 👨‍💻 Автор

Personal Trainer Bot Team

---

*Сделано с ❤️ для здорового образа жизни*
