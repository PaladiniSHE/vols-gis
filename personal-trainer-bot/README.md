# 🏋️ Личный Тренер — Telegram Bot

ИИ-бот персональный тренер, который поможет достичь фитнес-целей через Telegram.

## ✨ Возможности

- 📋 **Персональная анкета** — сбор данных для индивидуальной программы
- 🍽️ **План питания** — ежедневное меню с рецептами и БЖУ
- 🏋️ **Программа тренировок** — персонализированные тренировки
- 💧 **Трекер воды** — отслеживание водного баланса
- ⚖️ **Трекер веса** — история изменений и прогресс
- ⏰ **Напоминания** — уведомления о еде, воде и тренировках
- 📊 **Отчёты** — еженедельная и ежемесячная статистика
- 🤖 **ИИ-поддержка** — генерация контента через OpenAI

## 🚀 Быстрый старт

### 1. Клонирование и настройка

```bash
# Клонировать репозиторий
cd personal-trainer-bot

# Создать виртуальное окружение
python -m venv venv

# Активировать (Linux/Mac)
source venv/bin/activate

# Активировать (Windows)
venv\Scripts\activate

# Установить зависимости
pip install -r requirements.txt
```

### 2. Создание бота в Telegram

1. Откройте [@BotFather](https://t.me/BotFather) в Telegram
2. Отправьте `/newbot`
3. Введите имя бота (например: "Личный Тренер")
4. Введите username (например: `my_fitness_trainer_bot`)
5. Скопируйте полученный токен

### 3. Настройка переменных окружения

```bash
# Скопировать пример конфига
cp .env.example .env

# Отредактировать .env файл
nano .env  # или любой редактор
```

Заполните `.env`:

```env
# ОБЯЗАТЕЛЬНО
BOT_TOKEN=ваш_токен_от_botfather

# ОПЦИОНАЛЬНО (для ИИ-генерации)
OPENAI_API_KEY=ваш_ключ_openai

# ОПЦИОНАЛЬНО
ADMIN_IDS=ваш_telegram_id
DEBUG=False
```

### 4. Запуск бота

```bash
# Создать директорию для логов
mkdir -p logs

# Запустить бота
python main.py
```

## 📁 Структура проекта

```
personal-trainer-bot/
├── main.py                 # Точка входа
├── requirements.txt        # Зависимости
├── .env.example           # Пример конфига
├── .env                   # Конфиг (создать!)
│
├── config/
│   ├── __init__.py
│   └── settings.py        # Настройки приложения
│
├── database/
│   ├── __init__.py
│   ├── database.py        # Подключение к БД
│   ├── models/
│   │   ├── __init__.py
│   │   ├── base.py        # Базовая модель
│   │   ├── user.py        # Пользователь
│   │   ├── profile.py     # Профиль (анкета)
│   │   ├── progress.py    # Логи прогресса
│   │   └── program.py     # Программы тренировок
│   └── repositories/      # (опционально) репозитории
│
├── bot/
│   ├── __init__.py
│   ├── handlers/          # Обработчики команд
│   │   ├── __init__.py
│   │   ├── start.py       # /start, /help
│   │   ├── onboarding.py  # Анкетирование
│   │   ├── menu.py        # Главное меню
│   │   ├── workout.py     # Тренировки
│   │   ├── nutrition.py   # Питание
│   │   └── progress.py    # Прогресс, вес
│   ├── keyboards/         # Клавиатуры
│   │   ├── __init__.py
│   │   └── inline.py      # Inline кнопки
│   ├── states/            # FSM состояния
│   │   ├── __init__.py
│   │   └── onboarding.py  # Состояния анкеты
│   ├── middlewares/       # Middleware
│   │   ├── __init__.py
│   │   └── database.py    # Инъекция БД
│   └── services/          # Сервисы
│       ├── __init__.py
│       ├── scheduler.py   # Планировщик уведомлений
│       └── user_service.py # Работа с пользователями
│
├── ai/
│   ├── __init__.py
│   ├── trainer.py         # ИИ-генерация контента
│   └── prompts.py         # Шаблоны промптов
│
└── logs/                  # Логи (создаётся автоматически)
```

## 🎮 Команды бота

| Команда | Описание |
|---------|----------|
| `/start` | Начать работу / регистрация |
| `/menu` | Главное меню |
| `/today` | План на сегодня |
| `/workout` | Тренировка на сегодня |
| `/meal` | План питания |
| `/water` | Добавить воду |
| `/weight` | Записать вес |
| `/progress` | Отчёт о прогрессе |
| `/help` | Справка |

## ⚙️ Конфигурация

### Переменные окружения

| Переменная | Обязательно | Описание |
|------------|-------------|----------|
| `BOT_TOKEN` | ✅ | Токен бота от @BotFather |
| `OPENAI_API_KEY` | ❌ | Ключ OpenAI для ИИ-генерации |
| `DATABASE_URL` | ❌ | URL базы данных (по умолчанию SQLite) |
| `ADMIN_IDS` | ❌ | ID администраторов через запятую |
| `DEFAULT_TIMEZONE` | ❌ | Часовой пояс (Europe/Moscow) |
| `DEBUG` | ❌ | Режим отладки (False) |

### База данных

По умолчанию используется SQLite (`database/trainer.db`).

Для PostgreSQL измените `DATABASE_URL`:
```env
DATABASE_URL=postgresql+asyncpg://user:pass@localhost/trainer_db
```

## 🔧 Разработка

### Добавление нового обработчика

1. Создайте файл в `bot/handlers/`
2. Создайте роутер: `router = Router(name="my_router")`
3. Добавьте обработчики с декораторами
4. Импортируйте в `bot/handlers/__init__.py`
5. Включите роутер в `setup_routers()`

### Добавление новой модели БД

1. Создайте файл в `database/models/`
2. Унаследуйтесь от `Base` и `TimestampMixin`
3. Импортируйте в `database/models/__init__.py`
4. Перезапустите бота (таблицы создадутся автоматически)

## 📝 Логирование

Логи сохраняются в:
- `stdout` — консоль
- `logs/bot.log` — файл (ротация каждый день, хранение 7 дней)

## 🐳 Docker (опционально)

```dockerfile
# Dockerfile
FROM python:3.11-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["python", "main.py"]
```

```yaml
# docker-compose.yml
version: '3.8'
services:
  bot:
    build: .
    env_file: .env
    volumes:
      - ./logs:/app/logs
      - ./database:/app/database
    restart: unless-stopped
```

Запуск:
```bash
docker-compose up -d
```

## 🤝 Вклад в проект

1. Fork репозитория
2. Создайте ветку (`git checkout -b feature/amazing-feature`)
3. Commit изменения (`git commit -m 'Add amazing feature'`)
4. Push в ветку (`git push origin feature/amazing-feature`)
5. Откройте Pull Request

## 📄 Лицензия

MIT License — свободно используйте для личных и коммерческих проектов.

## 🆘 Поддержка

Возникли проблемы? Создайте Issue в репозитории или напишите разработчику.

---

Сделано с ❤️ для здорового образа жизни
