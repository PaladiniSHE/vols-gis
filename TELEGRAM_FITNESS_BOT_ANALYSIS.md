# Анализ профессиональных Telegram-приложений "Личный тренер"

## Оглавление

1. [Обзор рынка](#обзор-рынка)
2. [Лучшие профессиональные решения](#лучшие-профессиональные-решения)
3. [Анализ визуального интерфейса](#анализ-визуального-интерфейса)
4. [Функциональный анализ](#функциональный-анализ)
5. [Техническая документация](#техническая-документация)
6. [Программы для похудения](#программы-для-похудения)
7. [Сбалансированное питание](#сбалансированное-питание)
8. [Рекомендации по реализации](#рекомендации-по-реализации)

---

## Обзор рынка

### Текущее состояние рынка фитнес-ботов в Telegram

Telegram стал одной из ведущих платформ для фитнес и wellness приложений благодаря:
- **950+ млн** активных пользователей
- **Telegram Mini Apps (TWA)** - полноценные веб-приложения внутри мессенджера
- **Бесплатность** инфраструктуры для разработчиков
- **Высокая вовлеченность** - пользователи открывают Telegram ~23 раза в день

### Категории фитнес-ботов

| Категория | Описание | Примеры функций |
|-----------|----------|-----------------|
| **Трекеры питания** | Подсчет калорий, БЖУ | Ввод еды, база продуктов, дневник |
| **Тренировочные боты** | Программы тренировок | Видео/гифки упражнений, таймеры |
| **Комплексные решения** | Питание + тренировки | Персонализация, прогресс |
| **AI-коучи** | ИИ-консультации | GPT-интеграция, персональные советы |

---

## Лучшие профессиональные решения

### 1. @FatSecretBot / FatSecret

**Тип:** Трекер питания  
**Оценка:** ⭐⭐⭐⭐⭐ (4.8/5)

**Функционал:**
- База данных 14+ млн продуктов
- Сканирование штрих-кодов
- Распознавание еды по фото (AI)
- Синхронизация с фитнес-устройствами
- Социальные функции (сообщества, челленджи)

**Интерфейс:**
```
┌─────────────────────────────────────┐
│  🍎 FatSecret                       │
├─────────────────────────────────────┤
│  📊 Сегодня: 1,450 / 2,000 ккал    │
│  ████████████░░░░░░ 72%            │
├─────────────────────────────────────┤
│  🥣 Завтрак     420 ккал           │
│  🍜 Обед        580 ккал           │
│  🍽️ Ужин        450 ккал           │
│  🍿 Перекусы    ─ ккал             │
├─────────────────────────────────────┤
│  [📷 Добавить]  [🔍 Поиск]         │
│  [📊 Отчет]     [⚙️ Настройки]     │
└─────────────────────────────────────┘
```

### 2. @WorkoutBot / Workout Tracker

**Тип:** Тренировочный бот  
**Оценка:** ⭐⭐⭐⭐ (4.5/5)

**Функционал:**
- 500+ упражнений с анимациями
- Готовые программы (для дома/зала)
- Кастомные тренировки
- Таймер отдыха с уведомлениями
- Статистика прогресса по упражнениям

**Паттерн взаимодействия:**
```
Пользователь: /start_workout
Бот: 🏋️ Выберите тренировку:
     
     [💪 Верхняя часть тела]
     [🦵 Нижняя часть тела]
     [🫁 Кардио]
     [📋 Мои программы]

Пользователь: [💪 Верхняя часть тела]
Бот: Упражнение 1/8: Жим лежа
     
     [GIF анимация упражнения]
     
     📝 Рекомендация: 3×12 повторений
     ⚖️ Прошлый раз: 60 кг
     
     Введите вес и повторения:
     Пример: 65 12 12 10
```

### 3. @MyFitnessPal_Bot

**Тип:** Комплексное решение  
**Оценка:** ⭐⭐⭐⭐⭐ (4.7/5)

**Функционал:**
- Интеграция с MyFitnessPal API
- Подсчет КБЖУ
- Планирование приемов пищи
- Рецепты с расчетом калорий
- Водный баланс
- Интеграция с Apple Health / Google Fit

### 4. @coach_sport_bot

**Тип:** AI-коуч  
**Оценка:** ⭐⭐⭐⭐ (4.3/5)

**Функционал:**
- Персональные планы тренировок на основе целей
- AI-анализ прогресса
- Адаптивные рекомендации
- Мотивационные напоминания
- Голосовые заметки

### 5. @CalorieCounterBot

**Тип:** Трекер калорий (русскоязычный)  
**Оценка:** ⭐⭐⭐⭐ (4.4/5)

**Функционал:**
- База продуктов СНГ (20,000+ продуктов)
- Русскоязычный интерфейс
- Рецепты с подсчетом калорий
- Еженедельные отчеты
- Групповые челленджи

---

## Анализ визуального интерфейса

### Принципы UI/UX лучших решений

#### 1. Inline Keyboards (Инлайн-кнопки)

```
Преимущества:
- Минимум ввода текста
- Быстрая навигация
- Интуитивно понятно

Пример структуры:
┌────────────────────────────────┐
│    🎯 Ваша цель                │
├────────────────────────────────┤
│ [🔥 Похудение]                 │
│ [💪 Набор массы]               │
│ [🏃 Поддержание формы]         │
│ [🧘 Здоровый образ жизни]      │
└────────────────────────────────┘
```

#### 2. Progress Bars (Прогресс-бары)

```
Калории:   ████████░░░░░░ 1,450/2,000 (72%)
Белки:     ██████████████ 120/100г ✅
Жиры:      ██████████░░░░ 65/80г
Углеводы:  ████████░░░░░░ 180/250г
Вода:      ██████░░░░░░░░ 1.2/2.0л
```

#### 3. Emoji-иконография

| Категория | Emoji | Использование |
|-----------|-------|---------------|
| Приемы пищи | 🌅🌞🌆🌙 | Утро/день/вечер/ночь |
| Макросы | 🥩🧈🍞 | Белки/жиры/углеводы |
| Активность | 🚶🏃🚴🏋️ | Типы упражнений |
| Прогресс | 📈📉⚖️🎯 | Графики/цели |
| Вода | 💧🥤💦 | Водный баланс |
| Достижения | 🏆🥇🔥⭐ | Награды/серии |

#### 4. Telegram Mini Apps (TWA) - Современный стандарт

```
┌─────────────────────────────────────┐
│  ← Личный тренер         ⚙️  👤    │
├─────────────────────────────────────┤
│                                     │
│  ┌─────────────────────────────┐   │
│  │    📊 ДНЕВНИК ПИТАНИЯ       │   │
│  │                             │   │
│  │  Калории сегодня           │   │
│  │     1,847 / 2,200          │   │
│  │  ▓▓▓▓▓▓▓▓▓▓▓░░░ 84%       │   │
│  │                             │   │
│  │  Б: 98г  Ж: 72г  У: 215г  │   │
│  └─────────────────────────────┘   │
│                                     │
│  ┌─────────┐ ┌─────────┐          │
│  │ 🍳      │ │ 🍜      │          │
│  │ Завтрак │ │ Обед    │          │
│  │ 520ккал │ │ 680ккал │          │
│  └─────────┘ └─────────┘          │
│                                     │
│  ┌─────────┐ ┌─────────┐          │
│  │ 🍽️      │ │ 🍎      │          │
│  │ Ужин    │ │ Перекус │          │
│  │ 450ккал │ │ 197ккал │          │
│  └─────────┘ └─────────┘          │
│                                     │
├─────────────────────────────────────┤
│  🏠    📊    ➕    🏋️    👤      │
│  Дом   Стат  Добав Трен  Профиль  │
└─────────────────────────────────────┘
```

### Цветовая схема

```css
/* Рекомендуемая палитра для фитнес-ботов */

:root {
  /* Основные цвета */
  --primary: #4CAF50;      /* Зеленый - здоровье, успех */
  --secondary: #2196F3;    /* Синий - вода, спокойствие */
  --accent: #FF9800;       /* Оранжевый - энергия, активность */
  
  /* Макронутриенты */
  --protein: #E53935;      /* Красный - белки */
  --fat: #FFC107;          /* Желтый - жиры */
  --carbs: #9C27B0;        /* Фиолетовый - углеводы */
  
  /* Прогресс */
  --success: #4CAF50;      /* Цель достигнута */
  --warning: #FF9800;      /* Приближение к лимиту */
  --danger: #F44336;       /* Превышение */
  
  /* Фон */
  --bg-light: #F5F5F5;
  --bg-dark: #1E1E1E;
  --card: #FFFFFF;
}
```

---

## Функциональный анализ

### Ключевые функции топовых решений

#### 1. Onboarding (Первичная настройка)

```
Шаг 1: Приветствие
─────────────────────────
👋 Привет! Я твой личный тренер.
Давай настроим программу под тебя!

[🚀 Начать]

Шаг 2: Сбор данных
─────────────────────────
📏 Укажи свой рост (см):
[150] [160] [170] [180] [190] [200+]

⚖️ Укажи свой вес (кг):
[Ввести вручную]

🎂 Укажи возраст:
[Ввести вручную]

👤 Выбери пол:
[♂️ Мужской] [♀️ Женский]

Шаг 3: Определение цели
─────────────────────────
🎯 Какая у тебя цель?

[🔥 Похудеть]
   Снижение веса на 0.5-1 кг/неделю
   
[💪 Набрать мышечную массу]
   Профицит калорий + силовые
   
[🏃 Поддерживать форму]
   Сбалансированное питание
   
[🧘 Улучшить здоровье]
   Правильные привычки

Шаг 4: Уровень активности
─────────────────────────
🏃 Уровень твоей активности?

[🛋️ Минимальная]
   Сидячая работа, без спорта
   
[🚶 Низкая]
   1-2 тренировки в неделю
   
[🏃 Средняя]
   3-4 тренировки в неделю
   
[🔥 Высокая]
   5-7 тренировок в неделю
   
[⚡ Очень высокая]
   Профессиональный спорт

Шаг 5: Результат расчета
─────────────────────────
✅ Твой план готов!

📊 Твои параметры:
├ BMI: 24.2 (норма)
├ BMR: 1,720 ккал
└ TDEE: 2,408 ккал

🎯 Для похудения рекомендую:
├ Калории: 1,908 ккал/день (-500)
├ Белки: 120г (25%)
├ Жиры: 64г (30%)
└ Углеводы: 214г (45%)

💧 Вода: 2.5 л/день

[✅ Принять план]
[✏️ Настроить вручную]
```

#### 2. Дневник питания

```python
# Структура данных дневника питания
class FoodEntry:
    meal_type: str        # breakfast, lunch, dinner, snack
    food_name: str
    portion_size: float   # в граммах
    calories: float
    protein: float
    fat: float
    carbs: float
    fiber: float
    timestamp: datetime
    
# Функции добавления еды
FOOD_INPUT_METHODS = [
    "text_search",        # Поиск по названию
    "barcode_scan",       # Сканирование штрих-кода
    "photo_recognition",  # AI распознавание фото
    "recent_foods",       # Недавние продукты
    "favorites",          # Избранное
    "custom_food",        # Свой продукт
    "recipe",             # Готовые рецепты
    "meal_copy"           # Копирование приема пищи
]
```

#### 3. Тренировочный модуль

```
СТРУКТУРА ТРЕНИРОВКИ
═══════════════════════════════════

🏋️ Тренировка: Верхняя часть тела
⏱️ Примерная длительность: 45 мин
🔥 Ожидаемый расход: 280 ккал

───────────────────────────────────
📍 Разминка (5 мин)
───────────────────────────────────
1. Вращение плечами - 30 сек
2. Махи руками - 30 сек
3. Наклоны корпуса - 1 мин
4. Прыжки на месте - 2 мин

───────────────────────────────────
💪 Основная часть
───────────────────────────────────

▶️ Упражнение 1/6
┌─────────────────────────────────┐
│  ЖИМ ЛЕЖА                       │
│  [GIF анимация]                 │
│                                 │
│  📊 Рабочий вес: 60 кг         │
│  🔄 Подходы: 4 × 10-12         │
│  ⏱️ Отдых: 90 сек              │
│                                 │
│  💡 Советы:                     │
│  • Лопатки сведены             │
│  • Стопы на полу               │
│  • Контролируй негативную фазу │
└─────────────────────────────────┘

[✅ Записать результат]
[⏭️ Пропустить]
[📹 Смотреть технику]

───────────────────────────────────
🧘 Заминка (5 мин)
───────────────────────────────────
1. Растяжка грудных - 1 мин
2. Растяжка трицепсов - 1 мин
3. Растяжка плеч - 1 мин
4. Дыхательные упражнения - 2 мин
```

#### 4. Система напоминаний

```
⏰ НАСТРОЙКА УВЕДОМЛЕНИЙ

🍳 Завтрак
   [08:00] [Вкл/Выкл]
   
🍜 Обед
   [13:00] [Вкл/Выкл]
   
🍽️ Ужин
   [19:00] [Вкл/Выкл]

💧 Напоминания о воде
   [Каждые 2 часа] [Вкл/Выкл]
   
🏋️ Напоминания о тренировке
   [Пн, Ср, Пт в 18:00] [Вкл/Выкл]
   
⚖️ Напоминание взвеситься
   [Каждый понедельник в 07:00] [Вкл/Выкл]

📊 Еженедельный отчет
   [Воскресенье в 20:00] [Вкл/Выкл]
```

#### 5. Геймификация

```
🏆 СИСТЕМА ДОСТИЖЕНИЙ

═══════════════════════════════════
🔥 СЕРИИ (STREAKS)
───────────────────────────────────
🔥 7 дней подряд - Неделя дисциплины
🔥 30 дней подряд - Месяц силы воли
🔥 100 дней подряд - Железная привычка
🔥 365 дней подряд - Легенда

═══════════════════════════════════
🎯 ЦЕЛИ
───────────────────────────────────
⚖️ Минус 5 кг - Первые результаты
⚖️ Минус 10 кг - Трансформация
💧 30 дней нормы воды - Водный баланс
🏋️ 50 тренировок - Атлет

═══════════════════════════════════
📈 УРОВНИ
───────────────────────────────────
Уровень 1-10: Новичок 🌱
Уровень 11-25: Любитель 🌿
Уровень 26-50: Продвинутый 🌲
Уровень 51-100: Эксперт 🌳
Уровень 100+: Мастер 👑

XP начисляется за:
• Логирование еды: +10 XP
• Тренировку: +50 XP
• Достижение дневной цели: +25 XP
• Серию 7 дней: +100 XP
```

---

## Техническая документация

### Архитектура Telegram Bot

```
┌─────────────────────────────────────────────────────────────┐
│                      АРХИТЕКТУРА                            │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  ┌─────────────┐    ┌─────────────┐    ┌─────────────────┐ │
│  │   Telegram  │◄──►│   Webhook   │◄──►│   Bot Server    │ │
│  │   Client    │    │   Server    │    │   (Python)      │ │
│  └─────────────┘    └─────────────┘    └────────┬────────┘ │
│                                                  │          │
│                            ┌─────────────────────┼──────┐  │
│                            │                     ▼      │  │
│                            │  ┌─────────────────────┐   │  │
│                            │  │   Business Logic    │   │  │
│                            │  │   ─────────────────  │   │  │
│                            │  │   • User Service    │   │  │
│                            │  │   • Food Service    │   │  │
│                            │  │   • Workout Service │   │  │
│                            │  │   • Stats Service   │   │  │
│                            │  │   • AI Service      │   │  │
│                            │  └──────────┬──────────┘   │  │
│                            │             │              │  │
│                            │  ┌──────────▼──────────┐   │  │
│                            │  │    Data Access      │   │  │
│                            │  │   ─────────────────  │   │  │
│                            │  │   • PostgreSQL      │   │  │
│                            │  │   • Redis (cache)   │   │  │
│                            │  │   • S3 (media)      │   │  │
│                            │  └─────────────────────┘   │  │
│                            │                            │  │
│                            └────────────────────────────┘  │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

### Технологический стек

```yaml
# Рекомендуемый стек для фитнес-бота

backend:
  language: Python 3.11+
  frameworks:
    - aiogram 3.x           # Асинхронная библиотека для Telegram
    - FastAPI               # REST API для Mini App
    - SQLAlchemy 2.0        # ORM
    - Alembic               # Миграции БД
    - Celery                # Фоновые задачи
    - Redis                 # Кэш, очереди, сессии
    
database:
  primary: PostgreSQL 15+
  cache: Redis 7+
  search: Elasticsearch    # Поиск по продуктам
  
ai_services:
  food_recognition: 
    - Google Cloud Vision
    - Clarifai Food Model
    - Custom CNN (TensorFlow)
  nlp:
    - OpenAI GPT-4
    - Anthropic Claude
    - Local LLaMA
    
external_apis:
  food_databases:
    - USDA FoodData Central
    - Open Food Facts
    - Nutritionix
  fitness_tracking:
    - Strava API
    - Fitbit API
    - Apple HealthKit (через webhook)
    - Google Fit API

infrastructure:
  hosting: 
    - VPS (Hetzner, DigitalOcean)
    - Kubernetes (для масштабирования)
  cdn: Cloudflare
  monitoring: 
    - Prometheus + Grafana
    - Sentry (ошибки)
```

### Модели данных

```python
# models/user.py
from sqlalchemy import Column, Integer, String, Float, DateTime, Enum
from sqlalchemy.dialects.postgresql import JSONB

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True)
    telegram_id = Column(BigInteger, unique=True, index=True)
    username = Column(String(255))
    first_name = Column(String(255))
    
    # Физические параметры
    height = Column(Float)  # см
    weight = Column(Float)  # кг
    birth_date = Column(Date)
    gender = Column(Enum('male', 'female', name='gender_enum'))
    
    # Расчетные показатели
    bmr = Column(Float)  # Базовый метаболизм
    tdee = Column(Float)  # Суточный расход
    
    # Цели
    goal_type = Column(Enum('lose', 'gain', 'maintain', name='goal_enum'))
    goal_weight = Column(Float)
    daily_calories = Column(Integer)
    daily_protein = Column(Float)
    daily_fat = Column(Float)
    daily_carbs = Column(Float)
    daily_water = Column(Float)  # литры
    
    # Уровень активности (1.2-1.9)
    activity_level = Column(Float, default=1.5)
    
    # Настройки
    settings = Column(JSONB, default={})
    timezone = Column(String(50), default='Europe/Moscow')
    
    # Геймификация
    xp = Column(Integer, default=0)
    level = Column(Integer, default=1)
    current_streak = Column(Integer, default=0)
    longest_streak = Column(Integer, default=0)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, onupdate=datetime.utcnow)


# models/food_entry.py
class FoodEntry(Base):
    __tablename__ = "food_entries"
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), index=True)
    food_id = Column(Integer, ForeignKey("foods.id"))
    
    meal_type = Column(Enum('breakfast', 'lunch', 'dinner', 'snack'))
    portion_size = Column(Float)  # граммы
    
    # Нутриенты (рассчитываются на порцию)
    calories = Column(Float)
    protein = Column(Float)
    fat = Column(Float)
    carbs = Column(Float)
    fiber = Column(Float)
    sugar = Column(Float)
    sodium = Column(Float)
    
    logged_at = Column(DateTime, default=datetime.utcnow)
    date = Column(Date, index=True)  # для быстрой выборки по дням


# models/food.py
class Food(Base):
    __tablename__ = "foods"
    
    id = Column(Integer, primary_key=True)
    name = Column(String(500), index=True)
    brand = Column(String(255))
    barcode = Column(String(50), unique=True, index=True)
    
    # На 100г продукта
    calories_100g = Column(Float)
    protein_100g = Column(Float)
    fat_100g = Column(Float)
    carbs_100g = Column(Float)
    fiber_100g = Column(Float)
    sugar_100g = Column(Float)
    sodium_100g = Column(Float)
    
    # Типичные порции
    serving_size = Column(Float)  # граммы
    serving_name = Column(String(100))  # "1 штука", "1 стакан"
    
    # Категория
    category = Column(String(100))
    
    # Источник данных
    source = Column(String(50))  # 'usda', 'openfoodfacts', 'user'
    external_id = Column(String(100))
    
    # Верификация
    is_verified = Column(Boolean, default=False)
    usage_count = Column(Integer, default=0)


# models/workout.py
class Workout(Base):
    __tablename__ = "workouts"
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), index=True)
    
    name = Column(String(255))
    workout_type = Column(String(50))  # strength, cardio, flexibility
    
    started_at = Column(DateTime)
    finished_at = Column(DateTime)
    duration_minutes = Column(Integer)
    
    calories_burned = Column(Float)
    
    notes = Column(Text)
    rating = Column(Integer)  # 1-5
    
    # Для связи с программой тренировок
    program_id = Column(Integer, ForeignKey("workout_programs.id"))
    program_day = Column(Integer)


class WorkoutExercise(Base):
    __tablename__ = "workout_exercises"
    
    id = Column(Integer, primary_key=True)
    workout_id = Column(Integer, ForeignKey("workouts.id"))
    exercise_id = Column(Integer, ForeignKey("exercises.id"))
    
    order = Column(Integer)
    
    # Для силовых
    sets_completed = Column(Integer)
    reps_per_set = Column(ARRAY(Integer))  # [12, 10, 8]
    weight_per_set = Column(ARRAY(Float))  # [60, 65, 70]
    
    # Для кардио
    duration_seconds = Column(Integer)
    distance_meters = Column(Float)
    avg_heart_rate = Column(Integer)


# models/water_entry.py
class WaterEntry(Base):
    __tablename__ = "water_entries"
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), index=True)
    
    amount_ml = Column(Integer)
    logged_at = Column(DateTime, default=datetime.utcnow)
    date = Column(Date, index=True)


