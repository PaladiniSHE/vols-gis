"""
Базовая модель для SQLAlchemy
"""
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy import Column, DateTime
from datetime import datetime


class Base(DeclarativeBase):
    """Базовый класс для всех моделей"""
    pass


class TimestampMixin:
    """Миксин для добавления временных меток"""
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
