"""
ИИ-модуль для генерации контента (тренировки, питание, мотивация)
"""
from openai import AsyncOpenAI
from typing import Optional, Dict, Any
import json

from config import settings


class AITrainer:
    """ИИ Тренер для генерации персонализированного контента"""
    
    SYSTEM_PROMPT = """Ты — профессиональный персональный тренер и диетолог по имени "Фитнес Бот".

Твои ключевые качества:
- Профессионализм: даёшь только научно обоснованные рекомендации
- Эмпатия: понимаешь сложности и поддерживаешь
- Мотивация: вдохновляешь без токсичной позитивности
- Адаптивность: учитываешь индивидуальные особенности

Правила:
1. Всегда учитывай параметры пользователя (вес, рост, цель, ограничения)
2. Не давай медицинских диагнозов
3. При серьёзных проблемах со здоровьем направляй к врачу
4. Используй метрическую систему (кг, см, г)
5. Отвечай на русском языке
6. Будь конкретным — давай точные цифры и рекомендации"""

    def __init__(self):
        self.client = AsyncOpenAI(api_key=settings.openai_api_key) if settings.openai_api_key else None
        self.model = settings.ai_model
    
    async def generate_workout(self, user_profile: Dict[str, Any]) -> str:
        """Генерация тренировки на основе профиля пользователя"""
        
        prompt = f"""Составь тренировку для пользователя с параметрами:
- Цель: {user_profile.get('primary_goal', 'поддержание формы')}
- Уровень: {user_profile.get('fitness_level', 'beginner')}
- Место: {user_profile.get('training_location', 'gym')}
- Длительность: {user_profile.get('training_duration', 45)} минут
- Тренировочных дней в неделю: {user_profile.get('training_days_per_week', 3)}
- Ограничения/травмы: {', '.join(user_profile.get('health_conditions', [])) or 'нет'}
- Оборудование: {', '.join(user_profile.get('available_equipment', [])) or 'базовое'}

Формат ответа:
🏋️ ТРЕНИРОВКА: [Название]
⏱️ [Длительность] мин

🔥 РАЗМИНКА (5-7 мин):
[Список упражнений]

💪 ОСНОВНАЯ ЧАСТЬ:
[Упражнения с подходами, повторами и отдыхом]

🧘 ЗАМИНКА (5 мин):
[Растяжка]"""

        return await self._generate(prompt)
    
    async def generate_meal_plan(self, user_profile: Dict[str, Any]) -> str:
        """Генерация плана питания"""
        
        prompt = f"""Составь меню на день для пользователя:
- Калории: {user_profile.get('target_calories', 2000)} ккал
- Белки: {user_profile.get('target_protein', 150)} г
- Жиры: {user_profile.get('target_fat', 70)} г
- Углеводы: {user_profile.get('target_carbs', 200)} г
- Тип питания: {user_profile.get('diet_type', 'omnivore')}
- Аллергии: {', '.join(user_profile.get('allergies', [])) or 'нет'}
- Нелюбимые продукты: {', '.join(user_profile.get('disliked_foods', [])) or 'нет'}
- Приёмов пищи в день: {user_profile.get('meals_per_day', 4)}

Формат:
🍽️ МЕНЮ НА ДЕНЬ

🌅 ЗАВТРАК (время) — XXX ккал
[Блюда с граммовкой]

[И так далее для каждого приёма пищи]

📊 ИТОГО: калории/белки/жиры/углеводы"""

        return await self._generate(prompt)
    
    async def generate_motivation(self, context: Dict[str, Any]) -> str:
        """Генерация мотивационного сообщения"""
        
        situation = context.get('situation', 'general')
        user_name = context.get('name', 'друг')
        streak = context.get('streak_days', 0)
        
        prompts = {
            'morning': f"Напиши короткое мотивационное утреннее сообщение для {user_name}. Streak: {streak} дней.",
            'workout_done': f"Поздравь {user_name} с выполненной тренировкой. Streak: {streak} дней.",
            'workout_skipped': f"Поддержи {user_name}, который пропустил тренировку. Без осуждения.",
            'plateau': f"Поддержи {user_name}, у которого вес стоит на месте уже 2 недели.",
            'goal_reached': f"Поздравь {user_name} с достижением цели! Это большая победа!",
            'general': f"Напиши мотивационное сообщение для {user_name}, занимающегося фитнесом."
        }
        
        prompt = prompts.get(situation, prompts['general'])
        prompt += "\nОтвет должен быть 2-3 предложения, тёплый и поддерживающий."
        
        return await self._generate(prompt)
    
    async def answer_question(self, question: str, user_profile: Dict[str, Any]) -> str:
        """Ответ на вопрос пользователя"""
        
        context = f"""Параметры пользователя:
- Цель: {user_profile.get('primary_goal', 'не указана')}
- Вес: {user_profile.get('current_weight', '?')} кг
- Уровень: {user_profile.get('fitness_level', 'beginner')}
- Ограничения: {', '.join(user_profile.get('health_conditions', [])) or 'нет'}

Вопрос пользователя: {question}

Дай конкретный, полезный ответ. Если вопрос касается медицины — рекомендуй обратиться к врачу."""

        return await self._generate(context)
    
    async def _generate(self, prompt: str) -> str:
        """Генерация текста через OpenAI API"""
        
        if not self.client:
            return self._get_fallback_response()
        
        try:
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": self.SYSTEM_PROMPT},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=1500,
                temperature=0.7
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            print(f"AI Error: {e}")
            return self._get_fallback_response()
    
    def _get_fallback_response(self) -> str:
        """Fallback ответ при недоступности API"""
        return (
            "К сожалению, сейчас не могу сгенерировать персональный ответ. "
            "Попробуй позже или воспользуйся стандартными планами в меню."
        )


# Глобальный экземпляр
ai_trainer = AITrainer()
