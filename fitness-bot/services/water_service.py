"""
Сервис для отслеживания воды
"""
from datetime import date, datetime
from typing import List, Optional
from sqlalchemy import select, func, and_
from sqlalchemy.ext.asyncio import AsyncSession

from core.models.water import WaterEntry


class WaterService:
    """Сервис управления водным балансом"""
    
    def __init__(self, session: AsyncSession):
        self.session = session
    
    async def add_water_entry(
        self,
        user_id: int,
        amount_ml: int,
        entry_date: Optional[date] = None
    ) -> WaterEntry:
        """Добавить запись о выпитой воде"""
        if entry_date is None:
            entry_date = date.today()
        
        entry = WaterEntry(
            user_id=user_id,
            amount_ml=amount_ml,
            entry_date=entry_date
        )
        
        self.session.add(entry)
        await self.session.commit()
        await self.session.refresh(entry)
        
        return entry
    
    async def get_entries_by_date(
        self,
        user_id: int,
        entry_date: date
    ) -> List[WaterEntry]:
        """Получить записи о воде за день"""
        result = await self.session.execute(
            select(WaterEntry)
            .where(
                and_(
                    WaterEntry.user_id == user_id,
                    WaterEntry.entry_date == entry_date
                )
            )
            .order_by(WaterEntry.logged_at)
        )
        return result.scalars().all()
    
    async def get_daily_total(self, user_id: int, entry_date: date) -> int:
        """Получить суммарное количество воды за день (мл)"""
        result = await self.session.execute(
            select(func.sum(WaterEntry.amount_ml))
            .where(
                and_(
                    WaterEntry.user_id == user_id,
                    WaterEntry.entry_date == entry_date
                )
            )
        )
        total = result.scalar()
        return int(total) if total else 0
    
    async def delete_last_entry(self, user_id: int, entry_date: date) -> bool:
        """Удалить последнюю запись о воде"""
        result = await self.session.execute(
            select(WaterEntry)
            .where(
                and_(
                    WaterEntry.user_id == user_id,
                    WaterEntry.entry_date == entry_date
                )
            )
            .order_by(WaterEntry.logged_at.desc())
            .limit(1)
        )
        entry = result.scalar_one_or_none()
        
        if entry:
            await self.session.delete(entry)
            await self.session.commit()
            return True
        return False
