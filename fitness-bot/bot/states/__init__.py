"""
FSM состояния бота
"""
from bot.states.user_states import (
    OnboardingStates,
    FoodStates,
    WaterStates,
    WeightStates,
    ProfileStates
)

__all__ = [
    "OnboardingStates",
    "FoodStates", 
    "WaterStates",
    "WeightStates",
    "ProfileStates"
]
