"""Pydantic схемы для VOLS"""
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List


class VolsCreate(BaseModel):
    """Схема для создания ВОЛС маршрута"""
    name: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    start_node_id: Optional[int] = None
    end_node_id: Optional[int] = None
    path: List[List[float]] = Field(..., description="Список координат [lon, lat]")
    length_km: Optional[float] = None
    status: Optional[str] = Field(None, pattern='^(active|planning|under_construction)$')
    meta_data: Optional[Dict[str, Any]] = None


class VolsUpdate(BaseModel):
    """Схема для обновления ВОЛС маршрута"""
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = None
    start_node_id: Optional[int] = None
    end_node_id: Optional[int] = None
    path: Optional[List[List[float]]] = None
    length_km: Optional[float] = None
    status: Optional[str] = Field(None, pattern='^(active|planning|under_construction)$')
    meta_data: Optional[Dict[str, Any]] = None

