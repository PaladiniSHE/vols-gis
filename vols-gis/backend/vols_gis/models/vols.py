"""Модель ВОЛС маршрутов"""
from sqlalchemy import Column, String, Text, Integer, Numeric, ForeignKey, JSON
from geoalchemy2 import Geometry
from .base import BaseModel


class Vols(BaseModel):
    """ВОЛС маршрут"""
    __tablename__ = 'vols'
    
    name = Column(String(255), nullable=False)
    description = Column(Text)
    start_node_id = Column(Integer, ForeignKey('nodes.id'))
    end_node_id = Column(Integer, ForeignKey('nodes.id'))
    path = Column(Geometry('LINESTRING', srid=4326), nullable=False)
    length_km = Column(Numeric(10, 2))
    status = Column(String(50))  # 'active', 'planning', 'under_construction'
    meta_data = Column(JSON)
    
    def to_dict(self):
        """Преобразует объект в словарь"""
        try:
            return {
                'id': self.id,
                'name': self.name or '',
                'description': self.description,
                'start_node_id': self.start_node_id,
                'end_node_id': self.end_node_id,
                'path': self.path,
                'length_km': float(self.length_km) if self.length_km else None,
                'status': self.status,
                'meta_data': self.meta_data,
                'created_at': self.created_at.isoformat() if self.created_at else None,
                'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            }
        except Exception as e:
            # Безопасный fallback
            return {
                'id': getattr(self, 'id', None),
                'name': getattr(self, 'name', '') or '',
                'description': getattr(self, 'description', None),
                'start_node_id': getattr(self, 'start_node_id', None),
                'end_node_id': getattr(self, 'end_node_id', None),
                'path': getattr(self, 'path', None),
                'length_km': float(getattr(self, 'length_km', None)) if getattr(self, 'length_km', None) else None,
                'status': getattr(self, 'status', None),
                'meta_data': getattr(self, 'meta_data', None),
                'created_at': None,
                'updated_at': None,
            }