# models/weight_log.py
class WeightLog(Base):
    __tablename__ = "weight_logs"
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), index=True)
    
    weight = Column(Float)  # кг
    body_fat_percent = Column(Float)  # % жира (опционально)
    
    logged_at = Column(DateTime, default=datetime.utcnow)
    date = Column(Date, index=True, unique=True)  # одна запись в день
```

### API для Mini App

```python
# api/routes.py
from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="Fitness Bot API")

# CORS для Mini App
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Аутентификация через Telegram WebApp data
@app.middleware("http")
async def validate_telegram_data(request: Request, call_next):
    init_data = request.headers.get("X-Telegram-Init-Data")
    if not validate_init_data(init_data, BOT_TOKEN):
        return JSONResponse(status_code=401, content={"error": "Unauthorized"})
    return await call_next(request)

# Endpoints
@app.get("/api/v1/user/profile")
async def get_profile(user: User = Depends(get_current_user)):
    return UserProfileSchema.from_orm(user)

@app.get("/api/v1/diary/{date}")
async def get_diary(date: date, user: User = Depends(get_current_user)):
    """Получить дневник питания за день"""
    entries = await food_service.get_entries_by_date(user.id, date)
    totals = await food_service.calculate_totals(entries)
    return {
        "date": date,
        "entries": entries,
        "totals": totals,
        "goals": user.daily_goals,
        "progress": calculate_progress(totals, user.daily_goals)
    }

