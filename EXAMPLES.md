# Примеры использования AI Email Agent

## Примеры правил

### Удаление писем

```python
# Удалить все письма от конкретного отправителя
всё от spam@example.com удалять

# Удалить все письма с определенной темой
письма с темой 'Распродажа' удалять
```

### Сортировка по папкам

```python
# Переместить письма в папку
всё от github.com перемещать в Dev

# По категории
категория WORK в папку Work
категория PROMO в папку Promo

# По теме
письма с темой 'invoice' перемещать в Finance
```

### Архивирование

```python
# Архивировать письма от newsletter
от newsletter@ архивировать

# Архивировать старые уведомления
категория UPDATES архивировать
```

## Примеры Telegram команд

### Просмотр статистики

```
/stats
```

Ответ:
```
📈 Статистика

За сегодня:
• Обработано: 15
• Удалено: 3
• Перемещено: 8

За неделю:
• Обработано: 120
• Удалено: 25
• Перемещено: 60
```

### Проверка правил

```
/rules
```

Ответ:
```
📋 Правила обработки

Активных правил: 5

• Отправитель содержит 'amazon.com' → Удалить
• Тема содержит 'реклама' → Переместить в папку (Promo)
• Категория равно 'SPAM' → Удалить
• Отправитель содержит 'newsletter@' → Архивировать
• Тема содержит 'invoice' → Переместить в папку (Finance)
```

### Создание правила

```
добавь правило: всё от facebook.com перемещать в Social
```

Ответ:
```
✅ Создано правило ID 6
```

### Принудительная проверка

```
/check
```

Ответ:
```
🔄 Запускаю проверку почты...

✅ Проверка завершена

Обработано: 5
Удалено: 1
Перемещено: 3
```

### Просмотр последних писем

```
/last
```

Ответ:
```
📬 Последние обработанные письма:

• Re: Meeting tomorrow
  От: john@example.com
  Действие: move

• Your order has been shipped
  От: amazon@amazon.com
  Действие: delete

• Weekly Newsletter
  От: newsletter@example.com
  Действие: archive
```

## Примеры программного создания правил

### Python API

```python
from src.rules_engine.database import Database

db = Database()

# Создание правила удаления
db.add_rule(
    rule_type="DELETE",
    condition_field="sender",
    condition_operator="contains",
    condition_value="spam",
    action_type="delete",
    priority=10
)

# Создание правила перемещения
db.add_rule(
    rule_type="MOVE",
    condition_field="category",
    condition_operator="equals",
    condition_value="WORK",
    action_type="move",
    action_value="Work",
    priority=5
)

# Создание правила с регулярным выражением
db.add_rule(
    rule_type="FILTER",
    condition_field="subject",
    condition_operator="regex",
    condition_value=r"(invoice|receipt|payment)",
    action_type="move",
    action_value="Finance",
    priority=8
)

# Получение всех правил
rules = db.get_all_rules()
for rule in rules:
    print(f"Rule {rule['id']}: {rule['action_type']} when {rule['condition_field']} {rule['condition_operator']} {rule['condition_value']}")

# Отключение правила
db.toggle_rule(rule_id=5, enabled=False)

# Удаление правила
db.delete_rule(rule_id=3)
```

### Запросы к базе данных

```bash
sqlite3 data/email_agent.db

# Просмотр всех правил
SELECT id, condition_field, condition_operator, condition_value, action_type, action_value 
FROM rules 
WHERE enabled = 1;

# Просмотр последних обработанных писем
SELECT subject, sender, category, action, processed_at 
FROM processed_emails 
ORDER BY processed_at DESC 
LIMIT 10;

# Статистика за последнюю неделю
SELECT date, total_processed, total_deleted, total_moved, total_archived 
FROM statistics 
ORDER BY date DESC 
LIMIT 7;

# Поиск писем от конкретного отправителя
SELECT * 
FROM processed_emails 
WHERE sender LIKE '%amazon%';

# Логи ошибок
SELECT * 
FROM action_logs 
WHERE status = 'failed' 
ORDER BY created_at DESC;
```

## Примеры интеграции

### Webhook при обработке письма

Добавьте в `src/agent.py` в метод `_process_single_email`:

