"""Pydantic схемы для User"""
from pydantic import BaseModel, Field, EmailStr
from typing import Optional


class UserCreate(BaseModel):
    """Схема для создания пользователя"""
    username: str = Field(..., min_length=3, max_length=100)
    email: EmailStr
    password: str = Field(..., min_length=6)
    role: Optional[str] = Field('viewer', pattern='^(admin|operator|viewer)$')
    is_active: Optional[bool] = True


class UserUpdate(BaseModel):
    """Схема для обновления пользователя"""
    username: Optional[str] = Field(None, min_length=3, max_length=100)
    email: Optional[EmailStr] = None
    password: Optional[str] = Field(None, min_length=6)
    role: Optional[str] = Field(None, pattern='^(admin|operator|viewer)$')
    is_active: Optional[bool] = None


class UserLogin(BaseModel):
    """Схема для входа пользователя"""
    username: str
    password: str

