"""Модель пользователей"""
from sqlalchemy import Column, String, Boolean
from .base import BaseModel


class User(BaseModel):
    """Пользователь системы"""
    __tablename__ = 'users'
    
    username = Column(String(100), unique=True, nullable=False)
    email = Column(String(255), unique=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    role = Column(String(50))  # 'admin', 'operator', 'viewer'
    is_active = Column(Boolean, default=True)
    
    def to_dict(self):
        """Преобразует объект в словарь (без пароля)"""
        return {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'role': self.role,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat() if self.created_at else None,
        }





