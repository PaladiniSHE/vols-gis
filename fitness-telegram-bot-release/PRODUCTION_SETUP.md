# 🚀 Production Setup: Личный тренер (@mytrener1_bot)

## 📦 Способ 1: Клонирование из GitHub

```bash
# Клонировать репозиторий
git clone https://github.com/PaladiniSHE/vols-gis.git
cd vols-gis/fitness-bot
```

## 📦 Способ 2: Скачать архив

Скачайте архив с GitHub:
- https://github.com/PaladiniSHE/vols-gis/archive/refs/heads/cursor/-bc-89b63568-43ce-468f-9571-c506e3ca92f6-c448.zip

---

## 🔧 Установка (Linux/macOS)

### 1. Создать виртуальное окружение

```bash
cd fitness-bot

# Создать venv
python3 -m venv venv

# Активировать
source venv/bin/activate
```

### 2. Установить зависимости

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

### 3. Настроить конфигурацию

```bash
# Создать .env файл
cp .env.example .env

# Открыть в редакторе
nano .env
```

**Содержимое .env:**

```env
# ====== ОБЯЗАТЕЛЬНО ======
BOT_TOKEN=8237762701:AAG_8IG6XiTmSEt4ZdpkWd3vvFk1HkV1OeM

# ====== РЕКОМЕНДУЕТСЯ ДЛЯ PRODUCTION ======
# Redis для FSM (состояния не теряются при перезапуске)
REDIS_URL=redis://localhost:6379/0

# Ваш Telegram ID для получения обращений /support
BOT_ADMIN_IDS=YOUR_TELEGRAM_ID

# Мониторинг ошибок (опционально)
# SENTRY_DSN=https://your-key@sentry.io/123

# ====== НАСТРОЙКИ ======
DEBUG=False
TIMEZONE=Europe/Moscow
DATABASE_URL=sqlite+aiosqlite:///./fitness_bot.db
```

### 4. Инициализация базы данных

```bash
# База создастся автоматически при первом запуске
# Продукты загрузятся из data/foods.json
```

---

## 🚀 Запуск

### Вариант A: Простой запуск (для тестирования)

```bash
# Активировать venv
source venv/bin/activate

# Запустить бот
python -m bot.main
```

### Вариант B: Production запуск (бот + напоминания)

```bash
# Терминал 1: Бот
source venv/bin/activate
python -m bot.main

# Терминал 2: Воркер напоминаний
source venv/bin/activate
python reminder_worker.py
```

### Вариант C: Запуск через systemd (рекомендуется)

Создайте файлы сервисов:

**`/etc/systemd/system/fitness-bot.service`:**

```ini
[Unit]
Description=Fitness Telegram Bot
After=network.target

[Service]
Type=simple
User=ubuntu
WorkingDirectory=/home/ubuntu/fitness-bot
Environment=PATH=/home/ubuntu/fitness-bot/venv/bin
ExecStart=/home/ubuntu/fitness-bot/venv/bin/python -m bot.main
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

**`/etc/systemd/system/fitness-reminder.service`:**

```ini
[Unit]
Description=Fitness Bot Reminder Worker
After=network.target fitness-bot.service

[Service]
Type=simple
User=ubuntu
WorkingDirectory=/home/ubuntu/fitness-bot
Environment=PATH=/home/ubuntu/fitness-bot/venv/bin
ExecStart=/home/ubuntu/fitness-bot/venv/bin/python reminder_worker.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

**Запуск сервисов:**

```bash
sudo systemctl daemon-reload
sudo systemctl enable fitness-bot fitness-reminder
sudo systemctl start fitness-bot fitness-reminder

# Проверка статуса
sudo systemctl status fitness-bot
sudo systemctl status fitness-reminder

# Логи
sudo journalctl -u fitness-bot -f
sudo journalctl -u fitness-reminder -f
```

---

## 🔐 Получение вашего Telegram ID

Для настройки BOT_ADMIN_IDS (получение /support сообщений):

1. Напишите боту @userinfobot
2. Он покажет ваш ID (числовой)
3. Добавьте в .env: `BOT_ADMIN_IDS=123456789`

---

## 🐳 Docker (альтернатива)

**`docker-compose.yml`:**

```yaml
version: '3.8'

services:
  bot:
    build: .
    env_file: .env
    depends_on:
      - redis
    restart: always
    command: python -m bot.main

  reminder-worker:
    build: .
    env_file: .env
    depends_on:
      - redis
      - bot
    restart: always
    command: python reminder_worker.py

  redis:
    image: redis:7-alpine
    restart: always
    volumes:
      - redis_data:/data

volumes:
  redis_data:
```

**`Dockerfile`:**

```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["python", "-m", "bot.main"]
```

**Запуск:**

```bash
docker-compose up -d
docker-compose logs -f
```

---

## ✅ Проверка работы

1. Откройте Telegram
2. Найдите бота: @mytrener1_bot
3. Отправьте /start
4. Пройдите онбординг
5. Проверьте функции:
   - /food — добавить еду
   - /water — добавить воду
   - /stats — статистика
   - /reminders — напоминания

---

## 🛠️ Troubleshooting

### Ошибка "BOT_TOKEN required"
```bash
# Проверьте .env файл
cat .env | grep BOT_TOKEN
```

### Ошибка подключения к Redis
```bash
# Проверьте Redis
redis-cli ping
# Должно ответить: PONG

# Если Redis не установлен, работает без него (MemoryStorage)
```

### Бот не отвечает
```bash
# Проверьте логи
sudo journalctl -u fitness-bot -n 50

# Или если запущен напрямую
python -m bot.main 2>&1 | tee bot.log
```

### Напоминания не приходят
```bash
# Проверьте воркер
sudo systemctl status fitness-reminder

# Убедитесь, что напоминания включены в боте
# /reminders -> включить нужные
```

---

## 📞 Контакты

- Бот: @mytrener1_bot
- Команда /support в боте
