"""
База данных для хранения правил и истории
Database for storing rules and history
"""
import sqlite3
from typing import List, Dict, Optional, Tuple
from datetime import datetime
from pathlib import Path

from config.settings import Config
from src.utils.logger import logger


class Database:
    """Класс для работы с SQLite базой данных"""
    
    def __init__(self, db_path: Optional[str] = None):
        self.db_path = db_path or Config.DATABASE_PATH
        self._ensure_db_exists()
        self._init_tables()
    
    def _ensure_db_exists(self):
        """Создание директории для БД если не существует"""
        db_file = Path(self.db_path)
        db_file.parent.mkdir(parents=True, exist_ok=True)
    
    def _get_connection(self) -> sqlite3.Connection:
        """Получение подключения к БД"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn
    
    def _init_tables(self):
        """Инициализация таблиц БД"""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        # Таблица правил
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS rules (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                rule_type TEXT NOT NULL,
                condition_field TEXT NOT NULL,
                condition_operator TEXT NOT NULL,
                condition_value TEXT NOT NULL,
                action_type TEXT NOT NULL,
                action_value TEXT,
                priority INTEGER DEFAULT 0,
                enabled BOOLEAN DEFAULT 1,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Таблица обработанных писем
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS processed_emails (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                email_id TEXT UNIQUE NOT NULL,
                subject TEXT,
                sender TEXT,
                category TEXT,
                confidence REAL,
                folder TEXT,
                action TEXT,
                processed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Таблица логов действий
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS action_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                email_id TEXT,
                action_type TEXT NOT NULL,
                action_details TEXT,
                status TEXT,
                error_message TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Таблица статистики
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS statistics (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                date DATE NOT NULL,
                total_processed INTEGER DEFAULT 0,
                total_deleted INTEGER DEFAULT 0,
                total_archived INTEGER DEFAULT 0,
                total_moved INTEGER DEFAULT 0,
                by_category TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(date)
            )
        """)
        
        conn.commit()
        conn.close()
        
        logger.info("База данных инициализирована")
    
    # === Работа с правилами ===
    
    def add_rule(self, rule_type: str, condition_field: str, condition_operator: str,
                 condition_value: str, action_type: str, action_value: str = None,
                 priority: int = 0) -> int:
        """Добавление нового правила"""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT INTO rules (rule_type, condition_field, condition_operator, 
                             condition_value, action_type, action_value, priority)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (rule_type, condition_field, condition_operator, condition_value,
              action_type, action_value, priority))
        
        rule_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        logger.info(f"Добавлено правило ID {rule_id}: {action_type} когда {condition_field} {condition_operator} {condition_value}")
        return rule_id
    
    def get_all_rules(self, enabled_only: bool = True) -> List[Dict]:
        """Получение всех правил"""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        query = "SELECT * FROM rules"
        if enabled_only:
            query += " WHERE enabled = 1"
        query += " ORDER BY priority DESC, id ASC"
        
        cursor.execute(query)
        rows = cursor.fetchall()
        conn.close()
        
        return [dict(row) for row in rows]
    
    def get_rule(self, rule_id: int) -> Optional[Dict]:
        """Получение правила по ID"""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        cursor.execute("SELECT * FROM rules WHERE id = ?", (rule_id,))
        row = cursor.fetchone()
        conn.close()
        
        return dict(row) if row else None
    
    def update_rule(self, rule_id: int, **kwargs) -> bool:
        """Обновление правила"""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        # Динамическое формирование UPDATE запроса
        fields = []
        values = []
        for key, value in kwargs.items():
            fields.append(f"{key} = ?")
            values.append(value)
        
        if not fields:
            return False
        
        values.append(rule_id)
        query = f"UPDATE rules SET {', '.join(fields)}, updated_at = CURRENT_TIMESTAMP WHERE id = ?"
        
        cursor.execute(query, values)
        conn.commit()
        affected = cursor.rowcount
        conn.close()
        
        logger.info(f"Обновлено правило ID {rule_id}")
        return affected > 0
    
    def delete_rule(self, rule_id: int) -> bool:
        """Удаление правила"""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        cursor.execute("DELETE FROM rules WHERE id = ?", (rule_id,))
        conn.commit()
        affected = cursor.rowcount
        conn.close()
        
        logger.info(f"Удалено правило ID {rule_id}")
        return affected > 0
    
    def toggle_rule(self, rule_id: int, enabled: bool) -> bool:
        """Включение/выключение правила"""
        return self.update_rule(rule_id, enabled=1 if enabled else 0)
    
    # === Работа с обработанными письмами ===
    
    def is_email_processed(self, email_id: str) -> bool:
        """Проверка, было ли письмо уже обработано"""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        cursor.execute("SELECT 1 FROM processed_emails WHERE email_id = ?", (email_id,))
        result = cursor.fetchone()
        conn.close()
        
        return result is not None
    
    def add_processed_email(self, email_id: str, subject: str, sender: str,
                           category: str, confidence: float, folder: str, action: str):
        """Добавление обработанного письма"""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT OR REPLACE INTO processed_emails 
            (email_id, subject, sender, category, confidence, folder, action)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (email_id, subject, sender, category, confidence, folder, action))
        
        conn.commit()
        conn.close()
    
    def get_processed_emails(self, limit: int = 100, offset: int = 0) -> List[Dict]:
        """Получение списка обработанных писем"""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT * FROM processed_emails 
            ORDER BY processed_at DESC 
            LIMIT ? OFFSET ?
        """, (limit, offset))
        
        rows = cursor.fetchall()
        conn.close()
        
        return [dict(row) for row in rows]
    
    def get_emails_by_sender(self, sender: str, limit: int = 50) -> List[Dict]:
        """Получение писем от конкретного отправителя"""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT * FROM processed_emails 
            WHERE sender LIKE ?
            ORDER BY processed_at DESC 
            LIMIT ?
        """, (f"%{sender}%", limit))
        
        rows = cursor.fetchall()
        conn.close()
        
        return [dict(row) for row in rows]
    
    # === Логирование действий ===
    
    def log_action(self, email_id: str, action_type: str, action_details: str = None,
                   status: str = "success", error_message: str = None):
        """Логирование действия"""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT INTO action_logs (email_id, action_type, action_details, status, error_message)
            VALUES (?, ?, ?, ?, ?)
        """, (email_id, action_type, action_details, status, error_message))
        
        conn.commit()
        conn.close()
    
    def get_action_logs(self, limit: int = 100) -> List[Dict]:
        """Получение логов действий"""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT * FROM action_logs 
            ORDER BY created_at DESC 
            LIMIT ?
        """, (limit,))
        
        rows = cursor.fetchall()
        conn.close()
        
        return [dict(row) for row in rows]
    
    # === Статистика ===
    
    def update_statistics(self, date: str, processed: int = 0, deleted: int = 0,
                         archived: int = 0, moved: int = 0, by_category: str = None):
        """Обновление статистики"""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT INTO statistics (date, total_processed, total_deleted, 
                                   total_archived, total_moved, by_category)
            VALUES (?, ?, ?, ?, ?, ?)
            ON CONFLICT(date) DO UPDATE SET
                total_processed = total_processed + excluded.total_processed,
                total_deleted = total_deleted + excluded.total_deleted,
                total_archived = total_archived + excluded.total_archived,
                total_moved = total_moved + excluded.total_moved,
                by_category = excluded.by_category
        """, (date, processed, deleted, archived, moved, by_category))
        
        conn.commit()
        conn.close()
    
    def get_statistics(self, days: int = 30) -> List[Dict]:
        """Получение статистики за последние N дней"""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT * FROM statistics 
            WHERE date >= date('now', '-' || ? || ' days')
            ORDER BY date DESC
        """, (days,))
        
        rows = cursor.fetchall()
        conn.close()
        
        return [dict(row) for row in rows]