@app.post("/api/v1/diary/food")
async def add_food(
    entry: FoodEntryCreate,
    user: User = Depends(get_current_user)
):
    """Добавить продукт в дневник"""
    return await food_service.add_entry(user.id, entry)

@app.get("/api/v1/foods/search")
async def search_foods(
    q: str,
    limit: int = 20,
    user: User = Depends(get_current_user)
):
    """Поиск продуктов"""
    results = await food_service.search(q, user.id, limit)
    return results

@app.post("/api/v1/foods/barcode/{barcode}")
async def get_by_barcode(barcode: str):
    """Получить продукт по штрих-коду"""
    food = await food_service.get_by_barcode(barcode)
    if not food:
        # Поиск во внешних API
        food = await external_api.lookup_barcode(barcode)
    return food

@app.post("/api/v1/foods/recognize")
async def recognize_food(file: UploadFile):
    """AI распознавание еды по фото"""
    image_data = await file.read()
    predictions = await ai_service.recognize_food(image_data)
    return {"predictions": predictions}

@app.get("/api/v1/stats/weekly")
async def get_weekly_stats(user: User = Depends(get_current_user)):
    """Статистика за неделю"""
    return await stats_service.get_weekly(user.id)

@app.get("/api/v1/workouts")
async def get_workouts(
    skip: int = 0,
    limit: int = 20,
    user: User = Depends(get_current_user)
):
    """Список тренировок пользователя"""
    return await workout_service.get_user_workouts(user.id, skip, limit)
