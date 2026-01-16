"""
Сервис расчета КБЖУ и метаболизма
"""
from typing import Dict, Optional
from bot.config import Constants


class CalculatorService:
    """Калькулятор для расчета показателей"""
    
    @staticmethod
    def calculate_bmr(weight: float, height: float, age: int, gender: str) -> float:
        """
        Расчет базового метаболизма по формуле Mifflin-St Jeor
        
        Args:
            weight: вес в кг
            height: рост в см
            age: возраст в годах
            gender: пол ('male' или 'female')
        
        Returns:
            BMR в ккал
        """
        bmr = 10 * weight + 6.25 * height - 5 * age
        
        if gender == "male":
            bmr += 5
        else:
            bmr -= 161
            
        return round(bmr, 0)
    
    @staticmethod
    def calculate_tdee(bmr: float, activity_level: str) -> float:
        """
        Расчет суточного расхода калорий (TDEE)
        
        Args:
            bmr: базовый метаболизм
            activity_level: уровень активности
        
        Returns:
            TDEE в ккал
        """
        activity_data = Constants.ACTIVITY_LEVELS.get(activity_level, Constants.ACTIVITY_LEVELS["medium"])
        factor = activity_data["factor"]
        
        return round(bmr * factor, 0)
    
    @staticmethod
    def calculate_target_calories(tdee: float, goal: str, gender: str) -> int:
        """
        Расчет целевых калорий в зависимости от цели
        
        Args:
            tdee: суточный расход
            goal: цель ('lose', 'maintain', 'gain')
            gender: пол для определения минимума
        
        Returns:
            Целевые калории
        """
        goal_data = Constants.GOALS.get(goal, Constants.GOALS["maintain"])
        target = tdee + goal_data["deficit"]
        
        # Минимальные калории
        min_cal = Constants.MIN_CALORIES_MALE if gender == "male" else Constants.MIN_CALORIES_FEMALE
        
        return max(int(target), min_cal)
    
    @staticmethod
    def calculate_macros(calories: int, goal: str) -> Dict[str, float]:
        """
        Расчет макронутриентов (БЖУ)
        
        Args:
            calories: целевые калории
            goal: цель
        
        Returns:
            Dict с белками, жирами и углеводами в граммах
        """
        # Соотношения в зависимости от цели
        ratios = {
            "lose": {"protein": 0.30, "fat": 0.30, "carbs": 0.40},
            "gain": {"protein": 0.25, "fat": 0.25, "carbs": 0.50},
            "maintain": {"protein": 0.25, "fat": 0.30, "carbs": 0.45}
        }
        
        ratio = ratios.get(goal, ratios["maintain"])
        
        return {
            "protein": round(calories * ratio["protein"] / 4),   # 4 ккал/г белка
            "fat": round(calories * ratio["fat"] / 9),           # 9 ккал/г жира
            "carbs": round(calories * ratio["carbs"] / 4)        # 4 ккал/г углеводов
        }
    
    @staticmethod
    def calculate_water_norm(weight: float, activity_level: str = "medium") -> float:
        """
        Расчет нормы воды в литрах
        
        Args:
            weight: вес в кг
            activity_level: уровень активности
        
        Returns:
            Норма воды в литрах
        """
        # Базовая норма: 30-35 мл на кг веса
        base_ml = weight * 33
        
        # Добавка за активность
        activity_bonus = {
            "minimal": 0,
            "low": 200,
            "medium": 400,
            "high": 600,
            "extreme": 800
        }
        
        bonus = activity_bonus.get(activity_level, 400)
        total_ml = base_ml + bonus
        
        return round(total_ml / 1000, 1)
    
    @staticmethod
    def calculate_bmi(weight: float, height: float) -> Dict[str, any]:
        """
        Расчет индекса массы тела (BMI)
        
        Args:
            weight: вес в кг
            height: рост в см
        
        Returns:
            Dict с BMI и категорией
        """
        height_m = height / 100
        bmi = weight / (height_m ** 2)
        
        if bmi < 18.5:
            category = "Недостаточный вес"
            emoji = "⚠️"
        elif bmi < 25:
            category = "Норма"
            emoji = "✅"
        elif bmi < 30:
            category = "Избыточный вес"
            emoji = "⚠️"
        else:
            category = "Ожирение"
            emoji = "🔴"
        
        return {
            "bmi": round(bmi, 1),
            "category": category,
            "emoji": emoji
        }
    
    @staticmethod
    def calculate_ideal_weight(height: float, gender: str) -> Dict[str, float]:
        """
        Расчет идеального веса по разным формулам
        
        Args:
            height: рост в см
            gender: пол
        
        Returns:
            Dict с идеальным весом по разным формулам
        """
        # Формула Брока
        if gender == "male":
            broca = (height - 100) * 0.9
        else:
            broca = (height - 100) * 0.85
        
        # Формула Лоренца
        if gender == "male":
            lorentz = (height - 100) - ((height - 150) / 4)
        else:
            lorentz = (height - 100) - ((height - 150) / 2)
        
        # По BMI (норма 18.5-25)
        height_m = height / 100
        bmi_min = 18.5 * (height_m ** 2)
        bmi_max = 25 * (height_m ** 2)
        
        return {
            "broca": round(broca, 1),
            "lorentz": round(lorentz, 1),
            "bmi_range": f"{round(bmi_min, 1)} - {round(bmi_max, 1)}"
        }
    
    @staticmethod
    def calculate_weekly_weight_change(calories_deficit: int) -> float:
        """
        Расчет изменения веса за неделю
        
        Args:
            calories_deficit: дефицит/профицит калорий в день
        
        Returns:
            Изменение веса в кг за неделю
        """
        # 7700 ккал ≈ 1 кг жира
        weekly_deficit = calories_deficit * 7
        return round(weekly_deficit / 7700, 2)
    
    @staticmethod
    def calculate_food_nutrients(
        calories_100g: float,
        protein_100g: float,
        fat_100g: float,
        carbs_100g: float,
        portion_size: float
    ) -> Dict[str, float]:
        """
        Расчет нутриентов для порции
        
        Args:
            calories_100g, protein_100g, fat_100g, carbs_100g: значения на 100г
            portion_size: размер порции в граммах
        
        Returns:
            Dict с нутриентами для порции
        """
        factor = portion_size / 100
        
        return {
            "calories": round(calories_100g * factor, 0),
            "protein": round(protein_100g * factor, 1),
            "fat": round(fat_100g * factor, 1),
            "carbs": round(carbs_100g * factor, 1)
        }
