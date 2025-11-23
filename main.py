"""
Точка входа в приложение Email Agent
Entry point for Email Agent application
"""
import asyncio
import sys
import signal
from pathlib import Path

# Добавление корневой директории в путь
sys.path.insert(0, str(Path(__file__).parent))

from config.settings import Config
from src.agent import EmailAgent
from src.utils.logger import logger


def signal_handler(signum, frame):
    """Обработчик сигналов для graceful shutdown"""
    logger.info("Получен сигнал завершения, остановка агента...")
    sys.exit(0)


async def main():
    """Главная функция"""
    try:
        # Баннер
        print("""
╔══════════════════════════════════════════════════════╗
║                                                      ║
║          AI EMAIL AGENT                              ║
║          Intelligent Email Management System         ║
║                                                      ║
╚══════════════════════════════════════════════════════╝
        """)
        
        logger.info("Запуск AI Email Agent...")
        
        # Валидация конфигурации
        logger.info("Проверка конфигурации...")
        try:
            Config.validate()
            logger.info("✓ Конфигурация валидна")
        except ValueError as e:
            logger.error(f"✗ Ошибка конфигурации: {e}")
            print("\n❌ Ошибка конфигурации!")
            print(f"\n{e}")
            print("\nПожалуйста, проверьте файл .env")
            print("Используйте .env.example как шаблон")
            return 1
        
        # Вывод информации о настройках
        print(f"\n📧 Email провайдер: {Config.EMAIL_PROVIDER}")
        print(f"🤖 LLM провайдер: {Config.LLM_PROVIDER}")
        print(f"⏰ Интервал проверки: {Config.CHECK_INTERVAL_MINUTES} минут")
        print(f"📁 База данных: {Config.DATABASE_PATH}")
        print(f"📝 Лог файл: {Config.LOG_FILE}\n")
        
        # Создание и запуск агента
        agent = EmailAgent()
        
        # Регистрация обработчиков сигналов
        signal.signal(signal.SIGINT, signal_handler)
        signal.signal(signal.SIGTERM, signal_handler)
        
        try:
            await agent.start()
        except KeyboardInterrupt:
            logger.info("Получено прерывание с клавиатуры")
        finally:
            await agent.stop()
        
        logger.info("AI Email Agent завершил работу")
        return 0
        
    except Exception as e:
        logger.error(f"Критическая ошибка: {e}", exc_info=True)
        return 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
