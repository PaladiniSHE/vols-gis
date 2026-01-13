"""
Состояния FSM для онбординга
"""
from aiogram.fsm.state import State, StatesGroup


class OnboardingStates(StatesGroup):
    """Состояния анкеты онбординга"""
    
    # Личные данные
    waiting_name = State()
    waiting_age = State()
    waiting_gender = State()
    waiting_height = State()
    waiting_weight = State()
    waiting_target_weight = State()
    
    # Цели
    waiting_goal = State()
    waiting_target_date = State()
    waiting_motivation = State()
    
    # Уровень активности
    waiting_fitness_level = State()
    waiting_training_days = State()
    waiting_activity_types = State()
    
    # Здоровье
    waiting_health_conditions = State()
    waiting_injuries = State()
    waiting_allergies = State()
    
    # Образ жизни
    waiting_work_type = State()
    waiting_sleep_hours = State()
    
    # Тренировки
    waiting_training_location = State()
    waiting_equipment = State()
    waiting_training_duration = State()
    waiting_preferred_time = State()
    
    # Питание
    waiting_diet_type = State()
    waiting_meals_per_day = State()
    waiting_disliked_foods = State()
    waiting_budget = State()
    
    # Завершение
    confirmation = State()


class WorkoutStates(StatesGroup):
    """Состояния для работы с тренировками"""
    
    waiting_workout_feedback = State()
    waiting_exercise_weight = State()
    waiting_exercise_reps = State()
    waiting_workout_rating = State()
    waiting_workout_note = State()


class NutritionStates(StatesGroup):
    """Состояния для работы с питанием"""
    
    waiting_meal_confirmation = State()
    waiting_water_amount = State()
    waiting_cheat_description = State()


class ProgressStates(StatesGroup):
    """Состояния для отслеживания прогресса"""
    
    waiting_weight = State()
    waiting_measurements = State()
    waiting_photo = State()
    waiting_note = State()
