# 🚀 Установка и запуск бота "Личный тренер"

## 📋 Требования

- **Python 3.10+** (рекомендуется 3.11)
- **pip** (менеджер пакетов Python)
- **Интернет соединение**

---

## 🖥️ Установка на Windows

### Шаг 1: Установите Python

1. Скачайте Python: https://www.python.org/downloads/
2. **ВАЖНО:** При установке поставьте галочку **"Add Python to PATH"**
3. Установите Python

### Шаг 2: Откройте командную строку

- Нажмите `Win + R`
- Введите `cmd` и нажмите Enter

### Шаг 3: Перейдите в папку с ботом

```cmd
cd C:\путь\к\папке\fitness-telegram-bot-release
```

### Шаг 4: Создайте виртуальное окружение

```cmd
python -m venv venv
venv\Scripts\activate
```

### Шаг 5: Установите зависимости

```cmd
pip install -r requirements.txt
```

### Шаг 6: Настройте конфигурацию

1. Скопируйте файл `.env.example` и назовите его `.env`
2. Откройте `.env` в блокноте
3. Замените `your_bot_token_here` на токен вашего бота:

```
BOT_TOKEN=8237762701:AAG_8IG6XiTmSEt4ZdpkWd3vvFk1HkV1OeM
```

### Шаг 7: Запустите бота

```cmd
python -m bot.main
```

---

## 🍎 Установка на macOS

### Шаг 1: Установите Python (если нет)

```bash
# Через Homebrew
brew install python@3.11
```

### Шаг 2: Откройте Terminal и перейдите в папку

```bash
cd ~/Downloads/fitness-telegram-bot-release
```

### Шаг 3: Создайте окружение и установите зависимости

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### Шаг 4: Настройте конфигурацию

```bash
cp .env.example .env
nano .env
```

Вставьте токен:
```
BOT_TOKEN=8237762701:AAG_8IG6XiTmSEt4ZdpkWd3vvFk1HkV1OeM
```

Сохраните: `Ctrl+O`, `Enter`, `Ctrl+X`

### Шаг 5: Запустите

```bash
python -m bot.main
```

---

## 🐧 Установка на Linux (Ubuntu/Debian)

### Шаг 1: Установите Python

```bash
sudo apt update
sudo apt install python3.11 python3.11-venv python3-pip
```

### Шаг 2: Перейдите в папку и настройте

```bash
cd ~/fitness-telegram-bot-release
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### Шаг 3: Настройте .env

```bash
cp .env.example .env
nano .env
```

Добавьте токен:
```
BOT_TOKEN=8237762701:AAG_8IG6XiTmSEt4ZdpkWd3vvFk1HkV1OeM
```

### Шаг 4: Запустите

```bash
python -m bot.main
```

---

## ⚡ Быстрый запуск (после первой установки)

### Windows:
```cmd
cd C:\путь\к\боту
venv\Scripts\activate
python -m bot.main
```

### macOS / Linux:
```bash
cd ~/fitness-telegram-bot-release
source venv/bin/activate
python -m bot.main
```

---

## 🔔 Запуск с напоминаниями

Для работы напоминаний нужно запустить дополнительный процесс:

### Windows (два окна cmd):

**Окно 1 - Бот:**
```cmd
venv\Scripts\activate
python -m bot.main
```

**Окно 2 - Напоминания:**
```cmd
venv\Scripts\activate
python reminder_worker.py
```

### macOS / Linux (два терминала):

**Терминал 1:**
```bash
source venv/bin/activate
python -m bot.main
```

**Терминал 2:**
```bash
source venv/bin/activate
python reminder_worker.py
```

---

## ✅ Проверка работы

1. Откройте Telegram
2. Найдите бота: **@mytrener1_bot**
3. Отправьте `/start`
4. Пройдите настройку профиля
5. Попробуйте команды:
   - `/food` — добавить еду
   - `/water` — добавить воду
   - `/stats` — статистика

---

## 🛠️ Решение проблем

### "python не является внутренней командой" (Windows)

Python не добавлен в PATH. Решение:
1. Переустановите Python с галочкой "Add to PATH"
2. Или используйте полный путь: `C:\Users\ВашеИмя\AppData\Local\Programs\Python\Python311\python.exe`

### "No module named 'aiogram'"

Зависимости не установлены:
```bash
pip install -r requirements.txt
```

### "BOT_TOKEN required"

Файл `.env` не создан или токен не указан:
1. Скопируйте `.env.example` в `.env`
2. Откройте `.env` и добавьте токен

### Бот запускается но не отвечает

Проверьте:
1. Токен правильный
2. Интернет работает
3. В логах нет ошибок

---

## 📞 Информация о боте

- **Бот:** @mytrener1_bot
- **Токен:** `8237762701:AAG_8IG6XiTmSEt4ZdpkWd3vvFk1HkV1OeM`
- **Версия:** 1.3.0

---

## 📁 Структура проекта

```
fitness-telegram-bot-release/
├── bot/                 # Код бота
│   ├── handlers/        # Обработчики команд
│   ├── keyboards/       # Клавиатуры
│   └── main.py          # Точка входа
├── core/                # Модели базы данных
├── services/            # Бизнес-логика
├── data/foods.json      # База продуктов (330+)
├── reminder_worker.py   # Воркер напоминаний
├── requirements.txt     # Зависимости Python
├── .env.example         # Пример конфигурации
└── INSTALL.md           # Эта инструкция
```

---

*Удачи! 🏋️*
