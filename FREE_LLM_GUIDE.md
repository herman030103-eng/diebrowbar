# Бесплатные LLM для AI Email Agent

## 🆓 Доступные Бесплатные Опции

Этот гид поможет вам настроить **БЕСПЛАТНЫЕ** альтернативы OpenAI и Anthropic Claude.

---

## 1. 🦙 Ollama (РЕКОМЕНДУЕТСЯ - Полностью бесплатно, локально)

**Преимущества:**
- ✅ 100% бесплатно
- ✅ Работает локально (без интернета)
- ✅ Никаких ограничений по количеству запросов
- ✅ Приватность - данные не покидают ваш компьютер
- ✅ Много моделей на выбор

**Требования:**
- 8+ GB RAM (16 GB рекомендуется)
- ~4-7 GB дискового пространства на модель

### Установка Ollama

#### Linux / macOS:
```bash
curl -fsSL https://ollama.ai/install.sh | sh
```

#### Windows:
Скачайте установщик: https://ollama.ai/download

### Запуск модели

```bash
# Загрузить и запустить Llama 3.2 (3B параметров, быстрая)
ollama pull llama3.2

# Или более мощная модель (70B параметров, медленнее но точнее)
# ollama pull llama3.1:70b

# Запустить Ollama сервер (обычно запускается автоматически)
ollama serve
```

### Настройка в .env

```env
LLM_PROVIDER=ollama
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=llama3.2
OLLAMA_MAX_TOKENS=1000
OLLAMA_TEMPERATURE=0.3
```

### Доступные модели для Ollama:

```bash
# Быстрые модели (для слабых ПК)
ollama pull llama3.2           # 3B параметров, отлично для email
ollama pull phi3               # 3.8B параметров
ollama pull mistral            # 7B параметров

# Мощные модели (для производительных ПК)
ollama pull llama3.1:70b      # 70B параметров
ollama pull mixtral:8x7b      # 47B параметров

# Список всех моделей
ollama list
```

**Рекомендация:** `llama3.2` - отличный баланс скорости и качества для классификации email.

---

## 2. 🤗 Hugging Face (Бесплатно с ограничениями)

**Преимущества:**
- ✅ Бесплатный tier
- ✅ Множество моделей
- ✅ Не требует мощного ПК

**Ограничения:**
- ⚠️ Лимит запросов в минуту
- ⚠️ Может быть медленным в бесплатном tier
- ⚠️ Требует интернет

### Получение токена

1. Зарегистрируйтесь: https://huggingface.co/join
2. Перейдите в настройки: https://huggingface.co/settings/tokens
3. Создайте новый токен (Access Token)
4. Скопируйте токен (начинается с `hf_`)

### Настройка в .env

```env
LLM_PROVIDER=huggingface
HUGGINGFACE_API_KEY=hf_your_token_here
HUGGINGFACE_MODEL=mistralai/Mistral-7B-Instruct-v0.2
HUGGINGFACE_MAX_TOKENS=1000
```

### Рекомендуемые модели:

```env
# Быстрая и качественная
HUGGINGFACE_MODEL=mistralai/Mistral-7B-Instruct-v0.2

# Альтернативы
HUGGINGFACE_MODEL=meta-llama/Llama-2-7b-chat-hf
HUGGINGFACE_MODEL=HuggingFaceH4/zephyr-7b-beta
```

---

## 3. 💫 Perplexity (Ваш платный аккаунт)

Если у вас уже есть платный Perplexity аккаунт:

### Получение API ключа

1. Войдите в Perplexity: https://www.perplexity.ai/
2. Перейдите в настройки API: https://www.perplexity.ai/settings/api
3. Создайте новый API ключ
4. Скопируйте ключ (начинается с `pplx-`)

### Настройка в .env

```env
LLM_PROVIDER=perplexity
PERPLEXITY_API_KEY=pplx-your-api-key-here
PERPLEXITY_MODEL=llama-3.1-sonar-small-128k-online
PERPLEXITY_MAX_TOKENS=1000
PERPLEXITY_TEMPERATURE=0.3
```

### Доступные модели:

```env
# Рекомендуемая для email
PERPLEXITY_MODEL=llama-3.1-sonar-small-128k-online

# Более мощная
PERPLEXITY_MODEL=llama-3.1-sonar-large-128k-online

# С доступом к интернету (для актуальной информации)
PERPLEXITY_MODEL=llama-3.1-sonar-small-128k-online
```

---

## 📊 Сравнение Вариантов

