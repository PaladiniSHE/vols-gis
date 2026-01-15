#!/bin/bash

# ============================================
# Скрипт запуска бота "Личный тренер"
# ============================================

set -e

echo "🏋️ Личный тренер - Telegram Bot"
echo "================================"

# Проверка Python
if ! command -v python3 &> /dev/null; then
    echo "❌ Python3 не найден. Установите Python 3.11+"
    exit 1
fi

# Создание venv если не существует
if [ ! -d "venv" ]; then
    echo "📦 Создание виртуального окружения..."
    python3 -m venv venv
fi

# Активация venv
echo "🔄 Активация окружения..."
source venv/bin/activate

# Установка зависимостей
echo "📥 Проверка зависимостей..."
pip install -q --upgrade pip
pip install -q -r requirements.txt

# Проверка .env
if [ ! -f ".env" ]; then
    echo "⚠️  Файл .env не найден!"
    echo "📝 Создаю .env из примера..."
    cp .env.example .env
    echo ""
    echo "❗ ВАЖНО: Отредактируйте .env и укажите BOT_TOKEN"
    echo "   nano .env"
    echo ""
    exit 1
fi

# Проверка токена
if ! grep -q "BOT_TOKEN=." .env; then
    echo "❌ BOT_TOKEN не настроен в .env"
    exit 1
fi

echo ""
echo "✅ Всё готово!"
echo ""
echo "Выберите режим запуска:"
echo "1) Только бот (без напоминаний)"
echo "2) Бот + воркер напоминаний"
echo "3) Выход"
echo ""
read -p "Ваш выбор [1-3]: " choice

case $choice in
    1)
        echo ""
        echo "🚀 Запуск бота..."
        echo "   Для остановки нажмите Ctrl+C"
        echo ""
        python -m bot.main
        ;;
    2)
        echo ""
        echo "🚀 Запуск бота и воркера напоминаний..."
        echo "   Для остановки нажмите Ctrl+C"
        echo ""
        # Запуск воркера в фоне
        python reminder_worker.py &
        WORKER_PID=$!
        
        # Запуск бота
        python -m bot.main
        
        # Остановка воркера при выходе
        kill $WORKER_PID 2>/dev/null
        ;;
    3)
        echo "👋 До свидания!"
        exit 0
        ;;
    *)
        echo "❌ Неверный выбор"
        exit 1
        ;;
esac
