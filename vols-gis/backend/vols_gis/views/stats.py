"""Views для статистики и аналитики"""
from pyramid.view import view_config
from pyramid.response import Response
from sqlalchemy import func
from ..models.nodes import Node
from ..models.vols import Vols
from ..models.fibers import Fiber
from ..models.links import Link
from ..auth.decorators import require_auth
import logging
import traceback

logger = logging.getLogger(__name__)


@view_config(route_name='api_stats_dashboard', request_method='GET')
@require_auth
def stats_dashboard(request):
    """Дашборд со статистикой"""
    try:
        if not hasattr(request, 'db') or request.db is None:
            return Response(
                json_body={'error': 'Database session not available'},
                status=500,
                content_type='application/json'
            )
        
        db = request.db
        
        # Общая статистика
        total_nodes = db.query(func.count(Node.id)).scalar() or 0
        total_vols = db.query(func.count(Vols.id)).scalar() or 0
        total_fibers = db.query(func.count(Fiber.id)).scalar() or 0
        total_links = db.query(func.count(Link.id)).scalar() or 0
        
        # Статистика по статусам узлов
        nodes_by_status = db.query(
            Node.status,
            func.count(Node.id).label('count')
        ).group_by(Node.status).all()
        nodes_status_stats = {status or 'unknown': count for status, count in nodes_by_status}
        
        # Статистика по типам узлов
        nodes_by_type = db.query(
            Node.node_type,
            func.count(Node.id).label('count')
        ).group_by(Node.node_type).all()
        nodes_type_stats = {node_type or 'unknown': count for node_type, count in nodes_by_type}
        
        # Статистика по статусам маршрутов
        vols_by_status = db.query(
            Vols.status,
            func.count(Vols.id).label('count')
        ).group_by(Vols.status).all()
        vols_status_stats = {status or 'unknown': count for status, count in vols_by_status}
        
        # Общая длина маршрутов
        total_length = db.query(func.sum(Vols.length_km)).scalar() or 0
        
        # Статистика по статусам волокон
        fibers_by_status = db.query(
            Fiber.status,
            func.count(Fiber.id).label('count')
        ).group_by(Fiber.status).all()
        fibers_status_stats = {status or 'unknown': count for status, count in fibers_by_status}
        
        # Статистика по статусам связей
        links_by_status = db.query(
            Link.status,
            func.count(Link.id).label('count')
        ).group_by(Link.status).all()
        links_status_stats = {status or 'unknown': count for status, count in links_by_status}
        
        # Статистика по маршрутам (волокна по маршрутам)
        fibers_by_vols = db.query(
            Fiber.vols_id,
            func.count(Fiber.id).label('count')
        ).group_by(Fiber.vols_id).all()
        fibers_by_vols_stats = {vols_id: count for vols_id, count in fibers_by_vols if vols_id}
        
        # Статистика связей по узлам
        links_by_node = db.query(
            Link.start_node_id,
            func.count(Link.id).label('count')
        ).group_by(Link.start_node_id).all()
        links_by_node_stats = {node_id: count for node_id, count in links_by_node if node_id}
        
        dashboard = {
            'summary': {
                'total_nodes': total_nodes,
                'total_vols': total_vols,
                'total_fibers': total_fibers,
                'total_links': total_links,
                'total_length_km': float(total_length) if total_length else 0
            },
            'nodes': {
                'by_status': nodes_status_stats,
                'by_type': nodes_type_stats
            },
            'vols': {
                'by_status': vols_status_stats,
                'total_length_km': float(total_length) if total_length else 0
            },
            'fibers': {
                'by_status': fibers_status_stats,
                'by_vols': fibers_by_vols_stats
            },
            'links': {
                'by_status': links_status_stats,
                'by_node': links_by_node_stats
            }
        }
        
        return Response(
            json_body=dashboard,
            content_type='application/json'
        )
        
    except Exception as e:
        logger.error(f'Ошибка при получении статистики: {e}')
        logger.error(traceback.format_exc())
        return Response(
            json_body={'error': str(e)},
            status=500,
            content_type='application/json'
        )


@view_config(route_name='api_stats_summary', request_method='GET')
@require_auth
def stats_summary(request):
    """Краткая статистика"""
    try:
        if not hasattr(request, 'db') or request.db is None:
            return Response(
                json_body={'error': 'Database session not available'},
                status=500,
                content_type='application/json'
            )
        
        db = request.db
        
        summary = {
            'nodes': db.query(func.count(Node.id)).scalar() or 0,
            'vols': db.query(func.count(Vols.id)).scalar() or 0,
            'fibers': db.query(func.count(Fiber.id)).scalar() or 0,
            'links': db.query(func.count(Link.id)).scalar() or 0,
            'total_length_km': float(db.query(func.sum(Vols.length_km)).scalar() or 0)
        }
        
        return Response(
            json_body=summary,
            content_type='application/json'
        )
        
    except Exception as e:
        logger.error(f'Ошибка при получении краткой статистики: {e}')
        return Response(
            json_body={'error': str(e)},
            status=500,
            content_type='application/json'
        )