```

### Telegram Bot Handlers

```python
# bot/handlers/food.py
from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext

router = Router()

@router.message(Command("food"))
async def cmd_food(message: Message):
    """Главное меню питания"""
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="🍳 Завтрак", callback_data="meal:breakfast"),
            InlineKeyboardButton(text="🍜 Обед", callback_data="meal:lunch"),
        ],
        [
            InlineKeyboardButton(text="🍽️ Ужин", callback_data="meal:dinner"),
            InlineKeyboardButton(text="🍎 Перекус", callback_data="meal:snack"),
        ],
        [
            InlineKeyboardButton(text="📊 Статистика за сегодня", callback_data="stats:today"),
        ],
        [
            InlineKeyboardButton(text="📱 Открыть дневник", web_app=WebAppInfo(url=WEBAPP_URL)),
        ]
    ])
    
    # Получаем текущую статистику
    stats = await get_today_stats(message.from_user.id)
    
    text = f"""
📊 *Питание сегодня*

🔥 Калории: {stats.calories}/{stats.goal_calories} ккал
{create_progress_bar(stats.calories, stats.goal_calories)}

🥩 Белки: {stats.protein:.0f}г / {stats.goal_protein}г
🧈 Жиры: {stats.fat:.0f}г / {stats.goal_fat}г
🍞 Углеводы: {stats.carbs:.0f}г / {stats.goal_carbs}г

Выберите прием пищи для добавления:
"""
    
    await message.answer(text, reply_markup=keyboard, parse_mode="Markdown")


@router.callback_query(F.data.startswith("meal:"))
async def select_meal(callback: CallbackQuery, state: FSMContext):
    """Выбор приема пищи"""
    meal_type = callback.data.split(":")[1]
    meal_names = {
        "breakfast": "🍳 Завтрак",
        "lunch": "🍜 Обед", 
        "dinner": "🍽️ Ужин",
        "snack": "🍎 Перекус"
    }
    
    await state.update_data(meal_type=meal_type)
    await state.set_state(FoodStates.waiting_for_food)
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🔍 Поиск продукта", callback_data="search:food")],
        [InlineKeyboardButton(text="📷 Сканировать штрих-код", callback_data="scan:barcode")],
        [InlineKeyboardButton(text="🖼️ Распознать по фото", callback_data="recognize:photo")],
        [InlineKeyboardButton(text="⭐ Избранное", callback_data="favorites:list")],
        [InlineKeyboardButton(text="🕐 Недавние", callback_data="recent:list")],
        [InlineKeyboardButton(text="◀️ Назад", callback_data="food:menu")],
    ])
    
    await callback.message.edit_text(
        f"{meal_names[meal_type]}\n\nКак добавить продукт?",
        reply_markup=keyboard
    )


@router.message(FoodStates.waiting_for_food, F.text)
async def search_food(message: Message, state: FSMContext):
    """Поиск продукта по тексту"""
    query = message.text
    results = await food_service.search(query, limit=10)
    
    if not results:
        await message.answer("❌ Продукты не найдены. Попробуйте другой запрос.")
        return
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(
            text=f"{r.name} ({r.calories_100g} ккал/100г)",
            callback_data=f"food:{r.id}"
        )]
        for r in results
    ] + [[InlineKeyboardButton(text="➕ Добавить свой продукт", callback_data="food:custom")]])
    
    await message.answer(
        f"🔍 Найдено {len(results)} продуктов по запросу \"{query}\":",
        reply_markup=keyboard
    )


