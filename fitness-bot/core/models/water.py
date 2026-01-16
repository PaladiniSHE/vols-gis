"""
Модель для отслеживания воды
"""
from datetime import datetime, date
from sqlalchemy import Integer, Date, DateTime, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column

from core.database import Base


class WaterEntry(Base):
    """Запись о выпитой воде"""
    __tablename__ = "water_entries"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"), index=True)
    
    amount_ml: Mapped[int] = mapped_column(Integer)  # миллилитры
    
    logged_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    entry_date: Mapped[date] = mapped_column(Date, index=True)
    
    def __repr__(self):
        return f"<WaterEntry(id={self.id}, user_id={self.user_id}, amount={self.amount_ml}ml)>"
