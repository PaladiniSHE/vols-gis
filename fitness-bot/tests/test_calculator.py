"""
Тесты для калькулятора КБЖУ
"""
import pytest
from services.calculator import CalculatorService


class TestCalculatorService:
    """Тесты для CalculatorService"""
    
    def setup_method(self):
        """Инициализация перед каждым тестом"""
        self.calculator = CalculatorService()
    
    # ==================== BMR Tests ====================
    
    def test_calculate_bmr_male(self):
        """Тест расчета BMR для мужчины"""
        # Мужчина 30 лет, 80 кг, 180 см
        bmr = self.calculator.calculate_bmr(80, 180, 30, "male")
        
        # По формуле Mifflin-St Jeor: 10*80 + 6.25*180 - 5*30 + 5 = 1780
        assert bmr == 1780
    
    def test_calculate_bmr_female(self):
        """Тест расчета BMR для женщины"""
        # Женщина 25 лет, 60 кг, 165 см
        bmr = self.calculator.calculate_bmr(60, 165, 25, "female")
        
        # По формуле: 10*60 + 6.25*165 - 5*25 - 161 = 1370
        assert bmr == 1370
    
    def test_calculate_bmr_edge_case_young(self):
        """Тест BMR для молодого человека"""
        bmr = self.calculator.calculate_bmr(70, 175, 18, "male")
        assert bmr > 0
        assert isinstance(bmr, float)
    
    def test_calculate_bmr_edge_case_old(self):
        """Тест BMR для пожилого человека"""
        bmr = self.calculator.calculate_bmr(75, 170, 70, "female")
        assert bmr > 0
        assert isinstance(bmr, float)
    
    # ==================== TDEE Tests ====================
    
    def test_calculate_tdee_minimal_activity(self):
        """Тест TDEE для минимальной активности"""
        bmr = 1800
        tdee = self.calculator.calculate_tdee(bmr, "minimal")
        
        # TDEE = BMR * 1.2
        assert tdee == 2160
    
    def test_calculate_tdee_medium_activity(self):
        """Тест TDEE для средней активности"""
        bmr = 1800
        tdee = self.calculator.calculate_tdee(bmr, "medium")
        
        # TDEE = BMR * 1.55
        assert tdee == 2790
    
    def test_calculate_tdee_extreme_activity(self):
        """Тест TDEE для экстремальной активности"""
        bmr = 1800
        tdee = self.calculator.calculate_tdee(bmr, "extreme")
        
        # TDEE = BMR * 1.9
        assert tdee == 3420
    
    def test_calculate_tdee_unknown_activity(self):
        """Тест TDEE для неизвестной активности (должен использовать medium)"""
        bmr = 1800
        tdee = self.calculator.calculate_tdee(bmr, "unknown")
        
        # Должен использовать medium (1.55)
        assert tdee == 2790
    
    # ==================== Target Calories Tests ====================
    
    def test_calculate_target_calories_lose(self):
        """Тест целевых калорий для похудения"""
        tdee = 2500
        target = self.calculator.calculate_target_calories(tdee, "lose", "male")
        
        # TDEE - 500 = 2000
        assert target == 2000
    
    def test_calculate_target_calories_maintain(self):
        """Тест целевых калорий для поддержания веса"""
        tdee = 2500
        target = self.calculator.calculate_target_calories(tdee, "maintain", "male")
        
        assert target == 2500
    
    def test_calculate_target_calories_gain(self):
        """Тест целевых калорий для набора массы"""
        tdee = 2500
        target = self.calculator.calculate_target_calories(tdee, "gain", "male")
        
        # TDEE + 500 = 3000
        assert target == 3000
    
    def test_calculate_target_calories_minimum_male(self):
        """Тест минимальных калорий для мужчины"""
        tdee = 1800  # Низкий TDEE
        target = self.calculator.calculate_target_calories(tdee, "lose", "male")
        
        # Не должно быть меньше 1500 для мужчин
        assert target >= 1500
    
    def test_calculate_target_calories_minimum_female(self):
        """Тест минимальных калорий для женщины"""
        tdee = 1500  # Низкий TDEE
        target = self.calculator.calculate_target_calories(tdee, "lose", "female")
        
        # Не должно быть меньше 1200 для женщин
        assert target >= 1200
    
    # ==================== Macros Tests ====================
    
    def test_calculate_macros_lose(self):
        """Тест расчета макросов для похудения"""
        calories = 2000
        macros = self.calculator.calculate_macros(calories, "lose")
        
        assert "protein" in macros
        assert "fat" in macros
        assert "carbs" in macros
        
        # Проверяем соотношение (30/30/40 для похудения)
        assert macros["protein"] == 150  # 2000 * 0.30 / 4
        assert macros["fat"] == 67  # 2000 * 0.30 / 9 (округлено)
        assert macros["carbs"] == 200  # 2000 * 0.40 / 4
    
    def test_calculate_macros_gain(self):
        """Тест расчета макросов для набора массы"""
        calories = 3000
        macros = self.calculator.calculate_macros(calories, "gain")
        
        # Проверяем соотношение (25/25/50 для набора)
        assert macros["protein"] == 188  # 3000 * 0.25 / 4 (округлено)
        assert macros["fat"] == 83  # 3000 * 0.25 / 9 (округлено)
        assert macros["carbs"] == 375  # 3000 * 0.50 / 4
    
    # ==================== BMI Tests ====================
    
    def test_calculate_bmi_normal(self):
        """Тест BMI в норме"""
        result = self.calculator.calculate_bmi(70, 175)
        
        assert "bmi" in result
        assert "category" in result
        assert "emoji" in result
        
        # BMI = 70 / (1.75)^2 ≈ 22.9
        assert 22 < result["bmi"] < 23
        assert result["category"] == "Норма"
        assert result["emoji"] == "✅"
    
    def test_calculate_bmi_underweight(self):
        """Тест BMI недостаточный вес"""
        result = self.calculator.calculate_bmi(50, 175)
        
        # BMI = 50 / (1.75)^2 ≈ 16.3
        assert result["bmi"] < 18.5
        assert result["category"] == "Недостаточный вес"
        assert result["emoji"] == "⚠️"
    
    def test_calculate_bmi_overweight(self):
        """Тест BMI избыточный вес"""
        result = self.calculator.calculate_bmi(85, 175)
        
        # BMI = 85 / (1.75)^2 ≈ 27.8
        assert 25 <= result["bmi"] < 30
        assert result["category"] == "Избыточный вес"
    
    def test_calculate_bmi_obese(self):
        """Тест BMI ожирение"""
        result = self.calculator.calculate_bmi(100, 170)
        
        # BMI = 100 / (1.70)^2 ≈ 34.6
        assert result["bmi"] >= 30
        assert result["category"] == "Ожирение"
        assert result["emoji"] == "🔴"
    
    # ==================== Water Norm Tests ====================
    
    def test_calculate_water_norm_basic(self):
        """Тест базовой нормы воды"""
        water = self.calculator.calculate_water_norm(70, "minimal")
        
        # 70 * 33 = 2310 мл = 2.3 л (без бонуса за активность minimal)
        assert water > 2
        assert water < 3
    
    def test_calculate_water_norm_active(self):
        """Тест нормы воды при высокой активности"""
        water = self.calculator.calculate_water_norm(70, "high")
        
        # Должна быть выше чем при минимальной активности
        water_minimal = self.calculator.calculate_water_norm(70, "minimal")
        assert water > water_minimal
    
    # ==================== Weekly Weight Change Tests ====================
    
    def test_calculate_weekly_weight_change_deficit(self):
        """Тест изменения веса при дефиците"""
        change = self.calculator.calculate_weekly_weight_change(-500)
        
        # -500 * 7 / 7700 ≈ -0.45 кг/неделю
        assert change < 0
        assert -0.5 < change < -0.4
    
    def test_calculate_weekly_weight_change_surplus(self):
        """Тест изменения веса при профиците"""
        change = self.calculator.calculate_weekly_weight_change(500)
        
        assert change > 0
        assert 0.4 < change < 0.5
    
    def test_calculate_weekly_weight_change_maintenance(self):
        """Тест изменения веса при поддержании"""
        change = self.calculator.calculate_weekly_weight_change(0)
        
        assert change == 0
    
    # ==================== Food Nutrients Tests ====================
    
    def test_calculate_food_nutrients(self):
        """Тест расчета нутриентов для порции"""
        # Куриная грудка: 165 ккал, 31г белка, 3.6г жира, 0г углеводов на 100г
        nutrients = self.calculator.calculate_food_nutrients(165, 31, 3.6, 0, 150)
        
        assert nutrients["calories"] == 248  # 165 * 1.5
        assert nutrients["protein"] == 46.5  # 31 * 1.5
        assert nutrients["fat"] == 5.4  # 3.6 * 1.5
        assert nutrients["carbs"] == 0
    
    def test_calculate_food_nutrients_small_portion(self):
        """Тест расчета для маленькой порции"""
        nutrients = self.calculator.calculate_food_nutrients(100, 20, 5, 10, 50)
        
        assert nutrients["calories"] == 50  # 100 * 0.5
        assert nutrients["protein"] == 10  # 20 * 0.5
        assert nutrients["fat"] == 2.5  # 5 * 0.5
        assert nutrients["carbs"] == 5  # 10 * 0.5


class TestIdealWeight:
    """Тесты для расчета идеального веса"""
    
    def setup_method(self):
        self.calculator = CalculatorService()
    
    def test_calculate_ideal_weight_male(self):
        """Тест идеального веса для мужчины"""
        result = self.calculator.calculate_ideal_weight(180, "male")
        
        assert "broca" in result
        assert "lorentz" in result
        assert "bmi_range" in result
        
        # По формуле Брока для мужчин: (180 - 100) * 0.9 = 72
        assert result["broca"] == 72
    
    def test_calculate_ideal_weight_female(self):
        """Тест идеального веса для женщины"""
        result = self.calculator.calculate_ideal_weight(165, "female")
        
        # По формуле Брока для женщин: (165 - 100) * 0.85 = 55.25
        assert result["broca"] == 55.2


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
