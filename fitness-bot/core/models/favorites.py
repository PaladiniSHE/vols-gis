"""
Модель избранных продуктов
"""
from datetime import datetime
from sqlalchemy import Integer, DateTime, ForeignKey, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from core.database import Base


class FavoriteFood(Base):
    """Избранные продукты пользователя"""
    __tablename__ = "favorite_foods"
    __table_args__ = (
        UniqueConstraint('user_id', 'food_id', name='unique_user_food_favorite'),
    )
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"), index=True)
    food_id: Mapped[int] = mapped_column(Integer, ForeignKey("foods.id"), index=True)
    
    added_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    
    # Связи
    food: Mapped["Food"] = relationship("Food", lazy="selectin")
    
    def __repr__(self):
        return f"<FavoriteFood(user_id={self.user_id}, food_id={self.food_id})>"
