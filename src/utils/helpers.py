"""
Вспомогательные утилиты
Helper utilities
"""
import hashlib
from datetime import datetime
from typing import Optional

def generate_email_id(subject: str, sender: str, date: str) -> str:
    """
    Генерация уникального ID для письма для предотвращения дубликатов
    Generate unique ID for email to prevent duplicates
    """
    content = f"{subject}|{sender}|{date}"
    return hashlib.md5(content.encode()).hexdigest()

def clean_text(text: str, max_length: int = 5000) -> str:
    """
    Очистка и обрезка текста
    Clean and truncate text
    """
    if not text:
        return ""
    
    # Удаление лишних пробелов и переносов
    text = " ".join(text.split())
    
    # Обрезка до максимальной длины
    if len(text) > max_length:
        text = text[:max_length] + "..."
    
    return text

def format_date(date_obj: Optional[datetime]) -> str:
    """
    Форматирование даты для отображения
    Format date for display
    """
    if not date_obj:
        return "Неизвестно"
    
    return date_obj.strftime("%Y-%m-%d %H:%M:%S")

def truncate_text(text: str, length: int = 100) -> str:
    """
    Обрезка текста с добавлением многоточия
    Truncate text with ellipsis
    """
    if len(text) <= length:
        return text
    return text[:length] + "..."