@router.message(FoodStates.waiting_for_food, F.photo)
async def recognize_food_photo(message: Message, state: FSMContext):
    """AI распознавание еды по фото"""
    await message.answer("🤖 Анализирую фото...")
    
    # Скачиваем фото
    photo = message.photo[-1]
    file = await message.bot.get_file(photo.file_id)
    photo_data = await message.bot.download_file(file.file_path)
    
    # Отправляем в AI сервис
    predictions = await ai_service.recognize_food(photo_data.read())
    
    if not predictions:
        await message.answer("❌ Не удалось распознать еду на фото. Попробуйте другое фото или найдите вручную.")
        return
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(
            text=f"{p.name} ({p.confidence:.0%})",
            callback_data=f"ai_food:{p.food_id}"
        )]
        for p in predictions[:5]
    ])
    
    await message.answer(
        "🤖 Вот что я распознал на фото.\nВыберите правильный вариант:",
        reply_markup=keyboard
    )


# Утилита для создания прогресс-бара
def create_progress_bar(current: float, goal: float, length: int = 15) -> str:
    if goal <= 0:
        return "░" * length
    
    percent = min(current / goal, 1.5)  # Максимум 150%
    filled = int(percent * length)
    
    if percent > 1:
        # Превышение - красный цвет
        return "▓" * length + f" ⚠️ +{int((percent-1)*100)}%"
    
    return "▓" * filled + "░" * (length - filled)
```

---

## Программы для похудения

### Научно обоснованные подходы

#### 1. Дефицит калорий (Calorie Deficit)

```
📊 ФОРМУЛА РАСЧЕТА

1. BMR (Базовый метаболизм) по формуле Mifflin-St Jeor:
   
   Мужчины: BMR = 10 × вес(кг) + 6.25 × рост(см) − 5 × возраст + 5
   Женщины: BMR = 10 × вес(кг) + 6.25 × рост(см) − 5 × возраст − 161

2. TDEE (Суточный расход) = BMR × Коэффициент активности
   
   Коэффициенты:
   1.2  - Минимальная (сидячий образ жизни)
   1.375 - Низкая (1-3 тренировки в неделю)
   1.55 - Средняя (3-5 тренировок в неделю)
   1.725 - Высокая (6-7 тренировок в неделю)
   1.9  - Очень высокая (физическая работа + спорт)

3. Калории для похудения = TDEE - Дефицит
   
   Рекомендуемый дефицит:
   • Медленное похудение: 250-300 ккал/день (-0.25 кг/неделю)
   • Умеренное: 500 ккал/день (-0.5 кг/неделю)
   • Быстрое: 750-1000 ккал/день (-0.75-1 кг/неделю)
   
   ⚠️ Минимум: 1200 ккал для женщин, 1500 ккал для мужчин
```

```python
# services/calculator.py

def calculate_bmr(weight: float, height: float, age: int, gender: str) -> float:
    """Расчет базового метаболизма по формуле Mifflin-St Jeor"""
    bmr = 10 * weight + 6.25 * height - 5 * age
    if gender == 'male':
        bmr += 5
    else:
        bmr -= 161
    return round(bmr, 0)

def calculate_tdee(bmr: float, activity_level: float) -> float:
    """Расчет суточного расхода калорий"""
    return round(bmr * activity_level, 0)

def calculate_weight_loss_calories(
    tdee: float, 
    goal: str,
    gender: str
) -> dict:
    """Расчет калорий для похудения"""
    
    deficits = {
        'slow': 250,      # 0.25 кг/неделю
        'moderate': 500,   # 0.5 кг/неделю
        'fast': 750       # 0.75 кг/неделю
    }
    
    deficit = deficits.get(goal, 500)
    target = tdee - deficit
    
    # Минимальный порог
    min_calories = 1500 if gender == 'male' else 1200
    target = max(target, min_calories)
    
    return {
        'calories': int(target),
        'deficit': int(tdee - target),
        'weekly_loss_kg': round((tdee - target) * 7 / 7700, 2)
    }

def calculate_macros(calories: float, goal: str) -> dict:
    """Расчет БЖУ в зависимости от цели"""
    
    # Рекомендуемые соотношения
    ratios = {
        'lose': {'protein': 0.30, 'fat': 0.30, 'carbs': 0.40},
        'gain': {'protein': 0.25, 'fat': 0.25, 'carbs': 0.50},
        'maintain': {'protein': 0.25, 'fat': 0.30, 'carbs': 0.45}
    }
    
    ratio = ratios.get(goal, ratios['maintain'])
    
    return {
        'protein': round(calories * ratio['protein'] / 4),   # 4 ккал/г
        'fat': round(calories * ratio['fat'] / 9),           # 9 ккал/г
        'carbs': round(calories * ratio['carbs'] / 4)        # 4 ккал/г
    }
```

#### 2. Интервальное голодание (IF)

```
⏰ ПРОТОКОЛЫ ИНТЕРВАЛЬНОГО ГОЛОДАНИЯ

┌─────────────────────────────────────────────────────────────┐
│  16/8 (Leangains) - РЕКОМЕНДУЕТСЯ ДЛЯ НАЧИНАЮЩИХ          │
├─────────────────────────────────────────────────────────────┤
│  Окно питания: 8 часов                                      │
│  Голодание: 16 часов                                        │
│                                                             │
│  Пример расписания:                                         │
│  12:00 - Первый прием пищи                                 │
│  15:00 - Перекус                                           │
│  19:00 - Последний прием пищи                              │
│  20:00-12:00 - Голодание (вода, чай, кофе без добавок)     │
│                                                             │
│  ✅ Преимущества:                                           │
│  • Легко соблюдать                                         │
│  • Подходит для работающих людей                           │
│  • Не требует подсчета калорий (но рекомендуется)          │
└─────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────┐
│  5:2 - УМЕРЕННЫЙ ПРОТОКОЛ                                   │
├─────────────────────────────────────────────────────────────┤
│  5 дней: Обычное питание                                    │
│  2 дня: Ограничение до 500-600 ккал                        │
│                                                             │
│  Пример недели:                                             │
│  Пн, Вт, Чт, Пт, Вс - Обычное питание (TDEE)              │
│  Ср, Сб - Разгрузочные дни (500-600 ккал)                  │
└─────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────┐
│  OMAD (One Meal A Day) - ПРОДВИНУТЫЙ                       │
├─────────────────────────────────────────────────────────────┤
│  Окно питания: 1-2 часа                                     │
│  Голодание: 22-23 часа                                      │
│                                                             │
│  ⚠️ Только для опытных!                                     │
│  Требует тщательного планирования питательности еды        │
└─────────────────────────────────────────────────────────────┘
```

#### 3. Низкоуглеводные диеты

```
🥗 ТИПЫ НИЗКОУГЛЕВОДНЫХ ДИЕТ