| Провайдер | Цена | Скорость | Качество | Приватность | Интернет |
|-----------|------|----------|----------|-------------|----------|
| **Ollama** | 🆓 Бесплатно | ⚡ Быстро* | ⭐⭐⭐⭐ | 🔒 100% | ❌ Нет |
| Hugging Face | 🆓 Бесплатно** | 🐌 Медленно | ⭐⭐⭐ | ⚠️ Облако | ✅ Да |
| Perplexity | 💰 Платно | ⚡ Быстро | ⭐⭐⭐⭐⭐ | ⚠️ Облако | ✅ Да |
| OpenAI | 💰 Платно | ⚡ Очень быстро | ⭐⭐⭐⭐⭐ | ⚠️ Облако | ✅ Да |
| Anthropic | 💰 Платно | ⚡ Быстро | ⭐⭐⭐⭐⭐ | ⚠️ Облако | ✅ Да |

*Зависит от вашего ПК
**С ограничениями по запросам

---

## 🚀 Быстрый старт с Ollama (Рекомендуется)

### Полная установка за 5 минут:

```bash
# 1. Установить Ollama
curl -fsSL https://ollama.ai/install.sh | sh

# 2. Загрузить модель
ollama pull llama3.2

# 3. Проверить что работает
ollama run llama3.2 "Привет!"

# 4. Настроить .env
cd /path/to/diebrowbar
cp .env.example .env
nano .env
```

В .env установите:
```env
LLM_PROVIDER=ollama
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=llama3.2
```

```bash
# 5. Запустить агента
./start.sh
```

Готово! ✅

---

## ⚙️ Настройка производительности

### Для Ollama на слабом ПК:

```env
# Используйте меньшую модель
OLLAMA_MODEL=llama3.2  # 3B параметров

# Уменьшите количество токенов
OLLAMA_MAX_TOKENS=500

# Увеличьте температуру для более быстрых ответов
OLLAMA_TEMPERATURE=0.5
```

### Для Ollama на мощном ПК:

```env
# Используйте более мощную модель
OLLAMA_MODEL=llama3.1:70b

# Больше токенов для детального анализа
OLLAMA_MAX_TOKENS=2000

# Меньше температуры для точности
OLLAMA_TEMPERATURE=0.1
```

---

## 🔧 Устранение проблем

### Ollama: "Connection refused"

**Проблема:** Ollama сервер не запущен

**Решение:**
```bash
# Запустите Ollama
ollama serve

# Или проверьте статус
curl http://localhost:11434/api/tags
```

### Ollama: "Model not found"

**Проблема:** Модель не загружена

**Решение:**
```bash
# Загрузите модель
ollama pull llama3.2

# Проверьте список моделей
ollama list
```

### Hugging Face: "Rate limit exceeded"

**Проблема:** Превышен лимит запросов

**Решение:**
- Используйте Ollama (без лимитов)
- Увеличьте `CHECK_INTERVAL_MINUTES` в .env
- Подождите несколько минут

### Ollama работает медленно

**Решения:**
1. Используйте меньшую модель: `llama3.2` вместо `llama3.1:70b`
2. Закройте другие программы
3. Уменьшите `OLLAMA_MAX_TOKENS`
4. Обновите RAM (рекомендуется 16+ GB)

---

## 💡 Рекомендации

### Для домашнего использования:
✅ **Ollama** с `llama3.2` - идеальный выбор

### Для использования на работе:
✅ **Perplexity** (если есть аккаунт) или **Ollama**

### Для тестирования:
✅ **Ollama** - быстро и бесплатно

### Если нужна максимальная точность:
✅ **Perplexity** с `llama-3.1-sonar-large-128k-online`
✅ Или платные **OpenAI/Anthropic**

---

## 📚 Дополнительные ресурсы

- **Ollama документация**: https://github.com/ollama/ollama
- **Ollama модели**: https://ollama.ai/library
- **Hugging Face модели**: https://huggingface.co/models
- **Perplexity API**: https://docs.perplexity.ai/

---

## ❓ FAQ

**Q: Какой провайдер самый лучший?**
A: Для бесплатного использования - **Ollama**. Для максимального качества с бюджетом - **Perplexity** или **OpenAI**.

**Q: Ollama будет работать на моём ПК?**
A: Если у вас 8+ GB RAM, да. Модель `llama3.2` (3B) работает даже на слабых ПК.

**Q: Можно ли использовать несколько провайдеров?**
A: Пока нет, но вы можете легко переключаться меняя `LLM_PROVIDER` в .env

**Q: Безопасно ли использовать Ollama?**
A: Да! Все данные остаются на вашем компьютере. Это самый приватный вариант.

**Q: Какая модель лучше для классификации email?**
A: `llama3.2` (Ollama) или `mistralai/Mistral-7B-Instruct-v0.2` (Hugging Face)

---

**🎉 Наслаждайтесь бесплатной AI классификацией email!**
