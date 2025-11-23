"""
Клиент для работы с почтой через IMAP
Email client for IMAP operations
"""
import imaplib
import email
from email.header import decode_header
from typing import List, Dict, Optional, Tuple
from datetime import datetime
import ssl

from config.settings import Config
from src.utils.logger import logger
from src.utils.helpers import clean_text


class EmailClient:
    """Клиент для работы с почтовым ящиком"""
    
    def __init__(self):
        self.config = Config.get_imap_config()
        self.connection: Optional[imaplib.IMAP4_SSL] = None
        self.connected = False
    
    def connect(self) -> bool:
        """Подключение к почтовому серверу"""
        try:
            logger.info(f"Подключение к {self.config['server']}:{self.config['port']}")
            
            # Создание SSL контекста
            context = ssl.create_default_context()
            
            # Подключение к IMAP серверу
            self.connection = imaplib.IMAP4_SSL(
                self.config['server'],
                self.config['port'],
                ssl_context=context
            )
            
            # Аутентификация
            self.connection.login(self.config['email'], self.config['password'])
            self.connected = True
            
            logger.info("Успешное подключение к почтовому серверу")
            return True
            
        except Exception as e:
            logger.error(f"Ошибка подключения к почте: {e}")
            self.connected = False
            return False
    
    def disconnect(self):
        """Отключение от почтового сервера"""
        try:
            if self.connection and self.connected:
                self.connection.logout()
                self.connected = False
                logger.info("Отключение от почтового сервера")
        except Exception as e:
            logger.error(f"Ошибка при отключении: {e}")
    
    def get_folders(self) -> List[str]:
        """Получение списка папок"""
        try:
            if not self.connected:
                self.connect()
            
            status, folders = self.connection.list()
            folder_list = []
            
            for folder in folders:
                # Декодирование названия папки
                folder_name = folder.decode().split(' "/" ')[-1].strip('"')
                folder_list.append(folder_name)
            
            logger.info(f"Найдено папок: {len(folder_list)}")
            return folder_list
            
        except Exception as e:
            logger.error(f"Ошибка получения списка папок: {e}")
            return []
    
    def create_folder(self, folder_name: str) -> bool:
        """Создание новой папки"""
        try:
            if not self.connected:
                self.connect()
            
            status, response = self.connection.create(folder_name)
            
            if status == "OK":
                logger.info(f"Создана папка: {folder_name}")
                return True
            else:
                logger.warning(f"Не удалось создать папку {folder_name}: {response}")
                return False
                
        except Exception as e:
            logger.error(f"Ошибка создания папки: {e}")
            return False
    
    def select_folder(self, folder_name: str = "INBOX") -> bool:
        """Выбор папки для работы"""
        try:
            if not self.connected:
                self.connect()
            
            status, messages = self.connection.select(folder_name)
            
            if status == "OK":
                message_count = int(messages[0])
                logger.info(f"Выбрана папка '{folder_name}', писем: {message_count}")
                return True
            else:
                logger.warning(f"Не удалось выбрать папку: {folder_name}")
                return False
                
        except Exception as e:
            logger.error(f"Ошибка выбора папки: {e}")
            return False
    
    def fetch_emails(self, limit: int = 50, unseen_only: bool = True) -> List[Dict]:
        """
        Получение писем из текущей папки
        
        Args:
            limit: максимальное количество писем
            unseen_only: только непрочитанные письма
        """
        try:
            if not self.connected:
                self.connect()
            
            # Поиск писем
            search_criteria = "UNSEEN" if unseen_only else "ALL"
            status, message_ids = self.connection.search(None, search_criteria)
            
            if status != "OK":
                logger.warning("Не удалось получить список писем")
                return []
            
            # Список ID писем
            email_ids = message_ids[0].split()
            
            # Ограничение количества
            email_ids = email_ids[-limit:] if len(email_ids) > limit else email_ids
            
            logger.info(f"Найдено писем для обработки: {len(email_ids)}")
            
            emails = []
            for email_id in email_ids:
                email_data = self._fetch_email_by_id(email_id)
                if email_data:
                    emails.append(email_data)
            
            return emails
            
        except Exception as e:
            logger.error(f"Ошибка получения писем: {e}")
            return []
    
    def _fetch_email_by_id(self, email_id: bytes) -> Optional[Dict]:
        """Получение данных письма по ID"""
        try:
            status, msg_data = self.connection.fetch(email_id, "(RFC822)")
            
            if status != "OK":
                return None
            
            # Парсинг письма
            email_message = email.message_from_bytes(msg_data[0][1])
            
            # Извлечение основных данных
            subject = self._decode_header(email_message.get("Subject", ""))
            sender = self._decode_header(email_message.get("From", ""))
            date_str = email_message.get("Date", "")
            
            # Получение тела письма
            body = self._get_email_body(email_message)
            
            return {
                "id": email_id.decode(),
                "subject": subject,
                "sender": sender,
                "date": date_str,
                "body": clean_text(body),
                "raw": email_message
            }
            
        except Exception as e:
            logger.error(f"Ошибка парсинга письма {email_id}: {e}")
            return None
    
    def _decode_header(self, header: str) -> str:
        """Декодирование заголовка письма"""
        if not header:
            return ""
        
        decoded_parts = decode_header(header)
        decoded_header = ""
        
        for part, encoding in decoded_parts:
            if isinstance(part, bytes):
                decoded_header += part.decode(encoding or "utf-8", errors="ignore")
            else:
                decoded_header += part
        
        return decoded_header
    
    def _get_email_body(self, email_message) -> str:
        """Извлечение тела письма"""
        body = ""
        
        if email_message.is_multipart():
            for part in email_message.walk():
                content_type = part.get_content_type()
                content_disposition = str(part.get("Content-Disposition", ""))
                
                # Получение текстовой части
                if content_type == "text/plain" and "attachment" not in content_disposition:
                    try:
                        body = part.get_payload(decode=True).decode(errors="ignore")
                        break
                    except:
                        pass
        else:
            try:
                body = email_message.get_payload(decode=True).decode(errors="ignore")
            except:
                body = str(email_message.get_payload())
        
        return body
    
    def move_email(self, email_id: str, destination_folder: str) -> bool:
        """Перемещение письма в другую папку"""
        try:
            if not self.connected:
                self.connect()
            
            # Копирование письма в целевую папку
            status = self.connection.copy(email_id, destination_folder)
            
            if status[0] == "OK":
                # Пометка оригинального письма как удаленного
                self.connection.store(email_id, "+FLAGS", "\\Deleted")
                self.connection.expunge()
                
                logger.info(f"Письмо {email_id} перемещено в {destination_folder}")
                return True
            else:
                logger.warning(f"Не удалось переместить письмо {email_id}")
                return False
                
        except Exception as e:
            logger.error(f"Ошибка перемещения письма: {e}")
            return False
    
    def delete_email(self, email_id: str) -> bool:
        """Удаление письма"""
        try:
            if not self.connected:
                self.connect()
            
            # Пометка письма как удаленного
            self.connection.store(email_id, "+FLAGS", "\\Deleted")
            self.connection.expunge()
            
            logger.info(f"Письмо {email_id} удалено")
            return True
            
        except Exception as e:
            logger.error(f"Ошибка удаления письма: {e}")
            return False
    
    def mark_as_seen(self, email_id: str) -> bool:
        """Пометка письма как прочитанного"""
        try:
            if not self.connected:
                self.connect()
            
            self.connection.store(email_id, "+FLAGS", "\\Seen")
            logger.debug(f"Письмо {email_id} помечено как прочитанное")
            return True
            
        except Exception as e:
            logger.error(f"Ошибка пометки письма: {e}")
            return False
    
    def __enter__(self):
        """Context manager entry"""
        self.connect()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit"""
        self.disconnect()
