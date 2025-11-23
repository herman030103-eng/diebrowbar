"""
Telegram бот для управления агентом и уведомлений
Telegram bot for agent management and notifications
"""
import asyncio
from typing import Optional
from telegram import Update, Bot
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters
)
from telegram.constants import ParseMode

from config.settings import Config
from src.utils.logger import logger


class TelegramBot:
    """Telegram бот для взаимодействия с пользователем"""
    
    def __init__(self, agent_reference=None):
        self.token = Config.TELEGRAM_BOT_TOKEN
        self.chat_id = Config.TELEGRAM_CHAT_ID
        self.bot = Bot(token=self.token)
        self.application: Optional[Application] = None
        self.agent = agent_reference
        
        logger.info("Telegram бот инициализирован")
    
    async def send_message(self, text: str, parse_mode: str = ParseMode.MARKDOWN):
        """Отправка сообщения пользователю"""
        try:
            await self.bot.send_message(
                chat_id=self.chat_id,
                text=text,
                parse_mode=parse_mode
            )
            logger.debug(f"Сообщение отправлено в Telegram: {text[:50]}...")
        except Exception as e:
            logger.error(f"Ошибка отправки сообщения в Telegram: {e}")
    
    async def send_notification(self, title: str, message: str):
        """Отправка уведомления"""
        text = f"*{title}*\n\n{message}"
        await self.send_message(text)
    
    async def notify_email_processed(self, email_data: dict, classification: dict, action: str):
        """Уведомление об обработанном письме"""
        subject = email_data.get("subject", "Без темы")[:50]
        sender = email_data.get("sender", "Неизвестно")[:50]
        category = classification.get("category", "Unknown")
        
        message = f"""📧 *Обработано письмо*

От: `{sender}`
Тема: `{subject}`
Категория: `{category}`
Действие: `{action}`
"""
        await self.send_message(message)
    
    async def notify_error(self, error_message: str):
        """Уведомление об ошибке"""
        text = f"⚠️ *Ошибка*\n\n`{error_message}`"
        await self.send_message(text)
    
    async def notify_summary(self, stats: dict):
        """Отправка сводки по обработке"""
        message = f"""📊 *Сводка обработки писем*

Обработано: {stats.get('processed', 0)}
Удалено: {stats.get('deleted', 0)}
Перемещено: {stats.get('moved', 0)}
Архивировано: {stats.get('archived', 0)}
"""
        await self.send_message(message)
    
    # === Обработчики команд ===
    
    async def cmd_start(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Команда /start"""
        welcome_text = """👋 *Привет! Я AI Email Agent*

Я помогаю управлять вашей почтой, классифицирую письма и выполняю автоматические действия.

*Доступные команды:*

/status - статус агента
/stats - статистика обработки
/rules - список правил
/add_rule - добавить правило
/delete_rule [id] - удалить правило
/check - проверить почту сейчас
/last - последние обработанные письма
/help - помощь

Вы также можете писать команды на естественном языке, например:
• "удали все письма от amazon"
• "переместить письма о рекламе в папку Promo"
• "покажи статистику за неделю"
"""
        await update.message.reply_text(welcome_text, parse_mode=ParseMode.MARKDOWN)
    
    async def cmd_status(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Команда /status"""
        if self.agent:
            status = self.agent.get_status()
            status_text = f"""📊 *Статус агента*

Работает: {'✅ Да' if status.get('running', False) else '❌ Нет'}
Последняя проверка: {status.get('last_check', 'Никогда')}
Обработано писем: {status.get('total_processed', 0)}
Активных правил: {status.get('active_rules', 0)}
"""
        else:
            status_text = "Агент не инициализирован"
        
        await update.message.reply_text(status_text, parse_mode=ParseMode.MARKDOWN)
    
    async def cmd_stats(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Команда /stats"""
        if self.agent:
            stats = self.agent.get_statistics()
            stats_text = f"""📈 *Статистика*

За сегодня:
• Обработано: {stats.get('today_processed', 0)}
• Удалено: {stats.get('today_deleted', 0)}
• Перемещено: {stats.get('today_moved', 0)}

За неделю:
• Обработано: {stats.get('week_processed', 0)}
• Удалено: {stats.get('week_deleted', 0)}
• Перемещено: {stats.get('week_moved', 0)}
"""
        else:
            stats_text = "Статистика недоступна"
        
        await update.message.reply_text(stats_text, parse_mode=ParseMode.MARKDOWN)
    
    async def cmd_rules(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Команда /rules"""
        if self.agent:
            rules_summary = self.agent.get_rules_summary()
            rules_text = f"📋 *Правила обработки*\n\n{rules_summary}"
        else:
            rules_text = "Правила недоступны"
        
        await update.message.reply_text(rules_text, parse_mode=ParseMode.MARKDOWN)
    
    async def cmd_add_rule(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Команда /add_rule"""
        help_text = """📝 *Добавление правила*

Примеры команд:
• "всё от amazon.com удалять"
• "письма с темой 'реклама' перемещать в Promo"
• "от newsletter@example.com архивировать"

Просто напишите правило после команды /add_rule или отдельным сообщением.
"""
        await update.message.reply_text(help_text, parse_mode=ParseMode.MARKDOWN)
    
    async def cmd_delete_rule(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Команда /delete_rule"""
        if not context.args:
            await update.message.reply_text(
                "Использование: /delete_rule [id]\nНапример: /delete_rule 5"
            )
            return
        
        try:
            rule_id = int(context.args[0])
            if self.agent:
                success = self.agent.delete_rule(rule_id)
                if success:
                    await update.message.reply_text(f"✅ Правило {rule_id} удалено")
                else:
                    await update.message.reply_text(f"❌ Не удалось удалить правило {rule_id}")
            else:
                await update.message.reply_text("Агент недоступен")
        except ValueError:
            await update.message.reply_text("❌ Неверный ID правила")
    
    async def cmd_check(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Команда /check - проверить почту сейчас"""
        await update.message.reply_text("🔄 Запускаю проверку почты...")
        
        if self.agent:
            try:
                # Запуск проверки в фоне
                asyncio.create_task(self._run_check_in_background(update))
            except Exception as e:
                await update.message.reply_text(f"❌ Ошибка: {e}")
        else:
            await update.message.reply_text("Агент недоступен")
    
    async def _run_check_in_background(self, update: Update):
        """Запуск проверки почты в фоне"""
        try:
            result = self.agent.check_emails_now()
            await update.message.reply_text(
                f"✅ Проверка завершена\n\n"
                f"Обработано: {result.get('processed', 0)}\n"
                f"Удалено: {result.get('deleted', 0)}\n"
                f"Перемещено: {result.get('moved', 0)}"
            )
        except Exception as e:
            await update.message.reply_text(f"❌ Ошибка при проверке: {e}")
    
    async def cmd_last(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Команда /last - последние письма"""
        if self.agent:
            emails = self.agent.get_last_processed_emails(limit=5)
            if emails:
                text = "📬 *Последние обработанные письма:*\n\n"
                for email in emails:
                    subject = email.get("subject", "Без темы")[:40]
                    sender = email.get("sender", "Неизвестно")[:30]
                    action = email.get("action", "none")
                    text += f"• `{subject}`\n  От: {sender}\n  Действие: {action}\n\n"
            else:
                text = "Нет обработанных писем"
        else:
            text = "Агент недоступен"
        
        await update.message.reply_text(text, parse_mode=ParseMode.MARKDOWN)
    
    async def cmd_help(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Команда /help"""
        help_text = """❓ *Помощь*

*Основные команды:*
/start - начало работы
/status - статус агента
/stats - статистика
/rules - список правил
/check - проверить почту
/last - последние письма

*Управление правилами:*
/add_rule - добавить правило
/delete_rule [id] - удалить правило

*Естественный язык:*
Вы можете писать команды обычными словами:
• "покажи статистику"
• "удали все от amazon"
• "добавь правило: всё что реклама в Promo"

По вопросам пишите автору.
"""
        await update.message.reply_text(help_text, parse_mode=ParseMode.MARKDOWN)
    
    async def handle_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработка текстовых сообщений"""
        text = update.message.text.lower()
        
        # Обработка естественного языка
        if "статус" in text or "status" in text:
            await self.cmd_status(update, context)
        elif "статистик" in text or "stats" in text:
            await self.cmd_stats(update, context)
        elif "правил" in text or "rules" in text:
            await self.cmd_rules(update, context)
        elif "проверь" in text or "check" in text:
            await self.cmd_check(update, context)
        elif "удали" in text and "от" in text:
            # Попытка создать правило
            if self.agent:
                rule_id = self.agent.create_rule_from_text(update.message.text)
                if rule_id:
                    await update.message.reply_text(f"✅ Создано правило ID {rule_id}")
                else:
                    await update.message.reply_text("❌ Не удалось создать правило")
        else:
            await update.message.reply_text(
                "Не понял команду. Используйте /help для списка команд."
            )
    
    def setup_handlers(self):
        """Настройка обработчиков команд"""
        if not self.application:
            self.application = Application.builder().token(self.token).build()
        
        # Регистрация обработчиков
        self.application.add_handler(CommandHandler("start", self.cmd_start))
        self.application.add_handler(CommandHandler("status", self.cmd_status))
        self.application.add_handler(CommandHandler("stats", self.cmd_stats))
        self.application.add_handler(CommandHandler("rules", self.cmd_rules))
        self.application.add_handler(CommandHandler("add_rule", self.cmd_add_rule))
        self.application.add_handler(CommandHandler("delete_rule", self.cmd_delete_rule))
        self.application.add_handler(CommandHandler("check", self.cmd_check))
        self.application.add_handler(CommandHandler("last", self.cmd_last))
        self.application.add_handler(CommandHandler("help", self.cmd_help))
        
        # Обработчик текстовых сообщений
        self.application.add_handler(
            MessageHandler(filters.TEXT & ~filters.COMMAND, self.handle_message)
        )
        
        logger.info("Обработчики Telegram бота настроены")
    
    async def start_polling(self):
        """Запуск бота в режиме polling"""
        self.setup_handlers()
        
        logger.info("Запуск Telegram бота...")
        await self.application.initialize()
        await self.application.start()
        await self.application.updater.start_polling()
    
    async def stop_polling(self):
        """Остановка бота"""
        if self.application:
            logger.info("Остановка Telegram бота...")
            await self.application.updater.stop()
            await self.application.stop()
            await self.application.shutdown()
