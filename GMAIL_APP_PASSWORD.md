# Как получить App Password для Gmail

## 📧 Пошаговая инструкция

### Шаг 1: Включите двухфакторную аутентификацию (2FA)

**Это обязательный шаг!** App Passwords доступны только при включенной 2FA.

1. Откройте https://myaccount.google.com/security
2. Найдите раздел **"Двухэтапная аутентификация"** или **"2-Step Verification"**
3. Нажмите на него и следуйте инструкциям Google для настройки
4. Вы можете использовать:
   - SMS коды
   - Google Authenticator
   - Ключи безопасности
   - Другие методы подтверждения

### Шаг 2: Создайте App Password

После включения 2FA:

1. **Прямая ссылка**: Откройте https://myaccount.google.com/apppasswords
   
   ИЛИ
   
   - Перейдите на https://myaccount.google.com/security
   - Прокрутите вниз до раздела **"Signing in to Google"**
   - Найдите **"App passwords"** или **"Пароли приложений"**
   - Нажмите на стрелку справа →

2. **Возможно понадобится войти снова** - введите ваш основной пароль Google

3. **Выберите приложение**:
   - В выпадающем списке "Select app" выберите **"Mail"**
   - ИЛИ выберите **"Other (Custom name)"** и введите название, например: `Email Agent`

4. **Выберите устройство**:
   - Выберите ваше устройство или "Other"

5. **Нажмите "Generate"** / **"Создать"**

### Шаг 3: Скопируйте пароль

Google покажет **16-значный пароль** в желтой рамке:

```
Пример: abcd efgh ijkl mnop
```

**⚠️ ВАЖНО:**
- **Скопируйте пароль СЕЙЧАС** - он больше не будет показан!
- Пароль показан с пробелами для удобства чтения
- В `.env` файле используйте БЕЗ пробелов: `abcdefghijklmnop`
- Сохраните его в надежном месте (менеджер паролей)

### Шаг 4: Используйте в .env файле

Откройте файл `.env` и вставьте:

```env
EMAIL_PROVIDER=gmail
EMAIL_ADDRESS=your_email@gmail.com
EMAIL_PASSWORD=abcdefghijklmnop  # БЕЗ пробелов!
```

## ❓ Частые вопросы

### Не вижу "App passwords" в настройках

**Причины:**
1. **Не включена 2FA** - включите двухфакторную аутентификацию сначала
2. **Рабочий аккаунт Google Workspace** - администратор мог отключить эту функцию
3. **Advanced Protection** - если включена расширенная защита, App Passwords недоступны

**Решение:** Используйте прямую ссылку https://myaccount.google.com/apppasswords

### Ошибка "Authentication failed" при подключении

**Проверьте:**
1. ✅ Пароль скопирован **БЕЗ пробелов**
2. ✅ Используете App Password, а НЕ обычный пароль от Google
3. ✅ EMAIL_ADDRESS правильный (полный адрес с @gmail.com)
4. ✅ IMAP включен в настройках Gmail

**Включение IMAP:**
1. Откройте Gmail
2. Настройки (⚙️) → See all settings
3. Вкладка "Forwarding and POP/IMAP"
4. "IMAP access" → **Enable IMAP**
5. Сохраните изменения

### Можно ли использовать обычный пароль?

**НЕТ!** Google не разрешает использовать обычный пароль для IMAP приложений с включенной 2FA.

Вы **ДОЛЖНЫ** использовать App Password.

### Безопасно ли это?

**ДА!** App Passwords:
- ✅ Более безопасны, чем обычный пароль
- ✅ Работают только для конкретного приложения
- ✅ Можно отозвать в любой момент
- ✅ Не дают доступ к другим функциям аккаунта
- ✅ Не позволяют изменить пароль аккаунта

### Как отозвать App Password?

Если пароль скомпрометирован:

1. Откройте https://myaccount.google.com/apppasswords
2. Найдите нужный App Password в списке
3. Нажмите на значок корзины 🗑️ рядом с ним
4. Создайте новый App Password для приложения

## 📸 Визуальная инструкция

### Как выглядит страница App Passwords:

```
┌─────────────────────────────────────────────┐
│  App passwords                              │
│                                             │
│  Select the app and device you want to     │
│  generate the app password for.             │
│                                             │
│  Select app:  [Mail            ▼]          │
│  Select device: [Other         ▼]          │
│                                             │
│  [Generate]                                 │
└─────────────────────────────────────────────┘
```

### После нажатия Generate:

```
┌─────────────────────────────────────────────┐
│  Your app password for your device          │
│                                             │
│  ┌─────────────────────────────────────┐   │
│  │  abcd efgh ijkl mnop                │   │
│  └─────────────────────────────────────┘   │
│                                             │
│  You won't see this password again!         │
│  [Done]                                     │
└─────────────────────────────────────────────┘
```

## 🔗 Полезные ссылки

- **App Passwords (прямая ссылка)**: https://myaccount.google.com/apppasswords
- **Настройки безопасности**: https://myaccount.google.com/security
- **Справка Google об App Passwords**: https://support.google.com/accounts/answer/185833
- **Настройки Gmail IMAP**: https://mail.google.com/mail/u/0/#settings/fwdandpop

## 💡 Советы

1. **Сохраните пароль** в менеджере паролей (1Password, LastPass, Bitwarden)
2. **Используйте разные App Passwords** для разных приложений
3. **Регулярно проверяйте** список активных App Passwords
4. **Удаляйте неиспользуемые** App Passwords

## 🆘 Всё ещё не работает?

1. Проверьте логи агента:
   ```bash
   tail -f logs/email_agent.log
   ```

2. Запустите тест конфигурации:
   ```bash
   python test_config.py
   ```

3. Убедитесь, что в .env файле:
   - Нет лишних пробелов в EMAIL_PASSWORD
   - EMAIL_ADDRESS полный (с @gmail.com)
   - EMAIL_PROVIDER=gmail

4. Попробуйте пересоздать App Password

5. Проверьте, что IMAP включен в Gmail

---

**Нужна дополнительная помощь?** Создайте issue на GitHub с описанием проблемы и текстом ошибки из логов.
