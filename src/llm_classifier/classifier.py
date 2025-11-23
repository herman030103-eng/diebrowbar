"""
Классификатор писем с использованием LLM
Email classifier using LLM
"""
from typing import Dict, Optional, List
import json
import httpx

from config.settings import Config
from src.utils.logger import logger


class EmailClassifier:
    """Классификатор для анализа и категоризации писем"""
    
    # Стандартные категории
    CATEGORIES = {
        "SPAM": "Спам и нежелательная почта",
        "PROMO": "Промо и реклама",
        "SOCIAL": "Социальные сети",
        "UPDATES": "Обновления и уведомления",
        "WORK": "Рабочая переписка",
        "PERSONAL": "Личная переписка",
        "FINANCE": "Финансы и платежи",
        "SHOPPING": "Покупки и заказы",
        "TRAVEL": "Путешествия",
        "IMPORTANT": "Важные письма"
    }
    
    def __init__(self):
        self.provider = Config.LLM_PROVIDER
        self.client = None
        
        if self.provider == "openai":
            from openai import OpenAI
            self.client = OpenAI(api_key=Config.OPENAI_API_KEY)
            self.model = Config.OPENAI_MODEL
            self.max_tokens = Config.OPENAI_MAX_TOKENS
            self.temperature = Config.OPENAI_TEMPERATURE
        elif self.provider == "anthropic":
            from anthropic import Anthropic
            self.client = Anthropic(api_key=Config.ANTHROPIC_API_KEY)
            self.model = Config.ANTHROPIC_MODEL
            self.max_tokens = Config.ANTHROPIC_MAX_TOKENS
        elif self.provider == "perplexity":
            # Perplexity использует OpenAI-совместимый API
            self.model = Config.PERPLEXITY_MODEL
            self.max_tokens = Config.PERPLEXITY_MAX_TOKENS
            self.temperature = Config.PERPLEXITY_TEMPERATURE
            self.api_key = Config.PERPLEXITY_API_KEY
        elif self.provider == "ollama":
            # Ollama локальный
            self.base_url = Config.OLLAMA_BASE_URL
            self.model = Config.OLLAMA_MODEL
            self.max_tokens = Config.OLLAMA_MAX_TOKENS
            self.temperature = Config.OLLAMA_TEMPERATURE
        elif self.provider == "huggingface":
            # Hugging Face Inference API
            self.model = Config.HUGGINGFACE_MODEL
            self.max_tokens = Config.HUGGINGFACE_MAX_TOKENS
            self.api_key = Config.HUGGINGFACE_API_KEY
        else:
            raise ValueError(f"Неподдерживаемый LLM провайдер: {self.provider}")
        
        logger.info(f"Инициализирован классификатор с провайдером: {self.provider}")
    
    def classify_email(self, email_data: Dict) -> Dict:
        """
        Классификация письма
        
        Returns:
            {
                "category": "CATEGORY_NAME",
                "confidence": 0.95,
                "reasoning": "Объяснение",
                "suggested_folder": "Folder Name",
                "is_spam": False,
                "should_delete": False,
                "should_archive": False,
                "priority": "high|medium|low"
            }
        """
        try:
            subject = email_data.get("subject", "")
            sender = email_data.get("sender", "")
            body = email_data.get("body", "")[:2000]  # Ограничение для LLM
            
            # Формирование промпта
            prompt = self._create_classification_prompt(subject, sender, body)
            
            # Вызов LLM
            if self.provider == "openai":
                response = self._classify_with_openai(prompt)
            elif self.provider == "anthropic":
                response = self._classify_with_anthropic(prompt)
            elif self.provider == "perplexity":
                response = self._classify_with_perplexity(prompt)
            elif self.provider == "ollama":
                response = self._classify_with_ollama(prompt)
            elif self.provider == "huggingface":
                response = self._classify_with_huggingface(prompt)
            else:
                raise ValueError(f"Неподдерживаемый провайдер: {self.provider}")
            
            # Парсинг ответа
            result = self._parse_llm_response(response)
            
            logger.info(f"Письмо классифицировано: {result['category']} (уверенность: {result['confidence']})")
            
            return result
            
        except Exception as e:
            logger.error(f"Ошибка классификации письма: {e}")
            return self._get_default_classification()
    
    def _create_classification_prompt(self, subject: str, sender: str, body: str) -> str:
        """Создание промпта для классификации"""
        categories_list = "\n".join([f"- {key}: {value}" for key, value in self.CATEGORIES.items()])
        
        prompt = f"""Проанализируй следующее email-письмо и классифицируй его.

Тема: {subject}
Отправитель: {sender}
Тело письма: {body}

Доступные категории:
{categories_list}

Верни ответ СТРОГО в формате JSON со следующей структурой:
{{
    "category": "CATEGORY_NAME",
    "confidence": 0.0-1.0,
    "reasoning": "краткое объяснение",
    "suggested_folder": "название папки для сортировки",
    "is_spam": true/false,
    "should_delete": true/false,
    "should_archive": true/false,
    "priority": "high/medium/low"
}}

Правила:
1. category должна быть одной из доступных категорий
2. confidence - число от 0 до 1
3. suggested_folder - предложенное имя папки на русском языке
4. is_spam - true если письмо выглядит как спам
5. should_delete - true если письмо следует удалить
6. should_archive - true если письмо можно заархивировать
7. priority - приоритет письма (high/medium/low)

Отвечай ТОЛЬКО JSON, без дополнительного текста."""
        
        return prompt
    
    def _classify_with_openai(self, prompt: str) -> str:
        """Классификация через OpenAI"""
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "Ты - эксперт по классификации email-писем. Ты всегда отвечаешь в формате JSON."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=self.max_tokens,
                temperature=self.temperature
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            logger.error(f"Ошибка вызова OpenAI API: {e}")
            raise
    
    def _classify_with_anthropic(self, prompt: str) -> str:
        """Классификация через Anthropic Claude"""
        try:
            response = self.client.messages.create(
                model=self.model,
                max_tokens=self.max_tokens,
                messages=[
                    {"role": "user", "content": prompt}
                ]
            )
            
            return response.content[0].text
            
        except Exception as e:
            logger.error(f"Ошибка вызова Anthropic API: {e}")
            raise
    
    def _classify_with_perplexity(self, prompt: str) -> str:
        """Классификация через Perplexity API"""
        try:
            # Perplexity использует OpenAI-совместимый API
            url = "https://api.perplexity.ai/chat/completions"
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            data = {
                "model": self.model,
                "messages": [
                    {"role": "system", "content": "Ты - эксперт по классификации email-писем. Ты всегда отвечаешь в формате JSON."},
                    {"role": "user", "content": prompt}
                ],
                "max_tokens": self.max_tokens,
                "temperature": self.temperature
            }
            
            response = httpx.post(url, headers=headers, json=data, timeout=30.0)
            response.raise_for_status()
            result = response.json()
            
            return result["choices"][0]["message"]["content"]
            
        except Exception as e:
            logger.error(f"Ошибка вызова Perplexity API: {e}")
            raise
    
    def _classify_with_ollama(self, prompt: str) -> str:
        """Классификация через Ollama (локально)"""
        try:
            url = f"{self.base_url}/api/generate"
            data = {
                "model": self.model,
                "prompt": f"Ты - эксперт по классификации email-писем. Ты всегда отвечаешь в формате JSON.\n\n{prompt}",
                "stream": False,
                "options": {
                    "temperature": self.temperature,
                    "num_predict": self.max_tokens
                }
            }
            
            response = httpx.post(url, json=data, timeout=60.0)
            response.raise_for_status()
            result = response.json()
            
            return result["response"]
            
        except Exception as e:
            logger.error(f"Ошибка вызова Ollama API: {e}")
            logger.error("Убедитесь, что Ollama запущен и модель загружена: ollama pull llama3.2")
            raise
    
    def _classify_with_huggingface(self, prompt: str) -> str:
        """Классификация через Hugging Face Inference API"""
        try:
            url = f"https://api-inference.huggingface.co/models/{self.model}"
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            data = {
                "inputs": f"Ты - эксперт по классификации email-писем. Ты всегда отвечаешь в формате JSON.\n\n{prompt}",
                "parameters": {
                    "max_new_tokens": self.max_tokens,
                    "return_full_text": False
                }
            }
            
            response = httpx.post(url, headers=headers, json=data, timeout=60.0)
            response.raise_for_status()
            result = response.json()
            
            # Hugging Face может вернуть разные форматы
            if isinstance(result, list) and len(result) > 0:
                return result[0].get("generated_text", "")
            elif isinstance(result, dict):
                return result.get("generated_text", "")
            
            return str(result)
            
        except Exception as e:
            logger.error(f"Ошибка вызова Hugging Face API: {e}")
            raise
    
    def _parse_llm_response(self, response: str) -> Dict:
        """Парсинг ответа от LLM"""
        try:
            # Попытка извлечь JSON из ответа
            response = response.strip()
            
            # Если ответ содержит markdown блок кода
            if "```json" in response:
                response = response.split("```json")[1].split("```")[0].strip()
            elif "```" in response:
                response = response.split("```")[1].split("```")[0].strip()
            
            # Парсинг JSON
            result = json.loads(response)
            
            # Валидация обязательных полей
            required_fields = ["category", "confidence", "suggested_folder"]
            for field in required_fields:
                if field not in result:
                    raise ValueError(f"Отсутствует обязательное поле: {field}")
            
            # Установка значений по умолчанию
            result.setdefault("reasoning", "")
            result.setdefault("is_spam", False)
            result.setdefault("should_delete", False)
            result.setdefault("should_archive", False)
            result.setdefault("priority", "medium")
            
            # Валидация категории
            if result["category"] not in self.CATEGORIES:
                result["category"] = "UPDATES"
            
            # Валидация confidence
            if not isinstance(result["confidence"], (int, float)) or not 0 <= result["confidence"] <= 1:
                result["confidence"] = 0.5
            
            return result
            
        except json.JSONDecodeError as e:
            logger.error(f"Ошибка парсинга JSON: {e}")
            logger.debug(f"Ответ LLM: {response}")
            return self._get_default_classification()
        except Exception as e:
            logger.error(f"Ошибка обработки ответа LLM: {e}")
            return self._get_default_classification()
    
    def _get_default_classification(self) -> Dict:
        """Классификация по умолчанию при ошибке"""
        return {
            "category": "UPDATES",
            "confidence": 0.5,
            "reasoning": "Автоматическая классификация (ошибка LLM)",
            "suggested_folder": "Inbox",
            "is_spam": False,
            "should_delete": False,
            "should_archive": False,
            "priority": "medium"
        }
    
    def analyze_sender_pattern(self, sender: str, email_history: List[Dict]) -> Dict:
        """
        Анализ паттерна отправителя на основе истории
        
        Args:
            sender: адрес отправителя
            email_history: история писем от этого отправителя
        
        Returns:
            Анализ паттерна отправителя
        """
        try:
            if not email_history:
                return {"pattern": "unknown", "recommendation": "none"}
            
            # Подсчет категорий
            categories = {}
            total = len(email_history)
            
            for email in email_history:
                category = email.get("category", "UPDATES")
                categories[category] = categories.get(category, 0) + 1
            
            # Определение доминирующей категории
            dominant_category = max(categories, key=categories.get)
            frequency = categories[dominant_category] / total
            
            result = {
                "sender": sender,
                "total_emails": total,
                "dominant_category": dominant_category,
                "frequency": frequency,
                "pattern": "consistent" if frequency > 0.7 else "mixed",
                "recommendation": "auto_sort" if frequency > 0.8 else "manual_review"
            }
            
            logger.info(f"Анализ отправителя {sender}: {result['pattern']}")
            
            return result
            
        except Exception as e:
            logger.error(f"Ошибка анализа паттерна отправителя: {e}")
            return {"pattern": "unknown", "recommendation": "none"}