┌─────────────────────────────────────────────────────────────┐
│  КЕТО (Ketogenic Diet)                                      │
├─────────────────────────────────────────────────────────────┤
│  Углеводы: 20-50г/день (5-10% калорий)                     │
│  Жиры: 70-80% калорий                                       │
│  Белки: 15-20% калорий                                      │
│                                                             │
│  📋 Разрешенные продукты:                                   │
│  ✅ Мясо, рыба, яйца                                        │
│  ✅ Сыры, сливочное масло                                   │
│  ✅ Орехи, авокадо                                          │
│  ✅ Зеленые овощи                                           │
│  ✅ Ягоды (в небольших количествах)                         │
│                                                             │
│  📋 Запрещенные продукты:                                   │
│  ❌ Хлеб, крупы, макароны                                   │
│  ❌ Сахар, сладости                                         │
│  ❌ Фрукты (большинство)                                    │
│  ❌ Корнеплоды (картофель, морковь)                         │
│  ❌ Бобовые                                                 │
└─────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────┐
│  LOW-CARB (Умеренное ограничение)                          │
├─────────────────────────────────────────────────────────────┤
│  Углеводы: 50-150г/день (20-30% калорий)                   │
│                                                             │
│  Более гибкий вариант, подходит для долгосрочного          │
│  соблюдения. Разрешены цельнозерновые, фрукты.             │
└─────────────────────────────────────────────────────────────┘
```

#### 4. Реверсивная диета (после похудения)

```
🔄 РЕВЕРСИВНАЯ ДИЕТА - ВЫХОД ИЗ ДЕФИЦИТА

Цель: Восстановить метаболизм без набора жира

Процесс:
• Неделя 1: +100 ккал (в основном из углеводов)
• Неделя 2: +100 ккал
• Неделя 3: +100 ккал
• ...продолжать до достижения TDEE

Пример:
Начало: 1,500 ккал → Финиш: 2,200 ккал (через 7 недель)

Мониторинг:
• Вес может увеличиться на 1-2 кг (вода, гликоген)
• Энергия должна расти
• Сон улучшается
• Тренировки становятся продуктивнее
```

### Тренировочные программы для похудения

```
🏋️ ПРОГРАММА ДЛЯ НАЧИНАЮЩИХ (3 дня в неделю)

═══════════════════════════════════════════════════════════

ДЕНЬ 1: ВЕРХНЯЯ ЧАСТЬ ТЕЛА
─────────────────────────────────────────────────────────────
Разминка: 5 минут легкого кардио

1. Отжимания (или с колен)     3 × 8-12
2. Тяга гантели в наклоне      3 × 10-12 (каждая рука)
3. Жим гантелей сидя           3 × 10-12
4. Сгибания на бицепс          3 × 12-15
5. Разгибания на трицепс       3 × 12-15
6. Планка                       3 × 30-60 сек

Заминка: 5 минут растяжки

═══════════════════════════════════════════════════════════

ДЕНЬ 2: НИЖНЯЯ ЧАСТЬ ТЕЛА
─────────────────────────────────────────────────────────────
Разминка: 5 минут легкого кардио

1. Приседания                   3 × 12-15
2. Выпады на месте              3 × 10 (каждая нога)
3. Румынская тяга               3 × 10-12
4. Ягодичный мостик             3 × 15
5. Подъемы на носки             3 × 20
6. Скручивания                  3 × 15-20

Заминка: 5 минут растяжки

═══════════════════════════════════════════════════════════

ДЕНЬ 3: FULL BODY + КАРДИО
─────────────────────────────────────────────────────────────
Разминка: 5 минут

Круговая тренировка (3 круга, отдых 1 мин между кругами):
1. Берпи                        10 повторений
2. Приседания с прыжком         15 повторений
3. Отжимания                    10 повторений
4. Скалолаз                     20 повторений (всего)
5. Выпады с прыжком             10 повторений (всего)
6. Планка с касанием плеч       20 касаний

Кардио: 15-20 минут (бег, велосипед, эллипс)

═══════════════════════════════════════════════════════════
```

```
🔥 HIIT ТРЕНИРОВКА ДЛЯ ЖИРОСЖИГАНИЯ (20 минут)

Структура: 40 сек работа / 20 сек отдых

Раунд 1 (4 минуты):
1. Jumping Jacks (прыжки)
2. Приседания
3. Бег на месте с высоким подниманием колен
4. Отжимания

Отдых: 1 минута

Раунд 2 (4 минуты):
1. Берпи
2. Выпады с прыжком (чередуя ноги)
3. Скалолаз
4. Планка с подъемом рук

Отдых: 1 минута

Раунд 3 (4 минуты):
1. Прыжки в сторону
2. Приседания с прыжком
3. Отжимания с хлопком (или обычные)
4. Бег в планке

Отдых: 1 минута

Раунд 4 (4 минуты):
1. Скручивания велосипед
2. Боковая планка (20 сек каждая сторона)
3. Подъем ног лежа
4. Планка с подтягиванием колен

Заминка: 2-3 минуты растяжки
```

---

## Сбалансированное питание

### Принципы здорового питания

```
🍽️ МЕТОД ТАРЕЛКИ (HARVARD PLATE)

┌─────────────────────────────────────────────────────────────┐
│                                                             │
│                    ИДЕАЛЬНАЯ ТАРЕЛКА                        │
│                                                             │
│         ┌───────────────┬───────────────┐                  │
│         │               │               │                  │
│         │   ОВОЩИ       │   БЕЛОК       │                  │
│         │               │               │                  │
│         │    50%        │    25%        │                  │
│         │               │               │                  │
│         │  🥗🥦🥕🥒    │  🍗🐟🥚🫘    │                  │
│         │               │               │                  │
│         ├───────────────┼───────────────┤                  │
│         │               │               │                  │
│         │ УГЛЕВОДЫ      │    ФРУКТЫ     │                  │
│         │   25%         │    (отдельно) │                  │
│         │               │               │                  │
│         │  🍚🥔🍞      │    🍎🍊🍇    │                  │
│         │               │               │                  │
│         └───────────────┴───────────────┘                  │
│                                                             │
│         💧 Вода - основной напиток                          │
│         🫒 Масла - в умеренных количествах                  │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

### Рекомендуемые продукты

