"""Модель связей"""
from sqlalchemy import Column, Integer, Numeric, String, ForeignKey, JSON
from .base import BaseModel


class Link(BaseModel):
    """Связь между узлами (patch cord)"""
    __tablename__ = 'links'
    
    fiber_id = Column(Integer, ForeignKey('fibers.id'))
    start_node_id = Column(Integer, ForeignKey('nodes.id'))
    end_node_id = Column(Integer, ForeignKey('nodes.id'))
    start_port = Column(Integer)  # номер порта на старте
    end_port = Column(Integer)  # номер порта на конце
    status = Column(String(50))  # 'active', 'spare', 'unused'
    capacity_gbps = Column(Numeric(10, 2))
    meta_data = Column(JSON)
    
    def to_dict(self):
        """Преобразует объект в словарь"""
        try:
            return {
                'id': self.id,
                'fiber_id': self.fiber_id,
                'start_node_id': self.start_node_id,
                'end_node_id': self.end_node_id,
                'start_port': self.start_port,
                'end_port': self.end_port,
                'status': self.status,
                'capacity_gbps': float(self.capacity_gbps) if self.capacity_gbps else None,
                'meta_data': self.meta_data,
                'created_at': self.created_at.isoformat() if self.created_at else None,
                'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            }
        except Exception as e:
            # Безопасный fallback
            return {
                'id': self.id,
                'fiber_id': getattr(self, 'fiber_id', None),
                'start_node_id': getattr(self, 'start_node_id', None),
                'end_node_id': getattr(self, 'end_node_id', None),
                'start_port': getattr(self, 'start_port', None),
                'end_port': getattr(self, 'end_port', None),
                'status': getattr(self, 'status', None),
                'capacity_gbps': float(getattr(self, 'capacity_gbps', None)) if getattr(self, 'capacity_gbps', None) else None,
                'meta_data': getattr(self, 'meta_data', None),
                'created_at': None,
                'updated_at': None,
            }

