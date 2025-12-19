"""Pydantic схемы для Node"""
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any


class NodeCreate(BaseModel):
    """Схема для создания узла"""
    name: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    node_type: Optional[str] = Field(None, pattern='^(muft|cross|bsp|terminal)$')
    status: Optional[str] = Field(None, pattern='^(active|inactive|maintenance)$')
    lat: float = Field(..., ge=-90, le=90)
    lon: float = Field(..., ge=-180, le=180)
    meta_data: Optional[Dict[str, Any]] = None


class NodeUpdate(BaseModel):
    """Схема для обновления узла"""
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = None
    node_type: Optional[str] = Field(None, pattern='^(muft|cross|bsp|terminal)$')
    status: Optional[str] = Field(None, pattern='^(active|inactive|maintenance)$')
    lat: Optional[float] = Field(None, ge=-90, le=90)
    lon: Optional[float] = Field(None, ge=-180, le=180)
    meta_data: Optional[Dict[str, Any]] = None

