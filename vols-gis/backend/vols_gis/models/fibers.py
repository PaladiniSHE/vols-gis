"""Модель волокон"""
from sqlalchemy import Column, String, Integer, ForeignKey, JSON
from .base import BaseModel


class Fiber(BaseModel):
    """Волокно в кабеле"""
    __tablename__ = 'fibers'
    
    name = Column(String(255), nullable=False)
    cable_type = Column(String(100))  # марка кабеля
    fiber_count = Column(Integer)  # количество волокон в пучке
    status = Column(String(50))  # 'active', 'spare', 'damaged'
    vols_id = Column(Integer, ForeignKey('vols.id'))
    meta_data = Column(JSON)
    
    def to_dict(self):
        """Преобразует объект в словарь"""
        try:
            return {
                'id': self.id,
                'name': self.name or '',
                'cable_type': self.cable_type,
                'fiber_count': self.fiber_count,
                'status': self.status,
                'vols_id': self.vols_id,
                'meta_data': self.meta_data,
                'created_at': self.created_at.isoformat() if self.created_at else None,
                'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            }
        except Exception as e:
            # Безопасный fallback
            return {
                'id': self.id,
                'name': getattr(self, 'name', '') or '',
                'cable_type': getattr(self, 'cable_type', None),
                'fiber_count': getattr(self, 'fiber_count', None),
                'status': getattr(self, 'status', None),
                'vols_id': getattr(self, 'vols_id', None),
                'meta_data': getattr(self, 'meta_data', None),
                'created_at': None,
                'updated_at': None,
            }




