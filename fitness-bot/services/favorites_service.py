"""
Сервис для работы с избранными продуктами
"""
from typing import List, Optional
from sqlalchemy import select, and_, delete
from sqlalchemy.ext.asyncio import AsyncSession

from core.models.favorites import FavoriteFood
from core.models.food import Food


class FavoritesService:
    """Сервис управления избранными продуктами"""
    
    def __init__(self, session: AsyncSession):
        self.session = session
    
    async def add_to_favorites(self, user_id: int, food_id: int) -> FavoriteFood:
        """Добавить продукт в избранное"""
        # Проверяем, не добавлен ли уже
        existing = await self.get_favorite(user_id, food_id)
        if existing:
            return existing
        
        favorite = FavoriteFood(user_id=user_id, food_id=food_id)
        self.session.add(favorite)
        await self.session.commit()
        await self.session.refresh(favorite)
        
        return favorite
    
    async def remove_from_favorites(self, user_id: int, food_id: int) -> bool:
        """Удалить продукт из избранного"""
        result = await self.session.execute(
            delete(FavoriteFood)
            .where(
                and_(
                    FavoriteFood.user_id == user_id,
                    FavoriteFood.food_id == food_id
                )
            )
        )
        await self.session.commit()
        return result.rowcount > 0
    
    async def get_favorite(self, user_id: int, food_id: int) -> Optional[FavoriteFood]:
        """Проверить, есть ли продукт в избранном"""
        result = await self.session.execute(
            select(FavoriteFood)
            .where(
                and_(
                    FavoriteFood.user_id == user_id,
                    FavoriteFood.food_id == food_id
                )
            )
        )
        return result.scalar_one_or_none()
    
    async def is_favorite(self, user_id: int, food_id: int) -> bool:
        """Проверить, является ли продукт избранным"""
        fav = await self.get_favorite(user_id, food_id)
        return fav is not None
    
    async def get_user_favorites(self, user_id: int, limit: int = 20) -> List[Food]:
        """Получить избранные продукты пользователя"""
        result = await self.session.execute(
            select(Food)
            .join(FavoriteFood, Food.id == FavoriteFood.food_id)
            .where(FavoriteFood.user_id == user_id)
            .order_by(FavoriteFood.added_at.desc())
            .limit(limit)
        )
        return result.scalars().all()
    
    async def get_favorites_count(self, user_id: int) -> int:
        """Получить количество избранных продуктов"""
        from sqlalchemy import func
        result = await self.session.execute(
            select(func.count(FavoriteFood.id))
            .where(FavoriteFood.user_id == user_id)
        )
        return result.scalar() or 0
