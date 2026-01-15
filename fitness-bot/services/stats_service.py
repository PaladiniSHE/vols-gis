"""
Сервис статистики
"""
from datetime import date, timedelta
from typing import Dict, List, Optional
from sqlalchemy import select, func, and_
from sqlalchemy.ext.asyncio import AsyncSession

from core.models.user import User
from core.models.food import FoodEntry
from core.models.water import WaterEntry
from core.models.weight import WeightLog


class StatsService:
    """Сервис для получения статистики"""
    
    def __init__(self, session: AsyncSession):
        self.session = session
    
    async def get_daily_summary(self, user_id: int, target_date: date) -> Dict:
        """Получить сводку за день"""
        # Питание
        food_result = await self.session.execute(
            select(
                func.sum(FoodEntry.calories).label("calories"),
                func.sum(FoodEntry.protein).label("protein"),
                func.sum(FoodEntry.fat).label("fat"),
                func.sum(FoodEntry.carbs).label("carbs")
            )
            .where(
                and_(
                    FoodEntry.user_id == user_id,
                    FoodEntry.entry_date == target_date
                )
            )
        )
        food = food_result.one()
        
        # Вода
        water_result = await self.session.execute(
            select(func.sum(WaterEntry.amount_ml))
            .where(
                and_(
                    WaterEntry.user_id == user_id,
                    WaterEntry.entry_date == target_date
                )
            )
        )
        water_ml = water_result.scalar() or 0
        
        return {
            "date": target_date,
            "calories": float(food.calories or 0),
            "protein": float(food.protein or 0),
            "fat": float(food.fat or 0),
            "carbs": float(food.carbs or 0),
            "water_ml": int(water_ml),
            "water_liters": round(water_ml / 1000, 2)
        }
    
    async def get_weekly_summary(self, user_id: int) -> List[Dict]:
        """Получить сводку за неделю"""
        today = date.today()
        summaries = []
        
        for i in range(7):
            day = today - timedelta(days=i)
            summary = await self.get_daily_summary(user_id, day)
            summaries.append(summary)
        
        return summaries
    
    async def get_weekly_averages(self, user_id: int) -> Dict:
        """Получить средние показатели за неделю"""
        today = date.today()
        week_ago = today - timedelta(days=7)
        
        result = await self.session.execute(
            select(
                func.avg(FoodEntry.calories).label("avg_calories"),
                func.avg(FoodEntry.protein).label("avg_protein"),
                func.avg(FoodEntry.fat).label("avg_fat"),
                func.avg(FoodEntry.carbs).label("avg_carbs")
            )
            .where(
                and_(
                    FoodEntry.user_id == user_id,
                    FoodEntry.entry_date >= week_ago,
                    FoodEntry.entry_date <= today
                )
            )
        )
        row = result.one()
        
        return {
            "avg_calories": round(float(row.avg_calories or 0), 0),
            "avg_protein": round(float(row.avg_protein or 0), 1),
            "avg_fat": round(float(row.avg_fat or 0), 1),
            "avg_carbs": round(float(row.avg_carbs or 0), 1)
        }
    
    async def get_weight_history(
        self,
        user_id: int,
        days: int = 30
    ) -> List[WeightLog]:
        """Получить историю веса"""
        start_date = date.today() - timedelta(days=days)
        
        result = await self.session.execute(
            select(WeightLog)
            .where(
                and_(
                    WeightLog.user_id == user_id,
                    WeightLog.entry_date >= start_date
                )
            )
            .order_by(WeightLog.entry_date)
        )
        return result.scalars().all()
    
    async def get_weight_change(self, user_id: int, days: int = 7) -> Optional[float]:
        """Получить изменение веса за период"""
        today = date.today()
        start_date = today - timedelta(days=days)
        
        # Последний вес
        latest = await self.session.execute(
            select(WeightLog)
            .where(WeightLog.user_id == user_id)
            .order_by(WeightLog.entry_date.desc())
            .limit(1)
        )
        latest_log = latest.scalar_one_or_none()
        
        # Первый вес в периоде
        earliest = await self.session.execute(
            select(WeightLog)
            .where(
                and_(
                    WeightLog.user_id == user_id,
                    WeightLog.entry_date >= start_date
                )
            )
            .order_by(WeightLog.entry_date)
            .limit(1)
        )
        earliest_log = earliest.scalar_one_or_none()
        
        if latest_log and earliest_log:
            return round(latest_log.weight - earliest_log.weight, 2)
        return None
    
    async def log_weight(
        self,
        user_id: int,
        weight: float,
        body_fat_percent: Optional[float] = None,
        notes: Optional[str] = None,
        entry_date: Optional[date] = None
    ) -> WeightLog:
        """Записать вес"""
        if entry_date is None:
            entry_date = date.today()
        
        # Проверяем, есть ли уже запись на сегодня
        existing = await self.session.execute(
            select(WeightLog)
            .where(
                and_(
                    WeightLog.user_id == user_id,
                    WeightLog.entry_date == entry_date
                )
            )
        )
        log = existing.scalar_one_or_none()
        
        if log:
            # Обновляем существующую запись
            log.weight = weight
            if body_fat_percent:
                log.body_fat_percent = body_fat_percent
            if notes:
                log.notes = notes
        else:
            # Создаем новую запись
            log = WeightLog(
                user_id=user_id,
                weight=weight,
                body_fat_percent=body_fat_percent,
                notes=notes,
                entry_date=entry_date
            )
            self.session.add(log)
        
        await self.session.commit()
        await self.session.refresh(log)
        
        return log
    
    async def calculate_progress(self, user_id: int, user_goals: Dict) -> Dict:
        """Рассчитать прогресс к целям"""
        today = date.today()
        daily = await self.get_daily_summary(user_id, today)
        
        def calc_percent(current: float, goal: float) -> int:
            if goal <= 0:
                return 0
            return min(int((current / goal) * 100), 150)
        
        return {
            "calories": {
                "current": daily["calories"],
                "goal": user_goals.get("calories", 0),
                "percent": calc_percent(daily["calories"], user_goals.get("calories", 1))
            },
            "protein": {
                "current": daily["protein"],
                "goal": user_goals.get("protein", 0),
                "percent": calc_percent(daily["protein"], user_goals.get("protein", 1))
            },
            "fat": {
                "current": daily["fat"],
                "goal": user_goals.get("fat", 0),
                "percent": calc_percent(daily["fat"], user_goals.get("fat", 1))
            },
            "carbs": {
                "current": daily["carbs"],
                "goal": user_goals.get("carbs", 0),
                "percent": calc_percent(daily["carbs"], user_goals.get("carbs", 1))
            },
            "water": {
                "current": daily["water_liters"],
                "goal": user_goals.get("water", 2.0),
                "percent": calc_percent(daily["water_liters"], user_goals.get("water", 2.0))
            }
        }
