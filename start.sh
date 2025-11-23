#!/bin/bash
# Скрипт быстрого запуска AI Email Agent
# Quick start script for AI Email Agent

set -e

echo "========================================"
echo "AI Email Agent - Quick Start"
echo "========================================"
echo ""

# Проверка Python
echo "Проверка Python..."
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 не найден. Установите Python 3.10 или выше."
    exit 1
fi

PYTHON_VERSION=$(python3 -c 'import sys; print(".".join(map(str, sys.version_info[:2])))')
echo "✓ Python $PYTHON_VERSION"

# Проверка виртуального окружения
if [ ! -d "venv" ]; then
    echo ""
    echo "Создание виртуального окружения..."
    python3 -m venv venv
    echo "✓ Виртуальное окружение создано"
fi

# Активация виртуального окружения
echo ""
echo "Активация виртуального окружения..."
source venv/bin/activate

# Установка зависимостей
echo ""
echo "Установка зависимостей..."
pip install --upgrade pip -q
pip install -r requirements.txt -q
echo "✓ Зависимости установлены"

# Проверка .env файла
echo ""
if [ ! -f ".env" ]; then
    echo "⚠️  Файл .env не найден!"
    echo "Создайте его на основе .env.example:"
    echo "  cp .env.example .env"
    echo ""
    echo "Затем отредактируйте .env и укажите:"
    echo "  - EMAIL_ADDRESS и EMAIL_PASSWORD"
    echo "  - OPENAI_API_KEY или ANTHROPIC_API_KEY"
    echo "  - TELEGRAM_BOT_TOKEN и TELEGRAM_CHAT_ID"
    echo ""
    read -p "Создать .env сейчас? (y/n) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        cp .env.example .env
        echo "✓ Создан файл .env"
        echo "⚠️  ВАЖНО: Отредактируйте .env перед запуском!"
        exit 0
    else
        exit 1
    fi
else
    echo "✓ Файл .env найден"
fi

# Создание директорий
mkdir -p data logs

echo ""
echo "========================================"
echo "Запуск AI Email Agent..."
echo "========================================"
echo ""

# Запуск агента
python main.py
