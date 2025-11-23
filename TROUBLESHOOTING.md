# Решение проблем IMAP / IMAP Troubleshooting

## Распространенные ошибки и решения

### Ошибка: "COPY command error: BAD [b'Could not parse command']"

**Причины:**
1. Несовместимость типов данных при работе с IMAP командами
2. Попытка перемещения в Gmail системные папки (например, `[Gmail]/All Mail`)

**Решение:** 
Исправлено в последней версии:
- Email ID теперь правильно конвертируется в bytes
- Добавлена специальная обработка Gmail системных папок
- Архивирование теперь работает корректно для Gmail

**Если проблема сохраняется:**
1. Обновите код: `git pull`
2. Перезапустите агента
3. Проверьте логи: `tail -f logs/email_agent.log`

**Примечание для Gmail:**
- Архивирование в Gmail работает через удаление из Inbox
- Письма автоматически остаются в "All Mail"
- Не нужно перемещать в `[Gmail]/All Mail` вручную

---

### Ошибка: "Connection refused" или "Connection reset"

**Причины:**
- IMAP сервер недоступен
- Неправильные настройки порта
- Firewall блокирует подключение

**Решение:**
1. Проверьте настройки IMAP в .env:
   ```env
   GMAIL_IMAP_SERVER=imap.gmail.com
   GMAIL_IMAP_PORT=993
   ```

2. Проверьте подключение:
   ```bash
   telnet imap.gmail.com 993
   ```

3. Проверьте firewall:
   ```bash
   sudo ufw status
   ```

---

### Ошибка: "Authentication failed"

**Причины:**
- Неправильный пароль
- Не используется App Password для Gmail
- 2FA не включена

**Решение:**
1. Для Gmail используйте App Password (не обычный пароль)
2. Проверьте .env файл:
   ```env
   EMAIL_PASSWORD=abcdefghijklmnop  # БЕЗ пробелов!
   ```
3. Смотрите [GMAIL_APP_PASSWORD.md](GMAIL_APP_PASSWORD.md)

---

### Ошибка: "Folder not found" или "NO [NONEXISTENT]"

**Причина:** Папка не существует на сервере

**Решение:**
1. Агент автоматически создает папки, но иногда это не работает
2. Создайте папку вручную через веб-интерфейс Gmail/Yandex/Outlook
3. Проверьте имя папки (учитывается регистр)

**Для Gmail:**
- Используйте простые имена без спецсимволов
- Примеры: `Work`, `Promo`, `Finance`
- **НЕ используйте системные папки:** `[Gmail]/All Mail`, `[Gmail]/Trash`, `[Gmail]/Spam`
- Для архивирования используйте действие "archive" вместо перемещения в `[Gmail]/All Mail`

---

### Ошибка: "Too many simultaneous connections"

**Причина:** Превышен лимит одновременных IMAP подключений

**Решение:**
1. Закройте другие почтовые клиенты
2. Увеличьте `CHECK_INTERVAL_MINUTES` в .env:
   ```env
   CHECK_INTERVAL_MINUTES=10  # Вместо 5
   ```
3. Перезапустите агента

---

### Ошибка: "IMAP4 class has no attribute 'copy'"

**Причина:** Используется неправильный клиент IMAP

**Решение:**
Убедитесь что используется `imaplib.IMAP4_SSL`:
```python
self.connection = imaplib.IMAP4_SSL(server, port)
```

---

### Агент зависает при обработке писем

**Причины:**
- Слишком большие письма
- Медленный LLM
- Проблемы с сетью

**Решение:**
1. Уменьшите `MAX_EMAILS_PER_CHECK`:
   ```env
   MAX_EMAILS_PER_CHECK=10  # Вместо 50
   ```

2. Используйте более быструю модель:
   ```env
   OLLAMA_MODEL=llama3.2  # Вместо llama3.1:70b
   ```

3. Проверьте логи для деталей

---

### Письма не перемещаются в папки

**Причины:**
- Неправильное имя папки
- Недостаточно прав
- Ошибка IMAP сервера

**Решение:**
1. Проверьте логи агента
2. Создайте папки вручную
3. Проверьте права доступа к папкам

**Для Gmail:**
Системные папки обрабатываются специально:
- `[Gmail]/All Mail` - НЕ используйте для перемещения, используйте действие "archive"
- `[Gmail]/Trash` - для удаленных (автоматически при delete)
- `[Gmail]/Spam` - для спама (можно перемещать)
- Создавайте пользовательские папки для сортировки: `Work`, `Personal`, `Promo` и т.д.

---

### Письма дублируются

**Причина:** Агент не помечает письма как обработанные

**Решение:**
1. Проверьте базу данных:
   ```bash
   sqlite3 data/email_agent.db "SELECT COUNT(*) FROM processed_emails;"
   ```

2. Если база пустая, проблема с записью
3. Проверьте права на папку `data/`
4. Перезапустите агента

---

### LLM классификация не работает

**Для Ollama:**
1. Проверьте что Ollama запущен:
   ```bash
   ollama list
   curl http://localhost:11434/api/tags
   ```

2. Загрузите модель:
   ```bash
   ollama pull llama3.2
   ```

**Для других провайдеров:**
1. Проверьте API ключ в .env
2. Проверьте баланс/лимиты
3. Смотрите логи для деталей

---

## Диагностика проблем

### Включите детальное логирование

В .env:
```env
LOG_LEVEL=DEBUG
```

Перезапустите агента и проверьте логи:
```bash
tail -f logs/email_agent.log
```

### Проверка подключения к IMAP

```python
import imaplib
import ssl

context = ssl.create_default_context()
mail = imaplib.IMAP4_SSL('imap.gmail.com', 993, ssl_context=context)
mail.login('your_email@gmail.com', 'your_app_password')
print(mail.list())
mail.logout()
```

### Проверка базы данных

```bash
sqlite3 data/email_agent.db

# Просмотр обработанных писем
SELECT * FROM processed_emails ORDER BY processed_at DESC LIMIT 10;

# Просмотр правил
SELECT * FROM rules WHERE enabled = 1;

# Просмотр ошибок
SELECT * FROM action_logs WHERE status = 'failed' ORDER BY created_at DESC LIMIT 10;
```

---

## Получение помощи

Если проблема не решена:

1. **Соберите информацию:**
   ```bash
   # Последние 50 строк лога
   tail -n 50 logs/email_agent.log > debug.log
   
   # Версия Python
   python3 --version
   
   # Настройки (без паролей!)
   grep -v "PASSWORD\|API_KEY" .env
   ```

2. **Создайте issue на GitHub** с:
   - Описанием проблемы
   - Текстом ошибки из логов
   - Версией Python
   - Используемым провайдером email и LLM

3. **Временные решения:**
   - Увеличьте интервалы проверки
   - Уменьшите количество писем за раз
   - Используйте более простую модель LLM
   - Отключите автоматические действия

---

## Проверочный чек-лист

- [ ] Python 3.10+ установлен
- [ ] Все зависимости установлены: `pip install -r requirements.txt`
- [ ] .env файл создан и настроен
- [ ] App Password создан для Gmail (не обычный пароль)
- [ ] IMAP включен в настройках почты
- [ ] Ollama запущен (если используете)
- [ ] Telegram бот настроен
- [ ] Папки data/ и logs/ существуют и доступны для записи
- [ ] Firewall не блокирует порт 993 (IMAP)

---

**Большинство проблем решается:**
1. Проверкой логов
2. Использованием правильного App Password
3. Обновлением кода до последней версии
