"""Pydantic схемы для Fiber"""
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any


class FiberCreate(BaseModel):
    """Схема для создания волокна"""
    name: str = Field(..., min_length=1, max_length=255)
    cable_type: Optional[str] = Field(None, max_length=100)
    fiber_count: Optional[int] = Field(None, ge=1)
    status: Optional[str] = Field(None, pattern='^(active|spare|damaged)$')
    vols_id: Optional[int] = None
    meta_data: Optional[Dict[str, Any]] = None


class FiberUpdate(BaseModel):
    """Схема для обновления волокна"""
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    cable_type: Optional[str] = Field(None, max_length=100)
    fiber_count: Optional[int] = Field(None, ge=1)
    status: Optional[str] = Field(None, pattern='^(active|spare|damaged)$')
    vols_id: Optional[int] = None
    meta_data: Optional[Dict[str, Any]] = None