```
📋 СПИСОК ПРОДУКТОВ ДЛЯ ЗДОРОВОГО ПИТАНИЯ

═══════════════════════════════════════════════════════════

🥩 БЕЛКИ (1.6-2.2 г/кг массы тела для тренирующихся)
─────────────────────────────────────────────────────────────
Животные:
• Куриная грудка (31г белка / 100г, 165 ккал)
• Индейка (29г / 100г, 135 ккал)
• Нежирная говядина (26г / 100г, 250 ккал)
• Рыба (лосось, тунец, треска) (20-25г / 100г)
• Яйца (6г / шт, 70 ккал)
• Творог 5% (18г / 100г, 121 ккал)
• Греческий йогурт (10г / 100г, 59 ккал)

Растительные:
• Тофу (8г / 100г, 76 ккал)
• Чечевица (9г / 100г готовой, 116 ккал)
• Нут (9г / 100г готового, 164 ккал)
• Киноа (4г / 100г готовой, 120 ккал)

═══════════════════════════════════════════════════════════

🍚 СЛОЖНЫЕ УГЛЕВОДЫ (40-50% калорий)
─────────────────────────────────────────────────────────────
• Овсянка (66г углеводов / 100г сухой, 389 ккал)
• Бурый рис (23г / 100г готового, 111 ккал)
• Гречка (20г / 100г готовой, 92 ккал)
• Киноа (21г / 100г готовой, 120 ккал)
• Батат (20г / 100г, 86 ккал)
• Цельнозерновой хлеб (41г / 100г, 247 ккал)
• Бобовые (фасоль, чечевица, нут)

═══════════════════════════════════════════════════════════

🥑 ПОЛЕЗНЫЕ ЖИРЫ (25-35% калорий)
─────────────────────────────────────────────────────────────
• Авокадо (15г жиров / 100г, 160 ккал)
• Оливковое масло (100г жиров / 100г, 884 ккал)
• Орехи (миндаль, грецкие, кешью) (45-65г / 100г)
• Семена (чиа, льна, подсолнечника)
• Жирная рыба (лосось, скумбрия, сардины)
• Яичные желтки

═══════════════════════════════════════════════════════════

🥦 ОВОЩИ (минимум 400г в день)
─────────────────────────────────────────────────────────────
Низкокалорийные (до 30 ккал/100г):
• Огурцы, помидоры, листовая зелень
• Кабачки, баклажаны, перец
• Брокколи, цветная капуста
• Шпинат, руккола, салат

Умеренные (30-50 ккал/100г):
• Морковь, свекла
• Лук, чеснок
• Тыква

═══════════════════════════════════════════════════════════

🍎 ФРУКТЫ (2-3 порции в день)
─────────────────────────────────────────────────────────────
Низкий гликемический индекс:
• Ягоды (клубника, черника, малина) - 30-50 ккал/100г
• Яблоки, груши - 50-60 ккал/100г
• Цитрусовые (апельсины, грейпфруты) - 35-45 ккал/100г
• Киви - 61 ккал/100г

Высокий гликемический индекс (умеренно):
• Бананы - 89 ккал/100г
• Виноград - 69 ккал/100г
• Манго - 60 ккал/100г

═══════════════════════════════════════════════════════════
```

### Примеры рационов

```
📅 ПРИМЕР РАЦИОНА НА 1800 ККАЛ (ПОХУДЕНИЕ)

═══════════════════════════════════════════════════════════

🌅 ЗАВТРАК (450 ккал)
─────────────────────────────────────────────────────────────
• Овсянка на воде 60г (сухой) - 220 ккал
• Банан 1/2 шт - 45 ккал
• Ягоды 50г - 25 ккал
• Грецкие орехи 15г - 100 ккал
• Чай/кофе без сахара - 0 ккал
• Мед 10г - 30 ккал

БЖУ: Б-12г Ж-15г У-65г

═══════════════════════════════════════════════════════════

🌞 ОБЕД (550 ккал)
─────────────────────────────────────────────────────────────
• Куриная грудка 150г - 250 ккал
• Бурый рис 80г (сухой) - 95 ккал
• Овощной салат 200г - 50 ккал
  (огурцы, помидоры, зелень)
• Оливковое масло 15мл - 130 ккал
• Лимонный сок - 5 ккал

БЖУ: Б-48г Ж-17г У-50г

═══════════════════════════════════════════════════════════

🍎 ПЕРЕКУС (200 ккал)
─────────────────────────────────────────────────────────────
• Греческий йогурт 150г - 90 ккал
• Ягоды 100г - 50 ккал
• Миндаль 10г - 60 ккал

БЖУ: Б-15г Ж-6г У-17г

═══════════════════════════════════════════════════════════

🌆 УЖИН (500 ккал)
─────────────────────────────────────────────────────────────
• Лосось запеченный 150г - 290 ккал
• Брокколи на пару 200г - 70 ккал
• Батат 100г - 86 ккал
• Специи, лимон - 5 ккал
• Зелень - 5 ккал

БЖУ: Б-35г Ж-15г У-35г

═══════════════════════════════════════════════════════════

🌙 ВЕЧЕРНИЙ ПЕРЕКУС (100 ккал) - опционально
─────────────────────────────────────────────────────────────
• Творог 0.1% 100г - 70 ккал
• Корица - 0 ккал
• Ягоды 50г - 30 ккал

БЖУ: Б-12г Ж-0г У-8г

═══════════════════════════════════════════════════════════

📊 ИТОГО ЗА ДЕНЬ:
Калории: 1,800 ккал
Белки: 122г (27%)
Жиры: 53г (26%)
Углеводы: 175г (39%)
Клетчатка: 28г

💧 Вода: 2-2.5 литра

═══════════════════════════════════════════════════════════
```

```
📅 ПРИМЕР РАЦИОНА НА 2400 ККАЛ (НАБОР МАССЫ)

═══════════════════════════════════════════════════════════

🌅 ЗАВТРАК (600 ккал)
─────────────────────────────────────────────────────────────
• Яичница из 3 яиц - 210 ккал
• Цельнозерновой хлеб 2 ломтика - 160 ккал
• Авокадо 1/2 шт - 120 ккал
• Помидор 100г - 20 ккал
• Сыр 30г - 90 ккал

БЖУ: Б-28г Ж-40г У-25г

═══════════════════════════════════════════════════════════

🍌 ПЕРЕКУС 1 (300 ккал)
─────────────────────────────────────────────────────────────
• Банан 1 шт - 100 ккал
• Арахисовая паста 30г - 180 ккал
• Протеиновый коктейль (опционально)

БЖУ: Б-10г Ж-15г У-30г

═══════════════════════════════════════════════════════════

🌞 ОБЕД (700 ккал)
─────────────────────────────────────────────────────────────
• Говядина постная 200г - 350 ккал
• Гречка 100г (сухой) - 150 ккал
• Овощной салат 250г - 70 ккал
• Оливковое масло 15мл - 130 ккал

БЖУ: Б-55г Ж-25г У-55г

═══════════════════════════════════════════════════════════

🥤 ПЕРЕКУС 2 (250 ккал) - после тренировки
─────────────────────────────────────────────────────────────
• Творог 5% 200г - 240 ккал
• Мед 10г - 30 ккал
• Ягоды 50г - 25 ккал

БЖУ: Б-36г Ж-10г У-25г

═══════════════════════════════════════════════════════════

🌆 УЖИН (550 ккал)
─────────────────────────────────────────────────────────────
• Куриные бедра без кожи 200г - 220 ккал
• Рис басмати 100г (сухой) - 180 ккал
• Овощи на гриле 200г - 80 ккал
• Соус 50г - 70 ккал

БЖУ: Б-40г Ж-12г У-60г

═══════════════════════════════════════════════════════════

📊 ИТОГО ЗА ДЕНЬ:
Калории: 2,400 ккал
Белки: 169г (28%)
Жиры: 102г (38%)
Углеводы: 195г (33%)

═══════════════════════════════════════════════════════════
```

---

## Рекомендации по реализации

### Минимальный жизнеспособный продукт (MVP)

