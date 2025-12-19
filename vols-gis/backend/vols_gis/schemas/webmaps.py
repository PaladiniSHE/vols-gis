"""Pydantic схемы для WebMap"""
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List


class WebMapCreate(BaseModel):
    """Схема для создания веб-карты"""
    name: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    visible_layers: Optional[List[str]] = None
    center_lat: Optional[float] = Field(None, ge=-90, le=90)
    center_lon: Optional[float] = Field(None, ge=-180, le=180)
    zoom_level: Optional[int] = Field(8, ge=1, le=20)
    permissions: Optional[Dict[str, Any]] = None


class WebMapUpdate(BaseModel):
    """Схема для обновления веб-карты"""
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = None
    visible_layers: Optional[List[str]] = None
    center_lat: Optional[float] = Field(None, ge=-90, le=90)
    center_lon: Optional[float] = Field(None, ge=-180, le=180)
    zoom_level: Optional[int] = Field(None, ge=1, le=20)
    permissions: Optional[Dict[str, Any]] = None

