"""Базовый класс для моделей"""
from sqlalchemy import Column, Integer, DateTime
from sqlalchemy.sql import func
from ..db import Base


class BaseModel(Base):
    """Базовый класс с общими полями"""
    __abstract__ = True
    
    id = Column(Integer, primary_key=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())





