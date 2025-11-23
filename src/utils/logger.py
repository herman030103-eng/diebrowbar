"""
Модуль логирования для AI Email Agent
Logging module for AI Email Agent
"""
import logging
import sys
from logging.handlers import RotatingFileHandler
from pathlib import Path
from config.settings import Config

def setup_logger(name: str = "email_agent") -> logging.Logger:
    """
    Настройка логгера с цветным выводом в консоль и записью в файл
    Setup logger with colored console output and file logging
    """
    logger = logging.getLogger(name)
    logger.setLevel(getattr(logging, Config.LOG_LEVEL.upper()))
    
    # Очистка существующих обработчиков
    logger.handlers.clear()
    
    # Формат логов
    log_format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    date_format = '%Y-%m-%d %H:%M:%S'
    
    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.DEBUG)
    console_formatter = logging.Formatter(log_format, date_format)
    console_handler.setFormatter(console_formatter)
    logger.addHandler(console_handler)
    
    # File handler
    try:
        log_file = Path(Config.LOG_FILE)
        log_file.parent.mkdir(parents=True, exist_ok=True)
        
        file_handler = RotatingFileHandler(
            Config.LOG_FILE,
            maxBytes=Config.LOG_MAX_BYTES,
            backupCount=Config.LOG_BACKUP_COUNT,
            encoding='utf-8'
        )
        file_handler.setLevel(logging.DEBUG)
        file_formatter = logging.Formatter(log_format, date_format)
        file_handler.setFormatter(file_formatter)
        logger.addHandler(file_handler)
    except Exception as e:
        logger.error(f"Не удалось создать файл лога: {e}")
    
    return logger

# Создание основного логгера
logger = setup_logger()
