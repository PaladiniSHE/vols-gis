"""
FSM состояния для пользователя
"""
from aiogram.fsm.state import State, StatesGroup


class OnboardingStates(StatesGroup):
    """Состояния онбординга"""
    waiting_for_gender = State()
    waiting_for_birth_year = State()
    waiting_for_height = State()
    waiting_for_weight = State()
    waiting_for_goal = State()
    waiting_for_goal_weight = State()
    waiting_for_activity = State()


class FoodStates(StatesGroup):
    """Состояния для работы с питанием"""
    selecting_meal = State()
    searching_food = State()
    selecting_food = State()
    entering_portion = State()
    entering_custom_food = State()
    entering_custom_calories = State()
    entering_custom_protein = State()
    entering_custom_fat = State()
    entering_custom_carbs = State()


class WaterStates(StatesGroup):
    """Состояния для воды"""
    entering_amount = State()


class WeightStates(StatesGroup):
    """Состояния для веса"""
    entering_weight = State()
    entering_body_fat = State()
    entering_notes = State()


class ProfileStates(StatesGroup):
    """Состояния для редактирования профиля"""
    editing_height = State()
    editing_weight = State()
    editing_goal_weight = State()
