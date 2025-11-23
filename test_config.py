#!/usr/bin/env python3
"""
Тестовый скрипт для проверки конфигурации AI Email Agent
Test script to validate AI Email Agent configuration
"""
import os
import sys
from pathlib import Path

# Добавление корневой директории в путь
sys.path.insert(0, str(Path(__file__).parent))

def print_header(text):
    print("\n" + "="*50)
    print(f"  {text}")
    print("="*50)

def print_check(name, status, details=""):
    symbol = "✓" if status else "✗"
    status_text = "OK" if status else "FAIL"
    print(f"{symbol} {name}: {status_text}")
    if details:
        print(f"  → {details}")

def test_python_version():
    """Проверка версии Python"""
    print_header("Проверка Python")
    
    major, minor = sys.version_info[:2]
    version_ok = major == 3 and minor >= 10
    
    print_check(
        "Python версия", 
        version_ok,
        f"Python {major}.{minor} {'(требуется 3.10+)' if not version_ok else ''}"
    )
    
    return version_ok

def test_env_file():
    """Проверка .env файла"""
    print_header("Проверка конфигурации")
    
    env_exists = Path(".env").exists()
    print_check(".env файл существует", env_exists)
    
    if not env_exists:
        print("  → Создайте .env файл: cp .env.example .env")
        return False
    
    # Загрузка переменных
    from dotenv import load_dotenv
    load_dotenv()
    
    required_vars = {
        "EMAIL_ADDRESS": "Email адрес",
        "EMAIL_PASSWORD": "Email пароль",
        "EMAIL_PROVIDER": "Email провайдер",
        "TELEGRAM_BOT_TOKEN": "Telegram токен бота",
        "TELEGRAM_CHAT_ID": "Telegram Chat ID",
    }
    
    all_ok = True
    for var, description in required_vars.items():
        value = os.getenv(var)
        is_set = value and value != f"your_{var.lower()}_here"
        print_check(f"{description} ({var})", is_set)
        if not is_set:
            all_ok = False
    
    # Проверка LLM провайдера
    llm_provider = os.getenv("LLM_PROVIDER", "openai")
    if llm_provider == "openai":
        openai_key = os.getenv("OPENAI_API_KEY")
        is_set = openai_key and not openai_key.startswith("sk-your")
        print_check("OpenAI API ключ", is_set)
        if not is_set:
            all_ok = False
    elif llm_provider == "anthropic":
        anthropic_key = os.getenv("ANTHROPIC_API_KEY")
        is_set = anthropic_key and not anthropic_key.startswith("sk-ant-your")
        print_check("Anthropic API ключ", is_set)
        if not is_set:
            all_ok = False
    
    return all_ok

def test_dependencies():
    """Проверка зависимостей"""
    print_header("Проверка зависимостей")
    
    dependencies = [
        ("dotenv", "python-dotenv"),
        ("imapclient", "IMAPClient"),
        ("telegram", "python-telegram-bot"),
        ("openai", "OpenAI"),
        ("sqlite3", "SQLite3 (встроенный)"),
    ]
    
    all_ok = True
    for module, name in dependencies:
        try:
            __import__(module)
            print_check(name, True)
        except ImportError:
            print_check(name, False, "Не установлен")
            all_ok = False
    
    return all_ok

def test_file_structure():
    """Проверка структуры файлов"""
    print_header("Проверка структуры проекта")
    
    required_files = [
        "main.py",
        "requirements.txt",
        ".env.example",
        "config/settings.py",
        "src/agent.py",
        "src/email_client/client.py",
        "src/llm_classifier/classifier.py",
        "src/rules_engine/database.py",
        "src/rules_engine/engine.py",
        "src/telegram_bot/bot.py",
    ]
    
    all_ok = True
    for file_path in required_files:
        exists = Path(file_path).exists()
        print_check(file_path, exists)
        if not exists:
            all_ok = False
    
    return all_ok

def test_directories():
    """Проверка и создание директорий"""
    print_header("Проверка директорий")
    
    directories = ["data", "logs"]
    
    for dir_name in directories:
        dir_path = Path(dir_name)
        exists = dir_path.exists()
        
        if not exists:
            try:
                dir_path.mkdir(parents=True, exist_ok=True)
                print_check(f"Директория {dir_name}", True, "Создана")
            except Exception as e:
                print_check(f"Директория {dir_name}", False, str(e))
        else:
            print_check(f"Директория {dir_name}", True, "Существует")
    
    return True

def test_email_connection():
    """Проверка подключения к почте"""
    print_header("Проверка подключения к почте")
    
    try:
        from config.settings import Config
        from src.email_client.client import EmailClient
        
        print("Попытка подключения к почтовому серверу...")
        print(f"Провайдер: {Config.EMAIL_PROVIDER}")
        print(f"Email: {Config.EMAIL_ADDRESS}")
        
        client = EmailClient()
        result = client.connect()
        
        if result:
            print_check("Подключение к почте", True, "Успешно")
            client.disconnect()
            return True
        else:
            print_check("Подключение к почте", False, "Не удалось подключиться")
            return False
            
    except Exception as e:
        print_check("Подключение к почте", False, str(e))
        return False

def test_telegram():
    """Проверка Telegram бота"""
    print_header("Проверка Telegram бота")
    
    try:
        from telegram import Bot
        from config.settings import Config
        
        print("Проверка Telegram бота...")
        
        bot = Bot(token=Config.TELEGRAM_BOT_TOKEN)
        me = bot.get_me()
        
        print_check("Telegram бот", True, f"@{me.username}")
        
        # Попытка отправить тестовое сообщение
        try:
            bot.send_message(
                chat_id=Config.TELEGRAM_CHAT_ID,
                text="✅ Тестовое сообщение от AI Email Agent"
            )
            print_check("Отправка сообщений", True, "Тестовое сообщение отправлено")
            return True
        except Exception as e:
            print_check("Отправка сообщений", False, str(e))
            return False
            
    except Exception as e:
        print_check("Telegram бот", False, str(e))
        return False

def main():
    """Основная функция"""
    print("""
╔══════════════════════════════════════════════════════╗
║                                                      ║
║    AI EMAIL AGENT - ПРОВЕРКА КОНФИГУРАЦИИ            ║
║    Configuration Test                                ║
║                                                      ║
╚══════════════════════════════════════════════════════╝
    """)
    
    results = {}
    
    # Базовые проверки
    results["Python"] = test_python_version()
    results["Структура"] = test_file_structure()
    results["Директории"] = test_directories()
    results["Зависимости"] = test_dependencies()
    results["Конфигурация"] = test_env_file()
    
    # Проверки подключений (только если базовые проверки прошли)
    if results["Конфигурация"] and results["Зависимости"]:
        results["Email"] = test_email_connection()
        results["Telegram"] = test_telegram()
    
    # Итоги
    print_header("ИТОГИ")
    
    passed = sum(1 for v in results.values() if v)
    total = len(results)
    
    print(f"\nПройдено: {passed}/{total}")
    
    if passed == total:
        print("\n✅ Все проверки пройдены! Агент готов к запуску.")
        print("\nЗапустите агента:")
        print("  python main.py")
        print("\nИли используйте start.sh:")
        print("  ./start.sh")
        return 0
    else:
        print("\n⚠️  Некоторые проверки не прошли.")
        print("\nИсправьте ошибки и запустите тест снова:")
        print("  python test_config.py")
        return 1

if __name__ == "__main__":
    sys.exit(main())
