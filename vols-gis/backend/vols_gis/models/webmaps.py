"""Модель веб-карт"""
from sqlalchemy import Column, String, Text, Integer, JSON
from geoalchemy2 import Geometry
from .base import BaseModel


class WebMap(BaseModel):
    """Веб-карта/проект"""
    __tablename__ = 'webmaps'
    
    name = Column(String(255), nullable=False)
    description = Column(Text)
    visible_layers = Column(JSON)  # какие слои видны
    center_geom = Column(Geometry('POINT', srid=4326))
    zoom_level = Column(Integer, default=8)
    permissions = Column(JSON)  # права доступа
    
    def to_dict(self):
        """Преобразует объект в словарь"""
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'visible_layers': self.visible_layers,
            'center_geom': self.center_geom,
            'zoom_level': self.zoom_level,
            'permissions': self.permissions,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
        }





