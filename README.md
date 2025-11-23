# AI Email Agent - Инструкция по установке и запуску

## 🚀 Быстрый старт

**Нужна помощь с App Password для Gmail?** → [Смотрите детальную инструкцию ниже](#для-gmail)

**Основные шаги:**
1. Установите Python 3.10+
2. Настройте `.env` файл (инструкции ниже)
3. Запустите: `./start.sh`

---

## 📋 Описание проекта

AI Email Agent - это интеллектуальная система управления электронной почтой, которая использует искусственный интеллект (LLM) для автоматической классификации, сортировки и управления вашими письмами.

### Основные возможности:

✅ Автоматическое подключение к почтовым провайдерам (Gmail, Yandex, Outlook)
✅ Классификация писем через LLM (OpenAI GPT или Anthropic Claude)
✅ Автоматическая сортировка по папкам
✅ Удаление спама и нежелательной почты
✅ Архивирование писем
✅ Пользовательские правила обработки
✅ Уведомления в Telegram
✅ Управление через Telegram-бота
✅ Полное логирование всех действий
✅ Защита от дубликатов
✅ Статистика обработки

---

## 🏗 Структура проекта

```
diebrowbar/
├── config/
│   ├── __init__.py
│   └── settings.py           # Конфигурация приложения
├── src/
│   ├── __init__.py
│   ├── agent.py              # Главный модуль агента
│   ├── email_client/
│   │   ├── __init__.py
│   │   └── client.py         # IMAP клиент для работы с почтой
│   ├── llm_classifier/
│   │   ├── __init__.py
│   │   └── classifier.py     # LLM классификатор писем
│   ├── rules_engine/
│   │   ├── __init__.py
│   │   ├── database.py       # SQLite база данных
│   │   └── engine.py         # Движок правил
│   ├── telegram_bot/
│   │   ├── __init__.py
│   │   └── bot.py            # Telegram бот
│   └── utils/
│       ├── __init__.py
│       ├── logger.py         # Логирование
│       └── helpers.py        # Вспомогательные функции
├── data/                     # База данных (создается автоматически)
├── logs/                     # Логи (создается автоматически)
├── main.py                   # Точка входа
├── requirements.txt          # Зависимости Python
├── .env.example             # Пример конфигурации
├── .gitignore
└── README.md                # Этот файл
```

---

## 🚀 Установка

### Шаг 1: Системные требования

- Python 3.10 или выше
- Доступ в интернет
- Учетная запись Gmail/Yandex/Outlook
- OpenAI API ключ или Anthropic API ключ
- Telegram бот (создается через @BotFather)

### Шаг 2: Клонирование репозитория

```bash
git clone https://github.com/herman030103-eng/diebrowbar.git
cd diebrowbar
```

### Шаг 3: Создание виртуального окружения

```bash
# Создание виртуального окружения
python3 -m venv venv

# Активация (Linux/Mac)
source venv/bin/activate

# Активация (Windows)
venv\Scripts\activate
```

### Шаг 4: Установка зависимостей

```bash
pip install -r requirements.txt
```

---

## ⚙️ Настройка

### Шаг 1: Создание файла конфигурации

```bash
cp .env.example .env
```

### Шаг 2: Настройка почты

#### Для Gmail:

**📖 Нужна подробная инструкция?** → [Смотрите GMAIL_APP_PASSWORD.md](GMAIL_APP_PASSWORD.md)

**Краткая инструкция:**

1. **Включите двухфакторную аутентификацию** (обязательно для App Passwords):
   - Перейдите на https://myaccount.google.com/security
   - Найдите раздел "Двухэтапная аутентификация" / "2-Step Verification"
   - Следуйте инструкциям для включения

2. **Создайте App Password** (пароль приложения):
   - Перейдите напрямую: https://myaccount.google.com/apppasswords
   - Или через https://myaccount.google.com/security → найдите "App passwords" / "Пароли приложений"
   - В поле "Select app" выберите "Mail" или "Other (Custom name)"
   - Введите название, например "Email Agent"
   - Нажмите "Generate" / "Создать"
   - **Google покажет 16-значный пароль** (например: `abcd efgh ijkl mnop`)
   - **ВАЖНО**: Скопируйте этот пароль сразу! Он больше не будет показан
   - Используйте этот пароль БЕЗ пробелов: `abcdefghijklmnop`

3. В файле `.env` укажите:

```env
EMAIL_PROVIDER=gmail
EMAIL_ADDRESS=your_email@gmail.com
EMAIL_PASSWORD=abcdefghijklmnop  # 16 символов БЕЗ пробелов
```

**⚠️ Примечание**: НЕ используйте ваш обычный пароль от Google! Только App Password!

#### Для Yandex:

```env
EMAIL_PROVIDER=yandex
EMAIL_ADDRESS=your_email@yandex.ru
EMAIL_PASSWORD=your_password
```

#### Для Outlook:

```env
EMAIL_PROVIDER=outlook
EMAIL_ADDRESS=your_email@outlook.com
EMAIL_PASSWORD=your_password
```

### Шаг 3: Настройка LLM

**🆓 Хотите бесплатную альтернативу?** → [Смотрите FREE_LLM_GUIDE.md](FREE_LLM_GUIDE.md)

Доступные провайдеры:
- **Ollama** - БЕСПЛАТНО, локально (рекомендуется)
- **Hugging Face** - БЕСПЛАТНО с ограничениями
- **Perplexity** - Платно (если у вас есть аккаунт)
- **OpenAI** - Платно
- **Anthropic** - Платно

#### Для Ollama (БЕСПЛАТНО, рекомендуется):

1. Установите Ollama: https://ollama.ai/download
2. Загрузите модель:
```bash
ollama pull llama3.2
```
3. В файле `.env`:
```env
LLM_PROVIDER=ollama
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=llama3.2
OLLAMA_MAX_TOKENS=1000
OLLAMA_TEMPERATURE=0.3
```

#### Для Perplexity (Ваш платный аккаунт):

1. Получите API ключ: https://www.perplexity.ai/settings/api
2. В файле `.env`:
```env
LLM_PROVIDER=perplexity
PERPLEXITY_API_KEY=pplx-your-api-key-here
PERPLEXITY_MODEL=llama-3.1-sonar-small-128k-online
```

#### Для OpenAI (платно):

1. Получите API ключ на https://platform.openai.com/api-keys
2. В файле `.env`:

```env
LLM_PROVIDER=openai
OPENAI_API_KEY=sk-your-openai-api-key-here
OPENAI_MODEL=gpt-4-turbo-preview
```

#### Для Anthropic Claude:

1. Получите API ключ на https://console.anthropic.com/
2. В файле `.env`:

```env
LLM_PROVIDER=anthropic
ANTHROPIC_API_KEY=sk-ant-your-key-here
ANTHROPIC_MODEL=claude-3-sonnet-20240229
```

### Шаг 4: Настройка Telegram бота

1. Откройте Telegram и найдите бота **@BotFather**
2. Отправьте команду `/newbot` и следуйте инструкциям
3. Получите токен бота (выглядит как `123456789:ABCdefGHIjklMNOpqrsTUVwxyz`)
4. Найдите бота **@userinfobot** в Telegram
5. Отправьте ему любое сообщение, он ответит вашим Chat ID
6. В файле `.env`:

```env
TELEGRAM_BOT_TOKEN=123456789:ABCdefGHIjklMNOpqrsTUVwxyz
TELEGRAM_CHAT_ID=123456789
```

### Шаг 5: Дополнительные настройки

В файле `.env` вы можете настроить:

```env
# Интервал проверки почты (в минутах)
CHECK_INTERVAL_MINUTES=5

# Максимальное количество писем за проверку
MAX_EMAILS_PER_CHECK=50

# Автоматическое удаление
ENABLE_AUTO_DELETE=false

# Автоматическая архивация
ENABLE_AUTO_ARCHIVE=true

# Уровень логирования (DEBUG, INFO, WARNING, ERROR)
LOG_LEVEL=INFO
```

---

## ▶️ Запуск

### Обычный запуск:

```bash
python main.py
```

### Запуск в фоновом режиме (Linux/Mac):

```bash
nohup python main.py > output.log 2>&1 &
```

### Запуск как systemd сервис (Linux):

Создайте файл `/etc/systemd/system/email-agent.service`:

```ini
[Unit]
Description=AI Email Agent
After=network.target

[Service]
Type=simple
User=your_username
WorkingDirectory=/path/to/diebrowbar
ExecStart=/path/to/diebrowbar/venv/bin/python main.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

Затем:

```bash
sudo systemctl daemon-reload
sudo systemctl enable email-agent
sudo systemctl start email-agent
sudo systemctl status email-agent
```

---

## 📱 Использование Telegram бота

### Основные команды:

- `/start` - начало работы, список команд
- `/status` - текущий статус агента
- `/stats` - статистика обработки писем
- `/rules` - список активных правил
- `/check` - проверить почту прямо сейчас
- `/last` - показать последние обработанные письма
- `/help` - справка по командам

### Добавление правил:

Вы можете добавлять правила на естественном языке:

**Примеры:**

```
всё от amazon.com удалять
```

```
письма с темой 'реклама' перемещать в Promo
```

```
от newsletter@example.com архивировать
```

```
категория SPAM в папку Junk
```

### Управление правилами:

```
/rules - посмотреть все правила
/delete_rule 5 - удалить правило с ID 5
```

---

## 📊 Структура базы данных

База данных SQLite автоматически создается в `data/email_agent.db`

### Таблицы:

1. **rules** - пользовательские правила обработки
2. **processed_emails** - история обработанных писем
3. **action_logs** - лог всех действий агента
4. **statistics** - статистика по дням

---

## 🔍 Мониторинг и логи

### Просмотр логов:

```bash
# Последние 50 строк
tail -n 50 logs/email_agent.log

# Постоянный просмотр (следить за новыми записями)
tail -f logs/email_agent.log

# Поиск ошибок
grep ERROR logs/email_agent.log
```

### Просмотр базы данных:

```bash
sqlite3 data/email_agent.db

# Примеры запросов:
SELECT * FROM rules;
SELECT * FROM processed_emails LIMIT 10;
SELECT * FROM statistics ORDER BY date DESC LIMIT 7;
```

---

## 🛠 Решение проблем

### Проблема: Не удается подключиться к Gmail

**Решение:**
1. **Включите двухфакторную аутентификацию**: 
   - Перейдите на https://myaccount.google.com/security
   - Включите "2-Step Verification"
   
2. **Создайте App Password**:
   - Откройте https://myaccount.google.com/apppasswords
   - Выберите приложение "Mail" или "Other"
   - Скопируйте 16-значный пароль (без пробелов)
   - Вставьте его в .env как EMAIL_PASSWORD
   
3. **НЕ используйте обычный пароль от Google!** Только App Password работает с IMAP

4. **Проверьте, что IMAP включен**:
   - Откройте Gmail → Настройки → "Forwarding and POP/IMAP"
   - Убедитесь, что "IMAP access" включен

5. **Если всё равно не работает**:
   - Проверьте логи: `tail -f logs/email_agent.log`
   - Убедитесь, что EMAIL_PASSWORD без пробелов
   - Попробуйте пересоздать App Password

### Проблема: Ошибка OpenAI API

**Решение:**
1. Проверьте, что API ключ корректен
2. Убедитесь, что у вас есть кредиты на счету OpenAI
3. Проверьте лимиты API на https://platform.openai.com/usage

### Проблема: Telegram бот не отвечает

**Решение:**
1. Проверьте токен бота
2. Убедитесь, что Chat ID корректный
3. Напишите боту `/start` в Telegram
4. Проверьте, что бот не заблокирован

### Проблема: База данных заблокирована

**Решение:**
```bash
# Проверьте, не запущен ли агент дважды
ps aux | grep main.py

# Остановите лишние процессы
kill <PID>
```

---

## 🔒 Безопасность

### Рекомендации:

1. **Никогда не коммитьте файл `.env`** в Git
2. Используйте App Passwords вместо основных паролей
3. Регулярно обновляйте зависимости: `pip install --upgrade -r requirements.txt`
4. Проверяйте логи на подозрительную активность
5. Делайте резервные копии базы данных

### Резервное копирование:

```bash
# Создание бэкапа
cp data/email_agent.db data/email_agent_backup_$(date +%Y%m%d).db

# Автоматический бэкап (добавьте в crontab)
0 2 * * * cp /path/to/data/email_agent.db /path/to/backups/email_agent_$(date +\%Y\%m\%d).db
```

---

## 📈 Расширенное использование

### Создание сложных правил программно:

```python
from src.rules_engine.database import Database

db = Database()

# Добавление правила
db.add_rule(
    rule_type="FILTER",
    condition_field="sender",
    condition_operator="contains",
    condition_value="marketing@",
    action_type="move",
    action_value="Marketing",
    priority=10
)
```

### Интеграция с другими сервисами:

Вы можете расширить `src/agent.py` для интеграции с:
- Slack
- Discord
- Webhooks
- Email ответы
- И другими сервисами

---

## 🤝 Поддержка

При возникновении проблем:

1. Проверьте логи в `logs/email_agent.log`
2. Убедитесь, что все зависимости установлены
3. Проверьте конфигурацию в `.env`
4. Создайте issue на GitHub

---

## 📝 Лицензия

MIT License - свободное использование

---

## 🎯 Roadmap (будущие улучшения)

- [ ] Веб-интерфейс для управления
- [ ] Поддержка нескольких почтовых ящиков
- [ ] Машинное обучение для улучшения классификации
- [ ] Расширенные шаблоны ответов
- [ ] Интеграция с календарями
- [ ] Экспорт статистики в CSV/Excel
- [ ] Docker образ для упрощенного развертывания

---

**Разработано с ❤️ для автоматизации управления почтой**
