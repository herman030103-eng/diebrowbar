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


def encode_imap_folder_name(folder_name: str) -> str:
    """
    Кодирование имени папки в Modified UTF-7 (IMAP требует это для не-ASCII символов)
    Encode folder name to Modified UTF-7 (IMAP requires this for non-ASCII characters)
    """
    try:
        # Пробуем закодировать как ASCII - если получилось, используем как есть
        folder_name.encode('ascii')
        return folder_name
    except UnicodeEncodeError:
        # Если есть не-ASCII символы, кодируем в Modified UTF-7
        # Python's imaplib.utf7_encode() - это то, что нужно
        encoded = folder_name.encode('utf-7')
        # Modified UTF-7 для IMAP: заменяем '+' на '&' и добавляем '-' после кодированных частей
        modified = encoded.decode('ascii').replace('+', '&').replace('/', ',')
        return modified


def decode_imap_folder_name(folder_name: str) -> str:
    """
    Декодирование имени папки из Modified UTF-7
    Decode folder name from Modified UTF-7
    """
    try:
        # Если нет специальных символов, возвращаем как есть
        if '&' not in folder_name:
            return folder_name
        # Декодируем Modified UTF-7
        modified = folder_name.replace('&', '+').replace(',', '/')
        decoded = modified.encode('ascii').decode('utf-7')
        return decoded
    except:
        return folder_name


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
            
            # Кодируем имя папки в Modified UTF-7 для IMAP
            encoded_folder = encode_imap_folder_name(folder_name)
            logger.debug(f"Создание папки: '{folder_name}' -> encoded: '{encoded_folder}'")
            
            status, response = self.connection.create(encoded_folder)
            
            if status == "OK":
                logger.info(f"Создана папка: {folder_name}")
                return True
            else:
                logger.warning(f"Не удалось создать папку {folder_name}: {response}")
                return False
                
        except Exception as e:
            logger.error(f"Ошибка создания папки '{folder_name}': {e}")
            return False
    
    def select_folder(self, folder_name: str = "INBOX") -> bool:
        """Выбор папки для работы"""
        try:
            if not self.connected:
                self.connect()
            
            # Кодируем имя папки в Modified UTF-7 для IMAP
            encoded_folder = encode_imap_folder_name(folder_name)
            
            status, messages = self.connection.select(encoded_folder)
            
            if status == "OK":
                message_count = int(messages[0])
                logger.info(f"Выбрана папка '{folder_name}', писем: {message_count}")
                return True
            else:
                logger.warning(f"Не удалось выбрать папку: {folder_name}")
                return False
                
        except Exception as e:
            logger.error(f"Ошибка выбора папки '{folder_name}': {e}")
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
            
            # Преобразование email_id в bytes если это строка
            if isinstance(email_id, str):
                email_id_bytes = email_id.encode()
            else:
                email_id_bytes = email_id
            
            logger.debug(f"Попытка переместить письмо {email_id} в папку '{destination_folder}'")
            
            # Gmail система папок требует специальной обработки
            # Вместо перемещения в [Gmail]/All Mail, используем добавление лейбла
            if "[Gmail]" in destination_folder or destination_folder in ["[Gmail]/All Mail", "All Mail"]:
                # Для Gmail архивирования просто удаляем из Inbox и не удаляем письмо
                logger.info(f"Gmail архивирование: удаление из Inbox для письма {email_id}")
                try:
                    # Удаляем лейбл Inbox (это архивирование в Gmail)
                    self.connection.store(email_id_bytes, "-FLAGS", "\\Inbox")
                    logger.info(f"Письмо {email_id} заархивировано (удалено из Inbox)")
                    return True
                except:
                    # Если не получилось через лейблы, пробуем стандартный способ
                    pass
            
            # Кодируем имя папки в Modified UTF-7 для IMAP
            encoded_folder = encode_imap_folder_name(destination_folder)
            
            # Стандартное перемещение для обычных папок
            # Копирование письма в целевую папку
            status = self.connection.copy(email_id_bytes, encoded_folder)
            
            if status[0] == "OK":
                # Пометка оригинального письма как удаленного
                self.connection.store(email_id_bytes, "+FLAGS", "\\Deleted")
                self.connection.expunge()
                
                logger.info(f"Письмо {email_id} перемещено в {destination_folder}")
                return True
            else:
                logger.warning(f"Не удалось переместить письмо {email_id}: {status}")
                return False
                
        except Exception as e:
            logger.error(f"Ошибка перемещения письма {email_id} в '{destination_folder}': {e}")
            logger.debug(f"Email ID type: {type(email_id)}, Folder: '{destination_folder}'")
            return False
    
    def delete_email(self, email_id: str) -> bool:
        """Удаление письма"""
        try:
            if not self.connected:
                self.connect()
            
            # Преобразование email_id в bytes если это строка
            if isinstance(email_id, str):
                email_id_bytes = email_id.encode()
            else:
                email_id_bytes = email_id
            
            # Пометка письма как удаленного
            self.connection.store(email_id_bytes, "+FLAGS", "\\Deleted")
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
            
            # Преобразование email_id в bytes если это строка
            if isinstance(email_id, str):
                email_id_bytes = email_id.encode()
            else:
                email_id_bytes = email_id
            
            self.connection.store(email_id_bytes, "+FLAGS", "\\Seen")
            logger.debug(f"Письмо {email_id} помечено как прочитанное")
            return True
            
        except Exception as e:
            logger.error(f"Ошибка пометки письма: {e}")
            return False
    
    def archive_email(self, email_id: str) -> bool:
        """Архивирование письма (Gmail-совместимо)"""
        try:
            if not self.connected:
                self.connect()
            
            # Преобразование email_id в bytes если это строка
            if isinstance(email_id, str):
                email_id_bytes = email_id.encode()
            else:
                email_id_bytes = email_id
            
            # Для Gmail архивирование = удаление из Inbox
            # Письмо остается в All Mail автоматически
            logger.debug(f"Архивирование письма {email_id}")
            
            # Удаляем из текущей папки (обычно Inbox)
            self.connection.store(email_id_bytes, "+FLAGS", "\\Deleted")
            self.connection.expunge()
            
            logger.info(f"Письмо {email_id} заархивировано")
            return True
            
        except Exception as e:
            logger.error(f"Ошибка архивирования письма: {e}")
            return False
    
    def __enter__(self):
        """Context manager entry"""
        self.connect()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit"""
        self.disconnect()
