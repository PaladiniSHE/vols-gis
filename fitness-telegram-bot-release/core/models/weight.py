"""
Модель для отслеживания веса
"""
from datetime import datetime, date
from typing import Optional
from sqlalchemy import Integer, Float, Date, DateTime, ForeignKey, Text
from sqlalchemy.orm import Mapped, mapped_column

from core.database import Base


class WeightLog(Base):
    """Запись о весе"""
    __tablename__ = "weight_logs"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"), index=True)
    
    weight: Mapped[float] = mapped_column(Float)  # кг
    body_fat_percent: Mapped[Optional[float]] = mapped_column(Float, nullable=True)  # % жира
    
    notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    logged_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    entry_date: Mapped[date] = mapped_column(Date, index=True)
    
    def __repr__(self):
        return f"<WeightLog(id={self.id}, user_id={self.user_id}, weight={self.weight}kg)>"
