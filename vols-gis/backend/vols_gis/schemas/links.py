"""Pydantic схемы для Link"""
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any


class LinkCreate(BaseModel):
    """Схема для создания связи"""
    fiber_id: int
    start_node_id: int
    end_node_id: int
    start_port: Optional[int] = None
    end_port: Optional[int] = None
    status: Optional[str] = Field(None, pattern='^(active|spare|unused)$')
    capacity_gbps: Optional[float] = None
    meta_data: Optional[Dict[str, Any]] = None


class LinkUpdate(BaseModel):
    """Схема для обновления связи"""
    fiber_id: Optional[int] = None
    start_node_id: Optional[int] = None
    end_node_id: Optional[int] = None
    start_port: Optional[int] = None
    end_port: Optional[int] = None
    status: Optional[str] = Field(None, pattern='^(active|spare|unused)$')
    capacity_gbps: Optional[float] = None
    meta_data: Optional[Dict[str, Any]] = None