```
📋 MVP CHECKLIST

ЭТАП 1: БАЗОВЫЙ БОТ (2-3 недели)
───────────────────────────────────────────
☐ Регистрация и онбординг
  ├ Ввод параметров (рост, вес, возраст, пол)
  ├ Выбор цели
  └ Расчет КБЖУ

☐ Дневник питания
  ├ Поиск продуктов (локальная база 1000+ продуктов)
  ├ Добавление в приемы пищи
  ├ Подсчет калорий и БЖУ
  └ Дневная статистика

☐ Базовые напоминания
  ├ Напоминание о приемах пищи
  └ Напоминание о воде

ЭТАП 2: РАСШИРЕННЫЙ ФУНКЦИОНАЛ (3-4 недели)
───────────────────────────────────────────
☐ Расширенная база продуктов
  ├ Интеграция с Open Food Facts API
  ├ Сканирование штрих-кодов
  └ Добавление пользовательских продуктов

☐ Тренировочный модуль
  ├ Библиотека упражнений (50+ базовых)
  ├ Готовые программы тренировок
  └ Логирование тренировок

☐ Статистика и отчеты
  ├ Графики прогресса
  ├ Еженедельные отчеты
  └ История веса

ЭТАП 3: ПРОДВИНУТЫЕ ФИЧИ (4-6 недель)
───────────────────────────────────────────
☐ AI-функции
  ├ Распознавание еды по фото
  ├ Персональные рекомендации
  └ AI-чат для вопросов

☐ Telegram Mini App
  ├ Полноценный веб-интерфейс
  ├ Интерактивные графики
  └ Расширенный поиск

☐ Геймификация
  ├ Система достижений
  ├ Уровни и XP
  └ Серии (streaks)

☐ Социальные функции
  ├ Групповые челленджи
  ├ Таблицы лидеров
  └ Шеринг достижений
```

### Ключевые метрики успеха

```
📊 KPI ДЛЯ ФИТНЕС-БОТА

МЕТРИКИ ПРИВЛЕЧЕНИЯ
───────────────────────────────────────────
• DAU (Daily Active Users)
• MAU (Monthly Active Users)
• DAU/MAU ratio (цель: >25%)
• Стоимость привлечения (CAC)
• Источники трафика

МЕТРИКИ УДЕРЖАНИЯ
───────────────────────────────────────────
• Day 1 retention (цель: >40%)
• Day 7 retention (цель: >20%)
• Day 30 retention (цель: >10%)
• Churn rate
• User lifetime

МЕТРИКИ ВОВЛЕЧЕННОСТИ
───────────────────────────────────────────
• Среднее кол-во сессий в день
• Средняя длительность сессии
• Кол-во записей еды в день
• % пользователей с сериями 7+ дней
• Completion rate онбординга (цель: >70%)

МЕТРИКИ МОНЕТИЗАЦИИ (если применимо)
───────────────────────────────────────────
• Conversion rate Free→Premium
• ARPU (Average Revenue Per User)
• LTV (Lifetime Value)
• LTV/CAC ratio (цель: >3)
```

### Рекомендуемые библиотеки и инструменты

```python
# requirements.txt для MVP

# Telegram Bot
aiogram==3.4.1
aiohttp==3.9.3

# Web API (для Mini App)
fastapi==0.109.2
uvicorn==0.27.1
python-multipart==0.0.9

# Database
sqlalchemy==2.0.25
alembic==1.13.1
asyncpg==0.29.0  # Async PostgreSQL

# Cache & Queue
redis==5.0.1
celery==5.3.6

# Validation
pydantic==2.6.1

# Utils
python-dotenv==1.0.1
httpx==0.26.0  # Async HTTP client

# AI (опционально)
openai==1.12.0
anthropic==0.18.1

# Image processing
pillow==10.2.0

# Charts (для статистики)
matplotlib==3.8.2
plotly==5.18.0

# Testing
pytest==8.0.0
pytest-asyncio==0.23.4
```

### Структура проекта

```
fitness-bot/
├── bot/
│   ├── __init__.py
│   ├── main.py              # Точка входа бота
│   ├── config.py            # Конфигурация
│   ├── handlers/
│   │   ├── __init__.py
│   │   ├── start.py         # Онбординг
│   │   ├── food.py          # Дневник питания
│   │   ├── workout.py       # Тренировки
│   │   ├── stats.py         # Статистика
│   │   ├── settings.py      # Настройки
│   │   └── ai.py            # AI-функции
│   ├── keyboards/
│   │   ├── __init__.py
│   │   ├── inline.py        # Inline-клавиатуры
│   │   └── reply.py         # Reply-клавиатуры
│   ├── states/
│   │   ├── __init__.py
│   │   └── user_states.py   # FSM состояния
│   └── middlewares/
│       ├── __init__.py
│       ├── db.py            # Middleware для БД
│       └── auth.py          # Авторизация
│
├── api/
│   ├── __init__.py
│   ├── main.py              # FastAPI приложение
│   ├── routes/
│   │   ├── __init__.py
│   │   ├── users.py
│   │   ├── food.py
│   │   ├── workouts.py
│   │   └── stats.py
│   ├── dependencies.py
│   └── auth.py              # Валидация Telegram WebApp
│
├── core/
│   ├── __init__.py
│   ├── database.py          # Подключение к БД
│   ├── models/
│   │   ├── __init__.py
│   │   ├── user.py
│   │   ├── food.py
│   │   ├── workout.py
│   │   └── achievement.py
│   ├── schemas/
│   │   ├── __init__.py
│   │   └── *.py
│   └── repositories/        # Паттерн Repository
│       ├── __init__.py
│       ├── user_repo.py
│       └── food_repo.py
│
├── services/
│   ├── __init__.py
│   ├── calculator.py        # Расчет КБЖУ
│   ├── food_service.py      # Логика питания
│   ├── workout_service.py   # Логика тренировок
│   ├── stats_service.py     # Статистика
│   ├── notification.py      # Напоминания
│   └── ai_service.py        # AI-интеграции
│
├── external/
│   ├── __init__.py
│   ├── openfoodfacts.py     # API Open Food Facts
│   ├── usda.py              # USDA FoodData Central
│   └── openai_client.py     # OpenAI API
│
├── webapp/                   # Telegram Mini App (Frontend)
│   ├── index.html
│   ├── css/
│   │   └── style.css
│   ├── js/
│   │   ├── app.js
│   │   ├── api.js
│   │   └── components/
│   └── assets/
│
├── migrations/               # Alembic миграции
│   ├── versions/
│   └── env.py
│
├── tests/
│   ├── __init__.py
│   ├── test_calculator.py
│   ├── test_food_service.py
│   └── conftest.py
│
├── data/
│   └── foods.json           # Начальная база продуктов
│
├── docker-compose.yml
├── Dockerfile
├── requirements.txt
├── .env.example
└── README.md
```

---

## Заключение

### Ключевые выводы

1. **Успешные фитнес-боты** объединяют простой UI (inline-кнопки, прогресс-бары) с глубоким функционалом

2. **MVP должен включать**: онбординг, дневник питания, базовую статистику и напоминания

3. **Геймификация критична** для долгосрочного удержания пользователей

4. **Telegram Mini Apps** - современный стандарт для расширенного UI

5. **AI-интеграции** (распознавание еды, персональные рекомендации) значительно повышают ценность продукта

6. **Научная база** (формулы расчета, программы тренировок) должна быть заложена изначально

### Следующие шаги

1. Определить целевую аудиторию и ключевые use cases
2. Создать wireframes основных экранов
3. Разработать MVP с базовым функционалом
4. Провести пользовательское тестирование
5. Итеративно расширять функционал на основе обратной связи

---

*Документ создан: Январь 2026*
*Версия: 1.0*