```python
import httpx

# После успешной обработки
if action_success:
    # Отправка webhook
    webhook_url = "https://your-server.com/webhook"
    try:
        httpx.post(webhook_url, json={
            "email_id": unique_id,
            "subject": subject,
            "sender": sender,
            "category": classification.get("category"),
            "action": final_action
        }, timeout=5)
    except:
        pass
```

### Slack уведомления

```python
from slack_sdk import WebClient

slack_client = WebClient(token="your-slack-token")

# В методе notify_email_processed
slack_client.chat_postMessage(
    channel="#email-notifications",
    text=f"📧 Обработано письмо от {sender}: {subject}"
)
```

### Сохранение вложений

```python
# В src/email_client/client.py, в методе _get_email_body
if email_message.is_multipart():
    for part in email_message.walk():
        if part.get_content_disposition() == "attachment":
            filename = part.get_filename()
            if filename:
                filepath = Path("attachments") / filename
                filepath.parent.mkdir(exist_ok=True)
                filepath.write_bytes(part.get_payload(decode=True))
```

## Расширенные сценарии

### Автоматические ответы

```python
# Добавьте в src/agent.py
def _send_auto_reply(self, email_data: Dict, reply_text: str):
    """Отправка автоматического ответа"""
    import smtplib
    from email.mime.text import MIMEText
    
    smtp_config = Config.get_smtp_config()
    
    msg = MIMEText(reply_text, 'plain', 'utf-8')
    msg['Subject'] = f"Re: {email_data['subject']}"
    msg['From'] = smtp_config['email']
    msg['To'] = email_data['sender']
    
    with smtplib.SMTP(smtp_config['server'], smtp_config['port']) as server:
        server.starttls()
        server.login(smtp_config['email'], smtp_config['password'])
        server.send_message(msg)
```

### Расписание проверок

```python
# Разное время проверки для рабочих и выходных дней
from datetime import datetime

def get_check_interval():
    now = datetime.now()
    if now.weekday() < 5:  # Понедельник-Пятница
        if 9 <= now.hour <= 18:  # Рабочее время
            return 5  # Каждые 5 минут
        else:
            return 30  # Каждые 30 минут
    else:  # Выходные
        return 60  # Каждый час
```

### Множественные почтовые ящики

```python
# Конфигурация нескольких ящиков
accounts = [
    {
        "provider": "gmail",
        "email": "work@gmail.com",
        "password": "password1"
    },
    {
        "provider": "outlook",
        "email": "personal@outlook.com",
        "password": "password2"
    }
]

# Обработка каждого ящика
for account in accounts:
    client = EmailClient(
        provider=account["provider"],
        email=account["email"],
        password=account["password"]
    )
    # ... обработка
```

## Полезные советы

### Оптимизация производительности

1. Ограничьте количество писем за проверку (`MAX_EMAILS_PER_CHECK`)
2. Увеличьте интервал проверки для экономии API токенов
3. Используйте кэширование для повторяющихся отправителей
4. Отключите автоматическое удаление в начале (`ENABLE_AUTO_DELETE=false`)

### Мониторинг

```bash
# Мониторинг в реальном времени
tail -f logs/email_agent.log | grep ERROR

# Подсчет обработанных писем
sqlite3 data/email_agent.db "SELECT COUNT(*) FROM processed_emails;"

# Наиболее частые отправители
sqlite3 data/email_agent.db "SELECT sender, COUNT(*) as count FROM processed_emails GROUP BY sender ORDER BY count DESC LIMIT 10;"
```

### Резервное копирование

```bash
#!/bin/bash
# Скрипт автоматического бэкапа

DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_DIR="/backups/email_agent"

mkdir -p $BACKUP_DIR

# Бэкап базы данных
cp data/email_agent.db $BACKUP_DIR/email_agent_$DATE.db

# Бэкап логов
tar -czf $BACKUP_DIR/logs_$DATE.tar.gz logs/

# Удаление старых бэкапов (старше 30 дней)
find $BACKUP_DIR -name "*.db" -mtime +30 -delete
find $BACKUP_DIR -name "*.tar.gz" -mtime +30 -delete

echo "Backup completed: $DATE"
```
