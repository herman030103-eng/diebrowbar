"""
Модуль конфигурации для AI Email Agent
Configuration module for AI Email Agent
"""
import os
from typing import Optional
from pathlib import Path
from dotenv import load_dotenv

# Загрузка переменных окружения / Load environment variables
load_dotenv()

class Config:
    """Конфигурация приложения / Application configuration"""
    
    # Базовые пути / Base paths
    BASE_DIR = Path(__file__).resolve().parent.parent
    DATA_DIR = BASE_DIR / "data"
    LOGS_DIR = BASE_DIR / "logs"
    
    # Email настройки / Email settings
    EMAIL_PROVIDER = os.getenv("EMAIL_PROVIDER", "gmail")
    EMAIL_ADDRESS = os.getenv("EMAIL_ADDRESS")
    EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD")
    
    # Gmail
    GMAIL_IMAP_SERVER = os.getenv("GMAIL_IMAP_SERVER", "imap.gmail.com")
    GMAIL_IMAP_PORT = int(os.getenv("GMAIL_IMAP_PORT", "993"))
    GMAIL_SMTP_SERVER = os.getenv("GMAIL_SMTP_SERVER", "smtp.gmail.com")
    GMAIL_SMTP_PORT = int(os.getenv("GMAIL_SMTP_PORT", "587"))
    
    # Yandex
    YANDEX_IMAP_SERVER = os.getenv("YANDEX_IMAP_SERVER", "imap.yandex.ru")
    YANDEX_IMAP_PORT = int(os.getenv("YANDEX_IMAP_PORT", "993"))
    YANDEX_SMTP_SERVER = os.getenv("YANDEX_SMTP_SERVER", "smtp.yandex.ru")
    YANDEX_SMTP_PORT = int(os.getenv("YANDEX_SMTP_PORT", "587"))
    
    # Outlook
    OUTLOOK_IMAP_SERVER = os.getenv("OUTLOOK_IMAP_SERVER", "outlook.office365.com")
    OUTLOOK_IMAP_PORT = int(os.getenv("OUTLOOK_IMAP_PORT", "993"))
    OUTLOOK_SMTP_SERVER = os.getenv("OUTLOOK_SMTP_SERVER", "smtp.office365.com")
    OUTLOOK_SMTP_PORT = int(os.getenv("OUTLOOK_SMTP_PORT", "587"))
    
    # LLM настройки / LLM settings
    LLM_PROVIDER = os.getenv("LLM_PROVIDER", "ollama")
    
    # OpenAI
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
    OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4-turbo-preview")
    OPENAI_MAX_TOKENS = int(os.getenv("OPENAI_MAX_TOKENS", "1000"))
    OPENAI_TEMPERATURE = float(os.getenv("OPENAI_TEMPERATURE", "0.3"))
    
    # Anthropic
    ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")
    ANTHROPIC_MODEL = os.getenv("ANTHROPIC_MODEL", "claude-3-sonnet-20240229")
    ANTHROPIC_MAX_TOKENS = int(os.getenv("ANTHROPIC_MAX_TOKENS", "1000"))
    
    # Perplexity
    PERPLEXITY_API_KEY = os.getenv("PERPLEXITY_API_KEY")
    PERPLEXITY_MODEL = os.getenv("PERPLEXITY_MODEL", "llama-3.1-sonar-small-128k-online")
    PERPLEXITY_MAX_TOKENS = int(os.getenv("PERPLEXITY_MAX_TOKENS", "1000"))
    PERPLEXITY_TEMPERATURE = float(os.getenv("PERPLEXITY_TEMPERATURE", "0.3"))
    
    # Ollama (бесплатно, локально)
    OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
    OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "llama3.2")
    OLLAMA_MAX_TOKENS = int(os.getenv("OLLAMA_MAX_TOKENS", "1000"))
    OLLAMA_TEMPERATURE = float(os.getenv("OLLAMA_TEMPERATURE", "0.3"))
    
    # Hugging Face
    HUGGINGFACE_API_KEY = os.getenv("HUGGINGFACE_API_KEY")
    HUGGINGFACE_MODEL = os.getenv("HUGGINGFACE_MODEL", "mistralai/Mistral-7B-Instruct-v0.2")
    HUGGINGFACE_MAX_TOKENS = int(os.getenv("HUGGINGFACE_MAX_TOKENS", "1000"))
    
    # Telegram настройки / Telegram settings
    TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
    TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")
    
    # Agent настройки / Agent settings
    CHECK_INTERVAL_MINUTES = int(os.getenv("CHECK_INTERVAL_MINUTES", "5"))
    MAX_EMAILS_PER_CHECK = int(os.getenv("MAX_EMAILS_PER_CHECK", "50"))
    ENABLE_AUTO_DELETE = os.getenv("ENABLE_AUTO_DELETE", "false").lower() == "true"
    ENABLE_AUTO_ARCHIVE = os.getenv("ENABLE_AUTO_ARCHIVE", "true").lower() == "true"
    
    # База данных / Database
    DATABASE_PATH = os.getenv("DATABASE_PATH", str(DATA_DIR / "email_agent.db"))
    
    # Логирование / Logging
    LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
    LOG_FILE = os.getenv("LOG_FILE", str(LOGS_DIR / "email_agent.log"))
    LOG_MAX_BYTES = int(os.getenv("LOG_MAX_BYTES", "10485760"))
    LOG_BACKUP_COUNT = int(os.getenv("LOG_BACKUP_COUNT", "5"))
    
    # Дополнительные настройки / Additional settings
    LANGUAGE = os.getenv("LANGUAGE", "ru")
    TIMEZONE = os.getenv("TIMEZONE", "Europe/Moscow")
    
    @classmethod
    def get_imap_config(cls):
        """Получить IMAP конфигурацию для выбранного провайдера"""
        provider = cls.EMAIL_PROVIDER.lower()
        if provider == "gmail":
            return {
                "server": cls.GMAIL_IMAP_SERVER,
                "port": cls.GMAIL_IMAP_PORT,
                "email": cls.EMAIL_ADDRESS,
                "password": cls.EMAIL_PASSWORD
            }
        elif provider == "yandex":
            return {
                "server": cls.YANDEX_IMAP_SERVER,
                "port": cls.YANDEX_IMAP_PORT,
                "email": cls.EMAIL_ADDRESS,
                "password": cls.EMAIL_PASSWORD
            }
        elif provider == "outlook":
            return {
                "server": cls.OUTLOOK_IMAP_SERVER,
                "port": cls.OUTLOOK_IMAP_PORT,
                "email": cls.EMAIL_ADDRESS,
                "password": cls.EMAIL_PASSWORD
            }
        else:
            raise ValueError(f"Неподдерживаемый провайдер: {provider}")
    
    @classmethod
    def get_smtp_config(cls):
        """Получить SMTP конфигурацию для выбранного провайдера"""
        provider = cls.EMAIL_PROVIDER.lower()
        if provider == "gmail":
            return {
                "server": cls.GMAIL_SMTP_SERVER,
                "port": cls.GMAIL_SMTP_PORT,
                "email": cls.EMAIL_ADDRESS,
                "password": cls.EMAIL_PASSWORD
            }
        elif provider == "yandex":
            return {
                "server": cls.YANDEX_SMTP_SERVER,
                "port": cls.YANDEX_SMTP_PORT,
                "email": cls.EMAIL_ADDRESS,
                "password": cls.EMAIL_PASSWORD
            }
        elif provider == "outlook":
            return {
                "server": cls.OUTLOOK_SMTP_SERVER,
                "port": cls.OUTLOOK_SMTP_PORT,
                "email": cls.EMAIL_ADDRESS,
                "password": cls.EMAIL_PASSWORD
            }
        else:
            raise ValueError(f"Неподдерживаемый провайдер: {provider}")
    
    @classmethod
    def validate(cls):
        """Валидация конфигурации"""
        errors = []
        
        if not cls.EMAIL_ADDRESS:
            errors.append("EMAIL_ADDRESS не установлен")
        if not cls.EMAIL_PASSWORD:
            errors.append("EMAIL_PASSWORD не установлен")
        
        if cls.LLM_PROVIDER == "openai" and not cls.OPENAI_API_KEY:
            errors.append("OPENAI_API_KEY не установлен")
        elif cls.LLM_PROVIDER == "anthropic" and not cls.ANTHROPIC_API_KEY:
            errors.append("ANTHROPIC_API_KEY не установлен")
        elif cls.LLM_PROVIDER == "perplexity" and not cls.PERPLEXITY_API_KEY:
            errors.append("PERPLEXITY_API_KEY не установлен")
        elif cls.LLM_PROVIDER == "huggingface" and not cls.HUGGINGFACE_API_KEY:
            errors.append("HUGGINGFACE_API_KEY не установлен")
        elif cls.LLM_PROVIDER == "ollama":
            # Ollama не требует API ключа, но предупредим если не запущен
            pass
        
        if not cls.TELEGRAM_BOT_TOKEN:
            errors.append("TELEGRAM_BOT_TOKEN не установлен")
        if not cls.TELEGRAM_CHAT_ID:
            errors.append("TELEGRAM_CHAT_ID не установлен")
        
        if errors:
            raise ValueError("Ошибки конфигурации:\n" + "\n".join(f"- {e}" for e in errors))
        
        # Создание необходимых директорий
        cls.DATA_DIR.mkdir(parents=True, exist_ok=True)
        cls.LOGS_DIR.mkdir(parents=True, exist_ok=True)
        
        return True
