"""Модель узлов связи"""
from sqlalchemy import Column, String, Text, JSON
from geoalchemy2 import Geometry
from .base import BaseModel


class Node(BaseModel):
    """Узел связи (муфта, кросс, БСП, терминал)"""
    __tablename__ = 'nodes'
    
    name = Column(String(255), nullable=False)
    description = Column(Text)
    node_type = Column(String(50))  # 'muft', 'cross', 'bsp', 'terminal'
    status = Column(String(50))  # 'active', 'inactive', 'maintenance'
    geom = Column(Geometry('POINT', srid=4326), nullable=False)
    meta_data = Column(JSON)
    
    def to_dict(self):
        """Преобразует объект в словарь"""
        try:
            return {
                'id': self.id,
                'name': self.name or '',
                'description': self.description,
                'node_type': self.node_type,
                'status': self.status,
                'geom': self.geom,
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
                'node_type': getattr(self, 'node_type', None),
                'status': getattr(self, 'status', None),
                'geom': getattr(self, 'geom', None),
                'meta_data': getattr(self, 'meta_data', None),
                'created_at': None,
                'updated_at': None,
            }




