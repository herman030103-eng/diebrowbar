"""
Главный модуль AI Email Agent
Main AI Email Agent module
"""
import asyncio
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import json

from config.settings import Config
from src.email_client.client import EmailClient
from src.llm_classifier.classifier import EmailClassifier
from src.rules_engine.database import Database
from src.rules_engine.engine import RulesEngine
from src.telegram_bot.bot import TelegramBot
from src.utils.logger import logger
from src.utils.helpers import generate_email_id


class EmailAgent:
    """Главный класс AI Email Agent"""
    
    def __init__(self):
        logger.info("Инициализация Email Agent...")
        
        # Компоненты
        self.email_client = EmailClient()
        self.classifier = EmailClassifier()
        self.database = Database()
        self.rules_engine = RulesEngine(self.database)
        self.telegram_bot = TelegramBot(agent_reference=self)
        
        # Статус
        self.is_running = False
        self.last_check_time: Optional[datetime] = None
        self.stats = {
            "total_processed": 0,
            "total_deleted": 0,
            "total_moved": 0,
            "total_archived": 0
        }
        
        logger.info("Email Agent инициализирован")
    
    async def start(self):
        """Запуск агента"""
        try:
            logger.info("Запуск Email Agent...")
            self.is_running = True
            
            # Отправка уведомления о старте
            await self.telegram_bot.send_notification(
                "Email Agent запущен",
                f"Агент начал работу. Интервал проверки: {Config.CHECK_INTERVAL_MINUTES} мин."
            )
            
            # Запуск Telegram бота
            await self.telegram_bot.start_polling()
            
            # Основной цикл проверки почты
            await self._main_loop()
            
        except Exception as e:
            logger.error(f"Критическая ошибка агента: {e}")
            await self.telegram_bot.notify_error(f"Критическая ошибка: {e}")
            raise
    
    async def stop(self):
        """Остановка агента"""
        logger.info("Остановка Email Agent...")
        self.is_running = False
        
        # Остановка Telegram бота
        await self.telegram_bot.stop_polling()
        
        # Закрытие соединения с почтой
        self.email_client.disconnect()
        
        logger.info("Email Agent остановлен")
    
    async def _main_loop(self):
        """Основной цикл проверки почты"""
        while self.is_running:
            try:
                logger.info("Начало проверки почты...")
                
                # Проверка и обработка писем
                result = await self._check_and_process_emails()
                
                # Обновление времени последней проверки
                self.last_check_time = datetime.now()
                
                # Отправка сводки если были обработаны письма
                if result["processed"] > 0:
                    await self.telegram_bot.notify_summary(result)
                
                # Обновление статистики
                today = datetime.now().strftime("%Y-%m-%d")
                self.database.update_statistics(
                    date=today,
                    processed=result["processed"],
                    deleted=result["deleted"],
                    archived=result["archived"],
                    moved=result["moved"],
                    by_category=json.dumps(result.get("by_category", {}))
                )
                
                logger.info(f"Проверка завершена. Ожидание {Config.CHECK_INTERVAL_MINUTES} мин...")
                
                # Ожидание до следующей проверки
                await asyncio.sleep(Config.CHECK_INTERVAL_MINUTES * 60)
                
            except Exception as e:
                logger.error(f"Ошибка в главном цикле: {e}")
                await self.telegram_bot.notify_error(f"Ошибка обработки: {e}")
                # Ожидание перед повторной попыткой
                await asyncio.sleep(60)
    
    async def _check_and_process_emails(self) -> Dict:
        """Проверка и обработка новых писем"""
        result = {
            "processed": 0,
            "deleted": 0,
            "moved": 0,
            "archived": 0,
            "by_category": {}
        }
        
        try:
            # Подключение к почте
            if not self.email_client.connect():
                logger.error("Не удалось подключиться к почте")
                return result
            
            # Выбор папки Inbox
            if not self.email_client.select_folder("INBOX"):
                logger.error("Не удалось выбрать папку INBOX")
                return result
            
            # Получение новых писем
            emails = self.email_client.fetch_emails(
                limit=Config.MAX_EMAILS_PER_CHECK,
                unseen_only=True
            )
            
            logger.info(f"Получено писем для обработки: {len(emails)}")
            
            # Обработка каждого письма
            for email_data in emails:
                try:
                    processed = await self._process_single_email(email_data)
                    
                    if processed:
                        result["processed"] += 1
                        
                        # Подсчет по категориям
                        category = processed.get("category", "UNKNOWN")
                        result["by_category"][category] = result["by_category"].get(category, 0) + 1
                        
                        # Подсчет действий
                        action = processed.get("action", "none")
                        if action == "delete":
                            result["deleted"] += 1
                        elif action == "move":
                            result["moved"] += 1
                        elif action == "archive":
                            result["archived"] += 1
                        
                except Exception as e:
                    logger.error(f"Ошибка обработки письма: {e}")
                    continue
            
            # Обновление статистики
            self.stats["total_processed"] += result["processed"]
            self.stats["total_deleted"] += result["deleted"]
            self.stats["total_moved"] += result["moved"]
            self.stats["total_archived"] += result["archived"]
            
            return result
            
        except Exception as e:
            logger.error(f"Ошибка проверки писем: {e}")
            return result
        finally:
            self.email_client.disconnect()
    
    async def _process_single_email(self, email_data: Dict) -> Optional[Dict]:
        """Обработка одного письма"""
        try:
            subject = email_data.get("subject", "")
            sender = email_data.get("sender", "")
            email_id = email_data.get("id")
            
            logger.info(f"Обработка письма: {subject[:50]}... от {sender[:50]}")
            
            # Проверка на дубликат
            unique_id = generate_email_id(subject, sender, email_data.get("date", ""))
            if self.database.is_email_processed(unique_id):
                logger.info(f"Письмо уже обработано: {unique_id}")
                return None
            
            # Классификация письма через LLM
            classification = self.classifier.classify_email(email_data)
            
            # Применение пользовательских правил
            rules_result = self.rules_engine.apply_rules(email_data, classification)
            
            # Определение финального действия
            final_action = rules_result.get("action", "none")
            destination_folder = rules_result.get("destination")
            
            # Если правила не определили действие, используем рекомендации классификатора
            if final_action == "none":
                if classification.get("should_delete", False) and Config.ENABLE_AUTO_DELETE:
                    final_action = "delete"
                elif classification.get("should_archive", False) and Config.ENABLE_AUTO_ARCHIVE:
                    final_action = "archive"
                elif Config.ENABLE_AUTO_CATEGORIZE:
                    # Автоматическое перемещение по категории
                    # Используем suggested_folder от LLM или имя категории
                    category = classification.get("category", "UNKNOWN")
                    suggested_folder = classification.get("suggested_folder")
                    
                    # Определяем папку назначения
                    if suggested_folder:
                        destination_folder = suggested_folder
                    else:
                        # Используем название категории как имя папки
                        destination_folder = category
                    
                    # Не перемещаем SPAM в отдельную папку, если не удаляем
                    if category == "SPAM" and not Config.ENABLE_AUTO_DELETE:
                        # SPAM перемещаем в папку Spam
                        destination_folder = "Spam"
                    
                    final_action = "move"
                    from_cache = " (из кэша)" if classification.get("from_cache", False) else ""
                    logger.info(f"Автокатегоризация: {destination_folder} (категория: {category}, confidence: {classification.get('confidence', 0):.2f}){from_cache}")
            
            # Выполнение действия
            action_success = await self._execute_action(
                email_id, final_action, destination_folder
            )
            
            # Сохранение в базу данных
            self.database.add_processed_email(
                email_id=unique_id,
                subject=subject,
                sender=sender,
                category=classification.get("category", "UNKNOWN"),
                confidence=classification.get("confidence", 0.0),
                folder=destination_folder or "INBOX",
                action=final_action
            )
            
            # Логирование действия
            self.database.log_action(
                email_id=unique_id,
                action_type=final_action,
                action_details=f"Destination: {destination_folder}, Rules: {rules_result.get('reasoning')}",
                status="success" if action_success else "failed"
            )
            
            # Отправка уведомления
            if classification.get("priority") == "high" or final_action in ["delete", "move"]:
                await self.telegram_bot.notify_email_processed(
                    email_data, classification, final_action
                )
            
            return {
                "email_id": unique_id,
                "category": classification.get("category"),
                "action": final_action,
                "destination": destination_folder
            }
            
        except Exception as e:
            logger.error(f"Ошибка обработки письма: {e}")
            return None
    
    async def _execute_action(self, email_id: str, action: str, destination: Optional[str]) -> bool:
        """Выполнение действия с письмом"""
        try:
            if action == "delete":
                return self.email_client.delete_email(email_id)
            
            elif action == "move" and destination:
                # Создание папки если не существует
                folders = self.email_client.get_folders()
                if destination not in folders:
                    self.email_client.create_folder(destination)
                
                return self.email_client.move_email(email_id, destination)
            
            elif action == "archive":
                # Архивирование (Gmail-совместимое)
                return self.email_client.archive_email(email_id)
            
            elif action == "skip":
                logger.info("Пропуск обработки письма (правило skip)")
                return True
            
            else:
                # Пометка как прочитанное
                return self.email_client.mark_as_seen(email_id)
            
        except Exception as e:
            logger.error(f"Ошибка выполнения действия {action}: {e}")
            return False
    
    # === Методы для Telegram бота ===
    
    def get_status(self) -> Dict:
        """Получение статуса агента"""
        return {
            "running": self.is_running,
            "last_check": self.last_check_time.strftime("%Y-%m-%d %H:%M:%S") if self.last_check_time else "Никогда",
            "total_processed": self.stats["total_processed"],
            "active_rules": len(self.database.get_all_rules(enabled_only=True))
        }
    
    def get_statistics(self) -> Dict:
        """Получение статистики"""
        today = datetime.now().strftime("%Y-%m-%d")
        week_ago = (datetime.now() - timedelta(days=7)).strftime("%Y-%m-%d")
        
        stats_data = self.database.get_statistics(days=7)
        
        today_stats = next((s for s in stats_data if s["date"] == today), {})
        week_total = {
            "processed": sum(s.get("total_processed", 0) for s in stats_data),
            "deleted": sum(s.get("total_deleted", 0) for s in stats_data),
            "moved": sum(s.get("total_moved", 0) for s in stats_data)
        }
        
        return {
            "today_processed": today_stats.get("total_processed", 0),
            "today_deleted": today_stats.get("total_deleted", 0),
            "today_moved": today_stats.get("total_moved", 0),
            "week_processed": week_total["processed"],
            "week_deleted": week_total["deleted"],
            "week_moved": week_total["moved"]
        }
    
    def get_rules_summary(self) -> str:
        """Получение списка правил"""
        return self.rules_engine.get_rules_summary()
    
    def create_rule_from_text(self, text: str) -> Optional[int]:
        """Создание правила из текста"""
        return self.rules_engine.create_rule_from_command(text)
    
    def delete_rule(self, rule_id: int) -> bool:
        """Удаление правила"""
        return self.database.delete_rule(rule_id)
    
    def check_emails_now(self) -> Dict:
        """Принудительная проверка почты"""
        loop = asyncio.get_event_loop()
        return loop.run_until_complete(self._check_and_process_emails())
    
    def get_last_processed_emails(self, limit: int = 10) -> List[Dict]:
        """Получение последних обработанных писем"""
        return self.database.get_processed_emails(limit=limit)
