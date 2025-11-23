FROM python:3.10-slim

# Установка зависимостей системы
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Создание рабочей директории
WORKDIR /app

# Копирование файлов зависимостей
COPY requirements.txt .

# Установка Python зависимостей
RUN pip install --no-cache-dir -r requirements.txt

# Копирование исходного кода
COPY . .

# Создание необходимых директорий
RUN mkdir -p data logs

# Переменные окружения (будут переопределены через .env или docker-compose)
ENV PYTHONUNBUFFERED=1

# Запуск приложения
CMD ["python", "main.py"]
