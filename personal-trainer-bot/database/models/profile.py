"""
Модель профиля пользователя (анкета)
"""
from sqlalchemy import Column, Integer, Float, String, Boolean, JSON, ForeignKey, Text
from sqlalchemy.orm import relationship
from .base import Base, TimestampMixin


class UserProfile(Base, TimestampMixin):
    """Профиль пользователя с данными анкеты"""
    __tablename__ = "user_profiles"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id"), unique=True, nullable=False)
    
    # === ЛИЧНЫЕ ДАННЫЕ ===
    name = Column(String(100), nullable=True)
    age = Column(Integer, nullable=True)
    gender = Column(String(20), nullable=True)  # male, female, other
    height = Column(Float, nullable=True)  # см
    current_weight = Column(Float, nullable=True)  # кг
    target_weight = Column(Float, nullable=True)  # кг
    
    # === ЦЕЛИ ===
    primary_goal = Column(String(50), nullable=True)  # weight_loss, muscle_gain, maintenance, endurance, health
    target_date = Column(String(10), nullable=True)  # YYYY-MM-DD
    motivation = Column(Text, nullable=True)
    
    # === УРОВЕНЬ АКТИВНОСТИ ===
    fitness_level = Column(String(20), nullable=True)  # beginner, intermediate, advanced, pro
    experience_years = Column(Float, default=0)
    current_training_days = Column(Integer, default=0)
    activity_types = Column(JSON, default=list)  # ["strength", "cardio", "yoga"]
    
    # === ЗДОРОВЬЕ ===
    health_conditions = Column(JSON, default=list)  # ["diabetes", "hypertension"]
    injuries = Column(JSON, default=list)  # [{"area": "knee", "description": "..."}]
    allergies = Column(JSON, default=list)  # ["nuts", "dairy"]
    intolerances = Column(JSON, default=list)  # ["lactose", "gluten"]
    medications = Column(JSON, default=list)
    
    # === ОБРАЗ ЖИЗНИ ===
    work_type = Column(String(30), nullable=True)  # sedentary, moderate, active, physical
    work_schedule = Column(String(30), nullable=True)  # 5/2, shift, remote, flexible
    sleep_hours = Column(Float, nullable=True)
    
    # === ТРЕНИРОВКИ ===
    training_location = Column(String(30), nullable=True)  # gym, home_equipped, home_basic, outdoor
    available_equipment = Column(JSON, default=list)  # ["dumbbells", "barbell", "pullup_bar"]
    training_duration = Column(Integer, default=60)  # минут
    preferred_training_time = Column(String(20), nullable=True)  # morning, afternoon, evening
    training_days_per_week = Column(Integer, default=3)
    
    # === ПИТАНИЕ ===
    diet_type = Column(String(30), nullable=True)  # omnivore, vegetarian, vegan, keto
    meals_per_day = Column(Integer, default=4)
    can_cook = Column(Boolean, default=True)
    budget = Column(String(20), nullable=True)  # low, medium, high
    disliked_foods = Column(JSON, default=list)
    favorite_foods = Column(JSON, default=list)
    water_intake = Column(Float, default=1.5)  # литров в день
    
    # === ВРЕДНЫЕ ПРИВЫЧКИ ===
    smoking = Column(Boolean, default=False)
    alcohol_frequency = Column(String(20), nullable=True)  # never, rarely, sometimes, often
    
    # === РАССЧИТАННЫЕ ПАРАМЕТРЫ ===
    bmr = Column(Float, nullable=True)  # Базовый метаболизм
    tdee = Column(Float, nullable=True)  # Общий расход
    target_calories = Column(Integer, nullable=True)
    target_protein = Column(Integer, nullable=True)  # граммы
    target_fat = Column(Integer, nullable=True)
    target_carbs = Column(Integer, nullable=True)
    target_water = Column(Float, nullable=True)  # литры
    
    # Связь
    user = relationship("User", back_populates="profile")
    
    def calculate_metrics(self):
        """Рассчитать BMR, TDEE и макросы"""
        if not all([self.age, self.gender, self.height, self.current_weight]):
            return
        
        # BMR по формуле Миффлина-Сан Жеора
        if self.gender == "male":
            self.bmr = 10 * self.current_weight + 6.25 * self.height - 5 * self.age + 5
        else:
            self.bmr = 10 * self.current_weight + 6.25 * self.height - 5 * self.age - 161
        
        # Коэффициент активности
        activity_multipliers = {
            0: 1.2,    # Сидячий
            1: 1.375,  # 1-2 тренировки
            2: 1.375,
            3: 1.55,   # 3-4 тренировки
            4: 1.55,
            5: 1.725,  # 5-6 тренировок
            6: 1.725,
            7: 1.9     # Ежедневные тренировки
        }
        multiplier = activity_multipliers.get(self.training_days_per_week or 0, 1.2)
        self.tdee = self.bmr * multiplier
        
        # Калории по цели
        if self.primary_goal == "weight_loss":
            self.target_calories = int(self.tdee - 400)
        elif self.primary_goal == "muscle_gain":
            self.target_calories = int(self.tdee + 300)
        else:
            self.target_calories = int(self.tdee)
        
        # Макросы
        if self.primary_goal == "weight_loss":
            self.target_protein = int(self.current_weight * 2.0)
            self.target_fat = int(self.current_weight * 0.9)
        elif self.primary_goal == "muscle_gain":
            self.target_protein = int(self.current_weight * 1.8)
            self.target_fat = int(self.current_weight * 1.0)
        else:
            self.target_protein = int(self.current_weight * 1.6)
            self.target_fat = int(self.current_weight * 0.9)
        
        protein_cals = self.target_protein * 4
        fat_cals = self.target_fat * 9
        self.target_carbs = int((self.target_calories - protein_cals - fat_cals) / 4)
        
        # Вода (30 мл на кг веса)
        self.target_water = round(self.current_weight * 0.03, 1)
    
    def __repr__(self):
        return f"<UserProfile(user_id={self.user_id}, goal={self.primary_goal})>"
