# Docker для AI Email Agent

## Быстрый старт с Docker

### Шаг 1: Установка Docker

Убедитесь, что Docker и Docker Compose установлены:

```bash
docker --version
docker-compose --version
```

### Шаг 2: Настройка

```bash
# Создайте .env файл
cp .env.example .env

# Отредактируйте .env и укажите ваши данные
nano .env
```

### Шаг 3: Запуск

```bash
# Сборка и запуск
docker-compose up -d

# Просмотр логов
docker-compose logs -f

# Остановка
docker-compose down
```

## Управление

### Просмотр логов

```bash
# В реальном времени
docker-compose logs -f email-agent

# Последние 100 строк
docker-compose logs --tail=100 email-agent
```

### Перезапуск

```bash
docker-compose restart
```

### Обновление

```bash
# Остановка
docker-compose down

# Обновление кода (git pull или другой способ)
git pull

# Пересборка и запуск
docker-compose up -d --build
```

### Доступ к контейнеру

```bash
docker-compose exec email-agent bash
```

### Резервное копирование

```bash
# Бэкап базы данных
docker-compose exec email-agent cp /app/data/email_agent.db /app/data/backup.db

# Копирование бэкапа на хост
docker cp ai-email-agent:/app/data/backup.db ./backup.db
```

## Docker без docker-compose

### Сборка образа

```bash
docker build -t ai-email-agent .
```

### Запуск контейнера

```bash
docker run -d \
  --name ai-email-agent \
  --env-file .env \
  -v $(pwd)/data:/app/data \
  -v $(pwd)/logs:/app/logs \
  ai-email-agent
```

### Просмотр логов

```bash
docker logs -f ai-email-agent
```

### Остановка

```bash
docker stop ai-email-agent
docker rm ai-email-agent
```

## Продакшн рекомендации

### 1. Использование secrets для чувствительных данных

```yaml
version: '3.8'

services:
  email-agent:
    build: .
    secrets:
      - email_password
      - openai_api_key
      - telegram_bot_token
    environment:
      EMAIL_PASSWORD_FILE: /run/secrets/email_password
      OPENAI_API_KEY_FILE: /run/secrets/openai_api_key
      TELEGRAM_BOT_TOKEN_FILE: /run/secrets/telegram_bot_token

secrets:
  email_password:
    file: ./secrets/email_password.txt
  openai_api_key:
    file: ./secrets/openai_api_key.txt
  telegram_bot_token:
    file: ./secrets/telegram_bot_token.txt
```

### 2. Healthcheck

```yaml
services:
  email-agent:
    # ... другие настройки
    healthcheck:
      test: ["CMD", "python", "-c", "import sqlite3; sqlite3.connect('/app/data/email_agent.db').execute('SELECT 1')"]
      interval: 1m
      timeout: 10s
      retries: 3
```

### 3. Ограничения ресурсов

```yaml
services:
  email-agent:
    # ... другие настройки
    deploy:
      resources:
        limits:
          cpus: '1'
          memory: 512M
        reservations:
          cpus: '0.5'
          memory: 256M
```

### 4. Логирование в файл и stdout

```yaml
services:
  email-agent:
    # ... другие настройки
    logging:
      driver: "json-file"
      options:
        max-size: "10m"
        max-file: "3"
```

## Troubleshooting

### Проблема: Контейнер не запускается

```bash
# Проверьте логи
docker-compose logs email-agent

# Проверьте конфигурацию
docker-compose config
```

### Проблема: Нет доступа к файлам

```bash
# Проверьте права доступа
ls -la data/ logs/

# Измените владельца
sudo chown -R $(id -u):$(id -g) data/ logs/
```

### Проблема: База данных заблокирована

```bash
# Остановите контейнер
docker-compose down

# Проверьте процессы
ps aux | grep python

# Удалите lock файл если есть
rm -f data/*.db-journal

# Запустите снова
docker-compose up -d
```
